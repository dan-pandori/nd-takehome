"""Phase-2 checks of specific executor claims (run olmo-transplant; reviewer's code; my definitions stated inline).
Output: out/phase2_checks.txt"""
import collections
import csv
import gzip
import json
import statistics

from rvt_core import ART, OUT, RAW, SCR, Tee, answer_of, iter_gz, wsnorm

P = Tee("phase2_checks.txt")
tr = {r["trace"]: r for r in csv.DictReader(open(OUT / "traces_mine.csv"))}
need = {(m["job"], m["pid"], int(m["chunk"]), int(m["i"])): t for t, m in tr.items() if m["kind"] == "rl" and m["set"] == "reach"}
src = {}
for job in sorted({k[0] for k in need}):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (job, r["pid"], r["chunk"], r["i"])
        if k in need:
            src[need[k]] = wsnorm(r["text"].split("</think>", 1)[1])
# 1. T1 / T2: answers containing RL's final answer verbatim (whitespace-collapsed substring), how many fail strict;
#    answers > 1.5x RL's words; median words
for job, cell in (("R_dpo", "T1"), ("R_s2300", "T2")):
    g = {}
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            x = json.loads(ln)
            g[x["key"]] = x
    n = exact = cont = cont_fail = longer = 0
    words = []
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        if r["cond"] != cell:
            continue
        a = wsnorm(answer_of("</think>" + r["text"]))
        s = src[r["trace"]]
        st = g[f"{job}|{r['rid']}|{r['i']}"]["strict"]
        n += 1
        exact += a == s
        if s and s in a:
            cont += 1
            cont_fail += not st
        longer += len(a.split()) > 1.5 * len(s.split())
        words.append(len(a.split()))
    P(f"[1] {job} {cell}: answers {n}; exact copies {exact}; contain RL's answer {cont}, of which strict failures "
      f"{cont_fail}; > 1.5x RL's words {longer}; median words {statistics.median(words)}")
# 2. prompts with T1 genuine = 0 (executor's labels and mine)
for mode in ("exec", "mine", "strict"):
    rows = list(csv.DictReader(open(OUT / f"per_prompt_{mode}.csv")))
    field = "strict" if mode == "strict" else "g"
    z = [r["pid"] for r in rows if r["set"] == "reach" and r["field"] == field and float(r["T1"]) == 0]
    P(f"[2] {mode}: reach prompts with T1 = 0: {len(z)} / 41")
