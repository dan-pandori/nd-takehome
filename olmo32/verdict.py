#!/usr/bin/env python3
"""Candidate fates and the pre-registered verdict under each grade (pre-registration: Design 3-5, Verdict).

Grades: rl, final, hand (final-credited and confirmed sound under the uniform rule), hand_strict (the same with
residue-representative transitions counted as flawed: olmo32/handcheck_rule_aime2025_28.md). Hand grades count only
hand-checked samples; unchecked credited samples are listed. "Fresh" = drawn after the problem became a candidate
(phases ext / confirm). Confirmed (model, problem, G) = >= 2 G-successes within the first 256 draws, >= 1 of them fresh.
Reach problem of checkpoint c (G): c confirmed and dpo has no G-success within 256 on a reach candidate. Verdict:
"reach candidates for scale-up" if s2300 has >= 3 reach problems (non-excluded); "no reach at 256" if every reach
candidate is confirmed for dpo; else "inconclusive". Reverse problem (G): dpo confirmed and s2300 has no G-success.
Inputs: artifacts/olmo32/graded/*.jsonl via olmo32/jobs.csv, olmo32/candidates_fixed.csv, olmo32/handcheck.csv.
Outputs: olmo32/candidates.csv (one row per candidate x model), olmo32/verdict.csv (one row per grade).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo32"), Path("olmo32")
K = 256
STRICT_FLAWED = {"h4984ee", "h4cbdbc", "h9fea38", "h6d8d18", "h1747e2", "h094333", "hb2cdd6"}  # representative transitions
GRADES = ("rl", "final", "hand", "hand_strict")


def main():
    jobs = [j for j in csv.DictReader(open(O / "jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")]
    hand = {(r["job"], r["pid"], r["chunk"], r["i"]): r for r in csv.DictReader(open(O / "handcheck.csv"))}
    cand = list(csv.DictReader(open(O / "candidates_fixed.csv")))
    reach = sorted({c["pid"] for c in cand if c["kind"] == "reach" and not c["excluded"]})
    rev = sorted({c["pid"] for c in cand if c["kind"] == "reverse" and not c["excluded"]})
    draws = defaultdict(list)  # (model, pid) -> [(order, chunk, i, phase, job, row)]
    for j in jobs:
        f = A / "graded" / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        for r in map(json.loads, open(f)):
            if r["pid"] in reach + rev:
                draws[(j["model"], r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["phase"], j["job"], r))
    for k in draws:
        draws[k].sort(key=lambda t: t[:3])

    def credit(t, g):
        r, h = t[5], hand.get((t[4], t[5]["pid"], str(t[1]), str(t[2])))
        if g in ("rl", "final"):
            return bool(r[g])
        if not (r["rl"] or r["final"]) or not r["final"] or h is None:
            return False
        lab = h["final_label"]
        if g == "hand_strict" and h["item"] in STRICT_FLAWED:
            lab = "flawed"
        return lab == "sound"

    rows, status = [], {}
    for pid in reach + rev:
        kind = "reach" if pid in reach else "reverse"
        for model in ("dpo", "s0100", "s0750", "s2300"):
            ss = draws.get((model, pid), [])[:K]
            if not ss:
                continue
            rec = {"pid": pid, "kind": kind, "model": model, "draws": len(ss),
                   "fixed": sum(t[3] == "fixed" for t in ss), "fresh": sum(t[3] != "fixed" for t in ss),
                   "cut": sum(t[5]["finish"] == "length" for t in ss),
                   "hand_checked": sum((t[4], pid, str(t[1]), str(t[2])) in hand for t in ss),
                   "credited_unchecked": sum((t[5]["rl"] or t[5]["final"]) and (t[4], pid, str(t[1]), str(t[2])) not in hand
                                             for t in ss)}
            for g in GRADES:
                ok = [credit(t, g) for t in ss]
                pos = [n + 1 for n, x in enumerate(ok) if x]
                fresh = sum(x for x, t in zip(ok, ss) if t[3] != "fixed")
                rec[f"succ_{g}"] = len(pos)
                rec[f"fresh_{g}"] = fresh
                rec[f"first_{g}"] = pos[0] if pos else ""
                rec[f"second_{g}"] = pos[1] if len(pos) > 1 else ""
                rec[f"confirmed_{g}"] = len(pos) >= 2 and fresh >= 1
                status[(pid, model, g)] = rec
            rows.append(rec)
    with open(O / "candidates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    out = []
    for g in GRADES:
        def ok(pid, m, key):
            r = status.get((pid, m, g))
            return bool(r and (r[f"confirmed_{g}"] if key == "conf" else r[f"succ_{g}"] > 0))
        reach_by = {m: [p for p in reach if ok(p, m, "conf") and not ok(p, "dpo", "succ")]
                    for m in ("s0100", "s0750", "s2300")}
        no_reach = all(ok(p, "dpo", "conf") for p in reach)
        verdict = ("reach candidates for scale-up" if len(reach_by["s2300"]) >= 3 else
                   "no reach at 256" if no_reach else "inconclusive")
        reverse = [p for p in rev if ok(p, "dpo", "conf") and not ok(p, "s2300", "succ")]
        out.append({"grade": g, "reach_candidates": " ".join(reach), "reverse_candidates": " ".join(rev),
                    "dpo_confirmed_on": " ".join(p for p in reach if ok(p, "dpo", "conf")),
                    "dpo_any_success_on": " ".join(p for p in reach if ok(p, "dpo", "succ")),
                    **{f"reach_{m}": " ".join(v) for m, v in reach_by.items()},
                    **{f"n_reach_{m}": len(v) for m, v in reach_by.items()},
                    "reverse_problems": " ".join(reverse), "n_reverse": len(reverse), "verdict": verdict})
    with open(O / "verdict.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r["grade"], "|", r["verdict"], "| reach s0100/s0750/s2300:", r["n_reach_s0100"], r["n_reach_s0750"],
              r["n_reach_s2300"], "| reverse:", r["n_reverse"], "| dpo confirmed on:", r["dpo_confirmed_on"] or "-",
              "| dpo any success on:", r["dpo_any_success_on"] or "-")


if __name__ == "__main__":
    main()
