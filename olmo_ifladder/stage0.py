#!/usr/bin/env python3
"""Stage-0 re-cost of run olmo-ifladder (pre-registration § Budget): tokens per draw and throughput from the S0 jobs'
metas (artifacts/olmo_ifladder/meta/S0r2.json, S0r3.json), the LoRA step test (meta/steptest.json), and the projected
cost of the full design and of each cut, in the brief's order. Only lengths and throughput are read (no grades).

  python3 olmo_ifladder/stage0.py <rate $/h per GPU> <spent so far $> [--json out.json]
"""
import csv
import json
import sys
from pathlib import Path

A = Path("artifacts/olmo_ifladder/meta")


def meta(j):
    f = A / f"{j}.json"
    return json.load(open(f)) if f.exists() else None


def plain_means():
    """Stored unhinted mean tokens per draw on the 58 prompts (olmo-ifomega results.csv, all phases)."""
    pids = {r["pid"] for r in csv.DictReader(open("olmo_ifladder/prompts.csv"))}
    out = {}
    for r in csv.DictReader(open("olmo_ifomega/results.csv")):
        if r["pid"] in pids and r["model"] in ("dpo", "s2300") and r["mean_tok"]:
            out.setdefault(r["model"], []).append(float(r["mean_tok"]))
    return {m: sum(v) / len(v) for m, v in out.items()}


def main():
    rate, spent = float(sys.argv[1]), float(sys.argv[2])
    m2, m3, st = meta("S0r2"), meta("S0r3"), meta("steptest")
    t2 = m2["gen_tokens"] / m2["samples"]
    t3 = m3["gen_tokens"] / m3["samples"] if m3 else t2
    tps = [m["tok_per_s"] for m in (m2, m3) if m]
    tput = max(tps)
    pm = plain_means()
    rung1_dpo = 4089.0   # olmo-iffu T2 + T2c dpo mean tokens per draw (results.csv: 3,325 x 1,024 + 4,471 x 2,048)
    s23 = 5473.0         # olmo-iffu T2 + T2c s2300 mean with the hint (5,278 x 256 + 5,571 x 512)
    k = t2 / rung1_dpo
    draws = {"R1cal_dpo": (512, t2), "R1cal_s2300": (128, s23 * k),
             "R2_dpo": (3712, t2), "R3_dpo": (3712, t3), "R4_dpo": (3712, t3),
             "R2_s2300": (928, s23 * k), "R3_s2300": (928, s23 * k * t3 / t2), "R4_s2300": (928, s23 * k * t3 / t2),
             "Lchk": (576, (pm["dpo"] + pm["s2300"]) / 2), "Leval": (7104, (pm["dpo"] * 2 + pm["s2300"]) / 3)}
    load_h = 0.05   # per job (t_load in the S0 metas + engine start)
    overhead_h = 0.5 * 2 + 1.0 + 0.6   # set-up per GPU (x2), LoRA training + merges + NLL, misc idle
    tail = 1.10

    def cost(sel):
        tok = sum(draws[j][0] * draws[j][1] for j in sel)
        h = tok / tput / 3600 * tail + load_h * len(sel) + overhead_h
        return tok, h, h * rate

    full = list(draws)
    variants = [("full design", full)]
    c1 = [j for j in full if "s2300" not in j]
    variants.append(("cut 1: no s2300 sanity arm", c1))
    # cut 2: rungs 3 and 4 on unelicited prompts only (+ calibration); expected 32 + 10 at R3, 28 + 10 at R4 of 58
    frac3, frac4 = (29 + 10) / 58, (26 + 10) / 58
    draws["R3_dpo_c2"] = (int(3712 * frac3), t3)
    draws["R4_dpo_c2"] = (int(3712 * frac4), t3)
    c2 = [j for j in c1 if j not in ("R3_dpo", "R4_dpo")] + ["R3_dpo_c2", "R4_dpo_c2"]
    variants.append(("cuts 1+2: R3/R4 on unelicited only", c2))
    draws["Leval_c3"] = (7104 // 2, draws["Leval"][1])
    c3 = [j for j in c2 if j != "Leval"] + ["Leval_c3"]
    variants.append(("cuts 1+2+3: LoRA eval 32", c3))
    out = {"tokens_per_draw": {"R2": round(t2), "R3": round(t3), "plain_dpo": round(pm["dpo"]), "plain_s2300": round(pm["s2300"])},
           "throughput_tok_s": tps, "throughput_used": tput, "rate": rate, "spent": spent,
           "S0_cut_share": [m["length_cut"] / m["samples"] for m in (m2, m3) if m],
           "steptest": {k2: st[k2] for k2 in ("peak_gb", "train_secs", "steps", "trainable")} if st else None,
           "variants": []}
    for name, sel in variants:
        tok, h, usd = cost(sel)
        out["variants"].append({"variant": name, "tokens_M": round(tok / 1e6, 1), "gpu_hours": round(h, 1),
                                "usd_remaining": round(usd, 1), "usd_total": round(usd + spent, 1)})
    print(json.dumps(out, indent=1))
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
