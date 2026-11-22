"""Readings 1-4 and expectations 1-10 of run olmo-ifcurve from my labels (rvc_hand), my re-grade and arm A (armA.json).

Reading 1 (timing): F1 per prompt (step; never = 9999), numpy medians per olmo-ifladder class (P / T / N from
classify.csv `reading`); "habit first" iff med_P < med_T <= med_N and the 5th percentile of the stratified prompt
bootstrap (10,000; P, T and N resampled within class, T and N pooled) of med(T u N) - med(P) is > 0; also with F2 and
with ifbench_154 in P.
Reading 2 (gradual / abrupt), per prompt with F1* <= 2300: abrupt = F1* = F25 and the checkpoint before F1* at 0 of
>= 128 (or dpo's 0 in >= 256); gradual = >= 2 sampled checkpoints strictly between F1* and F25; intermediate = F25
exists, neither; slow = no F25. Earliest detectable rate = genuine / draws at F1* (extension cell: k / 128; base cell:
my estimated rate).
Reading 3 (gaming): gamed / labelled among strict successes; primary = my arm-C sub-sample (20 per checkpoint), early
{dpo, 50, 100, 200} vs late {1100, 1600, 2300} pooled, prompt-cluster bootstrap 90 %; secondary = arm-B cells' first
min(strict, 4) labels, early {50, 100, 200}, late as above (labelled prefixes only).
Reading 4 (brevity): B from armA.json; H = first checkpoint by which >= 24 of 48 have F2 <= c.
Estimated genuine rate of a cell = (genuine labelled + unlabelled strict x genuine share of its labelled prefix) / n.
Writes out/readings.txt / .json and out/emergence.csv (my per-prompt table).
"""
import collections
import csv
import json
import sys

import numpy as np

import rvc_hand as H
from rvc_core import OUT, RAW, SCR, STEP, Tee, dump, load_csv

NEVER = 9999
CK, CKA = H.CK, H.CKA


def klass(reading):
    s = reading.lower()
    return "P" if s.startswith("prompt-") else "T" if s.startswith("teachable") else "N" if s.startswith("neither") else "?"


CLS = {r["pid"]: klass(r["reading"]) for r in load_csv(RAW / "olmo_ifladder" / "classify.csv")}
ST = lambda c: NEVER if c is None else STEP[c]


def cell_counts(p, c, lab, keys):
    """(n draws, strict, labelled genuine, labelled gamed, unlabelled strict, prefix share genuine)"""
    g = m = u = 0
    pref = []
    for k in keys:
        v = lab(k)
        if v == "genuine":
            g += 1
        elif v == "gamed":
            m += 1
        else:
            u += 1
        if v is not None and (not pref or pref[-1] is not None):
            pref.append(v)
        else:
            pref.append(None)
    lab_pref = [v for v in pref if v is not None]
    share = (sum(v == "genuine" for v in lab_pref) / len(lab_pref)) if lab_pref else None
    return g, m, u, share


def boot_med_diff(vals, cls, groups_a, groups_b, nb=10000, seed=7):
    rng = np.random.default_rng(seed)
    arr = {c: np.array([v for v, k in zip(vals, cls) if k == c], dtype=float) for c in set(cls)}
    out = np.empty(nb)
    for b in range(nb):
        a = np.concatenate([rng.choice(arr[c], size=len(arr[c])) for c in groups_a])
        bb = np.concatenate([rng.choice(arr[c], size=len(arr[c])) for c in groups_b])
        out[b] = np.median(bb) - np.median(a)
    return out


def fm(x, f="{:.4f}"):
    return "NA" if x is None else f.format(x)


