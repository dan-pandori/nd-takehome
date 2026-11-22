#!/usr/bin/env python3
"""Analysis of run olmo-ifcurve (pre-registration preregistration/olmo-ifcurve.md, "Measures" and "Readings").
VPS-side (numpy). Inputs: artifacts/olmo_ifcurve/rows/*.csv (cells.py rows), the hand gate (hand.py), the class table
olmo_ifladder/classify.csv. Outputs (olmo_ifcurve/): results.csv (one row per arm x checkpoint x prompt cell),
passk.csv, emergence.csv, gaming.csv, lengths.csv, summary.json (6 dp).

  analyze.py [--reps 10000]
"""
import csv
import json
import statistics as st
import sys
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells  # noqa: E402
import hand  # noqa: E402

O = Path("olmo_ifcurve")
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 10000
NEVER = 9999
KS = (1, 2, 4, 8)
EARLY_C, LATE = ("dpo", "s0050", "s0100", "s0200"), ("s1100", "s1600", "s2300")
EARLY_B = ("s0050", "s0100", "s0200")


def r6(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 6)


def passk(n, c, k):
    if n < k:
        return float("nan")
    return 1.0 if n - c < k else 1.0 - comb(n - c, k) / comb(n, k)


def classes():
    out = {}
    for r in csv.DictReader(open("olmo_ifladder/classify.csv")):
        k = "P" if r["reading"].startswith("prompt") else ("T" if r["reading"].startswith("teach") else "N")
        out[r["pid"]] = k
    alt = dict(out)
    alt["ifbench_154"] = "P"  # rule-3 reading (olmo-ifladder review)
    return out, alt


def family(pid):
    return hand.ids_of(hand.problems()[pid])[0].split(":")[0]


def boot_ci(stat_reps, lo=2.5, hi=97.5):
    a = np.asarray(stat_reps, dtype=float)
    return float(np.percentile(a, lo)), float(np.percentile(a, hi))


