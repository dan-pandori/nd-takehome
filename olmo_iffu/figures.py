#!/usr/bin/env python3
"""Figure of run olmo-iffu: every olmo-ifomega reach prompt, its status before and after each test
(olmo_iffu/status.csv, from status.py) -> figures/olmo_iffu_status.png.

Cells give `dpo`'s successes / draws (test 1: hand-sound under `any` credit; tests 2-3: hand-genuine; "2+" = reading
stopped at the second genuine one). Fill = the number of `dpo` successes, one blue hue light -> dark (0 / 1 / >= 2;
validated as an ordinal ramp on the light surface); gray hatch = the hint also breaks `step_2300` (< 2 genuine of 16),
so `dpo`'s failure there says nothing about brevity; blank = untested. Test 4's column is about `step_0750`, not
`dpo`: filled dot = confirmed (>= 2 genuine), hollow = not.
"""
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

SURFACE, TEXT, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d4"
RAMP = {0: "#86b6ef", 1: "#2a78d6", 2: "#104281"}  # ordinal ramp (validate_palette.js --ordinal: all pass)
BROKEN = "#c3c2b7"
plt.rcParams.update({"font.size": 7.5, "font.family": "DejaVu Sans", "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "text.color": TEXT})
COLS = [("before", "before\n256 at 32k"), ("t1", "test 1\n64 at 65k"),
        ("t2", "test 2 / 2c\nhint, 64"), ("t3", "test 3\n1,024"), ("t4", "test 4\nstep_0750")]
GROUP_NAMES = {"geometry": "OMEGA geometry", "ifeval": "IFEval", "ifbench_t2": "IFBench: test-2 subset",
               "ifbench_t3": "IFBench: test-3 subset", "ifbench_other": "IFBench: other reach prompts"}


def count(cell):
    return int(cell.split("/")[0].rstrip("+")) if cell else None


def short(pid):
    return pid.replace("omega_out_geometry_perpendicular_intersection_test_out_", "perp_")


def main():
    rows = list(csv.DictReader(open("olmo_iffu/status.csv")))
    n = len(rows)
    gaps = sum(1 for i in range(1, n) if rows[i]["group"] != rows[i - 1]["group"])
    H = 0.165 * (n + gaps * 1.2 + 7.5)
    fig, ax = plt.subplots(figsize=(7.2, H))
    cw, ch = 1.0, 1.0
    y = 0.0
    ypos, gstart = [], {}
    for i, r in enumerate(rows):
        if i and r["group"] != rows[i - 1]["group"]:
            y += 1.2
        gstart.setdefault(r["group"], y)
        ypos.append(y)
        y += 1
    for r, yy in zip(rows, ypos):
        ax.text(-0.15, yy + 0.5, short(r["pid"]), ha="right", va="center", color=TEXT, fontsize=7)
        for j, (key, _) in enumerate(COLS):
            x = j * cw
            cell = r.get(key, "")
            if not cell:
                ax.add_patch(Rectangle((x + 0.04, yy + 0.06), cw - 0.08, ch - 0.12, fill=False, ec=GRID, lw=0.6))
                continue
            if key == "t4":
                k = count(cell)
                ax.add_patch(Rectangle((x + 0.04, yy + 0.06), cw - 0.08, ch - 0.12, fill=False, ec=GRID, lw=0.6))
                ax.plot(x + 0.17, yy + 0.5, "o", ms=4.2, mfc=TEXT if k >= 2 else SURFACE, mec=TEXT, mew=0.8)
                ax.text(x + 0.33, yy + 0.5, cell, ha="left", va="center", fontsize=6.5, color=TEXT)
                continue
            k = count(cell)
            broken = key == "t2" and "breaks" in r.get("t2_label", "")
            fc = BROKEN if broken else RAMP[min(k, 2)]
            ax.add_patch(Rectangle((x + 0.04, yy + 0.06), cw - 0.08, ch - 0.12, fc=fc, ec=SURFACE, lw=1.0,
                                   hatch="////" if broken else None))
            mark = "*" if key == "t2" and "literal reading" in r.get("t2_label", "") else ""
            ax.text(x + cw / 2, yy + 0.5, cell + mark, ha="center", va="center", fontsize=6.5,
                    color="#ffffff" if (not broken and k >= 1) else TEXT)
    for g, y0 in gstart.items():
        ax.text(-0.15, y0 - 0.25, GROUP_NAMES[g], ha="right", va="bottom", fontsize=7.5, color=MUTED, weight="bold")
    for j, (_, lab) in enumerate(COLS):
        ax.text(j * cw + cw / 2, -1.0, lab, ha="center", va="bottom", fontsize=7, color=TEXT)
    ax.set_xlim(-2.2, len(COLS) * cw + 0.05)
    ax.set_ylim(y + 2.2, -5.3)
    ax.axis("off")
    # legend (identity never color-alone: every cell carries its count)
    lx, ly = -2.1, -5.0
    items = [(RAMP[0], None, "dpo 0 successes: reach stands"), (RAMP[1], None, "dpo 1 success"),
             (RAMP[2], None, "dpo ≥ 2: reached (token budget / hint / samples)"),
             (BROKEN, "////", "hint also breaks step_2300 (uninformative)")]
    for i, (c, h, lab) in enumerate(items):
        xx = lx + (i % 2) * 3.6
        yy = ly + (i // 2) * 0.75
        ax.add_patch(Rectangle((xx, yy), 0.35, 0.5, fc=c, ec=SURFACE, hatch=h))
        ax.text(xx + 0.45, yy + 0.27, lab, va="center", fontsize=6.8, color=TEXT)
    ax.set_title("olmo-ifomega's reach prompts: does dpo reach them with more room, a brevity hint or more samples?",
                 fontsize=8.5, color=TEXT, loc="left", x=-0.28, pad=4)
    ax.text(-2.1, y + 0.4, "Cells: dpo successes / draws (test 1: hand-sound, any credit; tests 2–3: hand-genuine; 2+ = "
            "reading stopped at the second).\n* rests on ALL-CAPS answers to a title-case request (rule 6, literal "
            "reading). Test 4: step_0750's genuine successes in ≤ 32 fresh draws, ● ≥ 2, ○ fewer.",
            ha="left", va="top", fontsize=6.2, color=MUTED)
    fig.savefig("figures/olmo_iffu_status.png", dpi=170, bbox_inches="tight")
    print("figures/olmo_iffu_status.png")


if __name__ == "__main__":
    main()
