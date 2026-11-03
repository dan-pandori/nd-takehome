#!/usr/bin/env python3
"""Write the defender-extension job specs from the fixed phase (pre-registration, Design 2-3).

Reads olmo32/results.csv and olmo32/candidates_fixed.csv (analyze.py). Candidates on the union of the rl and final
definitions; excluded (contaminated) problems are not extended. Defender jobs:
  E1_dpo    dpo on reach candidates, 240 more samples each (16 + 5 x 48 = 256), chunks of 48, stop after the chunk
            in which its doubly-credited count reaches 2 (sample.py --stop_after 2 --inflight 1)
  E1_s2300  s2300 on reverse candidates, 248 more (8 + 5 x 48 + 8 = 256), same rule
Writes pod/olmo32/jobs/<job>.spec (runq.sh format) and olmo32/plan/ext1.json (the candidate lists).
Usage: plan_ext.py [--seed_dpo 3001] [--seed_rl 3002]
"""
import argparse
import csv
import json
from pathlib import Path

O = Path("olmo32")
REPO = {"dpo": ("allenai/Olmo-3-32B-Think-DPO", "main"), "s0100": ("allenai/Olmo-3.1-32B-Think", "step_0100"),
        "s0750": ("allenai/Olmo-3.1-32B-Think", "step_0750"), "s2300": ("allenai/Olmo-3.1-32B-Think", "main")}
K = 256


def spec(job, model, pids_n, seed, chunk, flags):
    repo, rev = REPO[model]
    pids = ",".join(f"{p}:{n}" for p, n in pids_n)
    return f"{model} {repo} {rev}|bash pod/olmo32/job.sh {job} {model} {repo} {rev} 0 {pids} {seed} {chunk} 0 {flags}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed_dpo", type=int, default=3001)
    ap.add_argument("--seed_rl", type=int, default=3002)
    a = ap.parse_args()
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    cand = list(csv.DictReader(open(O / "candidates_fixed.csv")))
    reach = sorted({c["pid"] for c in cand if c["kind"] == "reach" and not c["excluded"]})
    rev = sorted({c["pid"] for c in cand if c["kind"] == "reverse" and not c["excluded"]})
    plan = {"reach": reach, "reverse": rev,
            "excluded_candidates": sorted({c["pid"] for c in cand if c["excluded"]}),
            "challengers": {c["pid"]: c["challengers"] for c in cand if c["kind"] == "reach" and not c["excluded"]},
            "jobs": {}}
    (O / "plan").mkdir(exist_ok=True)
    jd = Path("pod/olmo32/jobs")
    jd.mkdir(parents=True, exist_ok=True)
    flags = "--stop_after 2 --inflight 1"
    if reach:
        pn = [(p, K - int(res[("dpo", p)]["n_fixed"])) for p in reach]
        (jd / "E1_dpo.spec").write_text(spec("E1_dpo", "dpo", pn, a.seed_dpo, 48, flags) + "\n")
        plan["jobs"]["E1_dpo"] = dict(pn)
    if rev:
        pn = [(p, K - int(res[("s2300", p)]["n_fixed"])) for p in rev]
        (jd / "E1_s2300.spec").write_text(spec("E1_s2300", "s2300", pn, a.seed_rl, 48, flags) + "\n")
        plan["jobs"]["E1_s2300"] = dict(pn)
    json.dump(plan, open(O / "plan" / "ext1.json", "w"), indent=1)
    print(json.dumps(plan, indent=1))


if __name__ == "__main__":
    main()
