#!/usr/bin/env python3
"""Re-cost the design from Stage 0 (pre-registration Part B). Usage: project.py [usd_per_h] [spent_usd]

Tokens = samples x mean tokens per sample (Stage 0, by task; RL checkpoints use s2300's Stage-0 lengths when
measured, else dpo's x RL_LEN). Fixed phase: dpo 16, each RL checkpoint 8 per prompt. Extension (expected, with a
pessimistic case): reach candidates x defender samples + reverse candidates x defender samples + challenger
confirmation, at the task's mean length of *failing* Stage-0 samples (hard prompts run long). GPU time = tokens /
throughput, throughput from the Stage-0 job (vLLM log integral) split by task with a simple occupancy model:
OMEGA-length sequences run at the measured long-sequence rate, IF at IF_SPEEDUP x that rate (short sequences fit
many more per KV cache). Overhead per pod-model: 0.15 h (download + load); idle and setup 10 %.
"""
import json
import sys

RATE = float(sys.argv[1]) if len(sys.argv) > 1 else 5.29
SPENT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
S0 = [json.loads(ln) for ln in open("olmo_ifomega/stage0_summary.json")]
N = {"ifbench": 300, "ifeval": 150, "omega_in": 100, "omega_out": 100}
# expected candidates (preliminary expectations, Part A) and a pessimistic case
CAND = {"ifbench": (30, 3, 60, 10), "ifeval": (4, 2, 10, 5), "omega_in": (6, 3, 12, 8), "omega_out": (8, 3, 15, 8)}
DEF_SAMPLES = (150, 240)      # defender samples per reach candidate beyond the fixed phase (expected, pessimistic)
REV_SAMPLES = (100, 248)
CONF_SAMPLES = (32, 96)       # challenger confirmation per unresolved candidate
UNRESOLVED = (0.4, 0.7)
RL_LEN = 1.0
IF_SPEEDUP = 3.0


def lengths():
    d = {r["model"]: r for r in S0}
    out = {}
    for m in ("dpo", "s2300"):
        if m not in d:
            continue
        t = d[m]["tasks"]
        out[m] = {"ifbench": t.get("rlif", t["ifeval"])["mean_tok"], "ifeval": t["ifeval"]["mean_tok"],
                  "omega_in": t["omega_in"]["mean_tok"], "omega_out": t["omega_out"]["mean_tok"]}
    if "s2300" not in out:
        out["s2300"] = {k: v * RL_LEN for k, v in out["dpo"].items()}
    return out


def main():
    L = lengths()
    dpo0 = next(r for r in S0 if r["model"] == "dpo")
    tps_long = dpo0["vllm_tok_per_s"] or dpo0["tok_per_s_job"]
    tps = {"ifbench": tps_long * IF_SPEEDUP, "ifeval": tps_long * IF_SPEEDUP, "omega_in": tps_long, "omega_out": tps_long}
    rows = []
    tot = {"exp": 0.0, "pess": 0.0}
    for task in N:
        fixed_tok = N[task] * (16 * L["dpo"][task] + 8 * 2 * L["dpo"][task] * 0.5 + 8 * 2 * L["s2300"][task] * 0.5
                               + 8 * L["s2300"][task])
        # s0100 / s0750 lengths: midway between dpo and s2300
        for case, j in (("exp", 0), ("pess", 1)):
            r, v = CAND[task][0 + 2 * j], CAND[task][1 + 2 * j]
            ext_tok = (r * DEF_SAMPLES[j] * L["dpo"][task] + v * REV_SAMPLES[j] * L["s2300"][task]
                       + (r + v) * UNRESOLVED[j] * CONF_SAMPLES[j] * L["s2300"][task]) * (1.3 if task.startswith("omega") else 1.15)
            h = (fixed_tok + ext_tok) / tps[task] / 3600
            rows.append((task, case, fixed_tok / 1e6, ext_tok / 1e6, h, h * RATE))
            tot[case] += h * RATE
    over = 4 * 2 * 0.15 * RATE
    print(f"rate ${RATE}/h; Stage-0 long-sequence throughput {tps_long:.0f} tok/s (dpo job); IF x{IF_SPEEDUP}")
    print("task       case  fixed_Mtok  ext_Mtok  GPU_h   usd")
    for t, c, f, e, h, u in rows:
        print(f"{t:10s} {c:5s} {f:10.1f} {e:9.1f} {h:6.1f} {u:6.1f}")
    for c in tot:
        t = tot[c] * 1.1 + over + SPENT
        print(f"total {c}: sampling ${tot[c]:.1f} + 10 % idle/setup + overhead ${over:.1f} + spent ${SPENT:.1f} = ${t:.1f}")


if __name__ == "__main__":
    main()
