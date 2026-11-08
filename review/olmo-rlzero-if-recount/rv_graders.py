"""Reviewer graders, run olmo-rlzero-if. The upstream checkers run as-is from my own fetches (fetch_upstream.sh):

  IFBench @ cd189a9c  evaluation_lib.test_instruction_following_{strict,loose} (ifbench/ package beside it);
  IFEval  = google-research instruction_following_eval @ e6890f85, the same two functions.

Answer = open-instruct remove_thinking_section @ d928a7c (rv_core), applied to the stored text; empty -> fail (RL's
IFEvalVerifier returns 0 for an empty answer). langdetect seeded; `random` re-seeded (0) before every check because
IFEval's letter-frequency check draws a random letter for a non a-z letter (my olmo-ifomega finding); `random_dep`
flags such constraints. Run with ~/review/oif_venv/bin/python (nltk 3.9.2, langdetect 1.0.9, emoji 2.15.0,
syllapy 0.8.0, immutabledict 4.2.2, absl-py 2.3.1)."""
import importlib.util
import os
import random
import sys

from rv_core import UP, remove_thinking_section

sys.path.insert(0, os.path.join(UP, "ifbench"))
sys.path.insert(0, os.path.join(UP, "ife"))
import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0
_spec = importlib.util.spec_from_file_location("ifbench_evaluation_lib", os.path.join(UP, "ifbench", "evaluation_lib.py"))
IFB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IFB)
from instruction_following_eval import evaluation_lib as IFE  # noqa: E402


def _clean(kws):
    return [{a: b for a, b in dict(k or {}).items() if b is not None} for k in kws]


def if_check(task, prob, response, loose=False, seed=0):
    """Official prompt-level check of `response` -> (all followed, per-constraint list)."""
    lib = IFB if task == "ifbench" else IFE
    # IFBench's own strict pass drops None kwargs in place (and run_eval runs strict before loose); IFEval's jsonl has
    # none; dropping them first is therefore the official behaviour for both passes
    inp = lib.InputExample(key=prob.get("key"), instruction_id_list=list(prob["instruction_id_list"]),
                           prompt=prob["prompt"], kwargs=_clean(prob["kwargs"]))
    fn = lib.test_instruction_following_loose if loose else lib.test_instruction_following_strict
    if seed is not None:
        random.seed(seed)
    out = fn(inp, {prob["prompt"]: response})
    return bool(out.follow_all_instructions), [bool(x) for x in out.follow_instruction_list]


def random_dep(prob):
    """Constraints whose check draws from `random` (IFEval letter_frequency with a letter outside a-z)."""
    out = []
    for cid, kw in zip(prob["instruction_id_list"], _clean(prob["kwargs"])):
        if cid.endswith("letter_frequency"):
            let = kw.get("letter")
            if not let or len(let) > 1 or not ("a" <= let.lower() <= "z"):
                out.append(cid)
    return out


def grade(task, prob, text):
    """strict / loose / per on RL's extraction of `text`."""
    n = len(prob["instruction_id_list"])
    ans = remove_thinking_section(text)
    if not ans:
        return {"strict": False, "loose": False, "per": [False] * n, "ans_chars": 0}
    s, per = if_check(task, prob, ans)
    lo, _ = if_check(task, prob, ans, loose=True)
    return {"strict": s, "loose": lo, "per": per, "ans_chars": len(ans)}


if __name__ == "__main__":
    from rv_core import load_problems
    P = load_problems()
    p = P["ifeval_1122"] if "ifeval_1122" in P else next(v for v in P.values() if v["task"] == "ifeval")
    print(p["pid"], p["instruction_id_list"], random_dep(p))
    print(remove_thinking_section("<think>a</think> <answer>b</answer>"), "expect b")
    print(remove_thinking_section("no tags here "), "expect 'no tags here'")
    q = P["ifbench_0"]
    print(grade("ifbench", q, "kaleidoscope " + "nebula " * 2 + "whisper " * 3 + "labyrinth " * 5 + "paradox " * 7),
          "expect strict True")
    print(grade("ifbench", q, "kaleidoscope nebula"), "expect strict False")
