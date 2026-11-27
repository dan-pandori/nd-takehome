"""Compare my seeded raw-weight recompute (pod_out/out, rvr_pod.py) with the run's stored Part-1 values for the same
matrices: rows.csv (exact norm^2, randomized top-256 sigma_1 / shares, floor B sigma_1, floor A rows), full_*.npz (all
singular values, Gram route), lora.csv (overlaps, inner products), gauss.csv, the N2300 exact spectra used for the
adapters (adapters_svd/spectra_layer_XX.npz), and the adapters (my B A vs my float64 truncation).
-> out/spectra_cmp.json, out/spectra_cmp.txt"""
import csv
import glob
import json
from collections import defaultdict

import numpy as np

from rvr_core import ART, KIT, OUT, Tee

KS = (1, 4, 16, 64, 256)
JOB = {"32B": ["R32", "S32"], "7B": ["R7"]}


def theirs():
    rows, full = {}, {}
    for fam, jobs in JOB.items():
        for j in jobs:
            for r in csv.DictReader(open(ART / "spectra" / j / "rows.csv")):
                rows[(fam, r["change"], r["name"])] = r
            for f in glob.glob(str(ART / "spectra" / j / "full_*.npz")):
                z = np.load(f)
                for k in z.files:
                    c, n = k.replace("~", ".").split("|")
                    full[(fam, c, n)] = z[k].astype(np.float64)
    return rows, full


def mine():
    rows, sig = {}, {}
    for r in csv.DictReader(open(KIT / "pod_out" / "out" / "rows.csv")):
        k = (r["fam"], r["change"], r["name"])
        if r["kind"] == "signal":
            rows.setdefault(k, {}).update({"floorA_s1": r["floorA_s1"], "signal_full": r["signal_full"],
                                           "signal_256": r["signal_256"]})
        else:
            rows.setdefault(k, {}).update(r)
    for f in glob.glob(str(KIT / "pod_out" / "out" / "sv_*.npz")):
        fam = f.split("sv_")[1].split("_")[0]
        z = np.load(f)
        for k in z.files:
            c, n = k.replace("~", ".").split("|")
            sig[(fam, c, n)] = z[k]
    return rows, sig


def rel(a, b):
    return abs(a / b - 1) if b else (0.0 if a == 0 else float("inf"))


