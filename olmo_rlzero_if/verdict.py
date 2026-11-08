#!/usr/bin/env python3
"""Candidate fates and the pre-registered verdict per task under each grade (pre-registration: Design 3-5, Verdict).

olmo_ifomega/verdict.py for run olmo-rlzero-if, with its implicit conditions made explicit. Grades: `strict` (the
official strict checker on RL's answer extraction) and `hand` (strict-credited and labelled genuine in
handcheck.csv). Hand grades count only hand-checked samples; unread credited samples are counted per model. "Fresh" =
drawn after the prompt became a candidate (phases ext / confirm). Within the first 256 draws of (model, prompt):
  confirmed(G)  >= 2 G-successes, >= 1 of them fresh (for the defender every success counts: the base on reach
                candidates, main on reverse candidates);
  clean(G)      no G-success, and the model drew its 256 (strict) / drew its 256 with every strict success read
                (hand).
Reach prompt (G): a non-excluded reach candidate where main is confirmed(G) and the base is clean(G).
Resolved: the base is confirmed(G). Dissolved: no RL-Zero-IF checkpoint (s0100, s0500, main) is confirmed(G) and each
challenger with a fixed-phase success drew 256 with every strict success read (hand). Open (gaming), hand only: main
met the challenger stopping rule (>= 7 strict successes read, >= 4 of them fresh, <= 1 genuine). Everything else: open.
Verdict per task and grade: "reach" if >= 3 reach prompts; "no reach at 256" if every reach candidate is resolved or
dissolved; else "inconclusive". Reverse prompt (G): the base confirmed(G) and main clean(G) on a reverse candidate.
math_reach candidates (the optional arm) are reported in candidates.csv only.
Inputs: artifacts/olmo_rlzero_if/graded/*.jsonl via olmo_rlzero_if/jobs.csv, candidates_fixed.csv, handcheck.csv.
Outputs: olmo_rlzero_if/candidates.csv (one row per candidate x kind x model), olmo_rlzero_if/verdict.csv.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")
K = 256
MODELS = ("base", "s0100", "s0500", "main", "math")
RLIF = ("s0100", "s0500", "main")
GRADES = ("strict", "hand")
STOP_READ, STOP_FRESH = 7, 4


def main():
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    jobs = [j for j in csv.DictReader(open(O / "jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")]
    hp = O / "handcheck.csv"
    hand = {(r["job"], r["pid"], r["chunk"], r["i"]): r for r in csv.DictReader(open(hp))} if hp.exists() else {}
    cand = [c for c in csv.DictReader(open(O / "candidates_fixed.csv")) if not c["excluded"]]
    kinds, challengers = defaultdict(set), {}
    for c in cand:
        kinds[c["pid"]].add(c["kind"])
        if c["kind"] == "reach":
            challengers[c["pid"]] = set(c["challengers"].split())
    draws = defaultdict(list)
    for j in jobs:
        f = A / "graded" / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        for r in map(json.loads, open(f)):
            if r["pid"] in kinds:
                draws[(j["model"], r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["phase"], j["job"], r))
    for k in draws:
        draws[k].sort(key=lambda t: t[:3])

    def hkey(t):
        return (t[4], t[5]["pid"], str(t[1]), str(t[2]))

    def credit(t, g):
        if g == "strict":
            return bool(t[5]["strict"])
        h = hand.get(hkey(t))
        return bool(t[5]["strict"]) and h is not None and h["final_label"] == "genuine"

    rows, st = [], {}
    for pid in sorted(kinds):
        for kind in sorted(kinds[pid]):
            defender = {"reach": "base", "math_reach": "base", "reverse": "main"}[kind]
            for model in MODELS:
                ss = draws.get((model, pid), [])[:K]
                if not ss:
                    continue
                strict_s = [t for t in ss if t[5]["strict"]]
                read = [t for t in strict_s if hkey(t) in hand and hand[hkey(t)]["final_label"]]
                rec = {"task": probs[pid]["task"], "pid": pid, "kind": kind, "model": model,
                       "role": "defender" if model == defender else "challenger", "draws": len(ss),
                       "fixed": sum(t[3] == "fixed" for t in ss), "fresh": sum(t[3] != "fixed" for t in ss),
                       "cut": sum(t[5]["finish"] == "length" for t in ss), "strict_read": len(read),
                       "strict_unread": len(strict_s) - len(read),
                       "read_fresh": sum(t[3] != "fixed" for t in read)}
                for g in GRADES:
                    ok = [credit(t, g) for t in ss]
                    pos = [n + 1 for n, x in enumerate(ok) if x]
                    fresh = sum(x for x, t in zip(ok, ss) if t[3] != "fixed")
                    rec[f"succ_{g}"] = len(pos)
                    rec[f"first_{g}"] = pos[0] if pos else ""
                    rec[f"second_{g}"] = pos[1] if len(pos) > 1 else ""
                    need_fresh = 0 if model == defender else 1
                    rec[f"confirmed_{g}"] = len(pos) >= 2 and fresh >= need_fresh
                    full = len(ss) >= K and (g == "strict" or rec["strict_unread"] == 0)
                    rec[f"clean_{g}"] = not pos and full
                rec["gaming_stop"] = (not rec["confirmed_hand"] and len(read) >= STOP_READ
                                      and rec["read_fresh"] >= STOP_FRESH and rec["succ_hand"] <= 1)
                st[(pid, kind, model)] = rec
                rows.append(rec)
    if rows:
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(O / "candidates.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)

    def get(pid, kind, m, field):
        r = st.get((pid, kind, m))
        return bool(r and r[field])

    out = []
    for task in ("ifbench", "ifeval"):
        reach = sorted(p for p in kinds if "reach" in kinds[p] and probs[p]["task"] == task)
        rev = sorted(p for p in kinds if "reverse" in kinds[p] and probs[p]["task"] == task)
        for g in GRADES:
            reach_by = {m: [p for p in reach if get(p, "reach", m, f"confirmed_{g}") and get(p, "reach", "base", f"clean_{g}")]
                        for m in RLIF}
            resolved = [p for p in reach if get(p, "reach", "base", f"confirmed_{g}")]

            def done_reading(p, m):
                r = st.get((p, "reach", m))
                return bool(r and r["draws"] >= K and (g == "strict" or r["strict_unread"] == 0))
            dissolved = [p for p in reach if p not in resolved
                         and not any(get(p, "reach", m, f"confirmed_{g}") for m in RLIF)
                         and all(done_reading(p, m) for m in challengers.get(p, set()) | {"main"})]
            gaming = [p for p in reach if g == "hand" and p not in resolved and p not in dissolved
                      and p not in reach_by["main"] and get(p, "reach", "main", "gaming_stop")]
            open_ = [p for p in reach if p not in resolved and p not in dissolved and p not in reach_by["main"]]
            verdict = ("reach" if len(reach_by["main"]) >= 3 else "no reach at 256" if not open_ and
                       not [p for p in reach if p not in resolved and p not in dissolved] else "inconclusive")
            reverse = [p for p in rev if get(p, "reverse", "base", f"confirmed_{g}") and get(p, "reverse", "main", f"clean_{g}")]
            out.append({"task": task, "grade": g, "n_reach_candidates": len(reach), "n_reverse_candidates": len(rev),
                        "n_base_resolved": len(resolved), "n_dissolved": len(dissolved),
                        "n_open": len(open_), "n_open_gaming": len(gaming),
                        **{f"n_reach_{m}": len(v) for m, v in reach_by.items()},
                        "n_reverse": len(reverse), "verdict": verdict, "reach_main": " ".join(reach_by["main"]),
                        "open": " ".join(open_), "open_gaming": " ".join(gaming), "dissolved": " ".join(dissolved),
                        "reverse_prompts": " ".join(reverse)})
    with open(O / "verdict.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(f"{r['task']:8s} {r['grade']:6s} | {r['verdict']:16s} | R {r['n_reach_candidates']} resolved "
              f"{r['n_base_resolved']} dissolved {r['n_dissolved']} open {r['n_open']} (gaming {r['n_open_gaming']}) | "
              f"reach s0100/s0500/main {r['n_reach_s0100']}/{r['n_reach_s0500']}/{r['n_reach_main']} | "
              f"V {r['n_reverse_candidates']} reverse {r['n_reverse']}")


if __name__ == "__main__":
    main()
