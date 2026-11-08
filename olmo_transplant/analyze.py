#!/usr/bin/env python3
"""Analysis of run olmo-transplant (pre-registration preregistration/olmo-transplant.md, Analysis and Readings).

Inputs: olmo_transplant/{prompts,traces}.csv; artifacts/olmo_transplant/graded/<job>.jsonl and samples/<job>.jsonl.gz;
labels: olmo_ifomega/handcheck.csv (the reach traces' own answers), olmo_transplant/handcheck_src.csv (calibration
sources) and olmo_transplant/handcheck.csv (this run's reads).
Run-condition = (writer, rcond) as sampled: T1, T2, T3, T4, T0, B<N>, P, F<N>. Per (pid, writer, rcond):
  strict rate; labelled successes = read or identity-inherited (same whitespace-collapsed answer on the prompt);
  genuine count = labelled genuine + unlabelled strict x (labelled genuine share of that (pid, writer, rcond)); if it
  has no labelled success, the pooled share of (writer, rcond) over prompts is used and the fallback is counted.
Cells: T1 = dpo:T1, T2 = s2300:T2, T3 = s2300:T3, T4 = dpo:T4, T0-w = w:T0; B(N)-w per trace: the B<N> rows if the
trace's thinking content c > N, else its full rows (same input); B(0) = T0, B(full) = T1 / T2; P-w; F<N>.
A condition's rate is the mean over prompts (equal weight) with a 95 % prompt bootstrap (10,000 resamples, seed 1).
Rule 6 (title case in ALL CAPS) is reported under both readings: `genuine` (primary) and `genuine_r6strict`.
Writes olmo_transplant/results.csv (per set, pid, cell) and olmo_transplant/summary.md / summary.json.
Usage: analyze.py [--jobs R_dpo,R_s2300,C_dpo,C_s2300,F_s2300]"""
import argparse
import collections
import csv
import gzip
import json
import os
import random
import re
import sys

sys.path.insert(0, "olmo_transplant")
from tok import Tok, ids_of  # noqa: E402

A = "artifacts/olmo_transplant"
CUTS = [1024, 2048, 4096, 8192, 16384]
FULL = {"dpo": "T1", "s2300": "T2"}
B_REPS = 10000
DRAFT_CHARS = 40


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def answer(text):
    return norm(text.rsplit("</think>", 1)[-1])


def rcond_of(r):
    return f"B{r['cut']}" if r["cond"] == "B" else (f"F{r['cut']}" if r["cond"] == "F" else r["cond"])


def load_labels():
    """(pid, answer_norm) -> (label, r6flag)."""
    lab = {}
    src = {}
    for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for ln in gzip.open(f"{A}/src/{jb}.jsonl.gz", "rt"):
            r = json.loads(ln)
            src[(jb, r["pid"], r["chunk"], r["i"])] = r["text"]
    for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")):
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if k in src and r["final_label"]:
            lab[(r["pid"], answer(src[k]))] = (r["final_label"], False)
    for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
        job, pid, ch, i = r["key"].split("|")
        if r["final_label"]:
            lab[(pid, answer(src[(job, pid, int(ch), int(i))]))] = (r["final_label"], r.get("r6") == "True")
    if os.path.exists("olmo_transplant/handcheck.csv"):
        for r in csv.DictReader(open("olmo_transplant/handcheck.csv")):
            if r["final_label"]:
                lab[(r["pid"], r["answer_norm"])] = (r["final_label"], r.get("r6") == "True")
    return lab, src


