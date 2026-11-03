#!/usr/bin/env python3
"""My own overlap scan of the 120 AIME problems against Dolci-RL-Zero-Math-7B @ 93b5e498 (13,314 prompts).

Independent of olmo_pilot/contam.py. Three measures per (problem, prompt):
  w8   word 8-gram containment |G8(P) & G8(D)| / |G8(P)|, tokens = [a-z]+ | \\d+ | \\[a-z]+ (LaTeX command names kept)
  m8   the same with every number replaced by '#'   (catches digit-changed variants)
  c50  character 50-gram containment on text with all whitespace removed, lower-cased
For each problem: best prompt by m8 (ties -> w8), its w8/c50, the answer of that prompt, and the best w8 match.
Writes out/contam_dolci.csv.
"""
import csv
import re
from collections import defaultdict

import pyarrow.parquet as pq

import rv_core as R

TOK = re.compile(r"\\[a-z]+|[a-z]+|\d+")


def toks(t, mask=False):
    ts = TOK.findall(t.lower())
    return ["#" if (mask and x.isdigit()) else x for x in ts]


def ngrams(ts, n):
    return {tuple(ts[i:i + n]) for i in range(len(ts) - n + 1)}


def cgrams(t, n=50):
    s = re.sub(r"\s+", "", t.lower())
    return {s[i:i + n] for i in range(0, max(len(s) - n + 1, 0))}


def main():
    t = pq.read_table(R.ROOT / "data" / "olmo_pilot" / "dolci_rl_zero_math_7b_93b5e498.parquet").to_pylist()
    print("dolci rows", len(t), "columns", list(t[0].keys()))
    probs = R.problems(with_probe=False)
    P = {p: (ngrams(toks(r["problem"]), 8), ngrams(toks(r["problem"], True), 8), cgrams(r["problem"])) for p, r in probs.items()}
    # inverted index on masked 8-grams and on word 8-grams
    inv_m, inv_w = defaultdict(set), defaultdict(set)
    for p, (w8, m8, _) in P.items():
        for g in m8:
            inv_m[g].add(p)
        for g in w8:
            inv_w[g].add(p)
    best_m = {p: (0.0, 0.0, -1) for p in P}
    best_w = {p: (0.0, -1) for p in P}
    for j, r in enumerate(t):
        text = r["prompt"]
        dm = ngrams(toks(text, True), 8)
        dw = ngrams(toks(text), 8)
        hit_m, hit_w = defaultdict(int), defaultdict(int)
        for g in dm:
            for p in inv_m.get(g, ()):
                hit_m[p] += 1
        for g in dw:
            for p in inv_w.get(g, ()):
                hit_w[p] += 1
        for p, h in hit_m.items():
            cm = h / max(len(P[p][1]), 1)
            cw = hit_w.get(p, 0) / max(len(P[p][0]), 1)
            if (cm, cw) > best_m[p][:2]:
                best_m[p] = (cm, cw, j)
        for p, h in hit_w.items():
            cw = h / max(len(P[p][0]), 1)
            if cw > best_w[p][0]:
                best_w[p] = (cw, j)
    rows = []
    for p in sorted(P):
        cm, cw, j = best_m[p]
        c50 = (len(P[p][2] & cgrams(t[j]["prompt"])) / max(len(P[p][2]), 1)) if j >= 0 else 0.0
        bw, jw = best_w[p]
        rows.append({"pid": p, "set": probs[p]["set"], "m8": round(cm, 3), "w8_at_m8best": round(cw, 3), "c50_at_m8best": round(c50, 3),
                     "m8best_idx": j, "m8best_answer": (str(t[j]["ground_truth"]) if j >= 0 else ""),
                     "same_answer": (j >= 0 and str(t[j]["ground_truth"]).strip() == str(probs[p]["answer"]).strip()),
                     "w8": round(bw, 3), "w8best_idx": jw})
    with open(R.OUT / "contam_dolci.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r["m8"] >= 0.3 or r["w8"] >= 0.3 or r["c50_at_m8best"] >= 0.3:
            print(r)


if __name__ == "__main__":
    main()
