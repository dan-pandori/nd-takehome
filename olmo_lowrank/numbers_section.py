#!/usr/bin/env python3
"""Print numbers.md § olmo-lowrank from this run's tables (VPS side, stdlib only). Every number below is read from a
file named next to it; nothing is typed by hand except the billed dollars (podbudget) passed with --dollars.

  numbers_section.py --dollars 61.23 --hours 17.1 > /tmp/section.md
"""
import argparse
import csv
import json
import os

T = "olmo_lowrank/tables"
KS = (1, 4, 16, 64, 256)


def rd(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def f(x, n=3):
    try:
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dollars", default="?")
    ap.add_argument("--hours", default="?")
    a = ap.parse_args()
    out = []
    P = out.append
    P("## olmo-lowrank")
    P("")
    P("Models (released AI2 checkpoints, pretrained, bf16; none trained here): Olmo 3 32B (32.2 B) base `main` "
      "(`c2b61dae`), Think SFT `main` (`a6d7f3cf`), Think DPO `main` (`97604023`, `dpo`), Olmo 3.1 32B Think RL steps "
      "50–2,300 (`step_NNNN`; `s2300` = `main` `97ade57a`); Olmo 3 7B (7.3 B) base / SFT / DPO / Think RL steps 25–1,375 / "
      "RL-Zero-IF `main`. Commits and shard sha256: `olmo_lowrank/plan/spectra_jobs.json`, `olmo_weights/manifest/checkpoints.csv`. "
      f"Pod spend {a.dollars} (podbudget, {a.hours} pod-hours).")
    P("")
    P("### Part 1: spectra (source `olmo_lowrank/tables/changes.csv`, from `artifacts/olmo_lowrank/spectra/<job>/rows.csv` "
      "and `full_*.npz`; full float64 spectra of every matrix)")
    P("")
    P("S_k = energy-weighted share of Σ‖ΔW‖² in each matrix's top k singular pieces; Gaussian / floor A at the same k. "
      "Medians over matrices: stable rank, signal rank (# σ_i above σ₁ of rounding floor A), spike count (# σ_i above σ₁ "
      "of matched-norm rounded noise, floor B).")
    P("")
    P("| model | change | matrices | S1 | S16 | S256 | Gaussian S16 | floor A S16 | median stable rank | median signal rank | median spike count |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rd(f"{T}/changes.csv"):
        P(f"| {r['family']} | {r['change']} | {r['matrices']} | {f(r['S_1'])} | {f(r['S_16'])} | {f(r['S_256'])} | "
          f"{f(r.get('gauss_S_16', ''), 4)} | {f(r.get('floorA_S_16', ''), 4)} | {f(r['med_stable_rank'], 1)} | "
          f"{f(r['med_signal_rank'], 0)} | {f(r['med_spike_count'], 0)} |")
    P("")
    acc = rd(f"{T}/accuracy.csv")
    if acc:
        m1 = max(float(r["s1_max_rel_err"]) for r in acc)
        m64 = max(max(float(r[f"share_{k}_max_rel_err"]) for k in (1, 4, 16, 64)) for r in acc)
        m256 = max(float(r["share_256_max_rel_err"]) for r in acc)
        P(f"Randomized top-256 (p 64, q 16) against the full spectra, every matrix of every change (`{T}/accuracy.csv`): "
          f"max relative error σ₁ {m1:.1e}, top-k shares k ≤ 64 {m64:.1e}, k = 256 {m256:.1e}.")
        P("")
    L = rd(f"{T}/lora.csv")
    if L:
        P("LoRA overlap with RL's top-16 subspaces (`olmo_lowrank/tables/lora.csv`; 448 matrices; overlap = mean of left "
          "and right, random ≈ 16 / n):")
        P("")
        P("| change | adapter | median overlap | left | right | cos(ΔW_lora, ΔW) | cos with top-16 | share of ⟨ΔW_lora, ΔW⟩ in top 16 / 256 |")
        P("|---|---|---|---|---|---|---|---|")
        for r in L:
            if r["adapter"] in ("main", "ctrl") or r["adapter"] == "r0":
                P(f"| {r['change']} | {r['adapter'] if r['adapter'] != 'r0' else 'random (r0; r1–r3 alike)'} | {f(r['med_overlap'], 4)} | "
                  f"{f(r['med_left'], 4)} | {f(r['med_right'], 4)} | {f(r.get('cos_full', ''), 5)} | {f(r.get('cos_k16', ''), 5)} | "
                  f"{f(r.get('inner_share_k16', ''), 2)} / {f(r.get('inner_share_k256', ''), 2)} |")
        P("")
    ex = json.load(open(f"{T}/expectations_part1.json")) if os.path.exists(f"{T}/expectations_part1.json") else {}
    if ex:
        P("Part-1 expectations (`olmo_lowrank/tables/expectations_part1.json`): " +
          "; ".join(f"{k.split('_')[0]} {'hit' if v['hit'] else 'miss'}" for k, v in ex.items()) + ".")
        P("")
    R = rd("olmo_lowrank/results.csv")
    if R:
        P("### Part 2: truncation arms (source `olmo_lowrank/results.csv`, `olmo_lowrank/summary.json`)")
        P("")
        P("Arms on `dpo` (T_k: rank-k LoRA of RL's change, exact SVD; F448: the 448 matrices from s2300; C16: F448 minus "
          "the top 16). 48 reach prompts × 16 draws, 176 other arm-A prompts × 4; olmo-ifcurve decoding (T 1, top-p 1, "
          "32,768 tokens, vLLM 0.11.0, one H200). R = reach prompts' estimated genuine rate (hand gate), A = 218 prompts' "
          "strict pass@1. G = (arm − dpo) / (s2300 − dpo), 95 % paired prompt bootstrap (10,000).")
        P("")
        P("| metric | arm | rate | dpo | s2300 | G | 95 % interval |")
        P("|---|---|---|---|---|---|---|")
        for r in R:
            P(f"| {r['metric']} | {r['arm']} | {f(r['rate'])} | {f(r['dpo'])} | {f(r['s2300'])} | {f(r['G'])} | "
              f"[{f(r['G_lo'])}, {f(r['G_hi'])}] |")
        P("")
        s = json.load(open("olmo_lowrank/summary.json"))
        P("Readings (pre-registered thresholds): " + "; ".join(f"{k}: {v}" for k, v in s["final"].items()) +
          f"; k50 R {s['readings']['R']['k50']}, A {s['readings']['A']['k50']}.")
        P("")
    H = rd("olmo_lowrank/hand_arm_summary.csv")
    if H:
        P("Hand gate per arm (reach prompts; `olmo_lowrank/hand_arm_summary.csv`, `olmo_lowrank/handcheck.csv`):")
        P("")
        P("| arm | draws | strict | labelled | genuine | gamed | gamed share | from readers / screen / inherited | est. genuine rate |")
        P("|---|---|---|---|---|---|---|---|---|")
        for r in H:
            P(f"| {r['job']} | {r['draws']} | {r['strict']} | {r['labelled']} | {r['genuine']} | {r['gamed']} | "
              f"{f(r['gamed_share'], 2)} | {r['read']} / {r['screen']} / {r['inherited']} | {f(r['est_genuine_rate'])} |")
        P("")
    C = rd("olmo_lowrank/compute.csv")
    if C:
        P("Compute (`olmo_lowrank/compute.csv`; registry rows via `olmo_lowrank/compute_rows.py`):")
        P("")
        P("| job | GPU | GPU-seconds | generated tokens | draws | cut at 32,768 |")
        P("|---|---|---|---|---|---|")
        agg = {}
        for r in C:
            x = agg.setdefault(r["job"], [r["gpu"], 0.0, 0, 0, 0])
            x[1] += float(r["gpu_seconds"] or 0)
            x[2] += int(r["gen_tokens"] or 0)
            x[3] += int(r["attempts"] or 0)
            x[4] += int(r["length_cut"] or 0) if str(r["length_cut"]).isdigit() else 0
        for j, (g, s_, t, n, c) in agg.items():
            P(f"| {j} | {g} | {s_:.0f} | {t} | {n} | {c} |")
        P("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
