#!/usr/bin/env python3
"""Figure of run olmo-lowrank (VPS side; numpy + matplotlib) -> figures/olmo_lowrank.png.

Panel 1: energy-weighted top-k share S(k) = sum_m sum_{i<=k} sigma_{m,i}^2 / sum_m ||dW_m||^2 against k, from the full
spectra of all 448 matrices of Olmo 3 32B: RL net change (Olmo-3-32B-Think-DPO -> Olmo-3.1-32B-Think step 2,300), one
single 50-step RL interval (2,250 -> 2,300), SFT's total change (base main -> SFT main), the Gaussian baseline (same
shapes, weighted by the RL net change's norms) and rounding floor A.
Panel 2: G = (arm - dpo) / (s2300 - dpo) against k for the T_k arms, on the reach prompts' genuine rate (R) and the
218 prompts' strict pass@1 (A), with 95 % prompt-bootstrap intervals; F448 and C16 at the right.
Colors: the dataviz reference palette's categorical slots 1-3 (validated, light surface); baselines in muted ink.
"""
import csv
import glob
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = "artifacts/olmo_lowrank/spectra"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb"


def full(job):
    out = {}
    for f in sorted(glob.glob(f"{S}/{job}/full_*.npz")):
        z = np.load(f)
        for k in z.files:
            out[k.replace("~", ".")] = z[k].astype(np.float64)
    return out


def curve(spectra, names, norms, kmax):
    """S(k) for k = 1..kmax: sum over matrices of the cumulative sigma^2 (saturating at a matrix's own length)."""
    tot = np.zeros(kmax)
    for nm in names:
        c = np.cumsum(spectra[nm] ** 2)
        if len(c) < kmax:
            c = np.concatenate([c, np.full(kmax - len(c), c[-1])])
        tot += c[:kmax]
    return tot / sum(norms[nm] for nm in names)


def panel1(ax):
    rows = {}
    for job in ("R32", "S32"):
        p = f"{S}/{job}/rows.csv"
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                rows[(r["change"], r["name"])] = r
    F = {**full("R32"), **full("S32")}
    kmax = 5120
    ks = np.arange(1, kmax + 1)
    series = [("N2300", "RL net, DPO → step 2,300", BLUE, "-"), ("I_late", "one RL interval, 2,250 → 2,300", ORANGE, "-"),
              ("SFT", "SFT total, base → SFT", AQUA, "-")]
    for cid, lab, col, ls in series:
        names = [k.split("|", 1)[1] for k in F if k.startswith(cid + "|")]
        if not names:
            continue
        norms = {nm: float(rows[(cid, nm)]["norm2"]) for nm in names}
        y = curve({nm: F[f"{cid}|{nm}"] for nm in names}, names, norms, kmax)
        ax.plot(ks, y, color=col, lw=2, ls=ls, label=lab)
    # Gaussian baseline: per shape, the mean full spectrum of 3 draws scaled to each RL-net matrix's norm
    gs = {}
    for k, v in F.items():
        if k.startswith("gauss"):
            gs.setdefault(k.split("|")[1], []).append(v)
    names = [k.split("|", 1)[1] for k in F if k.startswith("N2300|")]
    if gs and names:
        gsh = {shp: np.mean([np.cumsum(v ** 2) / np.sum(v ** 2) for v in vs], axis=0) for shp, vs in gs.items()}
        tot, den = np.zeros(kmax), 0.0
        for nm in names:
            r = rows[("N2300", nm)]
            m, n = sorted((int(r["m"]), int(r["n"])), reverse=True)
            c = gsh[f"{m}x{n}"]
            c = np.concatenate([c, np.full(max(0, kmax - len(c)), 1.0)])[:kmax]
            w = float(r["norm2"])
            tot += w * c
            den += w
        y = tot / den
        ax.plot(ks, y, color=MUTED, lw=1.5, ls="--", label="Gaussian at the RL net change's norms")
    fa = [k.split("|", 1)[1] for k in F if k.startswith("floorA|")]
    if fa:
        norms = {nm: float(rows[("floorA", nm)]["norm2"]) for nm in fa}
        y = curve({nm: F[f"floorA|{nm}"] for nm in fa}, fa, norms, kmax)
        ax.plot(ks, y, color=INK2, lw=2, ls=":", label="bf16 rounding floor A (on the Gaussian line)")
    ax.set_xscale("log")
    ax.set_xlim(1, kmax)
    ax.set_ylim(0, 1)
    for k in (1, 4, 16, 64, 256):
        ax.axvline(k, color=GRID, lw=0.8, zorder=0)
    ax.set_xticks([1, 4, 16, 64, 256, 1024, 5120])
    ax.set_xticklabels(["1", "4", "16", "64", "256", "1024", "5120"])
    ax.set_xlabel("k (top singular pieces kept per matrix)")
    ax.set_ylabel("share of ‖ΔW‖² in the top k (448 matrices)")
    ax.set_title("1  How concentrated each change is (Olmo 3 32B)", loc="left", fontsize=10, color=INK)
    ax.legend(loc="upper left", fontsize=8, frameon=False)


