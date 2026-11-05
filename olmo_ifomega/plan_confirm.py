#!/usr/bin/env python3
"""Write a challenger-confirmation job (pre-registration, Design 4-5).

A challenger gets fresh chunks of 16 (3 in flight) until it has >= 2 successes (IF strict, OMEGA doubly) of which >= 1
is fresh, capped at 256 draws in all for that model and prompt. sample.py's sequential mode counts --prior successes
before the job: prior = min(successes drawn so far, 1), so the job stops at its first fresh success when the model
already has one, and at its second when it has none. Hand-gated afterwards like the defenders (a non-genuine success
sends the prompt to a continuation job). Draws so far come from results.csv's `attempts` column.
Usage: plan_confirm.py <job> <model> <seed> <pid> [<pid> ...]   -> pod/olmo_ifomega/jobs/<job>.spec,
       olmo_ifomega/plan/<job>.pids, olmo_ifomega/plan/<job>.prior
"""
import csv
import json
import sys
from pathlib import Path

O = Path("olmo_ifomega")
REPO = {"dpo": ("allenai/Olmo-3-32B-Think-DPO", "main"), "s0100": ("allenai/Olmo-3.1-32B-Think", "step_0100"),
        "s0750": ("allenai/Olmo-3.1-32B-Think", "step_0750"), "s2300": ("allenai/Olmo-3.1-32B-Think", "main")}
K = 256


def main():
    job, model, seed, pids = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    pn, prior = [], []
    for p in pids:
        r = res[(model, p)]
        g = "succ_strict" if probs[p]["task"].startswith("if") else "succ_doubly"
        n = K - int(r["attempts"])
        if n <= 0:
            print(f"skip {p}: {model} already has {r['attempts']} draws")
            continue
        pn.append(f"{p}:{n}")
        prior.append(f"{p}:{min(int(r[g] or 0), 1)}")
    (O / "plan").mkdir(exist_ok=True)
    (O / "plan" / f"{job}.pids").write_text(" ".join(pn) + "\n")
    (O / "plan" / f"{job}.prior").write_text(" ".join(prior) + "\n")
    repo, rev = REPO[model]
    spec = (f"{model} {repo} {rev}|bash pod/olmo_ifomega/job.sh {job} {model} {repo} {rev} 0 @olmo_ifomega/plan/{job}.pids "
            f"{seed} 16 0 --stop_after 2 --inflight 3 --prior @olmo_ifomega/plan/{job}.prior")
    Path(f"pod/olmo_ifomega/jobs/{job}.spec").write_text(spec + "\n")
    print(spec)
    print("pids:", " ".join(pn))
    print("prior:", " ".join(prior))


if __name__ == "__main__":
    main()
