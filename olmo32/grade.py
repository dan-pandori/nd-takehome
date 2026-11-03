#!/usr/bin/env python3
"""Grade sampled responses of the Olmo 3 / 3.1 Think 32B models.

`rl` (primary): open-instruct's MathVerifier as the Think RL run computed its reward. Body verbatim from
ground_truth_utils.py at 7e780f2fea (2025-11-22; identical to the copy the olmo-rlzero-pilot vendored at bb58c66),
applied to the whole response decoded with skip_special_tokens=True (thinking included: <think> / </think> are
ordinary text in this tokenizer) and run in a worker thread, as `async_call` -> `run_in_executor` ran it. There
`is_equiv`'s signal-based timeout cannot be installed, so only `hendrycks_is_equiv` can return True.

`main` (diagnostic): the same function on the main thread, where sympy's `is_equiv` is live.

`final` (secondary, pre-registered): the final stated answer only. The text after the last "</think>" (no
"</think>" -> not credited); in it, the last \\boxed{...}, else the last line containing "answer" (any case); the
last integer in that span must equal the official answer.

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
    """MathVerifier.__call__ at 7e780f2fea, verbatim apart from returning a bool instead of VerificationResult."""
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


_INT = re.compile(r"-?\d+")
_WRAP = re.compile(r"\\(?:text|textbf|mathrm|mathbf|displaystyle)\s*\{([^{}]*)\}")


def _clean(span: str) -> str:
    s = _WRAP.sub(r"\1", span)
    for x in ("$", "\\,", "\\!", "\\;", "\\ ", "{,}", "^\\circ", "^{\\circ}", "\\%", "%", "\\left", "\\right"):
        s = s.replace(x, "")
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    return re.sub(r"\s+", "", s).rstrip(".")


def _boxed_int(inner: str):
    """A boxed answer counts only if it is an integer, or `<expression> = <integer>` (e.g. m+n=204)."""
    s = _clean(inner)
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    m = re.fullmatch(r".*=(-?\d+)", s)
    return int(m.group(1)) if m else None


def _last_int(span: str):
    m = _INT.findall(_clean(span))
    return int(m[-1]) if m else None


def final_answer(text: str):
    """(has_think_end, where, value): the integer the response states as its final answer, or None."""
    if "</think>" not in text:
        return False, None, None
    tail = text.rsplit("</think>", 1)[1]
    b = last_boxed_only_string(tail)
    if b is not None:
        try:
            inner = remove_boxed(b)
        except AssertionError:
            inner = b
        return True, "boxed", _boxed_int(inner)
    lines = [ln for ln in tail.splitlines() if "answer" in ln.lower()]
    if lines:
        return True, "line", _last_int(lines[-1].lower().rsplit("answer", 1)[1])
    return True, None, None


def grade_final(text: str, label: str) -> bool:
    v = final_answer(text)[2]
    try:
        return v is not None and v == int(str(label).strip())
    except ValueError:
        return False


def grade_one(text: str, label: str, main: bool = True) -> dict:
    te, where, v = final_answer(text)
    out = {"rl": grade_rl(text, label), "final": grade_final(text, label), "think_end": te, "final_from": where,
           "final_ans": v}
    if main:
        out["main"] = math_verifier(text, label)
    return out


def doubly(text: str, label: str) -> bool:
    """Credited by both the primary (rl) and the secondary (final) grade: the extension's stopping criterion."""
    return grade_final(text, label) and grade_rl(text, label)


def main():
    samples, problems, out = sys.argv[1:4]
    labels = {}
    for ln in open(problems):
        r = json.loads(ln)
        labels[r["pid"]] = str(r["answer"])
    n = 0
    with gzip.open(samples, "rt") as f, open(out, "w") as g:
        for ln in f:
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                break  # truncated tail of a killed job
            gr = grade_one(r["text"], labels[r["pid"]])
            row = {k: r[k] for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish")}
            row.update(gr)
            g.write(json.dumps(row) + "\n")
            n += 1
    print(f"graded {n} -> {out}")


if __name__ == "__main__":
    main()
