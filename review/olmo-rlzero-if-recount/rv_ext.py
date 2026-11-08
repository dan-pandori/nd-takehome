"""Extension / confirmation audit against the pre-registered stopping rule, from my grades.

Sequential jobs (stop_after 2, 2 chunks of 16 in flight): per pid, chunks in index order, my strict count per chunk
plus the job's prior (meta `prior` file), the chunk in which the count reached 2, and how many chunks were drawn after
it (allowed: at most 2 -- with 2 in flight, a later chunk can finish first and a third can be submitted before the
deciding one completes). A pid that stops below 2 strict before its requested n must be in the job's stop file
(budget stop). Cap: at most 256 draws per model per prompt over fixed + extension + confirmation jobs (diagnostics
apart). Output: out/ext.txt"""
import json
import os
from collections import Counter, defaultdict

import rv_core as C


def parse(spec, default=0):
    if not spec:
        return {}
    path = os.path.join(C.WS, spec[1:]) if spec.startswith("@") else None
    toks = open(path).read().split() if path else spec.split(",")
    out = {}
    for t in toks:
        p, _, n = t.partition(":")
        out[p] = int(n) if n else default
    return out


def main():
    lines = []
    rg = {}
    for fn in os.listdir(os.path.join(C.OUT, "regrade")):
        if fn.endswith(".jsonl"):
            rg[fn[:-6]] = [json.loads(x) for x in open(os.path.join(C.OUT, "regrade", fn))]
    for job in sorted(rg):
        mp = os.path.join(C.ART, "meta", f"{job}.json")
        if not os.path.exists(mp):
            continue
        m = json.loads(open(mp).readline())
        if not m.get("stop_after"):
            continue
        want = parse(m["pids"], 0)
        prior = parse(m.get("prior"), 0)
        stop = set(open(os.path.join(C.WS, m["stop_file"])).read().split()) if m.get("stop_file") else set()
        by = defaultdict(lambda: defaultdict(list))
        for r in rg[job]:
            by[r["pid"]][r["chunk"]].append(r["strict"])
        viol, stats = [], Counter()
        for p in sorted(set(by) | set(want)):
            chunks = by.get(p, {})
            idx = sorted(chunks)
            n_req = want.get(p, 0)
            if n_req == 0:  # pid list without counts: the job's --n
                n_req = 240
            full = all(len(chunks[c]) == 16 for c in idx)
            contiguous = idx == list(range(len(idx)))
            cum, reach = prior.get(p, 0), None
            for c in range(len(idx)):
                if c not in chunks:
                    break
                cum += sum(chunks[c])
                if cum >= 2 and reach is None:
                    reach = c
            after = (len(idx) - 1 - reach) if reach is not None else None
            drawn = 16 * len(idx)
            stats["pids"] += 1
            if reach is not None:
                stats["stopped_at_2"] += 1
                stats[f"overshoot_{after}"] += 1
                if after > 2:
                    viol.append(f"{p}: {after} chunks after the count reached 2 (chunk {reach})")
            elif drawn < n_req:
                if p in stop:
                    stats["budget_stop"] += 1
                else:
                    viol.append(f"{p}: stopped at {drawn} < {n_req} with count {cum} < 2 and not in the stop file")
            else:
                stats["ran_full"] += 1
            if not (full and contiguous):
                viol.append(f"{p}: chunks {idx} sizes {[len(chunks[c]) for c in idx]}")
        lines.append(f"{job}: prior {len(prior)} stop-file {len(stop)} | " + " ".join(f"{a}={b}" for a, b in sorted(stats.items())))
        lines += [f"   VIOLATION {v}" for v in viol] or ["   no violation"]
    # cap
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    over = [(mdl, p, len(v)) for mdl in ("base", "main", "s0100", "s0500") for p, v in cells[mdl].items() if len(v) > 256]
    lines.append(f"cap 256 per model per prompt (fixed + extension + confirmation): {len(over)} cells over: {over[:10]}")
    open(os.path.join(C.OUT, "ext.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
