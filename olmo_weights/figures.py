"""olmo-weights figures (VPS-side, matplotlib) from artifacts/olmo_weights/tables/ (analyze.py).

Fig. 1  <fam>: relative change per optimizer step along the released pipeline (main path), coloured by training type,
        labelled stage bands, boundary-crossing intervals ringed, merges hollow; panels: per step, raw interval change,
        learning rate, per step / LR (aligned panels instead of a second y-axis).
Fig. 2  distance from each stage's start (relative), with straightness and mean consecutive cosine per stretch.
Fig. 3  per-module (rel. change per step vs the whole model, by stage) and per-layer x checkpoint heatmaps per stage.
Fig. 4  bitwise-unchanged and <= 1-ulp fractions per interval, and per module for RL.
Fig. 5  32B RL: change per step and distance from DPO with olmo-ifcurve's IFBench pass@1 / pass@8 and the rug of the
        48 reach prompts' first-genuine steps.
Fig. 6  LoRA (lora_main, lora_ctrl, random rank 16) against RL's change from DPO: cosine and size ratio per checkpoint,
        per module at step 2,300.
Fig. 7  7B RL from the base (RL-Zero IF / Math / Code) against RL from DPO.
Usage: python3 olmo_weights/figures.py [--tables D] [--out D] [--only 1,2,...]
"""
import argparse, csv, json, math, os

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# reference palette (dataviz skill), fixed order; validated light: worst adjacent CVD dE 9.1, normal-vision 19.6
C = {"stage1": "#2a78d6", "stage2": "#eb6834", "stage3": "#1baf7a", "sft": "#eda100", "dpo": "#e87ba4", "rl": "#008300",
     "rlzero": "#4a3aa7"}
LABEL = {"stage1": "pretraining", "stage2": "mid-training", "stage3": "long-context", "sft": "SFT", "dpo": "DPO",
         "rl": "RL", "rlzero": "RL-Zero"}
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e7e6e2", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "font.size": 9,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "lines.linewidth": 2, "legend.frameon": False})
JOB_ORDER = {"32B": ["b32_s1", "b32_s2", "b32_s3", "p32_sft", "p32_rl"], "7B": ["b7_s1", "b7_s2", "b7_s3", "p7_sft", "p7_rl"]}
CHAIN_ORDER = {"p32_sft": ["sft-5e-5", "sftmain-to-dpo"]}
MODEL = {"32B": "Olmo 3 32B pipeline (32.2 B params, bf16): Olmo-3-1125-32B → Olmo-3-32B-Think-SFT → -DPO → Olmo-3.1-32B-Think",
         "7B": "Olmo 3 7B pipeline (7.3 B params, bf16): Olmo-3-1025-7B → Olmo-3-7B-Think-SFT → -DPO → Olmo-3-7B-Think"}


def rd(path):
    if not os.path.exists(path):
        return []
    out = []
    for r in csv.DictReader(open(path)):
        for k, v in r.items():
            if v == "":
                r[k] = None
            else:
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
        out.append(r)
    return out


def stage_key(r):
    s = r["stage"]
    if isinstance(s, str) and s.startswith("rlzero"):
        return "rlzero"
    return s


def main_path(IV, fam):
    rows = [r for r in IV if r["family"] == fam and r["main_path"] in ("True", True) and r["kind"] != "gap"]
    jo = {j: i for i, j in enumerate(JOB_ORDER[fam])}

    def key(r):
        co = CHAIN_ORDER.get(r["job"], [])
        return (jo.get(r["job"], 99), co.index(r["chain"]) if r["chain"] in co else 0, r["idx"])
    rows.sort(key=key)
    return rows


