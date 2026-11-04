#!/usr/bin/env python3
"""Figure for olmo-think32b (style and x-axis of the olmo-rlzero-pilot reach figure / nd-rl's 2026-10-31 σ figure).

olmo32_reach.png  (a) expected entries and exits relative to the RL start at matched k = 8, against cumulative RL
                  compute ÷ pretraining compute (FLOPs; geometric mean of the low and high bounds, bars = the bounds):
                  Olmo 3.1 Think 32B vs Olmo-3-32B-Think-DPO on 59 AIME 2025-26 problems (filled), and the 7B pilot
                  (Olmo 3.1 7B RL-Zero-Math vs its base, the 42-problem half every checkpoint was sampled on; hollow).
                  (b) reach at 256 samples (problems a checkpoint solves, confirmed, that the RL start never solves
                  within 256) under each grade, and the pilot's reach at <= 512 (0 at every checkpoint, rl grade).
Palette: categorical slots validated with the dataviz validator (light surface #fcfcfb): all checks pass; the green
(#1baf7a) is below 3:1 contrast, so its points carry direct labels.
Usage: figures.py [--outdir figures]  (reads olmo32/{dynamics,compute_axis,verdict}.csv, olmo_pilot/{half_subset,
compute_axis,reach}.csv)
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
ENTRY, EXIT, REACH, STRICT = "#2a78d6", "#eb6834", "#4a3aa7", "#1baf7a"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": TEXT, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})


def rows(p):
    return list(csv.DictReader(open(p))) if Path(p).exists() else []


def xaxis(path):
    return {int(r["step"]): (float(r["ratio_geomean"]), float(r["ratio_low"]), float(r["ratio_high"]))
            for r in rows(path) if int(r["step"]) > 0}


def plot(ax, X, pts, color, marker, label, hollow=False, ls="-", annotate=None, offset=(7, 5)):
    pts = sorted(p for p in pts if p[0] in X)
    xs = [X[s][0] for s, _ in pts]
    ys = [y for _, y in pts]
    err = [[X[s][0] - X[s][1] for s, _ in pts], [X[s][2] - X[s][0] for s, _ in pts]]
    ax.errorbar(xs, ys, xerr=err, color=color, marker=marker, ms=7, lw=2, ls=ls, capsize=0, elinewidth=1,
                mfc=SURFACE if hollow else color, mec=color, mew=1.6, label=label, zorder=3)
    if annotate:
        for (s, y), x in zip(pts, xs):
            ax.annotate(annotate(s, y), (x, y), textcoords="offset points", xytext=offset, fontsize=7.3, color=TEXT)


def grid(ax):
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xscale("log")
    ax.set_xticks([3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2],
                  ["3×10⁻⁵", "10⁻⁴", "3×10⁻⁴", "10⁻³", "3×10⁻³", "10⁻²", "3×10⁻²"])
    ax.minorticks_off()
    ax.set_xlim(2e-5, 5e-2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="figures")
    out = Path(ap.parse_args().outdir)
    X32, X7 = xaxis("olmo32/compute_axis.csv"), xaxis("olmo_pilot/compute_axis.csv")
    step32 = {"s0100": 100, "s0750": 750, "s2300": 2300}
    dyn = [r for r in rows("olmo32/dynamics.csv") if r["grade"] == "rl" and r["k"] == "8"]
    n32 = dyn[0]["n_problems"] if dyn else "?"
    step7 = {"step_0100": 100, "step_0500": 500, "step_2800": 2800}
    half = [r for r in rows("olmo_pilot/half_subset.csv") if r["model"] in step7]
    V = {r["grade"]: r for r in rows("olmo32/verdict.csv")}
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.4, 4.2), sharex=True)
    plot(a, X32, [(step32[r["model"]], float(r["exp_entries"])) for r in dyn], ENTRY, "o",
         f"entries, 32B Think vs DPO ({n32} problems)", annotate=lambda s, y: f"step {s}: {y:.1f}")
    plot(a, X32, [(step32[r["model"]], float(r["exp_exits"])) for r in dyn], EXIT, "s",
         f"exits, 32B Think vs DPO ({n32} problems)", annotate=lambda s, y: f"{y:.1f}", offset=(7, -12))
    plot(a, X7, [(step7[r["model"]], float(r["exp_entries_k8"])) for r in half], ENTRY, "o",
         "entries, 7B RL-Zero pilot vs base (42 problems)", hollow=True, ls=(0, (4, 2)))
    plot(a, X7, [(step7[r["model"]], float(r["exp_exits_k8"])) for r in half], EXIT, "s",
         "exits, 7B RL-Zero pilot vs base (42 problems)", hollow=True, ls=(0, (4, 2)))
    a.set_ylim(-0.5, None)
    a.set_ylabel("expected problems at k = 8")
    a.set_title("a  Problems RL adds and loses at matched k = 8", loc="left", fontsize=9.5, color=TEXT)
    a.legend(frameon=False, fontsize=7.1, loc="upper left")
    if V:
        for g, c, mk, lab in (("rl", REACH, "D", "reach at 256, RL's verifier / final answer / hand (rule)"),
                              ("hand_strict", STRICT, "^", "reach at 256, hand (strict)")):
            if g in V:
                pts = [(s, float(V[g][f"n_reach_{m}"])) for m, s in step32.items()]
                plot(b, X32, pts, c, mk, lab,
                     annotate=(lambda s, y: f"{y:.0f}") if g == "hand_strict" else None)
    pilot_reach = [(int(r["step"]), float(r["reach_full"])) for r in rows("olmo_pilot/reach.csv") if r["grade"] == "rl"]
    plot(b, X7, pilot_reach, REACH, "D", "7B pilot: reach at ≤ 512 (RL's verifier)", hollow=True, ls=(0, (4, 2)))
    b.set_ylim(-0.3, 3.3)
    b.set_yticks([0, 1, 2, 3])
    b.axhline(3, color=MUTED, lw=0.8, ls=":")
    b.annotate("scale-up threshold (≥ 3 problems)", (2.3e-5, 3.05), fontsize=7.2, color=MUTED)
    b.set_ylabel("problems")
    b.set_title("b  Problems out of the RL start's reach at 256 samples", loc="left", fontsize=9.5, color=TEXT)
    b.legend(frameon=False, fontsize=7.1, loc="center left")
    for ax in (a, b):
        grid(ax)
        ax.set_xlabel("cumulative RL compute ÷ pretraining compute (FLOPs)")
    fig.tight_layout()
    fig.savefig(out / "olmo32_reach.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out / 'olmo32_reach.png'}")


if __name__ == "__main__":
    main()
