"""IF strict / loose grading for the reviewer's re-grade of run olmo-transplant (my own driver).

Upstream code is my own fetch (gh api, IFBench @ cd189a9c2889526d8af901d2103fd3e1ffcea6df) under
~/review/otr_rv/upstream/ifbench, byte-compared with the run's vendored copy (out/provenance.txt). The checker's own
test_instruction_following_strict / _loose is called on the answer (text after the last '</think>', stripped) with
the ORIGINAL prompt / instruction ids / kwargs of the upstream IFBench_test.jsonl record (matched by key).
langdetect is seeded 0 (the run's grade.py seeds it; the upstream leaves it unseeded).
"""
import importlib.util
import json
import os
import sys

from rvt_core import SCR, answer_of

UP = SCR / "upstream" / "ifbench"
os.environ.setdefault("NLTK_DATA", str(SCR / "nltk_data"))

import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0
sys.path.insert(0, str(UP))  # package `ifbench`


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IFB = _load("rv_ifbench_evaluation_lib", UP / "evaluation_lib.py")
UPSTREAM = {}
for ln in open(UP / "IFBench_test.jsonl"):
    r = json.loads(ln)
    UPSTREAM[str(r["key"])] = r


def if_grade(rec, response):
    """rec = upstream record. Returns (strict, per, loose). response None -> all fail."""
    if response is None:
        n = len(rec["instruction_id_list"])
        return False, [False] * n, False
    out = []
    for fn in (IFB.test_instruction_following_strict, IFB.test_instruction_following_loose):
        # fresh kwargs per call (the strict check edits inp.kwargs in place); None-valued kwargs dropped for both
        kw = [{a: b for a, b in dict(k).items() if b is not None} for k in rec["kwargs"]]
        inp = IFB.InputExample(key=rec["key"], instruction_id_list=list(rec["instruction_id_list"]),
                               prompt=rec["prompt"], kwargs=kw)
        o = fn(inp, {rec["prompt"]: response})
        out.append((bool(o.follow_all_instructions), [bool(x) for x in o.follow_instruction_list]))
    return out[0][0], out[0][1], out[1][0]


def grade_text(rec, full_text):
    return if_grade(rec, answer_of(full_text))
