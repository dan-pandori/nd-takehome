#!/usr/bin/env python3
"""Figure of run olmo-answeronly: reach-41 genuine rates (95 % prompt bootstrap) per condition and writer, beside
olmo-transplant's T1 / T2; right panel the optional LoRA arm. Reads olmo_answeronly/summary.json.
Writes figures/olmo_answeronly.png."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = json.load(open("olmo_answeronly/summary.json"))["conditions"]
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
COL = {"dpo": "#2a78d6", "s2300": "#eb6834", "lora_main": "#1baf7a"}
LAB = {"dpo": "dpo (DPO start)", "s2300": "s2300 (RL)", "lora_main": "lora_main (dpo + 16-trajectory LoRA)"}


def g(w, c):
    return S[f"reach|{w}|{c}"]["genuine_rate"]


fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [5, 2.6]}, facecolor=SURF)
groups = [("none\n(T1 / T2)", {"dpo": "T1", "s2300": "T2"}), ("A1\ninstruction", "A1"), ("A2\n≤ 60 words", "A2"),
          ("A3\nclosing thought", "A3"), ("A4\n5-token prefill", "A4")]
right = [("s2300's thinking\n(T1 / T2 / L1)", {"dpo": "T1", "s2300": "T2", "lora_main": "L1"}),
         ("lora_main's thinking\n(L2 / L3)", {"dpo": "L2", "lora_main": "L3"})]
for ax, gr, ws, title in ((a, groups, ["dpo", "s2300"], "Writer given s2300's full genuine thinking, plus one change"),
                          (b, right, ["dpo", "s2300", "lora_main"], "Optional LoRA arm")):
    ax.set_facecolor(SURF)
    wd = 0.8 / len(ws)
    for i, (name, cs) in enumerate(gr):
        for j, w in enumerate(ws):
            c = cs.get(w) if isinstance(cs, dict) else cs
            if c is None or f"reach|{w}|{c}" not in S:
                continue
            v, lo, hi = g(w, c)
            x = i - 0.4 + wd * (j + 0.5)
            ax.bar(x, v, wd - 0.03, color=COL[w], label=LAB[w] if i == (0 if ax is a else 0) else None, zorder=2)
            ax.errorbar(x, v, yerr=[[v - lo], [hi - v]], color=INK2, lw=1, capsize=2, zorder=3)
            ax.text(x, hi + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.set_xticks(range(len(gr)))
    ax.set_xticklabels([n for n, _ in gr], fontsize=8.5, color=INK)
    ax.set_ylim(0, 1.08)
    ax.set_title(title, fontsize=10, color=INK, loc="left")
    ax.grid(axis="y", color="#e4e3df", lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=8)
a.set_ylabel("genuine rate, reach-41 (mean over prompts, 95 % CI)", fontsize=8.5, color=INK2)
h1, l1 = a.get_legend_handles_labels()
h2, l2 = b.get_legend_handles_labels()
fig.legend(h1 + [h for h, l in zip(h2, l2) if l not in l1], l1 + [l for l in l2 if l not in l1], loc="lower center",
           ncol=3, frameon=False, fontsize=8.5)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig("figures/olmo_answeronly.png", dpi=150, facecolor=SURF)
print("figures/olmo_answeronly.png")
