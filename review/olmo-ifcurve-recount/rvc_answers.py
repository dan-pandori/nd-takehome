"""Cache the answers of every strict success the hand gate can touch (arm-B base and extension cells of the 48 reach
prompts, and every arm-A strict success), keyed by draw key: out/answers.json.gz {json(key): answer}.
Also out/strict_lists.json: arm-B base / extension strict lists in draw order, and the arm-C sample (my implementation
of the pre-registered rule: per checkpoint, random.Random(4640 + step).sample of min(40, n) of the arm-A strict
successes, the population sorted by draw key (job, pid, chunk, i)).
"""
import gzip
import json
import random

from rvc_cells import CK, CKA, build
from rvc_core import OUT, STEP, answer_of, iter_job


def main():
    rows, armA, reach, A, B, XC, J = build()
    strict = lambda ks: [tuple(k) for k in ks if rows[tuple(k)]["strict"]]
    SL = {"B": {c: {p: strict(B[c][p]) for p in reach} for c in CK},
          "X": {p: {c: strict(ks[32:]) for c, ks in d.items()} for p, d in XC.items()}}
    armc = {}
    for c in CKA:
        pop = sorted(tuple(k) for p in armA for k in A[c][p] if rows[tuple(k)]["strict"])
        armc[c] = random.Random(4640 + STEP[c]).sample(pop, min(40, len(pop)))
    SL["C"] = armc
    want = set()
    for c in CK:
        for p in reach:
            want |= set(SL["B"][c][p])
    for p, d in SL["X"].items():
        for c, ks in d.items():
            want |= set(ks)
    for c in CKA:
        for p in armA:
            want |= set(strict(A[c][p]))
    jobs = {k[0] for k in want}
    ans = {}
    for job in sorted(jobs):
        for r in iter_job(job):
            k = (job, r["pid"], int(r["chunk"]), int(r["i"]))
            if k in want:
                ans[json.dumps(list(k))] = answer_of(r["text"])
    with gzip.open(OUT / "answers.json.gz", "wt") as f:
        json.dump(ans, f)
    ser = lambda v: [list(k) for k in v]
    json.dump({"B": {c: {p: ser(v) for p, v in d.items()} for c, d in SL["B"].items()},
               "X": {p: {c: ser(v) for c, v in d.items()} for p, d in SL["X"].items()},
               "C": {c: ser(v) for c, v in SL["C"].items()}}, open(OUT / "strict_lists.json", "w"))
    print("answers cached:", len(ans), "of", len(want))


if __name__ == "__main__":
    main()
