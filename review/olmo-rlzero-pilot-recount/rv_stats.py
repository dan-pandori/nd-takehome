#!/usr/bin/env python3
"""pass@k, matched-k dynamics, full-budget reach both ways round, strong reach, extension-protocol checks and the
pre-registered verdict, from my own table (out/table.json, rv_table.py). Writes out/stats.json and prints tables.

Definitions (pre-registration Part A + Part B amendment; my reading):
- headline = AIME 2024-2026 minus the 7 exclusions of olmo_pilot/exclusions.csv (fixed 02:30 UTC, before phase F).
- pass@k: Chen et al. unbiased estimator on the fixed-budget (phase F) samples, k <= n_fixed; problem bootstrap
  (10,000 resamples, percentile 95 %).
- matched k = 8: expected entries of c vs b = sum_p pass8_c (1 - pass8_b); exits = sum_p pass8_b (1 - pass8_c)
  (independent draws). Also the realised solved sets on the first 8 samples of each model.
- reach of c (full budget): >= 1 correct of c in its fixed budget AND 0 correct base samples in the base's whole
  budget (F + extension). Variant "c any": >= 1 correct of c in F + confirmation.
- reverse of c: >= 1 correct base sample (whole budget) AND 0 correct samples of c in c's whole budget.
- strong reach: reach + c >= 2 correct incl. >= 1 fresh confirmation sample + base has 0 integer-read-out-correct
  samples + base budget >= K* (largest extension budget reached) + not excluded.
"""
import csv
import json
import math
import sys
from collections import defaultdict

import numpy as np

import rv_core as R

B = 10000
MODELS = ["base", "step_0100", "step_0500", "step_2800"]