def bands(ax, rows, ymax_label=True):
    """Shade contiguous stage runs and label them at the top."""
    runs, cur = [], None
    for x, r in enumerate(rows):
        s = stage_key(r) if r["kind"] != "merge" else (cur[0] if cur else stage_key(r))
        if cur and cur[0] == s:
            cur[2] = x
        else:
            cur = [s, x, x]
            runs.append(cur)
    for s, x0, x1 in runs:
        ax.axvspan(x0 - 0.5, x1 + 0.5, color=C.get(s, MUTED), alpha=0.07, lw=0)
        if ymax_label:
            ax.text((x0 + x1) / 2, 1.01, LABEL.get(s, s), transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=8, color=INK2)
    for s, x0, x1 in runs[1:]:
        ax.axvline(x0 - 0.5, color=MUTED, lw=0.8, ls=(0, (2, 2)))


def fig1(T, fam, out):
    rows = main_path(T["iv"], fam)
    if not rows:
        return
    x = np.arange(len(rows))
    fig, axs = plt.subplots(4, 1, figsize=(13, 10.5), sharex=True, gridspec_kw={"height_ratios": [3, 2, 1.3, 2]})
    panels = [("rel_per_step", "relative change per optimizer step\n‖θ_b − θ_a‖ / ‖θ_a‖ / steps"),
              ("rel", "raw interval change\n‖θ_b − θ_a‖ / ‖θ_a‖"),
              ("lr_mean", "learning rate\n(mean over the interval)"),
              ("rel_per_step_per_lr", "change per step ÷ LR")]
    for ax, (k, lab) in zip(axs, panels):
        bands(ax, rows, ymax_label=(ax is axs[0]))
        for i, r in enumerate(rows):
            v = r.get(k)
            if v is None or not (v > 0):
                if k == "rel_per_step" and r["kind"] == "merge":
                    ax.axvline(i, color=INK2, lw=0.8, ls=(0, (1, 2)))
                    ax.text(i, 0.02, " merge\n (0 steps)", transform=ax.get_xaxis_transform(), fontsize=7, color=INK2)
                continue
            s = stage_key(r)
            if r["kind"] == "merge":
                ax.plot(i, v, "o", ms=7, mfc="none", mec=INK, mew=1.4, zorder=4)
            elif r["kind"] == "main":
                ax.plot(i, v, "D", ms=5, mfc="none", mec=C.get(s, MUTED), mew=1.4, zorder=4)
            elif r["kind"] in ("boundary", "dpo"):
                ax.plot(i, v, "o", ms=8, color=C.get(s, MUTED), mec=INK, mew=1.4, zorder=5)
            else:
                ax.plot(i, v, "o", ms=4, color=C.get(s, MUTED), zorder=3)
        # connect consecutive same-stage points with a thin line
        for s in set(stage_key(r) for r in rows):
            xs = [i for i, r in enumerate(rows) if stage_key(r) == s and r["kind"] in ("within", "pair") and (r.get(k) or 0) > 0]
            if len(xs) > 1:
                segs = np.split(np.array(xs), np.where(np.diff(xs) > 1)[0] + 1)
                for sg in segs:
                    ax.plot(sg, [rows[i][k] for i in sg], color=C.get(s, MUTED), lw=1.2, alpha=0.8, zorder=2)
        ax.set_yscale("log")
        ax.set_ylabel(lab, fontsize=8)
    lbl = []
    for i, r in enumerate(rows):   # one tick per stage start (the band labels name the stages)
        if r["kind"] in ("boundary", "merge"):
            lbl.append((i, r["b"].split("/", 1)[1]))
    axs[-1].set_xticks([i for i, _ in lbl])
    axs[-1].set_xticklabels([t for _, t in lbl], rotation=60, ha="right", fontsize=7)
    axs[-1].set_xlabel("checkpoints in pipeline order (one point per interval, at its later checkpoint; stage 1: "
                       "adjacent pairs s → s+1,000 at sampled locations)", fontsize=8)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color=C[s], label=LABEL[s]) for s in ("stage1", "stage2", "stage3", "sft", "dpo", "rl")]
    h += [Line2D([], [], marker="o", ls="", color=MUTED, mec=INK, mew=1.4, ms=8, label="interval crossing a stage boundary"),
          Line2D([], [], marker="o", ls="", mfc="none", mec=INK, mew=1.4, ms=7, label="merge (0 training steps)")]
    if any(r["kind"] == "main" for r in rows):
        h.append(Line2D([], [], marker="D", ls="", mfc="none", mec=MUTED, mew=1.4, ms=5, label="last branch → main (steps unknown)"))
    axs[0].legend(handles=h, ncol=5, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 1.25))
    fig.suptitle(f"How much the weights move between consecutive released checkpoints\n{MODEL[fam]}", fontsize=10,
                 x=0.01, ha="left", y=0.998)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(os.path.join(out, f"fig1_{fam}.png"), dpi=150)
    plt.close(fig)


