"""Markdown tables for numbers.md / the write-up, computed from artifacts/olmo_weights/tables/ (analyze.py output).
Writes artifacts/olmo_weights/tables/summary.md and stages.csv. Usage: python3 olmo_weights/report_tables.py"""
import csv, json, math, os
import numpy as np

D = "artifacts/olmo_weights/tables"


def rd(name):
    out = []
    for r in csv.DictReader(open(os.path.join(D, name))):
        for k, v in r.items():
            if v == "":
                r[k] = None
            else:
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
        out.append(r)
    return out


IV, CH, LO, MOD = rd("intervals.csv"), rd("chains.csv"), rd("lora.csv"), rd("modules.csv")
T = json.load(open(os.path.join(D, "tests.json")))
excl = set(T.get("excluded_names", T.get("rlzero_excluded", [])))
STAGES = [("32B", "stage 1 pairs (sampled)", "b32_s1", "stage1-sampled", ("pair",)),
          ("32B", "stage 2 ingredient 1", "b32_s2", "ingredient1", ("within",)),
          ("32B", "stage 2 ingredient 2 (every 4th)", "b32_s2", "ingredient2", ("within",)),
          ("32B", "stage 3", "b32_s3", "stage3", ("within",)),
          ("32B", "SFT 5e-5 run", "p32_sft", "sft-5e-5", ("within",)),
          ("32B", "SFT 1e-4", "p32_sft", "sft-1e-4", ("within",)),
          ("32B", "DPO (one interval)", "p32_sft", "sftmain-to-dpo", ("dpo",)),
          ("32B", "RL (3.1 Think)", "p32_rl", "rl", ("within",)),
          ("7B", "stage 1 pairs (sampled)", "b7_s1", "stage1-sampled", ("pair",)),
          ("7B", "stage 2", "b7_s2", "stage2", ("within",)),
          ("7B", "stage 3", "b7_s3", "stage3", ("within",)),
          ("7B", "SFT", "p7_sft", "sft-dpo", ("within",)),
          ("7B", "DPO (one interval)", "p7_sft", "sft-dpo", ("dpo",)),
          ("7B", "RL (Think)", "p7_rl", "rl", ("within",)),
          ("7B", "RL-Zero IF", "z7_if", "rlzero-if", ("within",)),
          ("7B", "RL-Zero Math", "z7_math", "rlzero-math", ("within",)),
          ("7B", "RL-Zero Code", "z7_code", "rlzero-code", ("within",))]


def g(x, f="{:.3g}"):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f.format(x)


def main():
    rows = []
    for fam, name, job, chain, kinds in STAGES:
        R = [r for r in IV if r["job"] == job and r["chain"] == chain and r["kind"] in kinds
             and r["a"] not in excl and r["b"] not in excl]
        if not R:
            continue
        med = lambda k: float(np.median([r[k] for r in R if r.get(k) is not None])) if any(r.get(k) is not None for r in R) else None
        rows.append(dict(family=fam, stage=name, n=len(R), steps_per_interval=med("steps"), rel_interval=med("rel"),
                         rel_per_step=med("rel_per_step"), lr=med("lr_mean"), per_step_per_lr=med("rel_per_step_per_lr"),
                         frac_eq=med("frac_eq"), frac_ulp=med("frac_ulp"), cos_lag1=med("cos_lag1"),
                         min_rel_per_step=min((r["rel_per_step"] for r in R if r.get("rel_per_step")), default=None),
                         max_rel_per_step=max((r["rel_per_step"] for r in R if r.get("rel_per_step")), default=None)))
    with open(os.path.join(D, "stages.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L = ["## Per-stage medians over within-stage intervals (stage 1: the sampled 1,000-step pairs)", "",
         "| model | stage | intervals | steps / interval | rel. change / interval | rel. change / step (min–max) | mean LR | per step ÷ LR | bitwise unchanged | ≤ 1 ulp | cos(consecutive) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['family']} | {r['stage']} | {r['n']} | {g(r['steps_per_interval'], '{:.0f}')} | {g(r['rel_interval'])} | "
                 f"{g(r['rel_per_step'])} ({g(r['min_rel_per_step'], '{:.2g}')}–{g(r['max_rel_per_step'], '{:.2g}')}) | {g(r['lr'])} | "
                 f"{g(r['per_step_per_lr'])} | {g(r['frac_eq'], '{:.3f}')} | {g(r['frac_ulp'], '{:.3f}')} | {g(r['cos_lag1'], '{:+.3f}')} |")
    L += ["", "## Distance and straightness per training stretch (released checkpoints, native spacing)", "",
          "| model | stretch | start → end | intervals | end distance / ‖θ_start‖ | path / ‖θ_start‖ | straightness S | mean cos(consecutive) | excluded names |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c in CH:
        L.append(f"| {c['family']} | {c['stretch']} | {c['start']} → {c['end']} | {int(c['n_intervals'])} | {g(c['end_distance_rel'])} | "
                 f"{g(c['path'] / c['norm_start'] if c.get('path') else None)} | {g(c['straightness'])} | {g(c['mean_cos_lag1'], '{:+.3f}')} | "
                 f"{c['excluded'] if c.get('excluded') not in (None, '[]') else ''} |")
    L += ["", "## Boundary, merge, DPO and `main` intervals", "",
          "| model | interval | kind | steps | rel. change | rel. change / step | bitwise unchanged | ≤ 1 ulp |", "|---|---|---|---|---|---|---|---|"]
    for r in IV:
        if r["kind"] in ("boundary", "merge", "dpo", "main") or r["chain"] == "pair":
            L.append(f"| {r['family']} | {r['a']} → {r['b']} | {r['kind']} | {g(r['steps'], '{:.0f}')} | {g(r['rel'])} | "
                     f"{g(r['rel_per_step'])} | {g(r['frac_eq'], '{:.3f}')} | {g(r['frac_ulp'], '{:.3f}')} |")
    if LO:
        L += ["", "## LoRA against RL (32B; 448 targeted matrices; cosine with θ_t − θ_DPO)", "",
              "| RL step | cos lora_main | cos lora_ctrl | random mean ± sd (8 draws) | ‖ΔW_main‖ / ‖θ_t − θ_DPO‖ | ‖ΔW_ctrl‖ / ‖θ_t − θ_DPO‖ |",
              "|---|---|---|---|---|---|"]
        for r in sorted(LO, key=lambda r: r["step"]):
            if r["step"] in (50, 100, 200, 500, 750, 1100, 1600, 2300) or r["step"] % 500 == 0:
                L.append(f"| {r['step']:.0f} | {r['cos_main']:.5f} | {r['cos_ctrl']:.5f} | {r['cos_rand_mean']:.1e} ± {r['cos_rand_sd']:.1e} | "
                         f"{r['norm_ratio_main']:.3f} | {r['norm_ratio_ctrl']:.3f} |")
    open(os.path.join(D, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
