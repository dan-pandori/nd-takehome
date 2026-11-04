#!/usr/bin/env python3
"""Grade sampled responses of run olmo-ifomega.

The answer of a response is the text after its last "</think>", stripped of surrounding whitespace (as RL's IF reward
strips it); a response without "</think>" has no answer.

IF tasks (official checkers, vendored unmodified in olmo_ifomega/vendor/, see its README):
  ifbench -> allenai/IFBench @ cd189a9c (`ifbench_evaluation_lib`); ifeval -> google-research
  instruction_following_eval @ e6890f85. Grades:
  `strict` (primary): the checker's test_instruction_following_strict on the answer: every constraint followed.
                      `per` = its per-constraint list. No answer -> every constraint fails.
  `loose`  (diagnostic): the checker's test_instruction_following_loose on the answer.
  `rlview` (diagnostic): strict on open-instruct's remove_thinking_section(text) (7e780f2fea), i.e. what RL's IF
                      reward graded: the text after the last "</think>", or the whole text when there is none.
  langdetect is seeded (DetectorFactory.seed = 0) so that re-grading reproduces; the official code leaves it unseeded.
OMEGA tasks (omega_in, omega_out):
  `omega` (primary): OMEGA's exact-match grade as AI2 implements it for the Olmo 3 evaluations (OLMES @ 5a51f502,
                      task omega_*:0-shot-chat: GenericTask._extract_answer + oe_eval.tasks.utils.extract_answer with
                      that task's regexes, metric exact_match_flex, ignore_case) applied to the answer.
  `rl` (second): open-instruct's MathVerifier as the Think RL ran it (olmo32/grade.py: whole response, worker thread).
  `doubly` = omega and rl.
`success(task, text, prob)` is the extension's stopping criterion: IF strict; OMEGA doubly.
Usage: grade.py <samples.jsonl.gz> <problems.jsonl> <out.jsonl>   (out: one row per sample, no text)
"""
import dataclasses
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import langdetect  # noqa: E402

langdetect.DetectorFactory.seed = 0
import ifbench_evaluation_lib as ifb_lib  # noqa: E402
from instruction_following_eval import evaluation_lib as ife_lib  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("olmo32_grade", HERE.parent / "olmo32" / "grade.py")
_g32 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g32)
grade_rl = _g32.grade_rl  # olmo32/grade.py: MathVerifier as RL ran it

IF_TASKS = ("ifbench", "ifeval")
OMEGA_TASKS = ("omega_in", "omega_out")


def answer_of(text):
    # stripped, as RL's remove_thinking_section strips: the template puts "\n\n" after </think>, and exact-format
    # checks (e.g. IFBench format:options) fail on it (fixed 2026-11-04 21:25 UTC, before any fixed-phase grading)
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def remove_thinking_section(prediction):
    """open-instruct ground_truth_utils.remove_thinking_section @ 7e780f2fea, verbatim."""
    prediction = prediction.replace("<|assistant|>", "").strip()
    prediction = prediction.split("</think>")[-1]
    prediction = prediction.replace("<answer>", "").replace("</answer>", "")
    return prediction.strip()


def _if_check(task, prob, response, loose=False):
    lib = ifb_lib if task == "ifbench" else ife_lib
    # None-valued kwargs dropped: IFBench's strict check does this in place on the shared inputs before its loose
    # check runs (run_eval.py), so this reproduces the official order; IFEval's kwargs carry no None values (checked)
    kw = [{a: b for a, b in dict(k).items() if b is not None} for k in prob["kwargs"]]
    inp = lib.InputExample(key=prob.get("key"), instruction_id_list=list(prob["instruction_id_list"]),
                           prompt=prob["prompt"], kwargs=kw)
    fn = lib.test_instruction_following_loose if loose else lib.test_instruction_following_strict
    out = fn(inp, {prob["prompt"]: response})
    return bool(out.follow_all_instructions), [bool(x) for x in out.follow_instruction_list]


def grade_if(task, text, prob):
    ans = answer_of(text)
    n = len(prob["instruction_id_list"])
    if ans is None:
        strict, per, loose = False, [False] * n, False
    else:
        strict, per = _if_check(task, prob, ans)
        loose = _if_check(task, prob, ans, loose=True)[0]
    rv = remove_thinking_section(text)
    rlview = _if_check(task, prob, rv)[0] if rv else False
    return {"strict": strict, "per": per, "loose": loose, "rlview": rlview, "think_end": ans is not None}


