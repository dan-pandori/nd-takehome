#!/usr/bin/env python3
"""Likelihood table and summary (pre-registration, Reported quantities / Expectations).

Reads artifacts/olmo32/ll/{items,scores_dpo}.jsonl (scored by score_ll.py under Olmo-3-32B-Think-DPO, prompt
log-probs of the response tokens given the olmo_thinker prompt). Writes olmo32/likelihood.csv (one row per scored
solution) and prints, per group, the per-token mean log-prob under dpo, the share of RL solutions inside the
2.5-97.5 % range of dpo's own correct solutions (reference set: one per other headline problem), and the gap between
RL's solutions and dpo's own on aime2025_28.
"""
import csv
import json

import numpy as np

items = {r["key"]: r for r in map(json.loads, open("artifacts/olmo32/ll/items.jsonl"))}
rows = []
for s in map(json.loads, open("artifacts/olmo32/ll/scores_dpo.jsonl")):
    it = items[s["key"]]
    rows.append({"key": s["key"], "group": it["group"], "gen_model": it["gen_model"], "pid": it["pid"],
                 "final_credited": it["final"], "n_tok": s["n_tok"], "sum_lp": round(s["sum_lp"], 2),
                 "mean_lp": round(s["mean_lp"], 5), "min_lp": round(s["min_lp"], 3), "n_lt_1e3": s["n_lt_1e3"],
                 "n_lt_1e6": s["n_lt_1e6"]})
with open("olmo32/likelihood.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
ref = np.array([r["mean_lp"] for r in rows if r["group"] == "dpo_reference"])
lo, hi = np.percentile(ref, [2.5, 97.5])
own = np.array([r["mean_lp"] for r in rows if r["group"] == "dpo_on_candidate"])
print(f"dpo reference (n={len(ref)}): mean {ref.mean():.4f}, 2.5-97.5 % [{lo:.4f}, {hi:.4f}]; dpo on aime2025_28 (n={len(own)}): "
      f"mean {own.mean():.4f} [{own.min():.4f}, {own.max():.4f}]")
allrl = []
for m in ("s0100", "s0750", "s2300"):
    x = np.array([r["mean_lp"] for r in rows if r["group"] == "rl_on_candidate" and r["gen_model"] == m])
    s = np.array([r["sum_lp"] for r in rows if r["group"] == "rl_on_candidate" and r["gen_model"] == m])
    allrl += list(x)
    print(f"{m} on aime2025_28 (n={len(x)}): per-token mean {x.mean():.4f} (range {x.min():.4f} .. {x.max():.4f}); "
          f"inside dpo reference range {np.mean((x >= lo) & (x <= hi)):.2f}; gap vs dpo own {x.mean() - own.mean():+.4f} nats/token; "
          f"whole-solution mean {s.mean():.0f} nats (dpo own {np.mean([r['sum_lp'] for r in rows if r['group'] == 'dpo_on_candidate']):.0f})")
a = np.array(allrl)
print(f"all RL (n={len(a)}): inside range {np.mean((a >= lo) & (a <= hi)):.2f}; gap vs dpo own {a.mean() - own.mean():+.4f}; below range {np.sum(a < lo)}")