def main():
    T = Tee("spectra_cmp.txt")
    tr, tf = theirs()
    mr, ms = mine()
    res = {}
    keys = sorted(k for k in mr if k[1] != "floorA" and "norm2" in mr[k])
    agg = defaultdict(list)
    sig_rows = []
    for k in keys:
        m, t = mr[k], tr.get(k)
        if t is None:
            agg["missing"].append(k)
            continue
        fam, c, n = k
        mS = ms[k]
        tS = tf.get(k)
        e = {"norm2": rel(float(t["norm2"]), float(m["norm2"])),
             "s1_rsvd": rel(float(t["s1"]), float(m["s1"])),
             "share16_rsvd": rel(float(t["share_16"]), float(m["share_16"])),
             "share256_rsvd": rel(float(t["share_256"]), float(m["share_256"]))}
        if tS is not None:
            kk = min(256, len(tS))
            e["full_top256_maxerr_over_s1"] = float(np.max(np.abs(tS[:kk] - mS[:kk])) / mS[0])
            e["full_all_maxerr_over_s1"] = float(np.max(np.abs(tS - mS[:len(tS)])) / mS[0])
            for q in KS:
                e[f"full_share{q}"] = rel(float(np.sum(tS[:q] ** 2) / float(t["norm2"])), float(m[f"share_{q}"]))
        if t.get("floorB_s1") and m.get("floorB_s1"):
            e["floorB_s1_ratio"] = float(t["floorB_s1"]) / float(m["floorB_s1"]) - 1
        for name, v in e.items():
            agg[(c in ("SFT", "DPO", "ZIF"), name)].append(v)
            agg[("all", name)].append(v)
        # signal rank / spike count: theirs (their full spectrum vs their floors) and mine (mine vs mine)
        fa_t = tr.get((fam, "floorA", n))
        srow = {"fam": fam, "change": c, "name": n}
        if tS is not None and fa_t is not None:
            srow["signal_theirs"] = int((tS > float(fa_t["s1"])).sum())
        srow["signal_mine"] = int(m["signal_full"])
        if tS is not None and t.get("floorB_s1"):
            srow["spike_theirs"] = int((tS > float(t["floorB_s1"])).sum())
        if m.get("spike") not in (None, ""):
            srow["spike_mine"] = int(m["spike"])
        sig_rows.append(srow)
    # floor A sigma_1 (independent draws) and norm^2 targets
    fa = []
    for k, m in mr.items():
        if k[1] != "floorA" or "norm2" not in m:
            continue
        t = tr.get(k)
        if t is None:
            continue
        fa.append({"fam": k[0], "name": k[2], "s1_ratio": float(t["s1"]) / float(m["s1"]) - 1,
                   "target_ratio": float(t["floorB_n2"]) / float(m["floorB_n2"]) - 1,
                   "share16_t": float(t["share_16"]), "share16_m": float(m["share_16"])})
    res["errors"] = {f"{a}|{b}": {"n": len(v), "max": float(np.max(np.abs(v))), "median": float(np.median(np.abs(v)))}
                     for (a, b), v in agg.items() if a != "missing"} if agg else {}
    res["missing"] = [list(k) for k in agg.get("missing", [])]
    res["floorA"] = {"n": len(fa), "s1_ratio_max": float(max(abs(x["s1_ratio"]) for x in fa)),
                     "s1_ratio_median": float(np.median([x["s1_ratio"] for x in fa])),
                     "target_ratio_max": float(max(abs(x["target_ratio"]) for x in fa)),
                     "share16_rel_max": float(max(abs(x["share16_t"] / x["share16_m"] - 1) for x in fa))}
    # signal / spike agreement
    d_sig = [s["signal_theirs"] - s["signal_mine"] for s in sig_rows if "signal_theirs" in s]
    d_spk = [s["spike_theirs"] - s["spike_mine"] for s in sig_rows if "spike_theirs" in s and "spike_mine" in s]
    res["signal"] = {"n": len(d_sig), "exact": sum(x == 0 for x in d_sig), "max_abs_diff": int(max(map(abs, d_sig))),
                     "examples": [s for s in sig_rows if s.get("signal_theirs") is not None and abs(s["signal_theirs"] - s["signal_mine"]) > 0][:12]}
    res["spike"] = {"n": len(d_spk), "exact": sum(x == 0 for x in d_spk), "max_abs_diff": int(max(map(abs, d_spk))) if d_spk else None,
                    "examples": [s for s in sig_rows if "spike_theirs" in s and "spike_mine" in s and s["spike_theirs"] != s["spike_mine"]][:12]}
    # LoRA overlaps
    tl = {(r["change"], r["name"], r["adapter"]): r for r in csv.DictReader(open(ART / "spectra" / "R32" / "lora.csv"))}
    lo = defaultdict(list)
    for r in csv.DictReader(open(KIT / "pod_out" / "out" / "lora.csv")):
        if r["adapter"] in ("main", "ctrl"):
            t = tl.get((r["change"], r["name"], r["adapter"]))
            if t is None:
                lo["missing"].append((r["change"], r["name"], r["adapter"]))
                continue
            for f in ("overlap_left", "overlap_right", "lora_norm2", "inner_full", "inner_k16", "inner_k256"):
                lo[(r["adapter"], f)].append(rel(float(t[f]), float(r[f])))
        else:
            lo[("random", "overlap_mean")].append((float(r["overlap_left"]) + float(r["overlap_right"])) / 2)
    res["lora"] = {f"{a}|{b}": {"n": len(v), "max_rel": float(np.max(v)), "median_rel": float(np.median(v))}
                   for (a, b), v in lo.items() if a != "missing" and a != "random"}
    res["lora_missing"] = len(lo.get("missing", []))
    # adapters
    ad = list(csv.DictReader(open(KIT / "pod_out" / "out" / "adapters.csv")))
    per = defaultdict(list)
    for r in ad:
        if r["adapter"] == "Z8":
            per["Z8_max_abs_BA"].append(float(r["max_abs_BA"]))
            continue
        per[(r["adapter"], "rel_err_fp64")].append(float(r["rel_err_fp64"]))
        per[(r["adapter"], "rel_err_bf16_factors")].append(float(r["rel_err_bf16_factors"]))
        per[(r["adapter"], "identity_gap")].append(abs(float(r["resid_n2"]) - float(r["identity_n2"])) / float(r["identity_n2"]))
        per[(r["adapter"], "config")].append((r["r"], r["lora_alpha"], r["B_shape"], r["A_shape"]))
    res["adapters"] = {}
    for kk, v in per.items():
        if kk == "Z8_max_abs_BA":
            res["adapters"]["Z8_max_abs_BA"] = max(v)
        elif kk[1] == "config":
            res["adapters"][f"{kk[0]}|config"] = sorted({f"r={a} alpha={b}" for a, b, _, _ in v})
        else:
            res["adapters"][f"{kk[0]}|{kk[1]}"] = {"n": len(v), "max": max(v), "median": float(np.median(v))}
    # executor's exact fp32 N2300 spectra (adapters_svd) vs mine
    ex = []
    for f in sorted(glob.glob(str(ART / "adapters_svd" / "spectra_layer_*.npz"))):
        z = np.load(f)
        for k in z.files:
            n = k.replace("__", ".")
            if ("32B", "N2300", n) in ms:
                mS = ms[("32B", "N2300", n)]
                ex.append(float(np.max(np.abs(z[k][:256] - mS[:256])) / mS[0]))
    res["adapters_svd_top256_maxerr_over_s1"] = {"n": len(ex), "max": max(ex) if ex else None}
    # gauss
    tg = defaultdict(list)
    for j in ("R32", "S32", "R7"):
        for r in csv.DictReader(open(ART / "spectra" / j / "gauss.csv")):
            tg[(int(r["m"]), int(r["n"]))].append({q: float(r[f"full_share_{q}"]) for q in KS})
    mg = defaultdict(list)
    for r in csv.DictReader(open(KIT / "pod_out" / "out" / "gauss.csv")):
        mg[(int(r["m"]), int(r["n"]))].append({q: float(r[f"share_{q}"]) for q in KS})
    res["gauss"] = {f"{a}x{b}": {q: [round(float(np.mean([x[q] for x in tg[(a, b)]])), 6), round(float(np.mean([x[q] for x in mg[(a, b)]])), 6)]
                                 for q in KS} for (a, b) in mg if (a, b) in tg}
    json.dump(res, open(OUT / "spectra_cmp.json", "w"), indent=1, default=str)
    T(json.dumps(res, indent=1, default=str)[:9000])


if __name__ == "__main__":
    main()
