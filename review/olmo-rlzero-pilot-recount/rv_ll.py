#!/usr/bin/env python3
"""Phase L recount: integrity of the scored items and my own likelihood summary.

Checks per scored item (artifacts/olmo_pilot/ll/*):
  - resp_ids == the stored sample's token ids (same job|pid|chunk|i) and the sample is rl-correct in my re-grade;
  - prompt_ids == tokenizer(my own rendering of olmo_thinker_rlzero applied to the problem);
  - per-token lps (base64 float32) reproduce n_tok / mean_lp / sum_lp; base and own scored the same token count.
Summary: per group, base and own mean log-prob per token, the gap, and the share of items whose base mean lp lies
inside the 2.5-97.5 % range of the base's own correct solutions (Part A support criterion), under three control
definitions: base_own only (extension samples), base_own + pilot (AIME 2023), and base_own on other problems.
Writes out/ll_recount.json.
"""
import base64
import json
from collections import defaultdict

import numpy as np

import rv_core as R

LL = R.ART / "ll"
TEMPLATE_HEAD = ("Solve the following problem step by step. The last line of your response should be the answer to the "
                 "problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem.\n\n")
TEMPLATE_TAIL = "\n" + "\nRemember to put your answer on its own line after \"Answer:\""


def f32(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.float32)


def i32(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.int32).tolist()


