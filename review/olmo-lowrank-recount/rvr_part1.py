"""My Part-1 recount over every matrix, from the run's stored per-matrix data, which my seeded raw-weight recompute
validated (rvr_spectra_cmp.py): exact norms (rows.csv), all singular values (full_*.npz, Gram route), the run's floor A /
floor B sigma_1 (rows.csv; my independent floors agree within 1 %), LoRA overlaps / inner products (lora.csv). Gaussian
baseline shares from MY simulation (pod_out/out/gauss.csv, 3 seeds per shape). Measures and expectations as
pre-registered ("Part 1: spectra", "Expected results"). -> out/part1.json, out/part1.txt"""
import csv
import glob
import json
from collections import defaultdict

import numpy as np

from rvr_core import ART, KIT, OUT, Tee

KS = (1, 4, 16, 64, 256)
TYPES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
FAM = {"R32": "32B", "S32": "32B", "R7": "7B"}


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def med_iqr(v):
    v = np.asarray(v, float)
    return [float(np.median(v)), float(np.percentile(v, 25)), float(np.percentile(v, 75))]


def main():
    T = Tee("part1.txt")
    G = defaultdict(list)
    for r in csv.DictReader(open(KIT / "pod_out" / "out" / "gauss.csv")):
        G[(int(r["m"]), int(r["n"]))].append({k: float(r[f"share_{k}"]) for k in KS})
    gsh = {s: {k: float(np.mean([x[k] for x in v])) for k in KS} for s, v in G.items()}
    per = defaultdict(dict)   # (fam, change) -> name -> dict
    floorA = {}
    for job in ("R32", "S32", "R7"):
        fam = FAM[job]
        full = {}
        for f in glob.glob(str(ART / "spectra" / job / "full_*.npz")):
            z = np.load(f)
            for k in z.files:
                c, n = k.replace("~", ".").split("|")
                full[(c, n)] = z[k].astype(np.float64)
        for r in csv.DictReader(open(ART / "spectra" / job / "rows.csv")):
            S = full[(r["change"], r["name"])]
            d = {"layer": int(r["layer"]), "type": r["type"], "shape": tuple(sorted((int(r["m"]), int(r["n"])), reverse=True)),
                 "n2": float(r["norm2"]), "S": S}
            if r["change"] == "floorA":
                floorA[(fam, r["name"])] = d | {"s1": float(r["s1"])}
            else:
                d["floorB_s1"] = float(r["floorB_s1"])
                per[(fam, r["change"])][r["name"]] = d
    res = {"changes": {}}
    for (fam, c), D in sorted(per.items()):
        n2 = np.array([d["n2"] for d in D.values()])
        row = {"matrices": len(D), "norm2_total": float(n2.sum())}
        for k in KS:
            row[f"S_{k}"] = float(sum(float(np.sum(d["S"][:k] ** 2)) for d in D.values()) / n2.sum())
            row[f"gauss_S_{k}"] = float(sum(gsh[d["shape"]][k] * d["n2"] for d in D.values()) / n2.sum())
            fa = [floorA[(fam, nm)] for nm in D]
            row[f"floorA_S_{k}"] = float(sum(float(np.sum(f["S"][:k] ** 2)) for f in fa) / sum(f["n2"] for f in fa))
        sig = [int((d["S"] > floorA[(fam, nm)]["s1"]).sum()) for nm, d in D.items()]
        sig256 = [int((d["S"][:256] > floorA[(fam, nm)]["s1"]).sum()) for nm, d in D.items()]
        spk = [int((d["S"] > d["floorB_s1"]).sum()) for d in D.values()]
        sh16 = [float(np.sum(d["S"][:16] ** 2) / d["n2"]) for d in D.values()]
        sr = [d["n2"] / float(d["S"][0]) ** 2 for d in D.values()]
        row.update({"signal_rank": med_iqr(sig), "signal_rank_censored256": med_iqr(sig256),
                    "share_signal_ge256": float(np.mean(np.array(sig) >= 256)),
                    "spike_count": med_iqr(spk), "share_spike_ge1": float(np.mean(np.array(spk) >= 1)),
                    "share_16": med_iqr(sh16), "stable_rank": med_iqr(sr)})
        row["by_type"] = {t: {"share_16": float(np.median([s for s, d in zip(sh16, D.values()) if d["type"] == t])),
                              "signal_rank": float(np.median([s for s, d in zip(sig, D.values()) if d["type"] == t])),
                              "spike_count": float(np.median([s for s, d in zip(spk, D.values()) if d["type"] == t]))}
                          for t in TYPES}
        row["by_depth"] = {f"{8 * b}-{8 * b + 7}": {"share_16": float(np.median([s for s, d in zip(sh16, D.values()) if d["layer"] // 8 == b])),
                                                     "spike_count": float(np.median([s for s, d in zip(spk, D.values()) if d["layer"] // 8 == b]))}
                           for b in sorted({d["layer"] // 8 for d in D.values()})}
        res["changes"][f"{fam}|{c}"] = row
    C = res["changes"]
    # LoRA overlap and cosines (32B net changes)
    L = defaultdict(list)
    for r in csv.DictReader(open(ART / "spectra" / "R32" / "lora.csv")):
        L[(r["change"], r["adapter"])].append(r)
    lo = {}
    for (c, a), rs in sorted(L.items()):
        ov = [(float(r["overlap_left"]) + float(r["overlap_right"])) / 2 for r in rs]
        x = {"matrices": len(rs), "median_overlap": float(np.median(ov)),
             "median_left": float(np.median([float(r["overlap_left"]) for r in rs])),
             "median_right": float(np.median([float(r["overlap_right"]) for r in rs]))}
        if a in ("main", "ctrl"):
            D = per[("32B", c)]
            Ln = sum(float(r["lora_norm2"]) for r in rs)
            Dn = sum(D[r["name"]]["n2"] for r in rs)
            inner = sum(float(r["inner_full"]) for r in rs)
            x["cos_full"] = inner / np.sqrt(Ln * Dn)
            for k in KS:
                ik = sum(float(r[f"inner_k{k}"]) for r in rs)
                Dk = sum(float(np.sum(D[r["name"]]["S"][:k] ** 2)) for r in rs)
                x[f"cos_k{k}"] = ik / np.sqrt(Ln * Dk)
                x[f"inner_share_k{k}"] = ik / inner
        lo[f"{c}|{a}"] = x
    # expected random overlap 16/dim
    exp_rand = {}
    for r in L[("N2300", "r0")]:
        D = per[("32B", "N2300")][r["name"]]
    res["lora"] = lo
    rnd = float(np.mean([lo[f"N2300|r{i}"]["median_overlap"] for i in range(4)]))
    # expectations
    n = C["32B|N2300"]
    iv = {i: C[f"32B|{i}"]["S_16"] / C[f"32B|{i}"]["floorA_S_16"] for i in ("I_early", "I_mid", "I_late")}
    ts = [50, 100, 500, 750, 1100, 1600, 2300]
    rho = spearman(ts, [C[f"32B|N{t}"]["S_16"] for t in ts])
    m, c_ = lo["N2300|main"]["median_overlap"], lo["N2300|ctrl"]["median_overlap"]
    ex = {"P1a median spike count N2300 >= 1": [n["spike_count"][0], n["spike_count"][0] >= 1],
          "P1b intervals S16 <= 1.5 x floor A S16": [iv, all(v <= 1.5 for v in iv.values())],
          "P3 lora_main median overlap >= 0.052": [m, m >= 0.052],
          "E1 N2300 S16 <= 3 x gauss and median signal rank >= 256": [{"S16/gauss": n["S_16"] / n["gauss_S_16"], "median_signal_rank": n["signal_rank"][0]},
                                                                      n["S_16"] / n["gauss_S_16"] <= 3 and n["signal_rank"][0] >= 256],
          "E2 S16(SFT) > S16(N2300)": [[C["32B|SFT"]["S_16"], n["S_16"]], C["32B|SFT"]["S_16"] > n["S_16"]],
          "E3 Spearman(S16, t) > 0": [rho, rho > 0],
          "E5 main >= 3 ctrl and >= 3 random and < 0.052": [{"main": m, "ctrl": c_, "random": rnd},
                                                          m >= 3 * c_ and m >= 3 * rnd and m < 0.052],
          "E6 S16(7B N1375) < S16(32B N2300)": [[C["7B|N1375"]["S_16"], n["S_16"]], C["7B|N1375"]["S_16"] < n["S_16"]]}
    res["expectations"] = ex
    json.dump(res, open(OUT / "part1.json", "w"), indent=1, default=float)
    for k, r in C.items():
        T(f"{k:14s} S1 {r['S_1']:.4f} S16 {r['S_16']:.4f} S64 {r['S_64']:.4f} S256 {r['S_256']:.4f} | gauss16 {r['gauss_S_16']:.4f} "
          f"floorA16 {r['floorA_S_16']:.4f} | med signal {r['signal_rank'][0]:.0f} [{r['signal_rank'][1]:.0f},{r['signal_rank'][2]:.0f}] "
          f"spike {r['spike_count'][0]:.0f} [{r['spike_count'][1]:.0f},{r['spike_count'][2]:.0f}] share16 {r['share_16'][0]:.4f} "
          f"stable {r['stable_rank'][0]:.1f} sig>=256 {r['share_signal_ge256']:.2f}")
    for k, x in lo.items():
        T(f"lora {k:14s} med overlap {x['median_overlap']:.5f} (L {x['median_left']:.5f} R {x['median_right']:.5f})"
          + (f" cos_full {x['cos_full']:.5f} cos_k16 {x['cos_k16']:.5f} cos_k256 {x['cos_k256']:.5f} share_k16 {x['inner_share_k16']:.3f} share_k256 {x['inner_share_k256']:.3f}" if "cos_full" in x else ""))
    for k, v in ex.items():
        T(f"{k}: {v}")


if __name__ == "__main__":
    main()
