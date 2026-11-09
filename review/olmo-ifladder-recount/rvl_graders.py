"""IF graders for the reviewer's re-grade of run olmo-ifladder (my own driver around the upstream checkers; the IF
part of my olmo-iffu kit's rvi_graders.py, unchanged in substance).

Upstream code is my own fetch (gh api, pinned commits) under ~/review/oiffu_rv/upstream (linked as
~/review/oifl_rv/upstream), byte-compared with the run's vendored copies by rvl_provenance.py:
  IFBench  allenai/IFBench @ cd189a9c (ifbench/, evaluation_lib.py, ifbench/data/IFBench_test.jsonl)
  IFEval   google-research instruction_following_eval @ e6890f85 (+ data/input_data.jsonl)
Strict / loose: the package's own test_instruction_following_strict / _loose on the answer (text after the last
'</think>', stripped), with the ORIGINAL prompt and kwargs of the upstream dataset record (never the hinted prompt).
langdetect is seeded 0.
"""
import importlib.util
import os
import sys

from rvl_core import SCR

UP = SCR / "upstream"
os.environ.setdefault("NLTK_DATA", str(SCR / "nltk_data"))

import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0

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
        # fresh kwargs per call (IFBench's strict edits inp.kwargs in place); None-valued kwargs dropped for both
        kw = [{a: b for a, b in dict(k).items() if b is not None} for k in rec["kwargs"]]
        inp = lib.InputExample(key=rec["key"], instruction_id_list=list(rec["instruction_id_list"]),
                               prompt=rec["prompt"], kwargs=kw)
        o = fn(inp, {rec["prompt"]: response})
        out.append((bool(o.follow_all_instructions), [bool(x) for x in o.follow_instruction_list]))
    return out[0][0], out[0][1], out[1][0]