def main():
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(R.Path.home() / "review/olmo-rlzero-pilot-rv/tok/base/tokenizer.json"))
    probs = R.problems(with_probe=False)
    groups = json.load(open(LL / "sel_groups.json"))
    items = {json.loads(l)["key"]: json.loads(l) for l in open(LL / "L_items_all.jsonl")}
    base = {json.loads(l)["key"]: json.loads(l) for l in open(LL / "L_scored_base_all.jsonl")}
    own = {}
    for m in ("step_2800", "step_0500"):
        for l in open(LL / f"L_scored_{m}_own.jsonl"):
            r = json.loads(l)
            own[r["key"]] = r
    # stored samples and my re-grade for every job referenced
    jobs = sorted({k.split("|")[0] for k in groups})
    sids, rl_ok = {}, {}
    for j in jobs:
        for s in R.samples(j):
            sids[f"{j}|{s['pid']}|{s['chunk']}|{s['i']}"] = s["ids"]
        for r in map(json.loads, open(R.OUT / f"regrade_{j}.jsonl")):
            rl_ok[f"{j}|{r['pid']}|{r['chunk']}|{r['i']}"] = r["rl"]
    bad = defaultdict(list)
    prompt_cache = {}
    rows = []
    for k, g in groups.items():
        it = items.get(k)
        if it is None:
            bad["no_item"].append(k)
            continue
        if it["resp_ids"] != sids.get(k):
            bad["resp_ids_mismatch"].append(k)
        if not rl_ok.get(k):
            bad["not_rl_correct"].append(k)
        pid = k.split("|")[1]
        if pid not in prompt_cache:
            txt = TEMPLATE_HEAD + probs[pid]["problem"] + TEMPLATE_TAIL
            prompt_cache[pid] = tok.encode(txt, add_special_tokens=False).ids
        if i32(it["prompt_ids"]) != prompt_cache[pid]:
            bad["prompt_ids_mismatch"].append(k)
        b = base.get(k)
        gen = it["model"]
        o = own.get(k) if gen != "base" else base.get(k)
        if b is None or o is None:
            bad["unscored"].append(k)
            continue
        lb, lo = f32(b["lps"]), f32(o["lps"])
        n = len(i32(it["resp_ids"]))
        if not (len(lb) == len(lo) == n == b["n_tok"] == o["n_tok"]):
            bad["len_mismatch"].append(k)
        if abs(float(lb.mean()) - b["mean_lp"]) > 1e-5 or abs(float(lo.mean()) - o["mean_lp"]) > 1e-5:
            bad["mean_mismatch"].append(k)
        rows.append({"key": k, "group": g, "gen": gen, "pid": pid, "n": n, "base": float(lb.mean()), "own": float(lo.mean()),
                     "base_sum": float(lb.sum()), "own_sum": float(lo.sum()),
                     "base_frac_lt_1e3": float((lb < np.log(1e-3)).mean())})
    print("integrity:", {k: len(v) for k, v in bad.items()}, "items checked:", len(groups), "scored rows:", len(rows))
    own_ctrl = [r for r in rows if r["group"] == "base_own"]
    pilot_ctrl = [r for r in rows if r["group"] == "base_own_pilot"]
    rng_a = np.percentile([r["base"] for r in own_ctrl], [2.5, 97.5])
    rng_b = np.percentile([r["base"] for r in own_ctrl + pilot_ctrl], [2.5, 97.5])
    out = {"integrity": {k: v[:5] + [len(v)] for k, v in bad.items()}, "range_base_own": list(rng_a),
           "range_base_own_plus_pilot": list(rng_b), "n_base_own": len(own_ctrl), "n_pilot": len(pilot_ctrl), "groups": {}}
    print(f"control ranges (base mean lp/token, 2.5-97.5 %): base_own n={len(own_ctrl)} {rng_a.round(3)}; "
          f"+pilot n={len(own_ctrl) + len(pilot_ctrl)} {rng_b.round(3)}")
    for g in ("late", "ckpt_other", "base_own", "base_own_pilot"):
        rr = [r for r in rows if r["group"] == g]
        if not rr:
            continue
        gap = np.array([r["own"] - r["base"] for r in rr])
        ins_a = np.mean([rng_a[0] <= r["base"] <= rng_a[1] for r in rr])
        ins_b = np.mean([rng_b[0] <= r["base"] <= rng_b[1] for r in rr])
        # leave-same-problem-out control range (base_own only, other problems)
        ins_c = []
        for r in rr:
            ctrl = [c["base"] for c in own_ctrl if c["pid"] != r["pid"]]
            lo_, hi_ = np.percentile(ctrl, [2.5, 97.5])
            ins_c.append(lo_ <= r["base"] <= hi_)
        by_gen = defaultdict(int)
        for r in rr:
            by_gen[r["gen"]] += 1
        d = {"n": len(rr), "n_problems": len({r["pid"] for r in rr}), "by_gen": dict(by_gen),
             "base_lp_median": float(np.median([r["base"] for r in rr])), "own_lp_median": float(np.median([r["own"] for r in rr])),
             "gap_median": float(np.median(gap)), "gap_p10": float(np.percentile(gap, 10)), "gap_p90": float(np.percentile(gap, 90)),
             "sum_gap_median": float(np.median([r["own_sum"] - r["base_sum"] for r in rr])),
             "inside_base_own": float(ins_a), "inside_base_own_plus_pilot": float(ins_b),
             "inside_other_problems": float(np.mean(ins_c)),
             "base_lp_min": float(min(r["base"] for r in rr)), "base_lp_max": float(max(r["base"] for r in rr))}
        out["groups"][g] = d
        print(f"  {g:14s} n={d['n']:3d} ({d['n_problems']} problems, {d['by_gen']}) base lp med {d['base_lp_median']:.3f} "
              f"own {d['own_lp_median']:.3f} gap med {d['gap_median']:.3f} [p10 {d['gap_p10']:.3f}, p90 {d['gap_p90']:.3f}] "
              f"sum-gap med {d['sum_gap_median']:.0f}; inside: own {ins_a:.2f} own+pilot {ins_b:.2f} other-problems {np.mean(ins_c):.2f}")
    # late group per generating model and below-range items
    late = [r for r in rows if r["group"] == "late"]
    below = [r for r in late if r["base"] < rng_b[0]]
    out["late_below_range_b"] = [(r["key"], round(r["base"], 3), round(r["own"], 3)) for r in below]
    print("late items below the own+pilot range:", out["late_below_range_b"])
    json.dump(out, open(R.OUT / "ll_recount.json", "w"), indent=1)


if __name__ == "__main__":
    main()
