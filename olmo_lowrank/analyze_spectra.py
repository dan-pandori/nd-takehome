#!/usr/bin/env python3
"""Part 1 analysis of run olmo-lowrank (VPS side; numpy). Pre-registration: "Part 1: spectra".

Inputs per job in artifacts/olmo_lowrank/spectra/<job>/: rows.csv (change x matrix: exact norm^2, randomized top-256
shares, floor B), lora.csv, gauss.csv, full_<step>.npz (all singular values; every matrix under --subset-mod 1).
Outputs in olmo_lowrank/tables/:
  changes.csv    per job x change: energy-weighted S_k (randomized and full), Gaussian and floor-A S_k at the same
                 norms, medians (IQR) of share_16 / stable rank / signal rank / spike count, matrices
  by_type.csv    per job x change x module type: the same medians
  by_depth.csv   per job x change x block of 8 layers: the same medians
  accuracy.csv   randomized vs full top-k shares and sigma_1 per job x change (max / median relative error)
  lora.csv       per net change x adapter (main / ctrl / random): median overlap (left, right, mean), by type;
                 whole-model cos(dW_lora, D_k) and the share of <dW_lora, D> carried by D_k
  expectations.json  P1, P3, E1, E2, E3, E5, E6 scored as pre-registered
Signal rank = #{sigma_i(D) > sigma_1(floor A of that matrix)} (floor A of the family's RL job: R32 for 32B, R7 for 7B);
spike count = #{sigma_i(D) > sigma_1(floor B of that change and matrix)}; both from the full spectra.
"""
import csv
import glob
import json
import os
from collections import defaultdict

import numpy as np

S = "artifacts/olmo_lowrank/spectra"
OUT = "olmo_lowrank/tables"
KS = (1, 4, 16, 64, 256)
TYPES = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
FAMILY = {"R32": "32B", "S32": "32B", "R7": "7B"}
FLOORA_JOB = {"32B": "R32", "7B": "R7"}


def load_full(job):
    out = {}
    for f in sorted(glob.glob(f"{S}/{job}/full_*.npz")):
        z = np.load(f)
        for k in z.files:
            out[k.replace("~", ".")] = z[k].astype(np.float64)
    return out