def fig2(T, out):
    CH = T["chains"]
    IV = T["iv"]
    panels = [("stage 2", ["stage 2, ingredient 1", "stage 2, ingredient 2 (every 4th)", "stage 2"]), ("stage 3", ["stage 3"]),
              ("SFT", ["SFT 5e-5 run", "SFT 1e-4", "SFT"]), ("RL", ["RL"]), ("stage 1 (sampled)", ["stage 1 (sampled)"])]
    fams = ["32B", "7B"]
    fig, axs = plt.subplots(2, len(panels), figsize=(15, 7.4))
    for fi, fam in enumerate(fams):
        for pi, (pname, names) in enumerate(panels):
            ax = axs[fi, pi]
            k = 0
            notes = []
            for c in CH:
                if c["family"] != fam or c["stretch"] not in names:
                    continue
                ex = set(T["tests"].get("excluded_names", []))
                rows = sorted([r for r in IV if r["job"] == c["job"] and r["chain"] == c["chain"] and r.get("dist_start_rel") is not None
                               and r["b"] not in ex], key=lambda r: r["idx"])
                end_i = next((r["idx"] for r in rows if r["b"] == c["end"]), None)
                rows = [r for r in rows if end_i is None or r["idx"] <= end_i]
                xs, ys = [0], [0]
                base = None
                for r in rows:
                    st = r["steps"] if r["steps"] is not None else 0
                    xs.append(xs[-1] + st if pname != "stage 1 (sampled)" else _step(r["b"]))
                    ys.append(r["dist_start_rel"])
                col = [C["stage2"], C["stage3"], C["sft"], C["rl"], C["stage1"]][pi]
                ls = "-" if k == 0 else (0, (3, 2))
                ax.plot(xs, ys, color=col if k == 0 else INK2, ls=ls, lw=1.6, marker="o" if len(xs) < 30 else None, ms=3)
                S = c["straightness"]
                notes.append(("— " if k == 0 else "- - ") + (f"{c['stretch']}: S {S:.2f}, cos {c['mean_cos_lag1']:+.2f}"
                             if S is not None and c["mean_cos_lag1"] is not None else c["stretch"]))
                k += 1
            ax.set_title(f"{fam} {pname}\n" + "\n".join(notes), fontsize=7, loc="left")
            if pname == "stage 1 (sampled)":
                ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
            ax.set_xlabel("optimizer steps since the stage start" if pname != "stage 1 (sampled)" else "stage-1 step", fontsize=7.5)
            if pi == 0:
                ax.set_ylabel("‖θ_t − θ_start‖ / ‖θ_start‖", fontsize=8)
    fig.suptitle("Distance from each stage's start (S = straightness: end distance ÷ path length over the released "
                 "checkpoints; cos = consecutive-change cosine). Stage 1: the sampled sequence, path = sum over pairs and gaps.",
                 fontsize=9, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(out, "fig2_distance_from_start.png"), dpi=150)
    plt.close(fig)


def _step(label):
    try:
        return int(label.rsplit("/", 1)[1])
    except ValueError:
        return None


