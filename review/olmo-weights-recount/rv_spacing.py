"""Reviewer (olmo-weights), phase 2: does per-step change / LR depend on the checkpoint spacing? For a chain with
members 0..K, the chord ||theta_{i+L} - theta_i|| for L = 1..4 intervals comes exactly from o2, dot_prev and lags 1-3
(as in rv_recount.S_sub); the chord from the stage start to member i is sqrt(o2_i). Prints the median over i of
(chord / ||theta_i||) / (steps) / LR. Usage: python3 rv_spacing.py ROOT"""
import math, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_load import load
D, J = load(sys.argv[1])
from collections import defaultdict
def chain_data(job, chain):
    d = D[job]
    iv = defaultdict(lambda: defaultdict(float))
    for r in d["iv"]:
        if r["chain"] == chain:
            o = iv[int(r["idx"])]; o["a"], o["b"] = r["a"], r["b"]
            for f in ("d2", "na2", "nb2"): o[f] += float(r[f])
    for r in d["st"]:
        if r["chain"] == chain:
            o = iv[int(r["idx"])]; o["o2"] += float(r["o2"]); o["dot_prev"] += float(r["dot_prev"])
    for r in d["lag"]:
        if r["chain"] == chain:
            iv[int(r["idx"])][f"lag{r['lag']}"] += float(r["dot"])
    return iv
def step(lab):
    p = lab.split("/"); return int(p[2]) if len(p) > 2 else None
def chords(iv, L):
    """||O_{i+L} - O_i||^2 for all i with i+L <= K (O_0 = 0)."""
    K = max(iv)
    o2 = {0: 0.0, **{i: iv[i]["o2"] for i in iv}}
    out = []
    for i in range(0, K - L + 1):
        j = i + L
        cross = 0.0
        for k in range(i + 1, j + 1):
            v = iv[k]["dot_prev"]
            for q in range(1, k - i):
                v -= iv[k][f"lag{q}"]
            cross += v
        c2 = o2[j] - o2[i] - 2 * cross
        na = iv[i + 1]["na2"]     # ||theta_i||^2
        out.append((i, j, math.sqrt(max(c2, 0) / na)))
    return out
for job, chain, lr, start_step in (("p32_rl", "rl", 2e-6, 0), ("p7_rl", "rl", 1e-6, 0)):
    iv = chain_data(job, chain)
    K = max(iv)
    labs = {0: iv[1]["a"], **{i: iv[i]["b"] for i in iv}}
    stp = {i: (0 if i == 0 else step(labs[i])) for i in labs}
    print(f"== {job} {chain}")
    for L in (1, 2, 3, 4):
        v = [r / (stp[j] - stp[i]) / lr for i, j, r in chords(iv, L) if stp.get(j) is not None and stp[j] and (i == 0 or stp[i]) is not None and labs[j].split('/')[1] == 'rl']
        n = [stp[j] - stp[i] for i, j, r in chords(iv, L) if labs[j].split('/')[1] == 'rl'][len(v) // 2]
        print(f"  spacing {L} interval(s) (~{n} steps): median per-step/LR {st.median(v):.2f} (n={len(v)})")
    na0 = iv[1]["na2"]
    for i in sorted(iv):
        s = step(labs[i])
        if s in (100, 200, 500, 1000, 1375, 1400, 2000, 2300) or labs[i].endswith("rlmain"):
            ss = s if s is not None else 1400
            print(f"  DPO -> {labs[i]} ({ss} steps): r = {math.sqrt(iv[i]['o2'] / na0):.3e}, per-step/LR {math.sqrt(iv[i]['o2'] / na0) / ss / lr:.2f}")
# SFT at 1,000 vs 2,000-4,000-step spacing (7B SFT, 5e-5 peak; mean LR over each chord)
def lin(peak, W, T):
    return lambda t: peak * t / W if t < W else peak * max(T - t, 0) / (T - W)
f7 = lin(5e-5, 0.03 * 45.4e9 / 1048576, 45.4e9 / 1048576)
iv = chain_data("p7_sft", "sft-dpo")
labs = {0: iv[1]["a"], **{i: iv[i]["b"] for i in iv}}
print("== p7_sft sft (1,000-step checkpoints)")
for L in (1, 2, 3, 4):
    v = []
    for i, j, r in chords(iv, L):
        if i == 0 or not labs[j].startswith("7B/sft/") or not labs[i].startswith("7B/sft/"):
            continue
        a, b = step(labs[i]), step(labs[j])
        m = sum(f7(t) for t in range(a + 1, b + 1)) / (b - a)
        v.append(r / (b - a) / m)
    print(f"  spacing {L} ({L * 1000} steps): median per-step/LR {st.median(v):.3f} (n={len(v)})")


# consecutive-change cosine at 1x and 2x checkpoint spacing: A = D_{i+1}+D_{i+2}, B = D_{i+3}+D_{i+4}
def cos2(job, chain, keep=lambda lab: True):
    iv = chain_data(job, chain)
    K = max(iv)
    c1, c2 = [], []
    for k in range(2, K + 1):
        if keep(iv[k]["b"]) and keep(iv[k]["a"]) and keep(iv[k - 1]["a"]):
            c1.append(iv[k]["lag1"] / math.sqrt(iv[k]["d2"] * iv[k - 1]["d2"]))
    for i in range(0, K - 3):
        a1, a2, b1, b2 = iv[i + 1], iv[i + 2], iv[i + 3], iv[i + 4]
        if not all(keep(x["b"]) and keep(x["a"]) for x in (a1, a2, b1, b2)):
            continue
        AA = a1["d2"] + a2["d2"] + 2 * a2["lag1"]
        BB = b1["d2"] + b2["d2"] + 2 * b2["lag1"]
        AB = b1["lag2"] + b2["lag3"] + b1["lag1"] + b2["lag2"]
        c2.append(AB / math.sqrt(AA * BB))
    return st.median(c1), len(c1), st.median(c2), len(c2)
print("== consecutive-change cosine (median) at 1x and 2x checkpoint spacing")
for job, chain, keep in (("p32_rl", "rl", lambda l: l.split('/')[1] == 'rl'), ("p7_rl", "rl", lambda l: l.split('/')[1] == 'rl'),
                         ("p7_sft", "sft-dpo", lambda l: l.startswith('7B/sft/')),
                         ("p32_sft", "sft-1e-4", lambda l: l.startswith('32B/sft1e-4/')),
                         ("b7_s2", "stage2", lambda l: l.startswith('7B/s2/')), ("b32_s3", "stage3", lambda l: l.startswith('32B/s3/')),
                         ("z7_math", "rlzero-math", lambda l: l.startswith('7B/zmath/') and 'main' not in l)):
    m1, n1, m2, n2 = cos2(job, chain, keep)
    print(f"  {job:8s} {chain:12s} 1x: {m1:+.3f} (n={n1})   2x: {m2:+.3f} (n={n2})")
