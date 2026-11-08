"""Rates, contrasts, budget curves and readings for run olmo-transplant (reviewer's own analysis code).

Per sample: strict (my re-grade) and a genuine weight: 1 / 0 for a labelled success (read or identity-inherited),
the (prompt, run-condition) genuine share for an unread success (share = labelled genuine / labelled), 0 for a strict
failure. A cell's genuine count therefore equals strict x share, the pre-registered rule; subsets (copy / draft
splits, the primary B curve's substituted full rows) keep each labelled row's own label.
Condition rate = mean over prompts (equal weight) of the per-prompt rate; 95 % interval = percentile prompt bootstrap
(10,000 resamples, my seed 99). Paired contrasts by prompt; realised SD and MDD = 2.80 SD / sqrt(n).
Usage: rvt_rates.py [labels: exec | exec_r6 | mine | mine_r6 | strict]   -> out/rates_<labels>.{txt,json}
"""
import collections
import csv
import gzip
import json
import math
import random
import statistics
import sys

from rvt_core import ART, OUT, RAW, SCR, Pieces, Tee, answer_of, iter_gz, unb64, wsnorm
from rvt_labels import cell_of, table

MODE = sys.argv[1] if len(sys.argv) > 1 else "exec"  # *_held: re-opened thinking counted as failure (post hoc)
P = Tee(f"rates_{MODE}.txt")
B_RESAMPLES = 10000
CUTS = [1024, 2048, 4096, 8192, 16384]
res = {"mode": MODE}

prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
SETS = {"reach": [p["pid"] for p in prompts if p["set"] == "reach"],
        "brief20": [p["pid"] for p in prompts if p["brief20"] == "True"],
        "calib": [p["pid"] for p in prompts if p["set"] == "calib"]}
REQ6 = [p["pid"] for p in prompts if p["required6"] == "True"]
FAM = {p["pid"]: p["family"] for p in prompts}
tr = {r["trace"]: r for r in csv.DictReader(open(OUT / "traces_mine.csv"))}

# ---------------------------------------------------------------- labels
mine = None
if MODE.startswith("mine"):  # key -> label, from rvt_hand.py (my blinded re-read, majority of my readers)
    mine = json.load(open(OUT / ("my_labels_r6.json" if MODE.endswith("r6") else "my_labels.json")))
lab_rows = table(mine=mine, r6_strict=(MODE == "exec_r6")) if MODE != "strict" else []
if MODE.endswith("_vac"):  # sensitivity: rule 1 applied mechanically -- a sub-bullet answer with no '*' is vacuous
    SBV = {p["pid"] for p in prompts if "format:sub-bullets" in p["instruction_ids"]}
    no_star = set()
    for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
        for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
            if r["pid"] in SBV and "*" not in answer_of("</think>" + r["text"]):
                no_star.add(f"{job}|{r['rid']}|{r['i']}")
    for r in lab_rows:
        if r["key"] in no_star:
            r["label"], r["src"] = "gamed", "vac_rule"
if MODE == "mine_sb":  # sensitivity: natural reading of format:sub-bullets (a '-' line under every '*' line)
    SB = {p["pid"] for p in prompts if "format:sub-bullets" in p["instruction_ids"]}

    def real_sub(ans):
        lines = ans.split("\n")
        bul = [i for i, l in enumerate(lines) if l.lstrip().startswith("*") and not l.lstrip().startswith("**")]
        if not bul:
            return False
        for j, i in enumerate(bul):
            end = bul[j + 1] if j + 1 < len(bul) else len(lines)
            if not any(lines[k].lstrip().startswith("-") for k in range(i + 1, end)):
                return False
        return True

    no_sub = set()
    for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
        for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
            if r["pid"] in SB and not real_sub(answer_of("</think>" + r["text"])):
                no_sub.add(f"{job}|{r['rid']}|{r['i']}")
    for r in lab_rows:
        if r["key"] in no_sub:
            r["label"], r["src"] = "gamed", "sb_rule"