def fig3(T, out):
    MOD = T["mod"]
    LAY = T["lay"]
    mods = ["embed", "q", "k", "v", "o", "q_norm", "k_norm", "attn_norm", "gate", "up", "down", "ffn_norm", "final_norm", "lm_head"]
    stages = ["stage1", "stage2", "stage3", "sft", "dpo", "rl", "rlzero"]
    for fam in ("32B", "7B"):
        IVf = [r for r in T["iv"] if r["family"] == fam]
        tot = {}
        for r in IVf:
            if r["kind"] in ("within", "pair", "dpo") and r.get("rel_per_step"):
                tot.setdefault(stage_key(r), []).append((r["job"], r["chain"], r["idx"], r["rel"]))
        st_here = [s for s in stages if s in tot]
        M = np.full((len(mods), len(st_here)), np.nan)
        Z = np.zeros((len(mods), len(st_here)), dtype=bool)
        for j, s in enumerate(st_here):
            keys = {(a, b, c): rel for a, b, c, rel in tot[s]}
            for i, m in enumerate(mods):
                ratios = [r["rel"] / keys[(r["job"], r["chain"], r["idx"])] for r in MOD
                          if r["family"] == fam and r["module"] == m and (r["job"], r["chain"], r["idx"]) in keys
                          and r["rel"] is not None]
                if ratios:   # a module that did not change at all (median 0) is shown as 0 at the colour floor
                    M[i, j] = np.log10(max(np.median(ratios), 1e-4))
                    Z[i, j] = np.median(ratios) == 0
        fig, axs = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1, 2.2]})
        lim = np.nanmax(np.abs(M)) if np.isfinite(M).any() else 1
        im = axs[0].imshow(M, cmap=_diverging(), vmin=-lim, vmax=lim, aspect="auto")
        axs[0].set_yticks(range(len(mods)))
        axs[0].set_yticklabels(mods, fontsize=8)
        axs[0].set_xticks(range(len(st_here)))
        axs[0].set_xticklabels([LABEL[s] for s in st_here], rotation=30, ha="right", fontsize=8)
        axs[0].grid(False)
        for i in range(len(mods)):
            for j in range(len(st_here)):
                if np.isfinite(M[i, j]):
                    axs[0].text(j, i, "0" if Z[i, j] else f"{10 ** M[i, j]:.2g}", ha="center", va="center",
                                fontsize=6.5, color=SURF if M[i, j] < -2 else INK)
        cb = fig.colorbar(im, ax=axs[0], fraction=0.05)
        cb.set_label("log10 (module's relative change ÷ whole model's), median over the stage's intervals", fontsize=7)
        axs[0].set_title(f"{fam}: which modules move more (> 1) or less (< 1) than the model as a whole", fontsize=8.5, loc="left")
        # per-layer heatmap: layers x within-stage intervals, all stages side by side (main path)
        rows = [r for r in main_path(T["iv"], fam) if r["kind"] in ("within", "pair", "boundary", "dpo")]
        keyx = {(r["job"], r["chain"], r["idx"]): x for x, r in enumerate(rows)}
        nl = int(max((r["layer"] for r in LAY if r["family"] == fam and r["layer"] is not None), default=0)) + 1
        H = np.full((nl, len(rows)), np.nan)
        for r in LAY:
            if r["family"] != fam or r["layer"] is None:
                continue
            x = keyx.get((r["job"], r["chain"], r["idx"]))
            if x is not None and r.get("rel_per_step"):
                H[int(r["layer"]), x] = np.log10(r["rel_per_step"])
        H = H - np.nanmedian(H, axis=0, keepdims=True)   # each interval relative to its median layer
        lim2 = np.nanpercentile(np.abs(H), 99) if np.isfinite(H).any() else 1
        im2 = axs[1].imshow(H, cmap=_diverging(), vmin=-lim2, vmax=lim2, aspect="auto", origin="lower")
        axs[1].grid(False)
        runs = []
        for x, r in enumerate(rows):
            s = stage_key(r)
            if runs and runs[-1][0] == s:
                runs[-1][2] = x
            else:
                runs.append([s, x, x])
        for s, x0, x1 in runs:
            axs[1].text((x0 + x1) / 2, nl + 0.5, LABEL[s], ha="center", va="bottom", fontsize=7.5, color=INK2)
            axs[1].axvline(x0 - 0.5, color=SURF, lw=2)
        axs[1].set_ylabel("layer", fontsize=8)
        axs[1].set_xlabel("intervals in pipeline order (as Fig. 1)", fontsize=8)
        axs[1].set_xticks([])
        cb2 = fig.colorbar(im2, ax=axs[1], fraction=0.03)
        cb2.set_label("log10 (layer's relative change ÷ the interval's median layer)", fontsize=7)
        fig.suptitle(f"Where the change happens — {MODEL[fam]}", fontsize=9, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(os.path.join(out, f"fig3_{fam}.png"), dpi=150)
        plt.close(fig)


def _sequential():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])


