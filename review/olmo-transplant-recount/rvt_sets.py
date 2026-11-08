"""Re-grade comparison and set criteria (run olmo-transplant; reviewer's code).

a. my re-grade (out/regrade/<job>.jsonl.gz) vs the executor's graded/<job>.jsonl, row by row: strict, per, loose.
b. traces: reach rl traces must be strict successes (they are genuine-labelled), dpo traces strict failures, calib
   rl traces strict successes of F_s2300_ifb, all under my re-grade.
c. calibration criteria (pre-registration): IFBench headline (not excluded), not a reach or reverse candidate, dpo
   >= 8 / 16 strict and s2300 >= 4 / 8 strict in olmo-ifomega's fixed phase (F_dpo_ifb, F_s2300_ifb; my re-grade);
   the eligible pool size; the 75 calibration source candidates; prompts.csv's fixed-phase columns.
Outputs: out/sets.txt, out/sets.json
"""
import collections
import csv
import gzip
import json

from rvt_core import ART, OUT, RAW, Tee, load_jsonl

P = Tee("sets.txt")


def mine(job):
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        return {r["key"]: r for r in map(json.loads, f)}


# ---------------------------------------------------------------- a. run rows
res = {}
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    m = mine(job)
    ex = {f"{job}|{r['rid']}|{r['i']}": r for r in load_jsonl(ART / "graded" / f"{job}.jsonl")}
    d = collections.Counter()
    for k, r in ex.items():
        a = m.get(k)
        if a is None:
            d["missing_mine"] += 1
            continue
        d["strict_differs"] += a["strict"] != r["strict"]
        d["per_differs"] += a["per"] != r["per"]
        d["loose_differs"] += a["loose"] != r["loose"]
        d["words_differs"] += a["words"] != r.get("answer_words")
    d["missing_exec"] = len(set(m) - set(ex))
    d["has_close_in_answer"] = sum(a["has_close"] for a in m.values())
    d["strict_mine"] = sum(a["strict"] for a in m.values())
    P(f"[a] {job}: rows mine {len(m)} exec {len(ex)}; {dict(d)}")
    res[job] = dict(d)

# ---------------------------------------------------------------- b. traces
src = {}
for job in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb", "F_dpo_ifb"):
    src.update(mine(job))
traces = list(csv.DictReader(open(RAW / "olmo_transplant" / "traces.csv")))
chk = collections.Counter()
for t in traces:
    k = f"{t['job']}|{t['pid']}|{t['chunk']}|{t['i']}"
    s = src[k]["strict"]
    chk[(t["set"], t["kind"], "strict" if s else "fail")] += 1
P(f"[b] traces by (set, kind, my strict grade): {dict(chk)}")
res["traces_strict"] = {"|".join(k): v for k, v in chk.items()}

# ---------------------------------------------------------------- c. calibration criteria
prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
cal = [p["pid"] for p in prompts if p["set"] == "calib"]
reach = {p["pid"] for p in prompts if p["set"] in ("reach", "reach_no_trace")}
fx = collections.defaultdict(lambda: [0, 0])  # (model, pid) -> [strict, n]
for k, r in src.items():
    job, pid = k.split("|")[:2]
    if job in ("F_s2300_ifb", "F_dpo_ifb"):
        fx[(job, pid)][0] += r["strict"]
        fx[(job, pid)][1] += 1
excl = {r["pid"] for r in csv.DictReader(open(RAW / "olmo_ifomega" / "exclusions.csv"))}
cand = collections.defaultdict(set)
for r in csv.DictReader(open(RAW / "olmo_ifomega" / "candidates_fixed.csv")):
    cand[r["pid"]].add(r["kind"])
ifb = [f"ifbench_{i}" for i in range(300)]
elig = [p for p in ifb if p not in excl and not cand[p] and fx[("F_dpo_ifb", p)][0] >= 8 and
        fx[("F_s2300_ifb", p)][0] >= 4 and fx[("F_dpo_ifb", p)][1] == 16 and fx[("F_s2300_ifb", p)][1] == 8]
P(f"[c] fixed-phase rows per prompt: dpo {collections.Counter(v[1] for (j, p), v in fx.items() if j == 'F_dpo_ifb')}, "
  f"s2300 {collections.Counter(v[1] for (j, p), v in fx.items() if j == 'F_s2300_ifb')}")
P(f"    excluded IFBench prompts {len([p for p in ifb if p in excl])}; reach/reverse candidates "
  f"{len([p for p in ifb if cand[p]])} (kinds {dict(collections.Counter(k for p in ifb for k in cand[p]))})")
P(f"    eligible calibration pool (not excluded, not a candidate, dpo >= 8/16, s2300 >= 4/8): {len(elig)}; "
  f"the run's 10 all eligible: {set(cal) <= set(elig)}; not eligible: {sorted(set(cal) - set(elig))}")
P(f"    calibration ∩ reach: {sorted(set(cal) & reach)}")
cols = []
for p in prompts:
    if p["set"] not in ("reach", "calib"):
        continue
    md = f"{fx[('F_dpo_ifb', p['pid'])][0]}/{fx[('F_dpo_ifb', p['pid'])][1]}"
    ms = f"{fx[('F_s2300_ifb', p['pid'])][0]}/{fx[('F_s2300_ifb', p['pid'])][1]}"
    if md != p["dpo_fixed_strict"] or ms != p["s2300_fixed_strict"]:
        cols.append((p["pid"], p["dpo_fixed_strict"], md, p["s2300_fixed_strict"], ms))
P(f"    prompts.csv fixed-phase columns vs my re-grade: {len(cols)} differ {cols[:6]}")
n75 = sum(fx[("F_s2300_ifb", p)][0] for p in cal)
P(f"    calibration source candidates (s2300 strict successes in F_s2300_ifb on the 10): {n75}")
reach_dpo_fixed = [(p["pid"], p["dpo_fixed_strict"]) for p in prompts if p["set"] == "reach" and
                   not p["dpo_fixed_strict"].startswith("0/")]
P(f"    reach prompts with a dpo fixed-phase strict success (strict, not hand; reach is defined on genuine): {reach_dpo_fixed}")
res.update({"eligible_calib": elig, "calib": cal, "n_calib_candidates": n75, "cols_differ": cols})
json.dump(res, open(OUT / "sets.json", "w"), indent=1)
