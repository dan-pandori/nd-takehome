#!/usr/bin/env python3
"""Figures for olmo-rlzero-pilot (style of nd-rl's 2026-10-31 σ figure: same x-axis label, muted axes, reference palette).

  passk.png      unbiased pass@k (rl grade), base vs RL checkpoints, headline problems, 95 % problem-bootstrap bands;
                 dashed continuation = lower bound where only the extended problems have samples beyond n_fixed
  reach.png      reach / reverse at full budget and expected entries / exits vs the base at matched k, against
                 cumulative RL compute ÷ pretraining compute (low–high bounds as horizontal bars)
  likelihood.png base vs generating-checkpoint mean log-prob per token for scored solutions, by group

Usage: figures.py [--outdir figures] (reads olmo_pilot/{passk,reach,dynamics,compute_axis,likelihood}.csv)
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

O = Path("olmo_pilot")
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BASE_C = "#eb6834"  # categorical slot 2 (orange): the base, the reference every checkpoint is compared with
RAMP = {100: "#86b6ef", 500: "#3987e5", 2800: "#184f95"}  # sequential blue (steps 250 / 400 / 600): RL step order
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": TEXT, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})


def color(step):
    return BASE_C if step == 0 else RAMP.get(step, "#256abf")


def label(model, step):
    return "base (step 0)" if step == 0 else f"RL step {step}"


def rows(name):
    p = O / name
    return list(csv.DictReader(open(p))) if p.exists() else []


def fig_passk(out):
    P = [r for r in rows("passk.csv") if r["grade"] == "rl"]
    LB = [r for r in rows("passk_lb.csv") if r["grade"] == "rl"]
    if not P:
        return
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    models = sorted({(int(r["step"]), r["model"]) for r in P})
    for step, m in models:
        rr = [r for r in P if r["model"] == m]
        k = [int(r["k"]) for r in rr]
        y = [float(r["pass_at_k"]) for r in rr]
        ax.fill_between(k, [float(r["lo95"]) for r in rr], [float(r["hi95"]) for r in rr], color=color(step),
                        alpha=0.12, lw=0)
        ax.plot(k, y, color=color(step), lw=2, marker="o", ms=4, label=label(m, step))
        lb = [r for r in LB if r["model"] == m and int(r["k"]) >= k[-1]]
        if len(lb) > 1:
            ax.plot([int(r["k"]) for r in lb], [float(r["pass_at_k"]) for r in lb], color=color(step), lw=1.5,
                    ls=(0, (4, 3)))
        ax.text(k[-1] * 1.08, y[-1], f"{y[-1]:.2f}", color=TEXT, fontsize=7.5, va="center")
    ax.set_xscale("log", base=2)
    ks = sorted({int(r["k"]) for r in P + LB})
    ax.set_xticks(ks, [str(x) for x in ks])
    ax.minorticks_off()
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 1)
    ax.set_xlabel("k (samples per problem)")
    ax.set_ylabel("pass@k (verifier RL rewarded)")
    n = P[0]["n_problems"]
    ax.set_title(f"pass@k on {n} AIME 2024–26 problems (dashed: lower bound, extended problems only)",
                 loc="left", fontsize=9.5, color=TEXT)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "olmo_pilot_passk.png", dpi=160)
    plt.close(fig)


def fig_reach(out):
    R = [r for r in rows("reach.csv") if r["grade"] == "rl"]
    X = {int(r["step"]): r for r in rows("compute_axis.csv")}
    if not R or not X:
        return
    kcol = [c for c in R[0] if c.startswith("exp_entries_k")][0]
    k = kcol.rsplit("k", 1)[1]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), gridspec_kw=dict(wspace=0.32))
    series = [("reach_full", "reach: solved by the checkpoint, never by the base", "#2a78d6", "o"),
              ("strong_reach", "strong reach (Part A/B definition)", "#4a3aa7", "D"),
              ("reverse_full", "reverse: solved by the base, never by the checkpoint", BASE_C, "s")]
    series2 = [(kcol, f"expected entries vs base at k = {k}", "#2a78d6", "o"),
               (f"exp_exits_k{k}", f"expected exits vs base at k = {k}", BASE_C, "s")]
    for ax, ser, title in ((axes[0], series, "a   Problems gained and lost at full budget"),
                           (axes[1], series2, f"b   Expected entries and exits at matched k = {k}")):
        for key, lab, c, mk in ser:
            pts = sorted((int(r["step"]), float(r[key])) for r in R)
            xs = [float(X[s]["ratio_geomean"]) for s, _ in pts]
            lo = [float(X[s]["ratio_low"]) for s, _ in pts]
            hi = [float(X[s]["ratio_high"]) for s, _ in pts]
            ys = [y for _, y in pts]
            ax.errorbar(xs, ys, xerr=[[x - a for x, a in zip(xs, lo)], [b - x for x, b in zip(xs, hi)]], color=c,
                        marker=mk, ms=6, lw=2, capsize=0, elinewidth=1, label=lab)
            for (s, y), x in zip(pts, xs):
                ax.annotate(f"{y:g}", (x, y), textcoords="offset points", xytext=(6, 4), fontsize=7.5, color=TEXT)
        ax.set_xscale("log")
        ax.grid(color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("cumulative RL compute ÷ pretraining compute (FLOPs)")
        ax.set_ylabel("problems (of the headline set)")
        ax.set_title(title, loc="left", fontsize=9.5, color=TEXT)
        ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    for s, r in X.items():
        if s:
            axes[0].annotate(f"step {s}", (float(r["ratio_geomean"]), 0), textcoords="offset points",
                             xytext=(0, -26), ha="center", fontsize=7, color=MUTED, annotation_clip=False)
    fig.savefig(out / "olmo_pilot_reach.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_likelihood(out):
    L = rows("likelihood.csv")
    if not L:
        return
    groups = [("reach", "RL checkpoint's solutions on reach problems", "#2a78d6", "o"),
              ("ckpt_other", "RL checkpoint's solutions, other problems", "#86b6ef", "^"),
              ("base_own", "base's own solutions", BASE_C, "s")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw=dict(wspace=0.3))
    lo = min(min(float(r["own_mean_lp"]), float(r["base_mean_lp"])) for r in L)
    for g, lab, c, mk in groups:
        rr = [r for r in L if r["group"] == g]
        if not rr:
            continue
        a.scatter([float(r["own_mean_lp"]) for r in rr], [float(r["base_mean_lp"]) for r in rr], s=22, color=c,
                  marker=mk, edgecolor=SURFACE, linewidth=0.8, label=f"{lab} (n = {len(rr)})")
        b.scatter([float(r["own_mean_lp"]) - float(r["base_mean_lp"]) for r in rr],
                  [float(r["base_frac_lt_1e3"]) for r in rr], s=22, color=c, marker=mk, edgecolor=SURFACE,
                  linewidth=0.8, label=lab)
    a.plot([lo, 0], [lo, 0], color=MUTED, lw=1, ls=(0, (4, 3)))
    a.set_xlabel("generating model's mean log-prob per token")
    a.set_ylabel("base's mean log-prob per token")
    a.set_title("a   Same solutions, scored by both models", loc="left", fontsize=9.5, color=TEXT)
    b.set_xlabel("gap: generating model − base (nats per token)")
    b.set_ylabel("share of tokens the base gives p < 10⁻³")
    b.set_title("b   Where the base finds the solutions unlikely", loc="left", fontsize=9.5, color=TEXT)
    for ax in (a, b):
        ax.grid(color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    a.legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.savefig(out / "olmo_pilot_likelihood.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="figures")
    a = ap.parse_args()
    out = Path(a.outdir)
    out.mkdir(exist_ok=True)
    fig_passk(out)
    fig_reach(out)
    fig_likelihood(out)
    print(f"figures -> {out}")


if __name__ == "__main__":
    main()
