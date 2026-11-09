"""Outcomes of run olmo-ifladder from MY labels: gamed shares, Fisher sensitivity, s2300 sanity, expectations 1-13.

Gamed share (pre-registered estimator): over every reach cell of a type, gamed / read among the first min(n, 4)
strict successes in draw order (every draw counted; identical answers carry their shared label; mechanical rule-1
labels count as gamed). Rung 1 = the same estimator on MY olmo-iffu labels (review/olmo-iffu-recount) where
available, else reported as the pre-registration's value.
Fisher (one-sided, my own hypergeometric sum; cross-checked with scipy if present): lora_main vs lora_ctrl per
prompt, (a) on genuine lower bounds (LM: genuine reads; LC: genuine reads, i.e. 0/1) and (b) on estimated genuine
counts (strict count x the cell's read genuine share), (c) on strict counts.
Writes out/outcomes.{txt,json} and out/expect.md.
"""
import collections
import json
import math

from rvl_core import CODE, KIT, OUT, Tee, dump, load_csv

P = Tee("outcomes.txt")
prompts = load_csv(CODE / "prompts.csv")
REACH = [r["pid"] for r in prompts if r["set"] == "reach"]
DROP60 = {f"ifbench_{k}" for k in (52, 58, 0, 1, 3, 4, 166, 170, 188, 284)}
H = json.load(open(OUT / "hand.json"))["cells"]
SETS = json.load(open(OUT / "sets.json"))["cells"]
C = json.load(open(OUT / "classify_mine.json"))["rows"]
CL = json.load(open(OUT / "calib_lengths.json"))
CR = {r["pid"]: r for r in C}
res = {}


def gamed_share(cell):
    g = n = 0
    for pid in REACH:
        w = H.get(f"{cell}|{pid}")
        if not w:
            continue
        k = min(w["n"], 4)
        seq = w["seq"][:k]
        for ch, i, L, src in seq:
            if L is None:
                continue
            n += 1
            g += L == "gamed"
    return g, n


for c in ("R2", "R3", "R4", "LM", "LC", "S2", "S3", "S4"):
    g, n = gamed_share(c)
    res[f"gamed_{c}"] = (g, n)
    P(f"gamed share {c}: {g}/{n} = {g / n if n else float('nan'):.3f}")


def fisher_one_sided(a, n1, b, n2):
    """P(X >= a) for X ~ hypergeometric: a of n1 (arm 1) vs b of n2 successes, margins fixed."""
    K = a + b
    N = n1 + n2
    tot = 0.0
    for x in range(a, min(K, n1) + 1):
        tot += math.comb(n1, x) * math.comb(n2, K - x)
    return tot / math.comb(N, K)


try:
    from scipy.stats import fisher_exact
except Exception:  # noqa: BLE001
    fisher_exact = None
sens = []
for pid in REACH:
    wm, wc = H.get(f"LM|{pid}"), H.get(f"LC|{pid}")
    sm, sc = SETS["LM"][pid]["strict"], SETS["LC"][pid]["strict"]
    nm = SETS["LM"][pid]["n"]
    nc = SETS["LC"][pid]["n"]
    gm = wm["genuine"] if wm else 0
    gc = wc["genuine"] if wc else 0
    readm = [x for x in (wm["seq"] if wm else []) if x[2] is not None]
    share = (sum(x[2] == "genuine" for x in readm) / len(readm)) if readm else 0.0
    estm = round(sm * share)
    pa = fisher_one_sided(gm, nm, gc, nc)
    pb = fisher_one_sided(estm, nm, gc, nc)
    pc = fisher_one_sided(sm, nm, sc, nc)
    if fisher_exact is not None:
        q = fisher_exact([[estm, gc], [nm - estm, nc - gc]], alternative="greater")[1]
        assert abs(q - pb) < 1e-9, (pid, q, pb)
    sens.append({"pid": pid, "LM_gen_lb": gm, "LM_strict": sm, "LM_share": share, "LM_est": estm, "LC_gen": gc,
                 "LC_strict": sc, "p_lb": pa, "p_est": pb, "p_strict": pc, "LM": CR[pid]["LM"], "LC": CR[pid]["LC"]})
