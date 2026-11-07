#!/usr/bin/env python3
"""Answer lengths with and without test 2's hint (run olmo-iffu) -> olmo_iffu/lengths_hint.csv.

Without the hint: olmo-ifomega's fixed-phase draws of the same prompts (`dpo` 16, `s2300` 8 per prompt; bucket files
artifacts/olmo_ifomega/samples/F_{dpo,s2300}_{ifb,ife}.jsonl.gz, fetched with fetch_artifacts.py). With the hint:
artifacts/olmo_iffu/samples/T2*_{dpo,s2300}.jsonl.gz. Words = whitespace split of the answer (text after the last
</think>, stripped; no answer counts as missing). One row per prompt x model x condition: n, answers, median words,
share <= 60 words, median response tokens.
"""
import csv
import gzip
import json
import statistics
from pathlib import Path

PROBS = {}
for f in ("olmo_iffu/problems_hint.jsonl", "olmo_iffu/problems_hint2c.jsonl"):
    if Path(f).exists():
        for l in open(f):
            r = json.loads(l)
            PROBS[r["pid"]] = r


def answer_of(text):
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def rows(path):
    try:
        with gzip.open(path, "rt") as f:
            for l in f:
                try:
                    yield json.loads(l)
                except json.JSONDecodeError:
                    return
    except (EOFError, OSError):
        return


def main():
    src = {("unhinted", m): [f"artifacts/olmo_ifomega/samples/F_{m}_{t}.jsonl.gz" for t in ("ifb", "ife")]
           for m in ("dpo", "s2300")}
    for m in ("dpo", "s2300"):
        src[("hinted", m)] = [str(p) for p in sorted(Path("artifacts/olmo_iffu/samples").glob(f"T2*_{m}.jsonl.gz"))]
    acc = {}
    for (cond, m), files in src.items():
        for fp in files:
            for r in rows(fp):
                if r["pid"] not in PROBS:
                    continue
                a = answer_of(r["text"])
                acc.setdefault((r["pid"], m, cond), []).append((None if a is None else len(a.split()), r["n_tok"]))
    out = []
    for (pid, m, cond), v in sorted(acc.items()):
        w = [x for x, _ in v if x is not None]
        out.append({"pid": pid, "model": m, "condition": cond, "n": len(v), "answers": len(w),
                    "words_median": statistics.median(w) if w else "", "share_le60": round(sum(x <= 60 for x in w) / len(w), 3) if w else "",
                    "tokens_median": statistics.median(t for _, t in v)})
    with open("olmo_iffu/lengths_hint.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        wr.writeheader()
        wr.writerows(out)
    print(f"lengths_hint.csv: {len(out)} rows")


if __name__ == "__main__":
    main()
