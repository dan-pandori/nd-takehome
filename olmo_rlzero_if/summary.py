#!/usr/bin/env python3
"""Hand-gate summary numbers for run olmo-rlzero-if (from handcheck.csv and the graded files).

1. Gamed share of RL's first-read strict successes (the brief's comparison with olmo-ifomega's ~36 %): per candidate
   prompt (non-excluded) and model, the first-read set = the first two strict successes in that model's reading
   sequence (gate.py: a challenger's first two fixed-phase strict successes; a defender's first two in draw order);
   share = gamed / read within those sets, per task and kind, with a prompt-bootstrap 95 % interval.
2. Every hand-read item by model, side, role and label.
3. The base's read strict successes by role (defender on reach candidates, challenger on reverse candidates).
Writes olmo_rlzero_if/hand_summary.csv and prints the tables.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")


def main():
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    hand = list(csv.DictReader(open(O / "handcheck.csv")))
    jobs = {j["job"]: j for j in csv.DictReader(open(O / "jobs.csv"))}
    cand = [c for c in csv.DictReader(open(O / "candidates_fixed.csv")) if not c["excluded"]]
    ckind = defaultdict(set)
    for c in cand:
        ckind[c["pid"]].add(c["kind"])
    # reading order key within (pid, model, role): fixed-phase items first two, then fresh in draw order (challenger);
    # draw order (defender)
    groups = defaultdict(list)
    for h in hand:
        if not h["final_label"] or h["pid"] not in ckind:
            continue
        j = jobs[h["job"]]
        groups[(h["pid"], h["model"], h["role"], h["side"])].append(
            (int(j["order"]), int(h["chunk"]), int(h["i"]), j["phase"], h["final_label"]))
    first = defaultdict(list)  # (task, kind, model) -> list of (pid, [labels])
    for (pid, model, role, side), items in groups.items():
        items.sort()
        if side == "challenger":
            fx = [t for t in items if t[3] == "fixed"]
            seq = fx[:2] + [t for t in items if t[3] != "fixed"] + fx[2:]
        else:
            seq = items
        first[(probs[pid]["task"], role, model)].append((pid, [t[4] for t in seq[:2]]))
    rows = []
    rng = np.random.default_rng(0)
    print("first-read strict successes (first two per prompt):")
    for key in sorted(first):
        task, role, model = key
        per = first[key]
        g = np.array([sum(x == "gamed" for x in lab) for _, lab in per], dtype=float)
        n = np.array([len(lab) for _, lab in per], dtype=float)
        share = g.sum() / n.sum()
        idx = rng.integers(0, len(per), size=(10000, len(per)))
        bs = g[idx].sum(1) / n[idx].sum(1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        rows.append({"what": "first_read", "task": task, "role": role, "model": model, "prompts": len(per),
                     "read": int(n.sum()), "gamed": int(g.sum()), "gamed_share": round(share, 3),
                     "lo95": round(lo, 3), "hi95": round(hi, 3)})
        print(f"  {task:8s} {role:8s} {model:6s} prompts {len(per):3d} read {int(n.sum()):4d} gamed {int(g.sum()):4d} "
              f"share {share:.3f} [{lo:.3f}, {hi:.3f}]")
    c = Counter((h["model"], h["side"], h["role"], h["final_label"]) for h in hand if h["final_label"])
    print("all hand-read items:")
    for (m, s, r, lab), v in sorted(c.items()):
        rows.append({"what": "all_read", "task": "", "role": r, "model": m, "side": s, "label": lab, "read": v})
        print(f"  {m:6s} {s:10s} {r:8s} {lab:8s} {v}")
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(O / "hand_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
