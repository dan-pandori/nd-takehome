#!/usr/bin/env python3
"""Write a challenger-confirmation job (pre-registration, Design 4-5).

olmo_ifomega/plan_confirm.py for run olmo-rlzero-if. A challenger gets fresh chunks of 16 (2 in flight) until it has
>= 2 strict successes of which >= 1
is fresh, capped at 256 draws in all for that model and prompt. sample.py's sequential mode counts --prior successes
before the job: prior = min(successes drawn so far, 1), so the job stops at its first fresh success when the model
already has one, and at its second when it has none. Hand-gated afterwards like the defenders (a non-genuine success
sends the prompt to a continuation job). Draws so far come from results.csv's `attempts` column.
Usage: plan_confirm.py [--inflight N] [--prior_from <file>] <job> <model> <seed> <pid> [<pid> ...]
       -> pod/olmo_rlzero_if/jobs/<job>.spec, olmo_rlzero_if/plan/<job>.pids, olmo_rlzero_if/plan/<job>.prior
--inflight (default 2) only changes the overshoot. --prior_from: a pid:count file of hand-genuine successes so far
(after the hand gate: prior = min(genuine so far, 1) replaces the strict count, so a gamed earlier success does not count).
"""
import csv
import json
import sys
from pathlib import Path

O = Path("olmo_rlzero_if")
REPO = {"base": ("allenai/Olmo-3-1025-7B", "main"), "s0100": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_100"),
        "s0500": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_500"), "main": ("allenai/Olmo-3-7B-RL-Zero-IF", "main"),
        "math": ("allenai/Olmo-3-7B-RL-Zero-Math", "main")}
K = 256


def main():
    argv, inflight, prior_from = sys.argv[1:], 2, None
    while argv[0].startswith("--"):
        if argv[0] == "--inflight":
            inflight, argv = int(argv[1]), argv[2:]
        elif argv[0] == "--prior_from":
            prior_from = dict(x.split(":") for x in open(argv[1]).read().split())
            argv = argv[2:]
    job, model, seed, pids = argv[0], argv[1], int(argv[2]), argv[3:]
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    res = {(r["model"], r["pid"]): r for r in csv.DictReader(open(O / "results.csv"))}
    pn, prior = [], []
    for p in pids:
        r = res[(model, p)]
        g = "succ_strict"
        n = K - int(r["attempts"])
        if n <= 0:
            print(f"skip {p}: {model} already has {r['attempts']} draws")
            continue
        pn.append(f"{p}:{n}")
        have = int(prior_from.get(p, 0)) if prior_from is not None else int(r[g] or 0)
        prior.append(f"{p}:{min(have, 1)}")
    (O / "plan").mkdir(exist_ok=True)
    (O / "plan" / f"{job}.pids").write_text(" ".join(pn) + "\n")
    (O / "plan" / f"{job}.prior").write_text(" ".join(prior) + "\n")
    repo, rev = REPO[model]
    spec = (f"{model} {repo} {rev}|bash pod/olmo_rlzero_if/job.sh {job} {model} {repo} {rev} 0 @olmo_rlzero_if/plan/{job}.pids "
            f"{seed} 16 0 --stop_after 2 --inflight {inflight} --prior @olmo_rlzero_if/plan/{job}.prior")
    Path(f"pod/olmo_rlzero_if/jobs/{job}.spec").write_text(spec + "\n")
    print(spec)
    print("pids:", " ".join(pn))
    print("prior:", " ".join(prior))


if __name__ == "__main__":
    main()