def load_rows(job):
    p = f"{S}/{job}/rows.csv"
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def q(x):
    x = np.asarray([v for v in x if v is not None and not np.isnan(v)], dtype=float)
    if not len(x):
        return "", "", ""
    return float(np.median(x)), float(np.percentile(x, 25)), float(np.percentile(x, 75))


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [j for j in ("R32", "S32", "R7") if load_rows(j)]
    rows = {j: load_rows(j) for j in jobs}
    full = {j: load_full(j) for j in jobs}
    gauss = {}
    for j in jobs:
        p = f"{S}/{j}/gauss.csv"
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                gauss.setdefault((int(r["m"]), int(r["n"])), []).append({k: float(r[f"full_share_{k}"]) for k in KS})
    gshare = {shp: {k: float(np.mean([g[k] for g in v])) for k in KS} for shp, v in gauss.items()}
    floorA = {}  # (family, matrix) -> (s1, share_k dict, norm2)
    for j in jobs:
        for r in rows[j]:
            if r["change"] == "floorA":
                floorA[(FAMILY[j], r["name"])] = (float(r["s1"]), {k: float(r[f"share_{k}"]) for k in KS},
                                                  float(r["norm2"]))
    ch_rows, type_rows, depth_rows, acc_rows = [], [], [], []
    per = defaultdict(list)  # (job, change) -> per-matrix dicts
    for j in jobs:
        fam = FAMILY[j]
        for r in rows[j]:
            if r["change"] == "floorA":
                continue
            name = r["name"]
            n2 = float(r["norm2"])
            sig = full.get(j, {}).get(f"{r['change']}|{name}")
            fa = floorA.get((fam, name))
            d = {"name": name, "layer": int(r["layer"]), "type": r["type"], "n2": n2,
                 "shape": tuple(sorted((int(r["m"]), int(r["n"])), reverse=True)),
                 "share": {k: float(r[f"share_{k}"]) if r[f"share_{k}"] else np.nan for k in KS},
                 "stable_rank": float(r["stable_rank"]) if r["stable_rank"] else np.nan,
                 "s1": float(r["s1"]), "floorB_s1": float(r["floorB_s1"])}
            if sig is not None:
                c = np.cumsum(sig ** 2)
                d["full_share"] = {k: float(c[k - 1] / n2) for k in KS}
                d["spike"] = int((sig > d["floorB_s1"]).sum())
                d["signal"] = int((sig > fa[0]).sum()) if fa else None
                d["full_s1"] = float(sig[0])
            else:
                d["full_share"], d["spike"], d["signal"], d["full_s1"] = None, None, None, None
            d["gshare"] = gshare.get(d["shape"])
            d["floorA"] = fa
            per[(j, r["change"])].append(d)
    for (j, c), ds in per.items():
        n2 = np.array([d["n2"] for d in ds])
        row = {"job": j, "family": FAMILY[j], "change": c, "matrices": len(ds), "norm2_total": float(n2.sum())}
        for k in KS:
            row[f"S_{k}"] = float(sum(d["share"][k] * d["n2"] for d in ds) / n2.sum())
            if all(d["full_share"] for d in ds):
                row[f"S_full_{k}"] = float(sum(d["full_share"][k] * d["n2"] for d in ds) / n2.sum())
            if all(d["gshare"] for d in ds):
                row[f"gauss_S_{k}"] = float(sum(d["gshare"][k] * d["n2"] for d in ds) / n2.sum())
            fas = [d["floorA"] for d in ds if d["floorA"]]
            if len(fas) == len(ds):
                row[f"floorA_S_{k}"] = float(sum(f[1][k] * f[2] for f in fas) / sum(f[2] for f in fas))
        for key, get in (("share_16", lambda d: d["share"][16]), ("stable_rank", lambda d: d["stable_rank"]),
                         ("signal_rank", lambda d: d["signal"]), ("spike_count", lambda d: d["spike"])):
            m, lo, hi = q([get(d) for d in ds])
            row[f"med_{key}"], row[f"q25_{key}"], row[f"q75_{key}"] = m, lo, hi
        ch_rows.append(row)
        for t in TYPES:
            dt = [d for d in ds if d["type"] == t]
            if dt:
                tr = {"job": j, "change": c, "type": t, "matrices": len(dt)}
                for key, get in (("share_16", lambda d: d["share"][16]), ("stable_rank", lambda d: d["stable_rank"]),
                                 ("signal_rank", lambda d: d["signal"]), ("spike_count", lambda d: d["spike"])):
                    tr[f"med_{key}"] = q([get(d) for d in dt])[0]
                tr["gauss_share_16"] = dt[0]["gshare"][16] if dt[0]["gshare"] else ""
                type_rows.append(tr)
        for b in sorted({d["layer"] // 8 for d in ds}):
            db = [d for d in ds if d["layer"] // 8 == b]
            dr = {"job": j, "change": c, "block": f"{8 * b}-{8 * b + 7}", "matrices": len(db)}
            for key, get in (("share_16", lambda d: d["share"][16]), ("stable_rank", lambda d: d["stable_rank"]),
                             ("signal_rank", lambda d: d["signal"]), ("spike_count", lambda d: d["spike"])):
                dr[f"med_{key}"] = q([get(d) for d in db])[0]
            depth_rows.append(dr)
        dsf = [d for d in ds if d["full_share"]]
        if dsf:
            ds = dsf
            ar = {"job": j, "change": c, "matrices_with_full": len(dsf)}
            for k in KS:
                e = np.array([abs(d["share"][k] / d["full_share"][k] - 1) for d in ds])
                ar[f"share_{k}_max_rel_err"], ar[f"share_{k}_med_rel_err"] = float(e.max()), float(np.median(e))
            e1 = np.array([abs(d["s1"] / d["full_s1"] - 1) for d in ds])
            ar["s1_max_rel_err"], ar["s1_med_rel_err"] = float(e1.max()), float(np.median(e1))
            acc_rows.append(ar)
    for fn, rs in (("changes.csv", ch_rows), ("by_type.csv", type_rows), ("by_depth.csv", depth_rows),
                   ("accuracy.csv", acc_rows)):
        if rs:
            keys = []
            for r in rs:
                keys += [k for k in r if k not in keys]
            with open(f"{OUT}/{fn}", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                w.writerows(rs)
    # ---- LoRA (R32 net changes)
    lora_rows, lr = [], defaultdict(list)
    p = f"{S}/R32/lora.csv"
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            lr[(r["change"], r["adapter"])].append(r)
        n2 = {(c, d["name"]): d for (j, c), ds in per.items() if j == "R32" for d in ds}
        for (c, ad), rs in sorted(lr.items()):
            ov = [(float(r["overlap_left"]) + float(r["overlap_right"])) / 2 for r in rs]
            row = {"change": c, "adapter": ad, "matrices": len(rs),
                   "med_overlap": float(np.median(ov)), "med_left": float(np.median([float(r["overlap_left"]) for r in rs])),
                   "med_right": float(np.median([float(r["overlap_right"]) for r in rs])), "mean_overlap": float(np.mean(ov))}
            for t in TYPES:
                ot = [(float(r["overlap_left"]) + float(r["overlap_right"])) / 2 for r in rs if r["type"] == t]
                row[f"med_overlap_{t}"] = float(np.median(ot)) if ot else ""
            if ad in ("main", "ctrl"):
                L2 = sum(float(r["lora_norm2"]) for r in rs)
                D2 = sum(n2[(c, r["name"])]["n2"] for r in rs)
                inner = sum(float(r["inner_full"]) for r in rs)
                row["cos_full"] = inner / np.sqrt(L2 * D2)
                for k in KS:
                    ik = sum(float(r[f"inner_k{k}"]) for r in rs)
                    Dk2 = sum(n2[(c, r["name"])]["share"][k] * n2[(c, r["name"])]["n2"] for r in rs)
                    row[f"cos_k{k}"] = ik / np.sqrt(L2 * Dk2)
                    row[f"inner_share_k{k}"] = ik / inner if inner else ""
            lora_rows.append(row)
        keys = []
        for r in lora_rows:
            keys += [k for k in r if k not in keys]
        with open(f"{OUT}/lora.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(lora_rows)
    # ---- expectations
    C = {(r["job"], r["change"]): r for r in ch_rows}
    Lr = {(r["change"], r["adapter"]): r for r in lora_rows}
    ex = {}
    n = C.get(("R32", "N2300"))
    if n:
        ex["P1a_spikes_N2300_median_spike_count>=1"] = {"value": n["med_spike_count"], "hit": n["med_spike_count"] >= 1}
        il = [C.get(("R32", i)) for i in ("I_early", "I_mid", "I_late")]
        if all(il) and "floorA_S_16" in il[0]:
            vals = {i["change"]: i["S_16"] / i["floorA_S_16"] for i in il}
            ex["P1b_intervals_S16<=1.5x_floorA"] = {"value": vals, "hit": all(v <= 1.5 for v in vals.values())}
        if "gauss_S_16" in n:
            ex["E1_N2300_S16<=3x_gauss_and_median_signal_rank>=256"] = {
                "value": {"S16/gauss": n["S_16"] / n["gauss_S_16"], "med_signal_rank": n["med_signal_rank"]},
                "hit": n["S_16"] / n["gauss_S_16"] <= 3 and n["med_signal_rank"] >= 256}
        sft = C.get(("S32", "SFT"))
        if sft:
            ex["E2_S16_SFT>S16_N2300"] = {"value": [sft["S_16"], n["S_16"]], "hit": sft["S_16"] > n["S_16"]}
        ts = [50, 100, 500, 750, 1100, 1600, 2300]
        if all(("R32", f"N{t}") in C for t in ts):
            rho = spearman(ts, [C[("R32", f"N{t}")]["S_16"] for t in ts])
            ex["E3_S16_rises_with_t_spearman>0"] = {"value": rho, "hit": rho > 0}
        n7 = C.get(("R7", "N1375"))
        if n7:
            ex["E6_S16_7B_N1375<S16_32B_N2300"] = {"value": [n7["S_16"], n["S_16"]], "hit": n7["S_16"] < n["S_16"]}
    m, c_, rnd = Lr.get(("N2300", "main")), Lr.get(("N2300", "ctrl")), [Lr.get(("N2300", f"r{i}")) for i in range(4)]
    if m:
        ex["P3_lora_main_median_overlap>=0.052"] = {"value": m["med_overlap"], "hit": m["med_overlap"] >= 0.052}
        if c_ and all(rnd):
            rm = float(np.mean([r["med_overlap"] for r in rnd]))
            ex["E5_main>=3x_ctrl_and_>=3x_random_and_<0.052"] = {
                "value": {"main": m["med_overlap"], "ctrl": c_["med_overlap"], "random": rm},
                "hit": m["med_overlap"] >= 3 * c_["med_overlap"] and m["med_overlap"] >= 3 * rm and m["med_overlap"] < 0.052}
    json.dump(ex, open(f"{OUT}/expectations_part1.json", "w"), indent=1, default=float)
    for r in ch_rows:
        print(f"{r['job']} {r['change']:8s} S1 {r['S_1']:.4f} S16 {r['S_16']:.4f} S256 {r['S_256']:.4f} "
              f"gauss16 {r.get('gauss_S_16', float('nan')):.4f} floorA16 {r.get('floorA_S_16', float('nan')):.4f} "
              f"med_sr {r['med_stable_rank']:.1f} signal {r['med_signal_rank']} spike {r['med_spike_count']}")
    for r in lora_rows:
        print(f"lora {r['change']} {r['adapter']} med_overlap {r['med_overlap']:.4f} cos_full {r.get('cos_full', '')} "
              f"cos_k16 {r.get('cos_k16', '')}")
    print(json.dumps(ex, indent=1, default=float))


if __name__ == "__main__":
    main()
