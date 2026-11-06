"""Reviewer graders, run olmo-ifomega. Each grade runs the upstream source itself (my own fetches at the pinned commits,
under upstream/), not olmo_ifomega/grade.py:

  IF   : allenai/IFBench @ cd189a9c evaluation_lib.test_instruction_following_{strict,loose};
         google-research instruction_following_eval @ e6890f85 (the official IFEval checker), the same two functions.
  omega: OLMES @ 5a51f502: GenericTask._extract_answer (oe_eval/tasks/oe_eval_tasks/omega.py) with the
         omega_*:0-shot-chat metric_kwargs (oe_eval/configs/tasks.py), oe_eval.tasks.utils.extract_answer, and
         ExactMatch's exact_match_flex path (model_answer_flex vs label through exact_match_hf_evaluate, ignore_case).
         The function bodies are taken from the files by `ast` and executed unmodified.
  rl   : open-instruct @ 7e780f2fea MathVerifier through VerifierFunction.async_call (a worker thread), as RL ran it.
  own  : my own final-answer read-out (diagnostic): the last \\boxed{...} of the answer (brace-matched), else nothing;
         compared with the label after stripping $, spaces, \\left/\\right and a trailing period, numerically for numbers.
Run python from ~/review/oif_venv (pod versions: nltk 3.9.2, langdetect 1.0.9, emoji 2.15.0, syllapy 0.8.0,
immutabledict 4.2.2, absl-py 2.3.1, sympy 1.13.3, antlr4 4.11.0)."""
import ast
import asyncio
import importlib.util
import os
import re
import shutil
import sys
import tempfile
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(HERE, "upstream")

# ---------------------------------------------------------------- IF
sys.path.insert(0, os.path.join(UP, "ifbench"))
sys.path.insert(0, os.path.join(UP, "ife"))
import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0  # the official code leaves it unseeded; seeded so a re-grade reproduces
_spec = importlib.util.spec_from_file_location("ifbench_evaluation_lib", os.path.join(UP, "ifbench", "evaluation_lib.py"))
IFB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IFB)
from instruction_following_eval import evaluation_lib as IFE  # noqa: E402


def if_check(task, prob, response, loose=False):
    """Official prompt-level check of `response`; returns (all_followed, per-constraint list)."""
    lib = IFB if task == "ifbench" else IFE
    kw = [dict(k) for k in prob["kwargs"]]
    if task == "ifeval":
        # google's code passes kwargs straight to build_description; IFEval's jsonl has no None values, but guard
        kw = [{a: b for a, b in k.items() if b is not None} for k in kw]
    inp = lib.InputExample(key=prob.get("key"), instruction_id_list=list(prob["instruction_id_list"]),
                           prompt=prob["prompt"], kwargs=kw)
    if loose:
        # IFBench's strict pass drops None kwargs in place before the loose pass runs (run_eval.py order)
        inp.kwargs[:] = [{a: b for a, b in k.items() if b is not None} for k in inp.kwargs]
    fn = lib.test_instruction_following_loose if loose else lib.test_instruction_following_strict
    out = fn(inp, {prob["prompt"]: response})
    return bool(out.follow_all_instructions), [bool(x) for x in out.follow_instruction_list]


# ---------------------------------------------------------------- OMEGA (OLMES)
_OL = os.path.join(UP, "olmes")


def _func_src(path, name, cls=None):
    tree = ast.parse(open(path).read())
    nodes = tree.body
    if cls:
        nodes = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    node = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(open(path).read(), node)


def _omega_metric_kwargs():
    path = os.path.join(_OL, "oe_eval_configs_tasks.py")
    src = open(path).read()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript):
            t = ast.get_source_segment(src, n.targets[0])
            if t == 'TASK_CONFIGS[f"omega_{broad_cate}_{sub_cate}_{target_split}:0-shot-chat"]':
                d = n.value
                co = d.values[[ast.literal_eval(k) for k in d.keys].index("chat_overrides")]
                mk = co.values[[ast.literal_eval(k) for k in co.keys].index("metric_kwargs")]
                return ast.literal_eval(mk)
    raise RuntimeError("omega config not found")


OMEGA_METRIC_KWARGS = _omega_metric_kwargs()
_ns = {"re": re, "np": np, "string": __import__("string")}
exec(_func_src(os.path.join(_OL, "oe_eval_tasks_utils.py"), "extract_answer"), _ns)
exec(_func_src(os.path.join(_OL, "oe_eval_dependencies_hf_evaluate_exact_match.py"), "exact_match_hf_evaluate"), _ns)
_ns["extract_answer_up"] = _ns["extract_answer"]
_ext_src = _func_src(os.path.join(_OL, "oe_eval_tasks_oe_eval_tasks_omega.py"), "_extract_answer", cls="GenericTask")
exec("import textwrap\n" + "def _mk():\n    extract_answer = extract_answer_up\n" +
     "\n".join("    " + ln for ln in __import__("textwrap").dedent(_ext_src).splitlines()) + "\n    return _extract_answer\n",
     _ns)
