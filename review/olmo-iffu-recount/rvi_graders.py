"""Graders for the reviewer's re-grade of run olmo-iffu (my own driver code around the upstream checkers).

Upstream code is my own fetch (gh api, pinned commits) under ~/review/oiffu_rv/upstream, byte-compared with the
run's vendored copies (out/upstream_check.txt):
  IFBench        allenai/IFBench @ cd189a9c (ifbench/, evaluation_lib.py, ifbench/data/IFBench_test.jsonl)
  IFEval         google-research instruction_following_eval @ e6890f85 (+ data/input_data.jsonl)
  OMEGA `omega`  OLMES @ 5a51f502: GenericTask._extract_answer (omega.py) + utils.extract_answer with the
                 omega_*:0-shot-chat metric_kwargs (configs/tasks.py), exact_match_flex (ignore_case) via
                 dependencies/hf_evaluate/exact_match.py; functions taken from the fetched files by `ast`.
  OMEGA `rl`     open-instruct @ 7e780f2fea ground_truth_utils.MathVerifier on the whole response, run in a worker
                 thread (the RL reward's run_in_executor path), imported from the fetched math_utils.py.
IF strict / loose: the package's own test_instruction_following_strict / _loose on the answer (text after the last
'</think>', stripped), with the ORIGINAL prompt and kwargs of the upstream dataset record. langdetect is seeded 0.
"""
import ast
import concurrent.futures as cf
import dataclasses
import importlib.util
import os
import re
import sys
import types
from pathlib import Path

from rvi_core import SCR, answer_of

UP = SCR / "upstream"
os.environ.setdefault("NLTK_DATA", str(SCR / "nltk_data"))

import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0

# ---------------------------------------------------------------- IFBench / IFEval
sys.path.insert(0, str(UP / "ifbench"))  # package `ifbench`
sys.path.insert(0, str(UP / "ife"))  # package `instruction_following_eval`


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IFB = _load("rv_ifbench_evaluation_lib", UP / "ifbench" / "evaluation_lib.py")
from instruction_following_eval import evaluation_lib as IFE  # noqa: E402


def if_grade(task, rec, response):
    """rec = upstream dataset record (prompt, instruction_id_list, kwargs). Returns (strict, per, loose)."""
    lib = IFB if task == "ifbench" else IFE
    if response is None:
        n = len(rec["instruction_id_list"])
        return False, [False] * n, False
    out = []
    for fn in (lib.test_instruction_following_strict, lib.test_instruction_following_loose):
        # fresh kwargs per call: IFBench's strict edits inp.kwargs in place
        # None-valued kwargs dropped for both checks: IFBench's strict drops them in place on the shared input before
        # its loose check runs (run_eval.py order); IFEval's upstream input_data.jsonl carries none
        kw = [{a: b for a, b in dict(k).items() if b is not None} for k in rec["kwargs"]]
        inp = lib.InputExample(key=rec["key"], instruction_id_list=list(rec["instruction_id_list"]),
                               prompt=rec["prompt"], kwargs=kw)
        o = fn(inp, {rec["prompt"]: response})
        out.append((bool(o.follow_all_instructions), [bool(x) for x in o.follow_instruction_list]))
    return out[0][0], out[0][1], out[1][0]


# ---------------------------------------------------------------- OMEGA `omega` (OLMES)
def _olmes_functions():
    src = (UP / "olmes" / "utils.py").read_text()
    tree = ast.parse(src)
    ns = {"re": re}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "extract_answer":
            exec(compile(ast.Module(body=[node], type_ignores=[]), "olmes_utils", "exec"), ns)
    em_src = (UP / "olmes" / "exact_match.py").read_text()
    ns2 = {}
    exec(compile(em_src, "olmes_exact_match", "exec"), ns2)
    # the task's metric_kwargs, read from configs/tasks.py text (the f-string block of omega_*:0-shot-chat)
    cfg = (UP / "olmes" / "configs_tasks.py").read_text()
    i = cfg.index('TASK_CONFIGS[f"omega_{broad_cate}_{sub_cate}_{target_split}:0-shot-chat"]')
    j = cfg.index('"metric_kwargs": {', i) + len('"metric_kwargs": ')
    # the dict literal: walk Python tokens from its "{" to the matching "}" (braces inside strings are not OPs)
    import io
    import tokenize
    depth, end = 0, None
    lines = cfg[j:].splitlines(keepends=True)
    for tok in tokenize.generate_tokens(io.StringIO("".join(lines)).readline):
        if tok.type == tokenize.OP and tok.string == "{":
            depth += 1
        elif tok.type == tokenize.OP and tok.string == "}":
            depth -= 1
            if depth == 0:
                row, col = tok.end
                end = sum(len(x) for x in lines[: row - 1]) + col
                break
    mk = ast.literal_eval(cfg[j:j + end])  # a dict literal of regex strings and a float
    return ns["extract_answer"], ns2["exact_match_hf_evaluate"], mk


