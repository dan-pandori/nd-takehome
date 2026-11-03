#!/usr/bin/env python3
"""Build likelihood-scoring items (prompt ids + response ids) from sampled jobs.

Selects samples graded correct (`--grade rl`, default) from the given jobs, optionally only for `--pids`, at most
`--cap` per (job, pid) and `--max_per_job` per job (random with a fixed seed), and writes score_ll.py input rows:
key = job|pid|chunk|i, prompt_ids, resp_ids (base64 int32), plus pid, job, model.

Usage: ll_items.py --jobs j1,j2 --tokenizer <dir> --out items.jsonl [--pids a,b|@file] [--cap 8] [--max_per_job 0]
"""
import argparse
import base64
import gzip
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample import prompt_ids  # noqa: E402

A = Path("artifacts/olmo_pilot")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pids", default=None)
    ap.add_argument("--cap", type=int, default=8)
    ap.add_argument("--max_per_job", type=int, default=0)
    ap.add_argument("--grade", default="rl")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.tokenizer)
    probs = {r["pid"]: r for r in (json.loads(ln) for ln in open("olmo_pilot/problems.jsonl"))}
    pids = None
    if args.pids:
        pids = set(open(args.pids[1:]).read().split() if args.pids.startswith("@") else args.pids.split(","))
    rng = random.Random(args.seed)
    n_out = 0
    with open(args.out, "w") as g:
        for job in args.jobs.split(","):
            ok = set()
            for ln in open(A / "graded" / f"{job}.jsonl"):
                r = json.loads(ln)
                if r.get(args.grade) and (pids is None or r["pid"] in pids):
                    ok.add((r["pid"], r["chunk"], r["i"]))
            by_pid = defaultdict(list)
            for k in sorted(ok):
                by_pid[k[0]].append(k)
            keep = set()
            for pid, ks in by_pid.items():
                keep.update(rng.sample(ks, min(args.cap, len(ks))) if args.cap else ks)
            if args.max_per_job and len(keep) > args.max_per_job:
                keep = set(rng.sample(sorted(keep), args.max_per_job))
            with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
                for ln in f:
                    r = json.loads(ln)
                    k = (r["pid"], r["chunk"], r["i"])
                    if k not in keep:
                        continue
                    p = prompt_ids(tok, probs[r["pid"]]["problem"])
                    g.write(json.dumps({"key": f"{job}|{r['pid']}|{r['chunk']}|{r['i']}", "job": job, "model": r["model"],
                                        "pid": r["pid"], "finish": r["finish"],
                                        "prompt_ids": base64.b64encode(np.asarray(p, dtype=np.int32).tobytes()).decode(),
                                        "resp_ids": r["ids"]}) + "\n")
                    n_out += 1
    print(f"{n_out} items -> {args.out}")


if __name__ == "__main__":
    main()
