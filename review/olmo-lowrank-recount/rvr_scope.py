"""Hand-gate scope from MY re-grade: per cell (job x reach prompt) the first min(strict, 8) strict successes in draw
order (chunk, i) -> out/scope.json (deciding draws), with counts per job and distinct answers per prompt."""
import gzip
import json
from collections import defaultdict

from rvr_core import ARMS, OUT, pids

JOBS = ARMS + ["B_s2300"]
LOOK = 8


def main():
    reach = pids("pids_reach.txt")
    R = set(reach)
    scope, cnt = [], {}
    for job in JOBS:
        rows = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
        by = defaultdict(list)
        for r in rows:
            if r["pid"] in R:
                by[r["pid"]].append(r)
        n_strict = n_dec = cells_with = 0
        for p in reach:
            xs = sorted(by[p], key=lambda r: (int(r["chunk"]), int(r["i"])))
            s = [r for r in xs if r["strict"]]
            n_strict += len(s)
            cells_with += bool(s)
            for r in s[:LOOK]:
                scope.append({"job": job, "pid": p, "chunk": int(r["chunk"]), "i": int(r["i"]), "ans_sha": r["ans_sha"],
                              "rank": s.index(r)})
                n_dec += 1
        cnt[job] = {"strict": n_strict, "deciding": n_dec, "cells_with_strict": cells_with}
    distinct = len({(d["pid"], d["ans_sha"]) for d in scope})
    json.dump({"scope": scope, "counts": cnt, "distinct_answers": distinct}, open(OUT / "scope.json", "w"), indent=1)
    for j, c in cnt.items():
        print(j, c)
    print("deciding draws", len(scope), "distinct (prompt, answer)", distinct)


if __name__ == "__main__":
    main()
