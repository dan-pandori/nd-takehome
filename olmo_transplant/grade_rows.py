#!/usr/bin/env python3
"""Grade this run's sampled answers with olmo_ifomega/grade.py (unchanged, imported): the IFBench official checker,
strict (primary) and loose, on the answer = the text after the last `</think>` of (inserted thinking + sampled
answer). The inserted thinking always ends in `</think>`, so the graded text is "</think>" + the sampled text.
Usage: grade_rows.py <samples.jsonl.gz> <out.jsonl>   (one row per sample, no text; complete rows only)"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "olmo_ifomega"))
from grade import grade_if  # noqa: E402

KEEP = ("rid", "pid", "cond", "writer", "trace", "cut", "i", "n_tok", "finish", "prefix_len", "natural", "job")


def main():
    src, out = sys.argv[1], sys.argv[2]
    probs = {json.loads(l)["pid"]: json.loads(l) for l in open("olmo_ifomega/problems.jsonl")}
    n = 0
    with open(out, "w") as g:
        with gzip.open(src, "rt") as f:
            try:
                for ln in f:
                    r = json.loads(ln)
                    p = probs[r["pid"]]
                    gr = grade_if(p["task"], "</think>" + r["text"], p)
                    g.write(json.dumps({**{k: r[k] for k in KEEP if k in r}, **gr,
                                        "answer_words": len(r["text"].rsplit("</think>", 1)[-1].split()),
                                        "extra_think_end": "</think>" in r["text"]}) + "\n")
                    n += 1
            except (EOFError, json.JSONDecodeError):
                pass  # a file still being written: complete rows only
    print(f"graded {n} rows -> {out}")


if __name__ == "__main__":
    main()