lab = {r["key"]: r for r in lab_rows}
cellc = collections.defaultdict(lambda: [0, 0])  # (job, pid, cell) -> [labelled, labelled genuine]
cellc_all = collections.defaultdict(lambda: [0, 0])
for r in lab_rows:
    if r["label"] in ("genuine", "gamed"):
        cellc_all[(r["job"], r["pid"], r["cell"])][0] += 1
        cellc_all[(r["job"], r["pid"], r["cell"])][1] += r["label"] == "genuine"
        if r["src"] not in ("vac_rule", "sb_rule"):  # mechanical labels do not enter the share ...
            cellc[(r["job"], r["pid"], r["cell"])][0] += 1
            cellc[(r["job"], r["pid"], r["cell"])][1] += r["label"] == "genuine"
for k, v in cellc_all.items():  # ... unless they are the cell's only labels
    if not cellc[k][0]:
        cellc[k] = v

# ---------------------------------------------------------------- sample rows
grade = {}
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            g = json.loads(ln)
            grade[g["key"]] = g
S = []
undefined_cells = set()
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        k = f"{job}|{r['rid']}|{r['i']}"
        st = grade[k]["strict"]
        cell = cell_of(r)
        if not st:
            gw = 0.0
        elif MODE == "strict":
            gw = 1.0
        else:
            L = lab[k]
            if L["label"] == "genuine":
                gw = 1.0
            elif L["label"] == "gamed":
                gw = 0.0
            else:
                c = cellc.get((job, r["pid"], cell))
                if c and c[0]:
                    gw = c[1] / c[0]
                else:
                    gw = float("nan")
                    undefined_cells.add((job, r["pid"], cell))
        ans = answer_of("</think>" + r["text"])
        if MODE.endswith("_held") and "</think>" in r["text"]:  # post hoc: an answer that re-opened thinking fails
            st, gw = False, 0.0
        S.append({"key": k, "job": job, "writer": r["writer"], "pid": r["pid"], "cond": r["cond"], "cut": r["cut"],
                  "cell": cell, "trace": r.get("trace", ""), "strict": int(st), "g": gw,
                  "finish": r["finish"], "close2": "</think>" in r["text"], "norm": wsnorm(ans),
                  "natural": r.get("natural")})
P(f"mode {MODE}: {len(S)} sample rows; cells with an unread success and no labelled success (genuine undefined): "
  f"{len(undefined_cells)} (jobs {dict(collections.Counter(c[0] for c in undefined_cells))})")


def jobs_for(st, writer):
    return f"{'R' if st != 'calib' else 'C'}_{writer}"


# per (job, pid, cell) -> list of rows ; per (job, trace, cell) too
by_cell = collections.defaultdict(list)
by_trace_cell = collections.defaultdict(list)
for s in S:
    by_cell[(s["job"], s["pid"], s["cell"])].append(s)
    if s["trace"]:
        by_trace_cell[(s["job"], s["trace"], s["cell"])].append(s)


def mean_of(rows, field):
    v = [r[field] for r in rows]
    return sum(v) / len(v) if v else None


def per_prompt(st, writer, cell, field):
    """{pid: rate} for a sampled run-condition."""
    job = jobs_for(st, writer)
    out = {}
    for pid in SETS[st]:
        rows = by_cell.get((job, pid, cell), [])
        if rows:
            out[pid] = mean_of(rows, field)
    return out


def per_prompt_B(st, writer, N, field, primary=True):
    """Primary curve: every rl trace; traces with c <= N contribute their full-condition rows. Secondary: cut only."""
    job = jobs_for(st, writer)
    full = "T1" if writer == "dpo" else "T2"
    out, out_full = {}, {}
    for pid in SETS[st]:
        rows, frows = [], []
        for t, m in tr.items():
            if m["pid"] != pid or m["kind"] != "rl" or m["set"] != ("calib" if st == "calib" else "reach"):
                continue
            if int(m["c"]) > N:
                rows += by_trace_cell[(job, t, f"B{N}")]
                frows += by_trace_cell[(job, t, full)]
            elif primary:
                rows += by_trace_cell[(job, t, full)]
                frows += by_trace_cell[(job, t, full)]
        if rows:
            out[pid] = mean_of(rows, field)
            out_full[pid] = mean_of(frows, field)
    return out, out_full