_omega_extract = _ns["_mk"]()


class _Self:
    task_config = {"metric_kwargs": OMEGA_METRIC_KWARGS}


def omega_grade(answer, label):
    """(credited, extracted answer, answer_format_correct) on the pre-registered answer text (None -> not credited)."""
    if answer is None:
        return False, "", 0.0
    ex = _omega_extract(_Self(), answer)
    flex = ex["answer"]
    em = _ns["exact_match_hf_evaluate"](predictions=[flex], references=[label], regexes_to_ignore=None,
                                        ignore_case=True, ignore_punctuation=False)["exact_match"]
    return bool(em == 1.0), flex, ex["answer_format_correct"]


# ---------------------------------------------------------------- RL MathVerifier (open-instruct 7e780f2fea)
def _build_oi_pkg():
    d = tempfile.mkdtemp(prefix="oi_pkg_")
    p = os.path.join(d, "open_instruct")
    os.makedirs(os.path.join(p, "IFEvalG"))
    for f in ("ground_truth_utils.py", "math_utils.py"):
        shutil.copy(os.path.join(UP, "open_instruct", f), os.path.join(p, f))
    stubs = {
        "__init__.py": "",
        "logger_utils.py": "import logging\ndef setup_logger(name=None):\n    return logging.getLogger(name)\n",
        "if_functions.py": "IF_FUNCTIONS_MAP = {}\n",
        "IFEvalG/__init__.py": "",
        "IFEvalG/instructions_registry.py": "INSTRUCTION_DICT = {}\n",
        "judge_utils.py": "EXTRACTOR_MAP = {}\nJUDGE_PROMPT_MAP = {}\nPRICE_PER_TOKEN = {}\n"
                          "def build_messages(*a, **k):\n    raise RuntimeError('stub')\n",
        "utils.py": "def extract_final_answer(x):\n    return x\n",
    }
    for k, v in stubs.items():
        with open(os.path.join(p, k), "w") as f:
            f.write(v)
    lit = types.ModuleType("litellm")

    async def acompletion(*a, **k):
        raise RuntimeError("stub")
    lit.acompletion = acompletion
    sys.modules.setdefault("litellm", lit)
    sys.path.insert(0, d)


_build_oi_pkg()
from open_instruct import ground_truth_utils as _gtu  # noqa: E402

_MV = _gtu.MathVerifier()


def rl_grade(text, label):
    async def go():
        return await _MV.async_call(tokenized_prediction=[], prediction=text, label=label, query=None)
    return asyncio.run(go()).score > 0


# ---------------------------------------------------------------- own final-answer read-out (diagnostic)
def last_boxed(s):
    k = s.rfind("\\boxed")
    if k < 0:
        return None
    j = s.find("{", k)
    if j < 0:
        return None
    depth, i = 0, j
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[j + 1:i]
        i += 1
    return None


def _norm(x):
    x = x.strip().strip("$").strip()
    x = re.sub(r"\\left|\\right|\\!|\\,|\\;|\s+", "", x)
    x = x.rstrip(".")
    x = re.sub(r"^\\text\{(.*)\}$", r"\1", x)
    return x


def own_grade(answer, label):
    if answer is None:
        return False, None
    b = last_boxed(answer)
    if b is None:
        return False, None
    a, l = _norm(b), _norm(label)
    if a == l:
        return True, b
    try:
        return abs(float(a) - float(l)) < 1e-9 * max(1.0, abs(float(l))), b
    except ValueError:
        return False, b


if __name__ == "__main__":
    # unit checks (each line must print its expectation)
    print(omega_grade("Therefore, the final answer is \\boxed{12}.", "12")[0], "expect True")
    print(omega_grade("so \\boxed{12} hmm \\boxed{13}", "13"), "-> OLMES takes the first boxed after no prefix? see")
    print(omega_grade("The answer is 7", "7")[0], "expect True (prefix regex)")
    print(omega_grade(None, "7")[0], "expect False")
    print(rl_grade("so \\boxed{70}", "70"), "expect True")
    print(rl_grade("\\boxed{70} later \\boxed{71}", "70"), "expect False")
    p = {"key": "x", "prompt": "Write in all lowercase.", "instruction_id_list": ["change_case:english_lowercase"],
         "kwargs": [{}]}
    print(if_check("ifeval", p, "hello world"), "expect (True, [True])")
    print(if_check("ifeval", p, "Hello world"), "expect (False, [False])")
    print(own_grade("x \\boxed{\\frac{1}{2}}", "\\frac{1}{2}"), own_grade("\\boxed{3.50}", "3.5"))
    print(OMEGA_METRIC_KWARGS)
