"""Compare my re-grade (out/regrade/<job>.jsonl.gz) with the grade files the run used (artifacts/<run>/graded/<job>.jsonl),
row by row on (pid, chunk, i); per job and prompt set: draws, my strict, cut (finish = length), decode check, rows
without '</think>', rows with more than one '</think>'. -> out/gradecmp.json + stdout."""
import gzip
import json
from collections import Counter

from rvr_core import ALL_JOBS, OUT, RAW, Tee, load_jsonl, pids

GRADED = {"B_s2300": RAW / "artifacts/olmo_ifcurve/graded/B_s2300.jsonl",
          "F_s2300_ifb": RAW / "artifacts/olmo_ifomega/graded/F_s2300_ifb.jsonl",
          "F_dpo_ifb": RAW / "artifacts/olmo_ifomega/graded/F_dpo_ifb.jsonl"}


def mine(job):
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        return [json.loads(ln) for ln in f]


def main():
    T = Tee("gradecmp.txt")
    reach, armA = set(pids("pids_reach.txt")), set(pids("pids_armA.txt"))
    others = armA - reach
    res = {}
    for job in ALL_JOBS:
        M = mine(job)
        G = {(g["pid"], int(g["chunk"]), int(g["i"])): g for g in load_jsonl(GRADED.get(job, RAW / f"artifacts/olmo_lowrank/graded/{job}.jsonl"))}
        keys = [(r["pid"], int(r["chunk"]), int(r["i"])) for r in M]
        dup = sum(v - 1 for v in Counter(keys).values() if v > 1)
        dis = [(k, r["strict"], G[k]["strict"]) for k, r in zip(keys, M) if k in G and bool(G[k]["strict"]) != bool(r["strict"])]
        dis_l = sum(1 for k, r in zip(keys, M) if k in G and bool(G[k].get("loose")) != bool(r["loose"]))
        miss = sum(1 for k in keys if k not in G)
        extra = len(set(G) - set(keys))
        row = {"rows": len(M), "dup_keys": dup, "graded_missing": miss, "graded_extra": extra,
               "strict_disagree": len(dis), "loose_disagree": dis_l, "examples": dis[:5]}
        for nm, S in (("reach", reach), ("others", others), ("armA", armA)):
            xs = [r for r in M if r["pid"] in S]
            row[nm] = {"prompts": len({r["pid"] for r in xs}), "draws": len(xs), "strict": sum(bool(r["strict"]) for r in xs),
                       "cut": sum(r["finish"] == "length" for r in xs), "dec_bad": sum(not r["dec_ok"] for r in xs),
                       "no_close": sum(r["ans_none"] for r in xs), "multi_close": sum(r["n_close"] > 1 for r in xs),
                       "draws_per_prompt": sorted(Counter(Counter(r["pid"] for r in xs).values()).items())}
        res[job] = row
        T(f"{job:12s} rows {len(M):5d} dup {dup} miss {miss} extra {extra} strict_dis {len(dis)} loose_dis {dis_l} | "
          + " | ".join(f"{nm}: P{row[nm]['prompts']} n{row[nm]['draws']} s{row[nm]['strict']} cut{row[nm]['cut']} "
                       f"dec_bad{row[nm]['dec_bad']} noclose{row[nm]['no_close']} multi{row[nm]['multi_close']} {row[nm]['draws_per_prompt']}"
                       for nm in ("reach", "others")))
    json.dump(res, open(OUT / "gradecmp.json", "w"), indent=1)


if __name__ == "__main__":
    main()
