"""Reviewer (olmo-weights): LoRA vs RL at 32B/rl/2300 by module type and by depth (8 layer bins), from the executor's
lora.csv rows and lora_norms.csv. Usage: python3 rv_lora_breakdown.py ROOT"""
import math, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_load import load, module_of
D, J = load(sys.argv[1])
nrm = {r["tensor"]: r for r in D["p32_rl"]["lora_norms"]}
rows = [r for r in D["p32_rl"]["lora"] if r["b"] == "32B/rl/2300"]
for key, kf in (("module", lambda t: module_of(t)[0]), ("depth", lambda t: f"L{module_of(t)[1] // 8 * 8:02d}-{module_of(t)[1] // 8 * 8 + 7:02d}")):
    g = defaultdict(lambda: defaultdict(float))
    for r in rows:
        k = kf(r["tensor"]); n = nrm[r["tensor"]]
        g[k]["o2"] += float(r["o2"])
        for nm in ("main", "ctrl"):
            g[k][f"dot_{nm}"] += float(r[f"dot_{nm}"]); g[k][f"n2_{nm}"] += float(n[f"n2_{nm}"])
        for q in range(8):
            g[k][f"dot_r{q}"] += float(r[f"dot_r{q}"]); g[k][f"n2_r{q}"] += float(n[f"n2_r{q}"])
    print(f"== by {key}: cos_main  cos_ctrl  rnd_sd  norm_ratio_main(|dW|/|dtheta|)")
    for k in sorted(g):
        x = g[k]
        cm = x["dot_main"] / math.sqrt(x["o2"] * x["n2_main"]); cc = x["dot_ctrl"] / math.sqrt(x["o2"] * x["n2_ctrl"])
        rc = [x[f"dot_r{q}"] / math.sqrt(x["o2"] * x[f"n2_r{q}"]) for q in range(8)]
        mu = sum(rc) / 8; sd = math.sqrt(sum((v - mu) ** 2 for v in rc) / 7)
        print(f"  {k:10s} {cm:.5f}  {cc:.5f}  {sd:.1e}  {math.sqrt(x['n2_main'] / x['o2']):.3f}")
