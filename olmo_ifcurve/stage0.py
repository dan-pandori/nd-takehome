#!/usr/bin/env python3
"""Stage 0 of run olmo-ifcurve: tokens per draw, cut share and throughput at s0050 / s1600, and the re-costed core
(pre-registration "Stage 0"). VPS-side, standard library only. Reads artifacts/olmo_ifcurve/meta/M_<c>_stage0.json,
the stage-0 rows (cells.py rows M_s0050 M_s1600, built from the stage-0 pull) and the stored jobs' rows.

  stage0.py [--rate 3.59] [--overhead 8]   -> artifacts/olmo_ifcurve/meta/stage0_projection.json + a table on stdout

Tokens per draw at unsampled checkpoints: piecewise-linear in step between the measured means (stage 0 at 50 / 1,600;
the stored fixed phase at 100 / 750 / 2,300 for arm A; arm B's reach stratum scaled by the reach / non-reach ratio
measured at 50, 750 and 1,600). Throughput: the stage-0 job averages and the stored fixed-phase job averages (1,780-1,930
tok/s on one H200); the projection uses the lower of the stage-0 and stored medians.
"""
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells  # noqa: E402

M = cells.A / "meta"


def mean_tok(rows):
    return st.mean(r["n_tok"] for r in rows) if rows else None


def interp(points, x):
    xs = sorted(points)
    if x <= xs[0]:
        return points[xs[0]]
    for a, b in zip(xs, xs[1:]):
        if a <= x <= b:
            return points[a] + (points[b] - points[a]) * (x - a) / (b - a)
    return points[xs[-1]]


def main():
    rate = float(sys.argv[sys.argv.index("--rate") + 1]) if "--rate" in sys.argv else 3.59
    overhead = float(sys.argv[sys.argv.index("--overhead") + 1]) if "--overhead" in sys.argv else 8.0
    R, AA = set(cells.reach()), cells.armA()
    nonreach = [p for p in AA if p not in R]
    out = {"rate_usd_per_h": rate, "measured": {}}
    tokA, tokB, tps = {}, {}, []
    for c, job in (("s0050", "M_s0050"), ("s1600", "M_s1600")):
        rs = cells.rows(job)
        a = [r for r in rs if r["pid"] not in R]
        b = [r for r in rs if r["pid"] in R]
        metas = [json.loads(ln) for ln in open(M / f"{job}_stage0.json")] if (M / f"{job}_stage0.json").exists() else []
        mt = metas[-1] if metas else {}
        tokA[cells.STEP[c]], tokB[cells.STEP[c]] = mean_tok(a), mean_tok(b)
        if mt.get("tok_per_s"):
            tps.append(mt["tok_per_s"])
        out["measured"][c] = {"draws": len(rs), "nonreach_draws": len(a), "reach_draws": len(b),
                              "tok_mean_nonreach": tokA[cells.STEP[c]], "tok_mean_reach": tokB[cells.STEP[c]],
                              "tok_q90_all": sorted(r["n_tok"] for r in rs)[int(0.9 * len(rs))] if rs else None,
                              "cut": sum(r["finish"] == "length" for r in rs), "no_think_end": sum(1 - r["think_end"] for r in rs),
                              "tok_per_s_job": mt.get("tok_per_s"), "t_gen_s": mt.get("t_gen_s"), "t_load_s": mt.get("t_load_s"),
                              "kv_cache": mt.get("kv_cache")}
    # stored points (arm A non-reach and reach strata)
    for c, job in (("s0100", "F_s0100_ifb"), ("s0750", "F_s0750_ifb"), ("s2300", "F_s2300_ifb")):
        rs = [r for r in cells.rows(job) if r["pid"] in set(AA)]
        tokA[cells.STEP[c]] = mean_tok([r for r in rs if r["pid"] not in R])
        rb = [r for r in rs if r["pid"] in R]
        if c == "s0750":
            rb = rb + [r for j in ("T4_s0750", "T4b_s0750") for r in cells.rows(j) if r["pid"] in R]
        tokB[cells.STEP[c]] = mean_tok(rb)
    stored_tps = [1933.6, 1827.9, 1781.3, 1894.9]  # F_s0100_ifb, F_s0750_ifb, F_s2300_ifb, F_dpo_ifb metas
    tp = min(st.median(tps) if tps else 1e9, st.median(stored_tps))
    out["tok_per_draw"] = {"nonreach": tokA, "reach": tokB}
    out["tok_per_s_used"] = tp
    jobs = []
    for c in cells.NEW:
        s = cells.STEP[c]
        jobs.append((f"M_{c}", 176 * 8 * interp(tokA, s) + 48 * 32 * interp(tokB, s)))
    jobs.append(("B_s0100", 1200 * interp(tokB, 100)))
    jobs.append(("B_s0750", 464 * interp(tokB, 750)))
    jobs.append(("B_s2300", 1536 * interp(tokB, 2300)))
    # extension: ~44 prompts x 96 draws at the checkpoint before first genuine (assume the median such step ~ 350)
    jobs.append(("X_all", 44 * 96 * interp(tokB, 350)))
    rows, total = [], 0.0
    for j, tok in jobs:
        h = tok / tp / 3600
        usd = h * rate
        total += usd
        rows.append({"job": j, "Mtok": round(tok / 1e6, 2), "gpu_h": round(h, 2), "usd": round(usd, 2)})
    out["jobs"] = rows
    out["overhead_usd"] = overhead
    out["core_total_usd"] = round(total + overhead, 2)
    (M / "stage0_projection.json").write_text(json.dumps(out, indent=1))
    for c, m in out["measured"].items():
        print(c, {k: (round(v) if isinstance(v, float) else v) for k, v in m.items() if k != "kv_cache"})
    print("tok/draw nonreach", {k: round(v) for k, v in sorted(tokA.items()) if v},
          "reach", {k: round(v) for k, v in sorted(tokB.items()) if v}, "tok/s used", round(tp))
    for r in rows:
        print(r)
    print(f"core total incl. ${overhead} overhead: ${out['core_total_usd']}")


if __name__ == "__main__":
    main()