def boot(vals, fn, seed=1):
    """vals: {pid: tuple}; fn(list of tuples) -> float. Returns (point, lo, hi)."""
    keys = sorted(vals)
    if not keys:
        return (None, None, None)
    pt = fn([vals[k] for k in keys])
    rng = random.Random(seed)
    bs = []
    for _ in range(B_REPS):
        s = [vals[keys[rng.randrange(len(keys))]] for _ in keys]
        v = fn(s)
        if v is not None:
            bs.append(v)
    bs.sort()
    if not bs:
        return (pt, None, None)
    return (pt, bs[int(0.025 * len(bs))], bs[min(len(bs) - 1, int(0.975 * len(bs)))])


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="R_dpo,R_s2300,C_dpo,C_s2300,F_s2300")
    ap.add_argument("--out", default="olmo_transplant")
    args = ap.parse_args()
    prompts = {p["pid"]: p for p in csv.DictReader(open("olmo_transplant/prompts.csv"))}
    traces = {t["trace"]: t for t in csv.DictReader(open("olmo_transplant/traces.csv"))}
    lab, src = load_labels()
    tok = Tok()
    # source answers and the draft covariate per (trace, N)
    src_ans, draft_in = {}, {}
    for t in traces.values():
        if t["kind"] != "rl":
            continue
        k = (t["job"], t["pid"], int(t["chunk"]), int(t["i"]))
        if k not in src:
            continue
        text = src[k]
        src_ans[t["trace"]] = answer(text)
    stored = {}
    for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for ln in gzip.open(f"{A}/src/{jb}.jsonl.gz", "rt"):
            r = json.loads(ln)
            stored[(jb, r["pid"], r["chunk"], r["i"])] = r
    for t in traces.values():
        if t["kind"] != "rl":
            continue
        r = stored.get((t["job"], t["pid"], int(t["chunk"]), int(t["i"])))
        if r is None:
            continue
        ids = ids_of(r)
        opening = src_ans[t["trace"]][:DRAFT_CHARS]
        for N in CUTS:
            if int(t["c"]) > N:
                draft_in[(t["trace"], N)] = opening in norm(tok.decode(ids[:N]))
        draft_in[(t["trace"], "P")] = False
    # samples
    rows = []
    for job in args.jobs.split(","):
        gf = f"{A}/graded/{job}.jsonl"
        if not os.path.exists(gf):
            continue
        g = {f"{r['rid']}|{r['i']}": r for r in map(json.loads, open(gf))}
        with gzip.open(f"{A}/samples/{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                gr = g.get(f"{r['rid']}|{r['i']}")
                if gr is None:
                    continue
                a = answer("</think>" + r["text"])
                rows.append({"pid": r["pid"], "writer": r["writer"], "rc": rcond_of(r), "trace": r.get("trace", ""),
                             "strict": gr["strict"], "a": a, "finish": r["finish"], "n_tok": r["n_tok"],
                             "words": gr["answer_words"], "extra_end": gr["extra_think_end"]})
    # labels per sample and shares per (pid, writer, rc)
    grp = collections.defaultdict(list)
    for r in rows:
        L = lab.get((r["pid"], r["a"])) if r["strict"] else None
        r["label"], r["r6"] = (L if L else (None, False))
        r["copy"] = r["trace"] in src_ans and r["a"] == src_ans[r["trace"]]
        grp[(r["pid"], r["writer"], r["rc"])].append(r)
    pooled = collections.defaultdict(lambda: [0, 0, 0])
    for (pid, w, rc), rs in grp.items():
        for r in rs:
            if r["strict"] and r["label"]:
                pooled[(w, rc)][0] += r["label"] == "genuine"
                pooled[(w, rc)][1] += r["label"] == "genuine" and not r["r6"]
                pooled[(w, rc)][2] += 1
    fallback = collections.Counter()

    def shares(pid, w, rc):
        rs = grp.get((pid, w, rc), [])
        lb = [r for r in rs if r["strict"] and r["label"]]
        if lb:
            return (sum(r["label"] == "genuine" for r in lb) / len(lb),
                    sum(r["label"] == "genuine" and not r["r6"] for r in lb) / len(lb))
        p = pooled[(w, rc)]
        if any(r["strict"] for r in rs):
            fallback[(w, rc)] += 1
        return (p[0] / p[2], p[1] / p[2]) if p[2] else (None, None)

    def counts(rs, pid, w, rc):
        """n, strict, genuine (estimate), genuine under rule-6 strict reading, copies among strict."""
        sh, sh6 = shares(pid, w, rc)
        n = len(rs)
        s = sum(r["strict"] for r in rs)
        lg = sum(1 for r in rs if r["strict"] and r["label"] == "genuine")
        lg6 = sum(1 for r in rs if r["strict"] and r["label"] == "genuine" and not r["r6"])
        un = sum(1 for r in rs if r["strict"] and not r["label"])
        g = lg + un * (sh or 0)
        g6 = lg6 + un * (sh6 or 0)
        cp = sum(1 for r in rs if r["strict"] and r["copy"])
        cut = sum(r["finish"] == "length" for r in rs)
        # post hoc: a writer that re-opens thinking after the forced </think> and closes it again counts as a failure
        snr = sum(1 for r in rs if r["strict"] and not r["extra_end"])
        gnr = sum(1 for r in rs if r["strict"] and not r["extra_end"] and r["label"] == "genuine") + \
            sum(1 for r in rs if r["strict"] and not r["extra_end"] and not r["label"]) * (sh or 0)
        res = sum(1 for r in rs if r["extra_end"])
        return [n, s, g, g6, cp, un, cut, snr, gnr, res]

    def add(a, b):
        return [x + y for x, y in zip(a, b)]

    by_trace = collections.defaultdict(list)
    for r in rows:
        by_trace[(r["pid"], r["writer"], r["rc"], r["trace"])].append(r)
    cells = {}  # (pid, cell) -> counts
    for pid, p in prompts.items():
        if p["set"] not in ("reach", "calib"):
            continue
        for w in ("dpo", "s2300"):
            for rc in (FULL[w], "T3" if w == "s2300" else "T4", "T0", "P"):
                rs = [r for r in rows if r["pid"] == pid and r["writer"] == w and r["rc"] == rc]
                if rs:
                    name = {"T1": "T1", "T2": "T2", "T3": "T3", "T4": "T4", "T0": f"T0-{w}", "P": f"P-{w}"}[rc]
                    cells[(pid, name)] = counts(rs, pid, w, rc)
            rl = [t for t in traces.values() if t["pid"] == pid and t["kind"] == "rl"]
            for N in CUTS:
                tot = None
                for t in rl:
                    rc = f"B{N}" if int(t["c"]) > N else FULL[w]
                    rs = by_trace.get((pid, w, rc, t["trace"]), [])
                    if not rs:
                        continue
                    c = counts(rs, pid, w, rc)
                    tot = c if tot is None else add(tot, c)
                if tot:
                    cells[(pid, f"B{N}-{w}")] = tot
        for N in (2048, 4096, 8192):
            rs = [r for r in rows if r["pid"] == pid and r["rc"] == f"F{N}"]
            if rs:
                cells[(pid, f"F{N}")] = counts(rs, pid, "s2300", f"F{N}")
    # results.csv
    with open(f"{args.out}/results.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["set", "pid", "family", "brief20", "cell", "n", "strict", "strict_rate", "genuine_est",
                     "genuine_rate", "genuine_rate_r6strict", "copies_of_source", "unlabelled_strict", "length_cut",
                     "resumed_thinking", "strict_rate_resumed_fail", "genuine_rate_resumed_fail"])
        for (pid, cell), c in sorted(cells.items()):
            p = prompts[pid]
            wr.writerow([p["set"], pid, p["family"], p["brief20"], cell, c[0], c[1], round(c[1] / c[0], 4),
                         round(c[2], 3), round(c[2] / c[0], 4), round(c[3] / c[0], 4), c[4], c[5], c[6], c[9],
                         round(c[7] / c[0], 4), round(c[8] / c[0], 4)])
    # summaries
    names = ["T1", "T2", "T3", "T4", "T0-dpo", "T0-s2300", "P-dpo", "P-s2300"] + \
        [f"B{N}-{w}" for w in ("dpo", "s2300") for N in CUTS] + [f"F{N}" for N in (2048, 4096, 8192)]
    S = {"fallback_shares": {f"{w}:{rc}": v for (w, rc), v in fallback.items()}}
    lines = ["# olmo-transplant summary (analyze.py)", ""]
    for setname, sel in (("reach-41", lambda p: p["set"] == "reach"), ("brief20", lambda p: p["brief20"] == "True"),
                         ("calibration", lambda p: p["set"] == "calib")):
        pids = [pid for pid, p in prompts.items() if sel(p)]
        S[setname] = {}
        lines += [f"## {setname} ({len(pids)} prompts)", "",
                  "| cell | prompts | samples | strict [95 %] | genuine [95 %] | genuine, rule-6 strict | copies / strict | cut "
                  "| re-opened thinking | genuine, re-opened = fail (post hoc) |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for nm in names:
            vals = {pid: cells[(pid, nm)] for pid in pids if (pid, nm) in cells}
            if not vals:
                continue
            st = boot(vals, lambda v: mean([c[1] / c[0] for c in v]))
            ge = boot(vals, lambda v: mean([c[2] / c[0] for c in v]))
            g6 = mean([c[3] / c[0] for c in vals.values()])
            ns = sum(c[0] for c in vals.values())
            ss = sum(c[1] for c in vals.values())
            cp = sum(c[4] for c in vals.values())
            cut = sum(c[6] for c in vals.values())
            gnr = boot(vals, lambda v: mean([c[8] / c[0] for c in v]))
            res = sum(c[9] for c in vals.values())
            S[setname][nm] = {"prompts": len(vals), "samples": ns, "strict": st, "genuine": ge, "genuine_r6strict": g6,
                              "copies": cp, "strict_n": ss, "length_cut": cut, "resumed": res,
                              "genuine_resumed_fail": gnr}
            fmt = lambda t: f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]" if t[1] is not None else f"{t[0]:.3f}"
            lines.append(f"| {nm} | {len(vals)} | {ns} | {fmt(st)} | {fmt(ge)} | {g6:.3f} | {cp} / {ss} | {cut} "
                         f"| {res} | {fmt(gnr)} |")
        lines.append("")
        # paired contrasts and derived quantities (genuine)
        def g(pid, nm):
            c = cells.get((pid, nm))
            return c[2] / c[0] if c else None
        def gs(pid, nm):
            c = cells.get((pid, nm))
            return c[1] / c[0] if c else None
        con = {}
        for lbl, a, b in (("D21 = T2 - T1", "T2", "T1"), ("D34 = T3 - T4", "T3", "T4"),
                          ("D0 = T0-s2300 - T0-dpo", "T0-s2300", "T0-dpo"), ("D30 = T3 - T0-s2300", "T3", "T0-s2300"),
                          ("T1 - T0-dpo", "T1", "T0-dpo")):
            for kind, fn in (("genuine", g), ("strict", gs)):
                vals = {pid: (fn(pid, a), fn(pid, b)) for pid in pids if fn(pid, a) is not None and fn(pid, b) is not None}
                con[f"{lbl} ({kind})"] = boot(vals, lambda v: mean([x - y for x, y in v])) + (len(vals),)
        for kind, fn in (("genuine", g), ("strict", gs)):
            vals = {pid: (fn(pid, "T1"), fn(pid, "T2")) for pid in pids if fn(pid, "T1") is not None and fn(pid, "T2") is not None}
            con[f"R1 = T1 / T2 ({kind})"] = boot(vals, lambda v: (mean([x for x, _ in v]) / mean([y for _, y in v]))
                                                 if mean([y for _, y in v]) else None) + (len(vals),)
            for w in ("dpo", "s2300"):
                full = FULL[w]
                for N in CUTS + ["P"]:
                    nm = f"B{N}-{w}" if N != "P" else f"P-{w}"
                    vals = {pid: (fn(pid, nm), fn(pid, f"T0-{w}"), fn(pid, full)) for pid in pids
                            if None not in (fn(pid, nm), fn(pid, f"T0-{w}"), fn(pid, full))}

                    def fr(v):
                        a, z, f_ = mean([x[0] for x in v]), mean([x[1] for x in v]), mean([x[2] for x in v])
                        return (a - z) / (f_ - z) if f_ - z >= 0.10 else None
                    con[f"F_{w}({N}) retained gain ({kind})"] = boot(vals, fr) + (len(vals),)
        S[setname]["contrasts"] = con
        lines += ["| contrast | value [95 %] | prompts |", "|---|---|---|"]
        for k, v in con.items():
            lines.append(f"| {k} | " + (f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]" if v[1] is not None else
                                         (f"{v[0]:.3f}" if v[0] is not None else "undefined")) + f" | {v[3]} |")
        lines.append("")
    # fresh budget forcing against s2300's natural rate on the same prompts (stored olmo-ifomega draws, strict;
    # genuine = strict x the prompt's olmo_ifomega/handcheck.csv genuine share among read s2300 successes)
    idx = [json.loads(l) for l in open(f"{A}/src/index.jsonl")]
    hc = [r for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")) if r["model"] == "s2300" and r["final_label"]]
    nat = {}
    for pid in {k[0] for k in cells if k[1].startswith("F")}:
        xs = [r["strict"] for r in idx if r["pid"] == pid and r["model"] == "s2300"]
        hl = [r["final_label"] == "genuine" for r in hc if r["pid"] == pid]
        nat[pid] = (sum(xs) / len(xs), sum(xs) / len(xs) * (sum(hl) / len(hl) if hl else 1.0), len(xs))
    S["natural_s2300_on_F_prompts"] = nat
    lines += ["## Fresh budget forcing vs s2300's natural rate (the 6 F prompts)", "",
              "| N | F strict | natural strict | ratio [95 %] | F genuine | natural genuine | ratio [95 %] |",
              "|---|---|---|---|---|---|---|"]
    for N in (2048, 4096, 8192):
        vals = {pid: (cells[(pid, f"F{N}")], nat[pid]) for pid in nat if (pid, f"F{N}") in cells}
        if not vals:
            continue
        rs_ = boot(vals, lambda v: mean([c[1] / c[0] for c, _ in v]) / mean([n[0] for _, n in v]))
        rg_ = boot(vals, lambda v: mean([c[2] / c[0] for c, _ in v]) / mean([n[1] for _, n in v]))
        fs = mean([c[1] / c[0] for c, _ in vals.values()])
        fg = mean([c[2] / c[0] for c, _ in vals.values()])
        ns_ = mean([n[0] for _, n in vals.values()])
        ng_ = mean([n[1] for _, n in vals.values()])
        S.setdefault("F_ratio", {})[N] = {"strict": rs_, "genuine": rg_}
        lines.append(f"| {N} | {fs:.3f} | {ns_:.3f} | {rs_[0]:.2f} [{rs_[1]:.2f}, {rs_[2]:.2f}] | {fg:.3f} | {ng_:.3f} "
                     f"| {rg_[0]:.2f} [{rg_[1]:.2f}, {rg_[2]:.2f}] |")
    lines.append("")
    # draft covariate (reach): cut prefixes (B rows that are actually cut, and P), pooled by writer
    dc = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        if prompts[r["pid"]]["set"] != "reach" or not (r["rc"].startswith("B") or r["rc"] == "P"):
            continue
        N = "P" if r["rc"] == "P" else int(r["rc"][1:])
        d = draft_in.get((r["trace"], N))
        if d is None:
            continue
        k = (r["writer"], d)
        dc[k][0] += 1
        dc[k][1] += r["strict"]
    lines += ["## Draft covariate (reach, cut prefixes; pooled samples, strict)", "",
              "| writer | prefix contains the final answer's opening | samples | strict rate |", "|---|---|---|---|"]
    S["draft"] = {}
    for (w, d), v in sorted(dc.items()):
        lines.append(f"| {w} | {d} | {v[0]} | {v[1] / v[0]:.3f} |")
        S["draft"][f"{w}|{d}"] = [v[0], v[1]]
    lines.append("")
    # family table (reach, genuine)
    fams = sorted({p["family"] for p in prompts.values() if p["set"] == "reach"})
    fc = ["T1", "T2", "T3", "T4", "T0-dpo", "T0-s2300", "B2048-dpo", "B2048-s2300"]
    lines += ["## By family (reach, genuine rate, prompt means)", "", "| family | prompts | " + " | ".join(fc) + " |",
              "|---|---|" + "---|" * len(fc)]
    for fa in fams:
        pids = [pid for pid, p in prompts.items() if p["set"] == "reach" and p["family"] == fa]
        vals = [mean([cells[(pid, nm)][2] / cells[(pid, nm)][0] for pid in pids if (pid, nm) in cells]) for nm in fc]
        lines.append(f"| {fa} | {len(pids)} | " + " | ".join("–" if v is None else f"{v:.2f}" for v in vals) + " |")
    lines += ["", f"Pooled-share fallbacks (a (pid, run-condition) with strict successes but no labelled one): "
              f"{dict(S['fallback_shares'])}", ""]
    ans_len = collections.defaultdict(list)
    for r in rows:
        ans_len[(r["writer"], r["rc"][:1] if r["rc"][0] in "BF" else r["rc"])].append(r["words"])
    lines += ["## Answer length (words, median)", ""] + \
        [f"- {w} {rc}: {sorted(v)[len(v) // 2]} (n {len(v)})" for (w, rc), v in sorted(ans_len.items())]
    open(f"{args.out}/summary.md", "w").write("\n".join(lines) + "\n")
    json.dump(S, open(f"{args.out}/summary.json", "w"), indent=1)
    print("\n".join(lines[:60]))


if __name__ == "__main__":
    main()
