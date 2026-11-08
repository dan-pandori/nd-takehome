#!/usr/bin/env python3
"""Figure for run olmo-rlzero-if: the 2 x 2 grid (domain x where RL starts) filled with reach shares.

Cell value = hand-confirmed reach prompts / headline prompts of the cell's main task (IFBench for IF, AIME for math),
each from its own run, labelled with its models; IFEval in the IF cells' second line. This run's cell is read from
olmo_rlzero_if/verdict.csv (hand row) and manifest.csv; the other three are the reviewed runs' headline numbers:
  IF after SFT  olmo-ifomega (numbers.md): Olmo 3.1 Think 32B step_2300 vs Olmo 3 Think 32B DPO, IFBench 42 / 218 by
                hand (94 candidates), IFEval 6 / 150 (8 candidates)
  math after SFT  olmo-think32b: AIME 2025-26, 0 / 59 (1 candidate, open)
  math from base  olmo-rlzero-pilot: Olmo 3.1 7B RL-Zero-Math step_2800 vs Olmo 3 7B base, AIME 2024-26, 0 / 83
                (17 candidates, all solved by the base within 512)
Colors: one sequential hue (blue ramp of the dataviz reference palette), share 0 -> step 100, >= 25 % -> step 600;
text in ink tokens, white on the two darkest steps. Writes figures/olmo_rlzero_if_grid.png.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

O = Path("olmo_rlzero_if")
RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
        "#1c5cab", "#184f95"]
SURF, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"


def fill(share):
    k = min(len(RAMP) - 1, int(round(share / 0.25 * (len(RAMP) - 1))))
    return RAMP[k], ("#ffffff" if k >= 8 else INK), ("#ffffff" if k >= 8 else INK2)


def this_run():
    v = {(r["task"], r["grade"]): r for r in csv.DictReader(open(O / "verdict.csv"))}
    head = {t: sum(1 for r in csv.DictReader(open(O / "manifest.csv")) if r["task"] == t and r["headline"] == "True")
            for t in ("ifbench", "ifeval")}
    out = {}
    for t in ("ifbench", "ifeval"):
        h, s = v[(t, "hand")], v[(t, "strict")]
        out[t] = dict(reach=int(h["n_reach_main"]), n=head[t], cand=int(h["n_reach_candidates"]),
                      open=int(h["n_open"]), verdict=h["verdict"], strict=int(s["n_reach_main"]))
    return out


def main():
    me = this_run()
    b, e = me["ifbench"], me["ifeval"]
    cells = {  # (row, col): (share, big, lines)
        (0, 0): (b["reach"] / b["n"], f"{100 * b['reach'] / b['n']:.1f} %",
                 [f"IFBench {b['reach']} / {b['n']} by hand ({b['cand']} candidates, {b['open']} open)",
                  f"strict checker alone: {b['strict']} / {b['n']}",
                  f"IFEval {e['reach']} / {e['n']} by hand ({e['cand']} candidates)",
                  "Olmo 3 7B RL-Zero-IF main vs Olmo 3 7B base", f"verdict: {b['verdict']} / {e['verdict']}"]),
        (0, 1): (42 / 218, f"{100 * 42 / 218:.1f} %",
                 ["IFBench 42 / 218 by hand (94 candidates)", "IFEval 6 / 150 (8 candidates)",
                  "Olmo 3.1 Think 32B step 2,300 vs its DPO start", "olmo-ifomega: Reach"]),
        (1, 0): (0.0, "0 %", ["AIME 0 / 83 (17 candidates, all solved", "by the base within 512 samples)",
                              "Olmo 3.1 7B RL-Zero-Math vs Olmo 3 7B base", "olmo-rlzero-pilot: elicitation only"]),
        (1, 1): (0.0, "0 %", ["AIME 0 / 59 (1 candidate, open)", "Olmo 3.1 Think 32B step 2,300 vs DPO",
                              "olmo-think32b: inconclusive"]),
    }
    fig = plt.figure(figsize=(10.4, 6.6), facecolor=SURF)
    ax = fig.add_axes([0.11, 0.04, 0.87, 0.80])
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.axis("off")
    for (r, c), (share, big, lines) in cells.items():
        bg, t1, t2 = fill(share)
        x, y = c, 1 - r
        ax.add_patch(FancyBboxPatch((x + 0.02, y + 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.03",
                                    fc=bg, ec=SURF, lw=2))
        ax.text(x + 0.06, y + 0.83, big, fontsize=26, color=t1, va="center", ha="left", weight="bold")
        ax.text(x + 0.06, y + 0.68, "of prompts are reach prompts", fontsize=9.5, color=t2, va="center")
        for k, ln in enumerate(lines):
            ax.text(x + 0.06, y + 0.52 - 0.095 * k, ln, fontsize=9, color=t1 if k == 0 else t2, va="center")
    fig.text(0.11 + 0.87 * 0.25, 0.875, "RL straight from the pretrained base\n(RL-Zero, 7B)", ha="center",
             fontsize=11, color=INK, weight="bold")
    fig.text(0.11 + 0.87 * 0.75, 0.875, "RL after SFT + DPO\n(Think, 32B)", ha="center", fontsize=11, color=INK,
             weight="bold")
    fig.text(0.055, 0.04 + 0.80 * 0.75, "instruction\nfollowing", ha="center", va="center", fontsize=11, color=INK,
             weight="bold")
    fig.text(0.055, 0.04 + 0.80 * 0.25, "math", ha="center", va="center", fontsize=11, color=INK, weight="bold")
    fig.text(0.11, 0.965, "Reach share: prompts an RL model solves (confirmed, hand-checked) that its RL start never "
             "solves genuinely in 256 samples", fontsize=11.5, color=INK, weight="bold")
    fig.text(0.11, 0.935, "share of headline prompts; darker = larger share", fontsize=9.5, color=MUTED)
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/olmo_rlzero_if_grid.png", dpi=150, facecolor=SURF)
    print("figures/olmo_rlzero_if_grid.png")


if __name__ == "__main__":
    main()
