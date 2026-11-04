#!/usr/bin/env python3
"""Figure for olmo-ifomega (style of olmo32/figures.py).

olmo_ifomega_reach.png: one panel per task run (IFBench headline set; OMEGA test_out; IFEval / test_in if run).
Each panel, against cumulative RL compute / pretraining compute (FLOPs; geometric mean of olmo32's low and high
bounds, bars = the bounds): expected entries and exits relative to Olmo-3-32B-Think-DPO at matched k = 8 (primary
grade), and reach at 256 (prompts a checkpoint solves, confirmed, that the DPO model never solves within 256; hand
grade, open candidates not counted), all per 100 prompts so tasks of different sizes and olmo-think32b's 59 AIME
problems (hollow, dashed; its rl-grade dynamics and strict-hand reach) share a scale.
Palette: olmo32/figures.py's validated categorical slots (light surface #fcfcfb).
Usage: figures.py [--outdir figures]   (reads olmo_ifomega/{dynamics,verdict,compute_axis}.csv, olmo32/{dynamics,
verdict,compute_axis}.csv)
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
ENTRY, EXIT, REACH = "#2a78d6", "#eb6834", "#4a3aa7"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": TEXT, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})
STEP = {"s0100": 100, "s0750": 750, "s2300": 2300}
PRIMARY = {"ifbench": "strict", "ifeval": "strict", "omega_in": "omega", "omega_out": "omega"}
TITLE = {"ifbench": "IFBench (headline prompts)", "ifeval": "IFEval", "omega_in": "OMEGA test_in",
         "omega_out": "OMEGA test_out"}


def rows(p):
    return list(csv.DictReader(open(p))) if Path(p).exists() else []


def xaxis(path):
    return {int(r["step"]): (float(r["ratio_geomean"]), float(r["ratio_low"]), float(r["ratio_high"]))
            for r in rows(path)}


def plot(ax, X, pts, color, marker, label, hollow=False, ls="-"):
    pts = sorted((s, y) for s, y in pts if s in X)
    if not pts:
        return
    xs = [X[s][0] for s, _ in pts]
    ys = [y for _, y in pts]
    ax.plot(xs, ys, ls=ls, color=color, lw=1.2, alpha=0.8)
    for s, y in pts:
        x, lo, hi = X[s]
        ax.errorbar([x], [y], xerr=[[x - lo], [hi - x]], fmt=marker, color=color, ms=6, capsize=2, lw=0.8,
                    mfc=SURFACE if hollow else color, mec=color)
    ax.plot([], [], ls=ls, marker=marker, color=color, mfc=SURFACE if hollow else color, label=label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="figures")
    a = ap.parse_args()
    X = xaxis("olmo_ifomega/compute_axis.csv")
    X32 = xaxis("olmo32/compute_axis.csv")
    dyn = rows("olmo_ifomega/dynamics.csv")
    ver = rows("olmo_ifomega/verdict.csv")
    tasks = [t for t in ("ifbench", "omega_out", "ifeval", "omega_in") if any(r["task"] == t for r in dyn)]
    aime_dyn = [r for r in rows("olmo32/dynamics.csv") if r["grade"] == "rl" and r["k"] == "8"]
    aime_n = int(aime_dyn[0]["n_problems"]) if aime_dyn else 59
    aime_reach = {r["grade"]: r for r in rows("olmo32/verdict.csv")}.get("hand_strict", {})
    fig, axes = plt.subplots(1, len(tasks), figsize=(4.2 * len(tasks), 3.6), squeeze=False)
    for ax, t in zip(axes[0], tasks):
        d = [r for r in dyn if r["task"] == t and r["grade"] == PRIMARY[t] and r["k"] == "8"]
        n = int(d[0]["n_prompts"]) if d else 100
        plot(ax, X, [(STEP[r["model"]], 100 * float(r["exp_entries"]) / n) for r in d], ENTRY, "o",
             "entries at k = 8")
        plot(ax, X, [(STEP[r["model"]], 100 * float(r["exp_exits"]) / n) for r in d], EXIT, "s", "exits at k = 8")
        v = {r["grade"]: r for r in ver if r["task"] == t}.get("hand", {})
        if v:
            plot(ax, X, [(STEP[m], 100 * int(v[f"n_reach_{m}"]) / n) for m in STEP if v.get(f"n_reach_{m}") != ""],
                 REACH, "D", "reach at 256 (hand)")
        plot(ax, X32, [(STEP[r["model"]], 100 * float(r["exp_entries"]) / aime_n) for r in aime_dyn], ENTRY, "o",
             "AIME 2025–26 entries (olmo-think32b)", hollow=True, ls=(0, (4, 2)))
        plot(ax, X32, [(STEP[r["model"]], 100 * float(r["exp_exits"]) / aime_n) for r in aime_dyn], EXIT, "s",
             "AIME exits", hollow=True, ls=(0, (4, 2)))
        if aime_reach:
            plot(ax, X32, [(STEP[m], 100 * int(aime_reach[f"n_reach_{m}"]) / aime_n) for m in STEP], REACH, "D",
                 "AIME reach (strict hand)", hollow=True, ls=(0, (4, 2)))
        ax.set_xscale("log")
        ax.set_title(f"{TITLE[t]} ({n} prompts)", fontsize=9, color=TEXT, loc="left")
        ax.set_xlabel("cumulative RL ÷ pretraining compute (FLOPs)")
        ax.grid(True, color=GRID, lw=0.6)
        ax.set_ylim(bottom=0)
    axes[0][0].set_ylabel("per 100 prompts")
    axes[0][-1].legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle("Olmo 3.1 Think 32B checkpoints vs Olmo-3-32B-Think-DPO (the RL start)", fontsize=10, color=TEXT,
                 x=0.01, ha="left")
    fig.tight_layout()
    Path(a.outdir).mkdir(exist_ok=True)
    out = Path(a.outdir) / "olmo_ifomega_reach.png"
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main()