def variant_labels(name):
    """Label sets for the sensitivity runs: 'final' (mine); 'rule6strict' (ALL-CAPS title-case answers confirmed
    genuine under rule 6 count as not successes); 'r7literal' (also: per-sentence answers whose checker sees <= 1
    sentence are gamed even when the visible lines meet the rule in substance; rule 7's literal example);
    'firstread' (each group's first reader label only; screen labels kept; no second reads, no confirmations);
    'noADJ4' (without the prompt-level rule 10-12 pass); 'noR5' (without the rule-5 pass and the rule 10-12 pass)."""
    L = H.labels(exclude_rounds={"noR5": ("R5", "ADJ4"), "noADJ4": ("ADJ4",)}.get(name, ()))
    if name == "firstread":
        rd = H.reads()
        L = {g: {"label": rs[0][1], "how": "first read", "n_reads": 1, "labs": [rs[0][1]]} for g, rs in rd.items()}
    if name in ("rule6strict", "r7literal"):
        conf = json.load(open(H.HAND / "confirm.json")) if (H.HAND / "confirm.json").exists() else {}
        for gs, c in conf.items():
            rules = c["reason"].split(" (", 1)[0].replace("rule ", "").split(";")
            g = tuple(json.loads(gs))
            if c["label"] == "genuine" and "6" in rules and g in L:
                L[g]["label"] = "gamed"
    if name == "adjall":   # every adjudicator proposal accepted, including the low-confidence majority overturns
        import glob
        rej = json.load(open(H.HAND / "adj_rejected.json"))
        rejected = {i for k, v in rej.items() if k != "policy" for i in v}
        rd = H.reads()
        byitem = {r[4]: g for g, rs in rd.items() for r in rs}
        for f in sorted(glob.glob(str(SCR / "adjud" / "ADJ*_*.json"))):
            for x in json.load(open(f)):
                if x["item"] in rejected and byitem.get(x["item"]) in L:
                    L[byitem[x["item"]]]["label"] = x["proposed"]
    if name == "r7literal":
        aud = json.load(open(OUT / "audit.json"))
        for f in aud:
            g = tuple(f["group"])
            if f["label"] == "genuine" and f["shape"].get("n_sent_checker", 9) <= 1 and g in L:
                L[g]["label"] = "gamed"
    return L


