"""Stage 0 recount from my re-grade: lengths (mean / median / p90), cuts, stop reasons, '</think>', IFEval strict on
the 40 Stage-0 IFEval prompts, the speculation A/B (s0_base_b vs s0_base_a) with prompt-paired bootstrap intervals,
and throughput from meta. Output: out/stage0.txt"""
import json
import os

import numpy as np

import rv_core as C


def load(job):
    return [json.loads(x) for x in open(os.path.join(C.OUT, "regrade", f"{job}.jsonl"))]


def main():
    lines = []
    R = {j: load(j) for j in ("s0_base_a", "s0_base_b", "s0_main", "s0_s0100", "s0_s0500")}
    for j, rows in R.items():
        nt = np.array([r["n_tok"] for r in rows])
        ife = [r for r in rows if r["task"] == "ifeval"]
        m = json.loads(open(os.path.join(C.ART, "meta", f"{j}.json")).readline())
        lines.append(f"{j:10s} n {len(rows):4d} mean {nt.mean():7.1f} median {np.median(nt):6.0f} p90 "
                     f"{np.percentile(nt, 90):7.0f} cut {sum(r['finish'] == 'length' for r in rows)} EOS "
                     f"{sum(r['eos_end'] for r in rows)} </think> {sum(r['think_end'] for r in rows)} IFEval strict "
                     f"{(sum(r['strict'] for r in ife) / len(ife)) if ife else float('nan'):.3f} ({len(ife)}) tok/s "
                     f"{m['tok_per_s']} spec {m['spec_ngram']}")
    a, b = R["s0_base_a"], R["s0_base_b"]
    pids = sorted({r["pid"] for r in a})
    rng = np.random.default_rng(0)
    A = {p: [r for r in a if r["pid"] == p] for p in pids}
    B = {p: [r for r in b if r["pid"] == p] for p in pids}
    dl, ds = [], []
    ife = [p for p in pids if A[p][0]["task"] == "ifeval"]
    for _ in range(10000):
        s = rng.choice(pids, len(pids))
        dl.append(np.mean([r["n_tok"] for p in s for r in B[p]]) - np.mean([r["n_tok"] for p in s for r in A[p]]))
        s2 = rng.choice(ife, len(ife))
        ds.append(np.mean([r["strict"] for p in s2 for r in B[p]]) - np.mean([r["strict"] for p in s2 for r in A[p]]))
    pl = np.mean([r["n_tok"] for r in b]) - np.mean([r["n_tok"] for r in a])
    ps = np.mean([r["strict"] for p in ife for r in B[p]]) - np.mean([r["strict"] for p in ife for r in A[p]])
    lines.append(f"A/B (spec - no spec): mean length {pl:+.0f} [{np.percentile(dl, 2.5):+.0f}, {np.percentile(dl, 97.5):+.0f}]"
                 f"; IFEval strict {ps:+.3f} [{np.percentile(ds, 2.5):+.3f}, {np.percentile(ds, 97.5):+.3f}] (prompt-paired "
                 f"bootstrap, 10,000)")
    ma = json.loads(open(os.path.join(C.ART, "meta", "s0_base_a.json")).readline())
    mb = json.loads(open(os.path.join(C.ART, "meta", "s0_base_b.json")).readline())
    lines.append(f"throughput ratio (job average) {mb['tok_per_s'] / ma['tok_per_s']:.3f}")
    open(os.path.join(C.OUT, "stage0.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
