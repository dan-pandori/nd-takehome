"""Arm A (aggregate curve) and arm D (lengths) for run olmo-ifcurve, from my re-grade and my cells.

pass@k: unbiased 1 - C(n-c, k) / C(n, k) per prompt, mean over the 218; 95 % prompt-bootstrap percentile intervals
(10,000 replicates, numpy default_rng(1)); per family (prefix of the first instruction id). Reading 5 (shape): for
c in {750, 1100, 1600}, paired prompt-bootstrap 90 % intervals of D8(c) = pass@8(2300) - pass@8(c) and D1(c);
"sharpening from c" iff D8's interval reaches 0 or below while D1's lies above 0; onset = earliest such c.
Arm D: medians over all arm-A draws (and over the reach cells' base-32 draws) of thinking tokens (ids wholly before the
first '</think>'), answer tokens (ids wholly after the last '</think>'), thinking words, answer words; shares of draws
without '</think>' and cut at the token cap (finish == 'length').
Writes out/armA.txt, out/armA.json.
"""
import json
from math import comb

import numpy as np

from rvc_cells import CK, CKA, build
from rvc_core import STEP, Tee, dump, upstream_record

T = Tee("armA.txt")
NB = 10000


def passk(n, c, k):
    if n < k:
        return None
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def main():
    rows, armA, reach, A, B, XC, J = build()
    fam = {p: upstream_record(p)[1]["instruction_id_list"][0].split(":")[0] for p in armA}
    nc = {c: np.array([[len(A[c][p]), sum(rows[tuple(k)]["strict"] for k in A[c][p])] for p in armA]) for c in CKA}
    # first-8 dpo check
    nc["dpo8"] = np.array([[8, sum(rows[tuple(k)]["strict"] for k in A["dpo"][p][:8])] for p in armA])
    rng = np.random.default_rng(1)
    idx = rng.integers(0, len(armA), size=(NB, len(armA)))
    per = {}
    for c, a in nc.items():
        for k in (1, 4, 8):
            v = np.array([passk(n, s, k) if n >= k else np.nan for n, s in a])
            if np.isnan(v).any():
                continue
            per[(c, k)] = v
    res = {"pass": {}, "family": {}, "shape": {}, "lengths": {}}
    T("arm A strict pass@k (218 IFBench prompts; mean, 95 % prompt-bootstrap interval); n = draws per prompt")
    for c in CKA + ["dpo8"]:
        line = f"   {c:6s} n={nc[c][0][0]:2d} strict draws {int(nc[c][:, 1].sum()):5d}/{int(nc[c][:, 0].sum()):5d}"
        for k in (1, 4, 8):
            if (c, k) in per:
                v = per[(c, k)]
                bs = v[idx].mean(axis=1)
                lo, hi = np.percentile(bs, [2.5, 97.5])
                res["pass"][f"{c}_p{k}"] = [float(v.mean()), float(lo), float(hi)]
                line += f" | pass@{k} {v.mean():.3f} [{lo:.3f}, {hi:.3f}]"
        T(line)
    T("adjacent pass@1 differences (step order; paired bootstrap 95 %):")
    for a, b in zip(CKA[:-1], CKA[1:]):
        d = per[(b, 1)] - per[(a, 1)]
        bs = d[idx].mean(axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        res["pass"][f"d1_{a}_{b}"] = [float(d.mean()), float(lo), float(hi)]
        T(f"   {a} -> {b}: {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]")
    T("per family pass@1 (and pass@8 where n >= 8):")
    fams = sorted(set(fam.values()), key=lambda f: -sum(fam[p] == f for p in armA))
    for f in fams:
        m = np.array([fam[p] == f for p in armA])
        cells = []
        for c in CKA:
            s = f"{per[(c, 1)][m].mean():.2f}"
            if (c, 8) in per:
                s += f"/{per[(c, 8)][m].mean():.2f}"
            cells.append(s)
            res["family"][f"{f}_{c}"] = [float(per[(c, 1)][m].mean())] + ([float(per[(c, 8)][m].mean())] if (c, 8) in per else [])
        T(f"   {f:8s} ({m.sum():2d}) " + " ".join(f"{c[1:] if c != 'dpo' else 'dpo'}:{x}" for c, x in zip(CKA, cells)))
    # family bootstrap intervals (pass@1) for the record
    fam_ci = {}
    for f in fams:
        ps = [i for i, p in enumerate(armA) if fam[p] == f]
        ri = np.random.default_rng(2).integers(0, len(ps), size=(NB, len(ps)))
        for c in CKA:
            v = per[(c, 1)][ps]
            lo, hi = np.percentile(v[ri].mean(axis=1), [2.5, 97.5])
            fam_ci[f"{f}_{c}"] = [float(v.mean()), float(lo), float(hi)]
    res["family_ci_p1"] = fam_ci
    # shape reading (90 % paired)
    T("reading 5 (shape): paired prompt-bootstrap 90 % intervals, D = value(2300) - value(c)")
    onset = None
    for c in ("s0750", "s1100", "s1600"):
        out = {}
        for k in (1, 8):
            d = per[("s2300", k)] - per[(c, k)]
            bs = d[idx].mean(axis=1)
            lo, hi = np.percentile(bs, [5, 95])
            out[k] = (float(d.mean()), float(lo), float(hi))
        sharp = out[8][1] <= 0 and out[1][1] > 0
        res["shape"][c] = {"D1": out[1], "D8": out[8], "sharpening": sharp}
        T(f"   c={c}: D1 {out[1][0]:+.3f} [{out[1][1]:+.3f}, {out[1][2]:+.3f}]  D8 {out[8][0]:+.3f} "
          f"[{out[8][1]:+.3f}, {out[8][2]:+.3f}]  -> sharpening from c: {sharp}")
        if sharp and onset is None:
            onset = c
    res["shape"]["onset"] = onset
    T(f"   reading: {'sharpening from ' + onset if onset else 'widening throughout'}")
    # ---- arm D
    T("arm D lengths (medians; thinking tokens over draws with </think>; answer words over draws with an answer)")
    T("   ckpt  | all arm-A draws: n, think_tok, ans_tok, think_w, ans_w, no-</think>, cut | reach base-32 draws: n, think_tok, ans_tok, think_w, ans_w, no-</think>, cut")
    for c in CKA:
        out = []
        for ks in ([k for p in armA for k in A[c][p]],
                   ([k for p in reach for k in B[c][p]] if c in B else [])):
            rs = [rows[tuple(k)] for k in ks]
            if not rs:
                out.append(None)
                continue
            th = [r["think_tok"] for r in rs if r["think_tok"] is not None]
            at = [r["ans_tok"] for r in rs if r["ans_tok"] is not None]
            tw = [r["think_words"] for r in rs if r["think_words"] is not None]
            aw = [r["ans_words"] for r in rs if r["ans_words"] is not None]
            th_all = [r["think_tok"] if r["think_tok"] is not None else r["n_ids"] for r in rs]
            d = {"n": len(rs), "think_tok": float(np.median(th)), "ans_tok": float(np.median(at)),
                 "think_words": float(np.median(tw)), "ans_words": float(np.median(aw)),
                 "think_tok_noclose_as_all": float(np.median(th_all)),
                 "no_close": sum(r["n_close"] == 0 for r in rs) / len(rs),
                 "cut": sum(r["finish"] == "length" for r in rs) / len(rs),
                 "n_cut": sum(r["finish"] == "length" for r in rs), "n_noclose": sum(r["n_close"] == 0 for r in rs),
                 "mean_tokens": float(np.mean([r["n_ids"] for r in rs]))}
            out.append(d)
        res["lengths"][c] = {"armA": out[0], "reach": out[1]}
        f = lambda d: (f"{d['n']:5d} {d['think_tok']:7.0f} {d['ans_tok']:6.0f} {d['think_words']:6.0f} {d['ans_words']:5.0f} "
                       f"{d['no_close']:.4f} {d['cut']:.4f}") if d else "-"
        T(f"   {c:6s}| {f(out[0])} | {f(out[1])}")
    # brevity B
    m = {c: res["lengths"][c]["armA"]["ans_words"] for c in CKA}
    ref = m["s2300"]
    Bc = None
    for i, c in enumerate(CKA):
        if all(abs(m[x] - ref) <= 0.2 * ref for x in CKA[i:]):
            Bc = c
            break
    mt = {c: res["lengths"][c]["armA"]["ans_tok"] for c in CKA}
    Bt = None
    for i, c in enumerate(CKA):
        if all(abs(mt[x] - mt["s2300"]) <= 0.2 * mt["s2300"] for x in CKA[i:]):
            Bt = c
            break
    res["brevity_B"] = Bc
    res["brevity_B_tokens"] = Bt
    T(f"brevity B (answer words, within +-20 % of m(2300) = {ref:.0f} from then on): {Bc}; with answer tokens: {Bt}")
    dump(res, "armA.json")


if __name__ == "__main__":
    main()