def panel2(ax):
    p = "olmo_lowrank/results.csv"
    if not os.path.exists(p):
        ax.text(0.5, 0.5, "Part 2 pending", ha="center", va="center", transform=ax.transAxes, color=INK2)
        return
    R = {(r["metric"], r["arm"]): r for r in csv.DictReader(open(p))}
    arms = ["T1", "T4", "T16", "T64", "T256"]
    xs = {a: i for i, a in enumerate(arms)}
    xs.update({"F448": 6.0, "C16": 7.0})
    for metric, lab, col, dx in (("R", "reach prompts, genuine rate", BLUE, -0.08), ("A", "218 prompts, strict pass@1", ORANGE, 0.08)):
        pts = [(xs[a] + dx, float(R[(metric, a)]["G"]), float(R[(metric, a)]["G_lo"]), float(R[(metric, a)]["G_hi"]))
               for a in arms + ["F448", "C16"] if (metric, a) in R]
        if not pts:
            continue
        tk = [q for q in pts if q[0] < 5]
        ax.plot([q[0] for q in tk], [q[1] for q in tk], color=col, lw=2, label=lab)
        for x, g, lo, hi in pts:
            ax.plot([x, x], [lo, hi], color=col, lw=1.2)
            ax.plot([x], [g], marker="o", ms=7, color=col, mec=SURF, mew=1.5, zorder=3)
    for y, t in ((0.0, "dpo"), (1.0, "s2300")):
        ax.axhline(y, color=MUTED, lw=1)
        ax.annotate(t, (7.45, y), fontsize=8, color=INK2, va="center")
    for y in (0.2, 0.5, 0.75):
        ax.axhline(y, color=GRID, lw=0.8, ls=":", zorder=0)
    ax.axvline(5.0, color=GRID, lw=1)
    ax.set_xticks([0, 1, 2, 3, 4, 6, 7])
    ax.set_xticklabels(["T1", "T4", "T16", "T64", "T256", "F448", "C16"])
    ax.set_xlim(-0.5, 7.8)
    ax.set_ylabel("G, share of RL's gain recovered")
    ax.set_xlabel("arm (T_k: DPO + RL's top-k pieces as a LoRA)")
    ax.set_title("2  How much of RL's IFBench gain each arm recovers", loc="left", fontsize=10, color=INK)
    ax.legend(loc="upper left", fontsize=8, frameon=False)


def main():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), facecolor=SURF)
    for ax in axs:
        ax.set_facecolor(SURF)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    panel1(axs[0])
    panel2(axs[1])
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/olmo_lowrank.png", dpi=150, facecolor=SURF)
    print("figures/olmo_lowrank.png")


if __name__ == "__main__":
    main()
