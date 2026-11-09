"""Calibration rates and lengths for run olmo-ifladder, from my re-grade and my own length measures.

Calibration (10 prompts; strict only, as pre-registered): dpo's strict rate per prompt at rung 1 (R1cal, 8 prompts;
DROP60 52 / 58 have none), rungs 2-4, and each LoRA (Lchk 16 + Leval 48 = 64 draws per prompt; also Lchk alone, the
fallback guard); against dpo's stored unhinted rate (olmo-ifomega fixed phase F_dpo_ifb, 16 draws per prompt, my
re-grade). The s2300 sanity cells too.

Lengths on the 48 reach prompts, no hints: thinking tokens = response ids up to and including the first '</think>'
(my piece table), answer words = whitespace words after the last '</think>'. LoRAs (Leval, 64 per prompt) vs dpo
(F_dpo_ifb / F_dpo_ife, 16 per prompt) and s2300 (F_s2300_ifb / _ife, 8 per prompt). Two summaries: the pooled
median over draws and the median over prompts of per-prompt medians. Rung cells for context.
Writes out/calib_lengths.{txt,json}.
"""
import collections
import gzip
import json
import statistics as stx

from rvl_core import CODE, OUT, SCR, Pieces, Tee, answer_of, dump, iter_gz, load_csv, unb64, upstream_record
from rvl_graders import if_grade

P = Tee("calib_lengths.txt")
prompts = load_csv(CODE / "prompts.csv")
REACH = [r["pid"] for r in prompts if r["set"] == "reach"]
CAL = [r["pid"] for r in prompts if r["set"] != "reach"]
PC = Pieces()
res = {}

# ---------------------------------------------------------------- stored unhinted (fixed phase)
fixed = {}
for job in ("F_dpo_ifb", "F_dpo_ife", "F_s2300_ifb", "F_s2300_ife"):
    w = "dpo" if "dpo" in job else "s2300"
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        if r["pid"] not in REACH and r["pid"] not in CAL:
            continue
        ans = answer_of(r["text"])
        task, rec = upstream_record(r["pid"])
        st = if_grade(task, rec, ans)[0] if r["pid"] in CAL else None
        ids = unb64(r["ids"])
        fixed.setdefault(w, []).append({"pid": r["pid"], "strict": st, "think": PC.first_close(ids),
                                        "words": None if ans is None else len(ans.split()), "n_tok": len(ids)})
P(f"fixed-phase rows on the 58: { {w: len(v) for w, v in fixed.items()} }")

# ---------------------------------------------------------------- my re-grade rows of the run
def regrade(job):
    return [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]


RJ = {j: regrade(j) for j in ("R1cal_dpo", "R2_dpo", "R3_dpo", "R4_dpo", "R2_s2300", "R3_s2300", "R4_s2300",
                              "Lchk_main", "Lchk_ctrl", "Leval_main", "Leval_ctrl")}


def rate(rows, pid):
    xs = [r["strict"] for r in rows if r["pid"] == pid]
    return (sum(xs) / len(xs), len(xs)) if xs else (None, 0)


base = {p: rate(fixed["dpo"], p) for p in CAL}
base_mean = stx.mean(v[0] for v in base.values())
s_base = {}
P(f"dpo unhinted (F, 16/prompt) calibration strict: "
  f"{ {p.replace('ifbench_', ''): round(v[0], 3) for p, v in base.items()} }; mean {base_mean:.4f}")
cols = [("R1", ["R1cal_dpo"]), ("R2", ["R2_dpo"]), ("R3", ["R3_dpo"]), ("R4", ["R4_dpo"]),
        ("S2", ["R2_s2300"]), ("S3", ["R3_s2300"]), ("S4", ["R4_s2300"]),
        ("LMchk", ["Lchk_main"]), ("LCchk", ["Lchk_ctrl"]), ("LM", ["Lchk_main", "Leval_main"]),
        ("LC", ["Lchk_ctrl", "Leval_ctrl"])]
cal = {}
for name, jobs in cols:
    rows = [r for j in jobs for r in RJ[j]]
    per = {p: rate(rows, p) for p in CAL}
    have = {p: v for p, v in per.items() if v[1]}
    m = stx.mean(v[0] for v in have.values()) if have else None
    half = [p for p, v in have.items() if v[0] < 0.5 * base[p][0]]
    cal[name] = {"per": {p: v for p, v in have.items()}, "mean": m, "n_prompts": len(have), "below_half": half}
    P(f"calibration {name}: prompts {len(have)}, draws/prompt {sorted({v[1] for v in have.values()})}, mean strict "
      f"{m:.4f}" + (f" (= {m / base_mean:.3f} x dpo unhinted)" if m is not None else "") +
      f"; below half dpo's unhinted rate: {[p.replace('ifbench_', '') for p in half]}; per prompt "
      f"{ {p.replace('ifbench_', ''): round(v[0], 3) for p, v in have.items()} }")
res["cal"] = cal
res["cal_base"] = {"per": base, "mean": base_mean}

# ---------------------------------------------------------------- lengths on the 48
def summ(rows, key):
    xs = [r[key] for r in rows if r[key] is not None and r["pid"] in REACH]
    per = collections.defaultdict(list)
    for r in rows:
        if r[key] is not None and r["pid"] in REACH:
            per[r["pid"]].append(r[key])
    pm = [stx.median(v) for v in per.values()]
    return {"pooled_median": stx.median(xs) if xs else None, "median_of_prompt_medians": stx.median(pm) if pm else None,
            "mean": stx.mean(xs) if xs else None, "n": len(xs), "prompts": len(per)}


L = {}
src_rows = {"dpo (F)": [dict(r, think_tok=r["think"], ans_words=r["words"]) for r in fixed["dpo"]],
            "s2300 (F)": [dict(r, think_tok=r["think"], ans_words=r["words"]) for r in fixed["s2300"]],
            "lora_main (Leval)": RJ["Leval_main"], "lora_ctrl (Leval)": RJ["Leval_ctrl"],
            "dpo R2": RJ["R2_dpo"], "dpo R3": RJ["R3_dpo"], "dpo R4": RJ["R4_dpo"]}
for name, rows in src_rows.items():
    L[name] = {"think_tok": summ(rows, "think_tok"), "ans_words": summ(rows, "ans_words")}
    t, a = L[name]["think_tok"], L[name]["ans_words"]
    P(f"lengths {name}: thinking tokens pooled median {t['pooled_median']} / median of prompt medians "
      f"{t['median_of_prompt_medians']} (n {t['n']}, {t['prompts']} prompts); answer words pooled median "
      f"{a['pooled_median']} / median of prompt medians {a['median_of_prompt_medians']}")
d = L["dpo (F)"]
for arm in ("lora_main (Leval)", "lora_ctrl (Leval)"):
    for k in ("think_tok", "ans_words"):
        for s in ("pooled_median", "median_of_prompt_medians"):
            P(f"    {arm} {k} {s}: {L[arm][k][s] / d[k][s]:.3f} x dpo's")
res["lengths"] = L
dump(res, "calib_lengths.json")