def boot(vals, fn=None, seed=99):
    """percentile bootstrap over prompts of fn (default mean) of a list of per-prompt values or tuples"""
    rng = random.Random(seed)
    n = len(vals)
    fn = fn or (lambda xs: sum(xs) / len(xs))
    est = fn(vals)
    bs = []
    for _ in range(B_RESAMPLES):
        smp = [vals[rng.randrange(n)] for _ in range(n)]
        try:
            bs.append(fn(smp))
        except ZeroDivisionError:
            continue
    bs.sort()
    lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]
    return est, lo, hi


def fmt(e, lo=None, hi=None):
    if e is None or (isinstance(e, float) and math.isnan(e)):
        return "n/a"
    return f"{e:.3f}" + (f" [{lo:.3f}, {hi:.3f}]" if lo is not None else "")


def cond_table(st, field):
    out = {}
    specs = [("T1", "dpo", "T1"), ("T2", "s2300", "T2"), ("T3", "s2300", "T3"), ("T4", "dpo", "T4"),
             ("T0-dpo", "dpo", "T0"), ("T0-s2300", "s2300", "T0"), ("P-dpo", "dpo", "P"), ("P-s2300", "s2300", "P")]
    for name, w, cell in specs:
        pp = per_prompt(st, w, cell, field)
        if any(isinstance(v, float) and math.isnan(v) for v in pp.values()):
            out[name] = (float("nan"), None, None, len(pp), pp)
            continue
        e, lo, hi = boot(list(pp.values())) if pp else (None, None, None)
        out[name] = (e, lo, hi, len(pp), pp)
    for w in ("dpo", "s2300"):
        for N in CUTS:
            pp, _ = per_prompt_B(st, w, N, field, primary=True)
            if any(isinstance(v, float) and math.isnan(v) for v in pp.values()):
                out[f"B{N}-{w}"] = (float("nan"), None, None, len(pp), pp)
                continue
            e, lo, hi = boot(list(pp.values()))
            out[f"B{N}-{w}"] = (e, lo, hi, len(pp), pp)
    return out


ALL = {}
for st in ("reach", "brief20", "calib"):
    for field in ("strict", "g"):
        if MODE == "strict" and field == "g":
            continue
        t = cond_table(st, field)
        ALL[(st, field)] = t
        P(f"\n== {st} ({len(SETS[st])} prompts), {'strict' if field == 'strict' else 'genuine'} rates "
          f"(mean over prompts, 95 % prompt bootstrap)")
        for name, (e, lo, hi, n, _) in t.items():
            P(f"   {name:12s} {fmt(e, lo, hi)}   (n prompts {n})")
res["tables"] = {f"{k[0]}|{k[1]}": {n: v[:4] for n, v in t.items()} for k, t in ALL.items()}

# ---------------------------------------------------------------- paired contrasts, R1
def paired(st, field, a, b):
    ta, tb = ALL[(st, field)][a][4], ALL[(st, field)][b][4]
    common = [p for p in SETS[st] if p in ta and p in tb]
    d = [ta[p] - tb[p] for p in common]
    e, lo, hi = boot(d)
    sd = statistics.stdev(d) if len(d) > 1 else float("nan")
    return e, lo, hi, sd, len(d), 2.80 * sd / math.sqrt(len(d))


for st in ("reach", "brief20", "calib"):
    for field in ("strict", "g"):
        if (st, field) not in ALL:
            continue
        P(f"\n== paired contrasts, {st}, {'strict' if field == 'strict' else 'genuine'}: mean [95 %], realised SD, n, MDD")
        for name, a, b in [("D21 = T2 - T1", "T2", "T1"), ("D34 = T3 - T4", "T3", "T4"),
                           ("D0 = T0s - T0d", "T0-s2300", "T0-dpo"), ("D30 = T3 - T0s", "T3", "T0-s2300"),
                           ("T1 - T0d", "T1", "T0-dpo")]:
            e, lo, hi, sd, n, mdd = paired(st, field, a, b)
            P(f"   {name:16s} {fmt(e, lo, hi)}  SD {sd:.3f}  n {n}  MDD {mdd:.3f}")
            res[f"paired|{st}|{field}|{a}-{b}"] = [e, lo, hi, sd, n, mdd]
        t1, t2 = ALL[(st, field)]["T1"][4], ALL[(st, field)]["T2"][4]
        common = [p for p in SETS[st] if p in t1 and p in t2]
        pairs = [(t1[p], t2[p]) for p in common]
        e, lo, hi = boot(pairs, fn=lambda xs: sum(x[0] for x in xs) / sum(x[1] for x in xs))
        P(f"   R1 = T1 / T2     {fmt(e, lo, hi)}")
        res[f"R1|{st}|{field}"] = [e, lo, hi]

