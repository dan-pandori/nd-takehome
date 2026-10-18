"""Negative / positive controls for the reviewer's Lean harness (run BEFORE the real re-check)."""
import gzip
import json
import random
from nd import parse_prompt, Proof
from lean import render, check

rng = random.Random(7)
K = [json.loads(l) for l in gzip.open("../data/ps/in/train_k12.jsonl.gz", "rt")]
sample = rng.sample(K, 600)
pos, sw, fl, tr, so = [], [], [], [], []
by_np = {}
for r in K[:20000]:
    p, c = parse_prompt(r["prompt"])
    by_np.setdefault(len(p), []).append((p, c, r["thm"]))
for r in sample[:300]:
    p, c = parse_prompt(r["prompt"])
    pos.append((p, c, render(p, c, r["proof"])))
for r in sample[300:500]:
    p, c = parse_prompt(r["prompt"])
    body = render(p, c, r["proof"])
    while True:
        p2, c2, t2 = rng.choice(by_np[len(p)])
        if t2 != r["thm"]:
            break
    sw.append((p2, c2, body))
nflip = 0
for r in K[1000:]:
    if len(fl) >= 200:
        break
    p, c = parse_prompt(r["prompt"])
    P = Proof(p, c, r["proof"])
    cand = [k for k in P.order if P.L[k]["rule"] in ("ORI1", "ORI2", "ANDE1", "ANDE2")]
    if not cand:
        continue
    k = rng.choice(cand)
    fl.append((p, c, render(p, c, r["proof"], flip=k)))
for r in sample[500:600]:
    p, c = parse_prompt(r["prompt"])
    body = render(p, c, r["proof"])
    tr.append((p, c, body.rsplit(" ; ", 1)[0] if " ; " in body else "skip"))
for r in sample[:50]:
    p, c = parse_prompt(r["prompt"])
    so.append((p, c, "sorry"))
items = pos + sw + fl + tr + so
res = check(items, progress="controls")
off = 0
out = {}
for name, grp in (("positive_k12", pos), ("statement_swap", sw), ("or_and_flip", fl), ("truncated", tr), ("sorry", so)):
    rr = res[off:off + len(grp)]
    off += len(grp)
    out[name] = {"n": len(grp), "accepted": sum(ok for ok, _ in rr),
                 "reasons": dict(__import__("collections").Counter(w for _, w in rr))}
    print(name, out[name])
json.dump(out, open("out/controls.json", "w"), indent=1)
