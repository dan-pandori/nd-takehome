#!/usr/bin/env python3
"""Grade sampled responses of run olmo-rlzero-if (IFBench, IFEval).

Answer = RL-Zero-IF's own extraction, open-instruct ground_truth_utils.remove_thinking_section at d928a7c (verbatim
below): the text after the last "</think>" (the whole response when there is none), "<answer>" / "</answer>"
removed, stripped. An empty answer fails every constraint (RL's reward scored it 0).

Grades (official checkers, vendored unmodified in olmo_ifomega/vendor/, see its README: IFBench @ cd189a9c, IFEval =
google-research instruction_following_eval @ e6890f85):
  strict (primary)   test_instruction_following_strict on the answer: every constraint followed; `per` = the list.
  loose  (secondary) test_instruction_following_loose on the answer.
  closed (diagnostic, olmo-ifomega's rule) strict, but a response without "</think>" fails.
  t1     (diagnostic, "first turn") strict on the extraction of the response cut before its first <|endoftext|>,
                     <|im_start|> or <|im_end|> token (sample row `t1_chars`): the reply a chat reader would see, for a
                     base that continues past its turn.
Flags: think_end ("</think>" present), ans_tag ("<answer>" present), cont (the response continues past a turn end:
<|im_start|> or <|im_end|> followed by more text), ans_chars.
langdetect is seeded (DetectorFactory.seed = 0) and `random` is re-seeded (0) before every check, so re-grades
reproduce (IFEval's keywords:letter_frequency draws a random letter when the letter is not a-z, e.g. ifeval_1122).
`success(task, text, prob)` = strict (the sequential extension's stopping count). Tasks other than ifbench / ifeval
(Stage 0's RL prompts) are not graded.
Usage: grade.py <samples.jsonl.gz> <problems.jsonl> <out.jsonl>   (out: one row per sample, no text)
"""
import ast
import gzip
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "olmo_ifomega" / "vendor"))

import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0
import ifbench_evaluation_lib as ifb_lib  # noqa: E402
from instruction_following_eval import evaluation_lib as ife_lib  # noqa: E402

IF_TASKS = ("ifbench", "ifeval")


def remove_thinking_section(prediction: str) -> str:
    """open-instruct ground_truth_utils.remove_thinking_section @ d928a7cd29, verbatim."""
    prediction = prediction.replace("<|assistant|>", "").strip()
    # remove thinking section from the prediction
    prediction = prediction.split("</think>")[-1]
    # remove answer tags from the prediction
    prediction = prediction.replace("<answer>", "").replace("</answer>", "")
    return prediction.strip()


def _kwargs(prob):
    kw = prob["kwargs"]
    return ast.literal_eval(kw) if isinstance(kw, str) else kw


def _ids(prob):
    ids = prob["instruction_id_list"]
    return ast.literal_eval(ids) if isinstance(ids, str) else ids


def _if_check(task, prob, response, loose=False):
    lib = ifb_lib if task == "ifbench" else ife_lib
    # None-valued kwargs dropped, as olmo_ifomega/grade.py (IFBench's run_eval drops them in place before its loose check)
    kw = [{a: b for a, b in dict(k or {}).items() if b is not None} for k in _kwargs(prob)]
    inp = lib.InputExample(key=prob.get("key"), instruction_id_list=list(_ids(prob)), prompt=prob["prompt"], kwargs=kw)
    fn = lib.test_instruction_following_loose if loose else lib.test_instruction_following_strict
    random.seed(0)
    out = fn(inp, {prob["prompt"]: response})
    return bool(out.follow_all_instructions), [bool(x) for x in out.follow_instruction_list]


def grade_if(task, text, prob, t1_chars=None):
    n = len(_ids(prob))
    ans = remove_thinking_section(text)
    if ans:
        strict, per = _if_check(task, prob, ans)
        loose = _if_check(task, prob, ans, loose=True)[0]
    else:
        strict, per, loose = False, [False] * n, False
    think_end = "</think>" in text
    g = {"strict": strict, "per": per, "loose": loose, "closed": strict and think_end, "think_end": think_end,
         "ans_tag": "<answer>" in text, "ans_chars": len(ans)}
    if t1_chars is not None and 0 <= t1_chars < len(text):
        a1 = remove_thinking_section(text[:t1_chars])
        g["t1"] = _if_check(task, prob, a1)[0] if a1 else False
        g["cont"] = bool(text[t1_chars:].strip())
    else:
        g["t1"], g["cont"] = strict, False
    return g


def grade_one(task, text, prob, t1_chars=None):
    if task in IF_TASKS:
        return grade_if(task, text, prob, t1_chars)
    return {}


def success(task, text, prob):
    return bool(grade_one(task, text, prob).get("strict", False))


def main():
    samples, problems, out = sys.argv[1:4]
    probs = {r["pid"]: r for r in map(json.loads, open(problems))}
    rows = []
    try:
        with gzip.open(samples, "rt") as f:
            for ln in f:
                rows.append(json.loads(ln))
    except (EOFError, json.JSONDecodeError):
        pass  # truncated tail of a killed job: complete rows only
    with open(out, "w") as g:
        n = 0
        for r in rows:
            p = probs[r["pid"]]
            row = {k: r.get(k) for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish", "stop_reason",
                                         "n_im_start", "n_im_end")}
            row["task"] = p["task"]
            row.update(grade_one(p["task"], r["text"], p, r.get("t1_chars")))
            g.write(json.dumps(row) + "\n")
            n += 1
    print(f"graded {n} -> {out}")


if __name__ == "__main__":
    sys.exit(main())
