#!/usr/bin/env python3
"""Grade sampled responses the way Olmo 3.1 RL-Zero-Math's RL reward did.

Primary grade `rl`: open-instruct's MathVerifier (verbatim body below, from ground_truth_utils.py at
bb58c664fb2dd2fd776c17b533b799653e2771e4) applied to the response decoded with skip_special_tokens=True, run in a
worker thread. That is how RL computed the reward: `async_call` runs `__call__` via `loop.run_in_executor`, so
`is_equiv`'s signal-based timeout cannot be installed (signal only works in the main thread), the ValueError is
caught by `is_equiv`'s `except Exception`, and only `hendrycks_is_equiv` can return True.

Secondary grade `main`: the same function in the main thread, where sympy's `is_equiv` is live (what an offline
evaluation calling MathVerifier directly would report).

Diagnostic grade `ansline`: the integer on the last "Answer:" line (or in the last \\boxed{}), compared as an integer
with the ground truth. Format-robust; used only to separate answer-format effects from solving.

Usage: grade.py <samples.jsonl.gz> <problems.jsonl> <out.jsonl>   (out: one row per sample, no text)
"""
import concurrent.futures as cf
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oi_math_utils import (  # noqa: E402
    get_unnormalized_answer,
    hendrycks_is_equiv,
    is_equiv,
    last_boxed_only_string,
    normalize_final_answer,
    remove_boxed,
)


def math_verifier(prediction: str, label: str) -> bool:
    """MathVerifier.__call__ at bb58c66, verbatim apart from returning a bool instead of VerificationResult."""
    raw_answer = prediction
    all_answers = []

    # Attempt extraction from \boxed{}.
    boxed_answer = last_boxed_only_string(raw_answer)
    if boxed_answer is not None:
        try:
            boxed_answer = remove_boxed(boxed_answer)
        except AssertionError:
            boxed_answer = None
    if boxed_answer is not None:
        all_answers.append(boxed_answer)

    # Attempt extraction via Minerva format.
    minerva_answer = normalize_final_answer(get_unnormalized_answer(raw_answer))
    if minerva_answer is not None and minerva_answer != "[invalidanswer]":
        all_answers.append(minerva_answer)

    # Attempt extraction from the last LaTeX-formatted answer.
    if not all_answers:
        dollars = [m.start() for m in re.finditer(r"\$", raw_answer)]
        if len(dollars) > 1:
            answer = normalize_final_answer(raw_answer[dollars[-2] + 1 : dollars[-1]])
            all_answers.append(answer)

    # Fallback to the full output.
    if not all_answers:
        all_answers.append(normalize_final_answer(prediction))
        # also provide original string in case normalization fails
        all_answers.append(prediction)

    # Compare each candidate answer to the ground truth.
    for answer in all_answers:
        if is_equiv(answer, label) or hendrycks_is_equiv(answer, label):
            return True
    return False


_POOL = cf.ThreadPoolExecutor(max_workers=1)


def grade_rl(prediction: str, label: str) -> bool:
    """The RL reward: MathVerifier run off the main thread (as loop.run_in_executor did)."""
    return _POOL.submit(math_verifier, prediction, label).result()


_INT = re.compile(r"-?\d[\d,]*")


def ansline(prediction: str):
    """Integer on the last 'Answer:' line, else in the last \\boxed{}, else None."""
    cand = None
    lines = [ln for ln in prediction.splitlines() if "Answer:" in ln or "answer:" in ln]
    if lines:
        tail = re.split(r"[Aa]nswer:", lines[-1])[-1]
        m = _INT.findall(tail.replace("\\,", "").replace("{,}", ""))
        if m:
            cand = m[0]
    if cand is None:
        b = last_boxed_only_string(prediction)
        if b is not None:
            m = _INT.findall(b)
            if m:
                cand = m[0]
    if cand is None:
        return None
    try:
        return int(cand.replace(",", ""))
    except ValueError:
        return None


def grade_one(text: str, label: str, main: bool = True) -> dict:
    a = ansline(text)
    out = {"rl": grade_rl(text, label), "ansline": (a is not None and str(a) == str(int(label))) if re.fullmatch(r"-?\d+", label.strip()) else None,
           "ans": a}
    if main:
        out["main"] = math_verifier(text, label)
    return out


def main():
    samples, problems, out = sys.argv[1:4]
    labels = {}
    for ln in open(problems):
        r = json.loads(ln)
        labels[r["pid"]] = str(r["answer"])
    n = 0
    with gzip.open(samples, "rt") as f, open(out, "w") as g:
        for ln in f:
            r = json.loads(ln)
            gr = grade_one(r["text"], labels[r["pid"]])
            row = {k: r[k] for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish")}
            row.update(gr)
            g.write(json.dumps(row) + "\n")
            n += 1
    print(f"graded {n} -> {out}")


if __name__ == "__main__":
    main()