# ---------------------------------------------------------------- B curves, retained gain
def Fgain(G, G0, Gf):
    den = Gf - G0
    return (G - G0) / den if den >= 0.10 else None, den


for st in ("reach", "brief20"):
    for field in ("strict", "g"):
        if (st, field) not in ALL:
            continue
        t = ALL[(st, field)]
        P(f"\n== B curves, {st}, {'strict' if field == 'strict' else 'genuine'}: G(N) primary; F(N) = (G(N)-G(0))/(G(full)-G(0)) "
          f"(defined if the denominator >= 0.10)")
        for w, full in (("dpo", "T1"), ("s2300", "T2")):
            G0, Gf = t[f"T0-{w}"][0], t[full][0]
            line = [f"G(0)={G0:.3f}"]
            for N in CUTS:
                G = t[f"B{N}-{w}"][0]
                F, den = Fgain(G, G0, Gf)
                line.append(f"G({N})={G:.3f} F={'undef' if F is None else f'{F:.3f}'}")
                res[f"F|{st}|{field}|{w}|{N}"] = F
                res[f"G|{st}|{field}|{w}|{N}"] = G
            line.append(f"G(full)={Gf:.3f} (denominator {Gf - G0:.3f})")
            GP = t[f"P-{w}"][0]
            FP, _ = Fgain(GP, G0, Gf)
            line.append(f"G(P)={GP:.3f} over {t[f'P-{w}'][3]} prompts, F(P)={'undef' if FP is None else f'{FP:.3f}'}")
            res[f"F|{st}|{field}|{w}|P"] = FP
            P(f"   {w}: " + "; ".join(line))
        # secondary curve (cut traces only) with the same traces' full rate
        for w in ("dpo", "s2300"):
            parts = []
            for N in CUTS:
                pp, pf = per_prompt_B(st, w, N, field, primary=False)
                if pp:
                    parts.append(f"N={N}: {statistics.mean(pp.values()):.3f} (same traces full "
                                 f"{statistics.mean(pf.values()):.3f}, {len(pp)} prompts)")
            P(f"   secondary (cut traces only) {w}: " + "; ".join(parts))

# P with matched traces: prompts having a drafted trace; G(full) over those same traces
for field in ("strict", "g"):
    if MODE == "strict" and field == "g":
        continue
    for w, full in (("dpo", "T1"), ("s2300", "T2")):
        job = jobs_for("reach", w)
        pp_p, pp_f, pp_0 = {}, {}, {}
        for pid in SETS["reach"]:
            ts = [t for t, m in tr.items() if m["pid"] == pid and m["kind"] == "rl" and m["set"] == "reach" and m["draft"]]
            if not ts:
                continue
            pp_p[pid] = mean_of(sum((by_trace_cell[(job, t, "P")] for t in ts), []), field)
            pp_f[pid] = mean_of(sum((by_trace_cell[(job, t, full)] for t in ts), []), field)
            pp_0[pid] = mean_of(by_cell[(job, pid, "T0")], field)
        Gp, Gf, G0 = (statistics.mean(x.values()) for x in (pp_p, pp_f, pp_0))
        F, den = Fgain(Gp, G0, Gf)
        P(f"   P matched ({'strict' if field == 'strict' else 'genuine'}), {w}: {len(pp_p)} prompts with a drafted trace: "
          f"G(P) {Gp:.3f}, G(full, same traces) {Gf:.3f}, G(0) {G0:.3f}, F(P) {'undef' if F is None else f'{F:.3f}'} "
          f"(denominator {den:.3f})")
        res[f"Pmatched|{field}|{w}"] = [Gp, Gf, G0, F, len(pp_p)]

# ---------------------------------------------------------------- N / c bins (post hoc), draft covariate, copies
pc = Pieces()
src_ans = {}
need = {(m["job"], m["pid"], int(m["chunk"]), int(m["i"])): t for t, m in tr.items() if m["kind"] == "rl"}
src_ids = {}
for job in sorted({k[0] for k in need}):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (job, r["pid"], r["chunk"], r["i"])
        if k in need:
            src_ans[need[k]] = wsnorm(r["text"].split("</think>", 1)[1])
            src_ids[need[k]] = unb64(r["ids"])
