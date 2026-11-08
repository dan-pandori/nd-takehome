#!/usr/bin/env python3
"""Figure of run olmo-transplant: (a) genuine success by supplied thinking and answer writer, (b) the budget curves.
Reads olmo_transplant/summary.json (analyze.py). Writes figures/olmo_transplant.png.
Palette: the dataviz reference categorical slots 1-3 (validated, light surface #fcfcfb): blue = dpo writes the
answer, orange = s2300 writes it, aqua = fresh budget forcing (s2300 generates its own capped thinking)."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = json.load(open("olmo_transplant/summary.json"))
R = S["reach-41"]
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#1f1f1e", "#5d5c55", "#e6e5df", "#fcfcfb"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF})


def val(cell, key="genuine"):
    v = R.get(cell, {}).get(key)
    return (None, None, None) if v is None else tuple(v)


fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.05, 1]})
# (a) condition bars
groups = [("no thinking", "T0-dpo", "T0-s2300"), ("RL's thinking,\ncut before its draft", "P-dpo", "P-s2300"),
          ("RL's genuine thinking", "T1", "T2"), ("DPO's failed thinking", "T4", "T3")]
w = 0.36
for gi, (name, cd, cs) in enumerate(groups):
    for off, cell, col, wr in ((-w / 2 - 0.01, cd, BLUE, "dpo"), (w / 2 + 0.01, cs, ORANGE, "s2300")):
        p, lo, hi = val(cell)
        if p is None:
            continue
        a.bar(gi + off, p, width=w, color=col, edgecolor=SURF, linewidth=2, zorder=2,
              label={"dpo": "DPO start writes the answer", "s2300": "RL step 2300 writes the answer"}[wr] if gi == 0 else None)
        if lo is not None:
            a.errorbar(gi + off, p, yerr=[[p - lo], [hi - p]], color=INK, capsize=3, lw=1.2, zorder=3)
        a.text(gi + off, (hi if hi is not None else p) + 0.02, f"{p:.2f}", ha="center", va="bottom", fontsize=8.5, color=INK)
a.set_xticks(range(len(groups)))
a.set_xticklabels([g[0] for g in groups])
a.set_ylim(0, 1.05)
a.set_ylabel("genuine success per answer (prompt mean)")
a.set_title("(a) Who thinks, who answers (41 IFBench reach prompts)", loc="left", fontsize=10.5)
a.grid(axis="y", color=GRID, lw=0.8, zorder=0)
a.spines[["top", "right"]].set_visible(False)
a.legend(frameon=False, loc="upper left", fontsize=8.5)
# (b) budget curves
xs = [0, 1, 2, 3, 4, 5, 6]
lab = ["0", "1k", "2k", "4k", "8k", "16k", "full"]
for wr, col, full, name in (("dpo", BLUE, "T1", "DPO start answers"), ("s2300", ORANGE, "T2", "RL step 2300 answers")):
    cells = [f"T0-{wr}"] + [f"B{N}-{wr}" for N in (1024, 2048, 4096, 8192, 16384)] + [full]
    pts = [val(c) for c in cells]
    xx = [x for x, p in zip(xs, pts) if p[0] is not None]
    yy = [p[0] for p in pts if p[0] is not None]
    b.plot(xx, yy, color=col, lw=2, marker="o", ms=8, mec=SURF, mew=2, zorder=3, label=name + " (RL's thinking cut at N)")
    for x, p in zip(xs, pts):
        if p[1] is not None:
            b.errorbar(x, p[0], yerr=[[p[0] - p[1]], [p[2] - p[0]]], color=col, capsize=3, lw=1.2, zorder=2)
    b.text(xx[-1] + 0.12, yy[-1], name.split(" answers")[0], color=INK, fontsize=8.5, va="center")
fx = {2048: 2, 4096: 3, 8192: 4}
fp = [(fx[N], tuple(S["reach-41"].get(f"F{N}", {}).get("genuine") or (None,) * 3)) for N in fx]
fp = [(x, p) for x, p in fp if p[0] is not None]
if fp:
    b.plot([x for x, _ in fp], [p[0] for _, p in fp], color=AQUA, lw=2, ls="--", marker="s", ms=8, mec=SURF, mew=2,
           zorder=3, label="fresh budget forcing: RL thinks itself, capped at N (6 prompts)")
b.set_xticks(xs)
b.set_xticklabels(lab)
b.set_xlim(-0.3, 7.2)
b.set_ylim(0, 1.05)
b.set_xlabel("thinking budget N (tokens of the supplied or generated thinking)")
b.set_title("(b) Thinking budget", loc="left", fontsize=10.5)
b.grid(axis="y", color=GRID, lw=0.8, zorder=0)
b.spines[["top", "right"]].set_visible(False)
b.legend(frameon=False, loc="upper left", fontsize=8)
fig.text(0.01, 0.005, "Genuine = official strict checker and blinded model readers (hand gate). Bars and points: mean over "
         "prompts; whiskers: 95 % prompt bootstrap. B(0) = no thinking; B(full) = full trace; traces shorter than N are "
         "full. Fresh forcing is on 6 of the 41 prompts.", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("figures/olmo_transplant.png", dpi=160)
print("wrote figures/olmo_transplant.png")
