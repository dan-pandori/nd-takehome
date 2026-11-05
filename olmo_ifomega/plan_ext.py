#!/usr/bin/env python3
"""Write the defender-extension job specs from the fixed phase (pre-registration, Design 2-3).

olmo32/plan_ext.py generalised to tasks. Reads olmo_ifomega/results.csv and candidates_fixed.csv (analyze.py);
excluded (contaminated) prompts are not extended; --tasks restricts the tasks (the in-run cut order). Jobs:
  E1_dpo    dpo on reach candidates, up to 256 samples in all (16 fixed + 5 x 48), chunks of 48, stop after the
            chunk in which its success count reaches 2 (IF strict, OMEGA doubly; sample.py --stop_after 2 --inflight 1)
  E1_s2300  s2300 on reverse candidates, up to 256 (8 fixed + 5 x 48 + 8), same rule
Writes pod/olmo_ifomega/jobs/<job>.spec (runq.sh format), olmo_ifomega/plan/<job>.pids (pid:n) and
olmo_ifomega/plan/ext1<suffix>.json. Usage: plan_ext.py [--tasks ifbench,ifeval,omega_in,omega_out] [--seed_dpo 4001]
[--seed_rl 4002] [--suffix ""] [--kinds reach,reverse] [--skip plan/a.json,...] (prompts planned there are left out)
"""
import argparse
import csv
import json
from pathlib import Path

O = Path("olmo_ifomega")
REPO = {"dpo": ("allenai/Olmo-3-32B-Think-DPO", "main"), "s0100": ("allenai/Olmo-3.1-32B-Think", "step_0100"),
        "s0750": ("allenai/Olmo-3.1-32B-Think", "step_0750"), "s2300": ("allenai/Olmo-3.1-32B-Think", "main")}
K = 256


def spec(job, model, pidfile, seed, chunk, flags):
    repo, rev = REPO[model]
    return f"{model} {repo} {rev}|bash pod/olmo_ifomega/job.sh {job} {model} {repo} {rev} 0 @{pidfile} {seed} {chunk} 0 {flags}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="ifbench,ifeval,omega_in,omega_out")
    ap.add_argument("--seed_dpo", type=int, default=4001)
    ap.add_argument("--seed_rl", type=int, default=4002)
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
    reach = sorted({c["pid"] for c in cand if c["kind"] == "reach" and not c["excluded"] and "reach" in kinds} - skip)
    rev = sorted({c["pid"] for c in cand if c["kind"] == "reverse" and not c["excluded"] and "reverse" in kinds} - skip)
    plan = {"tasks": tasks, "reach": reach, "reverse": rev,
            "excluded_candidates": sorted({c["pid"] for c in cand if c["excluded"]}),
            "challengers": {c["pid"]: c["challengers"] for c in cand if c["kind"] == "reach" and not c["excluded"]},
            "jobs": {}}
    (O / "plan").mkdir(exist_ok=True)
    jd = Path("pod/olmo_ifomega/jobs")
    flags = "--stop_after 2 --inflight 1"
    for job, model, pids, seed in ((f"E1_dpo{a.suffix}", "dpo", reach, a.seed_dpo),
                                   (f"E1_s2300{a.suffix}", "s2300", rev, a.seed_rl)):
        if not pids:
            continue
        pn = [(p, K - int(res[(model, p)]["n_fixed"])) for p in pids]
        pf = O / "plan" / f"{job}.pids"
        pf.write_text(" ".join(f"{p}:{n}" for p, n in pn) + "\n")
        (jd / f"{job}.spec").write_text(spec(job, model, pf, seed, 48, flags) + "\n")
        plan["jobs"][job] = dict(pn)
    json.dump(plan, open(O / "plan" / f"ext1{a.suffix}.json", "w"), indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in plan.items()}, indent=1))


if __name__ == "__main__":
    main()
