#!/usr/bin/env python3
"""Prompt and trace selection for run olmo-transplant (pre-registration preregistration/olmo-transplant.md).

Reach set: the 43 IFBench hand-reach prompts of review_olmo-ifomega.md (strict mapping), minus those with no s2300
success labelled genuine in olmo_ifomega/handcheck.csv (none can supply a trace) = the eligible reach set; all of it
is run. The brief's design (6 required + seeded, family-stratified draw to 20) is marked as a nested subset `brief20`.
Calibration: 10 IFBench headline prompts (not excluded, not a reach / reverse candidate) that both models solve in
olmo-ifomega's fixed phase (dpo >= 8 / 16 strict, s2300 >= 4 / 8 strict), a seeded family-stratified draw.
Family = the prefix of the prompt's first instruction id (count, format, ratio, sentence, words, custom, repeat).
Writes olmo_transplant/prompts.csv. Deterministic (SEED)."""
import collections
import csv
import json
import random
import re

SEED = 20261108
REQUIRED6 = ["ifbench_136", "ifbench_166", "ifbench_211", "ifbench_248", "ifbench_269", "ifbench_3"]
N_BRIEF = 20
N_CAL = 10
IDX = "artifacts/olmo_transplant/src/index.jsonl"


def reach43():
    for ln in open("review_olmo-ifomega.md"):
        if ln.startswith("IFBench hand-reach prompts (strict mapping, 43)"):
            ids = re.findall(r"`(ifbench_\d+)`", ln)
            assert len(ids) == 43
            return ids
    raise SystemExit("43-prompt list not found")


def family(prob):
    return prob["instruction_id_list"][0].split(":")[0]


def hamilton(counts, total, rng):
    """Largest-remainder allocation of `total` over strata sized `counts` (ties broken by rng)."""
    n = sum(counts.values())
    q = {k: total * v / n for k, v in counts.items()}
    a = {k: int(v) for k, v in q.items()}
    rest = sorted(q, key=lambda k: (-(q[k] - a[k]), rng.random()))
    for k in rest[: total - sum(a.values())]:
        a[k] += 1
    return a


def stratified(pool, fam, total, forced, rng):
    """Family-stratified draw of `total` from `pool` that contains every pid in `forced`."""
    counts = collections.Counter(fam[p] for p in pool)
    quota = hamilton(counts, total, rng)
    pick = list(forced)
    for f in sorted(counts):
        have = [p for p in pick if fam[p] == f]
        cand = sorted(p for p in pool if fam[p] == f and p not in pick)
        rng.shuffle(cand)
        pick += cand[: max(0, quota[f] - len(have))]
    while len(pick) > total:  # forced pids over a family's quota: drop seeded non-forced picks
        extra = [p for p in pick if p not in forced]
        pick.remove(rng.choice(extra))
    while len(pick) < total:
        cand = sorted(p for p in pool if p not in pick)
        pick.append(rng.choice(cand))
    return sorted(pick, key=lambda p: int(p.split("_")[1]))


def main():
    probs = {json.loads(l)["pid"]: json.loads(l) for l in open("olmo_ifomega/problems.jsonl")}
    fam = {p: family(v) for p, v in probs.items() if v["task"] == "ifbench"}
    L43 = reach43()
    hc = list(csv.DictReader(open("olmo_ifomega/handcheck.csv")))
    ngen = collections.Counter(r["pid"] for r in hc if r["model"] == "s2300" and r["final_label"] == "genuine")
    eligible = [p for p in L43 if ngen[p] > 0]
    rng = random.Random(SEED)
    brief20 = stratified(eligible, fam, N_BRIEF, REQUIRED6, rng)
    # calibration
    idx = [json.loads(l) for l in open(IDX)]
    rate = collections.defaultdict(lambda: [0, 0])
    for r in idx:
        if r["job"] in ("F_dpo_ifb", "F_s2300_ifb"):
            c = rate[(r["model"], r["pid"])]
            c[0] += r["strict"]
            c[1] += 1
    headline = set(open("olmo_ifomega/pids_ifbench.txt").read().split()) - \
        {r["pid"] for r in csv.DictReader(open("olmo_ifomega/exclusions.csv"))}
    cands = {r["pid"] for r in csv.DictReader(open("olmo_ifomega/candidates.csv"))}
    calpool = sorted(p for p in headline if p not in cands and p not in L43
                     and rate[("dpo", p)][1] == 16 and rate[("dpo", p)][0] >= 8
                     and rate[("s2300", p)][1] == 8 and rate[("s2300", p)][0] >= 4)
    cal = stratified(calpool, fam, N_CAL, [], random.Random(SEED + 1))
    with open("olmo_transplant/prompts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "set", "family", "instruction_ids", "required6", "brief20", "n_hand_genuine_s2300",
                    "dpo_fixed_strict", "s2300_fixed_strict"])
        for p in L43:
            w.writerow([p, "reach" if p in eligible else "reach_no_trace", fam[p], " ".join(probs[p]["instruction_id_list"]),
                        p in REQUIRED6, p in brief20, ngen[p], "%d/%d" % tuple(rate[("dpo", p)]),
                        "%d/%d" % tuple(rate[("s2300", p)])])
        for p in cal:
            w.writerow([p, "calib", fam[p], " ".join(probs[p]["instruction_id_list"]), False, False, 0,
                        "%d/%d" % tuple(rate[("dpo", p)]), "%d/%d" % tuple(rate[("s2300", p)])])
    print("eligible reach", len(eligible), "excluded (no labelled trace):", [p for p in L43 if p not in eligible])
    print("brief20", brief20, collections.Counter(fam[p] for p in brief20))
    print("calibration pool", len(calpool), collections.Counter(fam[p] for p in calpool))
    print("calibration", cal, collections.Counter(fam[p] for p in cal))


if __name__ == "__main__":
    main()