def _diverging():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("div", ["#184f95", "#3987e5", "#9ec5f4", "#f0efec", "#f1a9a8", "#e34948", "#a32a2a"])


def fig4(T, out):
    fig, axs = plt.subplots(2, 1, figsize=(13, 7), sharex=False)
    for ax, fam in zip(axs, ("32B", "7B")):
        rows = main_path(T["iv"], fam)
        rows = [r for r in rows if r["kind"] != "merge"]
        x = np.arange(len(rows))
        bands(ax, rows)
        eq = np.array([r["frac_eq"] if r.get("frac_eq") is not None else np.nan for r in rows])
        ul = np.array([r["frac_ulp"] if r.get("frac_ulp") is not None else np.nan for r in rows])
        ax.plot(x, ul, color=INK2, lw=1.4, marker="o", ms=3, label="|Δ| ≤ 1 ulp (incl. unchanged)")
        ax.plot(x, eq, color=INK, lw=1.4, marker="s", ms=3, ls=(0, (3, 1)), label="bitwise unchanged")
        ax.set_ylim(0, 1)
        ax.set_ylabel("fraction of weights", fontsize=8)
        ax.set_title(f"{fam}: weights that did not change, or changed by at most one bf16 rounding step, per interval",
                     fontsize=9, loc="left", pad=16)
        ax.legend(fontsize=8, loc="center left")
        lbl = [(i, r["b"].split("/", 1)[1]) for i, r in enumerate(rows) if r["kind"] in ("boundary", "dpo", "main")]
        ax.set_xticks([i for i, _ in lbl])
        ax.set_xticklabels([t for _, t in lbl], rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig4_unchanged.png"), dpi=150)
    plt.close(fig)


def fig5(T, out):
    rl = sorted([r for r in T["iv"] if r["job"] == "p32_rl" and r["chain"] == "rl"], key=lambda r: r["idx"])
    if not rl:
        return
    pk = rd("olmo_ifcurve/passk.csv")
    em = rd("olmo_ifcurve/emergence.csv")
    fig, axs = plt.subplots(3, 1, figsize=(10, 8.5), sharex=True, gridspec_kw={"height_ratios": [2, 2, 2.4]})
    st = [_step(r["b"]) for r in rl]
    axs[0].plot(st, [r["rel_per_step"] for r in rl], color=C["rl"], marker="o", ms=3.5, lw=1.4)
    axs[0].set_yscale("log")
    axs[0].set_ylabel("relative change\nper step", fontsize=8)
    axs[1].plot([0] + st, [0] + [r["dist_start_rel"] for r in rl], color=C["rl"], lw=1.8)
    axs[1].set_ylabel("‖θ_t − θ_DPO‖ / ‖θ_DPO‖", fontsize=8)
    for k, mk, col in ((1, "o", INK), (8, "s", INK2)):
        rows = sorted([r for r in pk if r["group"] == "all" and r["k"] == k and r["ckpt"] != "dpo_first8"
                       and r["pass_at_k"] is not None], key=lambda r: r["step"])   # pass@8 not measured at 50 / 200
        if rows:
            xs = [r["step"] for r in rows]
            axs[2].plot(xs, [r["pass_at_k"] for r in rows], color=col, marker=mk, ms=4, lw=1.6, label=f"IFBench pass@{k} (strict)")
            axs[2].fill_between(xs, [r["lo95"] for r in rows], [r["hi95"] for r in rows], color=col, alpha=0.08, lw=0)
            axs[2].text(xs[-1] + 30, rows[-1]["pass_at_k"], f"pass@{k}", fontsize=8, va="center", color=col)
    f1 = [r["F1_step"] for r in em if r.get("F1_step") is not None]
    axs[2].plot(f1, np.full(len(f1), 0.02), "|", color=C["rl"], ms=12, mew=1.2,
                label=f"first genuine success (rug; count per checkpoint), {len(f1)} reach prompts")
    for x0 in sorted(set(f1)):   # the rug sits on olmo-ifcurve's 9 checkpoints, so print how many prompts share a tick
        axs[2].text(x0, 0.06, str(sum(1 for v in f1 if v == x0)), ha="center", fontsize=7.5, color=C["rl"])
    axs[2].set_ylim(0, 1)
    axs[2].set_ylabel("olmo-ifcurve\n(IFBench, 218 prompts)", fontsize=8)
    axs[2].legend(fontsize=7.5, loc="center right")
    axs[2].set_xlabel("RL step (Olmo 3.1 Think 32B; 0 = Olmo-3-32B-Think-DPO)", fontsize=8)
    fig.suptitle("32B RL: weight change against instruction-following behaviour (olmo-ifcurve's reviewed numbers)",
                 fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(out, "fig5_rl32_ifcurve.png"), dpi=150)
    plt.close(fig)


def fig6(T, out):
    L = T["lora"]
    if not L:
        return
    L = sorted(L, key=lambda r: r["step"])
    st = [r["step"] for r in L]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axs[0]
    ax.plot(st, [r["cos_main"] for r in L], color=C["rl"], marker="o", ms=3.5, lw=1.6, label="lora_main (16 RL trajectories)")
    ax.plot(st, [r["cos_ctrl"] for r in L], color=C["dpo"], marker="s", ms=3.5, lw=1.6, label="lora_ctrl (16 DPO successes)")
    m = np.array([r["cos_rand_mean"] for r in L])
    sd = np.array([r["cos_rand_sd"] for r in L])
    ax.fill_between(st, m - 3 * sd, m + 3 * sd, color=MUTED, alpha=0.25, lw=0, label="random rank 16: mean ± 3 sd (8 draws)")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("RL step", fontsize=8)
    ax.set_ylabel("cosine with θ_t − θ_DPO\n(448 targeted matrices)", fontsize=8)
    ax.legend(fontsize=7)
    ax = axs[1]
    ax.plot(st, [r["norm_ratio_main"] for r in L], color=C["rl"], marker="o", ms=3.5, lw=1.6, label="lora_main")
    ax.plot(st, [r["norm_ratio_ctrl"] for r in L], color=C["dpo"], marker="s", ms=3.5, lw=1.6, label="lora_ctrl")
    ax.set_yscale("log")
    ax.set_xlabel("RL step", fontsize=8)
    ax.set_ylabel("‖ΔW_LoRA‖ / ‖θ_t − θ_DPO‖ (targeted matrices)", fontsize=8)
    ax.legend(fontsize=7)
    ax = axs[2]
    LM = [r for r in T["lora_mod"] if r["step"] == max(st)]
    mods = ["q", "k", "v", "o", "gate", "up", "down"]
    LM = {r["group"]: r for r in LM}
    xs = np.arange(len(mods))
    ax.bar(xs - 0.2, [LM[m]["cos_main"] if m in LM else 0 for m in mods], 0.38, color=C["rl"], label="lora_main")
    ax.bar(xs + 0.2, [LM[m]["cos_ctrl"] if m in LM else 0 for m in mods], 0.38, color=C["dpo"], label="lora_ctrl")
    ax.set_xticks(xs)
    ax.set_xticklabels(mods)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_ylabel(f"cosine at step {int(max(st))}, by module", fontsize=8)
    ax.legend(fontsize=7)
    fig.suptitle("Does a 16-example LoRA (olmo-ifladder, rank 16, on Olmo-3-32B-Think-DPO) point where RL went? "
                 "(Olmo 3.1 Think 32B RL checkpoints)", fontsize=9, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(out, "fig6_lora.png"), dpi=150)
    plt.close(fig)


def fig7(T, out):
    IV = T["iv"]
    runs = [("p7_rl", "rl", "RL from DPO (Olmo-3-7B-Think)", C["rl"], "-"),
            ("z7_if", "rlzero-if", "RL-Zero IF (from base)", C["rlzero"], "-"),
            ("z7_math", "rlzero-math", "RL-Zero Math (from base)", C["rlzero"], (0, (4, 2))),
            ("z7_code", "rlzero-code", "RL-Zero Code (from base)", C["rlzero"], (0, (1, 1.5)))]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
    excl = set(T["tests"].get("rlzero_excluded", []))
    for job, ch, lab, col, ls in runs:
        rows = sorted([r for r in IV if r["job"] == job and r["chain"] == ch and r["b"] not in excl and r["kind"] != "main"],
                      key=lambda r: _step(r["b"]) or 0)
        if not rows:
            continue
        st = [_step(r["b"]) for r in rows]
        axs[0].plot([0] + st, [0] + [r["dist_start_rel"] for r in rows], color=col, ls=ls, lw=1.6, label=lab)
        ok = [(s, r["rel_per_step"]) for s, r in zip(st, rows) if r["kind"] == "within" and r.get("rel_per_step")]
        axs[1].plot([a for a, _ in ok], [b for _, b in ok], color=col, ls=ls, lw=1.4, marker="o", ms=2.5, label=lab)
        axs[2].plot([0] + st, [1] + [r["frac_ulp_start"] for r in rows], color=col, ls=ls, lw=1.6, label=lab)
    axs[0].set_ylabel("‖θ_t − θ_start‖ / ‖θ_start‖", fontsize=8)
    axs[1].set_ylabel("relative change per step", fontsize=8)
    axs[1].set_title("spacing differs (25 steps from DPO, 100 for RL-Zero): per-step values are not\nspacing-matched; "
                     "distance from the start (left) is the fair comparison", fontsize=7, loc="left")
    axs[1].set_yscale("log")
    axs[2].set_ylabel("fraction within 1 ulp of the start", fontsize=8)
    for ax in axs:
        ax.set_xlabel("RL step", fontsize=8)
    axs[0].legend(fontsize=7)
    fig.suptitle("7B: RL from the base model (RL-Zero, start = Olmo-3-1025-7B main) against RL from DPO "
                 "(start = Olmo-3-7B-Think-DPO); LR 1e-6 constant in both", fontsize=9, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(out, "fig7_rlzero.png"), dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default="artifacts/olmo_weights/tables")
    ap.add_argument("--out", default="artifacts/olmo_weights/figures")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    T = dict(iv=rd(os.path.join(a.tables, "intervals.csv")), mod=rd(os.path.join(a.tables, "modules.csv")),
             lay=rd(os.path.join(a.tables, "layers.csv")), chains=rd(os.path.join(a.tables, "chains.csv")),
             lora=rd(os.path.join(a.tables, "lora.csv")), lora_mod=rd(os.path.join(a.tables, "lora_modules.csv")),
             tests=json.load(open(os.path.join(a.tables, "tests.json"))) if os.path.exists(os.path.join(a.tables, "tests.json")) else {})
    only = set(a.only.split(",")) if a.only else None
    for n, f in (("1", lambda: [fig1(T, fam, a.out) for fam in ("32B", "7B")]), ("2", lambda: fig2(T, a.out)),
                 ("3", lambda: fig3(T, a.out)), ("4", lambda: fig4(T, a.out)), ("5", lambda: fig5(T, a.out)),
                 ("6", lambda: fig6(T, a.out)), ("7", lambda: fig7(T, a.out))):
        if only and n not in only:
            continue
        try:
            f()
            print("figure", n, "ok")
        except Exception as e:  # a figure whose jobs are not finished yet
            print("figure", n, "skipped:", repr(e)[:200])


if __name__ == "__main__":
    main()
