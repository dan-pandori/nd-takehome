#!/usr/bin/env python3
"""Hand-gate planner (pre-registration Design 3-5, Part B steps 2-4): what to read next, what to draw next.

For every non-excluded candidate (reach: defender base, challengers s0100 / s0500 / main; reverse: defender main,
challenger base) and model with draws, the strict successes within its first 256 draws are taken in draw order
(jobs.csv `order`, then chunk, i). Labels come from olmo_rlzero_if/handcheck.csv (`final_label`, my confirmation).
Status per (candidate, kind, model):
  confirmed    >= 2 genuine, >= 1 fresh for a challenger (any for the defender)
  stop_gaming  challenger only: >= 7 strict successes read, >= 4 of them fresh, <= 1 genuine (olmo-ifomega dev. 13)
  read         unread strict successes remain: the next `--n_read` (challenger) / `--n_read_def` (defender) in the
               reading sequence are listed: defender = draw order; challenger = its first two fixed-phase strict
               successes (the first-read set), then its fresh ones in draw order, then its other fixed-phase ones
  draw         every strict success read, not confirmed, fewer than 256 draws: more samples needed
  exhausted    256 draws, every strict success read, not confirmed
Usage: gate.py [--models main,base] [--kinds reach,reverse] [--n_read 3] [--n_read_def 2] [--items out.csv]
       prints a status table; --items writes the next reading round (job,pid,chunk,i,model,side,role) for
       handcheck.py prep; --draws writes pid lists of (model, kind) needing draws to <prefix>_<model>_<kind>.txt
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")
K = 256


def load_draws(pids):
    jobs = [j for j in csv.DictReader(open(O / "jobs.csv")) if j["phase"] in ("fixed", "ext", "confirm")]
    draws = defaultdict(list)
    for j in jobs:
        f = A / "graded" / f"{j['job']}.jsonl"
        if not f.exists():
            continue
        for r in map(json.loads, open(f)):
            if r["pid"] in pids:
                draws[(j["model"], r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["phase"], j["job"], r))
    for k in draws:
        draws[k] = sorted(draws[k], key=lambda t: t[:3])[:K]
    return draws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="main,base,s0500,s0100")
    ap.add_argument("--kinds", default="reach,reverse")
    ap.add_argument("--n_read", type=int, default=3)
    ap.add_argument("--n_read_def", type=int, default=2)
    ap.add_argument("--items", default=None)
    ap.add_argument("--draws", default=None)
    ap.add_argument("--pids", default=None, help="restrict to these pids (comma-separated or @file)")
    a = ap.parse_args()
    cand = [c for c in csv.DictReader(open(O / "candidates_fixed.csv")) if not c["excluded"]
            and c["kind"] in a.kinds.split(",")]
    if a.pids:
        keep = set(open(a.pids[1:]).read().split() if a.pids.startswith("@") else a.pids.split(","))
        cand = [c for c in cand if c["pid"] in keep]
    hp = O / "handcheck.csv"
    lab = {}
    if hp.exists():
        for r in csv.DictReader(open(hp)):
            lab[(r["job"], r["pid"], r["chunk"], r["i"])] = r["final_label"] or "pending"
    draws = load_draws({c["pid"] for c in cand})
    models = a.models.split(",")
    items, need_draw, rows = [], defaultdict(list), []
    for c in cand:
        pid, kind = c["pid"], c["kind"]
        defender = "base" if kind == "reach" else "main"
        chall = ({"main"} | set(c["challengers"].split())) if kind == "reach" else {"base"}
        for m in models:
            if m != defender and m not in chall:
                continue
            ss = draws.get((m, pid), [])
            succ = [t for t in ss if t[5]["strict"]]
            lb = [lab.get((t[4], pid, str(t[1]), str(t[2]))) for t in succ]
            gen = [t for t, x in zip(succ, lb) if x == "genuine"]
            read = [t for t, x in zip(succ, lb) if x in ("genuine", "gamed")]
            pend = [t for t, x in zip(succ, lb) if x == "pending"]
            fresh_g = sum(t[3] != "fixed" for t in gen)
            is_def = m == defender
            if len(gen) >= 2 and (is_def or fresh_g >= 1):
                status = "confirmed"
            elif (not is_def and len(read) >= 7 and sum(t[3] != "fixed" for t in read) >= 4 and len(gen) <= 1):
                status = "stop_gaming"
            elif pend:
                status = "pending"
            else:
                # reading sequence (fixed in advance): defender = draw order; challenger = its first two
                # fixed-phase strict successes (the first-read set), then fresh ones in draw order, then the rest
                if is_def:
                    seq = succ
                else:
                    fx = [t for t in succ if t[3] == "fixed"]
                    seq = fx[:2] + [t for t in succ if t[3] != "fixed"] + fx[2:]
                unread = [t for t in seq if lab.get((t[4], pid, str(t[1]), str(t[2]))) is None]
                if unread:
                    status = "read"
                    n = a.n_read_def if is_def else a.n_read
                    for t in unread[:n]:
                        items.append({"job": t[4], "pid": pid, "chunk": t[1], "i": t[2], "model": m,
                                      "side": "defender" if is_def else "challenger", "role": kind})
                elif len(ss) < K:
                    status = "draw"
                    need_draw[(m, kind)].append(pid)
                else:
                    status = "exhausted"
            rows.append({"pid": pid, "task": c["task"], "kind": kind, "model": m, "draws": len(ss),
                         "strict": len(succ), "read": len(read), "genuine": len(gen), "fresh_genuine": fresh_g,
                         "status": status})
    cnt = Counter((r["kind"], r["model"], r["status"]) for r in rows)
    for k in sorted(cnt):
        print(*k, cnt[k])
    with open(O / "gate_status.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["pid"])
        w.writeheader()
        w.writerows(rows)
    if a.items:
        with open(a.items, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["job", "pid", "chunk", "i", "model", "side", "role"])
            w.writeheader()
            w.writerows(items)
        print(f"{len(items)} items to read -> {a.items}")
    if a.draws:
        for (m, kind), ps in sorted(need_draw.items()):
            Path(f"{a.draws}_{m}_{kind}.txt").write_text(" ".join(sorted(set(ps))) + "\n")
            print(f"draw: {m} {kind} {len(set(ps))} prompts -> {a.draws}_{m}_{kind}.txt")


if __name__ == "__main__":
    main()
