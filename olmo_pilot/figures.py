#!/usr/bin/env python3
"""Figures for olmo-rlzero-pilot (style of nd-rl's 2026-10-31 σ figure: same x-axis label, muted axes, reference palette).

  olmo_pilot_passk.png  a: unbiased pass@k (rl grade) on the headline problems, 95 % problem-bootstrap bands, at k up to
                           each model's fixed budget (16 base, 8 RL); b: the RL checkpoints' reach candidates (solved by
                           the checkpoint in its 8 samples, never by the base in 16) still unsolved by the base as the
                           base's budget grows, and the reverse candidates still unsolved by step 2800 as its budget grows
  olmo_pilot_reach.png  expected entries / exits vs the base at matched k = 8, reach and strong reach at full budget,
                        against cumulative RL compute ÷ pretraining compute (low–high bounds as horizontal bars)
  olmo_pilot_likelihood.png  base vs generating-checkpoint mean log-prob per token for scored correct solutions

Usage: figures.py [--outdir figures]   (reads olmo_pilot/{passk,results,candidates,reach,compute_axis,likelihood}.csv)
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


def label(step):
    return "base (before RL)" if step == 0 else f"RL step {step}"


def rows(name):
    p = O / name
    return list(csv.DictReader(open(p))) if p.exists() else []


def grid(ax):
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def survival(res, cand_rows, who, budget_model, ks):
    """Number of candidates (rows) whose `budget_model` has no correct sample within its first k draws, for each k;
    None once some unresolved candidate has fewer than k draws (censored)."""
    out = []
    for k in ks:
        n, ok = 0, True
        for r in cand_rows:
            m = res[(budget_model, r)]
            fs, att = m["first_rl"], int(m["attempts"])
            if fs != "" and int(fs) <= k:
                continue
            if att < k:
                ok = False
                break
            n += 1
        out.append(n if ok else None)
    return out


def fig_passk(out):
    P = [r for r in rows("passk.csv") if r["grade"] == "rl"]
    if not P:
        return
    res = {(r["model"], r["pid"]): r for r in rows("results.csv")}
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.3), gridspec_kw=dict(wspace=0.28, width_ratios=[1, 1.15]))
    for step, m in sorted({(int(r["step"]), r["model"]) for r in P}):
        rr = [r for r in P if r["model"] == m and int(r["k"]) <= (16 if step == 0 else 8)]
        k = [int(r["k"]) for r in rr]
        y = [float(r["pass_at_k"]) for r in rr]
        a.fill_between(k, [float(r["lo95"]) for r in rr], [float(r["hi95"]) for r in rr], color=color(step),
                       alpha=0.12, lw=0)
        a.plot(k, y, color=color(step), lw=2, marker="o", ms=4, label=label(step))
        a.annotate(f"{y[-1]:.2f}", (k[-1], y[-1]), textcoords="offset points", xytext=(6, -3), fontsize=7.5, color=TEXT)
    a.set_xscale("log", base=2)
    a.set_xticks([1, 2, 4, 8, 16], ["1", "2", "4", "8", "16"])
    a.minorticks_off()
    grid(a)
    a.set_ylim(0, 1)
    a.set_xlabel("k (samples per problem)")
    a.set_ylabel("pass@k (the verifier RL rewarded)")
    a.set_title(f"a   pass@k, {P[0]['n_problems']} AIME 2024–26 problems", loc="left", fontsize=9.5, color=TEXT)
    a.legend(frameon=False, fontsize=8, loc="upper left")
    C = rows("candidates.csv")
    reach = [r["pid"] for r in C if r["kind"] == "reach_candidate"]
    rev = [r["pid"] for r in C if r["kind"] == "reverse_candidate"]
    ks = [16, 32, 64, 128, 256, 512]
    for m, step in (("step_2800", 2800), ("step_0500", 500)):
        cand = [p for p in reach if int(res[(m, p)]["succ_fixed_rl"]) > 0]
        y = survival(res, cand, m, "base", ks)
        kk = [k for k, v in zip(ks, y) if v is not None]
        yy = [v for v in y if v is not None]
        b.plot(kk, yy, color=color(step), lw=2, marker="o", ms=5, drawstyle="steps-post",
               label=f"{label(step)}'s new solves ({len(cand)}): still unsolved by the base")
        b.annotate(f"{yy[-1]}", (kk[-1], yy[-1]), textcoords="offset points", xytext=(6, 2), fontsize=8, color=TEXT)
    ks2 = [8, 16, 32, 64, 128, 256, 512]
    y = survival(res, rev, "step_2800", "step_2800", ks2)
    kk = [k for k, v in zip(ks2, y) if v is not None]
    yy = [v for v in y if v is not None]
    b.plot(kk, yy, color=BASE_C, lw=2, marker="s", ms=5, drawstyle="steps-post", ls=(0, (4, 2)),
           label=f"the base's solves RL step 2800 missed ({len(rev)}): still unsolved by step 2800")
    b.annotate(f"{yy[-1]}", (kk[-1], yy[-1]), textcoords="offset points", xytext=(6, 2), fontsize=8, color=TEXT)
    b.set_xscale("log", base=2)
    b.set_xticks(ks2, [str(x) for x in ks2])
    b.minorticks_off()
    grid(b)
    b.set_ylim(0, None)
    b.set_xlabel("samples drawn for the model that has not solved it yet")
    b.set_ylabel("candidate problems still unsolved")
    b.set_title("b   Apparent new solves, re-tested with more samples", loc="left", fontsize=9.5, color=TEXT)
    b.legend(frameon=False, fontsize=7.6, loc="upper right")
    fig.savefig(out / "olmo_pilot_passk.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_reach(out):
    R = [r for r in rows("reach.csv") if r["grade"] == "rl"]
    X = {int(r["step"]): r for r in rows("compute_axis.csv")}
    if not R or not X:
        return
    kcol = [c for c in R[0] if c.startswith("exp_entries_k")][0]
    k = kcol.rsplit("k", 1)[1]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    series = [(kcol, f"expected entries vs the base at k = {k}", "#2a78d6", "o", "-"),
              (f"exp_exits_k{k}", f"expected exits vs the base at k = {k}", BASE_C, "s", "-"),
              ("reach_full", "reach: solved by the checkpoint, never by the base (full budget)", "#4a3aa7", "D", "-"),
              ("strong_reach", "strong reach (pre-registered definition)", "#1baf7a", "^", (0, (4, 2)))]
    for key, lab, c, mk, ls in series:
        pts = sorted((int(r["step"]), float(r[key])) for r in R)
        xs = [float(X[s]["ratio_geomean"]) for s, _ in pts]
        lo = [float(X[s]["ratio_low"]) for s, _ in pts]
        hi = [float(X[s]["ratio_high"]) for s, _ in pts]
        ys = [y for _, y in pts]
        ax.errorbar(xs, ys, xerr=[[x - l for x, l in zip(xs, lo)], [h - x for x, h in zip(xs, hi)]], color=c,
                    marker=mk, ms=6, lw=2, ls=ls, capsize=0, elinewidth=1, label=lab)
        for (s, _), x, y in zip(pts, xs, ys):
            txt = f"{y:.1f}" if y % 1 else f"{y:.0f}"
            if key == kcol:
                txt = f"RL step {s}: {txt}"
            ax.annotate(txt, (x, y), textcoords="offset points", xytext=(7, 4), fontsize=7.5, color=TEXT)
    ax.set_xscale("log")
    ax.set_xticks([1e-4, 3e-4, 1e-3, 3e-3], ["10⁻⁴", "3×10⁻⁴", "10⁻³", "3×10⁻³"])
    ax.minorticks_off()
    ax.set_xlim(1e-4, 6e-3)
    grid(ax)
    ax.set_ylim(0, None)
    ax.set_xlabel("cumulative RL compute ÷ pretraining compute (FLOPs)")
    ax.set_ylabel("problems (of 83)")
    ax.set_title("Problems RL adds and loses relative to the base", loc="left", fontsize=9.5, color=TEXT)
    ax.legend(frameon=False, fontsize=7.3, loc="upper left")
    fig.savefig(out / "olmo_pilot_reach.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_likelihood(out):
    L = rows("likelihood.csv")
    if not L:
        return
    groups = [("reach", "RL solutions, problems the base never solved", "#4a3aa7", "D"),
              ("late", "RL solutions, problems the base solved only after > 16 samples", "#2a78d6", "o"),
              ("ckpt_other", "RL solutions, other problems", "#86b6ef", "^"),
              ("base_own", "the base's own solutions (extension)", BASE_C, "s"),
              ("base_own_pilot", "the base's own solutions (AIME 2023 pilot)", "#eda100", "v")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.3), gridspec_kw=dict(wspace=0.3))
    vals = [float(r[c]) for r in L for c in ("own_mean_lp", "base_mean_lp")]
    lo = min(vals) - 0.02
    for g, lab, c, mk in groups:
        rr = [r for r in L if r["group"] == g]
        if not rr:
            continue
        a.scatter([float(r["own_mean_lp"]) for r in rr], [float(r["base_mean_lp"]) for r in rr], s=24, color=c,
                  marker=mk, edgecolor=SURFACE, linewidth=0.8, label=f"{lab} (n = {len(rr)})", zorder=3)
        b.scatter([float(r["own_mean_lp"]) - float(r["base_mean_lp"]) for r in rr],
                  [100 * float(r["base_frac_lt_1e3"]) for r in rr], s=24, color=c, marker=mk, edgecolor=SURFACE,
                  linewidth=0.8, zorder=3)
    a.plot([lo, 0], [lo, 0], color=MUTED, lw=1, ls=(0, (4, 3)))
    a.annotate("same likelihood under both", (lo * 0.35, lo * 0.35), rotation=37, fontsize=7.5, color=MUTED)
    a.set_xlabel("generating model's mean log-prob per token")
    a.set_ylabel("base's mean log-prob per token")
    a.set_title("a   Correct solutions, scored by both models", loc="left", fontsize=9.5, color=TEXT)
    b.set_xlabel("generating model − base (nats per token)")
    b.set_ylabel("% of tokens the base gives p < 10⁻³")
    b.set_title("b   How surprising the base finds them", loc="left", fontsize=9.5, color=TEXT)
    for ax in (a, b):
        grid(ax)
    a.legend(frameon=False, fontsize=7.2, loc="upper left")
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
