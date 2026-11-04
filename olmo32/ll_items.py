#!/usr/bin/env python3
"""Items for the likelihood check (pre-registration, Reported quantities): every rl-credited RL-checkpoint solution on
the reach candidates (fixed phase and confirmation), dpo's own rl-credited solutions on the same problems, and a
reference set of dpo's own correct solutions on the other headline problems (the first rl-credited fixed-phase sample
per problem). Prompt ids = the sampler's olmo_thinker prompt (rebuilt with its tokenizer and template on the pod).
Usage (pod): ll_items.py <out.jsonl> [pid ...]   (default pid: aime2025_28)
"""
import base64
import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample import prompt_ids  # noqa: E402

A = Path("artifacts/olmo32")
out, pids = sys.argv[1], (sys.argv[2:] or ["aime2025_28"])
from transformers import AutoTokenizer  # noqa: E402

tok = AutoTokenizer.from_pretrained("/workspace/models/tok")
probs = {r["pid"]: r for r in (json.loads(ln) for ln in open("olmo32/problems.jsonl"))}
excl = {r["pid"] for r in csv.DictReader(open("olmo32/exclusions.csv"))}
jobs = {j["job"]: j for j in csv.DictReader(open("olmo32/jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")}
items, ref_done = [], set()
for job, j in jobs.items():
    f = A / "samples" / f"{job}.jsonl.gz"
    g = A / "graded" / f"{job}.jsonl"
    if not f.exists() or not g.exists():
        continue
    grades = {(r["pid"], r["chunk"], r["i"]): r for r in map(json.loads, open(g))}
    with gzip.open(f, "rt") as fh:
        for ln in fh:
            r = json.loads(ln)
            gr = grades[(r["pid"], r["chunk"], r["i"])]
            if not gr["rl"]:
                continue
            if r["pid"] in pids:
                group = "rl_on_candidate" if j["model"] != "dpo" else "dpo_on_candidate"
            elif j["model"] == "dpo" and j["phase"] == "fixed" and r["pid"] not in excl and r["pid"] not in ref_done:
                group = "dpo_reference"
                ref_done.add(r["pid"])
            else:
                continue
            items.append({"key": f"{job}|{r['pid']}|{r['chunk']}|{r['i']}", "group": group, "gen_model": j["model"],
                          "pid": r["pid"], "final": gr["final"],
                          "prompt_ids": base64.b64encode(np.asarray(prompt_ids(tok, probs[r["pid"]]["problem"]),
                                                                    dtype=np.int32).tobytes()).decode(),
                          "resp_ids": r["ids"]})
with open(out, "w") as f:
    for it in items:
        f.write(json.dumps(it) + "\n")
from collections import Counter  # noqa: E402
print(f"{len(items)} items -> {out}", Counter((it["group"], it["gen_model"]) for it in items))