# 3. draft split as the executor defines it (cut prefixes = every B cut and every P cut), strict, pooled samples
R = json.load(open(OUT / "rates_strict.json"))
for w in ("dpo", "s2300"):
    a1, n1, a0, n0 = R[f"draftsplit|strict|{w}"][:4]
    job = f"R_{w}"
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        g = {x["key"]: x["strict"] for x in map(json.loads, f)}
    p_rows = [g[f"{job}|{r['rid']}|{r['i']}"] for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz") if r["cond"] == "P"]
    s0 = a0 * n0 * 8 + sum(p_rows)
    P(f"[3] {w}: with the opening {a1:.3f} (n {n1 * 8} samples); without, B cuts only {a0:.3f} (n {n0 * 8}); "
      f"without incl. P {s0 / (n0 * 8 + len(p_rows)):.3f} (n {n0 * 8 + len(p_rows)})")
# 4. cut shares per condition as sampled vs over the primary-curve cell (B rows + substituted full rows)
for job in ("R_dpo", "C_s2300"):
    c = R[f"cut|{job}"]
    full = "T1" if "dpo" in job else "T2"
    for N in (4096, 8192):
        cell = f"B{N}"
        if cell in c:
            n_tr = sum(1 for t, m in tr.items() if m["kind"] == "rl" and m["set"] == ("calib" if job[0] == "C" else "reach"))
            P(f"[4] {job} {cell}: cut {c[cell][1]} of {c[cell][0]} sampled ({100 * c[cell][1] / c[cell][0]:.2f} %); "
              f"over the primary-curve cell ({n_tr * 8} rows) {100 * c[cell][1] / (n_tr * 8):.2f} % "
              f"(+ substituted full rows' cuts: {c[full][1]})")
# 5. fresh-forcing ratios with a natural genuine baseline of 0.686 (back-solved from the executor's 0.27 / 0.62 / 0.88)
for mode in ("exec", "mine", "exec_vac", "mine_vac"):
    X = json.load(open(OUT / f"rates_{mode}.json"))
    v = [X[f"fresh|g|{N}"][0] for N in (2048, 4096, 8192)]
    P(f"[5] {mode}: fresh F genuine 2k / 4k / 8k = {v[0]:.3f} / {v[1]:.3f} / {v[2]:.3f}; / 0.686 = "
      f"{v[0] / 0.686:.2f} / {v[1] / 0.686:.2f} / {v[2] / 0.686:.2f}")
# 6. F_s2300(P) with re-thought answers as failures, from the executor's own genuine table values
G0, GP, Gf = 0.071, 0.283, 0.924
P(f"[6] executor's 're-opened = fail' genuine values: G(0) {G0}, G(P) {GP}, G(full) {Gf} -> F(P) = "
  f"{(GP - G0) / (Gf - G0):.3f}")
# 7. s2300's natural genuine rate on the 6 required prompts, my computation: per prompt, strict rate over every stored
#    olmo-ifomega s2300 draw (F, C1, C2; my re-grade) x the genuine share among olmo-ifomega's labelled s2300 successes
prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
REQ6 = [p["pid"] for p in prompts if p["required6"] == "True"]
st = collections.defaultdict(lambda: [0, 0])
for job in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            x = json.loads(ln)
            if x["pid"] in REQ6:
                st[x["pid"]][0] += x["strict"]
                st[x["pid"]][1] += 1
lab = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(RAW / "olmo_ifomega" / "handcheck.csv")):
    if r["model"] == "s2300" and r["pid"] in REQ6 and r["final_label"] in ("genuine", "gamed"):
        lab[r["pid"]][0] += 1
        lab[r["pid"]][1] += r["final_label"] == "genuine"
nat = {p: st[p][0] / st[p][1] * (lab[p][1] / lab[p][0] if lab[p][0] else float("nan")) for p in REQ6}
m = statistics.mean(nat.values())
P(f"[7] natural genuine on the 6: per prompt " + ", ".join(f"{p.split('_')[1]} {st[p][0]}/{st[p][1]} x {lab[p][1]}/{lab[p][0]}"
                                                       for p in REQ6) + f"; mean {m:.3f}")
for mode in ("exec", "mine", "exec_vac", "mine_vac"):
    X = json.load(open(OUT / f"rates_{mode}.json"))
    v = [X[f"fresh|g|{N}"][0] for N in (2048, 4096, 8192)]
    P(f"    {mode}: ratio of means {v[0] / m:.2f} / {v[1] / m:.2f} / {v[2] / m:.2f}")
# 8. results.csv (executor) vs my per-prompt tables: strict_rate vs my strict, genuine_rate vs my executor-label genuine
mine_s = {(r["pid"], c): float(r[c]) for r in csv.DictReader(open(OUT / "per_prompt_strict.csv"))
          if r["field"] == "strict" for c in r if c not in ("pid", "set", "family", "field") and r[c] != ""}
mine_g = {(r["pid"], c): float(r[c]) for r in csv.DictReader(open(OUT / "per_prompt_exec.csv"))
          if r["field"] == "g" for c in r if c not in ("pid", "set", "family", "field") and r[c] not in ("", "nan")}
dif_s, dif_g, nchk_s, nchk_g = [], [], 0, 0
for r in csv.DictReader(open(RAW.parent.parent / "work" / "olmo-transplant" / "olmo_transplant" / "results.csv")):
    k = (r["pid"], r["cell"])
    if k in mine_s:
        nchk_s += 1
        if abs(float(r["strict_rate"]) - mine_s[k]) > 6e-5:
            dif_s.append((k, r["strict_rate"], mine_s[k]))
    if k in mine_g and r["genuine_rate"] not in ("", "nan"):
        nchk_g += 1
        if abs(float(r["genuine_rate"]) - mine_g[k]) > 6e-5:
            dif_g.append((k, r["genuine_rate"], round(mine_g[k], 4)))
P(f"[8] results.csv vs mine: strict rates compared {nchk_s}, differ {len(dif_s)} {dif_s[:5]}; genuine (executor's "
  f"labels) compared {nchk_g}, differ {len(dif_g)} {dif_g[:8]}")
