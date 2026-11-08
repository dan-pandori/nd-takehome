#!/usr/bin/env python3
"""Write the defender-extension job specs from the fixed phase (pre-registration, Design 2-3).

olmo_ifomega/plan_ext.py for run olmo-rlzero-if. Reads olmo_rlzero_if/results.csv and candidates_fixed.csv
(analyze.py); excluded (contaminated) prompts are not extended; --tasks restricts the tasks; --kinds adds math_reach
(the optional math arm's own candidates; base extended on them like on R). Jobs:
  E1_base   base on reach candidates, up to 256 samples in all (16 fixed + 15 x 16), chunks of 16, at most 2 in
            flight per prompt, stop after the chunk in which its strict count reaches 2
            (sample.py --stop_after 2 --inflight 2)
  E1_main   main on reverse candidates, up to 256 (8 fixed + 248 = 15 x 16 + 8), same rule
Writes pod/olmo_rlzero_if/jobs/<job>.spec (runq.sh format), olmo_rlzero_if/plan/<job>.pids (pid:n) and
olmo_rlzero_if/plan/ext1<suffix>.json. Usage: plan_ext.py [--tasks ifbench,ifeval] [--seed_base 6001] [--seed_rl 6002]
[--suffix ""] [--kinds reach,reverse] [--skip plan/a.json,...] (prompts planned there are left out)
"""
import argparse
import csv
import json
from pathlib import Path

O = Path("olmo_rlzero_if")
REPO = {"base": ("allenai/Olmo-3-1025-7B", "main"), "s0100": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_100"),
        "s0500": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_500"), "main": ("allenai/Olmo-3-7B-RL-Zero-IF", "main"),
        "math": ("allenai/Olmo-3-7B-RL-Zero-Math", "main")}
K = 256


def spec(job, model, pidfile, seed, chunk, flags):
    repo, rev = REPO[model]
    return f"{model} {repo} {rev}|bash pod/olmo_rlzero_if/job.sh {job} {model} {repo} {rev} 0 @{pidfile} {seed} {chunk} 0 {flags}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="ifbench,ifeval")
    ap.add_argument("--seed_base", type=int, default=6001)
    ap.add_argument("--seed_rl", type=int, default=6002)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--kinds", default="reach,reverse")
    ap.add_argument("--skip", default="", help="comma-separated plan/*.json whose planned prompts are left out")
    a = ap.parse_args()
    skip = set()
    for f in filter(None, a.skip.split(",")):
        for pn in json.load(open(f))["jobs"].values():
            skip |= set(pn)
    tasks = a.tasks.split(",")
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    cand = [c for c in csv.DictReader(open(O / "candidates_fixed.csv")) if c["task"] in tasks]
    kinds = a.kinds.split(",")
    reach = sorted({c["pid"] for c in cand if c["kind"] in ("reach", "math_reach") and c["kind"] in kinds
                    and not c["excluded"]} - skip)
    rev = sorted({c["pid"] for c in cand if c["kind"] == "reverse" and not c["excluded"] and "reverse" in kinds} - skip)
    plan = {"tasks": tasks, "reach": reach, "reverse": rev,
            "excluded_candidates": sorted({c["pid"] for c in cand if c["excluded"]}),
            "challengers": {c["pid"]: c["challengers"] for c in cand if c["kind"] == "reach" and not c["excluded"]},
            "jobs": {}}
    (O / "plan").mkdir(exist_ok=True)
    jd = Path("pod/olmo_rlzero_if/jobs")
    flags = "--stop_after 2 --inflight 2"
    for job, model, pids, seed in ((f"E1_base{a.suffix}", "base", reach, a.seed_base),
                                   (f"E1_main{a.suffix}", "main", rev, a.seed_rl)):
        if not pids:
            continue
        pn = [(p, K - int(res[(model, p)]["n_fixed"])) for p in pids]
        pf = O / "plan" / f"{job}.pids"
        pf.write_text(" ".join(f"{p}:{n}" for p, n in pn) + "\n")
        (jd / f"{job}.spec").write_text(spec(job, model, pf, seed, 16, flags) + "\n")
        plan["jobs"][job] = dict(pn)
    json.dump(plan, open(O / "plan" / f"ext1{a.suffix}.json", "w"), indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in plan.items()}, indent=1))


if __name__ == "__main__":
    main()
