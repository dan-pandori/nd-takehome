#!/usr/bin/env python3
"""Index the stored olmo-ifomega IFBench samples used as trace sources: one row per stored sample with its grade and
the token position where its thinking ends (`</think>` located in the stored ids). Writes
artifacts/olmo_transplant/src/index.jsonl (no text)."""
import gzip
import json
import sys

sys.path.insert(0, "olmo_transplant")
from tok import Tok, ids_of, think_end

S = "artifacts/olmo_transplant/src"
JOBS = ["F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb", "F_dpo_ifb"]


def main():
    t = Tok()
    with open(f"{S}/index.jsonl", "w") as out:
        for j in JOBS:
            g = {}
            for ln in open(f"{S}/{j}_graded.jsonl"):
                r = json.loads(ln)
                g[(r["pid"], r["chunk"], r["i"])] = r
            n = 0
            for ln in gzip.open(f"{S}/{j}.jsonl.gz", "rt"):
                r = json.loads(ln)
                ids = ids_of(r)
                te = think_end(t, ids)
                gr = g[(r["pid"], r["chunk"], r["i"])]
                row = {"job": j, "pid": r["pid"], "model": r["model"], "chunk": r["chunk"], "i": r["i"],
                       "n_tok": r["n_tok"], "finish": r["finish"], "strict": gr["strict"], "loose": gr["loose"],
                       "think_k": te[0] if te else None, "think_tail": te[2].decode() if te else None,
                       "n_think_markers": r["text"].count("</think>"),
                       "answer_words": len(r["text"].split("</think>")[-1].split()) if te else None}
                out.write(json.dumps(row) + "\n")
                n += 1
            print(j, n, flush=True)


if __name__ == "__main__":
    main()
