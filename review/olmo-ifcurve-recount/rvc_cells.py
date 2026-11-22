"""Cells of run olmo-ifcurve, built by the reviewer from the pre-registration's reuse table and amendments 1-5
(my own implementation; the executor's cells.py is not imported). A cell is an ordered list of draw keys
(job, pid, chunk, i): source order as listed in the pre-registration, then chunk, then index; a cell's n draws are
the first n in that order.

Arm A (218 IFBench prompts): dpo F_dpo_ifb (all 16); s0100 / s0750 / s2300 F_*_ifb (8); s0050 / s0200 M job, 4
(chunk 0; the 42 IFBench reach prompts: the first 4 of their 32); s0500 M_s0500 chunk 0 + T_s0500 chunk 0 (reach: the
first 8 of 32; amendment 5); s1100 / s1600 M job, 8.
Arm B base (48 reach prompts x 32): s0100 IFBench F_s0100_ifb 8 + B_s0100 24, IFEval B_s0100 32; s0750 IFBench
T4_s0750 chunk 0 (16), then chunk 1 from T4_s0750 or T4b_s0750, else B_s0750 16; IFEval B_s0750 32; s2300 B_s2300;
s0050 / s0200 / s0500 / s1100 / s1600 the M job's 32. Extension: the base 32 + every X / X2 / X3 / X4 draw at the
same checkpoint (in that job order).
Writes out/cells.json (keys) and out/cells.txt (structure checks: sizes, sources, duplicate-ids test).
"""
import collections
import gzip
import json

from rvc_core import ALL_JOBS, OUT, STEP, Tee, dump, load_csv, RAW, CODE

CK = ["s0050", "s0100", "s0200", "s0500", "s0750", "s1100", "s1600", "s2300"]  # sampled RL checkpoints (s0350 cancelled)
CKA = ["dpo"] + CK


def load_rows():
    rows = {}
    for job in ALL_JOBS:
        with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                rows[(job, r["pid"], int(r["chunk"]), int(r["i"]))] = r
    return rows


def by_job_pid(rows):
    d = collections.defaultdict(list)
    for k in rows:
        d[(k[0], k[1])].append(k)
    for v in d.values():
        v.sort(key=lambda k: (k[2], k[3]))
    return d


def build():
    rows = load_rows()
    J = by_job_pid(rows)
    armA = open(CODE / "pids_armA.txt").read().split()
    reach = [r["pid"] for r in load_csv(RAW / "olmo_ifladder" / "classify.csv")]
    rset = set(reach)
    ckjob = {"s0050": "M_s0050", "s0200": "M_s0200", "s0500": "M_s0500", "s1100": "M_s1100", "s1600": "M_s1600"}
    A = {c: {} for c in CKA}
    for p in armA:
        A["dpo"][p] = J[("F_dpo_ifb", p)][:16]
        for c, j in (("s0100", "F_s0100_ifb"), ("s0750", "F_s0750_ifb"), ("s2300", "F_s2300_ifb")):
            A[c][p] = J[(j, p)][:8]
        for c in ("s0050", "s0200"):
            A[c][p] = J[(ckjob[c], p)][:4]
        if p in rset:
            A["s0500"][p] = J[("M_s0500", p)][:8]
        else:
            A["s0500"][p] = [k for k in J[("M_s0500", p)] if k[2] == 0] + J[("T_s0500", p)][:4]
        for c in ("s1100", "s1600"):
            A[c][p] = J[(ckjob[c], p)][:8]
    B = {c: {} for c in CK}
    for p in reach:
        ifb = p.startswith("ifbench")
        for c in ("s0050", "s0200", "s0500", "s1100", "s1600"):
            B[c][p] = J[(ckjob[c], p)][:32]
        B["s0100"][p] = ((J[("F_s0100_ifb", p)][:8] if ifb else []) + J[("B_s0100", p)])[:32]
        B["s2300"][p] = J[("B_s2300", p)][:32]
        if ifb:
            t4 = J[("T4_s0750", p)]
            c0 = [k for k in t4 if k[2] == 0]
            c1 = [k for k in t4 if k[2] == 1] or [k for k in J[("T4b_s0750", p)] if k[2] == 1]
            if len(c1) < 16:
                c1 = J[("B_s0750", p)][:16]
            B["s0750"][p] = (c0 + c1)[:32]
        else:
            B["s0750"][p] = J[("B_s0750", p)][:32]
    X = {}
    for (job, p), ks in J.items():
        if job.startswith("X"):
            c = rows[ks[0]]["model"]
            X.setdefault(p, {}).setdefault(c, []).append((job, ks))
    XC = {}
    order = {"X": 0, "X2": 1, "X3": 2, "X4": 3}
    for p, d in X.items():
        for c, lst in d.items():
            lst.sort(key=lambda t: order[t[0].split("_")[0]])
            XC.setdefault(p, {})[c] = B[c][p] + [k for _, ks in lst for k in ks]
    return rows, armA, reach, A, B, XC, J


def main():
    P = Tee("cells.txt")  # inside main: other scripts import build()
    rows, armA, reach, A, B, XC, J = build()
    P("arm A cell sizes per checkpoint (Counter of n):")
    for c in CKA:
        P(f"   {c}: {dict(collections.Counter(len(v) for v in A[c].values()))}  sources "
          f"{dict(collections.Counter(k[0] for v in A[c].values() for k in v))}")
    P("arm B base cell sizes per checkpoint:")
    for c in CK:
        P(f"   {c}: {dict(collections.Counter(len(v) for v in B[c].values()))}  sources "
          f"{dict(collections.Counter(k[0] for v in B[c].values() for k in v))}")
    t4one = sorted(p for p in reach if p.startswith("ifbench") and any(k[0] == "B_s0750" for k in B["s0750"][p]))
    P(f"s0750 IFBench reach prompts filled from B_s0750: {len(t4one)}: {t4one}")
    t4b = sorted(p for p in reach if any(k[0] == "T4b_s0750" for k in B["s0750"][p]))
    P(f"   ... taking T4b_s0750's chunk 1: {t4b}")
    unused_t4 = collections.Counter(k[2] for p in reach for k in J.get(("T4_s0750", p), []) if k not in set(B["s0750"][p]))
    P(f"   T4_s0750 draws on reach prompts not used (by chunk): {dict(unused_t4)}")
    P(f"extension cells: prompts with one {sum(len(v) == 1 for v in XC.values())}, with more than one "
      f"{[p for p, v in XC.items() if len(v) > 1]}; prompts without {sorted(set(reach) - set(XC))}")
    P(f"   extension cell sizes: {dict(collections.Counter(len(v) for d in XC.values() for v in d.values()))}; "
      f"by checkpoint {dict(collections.Counter(c for d in XC.values() for c in d))}")
    # duplicate response ids inside any (checkpoint, pid) across all jobs
    seen = collections.defaultdict(list)
    for k, r in rows.items():
        seen[(r["model"], r["pid"], r["ids_sha"])].append(k)
    dups = {str(k): v for k, v in seen.items() if len(v) > 1}
    P(f"identical response-id sequences within a (checkpoint, prompt) across all jobs: {len(dups)} {list(dups.items())[:3]}")
    dump({"A": {c: {p: v for p, v in d.items()} for c, d in A.items()},
          "B": {c: {p: v for p, v in d.items()} for c, d in B.items()},
          "X": XC, "armA": armA, "reach": reach}, "cells.json")


if __name__ == "__main__":
    main()