# ---- OMEGA: OLMES @ 5a51f502 (oe_eval/configs/tasks.py omega_*:0-shot-chat metric_kwargs; oe_eval/tasks/utils.py
# extract_answer; oe_eval/tasks/oe_eval_tasks/omega.py GenericTask._extract_answer), copied verbatim in substance.
OMEGA_KW = {
    "answer_format_regex": "Therefore, the final answer is \\\\boxed\\{(.*)\\}",
    "answer_prefix_regexes": ["(?i)Therefore,? the final answer is", "(?i)Therefore,? the answer is",
                              "(?i)the final answer is", "(?i)the answer is", "(?i)answer is", "(?i)answer is:",
                              "(?i)answer:"],
    "answer_regexes": ["[\\s\\S]*?\\\\boxed\\{(.*?)\\}[\\s\\S]*?", "(.*)\\.?"],
}


def olmes_extract_answer(continuation, answer_format_regex=None, answer_regexes=None, prefix_regexes=None,
                         use_last_prefix_match=True, use_last_raw_match=True):
    answer_format_correct = 0.0
    answer_string = ""
    if answer_format_regex:
        matches = re.findall(answer_format_regex, continuation)
        if matches:
            answer_string = matches[-1]
            answer_format_correct = 1.0
    # (answer_regexes_templates: not set for OMEGA)
    if (answer_string == "") and prefix_regexes:
        for idx, prefix_regex in enumerate(prefix_regexes):
            matches_list = list(re.finditer(prefix_regex, continuation))
            if len(matches_list) > 0:
                match = matches_list[-1] if use_last_prefix_match else matches_list[0]
                answer_text = continuation[match.end():].strip().strip(".")
                answer_match = re.findall("(" + "|".join(answer_regexes) + ")", answer_text)
                if answer_match:
                    res_tuple = answer_match[0]
                    if not isinstance(res_tuple, str):
                        answer_string = res_tuple[0]
                        for res1 in res_tuple[1:]:
                            if res1 != "":
                                answer_string = res1
                    else:
                        answer_string = res_tuple
                    if answer_string != "":
                        answer_format_correct = 1.0 if idx == 0 else 0.5
                        break
    if answer_string == "":
        for idx, answer_regex in enumerate(answer_regexes):
            ans_match = re.findall(answer_regex, continuation)
            if ans_match:
                answer_string = ans_match[-1] if use_last_raw_match else ans_match[0]
                answer_format_correct = 0.2 if idx == 0 else 0.1
                break
    return {"answer": answer_string, "answer_format_correct": answer_format_correct}


def omega_extract(continuation):
    output = re.sub(r"(\d),(\d)", r"\1\2", continuation)
    res = re.sub("\\.\\s*$", "", output).strip()
    for left, right in [("$", "$"), ("\\(", "\\)"), ("**", "**"), ("***", "***"), ("\\[", "\\]"),
                        ("\\[\n", "\n\\]")]:
        res = re.sub(f"{re.escape(left)}(.*){re.escape(right)}", "\\1", res).strip()
    return olmes_extract_answer(res, OMEGA_KW["answer_format_regex"], OMEGA_KW["answer_regexes"],
                                OMEGA_KW["answer_prefix_regexes"])


def grade_omega(text, prob):
    label = str(prob["answer"])
    ans = answer_of(text)
    ex = omega_extract(ans) if ans is not None else {"answer": "", "answer_format_correct": 0.0}
    omega = ans is not None and ex["answer"].lower() == label.lower()  # exact_match_flex, ignore_case
    rl = grade_rl(text, label)
    return {"omega": omega, "rl": rl, "doubly": omega and rl, "omega_ans": ex["answer"][:200],
            "omega_fmt": ex["answer_format_correct"], "think_end": ans is not None}


def grade_one(task, text, prob):
    if task in IF_TASKS:
        return grade_if(task, text, prob)
    if task in OMEGA_TASKS:
        return grade_omega(text, prob)
    return {"think_end": "</think>" in text}  # rlif (Stage 0): lengths only


def success(task, text, prob):
    g = grade_one(task, text, prob)
    return bool(g.get("strict", g.get("doubly", False)))


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
            row = {k: r[k] for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish")}
            row["task"] = p["task"]
            row.update(grade_one(p["task"], r["text"], p))
            g.write(json.dumps(row) + "\n")
            n += 1
    print(f"graded {n} -> {out}")


if __name__ == "__main__":
    sys.exit(main())
