"""Fixed-phase statistics (reviewer): unbiased pass@k with 10,000-resample problem bootstrap, matched-k (k = 8)
expected entries / exits vs dpo with intervals, observed candidate sets under both readings of 'union', lengths and
cut-offs, paired MDD. Own code."""
import collections, json, os, sys
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = C.rows(); probs = C.problems()
head = [p["pid"] for p in probs if p["pid"] not in C.excluded()]
allp = [p["pid"] for p in probs]
fx = collections.defaultdict(list)
for r in rs:
    if r["job"].startswith("F_"):
        fx[(r["model"], r["pid"])].append(r)

def pk(n, c, k):
    return 1.0 - comb(n - c, k) / comb(n, k) if n - c >= k else 1.0

out = {"n_head": len(head)}
rng = np.random.default_rng(12345)
B = 10000
idx = rng.integers(0, len(head), size=(B, len(head)))
res = {}
for g in ("rl", "final", "main"):
    for m in C.MODELS:
        n = 16 if m == "dpo" else 8
        for k in [1, 2, 4, 8] + ([16] if m == "dpo" else []):
            v = np.array([pk(len(fx[(m, p)]), sum(r[g] for r in fx[(m, p)]), k) for p in head])
            bs = v[idx].mean(axis=1)
            res[(g, m, k)] = v
            out[f"pass@{k}_{g}_{m}"] = [round(v.mean(), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]
# all-60 variant for reference
for g in ("rl", "final"):
    for m in C.MODELS:
        v = np.array([pk(len(fx[(m, p)]), sum(r[g] for r in fx[(m, p)]), 1) for p in allp])
        out[f"pass@1_{g}_{m}_all60"] = round(v.mean(), 4)
# paired differences of pass@1 vs dpo
for g in ("rl", "final"):
    for m in ("s0100", "s0750", "s2300"):
        d = res[(g, m, 1)] - res[(g, "dpo", 1)]
        bs = d[idx].mean(axis=1)
        out[f"dpass@1_{g}_{m}-dpo"] = [round(d.mean(), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4), "se", round(float(bs.std()), 4), "mdd80", round(2.8 * float(bs.std()), 4)]
# matched-k entries / exits at k = 8
for g in ("rl", "final", "union"):
    for m in ("s0100", "s0750", "s2300"):
        def cc(mm, p):
            return sum((r["rl"] or r["final"]) if g == "union" else r[g] for r in fx[(mm, p)])
        a = np.array([pk(8, cc(m, p), 8) for p in head])
        b = np.array([pk(16, cc("dpo", p), 8) for p in head])
        ent = a * (1 - b); exi = (1 - a) * b
        be = ent[idx].sum(axis=1); bx = exi[idx].sum(axis=1)
        out[f"entries8_{g}_{m}"] = [round(ent.sum(), 3), round(float(np.percentile(be, 2.5)), 3), round(float(np.percentile(be, 97.5)), 3)]
        out[f"exits8_{g}_{m}"] = [round(exi.sum(), 3), round(float(np.percentile(bx, 2.5)), 3), round(float(np.percentile(bx, 97.5)), 3)]
        out[f"obs_entries_{g}_{m}"] = sorted(p for p in head if cc(m, p) > 0 and cc("dpo", p) == 0)
        out[f"obs_exits_{g}_{m}"] = sorted(p for p in head if cc(m, p) == 0 and cc("dpo", p) > 0)
# candidate sets
def credited(mm, p, g):
    return sum(r[g] for r in fx[(mm, p)])
R = {}; V = {}
for g in ("rl", "final"):
    R[g] = sorted(p for p in head if credited("dpo", p, g) == 0 and any(credited(m, p, g) > 0 for m in ("s0100", "s0750", "s2300")))
    V[g] = sorted(p for p in head if credited("dpo", p, g) > 0 and credited("s2300", p, g) == 0)
cu = lambda mm, p: sum(r["rl"] or r["final"] for r in fx[(mm, p)])
R["either_credited"] = sorted(p for p in head if cu("dpo", p) == 0 and any(cu(m, p) > 0 for m in ("s0100", "s0750", "s2300")))
V["either_credited"] = sorted(p for p in head if cu("dpo", p) > 0 and cu("s2300", p) == 0)
R["union_of_sets"] = sorted(set(R["rl"]) | set(R["final"])); V["union_of_sets"] = sorted(set(V["rl"]) | set(V["final"]))
# also the excluded problem, for the record
R_all = sorted(p for p in allp if credited("dpo", p, "rl") == 0 and any(credited(m, p, "rl") > 0 for m in ("s0100", "s0750", "s2300")))
out["R"] = R; out["V"] = V; out["R_rl_incl_excluded"] = R_all
for p in sorted(set(sum(R.values(), [])) | set(sum(V.values(), []))):
    out[f"cell_{p}"] = {m: {g: credited(m, p, g) for g in ("rl", "final", "doubly", "main")} for m in C.MODELS}
# lengths / cut-offs, fixed phase, headline set and all 60
for m in C.MODELS:
    xs = [r for p in head for r in fx[(m, p)]]
    toks = np.array([r["n_tok"] for r in xs])
    out[f"tokens_{m}"] = {"n": len(xs), "mean": round(toks.mean()), "median": float(np.median(toks)),
                          "cut_share": round(float(np.mean([r["finish"] == "length" for r in xs])), 4),
                          "mean_correct_rl": round(float(np.mean([r["n_tok"] for r in xs if r["rl"]]))),
                          "think_end_share_uncut": round(float(np.mean([r["think_end"] for r in xs if r["finish"] == "stop"])), 4),
                          "boxed_after_think_share_uncut": round(float(np.mean([r["final_src"] == "boxed" for r in xs if r["finish"] == "stop"])), 4),
                          "rl_ne_final": int(sum(r["rl"] != r["final"] for r in xs)),
                          "rl_only": int(sum(r["rl"] and not r["final"] for r in xs)),
                          "final_only": int(sum(r["final"] and not r["rl"] for r in xs)),
                          "main_ne_rl": int(sum(r["main"] != r["rl"] for r in xs))}
json.dump(out, open(os.path.join(C.HERE, "out", "stats.json"), "w"), indent=1)
for k, v in out.items():
    print(k, v)