opening = {t: a[:40] for t, a in src_ans.items()}


def contains_opening(t, N):
    a = opening[t]
    if len(a) < 8:
        return False
    return a in wsnorm(pc.text(src_ids[t][:N]))


for field in ("strict", "g"):
    if MODE == "strict" and field == "g":
        continue
    nm = "strict" if field == "strict" else "genuine"
    P(f"\n== post hoc ({nm}): B(N) success by N / c bin, pooled over (trace, N) points (reach, cut traces)")
    for w in ("dpo", "s2300"):
        job = jobs_for("reach", w)
        bins = collections.defaultdict(list)
        split = collections.defaultdict(list)
        split_pp = collections.defaultdict(lambda: collections.defaultdict(list))
        for t, m in tr.items():
            if m["kind"] != "rl" or m["set"] != "reach":
                continue
            for N in CUTS:
                if int(m["c"]) <= N:
                    continue
                rows = by_trace_cell[(job, t, f"B{N}")]
                x = N / int(m["c"])
                b = min(int(x * 4), 3)
                bins[b].append(mean_of(rows, field))
                has = contains_opening(t, N)
                split[has].append(mean_of(rows, field))
                split_pp[has][m["pid"]].append(mean_of(rows, field))
        P(f"   {w}: " + "; ".join(f"N/c in [{b / 4:.2f}, {(b + 1) / 4:.2f}): {statistics.mean(v):.3f} ({len(v)} points)"
                           for b, v in sorted(bins.items())))
        a1 = statistics.mean(split[True]) if split[True] else float("nan")
        a0 = statistics.mean(split[False]) if split[False] else float("nan")
        pp1 = statistics.mean(statistics.mean(v) for v in split_pp[True].values()) if split_pp[True] else float("nan")
        pp0 = statistics.mean(statistics.mean(v) for v in split_pp[False].values()) if split_pp[False] else float("nan")
        P(f"   {w}: cut prefix contains the answer opening: {a1:.3f} ({len(split[True])} points) vs not {a0:.3f} "
          f"({len(split[False])} points); difference {a1 - a0:.3f}; prompt-weighted {pp1:.3f} vs {pp0:.3f} "
          f"({len(split_pp[True])} / {len(split_pp[False])} prompts), difference {pp1 - pp0:.3f}")
        res[f"draftsplit|{field}|{w}"] = [a1, len(split[True]), a0, len(split[False]), pp1, pp0]

# copies of the source trace's own answer, full conditions
P("\n== copies of the source trace's answer (whitespace-collapsed equality), reach")
for w, cell in (("dpo", "T1"), ("s2300", "T2"), ("dpo", "P"), ("s2300", "P")):
    job = jobs_for("reach", w)
    rows = [s for s in S if s["job"] == job and s["cell"] == cell]
    cp = [s for s in rows if s["norm"] == src_ans.get(s["trace"])]
    st_rows = [s for s in rows if s["strict"]]
    st_cp = [s for s in cp if s["strict"]]
    P(f"   {w} {cell}: {len(cp)} / {len(rows)} samples copy their trace's answer; strict successes {len(st_rows)}, of them "
      f"copies {len(st_cp)}; strict rate copies {mean_of(cp, 'strict') if cp else float('nan'):.3f} vs others "
      f"{mean_of([s for s in rows if s not in cp], 'strict'):.3f}")
    res[f"copies|{w}|{cell}"] = [len(cp), len(rows), len(st_rows), len(st_cp)]
for w, cell in (("dpo", "T1"), ("s2300", "T2")):
    job = jobs_for("reach", w)
    for field in ("strict", "g"):
        if MODE == "strict" and field == "g":
            continue
        d1 = [s for s in S if s["job"] == job and s["cell"] == cell and tr[s["trace"]]["draft"]]
        d0 = [s for s in S if s["job"] == job and s["cell"] == cell and not tr[s["trace"]]["draft"]]
        P(f"   {w} {cell} ({field}): traces whose thinking contains the answer opening {mean_of(d1, field):.3f} "
          f"({len(d1) // 8} traces) vs not {mean_of(d0, field):.3f} ({len(d0) // 8} traces)")

