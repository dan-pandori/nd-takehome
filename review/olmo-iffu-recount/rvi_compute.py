"""Compute record of run olmo-iffu, recounted: per job samples and generated tokens from the stored rows (my sums of
n_tok and of decoded id lengths), job GPU-seconds from the metas ((t_load_s + t_gen_s) x GPUs), pod hours and dollars
from the host's ~/podhours.log; then the run's registry rows compared with mine, job by job.
-> out/compute.txt, out/compute.json
"""
import collections
import gzip
import json
from pathlib import Path

import rvi_core as C

LINES = []


def say(s=""):
    LINES.append(s)
    print(s)


def main():
    res = {"jobs": {}}
    say("| job | pod | GPUs | samples | gen tokens (Σ n_tok) | Σ ids | meta gen_tokens | t_load s | t_gen s | GPU-s | tok/s (gen) |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    pod_of = {"T2_dpo": "iffu-a", "T2_s2300": "iffu-a", "T1_dpo": "iffu-a"}
    for job in C.JOBS:
        rows = [json.loads(ln) for ln in gzip.open(C.OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
        m = json.loads(open(C.ART / "meta" / f"{job}.json").read().strip().splitlines()[-1])
        ntok = sum(r["n_tok"] for r in rows)
        nids = sum(r["ids_len"] for r in rows)
        g = len(m["gpus"])
        gs = (m["t_load_s"] + m["t_gen_s"]) * g
        pod = pod_of.get(job, "iffu-b")
        res["jobs"][job] = {"samples": len(rows), "gen_tokens": ntok, "ids": nids, "meta_gen_tokens": m["gen_tokens"],
                            "t_load_s": m["t_load_s"], "t_gen_s": m["t_gen_s"], "gpus": g, "gpu": m["gpus"][0],
                            "gpu_seconds": round(gs, 1), "pod": pod, "seed": m["seed"]}
        say(f"| {job} | {pod} | {g} × {m['gpus'][0]} | {len(rows):,} | {ntok:,} | {nids:,} | {m['gen_tokens']:,} | "
            f"{m['t_load_s']} | {m['t_gen_s']} | {gs:,.0f} | {ntok / m['t_gen_s']:,.0f} |")
    tot = {k: sum(v[k] for v in res["jobs"].values()) for k in ("samples", "gen_tokens", "gpu_seconds")}
    say(f"| total | | | {tot['samples']:,} | {tot['gen_tokens']:,} | | | | | {tot['gpu_seconds']:,.0f} | |")
    res["total"] = tot
    # pod hours and dollars (host ledger)
    say("\nPods (~/podhours.log, last line per pod):")
    last = {}
    for ln in open(Path.home() / "podhours.log"):
        p = ln.split()
        if len(p) >= 5 and p[1] == "olmo-iffu":
            last[p[2]] = p
    usd = 0.0
    for pod, p in sorted(last.items()):
        h, d = float(p[3]), float(p[4])
        usd += d
        gpus = 2 if pod == "iffu-a" else 1
        say(f"   {pod}: {h:.4f} h, ${d:.2f} (${d / h:.2f}/h), {' '.join(p[5:])}; {gpus} GPU(s) -> {h * 3600 * gpus:,.0f} pod GPU-s")
        res.setdefault("pods", {})[pod] = {"hours": h, "usd": d, "gpus": gpus}
    say(f"   total ${usd:.2f}")
    # registry rows
    reg = [json.loads(ln) for f in sorted((C.RAW / "artifacts" / "olmo-iffu" / "registry").glob("*.jsonl"))
           for ln in open(f)]
    by = collections.defaultdict(dict)
    for r in reg:
        by[r["labels"].get("job")][r["metric"]] = r["value"]
    say(f"\nRegistry: {len(reg)} rows, jobs {sorted(k for k in by if k)}")
    diffs = []
    for job, v in res["jobs"].items():
        rj = by.get(job, {})
        cmp = {"attempts": v["samples"], "gen_tokens": v["gen_tokens"], "gpu_seconds": v["gpu_seconds"],
               "train_steps": 0, "train_tokens": 0, "lean_checks": 0}
        for k, mine in cmp.items():
            theirs = rj.get(k)
            if theirs is None or abs(float(theirs) - mine) > 0.5:
                diffs.append((job, k, theirs, mine))
        say(f"   {job}: registry {dict(sorted(rj.items()))}")
    say(f"   differences from my values: {diffs if diffs else 'none'}")
    C.dump(res, "compute.json")
    (C.OUT / "compute.txt").write_text("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
