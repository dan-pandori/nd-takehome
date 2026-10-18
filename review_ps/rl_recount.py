"""Reviewer recount of RL's own proofs per ladder from create-or-elicit's cumulative found_16.jsonl (bucket), with the
reviewer's classifier. Every line is JSON-parsed (no text prefilter); proofs with a DN line are classified (pruned).
usage: python3 rl_recount.py <arm> <found_file>"""
import gzip
import json
import sys
import time
from collections import Counter
from nd import parse_prompt, Proof
from cls import classify

arm, fn = sys.argv[1], sys.argv[2]
tg = [json.loads(l) for l in open("../data/ladder/rl_targets.jsonl")]
th = [json.loads(l) for l in gzip.open("out/thm_rl_targets.jsonl.gz", "rt")]
info = {r["name"]: (r["prompt"], t) for r, t in zip(tg, th)}
t0 = time.time()
new, red, work, temp, free, neg, unp, bad_round, dn_any = (Counter() for _ in range(9))
seen = set()
dup = 0
first_sc = {}
import random
rng = random.Random(sum(map(ord, arm)) * 7919)
res_w, res_r = [], []   # reservoir samples: working-reductio proofs, any-reductio proofs
nw = nr = 0
not_target = 0
prompt_mismatch = 0
for line in open(fn):
    x = json.loads(line)
    r = x.get("round")
    if not isinstance(r, int) or r < 1 or r > 16:
        bad_round[str(r)] += 1
        continue
    h = hash((x["name"], x["proof"]))
    if h in seen:
        dup += 1
    seen.add(h)
    new[r] += 1
    if x["name"] not in info:
        not_target += 1
        continue
    prompt, t = info[x["name"]]
    if x.get("prompt") and x["prompt"] != prompt:
        prompt_mismatch += 1
    try:
        p, c = parse_prompt(prompt)
        P = Proof(p, c, x["proof"])
    except Exception:
        unp[r] += 1
        continue
    if not any(P.L[k]["rule"] == "DN" for k in P.order):
        continue
    dn_any[r] += 1
    o = classify(p, c, x["proof"], P=P)
    if "contradiction" not in o["uses"]:
        continue
    red[r] += 1
    nr += 1
    item = {"name": x["name"], "prompt": prompt, "proof": x["proof"], "round": r, "work": "contradiction" in o["work"]}
    if len(res_r) < 60:
        res_r.append(item)
    elif rng.random() < 60 / nr:
        res_r[rng.randrange(60)] = item
    if "contradiction" in o["work"]:
        nw += 1
        if len(res_w) < 120:
            res_w.append(item)
        elif rng.random() < 120 / nw:
            res_w[rng.randrange(120)] = item
        work[r] += 1
        free[r] += ("contradiction", "free") in o["sub"]
        neg[r] += ("contradiction", "neg_goal") in o["sub"]
        if t["sc_sem"]:
            first_sc[x["name"]] = min(r, first_sc.get(x["name"], 99))
    else:
        temp[r] += 1
R = range(1, 17)
out = {"arm": arm, "lines": sum(new.values()) + sum(bad_round.values()), "dup_lines": dup, "bad_round": dict(bad_round),
       "not_target": not_target, "prompt_mismatch": prompt_mismatch, "unparsable": sum(unp.values()),
       "new_by_round": {r: new[r] for r in R}, "dn_by_round": {r: dn_any[r] for r in R},
       "reductio_by_round": {r: red[r] for r in R}, "working_by_round": {r: work[r] for r in R},
       "template_only_by_round": {r: temp[r] for r in R}, "free_working_by_round": {r: free[r] for r in R},
       "neg_goal_working_by_round": {r: neg[r] for r in R}, "sigma_cov_first_working_round": first_sc,
       "secs": round(time.time() - t0, 1)}
json.dump(out, open(f"out/rl_{arm}.json", "w"), indent=1)
with gzip.open(f"out/rl_sample_{arm}.jsonl.gz", "wt") as fh:
    for it in res_w + res_r:
        fh.write(json.dumps(it) + "\n")
w = out["working_by_round"]
print(f"{arm}: lines {out['lines']} dup {dup} unparsable {out['unparsable']} not_target {not_target} prompt_mismatch {prompt_mismatch} | "
      f"new r1 {new[1]} total {sum(new.values())} | reductio total {sum(red.values())} working r1 {w[1]} r2-16 {sum(w[r] for r in range(2, 17))} "
      f"| σ-cov targets with working reductio by r16 {len(first_sc)} (r1 {sum(1 for v in first_sc.values() if v == 1)}) | {out['secs']} s", flush=True)