def main(variant="final"):
    T = Tee("readings.txt" if variant == "final" else f"readings_{variant}.txt")
    L = variant_labels(variant)
    lab = H.lab_fn(L)
    armA = json.load(open(OUT / "armA.json"))
    res = {"prompts": {}}
    incomplete = []
    for p in H.REACH:
        w = H.walk(p, lab)
        if not w["complete"]:
            incomplete.append(p)
        cells = {}
        for c in CK:
            keys = H.B[c][p]
            g, m, u, share = cell_counts(p, c, lab, keys)
            est = (g + (u * share if share is not None else 0)) / 32
            cells[c] = {"n": 32, "strict": len(keys), "gen": g, "gam": m, "unl": u, "est": est}
        for c, ks in H.X.get(p, {}).items():
            g, m, u, share = cell_counts(p, c, lab, ks)
            bg = cells[c]["gen"]
            cells[c].update({"x_n": 96, "x_strict": len(ks), "x_gen": g, "x_unl": u,
                             "all_n": 128, "all_gen": bg + g})
        res["prompts"][p] = {"cls": CLS[p], "F1": w["F1"], "F2": w["F2"], "F25": w["F25"], "F1s": w["F1s"],
                             "F1s_all": w["F1s_all"], "ext_design": w["ext_design"], "ext_present": w["ext_present"],
                             "complete": w["complete"], "cells": cells, "xckpt": list(H.X.get(p, {}).keys())}
    T(f"prompts whose walk is not complete (labels pending): {len(incomplete)} {incomplete}")
    P = res["prompts"]
    # ---------------- extension placement vs my F1 (pre-registered: the checkpoint just before F1; never -> s2300)
    T("\nEXTENSION PLACEMENT (executor's extension cells vs the checkpoint before my F1)")
    mism = []
    for p in P:
        f1 = P[p]["F1"]
        want = "dpo" if f1 == "s0050" else ("s2300" if f1 is None else CKA[CKA.index(f1) - 1])
        have = P[p]["xckpt"]
        P[p]["ext_expected"] = want
        if want == "dpo":
            ok = not have
        else:
            ok = want in have
        if not ok or len(have) > 1:
            mism.append((p, f1, want, have))
    T(f"   prompts whose extension cell is not (only) the checkpoint before my F1: {len(mism)}")
    for m in mism:
        T(f"      {m[0]}: my F1 {m[1]}, expected extension at {m[2]}, extension draws at {m[3]}")
    res["ext_mismatch"] = mism
    # ---------------- never reached: tries and bounds
    nev = [p for p in P if P[p]["F1s"] is None]
    T(f"   never reached (no genuine in any base cell or extension): {nev}")
    for p in nev:
        c = P[p]["cells"]["s2300"]
        T(f"      {p}: 0 genuine in 8 x 32 base draws + 96 extension draws at s2300 ({c.get('all_n', 32)} at s2300); "
          f"0 of {c.get('all_n', 32)} at s2300 -> rate < {1 - 0.05 ** (1 / c.get('all_n', 32)):.3f} (95 %)")
    # ---------------- reading 1
    T("\nREADING 1 (timing by class; steps; never = 9999)")
    for var in ("F1", "F2"):
        for move154 in (False, True):
            cl = {p: ("P" if (move154 and p == "ifbench_154") else P[p]["cls"]) for p in P}
            vals = [ST(P[p][var]) for p in P]
            cls = [cl[p] for p in P]
            med = {c: float(np.median([v for v, k in zip(vals, cls) if k == c])) for c in "PTN"}
            bs = boot_med_diff(vals, cls, ["P"], ["T", "N"])
            obs = float(np.median([v for v, k in zip(vals, cls) if k in "TN"]) - med["P"])
            lo, hi = np.percentile(bs, [5, 95])
            habit = med["P"] < med["T"] <= med["N"] and lo > 0
            tag = f"{var}{' (154 in P)' if move154 else ''}"
            res[f"r1_{var}_{'154P' if move154 else 'prim'}"] = {"med": med, "obs": obs, "ci90": [float(lo), float(hi)],
                                                                "habit_first": habit,
                                                                "n": dict(collections.Counter(cls))}
            T(f"   {tag:16s} medians P {med['P']:.0f} T {med['T']:.0f} N {med['N']:.0f} | med(TuN) - med(P) = {obs:.0f}, "
              f"90 % [{lo:.0f}, {hi:.0f}] | {'HABIT FIRST' if habit else 'no order'}  n={dict(collections.Counter(cls))}")
    T("   F1 distribution by class:")
    for c in "PTN":
        T(f"      {c}: {dict(sorted(collections.Counter(ST(P[p]['F1']) for p in P if P[p]['cls'] == c).items()))}")
    # ---------------- reading 2
    T("\nREADING 2 (gradual / abrupt), prompts with F1* <= 2300")
    cat = {}
    rates = {}
    for p in P:
        f1s, f25 = P[p]["F1s"], P[p]["F25"]
        if f1s is None:
            cat[p] = "never"
            continue
        i = CKA.index(f1s)
        prev = CKA[i - 1]
        if prev == "dpo":
            prev_zero = True
            prev_desc = "dpo 0 in >= 256"
        else:
            pc = P[p]["cells"][prev]
            prev_zero = pc.get("all_n", 32) >= 128 and pc.get("all_gen", pc["gen"]) == 0 and pc.get("x_unl", 0) == 0
            prev_desc = f"{prev} {pc.get('all_gen', pc['gen'])}/{pc.get('all_n', 32)}"
        if f25 is None:
            cat[p] = "slow"
        elif f25 == f1s and prev_zero:
            cat[p] = "abrupt"
        elif sum(1 for c in CK if STEP[f1s] < STEP[c] < STEP[f25]) >= 2:
            cat[p] = "gradual"
        else:
            cat[p] = "intermediate"
        c = P[p]["cells"][f1s]
        if "all_n" in c:   # F1* at an extension checkpoint: all 128 draws (base part estimated, extension fully read)
            rates[p] = (round(c["est"] * 32 + c["x_gen"], 2), 128)
        else:
            rates[p] = (round(c["est"] * 32, 2), 32)
        P[p]["cat"] = cat[p]
        P[p]["prev_desc"] = prev_desc
        P[p]["rate_F1s"] = rates[p]
    cnt = collections.Counter(cat.values())
    T(f"   categories: {dict(cnt)}")
    for c in "PTN":
        T(f"      class {c}: {dict(collections.Counter(cat[p] for p in P if P[p]['cls'] == c))}")
    withf25 = [p for p in P if P[p]["F25"] is not None and P[p]["F1s"] is not None]
    rr = [rates[p][0] / rates[p][1] for p in P if p in rates]
    res["r2"] = {"cat": cat, "counts": dict(cnt), "n_withF25": len(withf25),
                 "share_gradual": sum(cat[p] == "gradual" for p in withf25) / max(1, len(withf25)),
                 "share_abrupt": sum(cat[p] == "abrupt" for p in withf25) / max(1, len(withf25)),
                 "median_rate_F1s": float(np.median(rr)) if rr else None}
    T(f"   of {len(withf25)} with F25 <= 2300: gradual {res['r2']['share_gradual']:.2f}, abrupt {res['r2']['share_abrupt']:.2f}; "
      f"median earliest detectable rate {fm(res['r2']['median_rate_F1s'])} (3/32 = {3 / 32:.4f})")
    # ---------------- reading 3
    T("\nREADING 3 (gaming among strict successes)")
    share_by = {}
    for c in CKA:
        ks = H.ARMC[c]
        v = [lab(k) for k in ks]
        lb = [x for x in v if x]
        share_by[c] = (sum(x == "gamed" for x in lb), len(lb), len(ks))
    T("   arm C (my sub-sample of 20 per checkpoint): gamed / labelled (of sampled) " +
      " ".join(f"{c}:{a}/{b}({n})" for c, (a, b, n) in share_by.items()))
    early, late = ["dpo", "s0050", "s0100", "s0200"], ["s1100", "s1600", "s2300"]

    def pooled(group, items):
        lb = [(k, lab(k)) for c in group for k in items[c]]
        lb = [(k, v) for k, v in lb if v]
        return sum(v == "gamed" for _, v in lb) / len(lb) if lb else None, lb

    def cluster_boot(items_e, items_l, nb=10000, seed=11):
        pids = sorted({k[1] for k, _ in items_e + items_l})
        ix = {p: i for i, p in enumerate(pids)}
        E = np.zeros((len(pids), 2))
        Lm = np.zeros((len(pids), 2))
        for k, v in items_e:
            E[ix[k[1]]] += [v == "gamed", 1]
        for k, v in items_l:
            Lm[ix[k[1]]] += [v == "gamed", 1]
        rng = np.random.default_rng(seed)
        d = np.empty(nb)
        for b in range(nb):
            s = rng.integers(0, len(pids), len(pids))
            e = E[s].sum(0)
            l = Lm[s].sum(0)
            d[b] = (e[0] / e[1] if e[1] else np.nan) - (l[0] / l[1] if l[1] else np.nan)
        return np.nanpercentile(d, [5, 95])

    se, ie = pooled(early, H.ARMC)
    sl, il = pooled(late, H.ARMC)
    if se is None or sl is None:
        T("   primary: not enough labels yet")
        dump(res, "readings.json")
        return
    lo, hi = cluster_boot(ie, il)
    rd = "gaming first" if se - sl >= 0.2 else "gaming grows" if sl - se >= 0.2 else "flat"
    res["r3_primary"] = {"early": se, "late": sl, "n_early": len(ie), "n_late": len(il), "diff": se - sl,
                         "ci90": [float(lo), float(hi)], "reading": rd, "by_ckpt": share_by}
    if se is None or sl is None:
        T("   primary: not enough labels yet")
        dump(res, "readings.json")
        return
    T(f"   primary: early {se:.3f} (n {len(ie)}), late {sl:.3f} (n {len(il)}), early - late {se - sl:+.3f} "
      f"90 % [{lo:+.3f}, {hi:+.3f}] -> {rd}")
    # reader-only (screen and inheritance excluded)
    def reader_only(items):
        out = []
        for k, v in items:
            src = H.source(L, k)
            if src not in ("screen", "unlabelled"):
                out.append((k, v))
        return out
    re_, rl_ = reader_only(ie), reader_only(il)
    if re_ and rl_:
        T(f"   primary, reader-labelled only: early {sum(v == 'gamed' for _, v in re_) / len(re_):.3f} (n {len(re_)}), "
          f"late {sum(v == 'gamed' for _, v in rl_) / len(rl_):.3f} (n {len(rl_)})")
    first4 = {c: [k for p in H.REACH for k in H.B[c][p][:4]] for c in CK}
    e2, l2 = ["s0050", "s0100", "s0200"], ["s1100", "s1600", "s2300"]
    se2, ie2 = pooled(e2, first4)
    sl2, il2 = pooled(l2, first4)
    cov = {c: (sum(1 for k in first4[c] if lab(k)), len(first4[c])) for c in CK}
    if ie2 and il2:
        lo2, hi2 = cluster_boot(ie2, il2)
        rd2 = "gaming first" if se2 - sl2 >= 0.2 else "gaming grows" if sl2 - se2 >= 0.2 else "flat"
        res["r3_secondary"] = {"early": se2, "late": sl2, "n_early": len(ie2), "n_late": len(il2), "ci90": [float(lo2), float(hi2)],
                               "reading": rd2, "coverage": cov}
        T(f"   secondary (arm B first min(strict,4), labelled): early {se2:.3f} (n {len(ie2)}), late {sl2:.3f} (n {len(il2)}), "
          f"diff {se2 - sl2:+.3f} 90 % [{lo2:+.3f}, {hi2:+.3f}] -> {rd2}; labelled / first-4 items per ckpt {cov}")
    # ---------------- reading 4
    T("\nREADING 4 (brevity)")
    Bc = armA["brevity_B"]
    Hc = None
    for c in CK:
        if sum(1 for p in P if P[p]["F2"] is not None and STEP[P[p]["F2"]] <= STEP[c]) >= 24:
            Hc = c
            break
    res["r4"] = {"B": Bc, "H": Hc, "brevity_first": (Hc is None or STEP[Bc] < STEP[Hc])}
    T(f"   B = {Bc}; H = {Hc} (F2 <= c on >= 24 of 48); {'BREVITY FIRST' if res['r4']['brevity_first'] else 'not brevity first'}")
    T("   prompts with F2 <= c: " + " ".join(f"{c}:{sum(1 for p in P if P[p]['F2'] is not None and STEP[P[p]['F2']] <= STEP[c])}" for c in CK))
    # ---------------- expectations 4-8 (1-3, 9, 10 are in armA.txt)
    T("\nEXPECTATIONS (labels-dependent)")
    anyg = {c: sum(1 for p in P if P[p]["cells"][c]["gen"] + P[p]["cells"][c].get("x_gen", 0) > 0) for c in CK}
    anyg_base = {c: sum(1 for p in P if P[p]["cells"][c]["gen"] > 0) for c in CK}
    T(f"   4a prompts with any genuine (base + extension) by ckpt: {anyg}; base only: {anyg_base}")
    f1le750 = sum(1 for p in P if ST(P[p]["F1"]) <= 750)
    T(f"   4b F1 <= 750 on {f1le750} of 48 (expected 28-36)")
    g1 = sum(1 for p in P if P[p]["cells"]["s2300"]["gen"] >= 1)
    g2 = sum(1 for p in P if P[p]["cells"]["s2300"]["gen"] >= 2)
    unk = [p for p in P if P[p]["cells"]["s2300"]["gen"] < 2 and P[p]["cells"]["s2300"]["unl"] > 0]
    T(f"   4c s2300 (B_s2300 new draws): >= 1 genuine on {g1}, >= 2 on {g2} of 48 (expected >= 44 / >= 40); "
      f"prompts with < 2 genuine and unlabelled strict left: {unk}")
    res["exp4"] = {"anyg": anyg, "anyg_base": anyg_base, "f1le750": f1le750, "s2300_g1": g1, "s2300_g2": g2}
    m = res["r1_F1_prim"]["med"]
    T(f"   5  medians F1 P {m['P']:.0f} (<= 500?) T {m['T']:.0f} (in 500, 750?) N {m['N']:.0f} (>= 1100?); reading "
      f"{'habit first' if res['r1_F1_prim']['habit_first'] else 'no order'} (expected habit first)")
    T(f"   6  of {len(withf25)} with F25: gradual {res['r2']['share_gradual']:.2f} (>= 0.5?), abrupt "
      f"{res['r2']['share_abrupt']:.2f} (<= 0.2?), median rate at F1* {fm(res['r2']['median_rate_F1s'])} (<= 0.0938?)")
    T(f"   7  arm C early {se:.3f} late {sl:.3f} (each in [0.05, 0.30]?), reading {rd} (expected flat); secondary "
      f"{res.get('r3_secondary', {}).get('reading')} (expected gaming first: early >= 0.5 if >= 10 items, late <= 0.35)")
    T(f"   8  B {Bc} (in 1100, 1600?) H {Hc} (in 750, 1100?) -> {'brevity first' if res['r4']['brevity_first'] else 'not brevity first'} (expected not)")
    # estimated genuine pass@1 (arm A)
    T("\nestimated genuine pass@1 (arm A strict pass@1 x (1 - my arm-C gamed share)):")
    for c in CKA:
        a, b, n = share_by[c]
        if b:
            p1 = armA["pass"][f"{c}_p1"][0]
            T(f"   {c}: strict {p1:.3f} x (1 - {a}/{b}) = {p1 * (1 - a / b):.3f}")
    # per-prompt table
    with open(OUT / ("emergence.csv" if variant == "final" else f"emergence_{variant}.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["pid", "class", "F1", "F2", "F1s", "F25", "category", "rate_at_F1s", "ext_ckpt"] +
                    [f"{c}_strict/gen/gam/unl/est" for c in CK])
        for p in H.REACH:
            r = P[p]
            wr.writerow([p, r["cls"], ST(r["F1"]), ST(r["F2"]), ST(r["F1s"]), ST(r["F25"]), r.get("cat", "never"),
                         "%s/%s" % r["rate_F1s"] if "rate_F1s" in r else "", "+".join(r["xckpt"])] +
                        [f"{r['cells'][c]['strict']}/{r['cells'][c]['gen']}/{r['cells'][c]['gam']}/{r['cells'][c]['unl']}/"
                         f"{r['cells'][c]['est']:.3f}" for c in CK])
    dump(res, "readings.json" if variant == "final" else f"readings_{variant}.json")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "final")
