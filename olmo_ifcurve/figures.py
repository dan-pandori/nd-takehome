#!/usr/bin/env python3
"""Figure of run olmo-ifcurve: figures/olmo_ifcurve.png (needs matplotlib; reads olmo_ifcurve/passk.csv and emergence.csv).

Panel 1: arm A strict pass@1 and pass@8 on the 218 IFBench prompts against RL step (dpo = step 0), 95 % prompt-bootstrap
bands; filled markers = this run's draws, open markers = stored olmo-ifomega draws. Panel 2: arm B, the 48 reach prompts
x RL checkpoints, coloured by estimated genuine rate (blue ramp; light grey = 0 genuine in the cell; hatched dpo column =
0 genuine in >= 256 by the set's definition), grouped by olmo-ifladder class; a dot marks each prompt's F1 cell.
"""
import csv
from pathlib import Path

import matplotlib
import numpy as np
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

O = Path("olmo_ifcurve")
CK = ["dpo", "s0050", "s0100", "s0200", "s0350", "s0500", "s0750", "s1100", "s1600", "s2300"]
STEP = {c: (0 if c == "dpo" else int(c[1:])) for c in CK}
STORED = {"dpo", "s0100", "s0750", "s2300"}
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
S1, S2 = "#2a78d6", "#eb6834"
RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ZERO = "#f0efec"


def main():
    pk = [r for r in csv.DictReader(open(O / "passk.csv")) if r["group"] == "all" and r["ckpt"] in CK]
    em = list(csv.DictReader(open(O / "emergence.csv")))
    fig = plt.figure(figsize=(12, 7.2), facecolor=SURF)
    ax1 = fig.add_axes([0.06, 0.15, 0.36, 0.75], facecolor=SURF)
    ax1.set_xscale("function", functions=(lambda v: np.sign(v) * np.sqrt(np.abs(v)), lambda v: np.sign(v) * v ** 2))
    for k, col, name in ((1, S1, "pass@1"), (8, S2, "pass@8")):
        rs = sorted((r for r in pk if int(r["k"]) == k and r["pass_at_k"] != ""), key=lambda r: STEP[r["ckpt"]])
        x = [STEP[r["ckpt"]] for r in rs]
        y = [float(r["pass_at_k"]) for r in rs]
        ax1.fill_between(x, [float(r["lo95"]) for r in rs], [float(r["hi95"]) for r in rs], color=col, alpha=0.13, lw=0)
        ax1.plot(x, y, color=col, lw=2, zorder=3)
        for r, xi, yi in zip(rs, x, y):
            st = r["ckpt"] in STORED
            ax1.plot([xi], [yi], marker="o", ms=8, mfc=SURF if st else col, mec=col, mew=2, zorder=4)
        ax1.annotate(name, (x[-1], y[-1]), xytext=(8, 0), textcoords="offset points", va="center", color=INK, fontsize=10)
    ax1.set_xlim(0, 2600)
    ax1.set_xticks([0, 50, 100, 200, 350, 500, 750, 1100, 1600, 2300])
    ax1.tick_params(axis="x", labelsize=8)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("RL step (square-root scale; 0 = DPO start)", color=INK2)
    ax1.set_ylabel("strict pass@k, 218 IFBench prompts", color=INK2)
    ax1.set_title("IFBench strict pass@1 and pass@8 over RL", color=INK, fontsize=11, loc="left")
    ax1.grid(axis="y", color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax1.spines[s].set_color(BASE)
    ax1.tick_params(colors=MUTED)
    ax1.plot([], [], marker="o", ms=8, mfc=SURF, mec=MUTED, mew=2, ls="", label="stored draws (olmo-ifomega)")
    ax1.plot([], [], marker="o", ms=8, mfc=MUTED, mec=MUTED, mew=2, ls="", label="this run's draws")
    ax1.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=INK2)

    ax2 = fig.add_axes([0.50, 0.15, 0.34, 0.75], facecolor=SURF)
    order = {"P": 0, "T": 1, "N": 2}
    first = {c: i for i, c in enumerate(CK)}
    em.sort(key=lambda r: (order[r["class"]], first.get(r["F1"], 99), r["pid"]))
    cmap = LinearSegmentedColormap.from_list("blue", RAMP)
    for yi, r in enumerate(em):
        for xi, c in enumerate(CK):
            if c == "dpo":
                ax2.add_patch(plt.Rectangle((xi, yi), 0.92, 0.92, fc=ZERO, ec=BASE, hatch="///", lw=0))
                continue
            v = r.get(f"rate_{c}", "")
            if v == "":
                continue
            v = float(v)
            ax2.add_patch(plt.Rectangle((xi, yi), 0.92, 0.92, fc=ZERO if v == 0 else cmap(min(v, 1.0)), lw=0))
        if r["F1"]:
            ax2.plot([first[r["F1"]] + 0.46], [yi + 0.46], marker="o", ms=3, color=INK, zorder=5)
    ax2.set_xlim(0, len(CK))
    ax2.set_ylim(len(em), 0)
    ax2.set_xticks([i + 0.46 for i in range(len(CK))])
    ax2.set_xticklabels([str(STEP[c]) for c in CK], color=MUTED, fontsize=8)
    ax2.set_yticks([i + 0.46 for i in range(len(em))])
    ax2.set_yticklabels([r["pid"].replace("ifbench_", "").replace("ifeval_", "e") for r in em], fontsize=6, color=MUTED)
    ax2.set_xlabel("RL step", color=INK2)
    ax2.set_title("48 reach prompts: genuine rate per checkpoint (dot = first genuine)", color=INK, fontsize=11,
                  loc="left")
    for s in ax2.spines.values():
        s.set_visible(False)
    ax2.tick_params(length=0)
    y0 = 0
    for k, name in (("P", "prompt-recoverable"), ("T", "teachable only"), ("N", "neither")):
        n = sum(1 for r in em if r["class"] == k)
        if y0:
            ax2.axhline(y0 - 0.04, color=INK2, lw=1)
        ax2.text(len(CK) + 0.15, y0 + n / 2, f"{name}\n({n})", va="center", fontsize=9, color=INK2)
        y0 += n
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    cax = fig.add_axes([0.50, 0.075, 0.34, 0.016])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label("estimated genuine rate (grey = 0 genuine; hatched = DPO: 0 in >= 256 by selection)", color=INK2, fontsize=8)
    cb.outline.set_visible(False)
    cax.tick_params(colors=MUTED, labelsize=8)
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/olmo_ifcurve.png", dpi=150, facecolor=SURF)
    print("wrote figures/olmo_ifcurve.png")


if __name__ == "__main__":
    main()