# ---------------------------------------------------------------- answers cut at the budget, second </think>
P("\n== answers cut at the budget (finish = length) and answers containing a second </think>, by job and cell")
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    c = collections.defaultdict(lambda: [0, 0, 0, 0])
    for s in S:
        if s["job"] == job:
            x = c[s["cell"]]
            x[0] += 1
            x[1] += s["finish"] == "length"
            x[2] += s["close2"]
            x[3] += s["close2"] and s["strict"]
    P(f"   {job}: " + "; ".join(f"{k} cut {v[1]}/{v[0]} ({100 * v[1] / v[0]:.2f} %) 2nd-close {v[2]} (strict {v[3]})"
                         for k, v in sorted(c.items())))
    res[f"cut|{job}"] = {k: v for k, v in c.items()}

# ---------------------------------------------------------------- fresh budget forcing
src_rows = collections.defaultdict(list)
fx = {}
for job in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            g = json.loads(ln)
            if g["pid"] in REQ6:
                src_rows[(job, g["pid"])].append(g["strict"])
for field in ("strict", "g"):
    if MODE == "strict" and field == "g":
        continue
    P(f"\n== fresh budget forcing F(N), s2300, the 6 required prompts x 16 ({'strict' if field == 'strict' else 'genuine'})")
    nat_f = statistics.mean(sum(src_rows[("F_s2300_ifb", p)]) / len(src_rows[("F_s2300_ifb", p)]) for p in REQ6)
    nat_all = statistics.mean(sum(src_rows[(j, p)].count(True) for j in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb")) /
                              sum(len(src_rows[(j, p)]) for j in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb")) for p in REQ6)
    for N in (2048, 4096, 8192):
        rows = [s for s in S if s["job"] == "F_s2300" and s["cut"] == N]
        pp = {p: mean_of([s for s in rows if s["pid"] == p], field) for p in REQ6}
        m = statistics.mean(pp.values())
        nat = sum(s["natural"] for s in rows)
        P(f"   F({N}): {m:.3f} (per prompt {', '.join(f'{p.split('_')[1]}:{v:.2f}' for p, v in pp.items())}); "
          f"natural </think> {nat}/{len(rows)}; share of s2300's fixed-phase strict rate on the 6 ({nat_f:.3f}): "
          f"{m / nat_f:.2f}; of all olmo-ifomega s2300 draws ({nat_all:.3f}): {m / nat_all:.2f}")
        res[f"fresh|{field}|{N}"] = [m, m / nat_f, m / nat_all]
    t2_6 = statistics.mean(ALL[("reach", field)]["T2"][4][p] for p in REQ6)
    t0_6 = statistics.mean(ALL[("reach", field)]["T0-s2300"][4][p] for p in REQ6)
    P(f"   on the same 6 prompts: T2 {t2_6:.3f}, T0-s2300 {t0_6:.3f}, B2048-s2300 "
      f"{statistics.mean(ALL[('reach', field)]['B2048-s2300'][4][p] for p in REQ6):.3f}, B8192-s2300 "
      f"{statistics.mean(ALL[('reach', field)]['B8192-s2300'][4][p] for p in REQ6):.3f}")

# ---------------------------------------------------------------- s2300's natural rate on reach (prereg anchor)
fx_reach = []
with gzip.open(OUT / "regrade" / "F_s2300_ifb.jsonl.gz", "rt") as f:
    per = collections.defaultdict(list)
    for ln in f:
        g = json.loads(ln)
        per[g["pid"]].append(g["strict"])
P(f"\n   s2300 fixed-phase strict rate on reach-41 (olmo-ifomega F_s2300_ifb, 8 per prompt, my re-grade): "
  f"{statistics.mean(sum(per[p]) / len(per[p]) for p in SETS['reach']):.3f}")

# ---------------------------------------------------------------- families
for field in ("strict", "g"):
    if MODE == "strict" and field == "g":
        continue
    t = ALL[("reach", field)]
    P(f"\n== by family (reach, {'strict' if field == 'strict' else 'genuine'}; mean over prompts)")
    fams = collections.defaultdict(list)
    for p in SETS["reach"]:
        fams[FAM[p]].append(p)
    for fm, ps in sorted(fams.items(), key=lambda x: -len(x[1])):
        P(f"   {fm:9s} n={len(ps):2d} " + " ".join(
            f"{nm} {statistics.mean(t[nm][4][p] for p in ps if p in t[nm][4]):.2f}" for nm in ("T1", "T2", "T3", "T4", "T0-dpo", "T0-s2300",
                                                                              "B2048-s2300", "P-s2300")))

# ---------------------------------------------------------------- readings
if MODE != "strict":
    t = ALL[("reach", "g")]
    R1 = res["R1|reach|g"][0]
    T1, T2, T3, T4 = (t[n][0] for n in ("T1", "T2", "T3", "T4"))
    T0d, T0s = t["T0-dpo"][0], t["T0-s2300"][0]
    D34 = res["paired|reach|g|T3-T4"][0]
    r1 = R1 >= 0.75 and T1 - T0d >= 0.30
    r2 = R1 <= 0.40 and T3 >= 0.22 and D34 >= 0.15
    r3 = (0.40 < R1 < 0.75) or not (r1 or r2)
    F2 = res["F|reach|g|s2300|2048"]
    F8 = res["F|reach|g|s2300|8192"]
    G2 = res["G|reach|g|s2300|2048"]
    fresh2 = res["fresh|g|2048"][1]
    r4 = [F2 is not None and F2 <= 0.25, F8 is not None and F8 >= 0.60, G2 <= T0d + 0.10, fresh2 <= 0.5]
    r5 = T0s >= T2 - 0.10 and all(res[f"G|reach|g|s2300|{N}"] >= T2 - 0.10 for N in CUTS)
    P("\n== pre-registered readings (reach-41, genuine)")
    P(f"   R1 {R1:.3f}; T1 - T0d {T1 - T0d:.3f}; T3 {T3:.3f}; D34 {D34:.3f}")
    P(f"   1 (in the thinking): {r1}; 2 (answer writing): {r2}; 3 (partly): {r3}")
    P(f"   4 (needs long search): parts F(2k)<=0.25 {r4[0]} (F={F2}), F(8k)>=0.60 {r4[1]} (F={F8}), "
      f"G(2k)<=T0d+0.10 {r4[2]} ({G2:.3f} vs {T0d + 0.10:.3f}), fresh F(2k)<=0.5 natural {r4[3]} ({fresh2:.2f}) "
      f"-> {all(r4)}")
    P(f"   5 (flat): {r5}; 6 (graded): {not all(r4) and not r5}")
    for w in ("dpo", "s2300"):
        FP = res[f"F|reach|g|{w}|P"]
        FPm = res[f"Pmatched|g|{w}"][3]
        P(f"   7 P, {w}: F(P) {FP} (matched traces {FPm}) -> plan suffices (>=0.60): "
          f"{FP is not None and FP >= 0.60}; copying (<=0.25): {FP is not None and FP <= 0.25}")
    res["readings"] = {"r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5}

# per-prompt table (strict and genuine) for comparison with the executor's results.csv in phase 2
with open(OUT / f"per_prompt_{MODE}.csv", "w", newline="") as fcsv:
    names = list(ALL[("reach", "strict")].keys())
    wr = csv.writer(fcsv)
    wr.writerow(["pid", "set", "family", "field"] + names)
    for st in ("reach", "calib"):
        for field in ("strict", "g"):
            if (st, field) not in ALL:
                continue
            for pid in SETS[st]:
                wr.writerow([pid, st, FAM[pid], field] + [
                    "" if pid not in ALL[(st, field)][n][4] else f"{ALL[(st, field)][n][4][pid]:.4f}" for n in names])
with open(OUT / f"per_prompt_fresh_{MODE}.csv", "w", newline="") as fcsv:
    wr = csv.writer(fcsv)
    wr.writerow(["pid", "field", "F2048", "F4096", "F8192"])
    for field in ("strict", "g"):
        if MODE == "strict" and field == "g":
            continue
        for pid in REQ6:
            wr.writerow([pid, field] + [f"{mean_of(by_cell[('F_s2300', pid, f'F{N}')], field):.4f}" for N in (2048, 4096, 8192)])
json.dump(res, open(OUT / f"rates_{MODE}.json", "w"), indent=1, default=str)
