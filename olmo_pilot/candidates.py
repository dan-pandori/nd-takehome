#!/usr/bin/env python3
"""Fate of every reach / reverse candidate: per problem, the base's first correct sample (in draw order) and budget,
and each RL checkpoint's correct samples in F and in fresh confirmation samples. Writes olmo_pilot/candidates.csv.

Usage: candidates.py   (reads olmo_pilot/results.csv written by analyze.py, and olmo_pilot/plan/summary*.json)
"""
import csv
import json
from pathlib import Path

O = Path("olmo_pilot")


def main():
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    cands, rev = [], []
    for f in sorted((O / "plan").glob("summary*.json")):
        s = json.load(open(f))
        cands += [p for p in s["reach_candidates"] if p not in cands]
        rev += [p for p in s["reverse_candidates"] if p not in rev]
    man = {r["pid"]: r for r in csv.DictReader(open(O / "manifest.csv"))}
    models = sorted({m for m, _ in res if m != "base"}, key=lambda m: int(m.split("_")[1]))
    rows = []
    for kind, ps in (("reach_candidate", cands), ("reverse_candidate", rev)):
        for p in ps:
            b = res.get(("base", p), {})
            row = {"pid": p, "kind": kind, "base_attempts": b.get("attempts", ""),
                   "base_first_rl": b.get("first_rl", ""), "base_succ_rl": b.get("succ_rl", ""),
                   "base_succ_ansline": b.get("succ_ansline", "")}
            for m in models:
                c = res.get((m, p), {})
                row[f"{m}_fixed"] = f"{c.get('succ_fixed_rl', '')}/{c.get('n_fixed', '')}"
                row[f"{m}_confirm"] = c.get("succ_confirm_rl", "")
                row[f"{m}_attempts"] = c.get("attempts", "")
                row[f"{m}_first_rl"] = c.get("first_rl", "")
            row["rl_idf5"] = man[p]["rl_idf5"]
            row["emb_cos"] = man[p].get("emb_cos_nearest", "")
            row["family_match"] = man[p].get("family_match", "")
            rows.append(row)
    with open(O / "candidates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r["pid"], r["kind"][:7], "base", f"{r['base_succ_rl']}/{r['base_attempts']}", "first", r["base_first_rl"] or "-",
              *(f"{m[5:]} F{r[m + '_fixed']} C{r[m + '_confirm']}" for m in models))


if __name__ == "__main__":
    main()