def main():
    rng = np.random.default_rng(20261121)
    R, AA = cells.reach(), cells.armA()
    cls, cls_alt = classes()
    L = hand.Labels()
    # a checkpoint counts only when every arm-A cell has its full N_A draws (a job still sampling does not)
    present = [c for c in cells.CKPTS if all(len(cells.draws(c, p, "A")) >= cells.N_A.get(c, 8) for p in AA)]
    results, summary = [], {"checkpoints_present": present}

    # ------------------------------------------------------------------ arm A
    fam = {p: family(p) for p in AA}
    A_counts = {}  # ckpt -> (n array, c array) over AA
    for c in present:
        ns, cs = [], []
        for p in AA:
            d = cells.draws(c, p, "A")
            ns.append(len(d))
            cs.append(sum(x["strict"] for x in d))
            results.append({"arm": "A", "ckpt": c, "step": cells.STEP[c], "pid": p, "set": "reach" if p in R else "armA",
                            "class": cls.get(p, ""), "family": fam[p], "n": len(d), "strict": cs[-1],
                            "cut": sum(x["finish"] == "length" for x in d), "no_think_end": sum(1 - x["think_end"] for x in d),
                            "tok_mean": r6(st.mean(x["n_tok"] for x in d)) if d else None})
        A_counts[c] = (np.array(ns), np.array(cs))
    if "dpo" in A_counts:  # first-8 check for dpo
        ns8, cs8 = [], []
        for p in AA:
            d = cells.draws("dpo", p, "A")[:8]
            ns8.append(len(d))
            cs8.append(sum(x["strict"] for x in d))
        A_counts["dpo_first8"] = (np.array(ns8), np.array(cs8))
    pk_rows = []
    idx_all = np.arange(len(AA))
    boots = rng.integers(0, len(AA), size=(REPS, len(AA)))
    pk_per = {}  # (ckpt, k) -> per-prompt pass@k array
    for c, (ns, cs) in A_counts.items():
        for k in KS:
            v = np.array([passk(n, x, k) for n, x in zip(ns, cs)])
            pk_per[(c, k)] = v
            for grp in ["all"] + sorted(set(fam.values())):
                sel = idx_all if grp == "all" else np.array([i for i, p in enumerate(AA) if fam[p] == grp])
                vv = v[sel]
                if grp == "all":
                    reps = vv[boots].mean(axis=1)
                else:
                    b = rng.integers(0, len(sel), size=(REPS, len(sel)))
                    reps = vv[b].mean(axis=1)
                lo, hi = boot_ci(reps)
                pk_rows.append({"ckpt": c, "step": cells.STEP.get(c, 0), "group": grp, "k": k, "n_prompts": len(sel),
                                "pass_at_k": r6(vv.mean()), "lo95": r6(lo), "hi95": r6(hi)})
    with open(O / "passk.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pk_rows[0]))
        w.writeheader()
        w.writerows(pk_rows)
    summary["armA"] = {c: {f"pass@{k}": r6(pk_per[(c, k)].mean()) for k in KS} for c in A_counts}
    # shape: paired bootstrap of the remaining gain from c to s2300
    shape = {}
    if "s2300" in A_counts:
        for c in ("s0750", "s1100", "s1600"):
            if c not in A_counts:
                continue
            out = {}
            for k in (1, 8):
                dv = pk_per[("s2300", k)] - pk_per[(c, k)]
                reps = dv[boots].mean(axis=1)
                lo, hi = boot_ci(reps, 5, 95)
                out[f"d{k}"] = {"est": r6(dv.mean()), "lo90": r6(lo), "hi90": r6(hi)}
            out["sharpening"] = (None if out["d8"]["lo90"] is None or out["d1"]["lo90"] is None
                                 else bool(out["d8"]["lo90"] <= 0 and out["d1"]["lo90"] > 0))
            shape[c] = out
        onset = next((c for c in ("s0750", "s1100", "s1600") if shape.get(c, {}).get("sharpening")), None)
        summary["shape"] = {"spans": shape, "onset": onset,
                            "reading": (f"sharpening from {onset}" if onset else "widening throughout")
                            if len(shape) == 3 else "incomplete"}

    # ------------------------------------------------------------------ arm B
    em_rows, cell_share = [], {}
    for p in R:
        stt, _, _ = hand.walk(L, p)
        rates = {}
        f1star = stt["F1"]
        ext_cells = {}
        for c in cells.CKPTS[1:]:
            dr = cells.draws(c, p, "B")
            if not dr:
                continue
            base, ext = dr[:cells.N_B], dr[cells.N_B:]
            S = [d for d in base if d["strict"]]
            labs = [L.label(d) for d in S]
            g = sum(1 for lab, _ in labs if lab == "genuine")
            b = sum(1 for lab, _ in labs if lab == "gamed")
            u = len(S) - g - b
            first = [lab for lab, _ in labs[:hand.LOOK] if lab]
            share = (first.count("genuine") / len(first)) if first else float("nan")
            est = g + (u * share if u and first else 0.0) if (first or not u) else float("nan")
            rates[c] = est / len(base) if base else float("nan")
            cell_share[(c, p)] = (len(first), first.count("gamed"))
            src = {}
            for lab, s_ in labs:
                src[s_] = src.get(s_, 0) + 1
            eg = eb = 0
            if ext:
                SE = [d for d in ext if d["strict"]]
                le = [L.label(d)[0] for d in SE]
                eg, eb = le.count("genuine"), le.count("gamed")
                ext_cells[c] = {"ext_ckpt": c, "ext_n": len(dr), "ext_strict": len([d for d in dr if d["strict"]]),
                                "ext_genuine": g + eg, "ext_unlabelled": (len(S) + len(SE)) - (g + b + eg + eb)}
            results.append({"arm": "B", "ckpt": c, "step": cells.STEP[c], "pid": p, "set": "reach", "class": cls[p],
                            "family": "", "n": len(base), "strict": len(S), "cut": sum(x["finish"] == "length" for x in base),
                            "no_think_end": sum(1 - x["think_end"] for x in base),
                            "tok_mean": r6(st.mean(x["n_tok"] for x in base)), "genuine_labelled": g, "gamed_labelled": b,
                            "unlabelled": u, "first4_labelled": len(first), "first4_genuine": first.count("genuine"),
                            "genuine_est": r6(est), "rate_est": r6(rates[c]), "label_sources": json.dumps(src),
                            "ext_n": len(ext), "ext_strict": sum(d["strict"] for d in ext), "ext_genuine": eg,
                            "ext_gamed": eb})
        # the pre-registered extension cell is the checkpoint just before F1 (s2300 if never reached); extra draws in any
        # other cell (ifbench_170's s1600 cell, extended before an audit moved its F1) are reported, not used
        pre = (cells.CKPTS[cells.CKPTS.index(stt["F1"]) - 1] if stt["F1"] else "s2300")
        ext_info = ext_cells.get(pre, {})
        extra_ext = sorted(c for c in ext_cells if c != pre)
        # F1*: the extension cell before F1 (or s2300 for never) with a genuine success
        if ext_info and ext_info.get("ext_genuine", 0) >= 1:
            ec = ext_info["ext_ckpt"]
            if f1star is None or cells.STEP[ec] < cells.STEP[f1star]:
                f1star = ec
        order = cells.CKPTS[1:]
        cat = "never"
        if f1star:
            if stt["F25"] is None:
                cat = "slow"
            else:
                i1, i25 = order.index(f1star), order.index(stt["F25"])
                prev = cells.CKPTS[cells.CKPTS.index(f1star) - 1]
                prev_zero = (prev == "dpo") or (ext_info.get("ext_ckpt") == prev and ext_info.get("ext_genuine", 0) == 0
                                                and ext_info.get("ext_unlabelled", 1) == 0 and ext_info.get("ext_n") == cells.N_X)
                if i1 == i25 and prev_zero:
                    cat = "abrupt"
                elif i25 - i1 - 1 >= 2:
                    cat = "gradual"
                else:
                    cat = "intermediate"
        rate_at = None
        if f1star:
            dr = cells.draws(f1star, p, "B")
            gg = sum(1 for d in dr if d["strict"] and L.label(d)[0] == "genuine")
            rate_at = gg / len(dr) if dr else None
        em_rows.append({"pid": p, "class": cls[p], "class_154rule3": cls_alt[p],
                        "F1": stt["F1"] or "", "F2": stt["F2"] or "", "F1star": f1star or "", "F25": stt["F25"] or "",
                        "F1_step": cells.STEP[stt["F1"]] if stt["F1"] else NEVER,
                        "F2_step": cells.STEP[stt["F2"]] if stt["F2"] else NEVER,
                        "category": cat, "rate_at_F1star": r6(rate_at), "blocked": stt["blocked"].strip(),
                        **{f"ext_{k}": v for k, v in ext_info.items()}, "extra_ext_cells": " ".join(extra_ext),
                        **{f"rate_{c}": r6(v) for c, v in rates.items()}})
    if em_rows:
        keys = []
        for r in em_rows:
            keys += [k for k in r if k not in keys]
        with open(O / "emergence.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(em_rows)
    # reading 1: timing by class
    timing = {}
    for nm, cm in (("primary", cls), ("ifbench_154_rule3", cls_alt)):
        for fk in ("F1_step", "F2_step"):
            vals = {k: np.array([r[fk] for r in em_rows if cm[r["pid"]] == k], dtype=float) for k in "PTN"}
            med = {k: float(np.median(v)) for k, v in vals.items()}
            rest = np.concatenate([vals["T"], vals["N"]])
            reps = []
            for _ in range(REPS):
                bp = rng.choice(vals["P"], len(vals["P"]))
                bt = rng.choice(vals["T"], len(vals["T"]))
                bn = rng.choice(vals["N"], len(vals["N"]))
                reps.append(np.median(np.concatenate([bt, bn])) - np.median(bp))
            lo, hi = boot_ci(reps, 5, 95)
            order_ok = med["P"] < med["T"] <= med["N"]
            timing[f"{nm}:{fk}"] = {"median": med, "n": {k: int(len(v)) for k, v in vals.items()},
                                    "median_rest": float(np.median(rest)), "diff_rest_minus_P": float(np.median(rest) - med["P"]),
                                    "lo90": lo, "hi90": hi, "order_holds": bool(order_ok),
                                    "reading": "habit first" if (order_ok and lo > 0) else "no order"}
    summary["timing"] = timing
    cats = {}
    for r in em_rows:
        cats.setdefault(r["category"], {"all": 0, "P": 0, "T": 0, "N": 0})
        cats[r["category"]]["all"] += 1
        cats[r["category"]][r["class"]] += 1
    summary["categories"] = cats
    ra = [r["rate_at_F1star"] for r in em_rows if r["rate_at_F1star"] is not None]
    summary["rate_at_F1star_median"] = r6(st.median(ra)) if ra else None

    # ------------------------------------------------------------------ arm C (gaming)
    samp, two = hand.armc_sample()
    gam_rows = []
    by_ck = {}
    for c, ds in samp.items():
        labs = [(d, L.label(d)) for d in ds]
        lab_ok = [(d, lab, s_) for d, (lab, s_) in labs if lab]
        g = sum(1 for _, lab, _ in lab_ok if lab == "gamed")
        by_ck[c] = [(d["pid"], lab == "gamed") for d, lab, _ in lab_ok]
        srcs = {}
        for _, _, s_ in lab_ok:
            srcs[s_] = srcs.get(s_, 0) + 1
        # arm B secondary: first-4 labels per cell
        bn = sum(cell_share.get((c, p), (0, 0))[0] for p in R)
        bg = sum(cell_share.get((c, p), (0, 0))[1] for p in R)
        gam_rows.append({"ckpt": c, "step": cells.STEP[c], "armC_sample": len(ds), "armC_labelled": len(lab_ok),
                         "armC_gamed": g, "armC_share": r6(g / len(lab_ok)) if lab_ok else None,
                         "armC_sources": json.dumps(srcs), "armB_first4_labelled": bn, "armB_first4_gamed": bg,
                         "armB_share": r6(bg / bn) if bn else None})
    with open(O / "gaming.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gam_rows[0]))
        w.writeheader()
        w.writerows(gam_rows)

    def pooled_diff(groupE, groupL, items):
        e = [x for c in groupE for x in items.get(c, [])]
        l_ = [x for c in groupL for x in items.get(c, [])]
        if not e or not l_:
            return None
        se, sl = np.mean([x[1] for x in e]), np.mean([x[1] for x in l_])

        def clus(xs):
            d = {}
            for pid, v in xs:
                d.setdefault(pid, []).append(v)
            return list(d.values())
        ce, cl = clus(e), clus(l_)
        reps = []
        for _ in range(REPS):
            be = [ce[i] for i in rng.integers(0, len(ce), len(ce))]
            bl = [cl[i] for i in rng.integers(0, len(cl), len(cl))]
            fe = np.mean([v for g in be for v in g])
            fl = np.mean([v for g in bl for v in g])
            reps.append(fe - fl)
        lo, hi = boot_ci(reps, 5, 95)
        d = se - sl
        reading = "gaming first" if d >= 0.2 else ("gaming grows" if -d >= 0.2 else "flat")
        return {"early": r6(se), "late": r6(sl), "n_early": len(e), "n_late": len(l_), "diff_early_minus_late": r6(d),
                "lo90": r6(lo), "hi90": r6(hi), "reading": reading}
    summary["gaming_armC"] = pooled_diff(EARLY_C, LATE, by_ck)
    itemsB = {}
    for (c, p), (n_, gm) in cell_share.items():
        itemsB.setdefault(c, []).extend([(p, True)] * gm + [(p, False)] * (n_ - gm))
    summary["gaming_armB"] = pooled_diff(EARLY_B, LATE, itemsB)

    # ------------------------------------------------------------------ arm D (lengths) and brevity
    len_rows = []
    m_words = {}
    for c in present:
        for setname, pids, arm in (("armA_all", AA, "A"), ("reach42_armA", [p for p in AA if p in R], "A"),
                                   ("reach48_armB", R, "B")):
            ds = [d for p in pids for d in (cells.draws(c, p, arm)[:cells.N_B] if arm == "B" else cells.draws(c, p, arm))]
            if not ds:
                continue
            wa = [d for d in ds if d["think_end"]]
            row = {"ckpt": c, "step": cells.STEP[c], "set": setname, "draws": len(ds),
                   "think_tok_median": r6(st.median(d["think_tok"] for d in ds)),
                   "ans_tok_median": r6(st.median(d["ans_tok"] for d in wa)) if wa else None,
                   "think_words_median": r6(st.median(d["think_words"] for d in ds)),
                   "ans_words_median": r6(st.median(d["ans_words"] for d in wa)) if wa else None,
                   "resp_tok_mean": r6(st.mean(d["n_tok"] for d in ds)),
                   "cut_share": r6(sum(d["finish"] == "length" for d in ds) / len(ds)),
                   "no_think_end_share": r6(sum(1 - d["think_end"] for d in ds) / len(ds))}
            len_rows.append(row)
            if setname == "armA_all":
                m_words[c] = row["ans_words_median"]
    with open(O / "lengths.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(len_rows[0]))
        w.writeheader()
        w.writerows(len_rows)
    if "s2300" in m_words and len(m_words) == len(cells.CKPTS):
        ref = m_words["s2300"]
        B = None
        for i, c in enumerate(cells.CKPTS):
            if all(abs(m_words[x] - ref) <= 0.2 * ref for x in cells.CKPTS[i:]):
                B = c
                break
        H = None
        for c in cells.CKPTS[1:]:
            if sum(1 for r in em_rows if r["F2_step"] <= cells.STEP[c]) >= 24:
                H = c
                break
        summary["brevity"] = {"m_words": m_words, "B": B, "H": H,
                              "reading": "brevity first" if (B and (H is None or cells.STEP[B] < cells.STEP[H]))
                              else "not brevity first"}
    with open(O / "results.csv", "w", newline="") as fh:
        keys = []
        for r in results:
            keys += [k for k in r if k not in keys]
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(results)
    json.dump(summary, open(O / "summary.json", "w"), indent=1)
    print(json.dumps({k: summary[k] for k in summary if k in ("armA", "shape", "categories", "gaming_armC", "brevity")},
                     indent=None)[:3000])


if __name__ == "__main__":
    main()
