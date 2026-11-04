"""Phase-2 claim checks (reviewer): numbers quoted in run_olmo_think32b.md / numbers.md recomputed from my rows."""
import collections, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = C.rows(); out = []
# stated final answers of dpo's 240 extension samples on aime2025_28 (my final grader's value)
e = [r for r in rs if r["job"] == "E1a_dpo"]
out.append(f"E1a_dpo n={len(e)} stated final answers: " + json.dumps(collections.Counter(str(r['final_val']) for r in e).most_common()))
for job in ("C1_s0100", "C2_s0100", "C1_s0750", "C2_s0750", "C3_s0750", "C4_s0750", "C1_s2300"):
    x = [r for r in rs if r["job"] == job]
    out.append(f"{job} n={len(x)} stated: " + json.dumps(collections.Counter(str(r['final_val']) for r in x).most_common(4)))
# problems solved by no model in the fixed phase (rl), headline set
head = {p["pid"] for p in C.problems()} - C.excluded()
solved = collections.defaultdict(int)
for r in rs:
    if r["job"].startswith("F_") and r["pid"] in head:
        solved[r["pid"]] += r["rl"]
out.append("unsolved by every model in the fixed phase (rl): " + str(sorted(p for p in head if solved[p] == 0)))
dpo0 = collections.defaultdict(int)
for r in rs:
    if r["job"] == "F_dpo" and r["pid"] in head:
        dpo0[r["pid"]] += r["rl"]
out.append("dpo 0/16 (rl): " + str(sorted(p for p in head if dpo0[p] == 0)))
# likelihood: means of whole-solution sums and lengths per group
L = json.load(open(os.path.join(C.HERE, "out", "ll_recount.json")))["rows"]
for g, m in (("rl_on_candidate", "s0100"), ("rl_on_candidate", "s0750"), ("rl_on_candidate", "s2300"), ("dpo_on_candidate", "dpo"), ("dpo_reference", "dpo")):
    xs = [r for r in L if r["group"] == g and r["model"] == m]
    out.append(f"LL {g} {m}: n={len(xs)} mean per-token {np.mean([r['mean'] for r in xs]):.4f}; whole-solution mean {np.mean([r['sum'] for r in xs]):.0f}, "
               f"median {np.median([r['sum'] for r in xs]):.0f}; length mean {np.mean([r['n'] for r in xs]):.0f}, median {np.median([r['n'] for r in xs]):.0f}")
own = [r["mean"] for r in L if r["group"] == "dpo_on_candidate"]
for m in ("s0100", "s0750", "s2300"):
    xs = [r["mean"] for r in L if r["group"] == "rl_on_candidate" and r["model"] == m]
    out.append(f"LL gap {m} - dpo own (aime2025_28): {np.mean(xs) - np.mean(own):+.4f}; inside own 7's 2.5-97.5% range: "
               f"{sum(np.percentile(own, 2.5) <= x <= np.percentile(own, 97.5) for x in xs)}/{len(xs)}; inside own min-max: {sum(min(own) <= x <= max(own) for x in xs)}/{len(xs)}")
open(os.path.join(C.HERE, "out", "phase2_checks.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
