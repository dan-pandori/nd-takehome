#!/usr/bin/env python3
"""Stage 0, SVD part (pod): time and accuracy of full and randomized SVDs on one 32B MLP matrix (gate_proj) and one
attention matrix (q_proj) of D = W_s2300 - W_dpo (layer 32), plus two noise-like test matrices of each shape (the
matched-norm rounding floor of D, floor B, and a Gaussian). Reference = float64 singular values (cuSOLVER SVD).
Picks the cheapest (p, q) whose randomized top-k shares are within 2 % (k <= 64) / 5 % (k = 256) of the reference
and whose sigma_1 is within 0.1 % on every test matrix, and projects the time per 448-matrix change.

  stage0_svd.py --dpo D --rl D --out J.json [--layer 32]
"""
import argparse
import json
import os
import sys
import time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linalg  # noqa: E402
from ckpt import Ckpt  # noqa: E402

GRID = [(64, 4), (64, 8), (64, 16), (256, 4), (256, 8), (256, 16)]


def timed(f, reps=1):
    torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(reps):
        r = f()
    torch.cuda.synchronize()
    return r, (time.time() - t0) / reps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpo", required=True)
    ap.add_argument("--rl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layer", type=int, default=32)
    a = ap.parse_args()
    linalg.precision()
    dev = "cuda"
    P, R = Ckpt(a.dpo), Ckpt(a.rl)
    rep = {"gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "layer": a.layer, "tests": []}
    for t, grp in (("gate_proj", "mlp"), ("q_proj", "self_attn")):
        name = f"model.layers.{a.layer}.{grp}.{t}.weight"
        W0 = P.get(name, dev)
        D = R.get(name, dev).float() - W0.float()
        n2 = linalg.norm2(D)
        FB, s, n2b = linalg.floor_matrix(W0, n2, ("stage0", name))
        G = linalg.gaussian(D.shape, ("stage0", name), dev)
        tests = {"D": D, "floorB": FB, "gauss": G}
        # timings of the full methods on D
        _, t_svd32 = timed(lambda: torch.linalg.svd(D, full_matrices=False))
        _, t_svd64 = timed(lambda: linalg.full_svals(D, "svd"))
        _, t_gram64 = timed(lambda: linalg.full_svals(D, "gram"))
        _, t_floor = timed(lambda: linalg.floor_matrix(W0, n2, ("stage0", name)))
        base = {"name": name, "shape": list(D.shape), "norm2_D": n2, "floorB_s": s, "floorB_n2": n2b,
                "t_svd_fp32_full": round(t_svd32, 3), "t_svdvals_fp64": round(t_svd64, 3),
                "t_gram_eigvalsh_fp64": round(t_gram64, 3), "t_floor_calibration": round(t_floor, 3)}
        for tn, M in tests.items():
            m2 = linalg.norm2(M)
            ref = linalg.full_svals(M, "svd")
            ref_g = linalg.full_svals(M, "gram")
            ref_sh = linalg.shares(ref, m2)
            row = dict(base, test=tn, ref_shares=ref_sh, sigma1=float(ref[0]), sigma256=float(ref[255]),
                       gram_vs_svd_max_rel=float(((ref_g[:256] - ref[:256]).abs() / ref[:256]).max()),
                       grid=[])
            for p, q in GRID:
                (U, S, V), dt = timed(lambda: linalg.rsvd(M, k=256, p=p, q=q, seed=linalg.seed_of("s0", name, tn)))
                sh = linalg.shares(S, m2)
                err = {k: abs(sh[k] / ref_sh[k] - 1.0) for k in linalg.KS}
                row["grid"].append({"p": p, "q": q, "seconds": round(dt, 4),
                                    "sigma1_rel_err": abs(float(S[0]) / float(ref[0]) - 1.0),
                                    "sigma256_rel_err": abs(float(S[255]) / float(ref[255]) - 1.0),
                                    "share_rel_err": err})
            rep["tests"].append(row)
            print(json.dumps({k: row[k] for k in ("name", "test", "sigma1", "sigma256")}), flush=True)
            for g in row["grid"]:
                print("  p", g["p"], "q", g["q"], "s", g["seconds"], "s1err %.1e" % g["sigma1_rel_err"],
                      "s256err %.1e" % g["sigma256_rel_err"],
                      "share err", {k: "%.1e" % v for k, v in g["share_rel_err"].items()}, flush=True)
        print(json.dumps(base), flush=True)
        del D, FB, G, W0
        torch.cuda.empty_cache()

    def meets(g):
        e = g["share_rel_err"]
        return g["sigma1_rel_err"] <= 1e-3 and all(e[k] <= 0.02 for k in (1, 4, 16, 64)) and e[256] <= 0.05
    ok = []
    for i, (p, q) in enumerate(GRID):
        if all(meets(r["grid"][i]) for r in rep["tests"]):
            cost = sum(r["grid"][i]["seconds"] for r in rep["tests"] if r["test"] == "D")
            ok.append((cost, p, q))
    rep["choice"] = None
    if ok:
        cost, p, q = min(ok)
        rep["choice"] = {"p": p, "q": q}
    # projection per 448-matrix change: 192 MLP (gate-sized), 128 q/o-sized, 128 k/v (~1/5 of q/o)
    tg = {r["name"].split(".")[-2]: r for r in rep["tests"] if r["test"] == "D"}
    if rep["choice"]:
        i = GRID.index((rep["choice"]["p"], rep["choice"]["q"]))
        mlp, att = tg["gate_proj"]["grid"][i]["seconds"], tg["q_proj"]["grid"][i]["seconds"]
        rep["proj_rsvd_s_per_change"] = round(192 * mlp + 128 * att + 128 * att / 5, 1)
    for k in ("t_svd_fp32_full", "t_svdvals_fp64", "t_gram_eigvalsh_fp64"):
        rep["proj_" + k + "_s_per_change"] = round(192 * tg["gate_proj"][k] + 128 * tg["q_proj"][k] + 128 * tg["q_proj"][k] / 5, 1)
    json.dump(rep, open(a.out, "w"), indent=1)
    print("CHOICE", rep["choice"], {k: v for k, v in rep.items() if k.startswith("proj_")}, flush=True)


if __name__ == "__main__":
    main()
