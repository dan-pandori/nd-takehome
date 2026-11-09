#!/usr/bin/env python3
"""Results of run olmo-ifladder (pre-registration preregistration/olmo-ifladder.md, Readings). VPS-side, standard library.

  python3 olmo_ifladder/analyze.py
    -> olmo_ifladder/results.csv    one row per job x prompt: draws, strict, loose, length cut, tokens, thinking tokens
                                    (through `</think>`), answer words, and the hand gate's cell state (gate.py)
    -> olmo_ifladder/classify.csv   one row per reach prompt: elicited at each rung / LoRA, the reading, flags
    -> olmo_ifladder/summary.json   counts (overall, by family), gamed shares, calibration, lengths
Rung 1 (reach) is olmo-iffu's status (olmo_iffu/status.csv); every other cell is this run's (job names: R1cal_dpo,
R{2,3,4}_dpo, R{2,3,4}_s2300, Lchk_{main,ctrl}, Leval_{main,ctrl}; S0* jobs are stage-0 measurements, not read).
"""
import base64
import csv
import gzip
import json
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

import importlib.util

A = Path("artifacts/olmo_ifladder")
O = Path("olmo_ifladder")
_spec = importlib.util.spec_from_file_location("gate", O / "gate.py")
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

JOBS = ["R1cal_dpo", "R2_dpo", "R3_dpo", "R4_dpo", "R2_s2300", "R3_s2300", "R4_s2300",
        "Lchk_main", "Lchk_ctrl", "Leval_main", "Leval_ctrl"]
END = (524, 27963)  # `</` `think` (olmo-transplant: Olmo 3's </think> is three ordinary tokens)


def think_tokens(b64):
    ids = base64.b64decode(b64)
    import array
    a = array.array("i")
    a.frombytes(ids)
    for k in range(len(a) - 2, -1, -1):
        if a[k] == END[0] and a[k + 1] == END[1]:
            return k + 3
    return None


def per_job(job):
    rows = defaultdict(list)
    f = A / "samples" / f"{job}.jsonl.gz"
    if not f.exists():
        return None
    grades = {}
    for ln in open(A / "graded" / f"{job}.jsonl"):
        r = json.loads(ln)
        grades[(r["pid"], r["chunk"], r["i"])] = r
    with gzip.open(f, "rt") as g:
        for ln in g:
            r = json.loads(ln)
            gr = grades.get((r["pid"], r["chunk"], r["i"]))
            ans = gate.answer_of(r["text"])
            rows[r["pid"]].append({"n_tok": r["n_tok"], "finish": r["finish"], "think": think_tokens(r["ids"]),
                                   "words": len(ans.split()) if ans is not None else None,
                                   "strict": bool(gr and gr["strict"]), "loose": bool(gr and gr["loose"])})
    return rows