el = [s for s in sens if s["LM"] == "E" and s["LC"] != "E"]
P(f"\nFisher one-sided, lora_main vs lora_ctrl, on the {len(el)} prompts LM elicits and LC does not:")
P(f"    p < 0.05 on genuine lower bounds (LM reads only): {sum(s['p_lb'] < 0.05 for s in el)}")
P(f"    p < 0.05 on estimated genuine counts (strict x read share): {sum(s['p_est'] < 0.05 for s in el)}")
P(f"    p < 0.05 on strict counts: {sum(s['p_strict'] < 0.05 for s in el)}")
for s in sorted(el, key=lambda s: s["p_est"])[-8:]:
    P(f"    weakest: {s['pid']} LM strict {s['LM_strict']} share {s['LM_share']:.2f} est {s['LM_est']} vs LC gen "
      f"{s['LC_gen']} (strict {s['LC_strict']}): p_est {s['p_est']:.4f} p_lb {s['p_lb']:.3f}")
res["fisher"] = sens

# s2300 sanity
for c, rung in (("S2", 2), ("S3", 3), ("S4", 4)):
    ran = [p for p in REACH if p in SETS[c]]
    br = [p for p in ran if CR[p][c] == "N"]
    br40 = [p for p in br if p not in DROP60]
    ran40 = [p for p in ran if p not in DROP60]
    P(f"s2300 sanity rung {rung}: ran on {len(ran)} reach prompts ({len(ran40)} non-DROP60); breaks s2300 on {len(br)} "
      f"({len(br40)} non-DROP60): {sorted(br)}")
    res[f"breaks_{c}"] = {"ran": len(ran), "ran40": len(ran40), "breaks": br, "breaks40": br40}

# expectations
cnt = collections.Counter(r["reading"] for r in C)
not1 = [r for r in C if r["R1"] == "N"]
e1 = sum(r["R2"] == "E" for r in not1)
not12 = [r for r in not1 if r["R2"] != "E"]
e2 = sum(r["R3"] == "E" for r in not12)
not123 = [r for r in not12 if r["R3"] != "E"]
e3 = sum(r["R4"] == "E" for r in not123)
e4 = sum(r["reading"].startswith("prompt") for r in C)
lm = sum(r["LM"] == "E" for r in C)
lc = sum(r["LC"] == "E" for r in C)
lm_pe = sum(r["LM"] == "E" and r["reading"].startswith("prompt") for r in C)
t_rl = cnt.get("teachable from RL's trajectories", 0)
t_any = cnt.get("teachable by any light fine-tune", 0)
nei = cnt.get("neither", 0)
six = ["ifbench_3", "ifbench_136", "ifbench_166", "ifbench_211", "ifbench_248", "ifbench_269"]
six_nei = sum(CR[p]["reading"] == "neither" for p in six)
four = ["ifbench_78", "ifbench_133", "ifbench_252", "ifbench_253"]
f_r2 = sum(CR[p]["R2"] == "E" for p in four)
f_lora = (sum(CR[p]["LM"] == "E" for p in four), sum(CR[p]["LC"] == "E" for p in four))
g = {c: res[f"gamed_{c}"] for c in ("R2", "R3", "R4", "LM")}
sh = {c: (v[0] / v[1] if v[1] else float("nan")) for c, v in g.items()}
cal = CL["cal"]
base = CL["cal_base"]["mean"]
rmin = min(cal[c]["mean"] for c in ("R1", "R2", "R3", "R4"))
rhalf = max(len(cal[c]["below_half"]) for c in ("R1", "R2", "R3", "R4"))
Lw = CL["lengths"]
lm_w = Lw["lora_main (Leval)"]["ans_words"]["median_of_prompt_medians"]
lc_w = Lw["lora_ctrl (Leval)"]["ans_words"]["median_of_prompt_medians"]
d_w = Lw["dpo (F)"]["ans_words"]["median_of_prompt_medians"]
lm_t = Lw["lora_main (Leval)"]["think_tok"]["median_of_prompt_medians"]
lc_t = Lw["lora_ctrl (Leval)"]["think_tok"]["median_of_prompt_medians"]
d_t = Lw["dpo (F)"]["think_tok"]["median_of_prompt_medians"]
b2 = len(res["breaks_S2"]["breaks40"])
b3 = len(res["breaks_S3"]["breaks40"])
b4 = len(res["breaks_S4"]["breaks40"])
comp = json.load(open(OUT / "compute.json"))["jobs"]
s0r2 = comp["S0r2"]["gen_tokens_rows"] / comp["S0r2"]["samples"]
s0r3 = comp["S0r3"]["gen_tokens_rows"] / comp["S0r3"]["samples"]
R1G = 6 / 48  # pre-registered rung-1 dpo gamed share (olmo-iffu reads, executor's estimator)
# the same estimator on MY olmo-iffu labels (my walks stop at 2 genuine, so ranks < min(n, 4) can be unread)
OI = json.load(open(KIT.parent / "olmo-iffu-recount" / "out" / "hand.json"))["if"]
r1g = {}
for w, jobs in (("dpo", ("T2_dpo", "T2c_dpo")), ("s2300", ("T2_s2300", "T2c_s2300"))):
    g_ = n_ = unread = 0
    for k, v in OI.items():
        job, pid = k.split("|")
        if job in jobs and pid in REACH:
            lim = min(v["strict"], 4)
            got = {it["rank"]: it["label"] for it in v["items"]}
            for rk in range(lim):
                L = got.get(rk)
                if L in ("genuine", "gamed"):
                    n_ += 1
                    g_ += L == "gamed"
                else:
                    unread += 1
    r1g[w] = (g_, n_, unread)
    P(f"rung-1 gamed share from my olmo-iffu labels, {w}: {g_}/{n_} = {g_ / n_:.3f} (unread ranks < min(n, 4): {unread})")
