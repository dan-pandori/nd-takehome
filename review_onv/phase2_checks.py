#!/usr/bin/env python3
"""Phase-2 numeric checks of olmo-novelty statements against stored results (own code).
python3 review_onv/phase2_checks.py   (run from the repository root)"""
import csv, json
from collections import Counter
import numpy as np
import sys
sys.path.insert(0, "review_onv")
from corr import spearman, load_counts, arrays
from pathlib import Path

V = {(r["task"], r["grade"]): r for r in csv.DictReader(open("olmo_ifomega/verdict.csv"))}
reach_s = V[("ifbench", "strict")]["reach_s2300"].split()
reach_h = V[("ifbench", "hand")]["reach_s2300"].split()
ife_s = V[("ifeval", "strict")]["reach_s2300"].split()
R = {(r["model"], r["pid"]): r for r in csv.DictReader(open("olmo_ifomega/results.csv"))}
print("strict-reach", len(reach_s), "hand-reach", len(reach_h), "ifeval strict-reach", len(ife_s))


def loose(pids):
    out = []
    for p in pids:
        r = R[("dpo", p)]
        out.append((p, int(r["succ_loose"]), int(r["attempts"]), int(r["succ_strict"])))
    return out


L = loose(reach_s)
att = Counter(a for _, _, a, _ in L)
print("attempts on strict-reach dpo rows:", dict(att), "| strict succ all 0:", all(s == 0 for *_, s in L))
n = lambda f: sum(1 for x in L if f(x[1]))
print(f"dpo loose >=1: {n(lambda v: v >= 1)}, >=2: {n(lambda v: v >= 2)}, ==0: {n(lambda v: v == 0)}, ==1: {n(lambda v: v == 1)}, "
      f">=13: {n(lambda v: v >= 13)}, ==256: {n(lambda v: v == 256)}")
H = loose(reach_h)
print("hand-reach: loose >=2:", sum(1 for x in H if x[1] >= 2), "of", len(H))
E = loose(ife_s)
print("IFEval strict-reach loose:", [(p, v, a) for p, v, a, _ in E if v > 0])

# summed gain and share on dpo 0/16, on strict-reach; rho(x, RL)
cnt = load_counts(Path("."), "ifbench", "strict")
pids, c, s = arrays(cnt, "s2300")
g = s / 8 - c / 16
print("summed gain %.2f; on dpo 0/16 (%d prompts) %.2f (%.0f %%); on 49 strict-reach %.2f" % (
    g.sum(), (c == 0).sum(), g[c == 0].sum(), 100 * g[c == 0].sum() / g.sum(),
    sum(g[i] for i, p in enumerate(pids) if p in set(reach_s))))
rng = np.random.default_rng(3)
for rl in ("s2300", "s0750", "s0100"):
    pids, c, s = arrays(cnt, rl)
    vals = []
    for _ in range(2000):
        a = rng.hypergeometric(c, 16 - c, 8)
        vals.append(spearman(a / 8, s / 8))
    print(f"rho(x half-sample, {rl} rate) = {np.mean(vals):+.3f}")

# --- remaining numbers.md correlation cells
import math
from corr import per_type
rng = np.random.default_rng(11)
pids, c, s = arrays(cnt, "s2300")
vals = []
for _ in range(2000):
    a = rng.hypergeometric(c, 16 - c, 8); b = c - a
    sp = rng.permutation(s)
    vals.append(spearman((a > 0).astype(float), (sp > 0).astype(float) - (b > 0).astype(float)))
print("pass@8 random-pairing null (IFBench strict s2300): %.3f" % np.mean(vals))
m = c >= 1
x = c[m] / 16
print("dpo>=1/16 subset same-draws rho: %.3f" % spearman(x, s[m] / 8 - x))
cnt_e = load_counts(Path("."), "ifeval", "strict")
r = per_type(Path("."), cnt_e, "s2300", np.random.default_rng(12), "id", 8)
print("IFEval per constraint type pass@8: rho %.3f [%.3f, %.3f] same draws %.3f types %d" % (r["rho"], r["lo"], r["hi"], r["naive"], r["n_types"]))
# typical dpo IFBench draw length vs the E1_dpo_ifa reach-candidate draws used for the K estimate
toks = [float(R[("dpo", p)]["mean_tok_fixed"]) for p in pids]
print("dpo IFBench fixed-phase mean tokens per draw (218 prompts): %.0f (E1_dpo_ifa reach candidates: 5,442)" % np.mean(toks))

# --- C-7 definition sensitivity: one constraint type per prompt (its first instruction id), pass@8 split
from collections import defaultdict
P = {json.loads(l)["pid"]: json.loads(l) for l in open("olmo_ifomega/problems.jsonl")}
pids, c, s = arrays(cnt, "s2300")
g = defaultdict(list)
for j, p in enumerate(pids):
    g[P[p]["instruction_id_list"][0]].append(j)
idx = [np.array(v) for k, v in sorted(g.items()) if len(v) >= 2]
rng = np.random.default_rng(5)
vals = []
for _ in range(2000):
    a = rng.hypergeometric(c, 16 - c, 8); b = c - a
    x = (a > 0).astype(float); y = (s > 0).astype(float) - (b > 0).astype(float)
    vals.append(spearman([x[i].mean() for i in idx], [y[i].mean() for i in idx]))
print("C-7 variant, first instruction id only: %d types, rho %.3f" % (len(idx), np.mean(vals)))
