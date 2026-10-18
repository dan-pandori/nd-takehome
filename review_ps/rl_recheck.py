"""Lean re-check of RL proofs counted by the run (create-or-elicit found files): per ladder 120 sampled working-reductio
proofs + 60 sampled any-reductio proofs (reservoir samples saved by rl_recount.py)."""
import glob
import gzip
import json
from collections import Counter
from nd import parse_prompt
from lean import render, check

out = {}
for fn in sorted(glob.glob("out/rl_sample_*.jsonl.gz")):
    arm = fn.split("rl_sample_")[1].split(".")[0]
    items = [json.loads(l) for l in gzip.open(fn, "rt")]
    srcs = []
    for it in items:
        p, c = parse_prompt(it["prompt"])
        srcs.append((p, c, render(p, c, it["proof"])))
    res = check(srcs)
    w = [ok for it, (ok, _) in zip(items, res) if it["work"]]
    out[arm] = {"n": len(items), "accepted": sum(ok for ok, _ in res), "n_working": len(w), "working_accepted": sum(w),
                "reasons": dict(Counter(why for ok, why in res if not ok))}
    print(arm, out[arm], flush=True)
json.dump(out, open("out/rl_recheck.json", "w"), indent=1)
