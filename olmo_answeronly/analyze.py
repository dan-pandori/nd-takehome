#!/usr/bin/env python3
"""Analysis of run olmo-answeronly (pre-registration preregistration/olmo-answeronly.md, Analysis and Readings).

Inputs: olmo_transplant/{prompts,traces,results}.csv; this run's artifacts/olmo_answeronly/{graded,samples}/<job>;
olmo-transplant's T1 / T2 samples and grades (artifacts/olmo_answeronly/inputs/tp_<job>, copies of its bucket files);
labels for identity inheritance: olmo_ifomega/handcheck.csv (the traces' own answers), olmo_transplant/handcheck_src.csv,
olmo_transplant/handcheck.csv, olmo_ifladder/handcheck.csv (Leval_main, for L2 / L3) and olmo_answeronly/handcheck.csv.

Cell = (set, pid, writer, cond). Per cell: strict rate; labelled successes = read or identity-inherited (same
whitespace-collapsed answer on the prompt); genuine = labelled genuine + unlabelled strict x the cell's labelled genuine
share (fallback: the pooled share of (set, writer, cond), counted). Re-opened answers (sampled text contains
`</think>`) are also counted as failures (`*_ro`). T1 / T2 genuine rates are olmo-transplant's (results.csv, not
re-estimated); their copy and word counts are recomputed from its samples.
Copies against the trace's own final answer (whitespace-collapsed; review_olmo-transplant's rvt_copy.py definitions):
exact; near = word 3-gram Jaccard >= 0.8 (word sets under 3 words). A4 stop classes: exact (stops where the draft
stops), past (starts with the whole draft and adds text), diverges.
R_c = mean dpo / mean s2300 genuine over S_c = {reach pids with s2300 genuine under c >= 0.75}; broken if s2300 < 0.75
on more than 20 of 41. Bootstrap: 10,000 prompt resamples, seed 1.
Writes olmo_answeronly/results.csv, summary.json, summary.md. Usage: analyze.py [--jobs ...]"""
import argparse
import collections
import csv
import gzip
import json
import os
import random
import re
import statistics

A = "artifacts/olmo_answeronly"
INP = f"{A}/inputs"
B_REPS = 10000
CONDS = ["A1", "A2", "A3", "A4"]
LCONDS = ["L1", "L2", "L3"]
WR = {"dpo": "dpo", "s2300": "s2300", "lora_main": "lora_main"}


def wsnorm(s):
    return re.sub(r"\s+", " ", s).strip()


def answer(text):
    return wsnorm(text.rsplit("</think>", 1)[-1]) if "</think>" in text else wsnorm(text)


def grams(s):
    w = s.split()
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)} if len(w) >= 3 else {(x,) for x in w}


def jac(a, b):
    ga, gb = grams(a), grams(b)
    return len(ga & gb) / len(ga | gb) if ga | gb else 1.0


def iter_gz(path):
    with gzip.open(path, "rt") as f:
        try:
            for ln in f:
                yield json.loads(ln)
        except (EOFError, json.JSONDecodeError):
            return


def load_labels():
    """(pid, answer_norm) -> (label, r6)."""
    lab, src = {}, {}
    for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for r in iter_gz(f"{INP}/{jb}.jsonl.gz"):
            src[(jb, r["pid"], r["chunk"], r["i"])] = r["text"]
    for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")):
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if k in src and r["final_label"]:
            lab[(r["pid"], answer(src[k]))] = (r["final_label"], False)
    for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
        job, pid, ch, i = r["key"].split("|")
        if r["final_label"]:
            lab[(pid, answer(src[(job, pid, int(ch), int(i))]))] = (r["final_label"], r.get("r6") == "True")
    for r in csv.DictReader(open("olmo_transplant/handcheck.csv")):
        if r["final_label"]:
            lab[(r["pid"], r["answer_norm"])] = (r["final_label"], r.get("r6") == "True")
    if os.path.exists(f"{INP}/Leval_main.jsonl.gz"):
        lv = {(r["pid"], r["chunk"], r["i"]): r["final_label"] for r in csv.DictReader(open("olmo_ifladder/handcheck.csv"))
              if r["job"] == "Leval_main" and r["final_label"]}
        for r in iter_gz(f"{INP}/Leval_main.jsonl.gz"):
            k = (r["pid"], str(r["chunk"]), str(r["i"]))
            if k in lv:
                lab[(r["pid"], answer(r["text"]))] = (lv[k], False)
    if os.path.exists("olmo_answeronly/handcheck.csv"):
        for r in csv.DictReader(open("olmo_answeronly/handcheck.csv")):
            if r["final_label"]:
                lab[(r["pid"], r["answer_norm"])] = (r["final_label"], r.get("r6") == "True")
    return lab, src


