"""Does the writer keep thinking after the forced `</think>`? (run olmo-transplant; reviewer's check)

A sampled answer that itself contains `</think>` means the writer wrote more reasoning after the supplied closing and
then closed again; the grader takes the text after the LAST `</think>`. Per (writer, cell) on reach: share of such
samples, the extra reasoning's length (tokens through the token that completes the sampled `</think>`), strict
success among them, and the strict B curve / P / T0 with those samples counted as failures ("budget held").
Output: out/mech.txt, out/mech.json
"""
import collections
import csv
import gzip
import json
import statistics

from rvt_core import ART, OUT, RAW, Pieces, Tee, iter_gz, unb64

P = Tee("mech.txt")
pc = Pieces()
prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
REACH = [p["pid"] for p in prompts if p["set"] == "reach"]
tr = {r["trace"]: r for r in csv.DictReader(open(OUT / "traces_mine.csv"))}
CUTS = [1024, 2048, 4096, 8192, 16384]
res = {}
rows = []
for job in ("R_dpo", "R_s2300", "F_s2300"):
    g = {}
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            x = json.loads(ln)
            g[x["key"]] = x["strict"]
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        k = f"{job}|{r['rid']}|{r['i']}"
        ids = unb64(r["ids"])
        kk = pc.first_close(ids)
        cell = r["cond"] + (str(r["cut"]) if r["cond"] in ("B", "F") else "")
        rows.append({"job": job, "writer": r["writer"], "pid": r["pid"], "cell": cell, "trace": r.get("trace", ""),
                     "strict": g[k], "extra": kk, "n_tok": len(ids)})

P("== samples whose answer contains a second `</think>` (reach + F), by writer and cell")
grp = collections.defaultdict(list)
for r in rows:
    grp[(r["job"], r["cell"])].append(r)
for (job, cell), rs in sorted(grp.items()):
    ex = [r for r in rs if r["extra"] is not None]
    if not ex:
        P(f"   {job:8s} {cell:7s} n {len(rs):5d}: none")
        continue
    lens = sorted(r["extra"] for r in ex)
    s_ex = sum(r["strict"] for r in ex)
    s_all = sum(r["strict"] for r in rs)
    P(f"   {job:8s} {cell:7s} n {len(rs):5d}: {len(ex):4d} ({100 * len(ex) / len(rs):5.1f} %) re-think; extra tokens "
      f"median {statistics.median(lens):.0f}, q90 {lens[int(0.9 * (len(lens) - 1))]}, max {lens[-1]}; strict among them "
      f"{s_ex} / {len(ex)} = {s_ex / len(ex):.2f}; share of the cell's strict successes {s_ex}/{s_all}")
    res[f"{job}|{cell}"] = {"n": len(rs), "rethink": len(ex), "median_extra": statistics.median(lens),
                            "strict_rethink": s_ex, "strict_all": s_all}

# strict B curve for s2300 with re-think samples counted as failures ("budget held"), primary curve
by_tc = collections.defaultdict(list)
for r in rows:
    if r["trace"]:
        by_tc[(r["job"], r["trace"], r["cell"])].append(r)
by_pc = collections.defaultdict(list)
for r in rows:
    by_pc[(r["job"], r["pid"], r["cell"])].append(r)


def rate(rs, held):
    return sum(r["strict"] and not (held and r["extra"] is not None) for r in rs) / len(rs)


for job, full in (("R_s2300", "T2"), ("R_dpo", "T1")):
    for held in (False, True):
        out = []
        G0 = statistics.mean(rate(by_pc[(job, p, "T0")], held) for p in REACH)
        Gf = statistics.mean(rate(by_pc[(job, p, full)], held) for p in REACH)
        for N in CUTS:
            pp = []
            for p in REACH:
                rs = []
                for t, m in tr.items():
                    if m["pid"] != p or m["kind"] != "rl" or m["set"] != "reach":
                        continue
                    rs += by_tc[(job, t, f"B{N}")] if int(m["c"]) > N else by_tc[(job, t, full)]
                pp.append(rate(rs, held))
            G = statistics.mean(pp)
            out.append(f"G({N}) {G:.3f} F {(G - G0) / (Gf - G0):.3f}")
            res[f"Bheld|{job}|{held}|{N}"] = G
        pp = [rate(by_pc[(job, p, "P")], held) for p in REACH if by_pc[(job, p, "P")]]
        GP = statistics.mean(pp)
        P(f"   {job} strict primary B curve {'re-think = failure' if held else 'as graded      '}: G(0) {G0:.3f}; "
          + "; ".join(out) + f"; G(full) {Gf:.3f}; G(P) {GP:.3f} F(P) {(GP - G0) / (Gf - G0):.3f}")
        res[f"Bheld|{job}|{held}|T0"] = G0
        res[f"Bheld|{job}|{held}|P"] = GP
json.dump(res, open(OUT / "mech.json", "w"), indent=1)

# fresh budget forcing with re-think samples counted as failures
REQ6 = [p["pid"] for p in prompts if p["required6"] == "True"]
for held in (False, True):
    parts = []
    for N in (2048, 4096, 8192):
        pp = [rate(by_pc[("F_s2300", p, f"F{N}")], held) for p in REQ6]
        parts.append(f"F({N}) {statistics.mean(pp):.3f}")
        res[f"Fheld|{held}|{N}"] = statistics.mean(pp)
    P(f"   fresh F(N), strict, {'re-think = failure' if held else 'as graded'}: " + "; ".join(parts))
json.dump(res, open(OUT / "mech.json", "w"), indent=1)
