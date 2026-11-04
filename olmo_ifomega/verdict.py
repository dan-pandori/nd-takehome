#!/usr/bin/env python3
"""Candidate fates and the pre-registered verdict per task under each grade (pre-registration: Design 3-5, Verdict).

Grades: IF strict, hand (strict-credited and labelled genuine); OMEGA omega, rl, hand (doubly credited and labelled
sound). Hand grades count only hand-checked samples; unchecked credited samples are listed. "Fresh" = drawn after the
prompt became a candidate (phases ext / confirm). Confirmed (model, prompt, G) = >= 2 G-successes within the first 256
draws, >= 1 of them fresh. Reach prompt (G): s2300 confirmed and dpo has no G-success within 256 on a reach candidate.
A candidate is resolved for dpo if dpo is confirmed under G, dissolved if no RL checkpoint is confirmed under G within
256. Verdict per task: "reach" if >= 3 reach prompts (non-excluded); "no reach at 256" if every reach candidate is
resolved or dissolved; else "inconclusive". Reverse prompt (G): dpo confirmed and s2300 has no G-success within 256.
Inputs: artifacts/olmo_ifomega/graded/*.jsonl via olmo_ifomega/jobs.csv, candidates_fixed.csv, handcheck.csv.
Outputs: olmo_ifomega/candidates.csv (one row per candidate x model), olmo_ifomega/verdict.csv (task x grade).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_ifomega"), Path("olmo_ifomega")
K = 256
MODELS = ("dpo", "s0100", "s0750", "s2300")
GRADES = {"ifbench": ("strict", "hand"), "ifeval": ("strict", "hand"), "omega_in": ("omega", "rl", "hand"),
          "omega_out": ("omega", "rl", "hand")}
GOOD = {"ifbench": "genuine", "ifeval": "genuine", "omega_in": "sound", "omega_out": "sound"}


def main():
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    jobs = [j for j in csv.DictReader(open(O / "jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")]
    hp = O / "handcheck.csv"
    hand = {(r["job"], r["pid"], r["chunk"], r["i"]): r for r in csv.DictReader(open(hp))} if hp.exists() else {}
    cand = list(csv.DictReader(open(O / "candidates_fixed.csv")))
    kinds, challengers = {}, {}
    for c in cand:
        if not c["excluded"]:
            kinds.setdefault(c["pid"], set()).add(c["kind"])
            if c["kind"] == "reach":
                challengers.setdefault(c["pid"], {"s2300"}).update(c["challengers"].split())
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

    def primary(r):
        return bool(r["strict"]) if "strict" in r else bool(r["omega"] and r["rl"])

    def credit(t, g, task):
        r = t[5]
        if g != "hand":
            return bool(r[g])
        h = hand.get((t[4], r["pid"], str(t[1]), str(t[2])))
        return primary(r) and h is not None and h["final_label"] == GOOD[task]

    rows, status = [], {}
    for pid in sorted(kinds):
        task = probs[pid]["task"]
        for kind in sorted(kinds[pid]):
            for model in MODELS:
                ss = draws.get((model, pid), [])[:K]
                if not ss:
                    continue
                key = lambda t: (t[4], pid, str(t[1]), str(t[2]))  # noqa: E731
                rec = {"task": task, "pid": pid, "kind": kind, "model": model, "draws": len(ss),
                       "fixed": sum(t[3] == "fixed" for t in ss), "fresh": sum(t[3] != "fixed" for t in ss),
                       "cut": sum(t[5]["finish"] == "length" for t in ss),
                       "hand_checked": sum(key(t) in hand for t in ss),
                       "credited_unchecked": sum(primary(t[5]) and key(t) not in hand for t in ss)}
                for g in ("strict", "omega", "rl", "hand"):
                    if g not in GRADES[task]:
                        continue
                    ok = [credit(t, g, task) for t in ss]
                    pos = [n + 1 for n, x in enumerate(ok) if x]
                    fresh = sum(x for x, t in zip(ok, ss) if t[3] != "fixed")
                    rec[f"succ_{g}"] = len(pos)
                    rec[f"fresh_{g}"] = fresh
                    rec[f"first_{g}"] = pos[0] if pos else ""
                    rec[f"second_{g}"] = pos[1] if len(pos) > 1 else ""
                    rec[f"confirmed_{g}"] = len(pos) >= 2 and fresh >= 1
                    status[(pid, model, g)] = rec
                rows.append(rec)
    if rows:
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(O / "candidates.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    out = []
    for task, grades in GRADES.items():
        reach = sorted(p for p in kinds if "reach" in kinds[p] and probs[p]["task"] == task)
        rev = sorted(p for p in kinds if "reverse" in kinds[p] and probs[p]["task"] == task)
        for g in grades:
            def ok(pid, m, what):
                r = status.get((pid, m, g))
                return bool(r and (r[f"confirmed_{g}"] if what == "conf" else r[f"succ_{g}"] > 0))
            reach_by = {m: [p for p in reach if ok(p, m, "conf") and not ok(p, "dpo", "succ")] for m in MODELS[1:]}
            resolved = [p for p in reach if ok(p, "dpo", "conf")]
            # dissolved: every challenger (s2300 and each RL checkpoint with a fixed-phase success) drew 256 without
            # confirming; a challenger confirmation cut short (budget) leaves the candidate open
            dissolved = [p for p in reach if p not in resolved and not any(ok(p, m, "conf") for m in MODELS[1:])
                         and all(len(draws.get((m, p), [])) >= K for m in challengers.get(p, {"s2300"}))]
            open_ = [p for p in reach if p not in resolved and p not in dissolved]
            verdict = ("reach" if len(reach_by["s2300"]) >= 3 else "no reach at 256" if not open_ else "inconclusive")
            reverse = [p for p in rev if ok(p, "dpo", "conf") and not ok(p, "s2300", "succ")]
            out.append({"task": task, "grade": g, "n_reach_candidates": len(reach), "n_reverse_candidates": len(rev),
                        "n_dpo_resolved": len(resolved), "n_dissolved": len(dissolved), "n_open": len(open_),
                        **{f"n_reach_{m}": len(v) for m, v in reach_by.items()},
                        "n_reverse": len(reverse), "verdict": verdict,
                        "reach_s2300": " ".join(reach_by["s2300"]), "open": " ".join(open_),
                        "dissolved": " ".join(dissolved), "reverse_prompts": " ".join(reverse)})
    with open(O / "verdict.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(f"{r['task']:9s} {r['grade']:6s} | {r['verdict']:16s} | R {r['n_reach_candidates']} resolved "
              f"{r['n_dpo_resolved']} dissolved {r['n_dissolved']} open {r['n_open']} | reach s0100/s0750/s2300 "
              f"{r['n_reach_s0100']}/{r['n_reach_s0750']}/{r['n_reach_s2300']} | V {r['n_reverse_candidates']} "
              f"reverse {r['n_reverse']}")


if __name__ == "__main__":
    main()