def fisher_greater(a, n1, b, n2):
    """One-sided Fisher exact p for 'rate 1 > rate 2' (a of n1 vs b of n2), hypergeometric tail, standard library."""
    from math import comb
    k, n = a + b, n1 + n2
    tot = comb(n, k)
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(k, n1) + 1)) / tot


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def main():
    prompts = {r["pid"]: r for r in csv.DictReader(open(O / "prompts.csv"))}
    reach = [p for p, r in prompts.items() if r["set"] == "reach"]
    have = [j for j in JOBS if (A / "graded" / f"{j}.jsonl").exists()]
    cells, _, _ = gate.walk([j for j in have if j != "R1cal_dpo" and not j.startswith("Lchk")])
    cell = {(c["job"], c["pid"]): c for c in cells}
    out = []
    for j in have:
        rows = per_job(j)
        for pid, rs in sorted(rows.items()):
            c = cell.get((j, pid), {})
            out.append({"job": j, "pid": pid, "set": prompts.get(pid, {}).get("set", "heldout"), "draws": len(rs),
                        "strict": sum(r["strict"] for r in rs), "loose": sum(r["loose"] for r in rs),
                        "cut": sum(r["finish"] == "length" for r in rs),
                        "tok_mean": round(st.mean(r["n_tok"] for r in rs)),
                        "think_median": med([r["think"] for r in rs]), "words_median": med([r["words"] for r in rs]),
                        "genuine": c.get("genuine", 0 if pid in reach else ""), "gate": c.get("status", "no strict success" if pid in reach else ""),
                        "first4_read": c.get("first4_read", ""), "first4_gamed": c.get("first4_gamed", "")})
    with open(O / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    res = {(r["job"], r["pid"]): r for r in out}

    def state(job, pid):
        r = res.get((job, pid))
        if r is None:
            return "not run"
        if r["gate"] == "open":
            return "open"
        return "elicited" if r["gate"] == "elicited" else "no"

    cls = []
    for pid in reach:
        p = prompts[pid]
        r1 = "elicited" if p["r1_elicited"] == "True" else "no"
        s = {"R1": r1, "R2": state("R2_dpo", pid), "R3": state("R3_dpo", pid), "R4": state("R4_dpo", pid),
             "main": state("Leval_main", pid), "ctrl": state("Leval_ctrl", pid)}
        first = next((k for k in ("R1", "R2", "R3", "R4") if s[k] == "elicited"), None)
        undecided = any(v == "open" for v in s.values())
        if first:
            reading = f"prompt-elicitable at rung {first[1]}"
        elif s["main"] == "elicited" and s["ctrl"] == "elicited":
            reading = "teachable by any light fine-tune"
        elif s["main"] == "elicited":
            reading = "teachable from RL's trajectories"
        elif s["ctrl"] == "elicited":
            reading = "control LoRA only"
        else:
            reading = "neither"
        if undecided and reading in ("neither",) or any(v == "not run" for v in (s["R2"], s["main"], s["ctrl"])):
            reading += " (provisional)"
        breaks = [k for k in ("R2", "R3", "R4") if state(f"{k}_s2300", pid) == "no"]
        est = {}
        for arm in ("main", "ctrl"):
            rr = res.get((f"Leval_{arm}", pid))
            c = cell.get((f"Leval_{arm}", pid), {})
            lab = int(c.get("labelled", 0) or 0)
            est[arm] = round(rr["strict"] * int(c.get("genuine", 0)) / lab) if (rr and lab) else 0
        fp = fisher_greater(est["main"], 64, est["ctrl"], 64)
        cls.append({"pid": pid, "family": p["family"], "binding": p["binding"], "drop60": p["drop60"],
                    **{k: v for k, v in s.items()}, "reading": reading,
                    "t3_survivor": p["t3_1024"] == "0/1024", "r1_breaks_s2300": "breaks" in p["r1_label"],
                    "rungs_breaking_s2300": " ".join(breaks),
                    "est_genuine_main": est["main"], "est_genuine_ctrl": est["ctrl"], "fisher_p_main_gt_ctrl": f"{fp:.2g}",
                    **{f"g_{k}": (res.get((j, pid)) or {}).get("genuine", "") for k, j in
                       (("R2", "R2_dpo"), ("R3", "R3_dpo"), ("R4", "R4_dpo"), ("main", "Leval_main"), ("ctrl", "Leval_ctrl"))}})
    with open(O / "classify.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cls[0]))
        w.writeheader()
        w.writerows(cls)
    summ = {"readings": Counter(c["reading"] for c in cls),
            "teachable_rl_fisher_lt_0.05": sum(1 for c in cls if c["reading"].startswith("teachable from RL")
                                               and float(c["fisher_p_main_gt_ctrl"]) < 0.05),
            "by_family": {fam: Counter(c["reading"] for c in cls if c["family"] == fam) for fam in sorted({c["family"] for c in cls})},
            "neither_t3_survivors": [c["pid"] for c in cls if c["reading"].startswith("neither") and c["t3_survivor"]],
            "four_1024_hint": {pid: {k: next(c for c in cls if c["pid"] == pid)[k] for k in ("R1", "R2", "R3", "R4", "main", "ctrl")}
                               for pid in ("ifbench_78", "ifbench_133", "ifbench_252", "ifbench_253")}}
    gs = {}
    for j in have:
        rr = [r for r in out if r["job"] == j and r["set"] == "reach" and r["first4_read"] not in ("", 0)]
        n = sum(int(r["first4_read"]) for r in rr)
        g = sum(int(r["first4_gamed"]) for r in rr)
        gs[j] = {"read": n, "gamed": g, "share": round(g / n, 3) if n else None}
    summ["gamed_share_first4"] = gs
    cal = {}
    for j in have:
        rr = [r for r in out if r["job"] == j and r["set"] == "calib"]
        if rr:
            cal[j] = {"mean_strict": round(st.mean(r["strict"] / r["draws"] for r in rr), 3),
                      "per_prompt": {r["pid"]: f"{r['strict']}/{r['draws']}" for r in rr}}
    summ["calibration"] = cal
    summ["lengths_reach"] = {j: {"think_median_of_medians": med([r["think_median"] for r in out if r["job"] == j and r["set"] == "reach"]),
                                 "words_median_of_medians": med([r["words_median"] for r in out if r["job"] == j and r["set"] == "reach"])}
                             for j in have}
    json.dump(summ, open(O / "summary.json", "w"), indent=1, default=dict)
    print(json.dumps({"readings": summ["readings"], "gamed": gs}, default=dict))


if __name__ == "__main__":
    sys.exit(main())
