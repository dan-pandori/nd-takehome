#!/usr/bin/env python3
"""Per-constraint analysis of the IF tasks (pre-registration, Design 6).

For every IF candidate (candidates_fixed.csv, non-excluded) and every constraint of its prompt: each model's
per-constraint success rate over its draws within 256 (graded `per`: the official strict checker, constraint by
constraint), the losing model (reach: dpo; reverse: s2300), the binding constraint (the loser's lowest per-constraint
rate), and whether the constraint id occurs in RL's IF data (rl_if_ids.csv: IFEval's ids do, IFBench's never do) or, for
IFBench, the closest RL constraint and how close it is (ifbench_rl_map.csv: close / loose / none, written from the
checker code before any result). Fates come from candidates.csv (verdict.py): resolved for dpo / reach prompt /
reverse prompt / open, under strict and hand.
Per instruction id (headline prompts, fixed phase): each model's per-constraint rate and the RL - DPO difference, so
RL's gain can be set against the id's distance from RL's IF data.
Outputs: olmo_ifomega/constraints.csv (candidate x constraint), constraints_by_id.csv (task x instruction id),
constraints_summary.csv (task x similarity class: shares among headline constraints, reach candidates' binding
constraints and reach prompts' binding constraints; mean RL - DPO difference).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_ifomega"), Path("olmo_ifomega")
K = 256
MODELS = ("dpo", "s0100", "s0750", "s2300")
IF_TASKS = ("ifbench", "ifeval")


def write(name, rows):
    if not rows:
        return
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(O / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl")) if r["task"] in IF_TASKS}
    excl = {r["pid"] for r in csv.DictReader(open(O / "exclusions.csv"))}
    rl_ids = {r["instruction_id"]: int(r["rl_prompts"]) for r in csv.DictReader(open(O / "rl_if_ids.csv"))}
    near = {r["ifbench_id"]: r for r in csv.DictReader(open(O / "ifbench_rl_map.csv"))}

    def rl_info(task, cid):
        if cid in rl_ids:
            return {"in_rl": True, "rl_prompts": rl_ids[cid], "closest_rl_id": cid, "similarity": "same"}
        m = near.get(cid, {})
        return {"in_rl": False, "rl_prompts": 0, "closest_rl_id": m.get("closest_rl_id", ""),
                "similarity": m.get("similarity", "none" if task == "ifbench" else "")}

    jobs = [j for j in csv.DictReader(open(O / "jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")]
    draws, fixed = defaultdict(list), defaultdict(list)
    for j in jobs:
        f = A / "graded" / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        for r in map(json.loads, open(f)):
            if r["pid"] not in probs:
                continue
            draws[(j["model"], r["pid"])].append((int(j["order"]), r["chunk"], r["i"], r["per"]))
            if j["phase"] == "fixed":
                fixed[(j["model"], r["pid"])].append(r["per"])
    for k in draws:
        draws[k] = [t[3] for t in sorted(draws[k], key=lambda t: t[:3])][:K]

    def rates(per_lists, n):
        if not per_lists:
            return [None] * n
        return [sum(p[i] for p in per_lists) / len(per_lists) for i in range(n)]

    fate = defaultdict(dict)
    cp = O / "candidates.csv"
    if cp.exists():
        for r in csv.DictReader(open(cp)):
            fate[(r["pid"], r["kind"])][r["model"]] = r

    def status(pid, kind, g):
        f = fate.get((pid, kind), {})
        conf = lambda m: f.get(m, {}).get(f"confirmed_{g}") == "True"  # noqa: E731
        succ = lambda m: int(f.get(m, {}).get(f"succ_{g}") or 0) > 0  # noqa: E731
        if kind == "reach":
            if conf("dpo"):
                return "resolved"
            if conf("s2300") and not succ("dpo"):
                return "reach"
            return "open"
        if conf("dpo") and not succ("s2300"):
            return "reverse"
        return "resolved" if conf("s2300") else "open"

    cands = {}
    for c in csv.DictReader(open(O / "candidates_fixed.csv")):
        if c["task"] in IF_TASKS and not c["excluded"]:
            cands[(c["pid"], c["kind"])] = c
    rows = []
    for (pid, kind), c in sorted(cands.items()):
        p = probs[pid]
        ids = p["instruction_id_list"]
        rt = {m: rates(draws.get((m, pid), []), len(ids)) for m in MODELS}
        loser = "dpo" if kind == "reach" else "s2300"
        lr = rt[loser]
        bind = min(range(len(ids)), key=lambda i: lr[i]) if lr[0] is not None else None
        for i, cid in enumerate(ids):
            row = {"task": c["task"], "pid": pid, "kind": kind, "n_constraints": len(ids), "k": i, "instruction_id": cid,
                   "binding": i == bind, "loser": loser,
                   "status_strict": status(pid, kind, "strict"), "status_hand": status(pid, kind, "hand")}
            for m in MODELS:
                row[f"n_{m}"] = len(draws.get((m, pid), []))
                row[f"rate_{m}"] = "" if rt[m][i] is None else round(rt[m][i], 3)
            row.update(rl_info(c["task"], cid))
            rows.append(row)
    write("constraints.csv", rows)

    by_id = []
    for task in IF_TASKS:
        head = [pid for pid, p in probs.items() if p["task"] == task and pid not in excl]
        acc = defaultdict(lambda: defaultdict(list))
        for pid in head:
            for i, cid in enumerate(probs[pid]["instruction_id_list"]):
                for m in MODELS:
                    if fixed.get((m, pid)):
                        acc[cid][m].append(sum(p[i] for p in fixed[(m, pid)]) / len(fixed[(m, pid)]))
        for cid, v in sorted(acc.items()):
            row = {"task": task, "instruction_id": cid, "n_prompts": len(v["dpo"])}
            for m in MODELS:
                row[f"rate_{m}"] = round(sum(v[m]) / len(v[m]), 3) if v[m] else ""
            row["diff_s2300_dpo"] = round(row["rate_s2300"] - row["rate_dpo"], 3) if v["s2300"] and v["dpo"] else ""
            bind = [r for r in rows if r["task"] == task and r["instruction_id"] == cid and r["binding"]]
            row["reach_cand_binding"] = sum(r["kind"] == "reach" for r in bind)
            row["reach_strict_binding"] = sum(r["kind"] == "reach" and r["status_strict"] == "reach" for r in bind)
            row["reach_hand_binding"] = sum(r["kind"] == "reach" and r["status_hand"] == "reach" for r in bind)
            row["reverse_cand_binding"] = sum(r["kind"] == "reverse" for r in bind)
            row.update(rl_info(task, cid))
            by_id.append(row)
    write("constraints_by_id.csv", by_id)

    summ = []
    for task in IF_TASKS:
        ids = [r for r in by_id if r["task"] == task]
        tot = {"headline_constraints": sum(r["n_prompts"] for r in ids),
               "reach_cand_binding": sum(r["reach_cand_binding"] for r in ids),
               "reach_strict_binding": sum(r["reach_strict_binding"] for r in ids),
               "reach_hand_binding": sum(r["reach_hand_binding"] for r in ids)}
        for sim in sorted({r["similarity"] for r in ids}):
            sub = [r for r in ids if r["similarity"] == sim]
            row = {"task": task, "similarity": sim, "n_ids": len(sub)}
            for k, t in tot.items():
                n = sum(r["n_prompts"] if k == "headline_constraints" else r[k] for r in sub)
                row[k] = n
                row[f"{k}_share"] = round(n / t, 3) if t else ""
            w = [(r["n_prompts"], r["diff_s2300_dpo"]) for r in sub if r["diff_s2300_dpo"] != ""]
            row["mean_diff_s2300_dpo"] = round(sum(a * b for a, b in w) / sum(a for a, _ in w), 3) if w else ""
            summ.append(row)
    write("constraints_summary.csv", summ)
    for r in summ:
        print(r)


if __name__ == "__main__":
    main()
