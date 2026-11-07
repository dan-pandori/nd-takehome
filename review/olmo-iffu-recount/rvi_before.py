"""'Before' counts from olmo-ifomega's raw samples (bucket), re-graded with my driver: for the 43 IFBench hand-reach
prompts and the 6 IFEval reach prompts, per (model, prompt): draws and strict successes, with draw keys
(job, chunk, i) of every strict success. Streams each bucket file through `hf buckets cp <uri> -` (no local copy;
one file at a time). Only the files that hold IF samples of dpo / s2300 / s0750 are read.
-> out/before.json, out/before.txt
"""
import collections
import gzip
import io
import json
import subprocess

import rvi_core as C
import rvi_graders as G

BK = "hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/samples/"
FILES = ["F_dpo_ifb", "E1_dpo_if", "E1_dpo_ifa", "E2_dpo_ifa", "F_dpo_ife", "E1_dpo_ifev",
         "F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb", "E1_s2300_ifa", "F_s2300_ife", "C1_s2300_ifev",
         "E1_s2300_ifev", "F_s0750_ifb"]


def main():
    prov = json.load(open(C.OUT / "provenance.json"))
    want = set(prov["r43"]) | {"ifeval_2350", "ifeval_2447", "ifeval_3478", "ifeval_1314", "ifeval_2247", "ifeval_2563"}
    ifb, ife = C.upstream_ifbench(), C.upstream_ifeval()
    draws = collections.Counter()
    succ = collections.defaultdict(list)
    seen = collections.defaultdict(set)
    files = {}
    for name in FILES:
        p = subprocess.Popen(["hf", "buckets", "cp", BK + name + ".jsonl.gz", "-"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        n = nrel = 0
        trunc = False
        try:
            with gzip.open(io.BufferedReader(p.stdout), "rt", encoding="utf-8") as f:
                for ln in f:
                    try:
                        r = json.loads(ln)
                    except json.JSONDecodeError:
                        trunc = True
                        break
                    n += 1
                    pid = r["pid"]
                    if pid not in want:
                        continue
                    key = (r["model"], pid)
                    dk = (r["job"], r["chunk"], r["i"])
                    if dk in seen[key]:
                        continue  # a resumed job can repeat a chunk; count each draw once
                    seen[key].add(dk)
                    nrel += 1
                    draws[key] += 1
                    task, num = pid.split("_")
                    rec = (ifb if task == "ifbench" else ife)[num]
                    s, _, _ = G.if_grade(task, rec, C.answer_of(r["text"]))
                    if s:
                        succ[key].append(list(dk))
        except (EOFError, OSError):
            trunc = True
        p.wait()
        files[name] = {"rows": n, "relevant": nrel, "truncated": trunc, "rc": p.returncode}
        print(name, files[name], flush=True)
    out = {"files": files, "cells": {f"{m}|{pid}": {"draws": draws[(m, pid)], "strict": len(succ[(m, pid)]),
                                                     "succ": succ[(m, pid)]}
                                     for (m, pid) in sorted(draws)}}
    C.dump(out, "before.json")
    lines = [f"{k}: {v['draws']} draws, {v['strict']} strict" for k, v in out["cells"].items()]
    (C.OUT / "before.txt").write_text(json.dumps(files, indent=1) + "\n" + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