OLMES_EXTRACT, OLMES_EM, OMEGA_MK = _olmes_functions()


def omega_extract(continuation):
    """oe_eval/tasks/oe_eval_tasks/omega.py GenericTask._extract_answer (answer_regexes set), re-typed by me."""
    output = re.sub(r"(\d),(\d)", r"\1\2", continuation)
    res = re.sub("\\.\\s*$", "", output).strip()
    for left, right in [("$", "$"), ("\\(", "\\)"), ("**", "**"), ("***", "***"), ("\\[", "\\]"), ("\\[\n", "\n\\]")]:
        res = re.sub(f"{re.escape(left)}(.*){re.escape(right)}", "\\1", res).strip()
    cfg = {"metric_kwargs": OMEGA_MK}
    return OLMES_EXTRACT(res, task_config=cfg)


def omega_grade(text, label):
    ans = answer_of(text)
    if ans is None:
        return False, ""
    ex = omega_extract(ans)
    flex = ex["answer"]  # model_answer_flex: kept whatever answer_format_correct is (cutoff applies to exact_match)
    em = OLMES_EM(predictions=[flex], references=[str(label)], ignore_case=True, ignore_punctuation=False)
    return bool(em["exact_match"] == 1.0), flex


# ---------------------------------------------------------------- OMEGA `rl` (open-instruct MathVerifier)
def _math_utils():
    # math_utils imports stdlib + sympy (+ antlr via sympy.parsing.latex) and open_instruct.logger_utils (a logger
    # factory only): stub that one module, load the rest as fetched
    import logging
    pkg = sys.modules.setdefault("open_instruct", types.ModuleType("open_instruct"))
    lu = types.ModuleType("open_instruct.logger_utils")
    lu.setup_logger = lambda name=None, *a, **k: logging.getLogger(name or "oi")
    sys.modules["open_instruct.logger_utils"] = lu
    pkg.logger_utils = lu
    return _load("oi_math_utils_rv", UP / "oi" / "math_utils.py")


MU = _math_utils()


def _mathverifier_src():
    """MathVerifier.__call__'s body from ground_truth_utils.py, extracted by `ast` and turned into a function of
    (prediction, label) so it runs exactly as written there (names resolved against math_utils)."""
    src = (UP / "oi" / "ground_truth_utils.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MathVerifier":
            for f in node.body:
                if isinstance(f, ast.FunctionDef) and f.name == "__call__":
                    return ast.get_source_segment(src, f)
    raise RuntimeError("MathVerifier.__call__ not found")


MV_SRC = _mathverifier_src()


class _VR:  # stand-in for VerificationResult(score=...)
    def __init__(self, score, **kw):
        self.score = score


def _make_mv():
    import textwrap
    body = textwrap.dedent(MV_SRC)
    ns = {"re": re, "VerificationResult": _VR, "Any": object, "Optional": object, "List": list, "Dict": dict,
          "Union": object}
    for name in dir(MU):
        if not name.startswith("__"):
            ns[name] = getattr(MU, name)
    exec(compile(body, "mathverifier_call", "exec"), ns)
    call = ns["__call__"]

    def mv(prediction, label):
        r = call(None, tokenized_prediction=[], prediction=prediction, label=label, query=None)
        return float(r.score) > 0

    return mv


MV = _make_mv()
_POOL = cf.ThreadPoolExecutor(max_workers=1)


def rl_grade(text, label):
    """The RL reward path: MathVerifier in a worker thread (is_equiv's signal timeout cannot be installed there)."""
    return bool(_POOL.submit(MV, text, str(label)).result())


def rl_grade_main(text, label):
    """Diagnostic: the same on the main thread (sympy is_equiv live)."""
    return bool(MV(text, str(label)))