def boot(vals, fn, seed=1):
    keys = sorted(vals)
    if not keys:
        return (None, None, None)
    pt = fn([vals[k] for k in keys])
    rng = random.Random(seed)
    bs = []
    for _ in range(B_REPS):
        v = fn([vals[keys[rng.randrange(len(keys))]] for _ in keys])
        if v is not None:
            bs.append(v)
    bs.sort()
    return (pt, bs[int(0.025 * len(bs))], bs[min(len(bs) - 1, int(0.975 * len(bs)))]) if bs else (pt, None, None)


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def ratio(xs):
    d = sum(b for _, b in xs)
    return sum(a for a, _ in xs) / d if d else None


def r3(x):
    return None if x is None else round(x, 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="R_dpo,R_s2300,C_dpo,C_s2300")
    ap.add_argument("--out", default="olmo_answeronly")
    args = ap.parse_args()
    prompts = {p["pid"]: p for p in csv.DictReader(open("olmo_transplant/prompts.csv"))}
    traces = {t["trace"]: t for t in csv.DictReader(open("olmo_transplant/traces.csv"))}
    lab, src = load_labels()
    src_ans = {}
    for t in traces.values():
        k = (t["job"], t["pid"], int(t["chunk"]), int(t["i"]))
        if k in src:
            src_ans[t["trace"]] = wsnorm(src[k].split("</think>", 1)[1])
    lv_ans = {}  # L2 / L3 traces: lora_main's own answer
    if os.path.exists(f"{A}/requests/dpo_lrev.jsonl.gz"):
        want = {r["trace"]: r["src"] for r in iter_gz(f"{A}/requests/dpo_lrev.jsonl.gz")}
        bysrc = {v: k for k, v in want.items()}
        for r in iter_gz(f"{INP}/Leval_main.jsonl.gz"):
            s = f"Leval_main|{r['pid']}|{r['chunk']}|{r['i']}"
            if s in bysrc:
                lv_ans[bysrc[s]] = wsnorm(r["text"].split("</think>", 1)[1])
    src_ans.update(lv_ans)

    rows = []
    jobs = [(j, f"{A}/samples/{j}.jsonl.gz", f"{A}/graded/{j}.jsonl", None) for j in args.jobs.split(",")]
    jobs += [(f"tp_{j}", f"{INP}/tp_{j}.jsonl.gz", f"{INP}/tp_{j}_graded.jsonl", {"T1", "T2"})
             for j in ("R_dpo", "R_s2300", "C_dpo", "C_s2300")]
    for job, sf, gf, keep in jobs:
        if not os.path.exists(gf):
            print("missing", gf)
            continue
        g = {}
        for ln in open(gf):
            x = json.loads(ln)
            g[f"{x['rid']}|{x['i']}"] = x
        for r in iter_gz(sf):
            if keep and r["cond"] not in keep:
                continue
            gr = g.get(f"{r['rid']}|{r['i']}")
            if gr is None:
                continue
            a = answer("</think>" + r["text"])
            sa = src_ans.get(r["trace"])
            x = None if sa is None else (1.0 if a == sa else min(0.999, jac(a, sa)))
            stop = None
            if r["cond"] == "A4" and sa is not None:
                stop = "exact" if a == sa else ("past" if a.startswith(sa) else "diverges")
            rows.append({"pid": r["pid"], "set": prompts[r["pid"]]["set"], "writer": r["writer"], "cond": r["cond"],
                         "trace": r["trace"], "strict": bool(gr["strict"]), "a": a, "finish": r["finish"],
                         "n_tok": r["n_tok"], "words": gr["answer_words"], "ro": bool(gr["extra_think_end"]),
                         "jac": x, "stop": stop, "job": job})
    for r in rows:
        L = lab.get((r["pid"], r["a"])) if r["strict"] else None
        r["label"], r["r6"] = L if L else (None, False)
    grp = collections.defaultdict(list)
    for r in rows:
        grp[(r["set"], r["pid"], r["writer"], r["cond"])].append(r)
    pooled = collections.defaultdict(lambda: [0, 0, 0])
    for (st, pid, w, c), rs in grp.items():
        for r in rs:
            if r["strict"] and r["label"]:
                pooled[(st, w, c)][0] += r["label"] == "genuine"
                pooled[(st, w, c)][1] += r["label"] == "genuine" and not r["r6"]
                pooled[(st, w, c)][2] += 1
    fallback = collections.Counter()
    tp_res = {(r["set"], r["pid"], r["cell"]): r for r in csv.DictReader(open("olmo_transplant/results.csv"))}

    out = []
    for (st, pid, w, c), rs in sorted(grp.items()):
        lb = [r for r in rs if r["strict"] and r["label"]]
        un = [r for r in rs if r["strict"] and not r["label"]]
        if lb:
            sh = sum(r["label"] == "genuine" for r in lb) / len(lb)
            sh6 = sum(r["label"] == "genuine" and not r["r6"] for r in lb) / len(lb)
        else:
            p = pooled[(st, w, c)]
            sh, sh6 = (p[0] / p[2], p[1] / p[2]) if p[2] else (None, None)
            if un:
                fallback[(st, w, c)] += 1
        n = len(rs)
        s = sum(r["strict"] for r in rs)

        def gen(sel, share, r6s=False):
            return (sum(1 for r in sel if r["strict"] and r["label"] == "genuine" and not (r6s and r["r6"]))
                    + sum(1 for r in sel if r["strict"] and not r["label"]) * (share or 0))
        g = gen(rs, sh)
        g6 = gen(rs, sh6, True)
        nro = [r for r in rs if not r["ro"]]
        s_ro = sum(r["strict"] for r in nro)
        g_ro = gen(nro, sh)
        js = [r["jac"] for r in rs if r["jac"] is not None]
        row = {"set": st, "pid": pid, "family": prompts[pid]["family"], "writer": w, "cond": c, "n": n, "strict": s,
               "strict_rate": r3(s / n), "genuine_est": r3(g), "genuine_rate": r3(g / n),
               "genuine_rate_r6strict": r3(g6 / n), "labelled": len(lb), "unlabelled_strict": len(un),
               "strict_rate_ro_fail": r3(s_ro / n), "genuine_rate_ro_fail": r3(g_ro / n),
               "reopened": sum(r["ro"] for r in rs), "length_cut": sum(r["finish"] == "length" for r in rs),
               "exact": sum(x == 1.0 for x in js), "near": sum(0.8 <= x < 1.0 for x in js),
               "exact_strict": sum(1 for r in rs if r["strict"] and r["jac"] == 1.0),
               "near_strict": sum(1 for r in rs if r["strict"] and r["jac"] is not None and 0.8 <= r["jac"] < 1.0),
               "median_words": statistics.median([r["words"] for r in rs]),
               "gen_tokens": sum(r["n_tok"] for r in rs),
               "a4_exact": sum(r["stop"] == "exact" for r in rs), "a4_past": sum(r["stop"] == "past" for r in rs),
               "a4_diverges": sum(r["stop"] == "diverges" for r in rs)}
        if c in ("T1", "T2"):  # olmo-transplant's estimates, not re-estimated here
            tp = tp_res[(st, pid, c)]
            row["genuine_rate"] = float(tp["genuine_rate"]) if tp["genuine_rate"] != "" else None
            row["genuine_rate_r6strict"] = float(tp["genuine_rate_r6strict"]) if tp["genuine_rate_r6strict"] != "" else None
            row["genuine_rate_ro_fail"] = (float(tp["genuine_rate_resumed_fail"])
                                           if tp["genuine_rate_resumed_fail"] != "" else None)
            row["genuine_est"] = None
            row["source"] = "olmo_transplant/results.csv"
        else:
            row["source"] = "this run"
        out.append(row)
    with open(f"{args.out}/results.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        wr.writeheader()
        wr.writerows(out)

    cell = {(r["set"], r["pid"], r["writer"], r["cond"]): r for r in out}
    S = {"fallback_shares": {"|".join(k): v for k, v in fallback.items()}, "conditions": {}, "R": {}, "paired": {},
         "family": {}, "calib_choice": None, "readings": {}}
    reach = sorted(p for p in prompts if prompts[p]["set"] == "reach")
    calib = sorted(p for p in prompts if prompts[p]["set"] == "calib")
    base = {"dpo": "T1", "s2300": "T2", "lora_main": "T2"}
    allc = ["T1", "T2"] + CONDS + LCONDS

    def rate_of(st, pid, w, c, key):
        r = cell.get((st, pid, w, c))
        return None if r is None else r[key]

    for st, pids in (("reach", reach), ("calib", calib)):
        for w in ("dpo", "s2300", "lora_main"):
            for c in allc:
                rs = [cell[(st, p, w, c)] for p in pids if (st, p, w, c) in cell]
                if not rs:
                    continue
                d = {"n_prompts": len(rs), "samples": sum(r["n"] for r in rs)}
                for key in ("strict_rate", "genuine_rate", "genuine_rate_r6strict", "strict_rate_ro_fail",
                            "genuine_rate_ro_fail"):
                    vals = {r["pid"]: (r[key],) for r in rs if r[key] is not None}
                    d[key] = [r3(v) for v in boot(vals, lambda xs: mean([x[0] for x in xs]))]
                n = sum(r["n"] for r in rs)
                s = sum(r["strict"] for r in rs)
                d.update({"reopened_share": r3(sum(r["reopened"] for r in rs) / n),
                          "length_cut_share": r3(sum(r["length_cut"] for r in rs) / n),
                          "max_cell_length_cut_share": r3(max(r["length_cut"] / r["n"] for r in rs)),
                          "exact_share": r3(sum(r["exact"] for r in rs) / n),
                          "near_share": r3(sum(r["near"] for r in rs) / n),
                          "exact_near_of_strict": r3((sum(r["exact_strict"] + r["near_strict"] for r in rs) / s) if s else None),
                          "median_words_of_cell_medians": statistics.median([r["median_words"] for r in rs]),
                          "gen_tokens": sum(r["gen_tokens"] for r in rs),
                          "s2300_below_075": None})
                if c == "A4":
                    d["a4_stop"] = {k: r3(sum(r[f"a4_{k}"] for r in rs) / n) for k in ("exact", "past", "diverges")}
                S["conditions"][f"{st}|{w}|{c}"] = d

    # R per condition (reach), the broken rule, paired differences, families
    for c in ["T"] + CONDS + LCONDS:
        cd, cs = ("T1", "T2") if c == "T" else (c, c)
        wd, ws = "dpo", "s2300"
        if c == "L1":
            wd, cs = "lora_main", "T2"
        elif c == "L2":
            cs, ws = "L3", "lora_main"
        elif c == "L3":
            continue
        sv = {p: rate_of("reach", p, ws, cs, "genuine_rate") for p in reach}
        dv = {p: rate_of("reach", p, wd, cd, "genuine_rate") for p in reach}
        if all(v is None for v in dv.values()) or all(v is None for v in sv.values()):
            continue
        pairs = [p for p in reach if sv[p] is not None and dv[p] is not None]
        below = sum(sv[p] < 0.75 for p in pairs)
        Sc = [p for p in pairs if sv[p] >= 0.75]
        R = boot({p: (dv[p], sv[p]) for p in Sc}, ratio)
        S["R"][c] = {"writer_num": f"{wd}:{cd}", "writer_den": f"{ws}:{cs}", "n_prompts": len(pairs),
                     "s2300_below_075": below, "broken": below > len(pairs) / 2 if c != "T" else False,
                     "S_c": len(Sc), "R": [r3(v) for v in R],
                     "num_mean_Sc": r3(mean([dv[p] for p in Sc])), "den_mean_Sc": r3(mean([sv[p] for p in Sc]))}
        # the same on strict, and with re-opened answers as failures
        for key in ("strict_rate", "genuine_rate_ro_fail"):
            sv2 = {p: rate_of("reach", p, ws, cs, key) for p in reach}
            dv2 = {p: rate_of("reach", p, wd, cd, key) for p in reach}
            pp = [p for p in reach if sv2[p] is not None and dv2[p] is not None]
            Sc2 = [p for p in pp if sv2[p] >= 0.75]
            S["R"][c][f"R_{key}"] = [r3(v) for v in boot({p: (dv2[p], sv2[p]) for p in Sc2}, ratio)] + [len(Sc2)]
        if c in CONDS:
            for w, b in (("dpo", "T1"), ("s2300", "T2")):
                vals = {p: (rate_of("reach", p, w, c, "genuine_rate"), rate_of("reach", p, w, b, "genuine_rate"))
                        for p in reach}
                vals = {p: v for p, v in vals.items() if None not in v}
                S["paired"][f"{w}:{c}-{b}"] = [r3(v) for v in boot(vals, lambda xs: mean([a - b_ for a, b_ in xs]))] + \
                    [r3(statistics.pstdev([a - b_ for a, b_ in vals.values()]))]
            fam = collections.defaultdict(list)
            for p in reach:
                fam[prompts[p]["family"]].append(p)
            S["family"][c] = {f: {"n": len(ps),
                                  "dpo": r3(mean([rate_of("reach", p, "dpo", c, "genuine_rate") for p in ps])),
                                  "s2300": r3(mean([rate_of("reach", p, "s2300", c, "genuine_rate") for p in ps])),
                                  "dpo_T1": r3(mean([rate_of("reach", p, "dpo", "T1", "genuine_rate") for p in ps]))}
                              for f, ps in sorted(fam.items())}

    # choice of the best of A1-A3 on calibration (strict; ties <= 0.03 by exact + near copy share; then A1, A3, A2)
    cand = []
    for c in ("A1", "A3", "A2"):
        dk, sk = f"calib|dpo|{c}", f"calib|s2300|{c}"
        if dk not in S["conditions"] or sk not in S["conditions"]:
            continue
        sbelow = sum(1 for p in calib if (rate_of("calib", p, "s2300", c, "strict_rate") or 0) < 0.75)
        rs = [cell[("calib", p, "dpo", c)] for p in calib if ("calib", p, "dpo", c) in cell]
        n = sum(r["n"] for r in rs)
        cand.append({"cond": c, "dpo_strict": S["conditions"][dk]["strict_rate"][0],
                     "copy_share": sum(r["exact"] + r["near"] for r in rs) / n if n else 0,
                     "s2300_below_075": sbelow, "broken": sbelow > len(calib) / 2})
    ok = [x for x in cand if not x["broken"]]
    choice = None
    if ok:
        top = max(x["dpo_strict"] for x in ok)
        t = [x for x in ok if x["dpo_strict"] >= top - 0.03]
        if len(t) > 1:
            tc = max(x["copy_share"] for x in t)
            t = [x for x in t if x["copy_share"] >= tc - 0.03]
        choice = t[0]["cond"]  # cand is in the order A1, A3, A2
    S["calib_choice"] = {"candidates": cand, "chosen": choice}

    def reading(Rv):
        if Rv is None:
            return None
        return "habit" if Rv >= 0.75 else "skill" if Rv <= 0.40 else "between"
    if choice and choice in S["R"]:
        rc = S["R"][choice]
        S["readings"]["chosen"] = {"cond": choice, "R": rc["R"], "broken": rc["broken"],
                                   "reading": None if rc["broken"] else reading(rc["R"][0])}
    for c in CONDS:
        if c in S["R"]:
            S["readings"][c] = None if S["R"][c]["broken"] else reading(S["R"][c]["R"][0])
    if all(c in S["R"] for c in CONDS):
        a13 = [S["R"][c]["R"][0] for c in ("A1", "A2", "A3") if not S["R"][c]["broken"]]
        S["readings"]["first_tokens"] = bool(S["R"]["A4"]["R"][0] >= 0.75 and a13 and max(a13) <= 0.40)
    json.dump(S, open(f"{args.out}/summary.json", "w"), indent=1)

    L = ["# olmo-answeronly summary (generated by olmo_answeronly/analyze.py)", ""]
    L.append("| set | writer | cond | prompts | samples | strict [95 %] | genuine [95 %] | genuine, re-opened = fail | "
             "re-opened | cut | exact | near | exact+near of strict | median words | A4 stop exact / past / diverges |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    def f3(v):
        return "–" if v[0] is None else f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]" if v[1] is not None else f"{v[0]:.3f}"
    for k, d in S["conditions"].items():
        st, w, c = k.split("|")
        a4 = d.get("a4_stop")
        L.append(f"| {st} | {w} | {c} | {d['n_prompts']} | {d['samples']} | {f3(d['strict_rate'])} | "
                 f"{f3(d['genuine_rate'])} | {f3(d['genuine_rate_ro_fail'])} | {d['reopened_share']} | "
                 f"{d['length_cut_share']} | {d['exact_share']} | {d['near_share']} | {d['exact_near_of_strict']} | "
                 f"{d['median_words_of_cell_medians']} | "
                 f"{'' if not a4 else ' / '.join(str(a4[x]) for x in ('exact', 'past', 'diverges'))} |")
    L += ["", "| R | numerator | denominator | prompts | s2300 < 0.75 | broken | S_c | R [95 %] | means on S_c | R strict | R re-opened = fail |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c, d in S["R"].items():
        L.append(f"| {c} | {d['writer_num']} | {d['writer_den']} | {d['n_prompts']} | {d['s2300_below_075']} | "
                 f"{d['broken']} | {d['S_c']} | {f3(d['R'])} | {d['num_mean_Sc']} / {d['den_mean_Sc']} | "
                 f"{f3(d['R_strict_rate'][:3])} (S {d['R_strict_rate'][3]}) | "
                 f"{f3(d['R_genuine_rate_ro_fail'][:3])} (S {d['R_genuine_rate_ro_fail'][3]}) |")
    L += ["", "Paired differences by prompt (genuine; mean [95 %], SD): " +
          "; ".join(f"{k} {f3(v[:3])} (SD {v[3]})" for k, v in S["paired"].items()), "",
          f"Calibration choice: {json.dumps(S['calib_choice'])}", "", f"Readings: {json.dumps(S['readings'])}", "",
          f"Pooled-share fallbacks: {S['fallback_shares']}", ""]
    for c, fd in S["family"].items():
        L.append(f"Family {c}: " + "; ".join(f"{f} (n {v['n']}) dpo {v['dpo']} s2300 {v['s2300']} T1 {v['dpo_T1']}"
                                              for f, v in fd.items()))
    open(f"{args.out}/summary.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
