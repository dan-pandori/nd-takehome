"""Lean re-check of every counted / searched proof of the run, from stored literal ND text (reviewer harness)."""
import gzip
import json
import random
from collections import Counter
from nd import parse_prompt, Proof
from lean import render, check

rng = random.Random(11)
groups = {}   # name -> list of (prem, concl, body, meta)
struct = Counter()


def add(g, prompt, proof, meta=None, bound=None, banned=None):
    p, c = parse_prompt(prompt)
    P = Proof(p, c, proof)
    ok, why = P.check()
    if not ok:
        struct[(g, "my ND check fails")] += 1
    if bound is not None and len(P.order) > bound:
        struct[(g, f"longer than {bound}")] += 1
    if banned is not None and any(P.L[k]["rule"] == banned for k in P.order):
        struct[(g, f"uses banned {banned}")] += 1
    groups.setdefault(g, []).append((p, c, render(p, c, proof), meta))


for fn, bound in (("k12_min990", 14), ("tb_schema", 14), ("textbook72", 14)):
    for r in map(json.loads, open(f"../data/ps/search/{fn}.checked.jsonl")):
        if r.get("proof"):
            add("search_" + fn, r["prompt"], r["proof"], {"name": r["name"], "lean_ok": r.get("lean_ok")}, bound)
for fn in ("k12_nec594", "charles_base", "textbook72"):
    for r in map(json.loads, open(f"../data/ps/nec/{fn}.checked.jsonl")):
        if r["free"] and r["free"].get("proof"):
            add("nec_free_" + fn, r["prompt"], r["free"]["proof"], {"name": r["name"], "lean_ok": r["free"].get("lean_ok")}, 12)
        for b, v in (r.get("ban") or {}).items():
            if v and v.get("proof"):
                add("nec_ban_" + fn, r["prompt"], v["proof"], {"name": r["name"], "ban": b, "lean_ok": v.get("lean_ok")}, 12, b)
for r in map(json.loads, open("../data/ps/in/charles/charles_base_full.jsonl")):
    add("charles_reference", r["prompt"], r["reference_proof"], {"name": r["name"]})


def sample(g, fn, field, n):
    op = gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)
    rows = [json.loads(l) for l in op]
    rows = [r for r in rows if r.get(field)]
    for r in (rng.sample(rows, n) if n < len(rows) else rows):
        add(g, r["prompt"], r[field], {"name": r.get("name")})


sample("gen_k12", "../data/ps/in/train_k12.jsonl.gz", "proof", 1000)
sample("gen_cap6", "../data/ps/in/train_depth3_f0_a1.jsonl.gz", "proof", 300)
sample("gen_k12ko", "../data/ps/in/train_k12ko.jsonl.gz", "proof", 300)
sample("gen_k12dose1", "../data/ps/in/train_k12dose1.jsonl.gz", "proof", 300)
sample("gen_rl_targets", "../data/ladder/rl_targets.jsonl", "gen_proof", 300)
sample("gen_transfer", "../data/ladder/transfer.jsonl", "gen_proof", 300)
sample("gen_holdout250", "../data/bs/holdout250.jsonl", "gen_proof", 1000)

out = {"struct": {f"{a} | {b}": v for (a, b), v in struct.items()}, "groups": {}}
for g, items in groups.items():
    res = check([(p, c, b) for p, c, b, _ in items], progress=g)
    rej = [(m, why) for (_, _, _, m), (ok, why) in zip(items, res) if not ok]
    flag_mismatch = sum(1 for (_, _, _, m), (ok, _) in zip(items, res) if m and "lean_ok" in m and m["lean_ok"] != ok)
    out["groups"][g] = {"n": len(items), "accepted": sum(ok for ok, _ in res), "rejected": len(rej),
                        "reasons": dict(Counter(w for _, w in rej)), "stored_flag_mismatch": flag_mismatch,
                        "rejected_names": [m.get("name") if m else None for m, _ in rej][:50]}
    print(g, {k: v for k, v in out["groups"][g].items() if k != "rejected_names"}, flush=True)
print("structural:", out["struct"])
json.dump(out, open("out/recheck.json", "w"), indent=1)
