#!/usr/bin/env python3
"""The per-prompt ladder figure of run olmo-ifladder: reach prompts as rows (grouped by reading), rungs 1-4 and the two
LoRAs as columns; a cell is the hand-gated genuine count among the cell's strict successes (2+ = elicited), one-hue
ordinal ramp (validated: dataviz validate_palette --ordinal, light), "-" = not run (cut 2: an earlier rung elicited it).
Reads olmo_ifladder/classify.csv (analyze.py) and prompts.csv; writes figures/olmo_ifladder_ladder.png.
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

O = Path("olmo_ifladder")
RAMP = {0: "#86b6ef", 1: "#3987e5", 2: "#184f95"}  # blue 250 / 400 / 600
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
COLS = [("R1", "rung 1\nbrevity"), ("R2", "rung 2\n+ check"), ("R3", "rung 3\n+ method"), ("R4", "rung 4\n+ 2 shots"),
        ("main", "LoRA\ns2300"), ("ctrl", "LoRA\ncontrol")]
ORDER = ["prompt-elicitable at rung 1", "prompt-elicitable at rung 2", "prompt-elicitable at rung 3",
         "prompt-elicitable at rung 4", "teachable from RL's trajectories", "teachable by any light fine-tune",
         "control LoRA only", "neither"]
SHORT = {"keywords:letter_frequency": "letter limit", "change_case:capital_word_frequency": "caps count",
         "change_case:english_capital": "all caps", "format:title_case": "title case", "count:keywords_multiple": "keyword counts",
         "repeat:repeat_simple": "repeat sentence", "format:line_indent": "stairs", "ratio:sentence_words": "equal sentences",
         "sentence:increment": "+n words", "format:thesis": "thesis", "words:consonants": "consonant clusters",
         "sentence:alliteration_increment": "alliteration", "words:vowel": "three vowels", "words:repeats": "word repeats",
         "words:prime_lengths": "prime lengths", "format:sub-bullets": "sub-bullets", "ratio:stop_words": "stop words",
         "count:numbers": "number count", "format:emoji": "emoji", "ratio:sentence_balance": "sentence balance",
         "words:alphabet": "alphabet", "words:odd_even_syllables": "syllable parity", "words:last_first": "last-first",
         "words:no_consecutive": "no consecutive", "count:pronouns": "pronouns", "custom:multiples": "multiples",
         "repeat:repeat_span": "span copy"}


def r1_count(s):
    """olmo-iffu's t2 column ('3+/64', '2/64', '1/64', '0/64')."""
    head = (s or "0").split("/")[0]
    return 2 if head.endswith("+") or int(head or 0) >= 2 else int(head or 0)


def main():
    pr = {r["pid"]: r for r in csv.DictReader(open(O / "prompts.csv"))}
    cl = list(csv.DictReader(open(O / "classify.csv")))
    base = lambda r: r["reading"].replace(" (provisional)", "")  # noqa: E731
    cl.sort(key=lambda r: (ORDER.index(base(r)) if base(r) in ORDER else 99, r["family"], r["pid"]))
    n = len(cl)
    fig, ax = plt.subplots(figsize=(7.6, 0.24 * n + 1.6), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    gap = 0.06
    for y, r in enumerate(cl):
        for x, (k, _) in enumerate(COLS):
            state = r[k]
            if k == "R1":
                g = r1_count(pr[r["pid"]]["r1_dpo"])
            else:
                gk = r.get(f"g_{k}", "")
                g = 2 if state == "elicited" else (int(gk) if str(gk).isdigit() else 0)
            if state == "not run":
                ax.add_patch(Rectangle((x + gap, y + gap), 1 - 2 * gap, 1 - 2 * gap, facecolor=SURFACE,
                                       edgecolor="#d6d5d0", linewidth=0.6))
                ax.text(x + 0.5, y + 0.5, "–", ha="center", va="center", fontsize=7, color=MUTED)
                continue
            c = RAMP[min(g, 2)]
            ax.add_patch(Rectangle((x + gap, y + gap), 1 - 2 * gap, 1 - 2 * gap, facecolor=c, edgecolor=SURFACE,
                                   linewidth=1.0))
            ax.text(x + 0.5, y + 0.5, "2+" if g >= 2 else str(g), ha="center", va="center", fontsize=6.5,
                    color="#ffffff" if g >= 1 else INK)
    # group separators and labels
    prev = None
    for y, r in enumerate(cl):
        b = base(r)
        if b != prev:
            if y:
                ax.axhline(y, color=INK, linewidth=0.8)
            span = sum(1 for q in cl if base(q) == b)
            ax.text(len(COLS) + 0.15, y + span / 2, b.replace("prompt-elicitable", "prompt-elicitable\n").replace(
                "teachable from RL's trajectories", "teachable from\nRL's trajectories"), va="center", ha="left",
                fontsize=6.5, color=INK)
            prev = b
    ax.set_xlim(0, len(COLS) + 2.6)
    ax.set_ylim(n, 0)
    ax.set_xticks([i + 0.5 for i in range(len(COLS))])
    ax.set_xticklabels([c[1] for c in COLS], fontsize=6.5, color=INK)
    ax.xaxis.tick_top()
    labels = []
    for r in cl:
        p = pr[r["pid"]]
        ids = p["ids"].split()
        tag = "+".join(SHORT.get(i, i) for i in dict.fromkeys(ids))
        mark = ("†" if r["t3_survivor"] == "True" else "") + ("‡" if r["drop60"] == "True" else "")
        labels.append(f"{r['pid'].replace('ifbench_', 'IFBench ').replace('ifeval_', 'IFEval ')}{mark}  {tag}")
    ax.set_yticks([i + 0.5 for i in range(n)])
    ax.set_yticklabels(labels, fontsize=5.8, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.text(0.01, 0.005, "Cell = hand-gated genuine answers among the cell's strict successes (2+ = elicited: ≥ 2 genuine of 64 "
             "draws); – = not run (an earlier rung elicited it).\n† = 0 genuine in 1,024 unhinted draws (olmo-iffu test 3); "
             "‡ = the 60-word line dropped from every rung. Model: dpo = Olmo-3-32B-Think-DPO; LoRAs = dpo + r16 adapter.",
             fontsize=5.4, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    Path("figures").mkdir(exist_ok=True)
    fig.savefig("figures/olmo_ifladder_ladder.png", facecolor=SURFACE)
    print("figures/olmo_ifladder_ladder.png", n, "rows")


if __name__ == "__main__":
    main()