def pk(n, c, k):
    if k > n:
        return float("nan")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def boot(vals, rng_seed=1):
    v = np.asarray(vals, float)
    rng = np.random.default_rng(rng_seed)
    idx = rng.integers(0, len(v), size=(B, len(v)))
    m = v[idx].mean(1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_diff(a, b, rng_seed=2):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(rng_seed)
    idx = rng.integers(0, len(a), size=(B, len(a)))
    d = a[idx].mean(1) - b[idx].mean(1)
    return float(a.mean() - b.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main():
    T = json.load(open(R.OUT / "table.json"))
    probs = R.problems(with_probe=False)
    excl = {r["pid"] for r in csv.DictReader(open(R.ROOT / "olmo_pilot" / "exclusions.csv"))}
    evalp = [p for p in sorted(probs) if probs[p]["set"] in R.HEADLINE_SETS]
    head = [p for p in evalp if p not in excl]
    half = open(R.ROOT / "olmo_pilot" / "plan" / "F_s0100_half.txt").read().split()
    out = {"n_eval": len(evalp), "n_head": len(head), "excluded": sorted(excl)}
    cell = lambda m, p: T.get(f"{m}|{p}")

    # ---------------- pass@k per model and set (rl grade, fixed budget)
    pas = {}
    for grade in ("rl", "main"):
        for m in MODELS:
            for sname, pids in [("all", head)] + [(s, [p for p in head if probs[p]["set"] == s]) for s in R.HEADLINE_SETS]:
                pp = [p for p in pids if cell(m, p)]
                if not pp:
                    continue
                n = cell(m, pp[0])["n_fixed"]
                for k in (1, 2, 4, 8, 16):
                    if k > min(cell(m, p)["n_fixed"] for p in pp):
                        continue
                    v = [pk(cell(m, p)["n_fixed"], cell(m, p)[f"c_fixed_{grade}"], k) for p in pp]
                    pas[f"{grade}|{m}|{sname}|{k}"] = (len(pp),) + boot(v)
    out["passk"] = pas
    print("pass@k (rl, phase F, headline; mean [95% problem bootstrap])")
    for m in MODELS:
        for sname in ("all",) + R.HEADLINE_SETS:
            row = [f"{m:9s} {sname:8s}"]
            for k in (1, 8, 16):
                key = f"rl|{m}|{sname}|{k}"
                if key in pas:
                    n, mu, lo, hi = pas[key]
                    row.append(f"p@{k}={mu:.3f} [{lo:.3f},{hi:.3f}] (n={n})")
            print("  ".join(row))

    # same-subset comparison on step_0100's half (headline problems in the half)
    hh = [p for p in head if p in half]
    out["half_head"] = len(hh)
    print(f"\nhalf subset: {len(hh)} headline problems")
    for m in MODELS:
        v1 = [pk(cell(m, p)["n_fixed"], cell(m, p)["c_fixed_rl"], 1) for p in hh]
        v8 = [pk(cell(m, p)["n_fixed"], cell(m, p)["c_fixed_rl"], 8) for p in hh]
        a, b = boot(v1), boot(v8)
        out[f"half|{m}"] = {"pass1": a, "pass8": b}
        print(f"  {m:9s} p@1={a[0]:.3f} [{a[1]:.3f},{a[2]:.3f}]  p@8={b[0]:.3f} [{b[1]:.3f},{b[2]:.3f}]")

    # ---------------- matched k = 8 expected entries / exits (vs base and vs previous checkpoint)
    print("\nmatched k=8 expected entries/exits (rl, fixed budget)")
    dyn = {}

    def ee(c, b, pids):
        ent = sum(pk(cell(c, p)["n_fixed"], cell(c, p)["c_fixed_rl"], 8) * (1 - pk(cell(b, p)["n_fixed"], cell(b, p)["c_fixed_rl"], 8)) for p in pids)
        ext = sum(pk(cell(b, p)["n_fixed"], cell(b, p)["c_fixed_rl"], 8) * (1 - pk(cell(c, p)["n_fixed"], cell(c, p)["c_fixed_rl"], 8)) for p in pids)
        return round(ent, 3), round(ext, 3)

    for c, b, pids, lab in [("step_0500", "base", head, "all83"), ("step_2800", "base", head, "all83"),
                            ("step_2800", "step_0500", head, "all83"), ("step_0100", "base", hh, "half"),
                            ("step_0500", "base", hh, "half"), ("step_2800", "base", hh, "half"),
                            ("step_0500", "step_0100", hh, "half")]:
        e, x = ee(c, b, pids)
        dyn[f"{c}_vs_{b}|{lab}"] = {"entries": e, "exits": x, "n": len(pids)}
        print(f"  {c} vs {b} on {lab} ({len(pids)}): entries {e}, exits {x}, net {e - x:.3f}")
    out["dyn_k8"] = dyn

    # realised first-8 solved sets
    def first8(m, p):
        return None  # needs per-sample order; computed in rv_first8.py
    # ---------------- reach / reverse at full budget
    print("\nfull-budget reach / reverse (rl)")
    rr = {}
    kstar = max((cell("base", p)["attempts"] for p in head), default=0)
    for c in ("step_0100", "step_0500", "step_2800"):
        reach_f = [p for p in head if cell(c, p) and cell(c, p)["c_fixed_rl"] >= 1 and cell("base", p)["succ_rl"] == 0]
        reach_any = [p for p in head if cell(c, p) and cell(c, p)["succ_rl"] >= 1 and cell("base", p)["succ_rl"] == 0]
        rev = [p for p in head if cell(c, p) and cell("base", p)["succ_rl"] >= 1 and cell(c, p)["succ_rl"] == 0]
        strong = [p for p in reach_any if cell(c, p)["succ_rl"] >= 2 and cell(c, p)["c_confirm_rl"] >= 1
                  and cell("base", p)["succ_int"] == 0 and cell("base", p)["attempts"] >= kstar]
        # the same under main and under the integer read-out
        reach_main = [p for p in head if cell(c, p) and cell(c, p)["succ_main"] >= 1 and cell("base", p)["succ_main"] == 0]
        reach_int = [p for p in head if cell(c, p) and cell(c, p)["succ_int"] >= 1 and cell("base", p)["succ_int"] == 0]
        rev_main = [p for p in head if cell(c, p) and cell("base", p)["succ_main"] >= 1 and cell(c, p)["succ_main"] == 0]
        rev_int = [p for p in head if cell(c, p) and cell("base", p)["succ_int"] >= 1 and cell(c, p)["succ_int"] == 0]
        rr[c] = {"reach_fixed": reach_f, "reach_any": reach_any, "reverse": rev, "strong": strong,
                 "reach_main": reach_main, "reach_int": reach_int, "reverse_main": rev_main, "reverse_int": rev_int,
                 "reverse_budget_of_c": {p: cell(c, p)["attempts"] for p in rev}}
        print(f"  {c}: reach(F) {len(reach_f)} {reach_f}; reach(F+C) {len(reach_any)}; strong {len(strong)}; "
              f"reverse {len(rev)} {[(p, cell(c, p)['attempts']) for p in rev]}; main reach/rev {len(reach_main)}/{len(rev_main)}; "
              f"int reach/rev {len(reach_int)}/{len(rev_int)}")
    out["reach"] = rr
    out["kstar"] = kstar

    # ---------------- candidates and extension protocol
    print("\nreach candidates after phase F (RL F >= 1 among step_2800/step_0500, base F == 0) and their resolution")
    cands = [p for p in head if cell("base", p)["c_fixed_rl"] == 0 and any(cell(m, p)["c_fixed_rl"] >= 1 for m in ("step_2800", "step_0500"))]
    rows = []
    for p in cands:
        b = cell("base", p)
        rows.append({"pid": p, "s2800_F": cell("step_2800", p)["c_fixed_rl"], "s2800_C": f"{cell('step_2800', p)['c_confirm_rl']}/{cell('step_2800', p)['n_confirm']}",
                     "s0500_F": cell("step_0500", p)["c_fixed_rl"], "s0500_C": f"{cell('step_0500', p)['c_confirm_rl']}/{cell('step_0500', p)['n_confirm']}",
                     "s0100_F": (cell("step_0100", p)["c_fixed_rl"] if cell("step_0100", p) else None),
                     "base_attempts": b["attempts"], "base_succ": b["succ_rl"], "base_first": b["first_rl"],
                     "base_first_main": b["first_main"], "base_first_int": b["first_int"], "base_succ_int": b["succ_int"]})
    for r in rows:
        print("  ", r)
    out["candidates"] = rows
    rev_c = [p for p in head if cell("base", p)["c_fixed_rl"] >= 1 and cell("step_2800", p)["c_fixed_rl"] == 0]
    print("reverse candidates after F (base F >= 1, step_2800 F == 0):", rev_c)
    out["reverse_candidates_F"] = [{"pid": p, "base_F": cell("base", p)["c_fixed_rl"], "s2800_attempts": cell("step_2800", p)["attempts"],
                                    "s2800_succ": cell("step_2800", p)["succ_rl"], "s2800_first": cell("step_2800", p)["first_rl"]} for p in rev_c]
    for r in out["reverse_candidates_F"]:
        print("  ", r)
    # problems the base solved only in its extension and step_2800 missed in F (symmetric reverse extension)
    late_rev = [p for p in cands if cell("step_2800", p)["c_fixed_rl"] == 0]
    print("candidates step_2800 missed in F (need the symmetric extension):", late_rev,
          [(cell("step_2800", p)["attempts"], cell("step_2800", p)["first_rl"]) for p in late_rev])

    # step_0100 problems never extended for the base
    s01_new = [p for p in hh if cell("step_0100", p)["c_fixed_rl"] >= 1 and cell("base", p)["c_fixed_rl"] == 0]
    print("step_0100 solves (F) where base F == 0:", [(p, cell("base", p)["attempts"], cell("base", p)["succ_rl"]) for p in s01_new])
    out["s0100_vs_baseF0"] = [(p, cell("base", p)["attempts"], cell("base", p)["succ_rl"]) for p in s01_new]

    # ---------------- verdict inputs
    b8 = [pk(cell("base", p)["n_fixed"], cell("base", p)["c_fixed_rl"], 8) for p in head]
    f8 = [pk(cell("step_2800", p)["n_fixed"], cell("step_2800", p)["c_fixed_rl"], 8) for p in head]
    d = boot_diff(f8, b8)
    bb, ff = boot(b8), boot(f8)
    out["verdict_inputs"] = {"base_pass8": bb, "final_pass8": ff, "final_minus_base_pass8": d,
                             "base_point_inside_final_CI": ff[1] <= bb[0] <= ff[2],
                             "diff_CI_contains_0": d[1] <= 0 <= d[2]}
    print(f"\nverdict inputs: base pass@8 {bb}, final pass@8 {ff}, diff {d}")
    s, r_ = len(rr["step_2800"]["strong"]), len(rr["step_2800"]["reverse"])
    ext = s >= 3 and s - r_ >= 2
    elic_a = s == 0 or s <= r_
    print(f"strong reach {s}, reverse {r_}: 'extended' rule {ext}; elicitation clause (a) {elic_a}; clause (b) at k=8 "
          f"{out['verdict_inputs']['diff_CI_contains_0']}")
    json.dump(out, open(R.OUT / "stats.json", "w"), indent=1)


if __name__ == "__main__":
    main()