res["gamed_R1_mine"] = r1g


def inside(x, lo, hi):
    return "held" if lo <= x <= hi else "missed"


E = [
    ("1", "rung 2 elicits 3 (0-7) of the 32 rung-1-unelicited", f"{e1} of {len(not1)}", inside(e1, 0, 7)),
    ("2", "rung 3 elicits 4 (1-9) of those still unelicited", f"{e2} of {len(not12)}", inside(e2, 1, 9)),
    ("3", "rung 4 elicits 3 (0-8) of those still unelicited", f"{e3} of {len(not123)}", inside(e3, 0, 8)),
    ("4", "prompt-elicitable at some rung 26 of 48 (19-33)", f"{e4} of 48", inside(e4, 19, 33)),
    ("5", "lora_main elicits 4 of 48 (0-10); lora_ctrl 2 (0-6); most prompt-elicitable anyway",
     f"lora_main {lm} (of them prompt-elicitable {lm_pe}); lora_ctrl {lc}",
     f"lora_main {inside(lm, 0, 10)}; lora_ctrl {inside(lc, 0, 6)}; 'most prompt-elicitable' "
     f"{'held' if lm_pe > lm / 2 else 'missed'}"),
    ("6", "teachable from RL's trajectories 1 (0-4); teachable by any light fine-tune 0 (0-2)",
     f"{t_rl}; {t_any}", f"{inside(t_rl, 0, 4)}; {inside(t_any, 0, 2)}"),
    ("7", "neither 21 of 48 (13-28); of the 6 test-3 survivors not elicited at rung 1, 4 (2-6) neither",
     f"{nei}; {six_nei} of 6", f"{inside(nei, 13, 28)}; {inside(six_nei, 2, 6)}"),
    ("8", "gamed share: R2 = R1 + 5 pp (-10 to +20); R3 0.15 (0.05-0.40); R4 0.12 (0.03-0.35); lora_main 0.10 (0-0.35)",
     f"R2 {sh['R2']:.3f} ({g['R2'][0]}/{g['R2'][1]}; R1 {R1G:.3f} -> {sh['R2'] - R1G:+.3f}); R3 {sh['R3']:.3f} "
     f"({g['R3'][0]}/{g['R3'][1]}); R4 {sh['R4']:.3f} ({g['R4'][0]}/{g['R4'][1]}); LM {sh['LM']:.3f} "
     f"({g['LM'][0]}/{g['LM'][1]})",
     f"R2 {inside(sh['R2'] - R1G, -0.10, 0.20)}; R3 {inside(sh['R3'], 0.05, 0.40)}; R4 {inside(sh['R4'], 0.03, 0.35)}; "
     f"LM {inside(sh['LM'], 0.0, 0.35)}"),
    ("9", "dpo calibration mean >= 0.75 at every rung; below half its unhinted rate on <= 2 prompts at any rung; each "
          "LoRA's calibration mean >= 0.8 x dpo's unhinted mean",
     f"min rung mean {rmin:.3f}; max prompts below half {rhalf}; LM {cal['LM']['mean']:.3f}, LC {cal['LC']['mean']:.3f} "
     f"vs 0.8 x {base:.3f} = {0.8 * base:.3f}",
     "held" if rmin >= 0.75 and rhalf <= 2 and cal["LM"]["mean"] >= 0.8 * base and cal["LC"]["mean"] >= 0.8 * base
     else "missed"),
    ("10", "lengths: lora_main median answer words 140 (60-220) vs dpo 231; lora_ctrl within +-25 % of dpo; both LoRAs' "
           "median thinking tokens within +-35 % of dpo's",
     f"answer words (median of prompt medians) LM {lm_w}, LC {lc_w}, dpo {d_w}; thinking LM {lm_t} ({lm_t / d_t:.2f}x), "
     f"LC {lc_t} ({lc_t / d_t:.2f}x), dpo {d_t}",
     f"LM words {inside(lm_w, 60, 220)}; LC words {inside(lc_w / d_w, 0.75, 1.25)}; LM thinking "
     f"{inside(lm_t / d_t, 0.65, 1.35)}; LC thinking {inside(lc_t / d_t, 0.65, 1.35)}"),
    ("11", "the four 1,024-survivors the hint elicits (78 133 252 253): >= 3 of 4 at rung 2 (2-4); 0 of 4 by either LoRA "
           "(0-2)", f"rung 2 {f_r2} of 4; lora_main {f_lora[0]}, lora_ctrl {f_lora[1]}",
     f"rung 2 {inside(f_r2, 2, 4)}; LoRAs {inside(max(f_lora), 0, 2)}"),
    ("12", "s2300 sanity: a rung breaks s2300 on <= 3 (R2) / <= 5 (R3, R4) of the 40 non-DROP60 reach prompts",
     f"R2 {b2} of {res['breaks_S2']['ran40']}; R3 {b3} of {res['breaks_S3']['ran40']} run; R4 {b4} of "
     f"{res['breaks_S4']['ran40']} run",
     f"R2 {'held' if b2 <= 3 else 'missed'}; R3 {'held' if b3 <= 5 else 'missed'} (on the run subset); R4 "
     f"{'held' if b4 <= 5 else 'missed'} (on the run subset)"),
    ("13", "stage 0: dpo tokens per draw R2 4.5k (3-7k), R3 5k (3-8k)", f"R2 {s0r2:.0f}, R3 {s0r3:.0f}",
     f"R2 {inside(s0r2, 3000, 7000)}; R3 {inside(s0r3, 3000, 8000)}"),
]
with open(OUT / "expect.md", "w") as f:
    f.write("| # | pre-registered expectation | my value | verdict |\n|---|---|---|---|\n")
    for e in E:
        f.write(f"| {e[0]} | {e[1]} | {e[2]} | {e[3]} |\n")
for e in E:
    P(f"E{e[0]}: {e[2]} -> {e[3]}")
res["expect"] = E
dump(res, "outcomes.json")