# 9. the 183 T1 answers that contain RL's answer and fail strict: do they all ADD words?
g = {}
with gzip.open(OUT / "regrade" / "R_dpo.jsonl.gz", "rt") as f:
    for ln in f:
        x = json.loads(ln)
        g[x["key"]] = x
more = same = 0
for r in iter_gz(ART / "samples" / "R_dpo.jsonl.gz"):
    if r["cond"] != "T1":
        continue
    a = wsnorm(answer_of("</think>" + r["text"]))
    s = src[r["trace"]]
    if s and s in a and not g[f"R_dpo|{r['rid']}|{r['i']}"]["strict"]:
        if len(a.split()) > len(s.split()):
            more += 1
        else:
            same += 1
P(f"[9] T1 answers containing RL's answer and failing strict: {more + same}; with more words than RL's answer {more}; "
  f"same word count (fail on layout only) {same}")
# 10. F(P) on the executor's definition: G(0), G(P) and G(full) all over the prompts that have a P cell
def pp_table(mode, st):
    field = "strict" if mode == "strict" else "g"
    return {r["pid"]: r for r in csv.DictReader(open(OUT / f"per_prompt_{mode}.csv")) if r["field"] == field and
            r["set"] == st}
b20 = {p["pid"] for p in prompts if p["brief20"] == "True"}
for mode in ("strict", "exec", "mine", "exec_held", "mine_held"):
    T = pp_table(mode, "reach")
    out = []
    for setname, keep in (("reach", None), ("brief20", b20)):
        for w, full in (("dpo", "T1"), ("s2300", "T2")):
            ps = [p for p, r in T.items() if r[f"P-{w}"] != "" and (keep is None or p in keep)]
            G = {c: statistics.mean(float(T[p][c]) for p in ps) for c in (f"P-{w}", f"T0-{w}", full)}
            F = (G[f"P-{w}"] - G[f"T0-{w}"]) / (G[full] - G[f"T0-{w}"])
            out.append(f"{setname} {w} F(P) {F:.3f} (n {len(ps)})")
    P(f"[10] {mode}: " + "; ".join(out))
# 11. results.csv fresh-forcing rows vs my per-prompt fresh values; calibration genuine_rate values in strict-only cells
fr = {(r["pid"], f): r for f in ("strict", "g") for r in csv.DictReader(open(OUT / "per_prompt_fresh_exec.csv")) if r["field"] == f}
d = []
cal_art = 0
for r in csv.DictReader(open(RAW.parent.parent / "work" / "olmo-transplant" / "olmo_transplant" / "results.csv")):
    if r["cell"].startswith("F"):
        for col, f in (("strict_rate", "strict"), ("genuine_rate", "g")):
            if abs(float(r[col]) - float(fr[(r["pid"], f)][r["cell"]])) > 6e-5:
                d.append((r["pid"], r["cell"], col, r[col], fr[(r["pid"], f)][r["cell"]]))
    if r["set"] == "calib" and (r["cell"].startswith("B") or r["cell"].startswith("P")) and r["genuine_rate"] not in ("", "nan"):
        if int(r["strict"]) > 0:
            cal_art += 1
P(f"[11] results.csv F rows: 18 x (strict, genuine) compared, differ {len(d)} {d[:4]}; calibration B / P rows (strict "
  f"only by design) that still carry a numeric genuine_rate with strict > 0: {cal_art}")
# 12. how many of the 115 reach rl trace labels did the olmo-ifomega review re-read (by sample key)?
keys = set()
for f in sorted((RAW / "review" / "olmo-ifomega-recount" / "hand").glob("key_r*.json")):
    for v in json.load(open(f)).values():
        if v.get("job"):
            keys.add(f"{v['job']}|{v['pid']}|{v['chunk']}|{v['i']}")
rl = [t for t in csv.DictReader(open(RAW / "olmo_transplant" / "traces.csv")) if t["set"] == "reach" and t["kind"] == "rl"]
n_cov = sum("|".join((t["job"], t["pid"], t["chunk"], t["i"])) in keys for t in rl)
P(f"[12] reach rl traces whose source sample the olmo-ifomega review re-read: "
  f"{n_cov} / {len(rl)}")
