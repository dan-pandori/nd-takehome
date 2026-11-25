"""olmo-weights analysis (VPS-side, csv + numpy): aggregate the engine's per-tensor statistics into tables, run the
merge / start / duplicate tests, the LoRA comparison and score the pre-registered expectations.

Reads  artifacts/olmo_weights/stats/<job>/ (engine output), olmo_weights/manifest/{checkpoints.csv,jobs.json}.
Writes artifacts/olmo_weights/tables/:
  intervals.csv          one row per chain interval (all jobs): family, job, chain, idx, a, b, kind, stage, steps,
                         lr_mean, rel (= ||d|| / ||theta_a||), rel_per_step, rel_per_step_per_lr, norm_d, norm_a,
                         frac_eq, frac_ulp (<= 1 ulp incl. equal), cos_lag1, cos_lag2, dist_start_rel, frac_eq_start,
                         frac_ulp_start, main_path
  modules.csv / layers.csv   the same core quantities per module type / per layer for every interval
  chains.csv             per training stretch: start, end, n_intervals, path, end distance, straightness (native and
                         matched-count), mean consecutive cosine
  tests.json             merge residuals, DPO-start soup fit, stage-3 / 7B start tests, mains, RL-Zero duplicates
  lora.csv / lora_modules.csv / lora_layers.csv   LoRA vs RL cosines and norm ratios per RL checkpoint
  expectations.json      E1-E5, G1-G7 scored against their pre-registered definitions
Usage: python3 olmo_weights/analyze.py [--stats DIR] [--out DIR]
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agg  # noqa: E402
import lr as LR  # noqa: E402

MAN = "olmo_weights/manifest"
CK = {r["label"]: r for r in csv.DictReader(open(f"{MAN}/checkpoints.csv"))}
JOBS = json.load(open(f"{MAN}/jobs.json"))
DPO_STEPS = {"32B": 1563, "7B": 1172}          # report Table 48: 200 K / 150 K pairs, 1 epoch, batch 128
MERGES = {"32B/s2merge", "32B/s3merge"}


def step_of(x):
    s = CK[x]["step"]
    return int(s) if s not in ("", "None", None) else None


def stage_of(x):
    return CK[x]["stage"]


def lr_stage(x):
    """LR-schedule stage name of checkpoint x (lr.py)."""
    st, lab = stage_of(x), x
    if st == "sft":
        return "sft-1e-4" if "/sft1e-4/" in lab else ("sft-5e-5" if "/sft5e-5/" in lab else "sft")
    if st.startswith("rlzero"):
        return "rlzero"
    return st


def classify(chain, a, b, fam):
    """-> (kind, stage, steps, s0, s1) for interval a -> b. s0/s1: optimizer steps within b's stage for the LR mean."""
    sa, sb = stage_of(a), stage_of(b)
    pa, pb = step_of(a), step_of(b)
    if chain == "pair":
        return "test-pair", sb, None, None, None
    if b in MERGES:
        return "merge", sb, 0, None, None
    if sb == "dpo":
        return "dpo", "dpo", DPO_STEPS[fam], 0, DPO_STEPS[fam]
    if pb is None:
        return "main", sb, None, None, None
    if sa == sb and a not in MERGES and not (sa == "sft" and "/sftmain" in a):
        if pa is None:
            return "main", sb, None, None, None
        if sb == "stage1":
            return ("pair" if pb - pa <= 1000 else "gap"), sb, pb - pa, pa, pb
        return "within", sb, pb - pa, pa, pb
    # stage boundary (or the first interval after a merge / DPO): training steps of the new stage = b's own step
    return "boundary", sb, pb, 0, pb


def main_path(fam, job, chain, a, b):
    """Is interval a -> b on the released pipeline path (Figure 1's main line)?"""
    if fam == "32B":
        if chain in ("stage1-sampled", "ingredient1", "stage3", "rl", "sftmain-to-dpo"):
            return True
        if chain == "sft-5e-5":
            return True
        return False
    if fam == "7B":
        return chain in ("stage1-sampled", "stage2", "stage3", "sft-dpo", "rl")
    return False


def chain_members(job, chain):
    for c in JOBS[job]["chains"]:
        if c["name"] == chain:
            return c
    return None


# ------------------------------------------------------------------------------------------------------- intervals
def job_tables(job, D):
    fam = CK[JOBS[job]["members"][0]]["family"]
    iv = agg.sums(D["iv"], ["d2", "na2", "nb2", "n_eq", "n_ulp", "numel", "n_nonfinite"], by=["chain", "idx", "a", "b"])
    lag = agg.sums(D["lag"], ["dot"], by=["chain", "idx", "lag"])
    st = agg.sums(D["st"], ["o2", "n_eq_s", "n_ulp_s", "dot_prev"], by=["chain", "idx", "s", "b"])
    rows = []
    d2_of = {(c, int(i)): v["d2"] for (c, i, a, b), v in iv.items()}
    na2_start = {}
    for (c, i, a, b), v in iv.items():
        if int(i) == 1 and c != "pair":
            na2_start[c] = v["na2"]
    for (c, i, a, b), v in sorted(iv.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        i = int(i)
        kind, stage, steps, s0, s1 = classify(c, a, b, fam)
        lrm = LR.mean_lr(fam, lr_stage(b), s0, s1) if s0 is not None else None
        rel = math.sqrt(v["d2"] / v["na2"]) if v["na2"] > 0 else float("nan")
        r = dict(family=fam, job=job, chain=c, idx=i, a=a, b=b, kind=kind, stage=stage, steps=steps, lr_mean=lrm,
                 rel=rel, rel_per_step=(rel / steps if steps else None),
                 rel_per_step_per_lr=(rel / steps / lrm if steps and lrm else None),
                 norm_d=math.sqrt(v["d2"]), norm_a=math.sqrt(v["na2"]), norm_b=math.sqrt(v["nb2"]),
                 frac_eq=v["n_eq"] / v["numel"], frac_ulp=v["n_ulp"] / v["numel"], numel=v["numel"],
                 n_nonfinite=v["n_nonfinite"], main_path=main_path(fam, job, c, a, b))
        for L in (1, 2):
            dv = lag.get((c, str(i), str(L)))
            prev = d2_of.get((c, i - L))
            r[f"cos_lag{L}"] = dv["dot"] / math.sqrt(v["d2"] * prev) if dv and prev and v["d2"] > 0 and prev > 0 else None
        sv = [x for (cc, ii, s, bb), x in st.items() if cc == c and int(ii) == i]
        if sv and c in na2_start:
            x = sv[0]
            r["dist_start_rel"] = math.sqrt(x["o2"] / na2_start[c])
            r["frac_eq_start"] = x["n_eq_s"] / v["numel"]
            r["frac_ulp_start"] = x["n_ulp_s"] / v["numel"]
            r["dot_prev_start"] = x["dot_prev"]
            r["o2"] = x["o2"]
        rows.append(r)
    return rows


def group_tables(job, D, by):
    """Per-module or per-layer core quantities for every interval of the job."""
    fam = CK[JOBS[job]["members"][0]]["family"]
    iv = agg.sums(D["iv"], ["d2", "na2", "n_eq", "n_ulp", "numel"], by=["chain", "idx", "a", "b", by])
    st = agg.sums(D["st"], ["o2", "n_eq_s", "n_ulp_s"], by=["chain", "idx", by])
    lag = agg.sums(D["lag"], ["dot"], by=["chain", "idx", "lag", by])
    d2g = {(c, int(i), g): v["d2"] for (c, i, a, b, g), v in iv.items()}
    na2s = {(c, g): v["na2"] for (c, i, a, b, g), v in iv.items() if int(i) == 1}
    out = []
    for (c, i, a, b, g), v in iv.items():
        i = int(i)
        kind, stage, steps, s0, s1 = classify(c, a, b, fam)
        rel = math.sqrt(v["d2"] / v["na2"]) if v["na2"] > 0 else float("nan")
        x = st.get((c, str(i), g))
        dv = lag.get((c, str(i), "1", g))
        prev = d2g.get((c, i - 1, g))
        out.append(dict(family=fam, job=job, chain=c, idx=i, a=a, b=b, kind=kind, stage=stage, steps=steps,
                        **{by: g}, rel=rel, rel_per_step=(rel / steps if steps else None), d2=v["d2"], na2=v["na2"],
                        frac_eq=v["n_eq"] / v["numel"], frac_ulp=v["n_ulp"] / v["numel"], numel=v["numel"],
                        dist_start_rel=(math.sqrt(x["o2"] / na2s[(c, g)]) if x and na2s.get((c, g)) else None),
                        frac_ulp_start=(x["n_ulp_s"] / v["numel"] if x else None),
                        cos_lag1=(dv["dot"] / math.sqrt(v["d2"] * prev) if dv and prev and v["d2"] > 0 and prev > 0
                                  else None)))
    return out


# -------------------------------------------------------------------------------------------------- training stretches
STRETCHES = [  # (family, name, job, chain, first member index, last member label or None = chain end)
    ("32B", "stage 1 (sampled)", "b32_s1", "stage1-sampled", 0, None),
    ("32B", "stage 2, ingredient 1", "b32_s2", "ingredient1", 0, "32B/s2i1/23842"),
    ("32B", "stage 2, ingredient 2 (every 4th)", "b32_s2", "ingredient2", 0, "32B/s2i2/23842"),
    ("32B", "stage 3", "b32_s3", "stage3", 0, "32B/s3/11921"),
    ("32B", "SFT 5e-5 run", "p32_sft", "sft-5e-5", 0, None),
    ("32B", "SFT 1e-4", "p32_sft", "sft-1e-4", 0, None),
    ("32B", "RL", "p32_rl", "rl", 0, None),
    ("7B", "stage 1 (sampled)", "b7_s1", "stage1-sampled", 0, None),
    ("7B", "stage 2", "b7_s2", "stage2", 0, None),
    ("7B", "stage 3", "b7_s3", "stage3", 0, None),
    ("7B", "SFT", "p7_sft", "sft-dpo", 0, "7B/sft/43000"),
    ("7B", "RL", "p7_rl", "rl", 0, "7B/rl/1375"),
    ("7B", "RL-Zero IF", "z7_if", "rlzero-if", 0, "7B/zif/1900"),
    ("7B", "RL-Zero Math", "z7_math", "rlzero-math", 0, "7B/zmath/1900"),
    ("7B", "RL-Zero Code", "z7_code", "rlzero-code", 0, "7B/zcode/2900"),
]


def stretch_rows(IV, exclude=()):
    """Straightness etc. per training stretch. IV: interval rows (with lag dots attached for bridging). Members in
    `exclude` (duplicate branch names) are skipped: the path bridges them with the distance between the members on
    either side (lag dot products for gaps <= 4 intervals, or the distance from the start when bridging from it)."""
    out = []
    for fam, name, job, chain, i0, last in STRETCHES:
        rows = sorted([r for r in IV if r["job"] == job and r["chain"] == chain], key=lambda r: r["idx"])
        if not rows:
            continue
        mem = chain_members(job, chain)["members"]
        end_i = mem.index(last) if last in mem else len(mem) - 1
        by = {r["idx"]: r for r in rows}
        keep = [i for i in range(end_i + 1) if mem[i] not in exclude]
        path, bridged, ok = 0.0, 0, True
        for u, v in zip(keep, keep[1:]):
            if v == u + 1:
                path += by[v]["norm_d"]
            elif u == 0 and by[v].get("o2") is not None:
                path += math.sqrt(by[v]["o2"])
                bridged += 1
            else:
                dd = pair_distance(by, u, v)
                if dd is None:
                    ok = False
                    break
                path += dd
                bridged += 1
        end = by[keep[-1]]
        dist = math.sqrt(end["o2"]) if end.get("o2") is not None else None
        cos1 = [by[i]["cos_lag1"] for i in keep[1:] if by[i].get("cos_lag1") is not None and (i - 1) in keep]
        out.append(dict(family=fam, stretch=name, job=job, chain=chain, start=mem[0], end=mem[keep[-1]],
                        n_intervals=len(keep) - 1, excluded=[mem[i] for i in range(end_i + 1) if mem[i] in exclude],
                        bridged=bridged, path=(path if ok else None), end_distance=dist, norm_start=rows[0]["norm_a"],
                        end_distance_rel=(dist / rows[0]["norm_a"] if dist is not None else None),
                        straightness=(dist / path if ok and dist is not None and path > 0 else None),
                        mean_cos_lag1=(float(np.mean(cos1)) if cos1 else None),
                        median_cos_lag1=(float(np.median(cos1)) if cos1 else None)))
    return out


# --------------------------------------------------------------------------------------------------------- gram tests
def gram_sum(D):
    """Sum each Gram set's per-tensor matrices -> {set: (ref, members, G)}."""
    out = {}
    for r in D["gram"]:
        mem = r["members"].split("|")
        k = len(mem)
        v = np.array([float(x) for x in r["gram_upper"].split()])
        G = np.zeros((k, k))
        iu = np.triu_indices(k)
        G[iu] = v
        G = G + G.T - np.diag(np.diag(G))
        s = r["set"]
        if s in out:
            out[s] = (out[s][0], out[s][1], out[s][2] + G)
        else:
            out[s] = (r["ref"], mem, G)
    return out


def lsq_fit(G, ref_names, target, basis):
    """Least squares target - ref ~ sum_j c_j (basis_j - ref) using Gram entries. Returns (c, residual^2)."""
    ix = {m: i for i, m in enumerate(ref_names)}
    t = ix[target]
    B = [ix[m] for m in basis]
    A = G[np.ix_(B, B)]
    bvec = G[B, t]
    c = np.linalg.solve(A, bvec)
    res2 = G[t, t] - 2 * c @ bvec + c @ A @ c
    return c, res2


def _complete(job, D):
    return D["n_shards_done"] == len(CK[JOBS[job]["members"][0]]["files"].split(";"))


def tests(stats_root):
    T = {}
    _load = agg.load

    def load(job, root):   # tests use complete jobs only
        D = _load(job, root)
        return D if _complete(job, D) else {"iv": [], "gram": [], "lag": [], "st": [], "lora": [], "lora_norms": []}
    # stage-2 merge
    D = load("b32_s2", stats_root)
    if D["gram"]:
        ref, mem, G = gram_sum(D)["0"]
        ix = {m: i for i, m in enumerate(mem)}
        i2, m2 = ix.get("32B/s2i2/23842"), ix["32B/s2merge"]
        if i2 is not None:
            res_half = G[m2, m2] - G[m2, i2] + G[i2, i2] / 4
            w = G[m2, i2] / G[i2, i2]
            res_w = G[m2, m2] - G[m2, i2] ** 2 / G[i2, i2]
            T["stage2_merge"] = dict(ref=ref, d_i1_i2=math.sqrt(G[i2, i2]), d_merge_i1=math.sqrt(G[m2, m2]),
                                     residual_equal_weights=math.sqrt(max(res_half, 0)),
                                     residual_rel_to_d_i1_i2=math.sqrt(max(res_half, 0)) / math.sqrt(G[i2, i2]),
                                     best_weight_on_i2=w, residual_best=math.sqrt(max(res_w, 0)))
    # stage-3 merge and start
    D = load("b32_s3", stats_root)
    if D["gram"]:
        ref, mem, G = gram_sum(D)["0"]
        names = [ref] + mem
        Gf = np.zeros((len(names), len(names)))
        Gf[1:, 1:] = G
        tgt = "32B/s3merge"
        fits = {}
        for basis in (["32B/s3/10000", "32B/s3/11000", "32B/s3/11921"], ["32B/s3/11000", "32B/s3/11921"],
                      ["32B/s3/11921"]):
            c, r2 = lsq_fit(Gf, names, tgt, basis)
            fits["+".join(b.rsplit("/", 1)[1] for b in basis)] = dict(coef=c.tolist(), coef_ref_9000=1 - float(c.sum()),
                                                                      residual=math.sqrt(max(r2, 0)))
        # equal thirds on 10000 / 11000 / 11921
        ix = {m: i for i, m in enumerate(names)}
        e = np.zeros(len(names))
        e[ix[tgt]] = 1
        for m in ("32B/s3/10000", "32B/s3/11000", "32B/s3/11921"):
            e[ix[m]] -= 1 / 3
        res_eq = float(e @ Gf @ e)
        d_m_last = Gf[ix[tgt], ix[tgt]] - 2 * Gf[ix[tgt], ix["32B/s3/11921"]] + Gf[ix["32B/s3/11921"], ix["32B/s3/11921"]]
        T["stage3_merge"] = dict(ref=ref, fits=fits, residual_equal_thirds=math.sqrt(max(res_eq, 0)),
                                 d_merge_s3_11921=math.sqrt(max(d_m_last, 0)),
                                 residual_equal_thirds_rel=math.sqrt(max(res_eq, 0)) / math.sqrt(max(d_m_last, 1e-300)))
    iv = agg.sums(D["iv"], ["d2", "na2"], by=["chain", "a", "b"]) if D["iv"] else {}
    a = iv.get(("pair", "32B/s1/656000", "32B/s3/1000"))
    b = iv.get(("stage3", "32B/s2merge", "32B/s3/1000"))
    if a and b:
        T["stage3_start"] = dict(d_from_s1_656000=math.sqrt(a["d2"]), d_from_s2merge=math.sqrt(b["d2"]),
                                 nearer="s2merge" if b["d2"] < a["d2"] else "s1_656000")
    # DPO-32B start: soups of one 1e-4 and one 5e-5 SFT checkpoint
    D = load("p32_sft", stats_root)
    if D["gram"]:
        ref, mem, G = gram_sum(D)["0"]
        names = [ref] + mem
        Gf = np.zeros((len(names), len(names)))
        Gf[1:, 1:] = G
        ix = {m: i for i, m in enumerate(names)}
        v = ix["32B/dpo"]
        single = {m: math.sqrt(max(Gf[v, v] - 2 * Gf[v, ix[m]] + Gf[ix[m], ix[m]], 0)) for m in names if m != "32B/dpo"}
        soups = []
        for x in names:
            if "/sft1e-4/" not in x:
                continue
            for y in names:
                if "/sft5e-5/" not in y:
                    continue
                ua, ub = ix[x], ix[y]
                # v ~ ub + w (ua - ub)
                dd = Gf[ua, ua] - 2 * Gf[ua, ub] + Gf[ub, ub]
                vb = Gf[v, ua] - Gf[v, ub] - Gf[ua, ub] + Gf[ub, ub]
                w = vb / dd
                rv = Gf[v, v] - 2 * Gf[v, ub] + Gf[ub, ub]
                res2 = rv - vb ** 2 / dd
                res_half = rv - vb + dd / 4
                soups.append(dict(a=x, b=y, w_on_1e4=w, residual=math.sqrt(max(res2, 0)),
                                  residual_half=math.sqrt(max(res_half, 0))))
        soups.sort(key=lambda s: s["residual"])
        T["dpo32_start"] = dict(ref=ref, d_dpo_sftmain=single["32B/sft5e-5/8000"],
                                nearest_single=min(single.items(), key=lambda kv: kv[1]),
                                best_soups=soups[:5], best_soup_rel_to_sftmain=soups[0]["residual"] / single["32B/sft5e-5/8000"])
    # 7B start tests and mains
    for job, first in (("p7_sft", "7B/sft/1000"), ("z7_if", "7B/zif/100"), ("z7_math", "7B/zmath/100"),
                       ("z7_code", "7B/zcode/100")):
        D = load(job, stats_root)
        if not D["iv"]:
            continue
        iv = agg.sums(D["iv"], ["d2", "na2"], by=["chain", "a", "b"])
        alt = iv.get(("pair", "7B/s3/11000", first))
        main = [v for (c, a, b), v in iv.items() if c != "pair" and a == "7B/s3/11921" and b == first]
        if alt and main:
            T[f"start_{job}"] = dict(first=first, d_from_base_main=math.sqrt(main[0]["d2"]),
                                     d_from_s3_11000=math.sqrt(alt["d2"]),
                                     nearer="base main" if main[0]["d2"] < alt["d2"] else "s3_11000")
    return T


# ---------------------------------------------------------------------------------------------------------------- LoRA
def lora_tables(D):
    if not D["lora"]:
        return [], [], []
    nrm = {r["tensor"]: r for r in D["lora_norms"]}
    names = ["main", "ctrl"] + [f"r{q}" for q in range(8)]

    def agg_rows(key_fn):
        acc = defaultdict(lambda: defaultdict(float))
        for r in D["lora"]:
            g = key_fn(r)
            a = acc[g]
            a["o2"] += float(r["o2"])
            for n in names:
                a[f"dot_{n}"] += float(r[f"dot_{n}"])
                a[f"n2_{n}"] += float(nrm[r["tensor"]][f"n2_{n}"])
        out = []
        for g, a in acc.items():
            row = dict(zip(("b", "group"), g))
            for n in names:
                row[f"cos_{n}"] = a[f"dot_{n}"] / math.sqrt(a["o2"] * a[f"n2_{n}"]) if a["o2"] > 0 and a[f"n2_{n}"] > 0 else None
            rc = [row[f"cos_r{q}"] for q in range(8)]
            row["cos_rand_mean"] = float(np.mean(rc))
            row["cos_rand_sd"] = float(np.std(rc, ddof=1))
            row["norm_ratio_main"] = math.sqrt(a["n2_main"] / a["o2"]) if a["o2"] > 0 else None
            row["norm_ratio_ctrl"] = math.sqrt(a["n2_ctrl"] / a["o2"]) if a["o2"] > 0 else None
            row["step"] = step_of(row["b"])
            out.append(row)
        return sorted(out, key=lambda r: (str(r["group"]), r["step"]))
    tot = agg_rows(lambda r: (r["b"], "all"))
    mods = agg_rows(lambda r: (r["b"], agg.group_of(r["tensor"])[0]))
    lays = agg_rows(lambda r: (r["b"], agg.group_of(r["tensor"])[1]))
    return tot, mods, lays


# ------------------------------------------------------------------------------------------------------------ writing
def write_csv(path, rows):
    if not rows:
        return
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else (f"{r[k]:.10g}" if isinstance(r[k], float) else r[k]))
                        for k in cols})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", default=agg.STATS)
    ap.add_argument("--out", default="artifacts/olmo_weights/tables")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    IV, MODS, LAYS, LO = [], [], [], ([], [], [])
    status = {}
    for job in JOBS:
        D = agg.load(job, a.stats)
        nsh = len(CK[JOBS[job]["members"][0]]["files"].split(";"))
        status[job] = f"{D['n_shards_done']}/{nsh} shards"
        if D["n_shards_done"] < nsh:
            continue      # a job counts only when every shard is done (totals over all tensors)
        IV += job_tables(job, D)
        MODS += group_tables(job, D, "module")
        LAYS += group_tables(job, D, "layer")
        if JOBS[job].get("lora"):
            LO = lora_tables(D)
    write_csv(os.path.join(a.out, "intervals.csv"), IV)
    write_csv(os.path.join(a.out, "modules.csv"), MODS)
    write_csv(os.path.join(a.out, "layers.csv"), LAYS)
    for name, rows in zip(("lora.csv", "lora_modules.csv", "lora_layers.csv"), LO):
        write_csv(os.path.join(a.out, name), rows)
    T = tests(a.stats)
    json.dump(T, open(os.path.join(a.out, "tests.json"), "w"), indent=1, default=float)
    json.dump(status, open(os.path.join(a.out, "status.json"), "w"), indent=1)
    print("jobs:", status)
    print(f"{len(IV)} intervals, {len(MODS)} module rows, {len(LAYS)} layer rows, tests: {list(T)}")
    finish(a, IV, MODS, LO)


# --------------------------------------------------------------------------- RL-Zero duplicate names (pre-registered rule)
def rlzero_duplicates(IV):
    """Pre-registered rule for byte-identical branch pairs (same shard sha256): each belongs where its distance from
    base main fits its neighbours' distances; the other name is excluded. Applied in two passes so that a misplaced
    checkpoint never serves as a neighbour: (1) members without a byte-identical twin whose distance lies outside the
    bracket of their nearest twin-free neighbours by more than 20 % are anomalous and excluded; (2) each member of a
    byte-identical pair is kept only if its distance fits the bracket of its nearest clean neighbours (twin-free, not
    anomalous). Returns (report, excluded labels)."""
    rep, excl = {}, set()

    def bracket(i, mem, d, ok):
        prev = next((d[x] for x in reversed(mem[:i]) if ok(x)), None)
        nxt = next((d[x] for x in mem[i + 1:] if ok(x)), None)
        v = d.get(mem[i])
        if v is None or prev is None:
            return None, prev, nxt
        if nxt is None:
            return v >= prev / 1.2, prev, nxt
        lo, hi = min(prev, nxt), max(prev, nxt)
        return lo / 1.2 <= v <= hi * 1.2, prev, nxt
    for job in ("z7_if", "z7_math", "z7_code"):
        if job not in JOBS:
            continue
        ch = JOBS[job]["chains"][0]
        mem = ch["members"]
        d = {r["b"]: r.get("dist_start_rel") for r in IV if r["job"] == job and r["chain"] == ch["name"]}
        if not d:
            continue
        d[mem[0]] = 0.0
        sha = {m: CK[m]["sha256"] for m in mem}
        twin = {m: [x for x in mem if x != m and sha[x] == sha[m]] for m in mem}
        anomalous = set()
        for _ in range(2):   # pass 1, repeated once so an anomaly found late is not used as a neighbour
            for i, m in enumerate(mem[1:], 1):
                if twin[m]:
                    continue
                f, _, _ = bracket(i, mem, d, lambda x: not twin[x] and x not in anomalous and d.get(x) is not None)
                if f is False:
                    anomalous.add(m)
        rows = []
        for i, m in enumerate(mem):
            clean = lambda x: not twin[x] and x not in anomalous and d.get(x) is not None
            f, prev, nxt = bracket(i, mem, d, clean) if i else (True, None, None)
            keep = (f is not False) and m not in anomalous
            if not keep:
                excl.add(m)
            rows.append(dict(member=m, dist_start_rel=d.get(m), byte_identical_to=twin[m], neighbour_prev=prev,
                             neighbour_next=nxt, fits=f, anomalous=m in anomalous, kept=keep))
        rep[job] = rows
    return rep, sorted(excl)


def pair_distance(rows_by_idx, i, j):
    """||theta_j - theta_i|| for chain members i < j <= i + 4 from the interval norms and lag-1..3 dot products."""
    if j - i > 4 or j <= i:
        return None
    tot = 0.0
    for p in range(i + 1, j + 1):
        tot += rows_by_idx[p]["norm_d"] ** 2
        for q in range(i + 1, p):
            L = p - q
            dot = rows_by_idx[p].get(f"_dot_lag{L}")
            if dot is None:
                return None
            tot += 2 * dot
    return math.sqrt(max(tot, 0.0))


def matched_straightness(IV, job, chain, n_target, end_label=None):
    """Straightness of a chain subsampled to about n_target intervals (gaps <= 4, from the lag dot products)."""
    rows = sorted([r for r in IV if r["job"] == job and r["chain"] == chain], key=lambda r: r["idx"])
    if not rows:
        return None
    if end_label:
        rows = [r for r in rows if r["idx"] <= next((x["idx"] for x in rows if x["b"] == end_label), rows[-1]["idx"])]
    n = len(rows)
    by = {r["idx"]: r for r in rows}
    k = n_target
    while k <= n:
        pts = sorted({round(j * n / k) for j in range(k + 1)})
        if max(b - a for a, b in zip(pts, pts[1:])) <= 4:
            break
        k += 1
    path = 0.0
    for a, b in zip(pts, pts[1:]):
        dd = pair_distance(by, a, b)
        if dd is None:
            return None
        path += dd
    end = math.sqrt(rows[-1]["o2"])
    return dict(n_intervals=len(pts) - 1, straightness=end / path, gaps=sorted({b - a for a, b in zip(pts, pts[1:])}))


def attach_lag_dots(IV, stats_root):
    """Put the raw lag dot products on the interval rows (needed for pair_distance)."""
    for job in JOBS:
        D = agg.load(job, stats_root)
        if not D["lag"]:
            continue
        lag = agg.sums(D["lag"], ["dot"], by=["chain", "idx", "lag"])
        for r in IV:
            if r["job"] != job:
                continue
            for L in (1, 2, 3):
                v = lag.get((r["chain"], str(r["idx"]), str(L)))
                if v is not None:
                    r[f"_dot_lag{L}"] = v["dot"]


# ------------------------------------------------------------------------------------------- pre-registered expectations
def expectations(IV, CH, MODS, T, LO):
    E = {}

    def sel(job, chain, kind="within"):
        return [r for r in IV if r["job"] == job and r["chain"] == chain and r["kind"] == kind]

    def med(rows, k):
        v = [r[k] for r in rows if r.get(k) is not None]
        return float(np.median(v)) if v else None

    def row_b(job, chain, b):
        return next((r for r in IV if r["job"] == job and r["chain"] == chain and r["b"] == b), None)
    fams = {"32B": dict(rl=("p32_rl", "rl"), sft=("p32_sft", "sft-5e-5"), rl_last="32B/rl/2300",
                        sft_main=("p32_sft", "sft-5e-5", "32B/sft5e-5/8000"), sft_stretch="SFT 5e-5 run"),
            "7B": dict(rl=("p7_rl", "rl"), sft=("p7_sft", "sft-dpo"), rl_last=None,
                       sft_main=("p7_sft", "sft-dpo", "7B/sftmain"), sft_stretch="SFT")}
    for fam, F in fams.items():
        rl, sft = sel(*F["rl"]), sel(*F["sft"])
        if not rl or not sft:
            continue
        r1, s1 = med(rl, "rel_per_step"), med(sft, "rel_per_step")
        E.setdefault("E1", {})[fam] = dict(median_rl=r1, median_sft=s1, ratio_sft_over_rl=s1 / r1, hit=s1 / r1 >= 10,
                                           n_rl=len(rl), n_sft=len(sft))
        last = F["rl_last"]
        if last is None:   # 7B: main if it lies beyond step_1375, else step_1375
            m = row_b("p7_rl", "rl", "7B/rlmain")
            l1375 = row_b("p7_rl", "rl", "7B/rl/1375")
            last = "7B/rlmain" if m and l1375 and m["dist_start_rel"] > l1375["dist_start_rel"] else "7B/rl/1375"
        rlr = row_b(F["rl"][0], F["rl"][1], last)
        sm = row_b(*F["sft_main"])
        if rlr and sm:
            E.setdefault("E2", {})[fam] = dict(rl_last=last, total_rl=rlr["dist_start_rel"], total_sft=sm["dist_start_rel"],
                                               hit=rlr["dist_start_rel"] < sm["dist_start_rel"])
            E.setdefault("E3", {})[fam] = dict(rl_last=last, frac_within_1ulp_of_dpo=rlr["frac_ulp_start"],
                                               frac_unchanged=rlr["frac_eq_start"], hit=rlr["frac_ulp_start"] > 0.5)
        cr = next((c for c in CH if c["family"] == fam and c["stretch"] == "RL"), None)
        cs = next((c for c in CH if c["family"] == fam and c["stretch"] == F["sft_stretch"]), None)
        if cr and cs:
            mt = matched_straightness(IV, F["rl"][0], F["rl"][1], cs["n_intervals"],
                                      end_label=(None if fam == "32B" else "7B/rl/1375"))
            E.setdefault("E4", {})[fam] = dict(S_rl=cr["straightness"], S_sft=cs["straightness"], n_rl=cr["n_intervals"],
                                               n_sft=cs["n_intervals"], hit=cr["straightness"] > cs["straightness"],
                                               matched=mt, matched_hit=(mt["straightness"] > cs["straightness"]) if mt else None)
        # G1 / G2 / G6
        if fam == "32B":
            E["G1"] = dict(median_frac_eq_rl=med(rl, "frac_eq"), median_frac_eq_sft=med(sft, "frac_eq"),
                           hit=(med(rl, "frac_eq") > 0.5 and med(sft, "frac_eq") < 0.1))
            emb = [r["frac_eq"] for r in MODS if r["job"] == "p32_rl" and r["kind"] == "within" and r["module"] == "embed"]
            mlp = {m: float(np.median([r["frac_eq"] for r in MODS if r["job"] == "p32_rl" and r["kind"] == "within"
                                       and r["module"] == m])) for m in ("gate", "up", "down")}
            if emb:
                E["G6"] = dict(median_frac_eq_embed=float(np.median(emb)), mlp=mlp,
                               hit=all(float(np.median(emb)) > v for v in mlp.values()))
        g2r, g2s = med(rl, "rel_per_step_per_lr"), med(sft, "rel_per_step_per_lr")
        E.setdefault("G2", {})[fam] = dict(rl=g2r, sft=g2s, ratio=g2r / g2s if g2r and g2s else None,
                                           hit=(g2r / g2s >= 2) if g2r and g2s else None)
    # G3: boundary intervals vs the last within-stage interval before them
    g3 = {}
    for fam, specs in {"32B": [("b32_s2", "ingredient1", 1, ("b32_s1", "stage1-sampled")), ("b32_s3", "stage3", 1, ("b32_s2", "ingredient1"))],
                       "7B": [("b7_s2", "stage2", 1, ("b7_s1", "stage1-sampled")), ("b7_s3", "stage3", 1, ("b7_s2", "stage2"))]}.items():
        for job, chain, idx, (pj, pc) in specs:
            b = next((r for r in IV if r["job"] == job and r["chain"] == chain and r["idx"] == idx), None)
            prev = [r for r in IV if r["job"] == pj and r["chain"] == pc and r["kind"] in ("within", "pair") and r.get("rel_per_step")]
            if b and prev:
                p = max(prev, key=lambda r: r["idx"])
                g3[f"{fam} {b['a']} -> {b['b']}"] = dict(boundary=b["rel_per_step"], last_before=p["rel_per_step"],
                                                         last_before_interval=f"{p['a']} -> {p['b']}",
                                                         hit=b["rel_per_step"] > p["rel_per_step"])
    if g3:
        E["G3"] = dict(cases=g3, hit=all(v["hit"] for v in g3.values()) if len(g3) == 4 else None)
    if "stage2_merge" in T and "stage3_merge" in T:
        s2, s3 = T["stage2_merge"], T["stage3_merge"]
        best3 = min(s3["fits"].items(), key=lambda kv: kv[1]["residual"])
        E["G4"] = dict(stage2_residual_rel=s2["residual_rel_to_d_i1_i2"], stage3_residual_equal_thirds_rel=s3["residual_equal_thirds_rel"],
                       stage3_best_basis=best3[0], hit=(s2["residual_rel_to_d_i1_i2"] < 0.01 and s3["residual_equal_thirds_rel"] < 0.01))
    if "dpo32_start" in T:
        E["G5"] = dict(best_soup=T["dpo32_start"]["best_soups"][0], rel_to_sftmain=T["dpo32_start"]["best_soup_rel_to_sftmain"],
                       hit=T["dpo32_start"]["best_soup_rel_to_sftmain"] < 0.5)
    # G7: distance from the start at step 1,000
    r7 = row_b("p7_rl", "rl", "7B/rl/1000")
    if r7:
        g7 = {}
        for k, job in (("IF", "z7_if"), ("Math", "z7_math"), ("Code", "z7_code")):
            z = row_b(job, f"rlzero-{k.lower()}", f"7B/z{k.lower()}/1000")
            if z:
                g7[k] = dict(rlzero=z["dist_start_rel"], rl_from_dpo=r7["dist_start_rel"], hit=z["dist_start_rel"] > r7["dist_start_rel"])
        E["G7"] = dict(cases=g7, hit=all(v["hit"] for v in g7.values()) if len(g7) == 3 else None)
    # E5: LoRA at the last RL checkpoint
    tot = LO[0] if LO else []
    if tot:
        last = max(tot, key=lambda r: r["step"])
        E["E5"] = dict(step=last["step"], cos_main=last["cos_main"], cos_ctrl=last["cos_ctrl"], rand_mean=last["cos_rand_mean"],
                       rand_sd=last["cos_rand_sd"], norm_ratio_main=last["norm_ratio_main"],
                       hit=(last["cos_main"] > last["cos_ctrl"] and abs(last["cos_main"]) < 0.1 and abs(last["cos_ctrl"]) < 0.1
                            and last["cos_main"] > last["cos_rand_mean"] + 3 * last["cos_rand_sd"]))
    return E


def finish(a, IV, MODS, LO):
    """Second pass: duplicates, stretches with exclusions, expectations."""
    attach_lag_dots(IV, a.stats)
    rep, excl = rlzero_duplicates(IV)
    T = json.load(open(os.path.join(a.out, "tests.json")))
    T["rlzero_duplicates"] = rep
    T["rlzero_excluded"] = excl
    soup = sft32_soup_test(a.stats)
    T["sft32_soup"] = soup
    excl = list(excl) + ([SOUP] if soup and soup["is_soup"] else [])
    T["excluded_names"] = excl
    apply_exclusions(IV, set(excl), soup)
    write_csv(os.path.join(a.out, "intervals.csv"), sorted(IV, key=lambda r: (r["family"], r["job"], r["chain"], r["idx"])))
    json.dump(T, open(os.path.join(a.out, "tests.json"), "w"), indent=1, default=float)
    CH = stretch_rows(IV, exclude=set(excl))
    write_csv(os.path.join(a.out, "chains.csv"), CH)
    E = expectations(IV, CH, MODS, T, LO)
    json.dump(E, open(os.path.join(a.out, "expectations.json"), "w"), indent=1, default=float)
    print("excluded (duplicate names):", excl)
    for k, v in E.items():
        print(k, json.dumps(v, default=float)[:300])



# ---------------------------------------------------------------- the 32B SFT soup filed under 5e-5-step8000 (found in the data)
SOUP = "32B/sft5e-5/8000"   # byte-identical to Olmo-3-32B-Think-SFT main


def sft32_soup_test(stats_root):
    """Is the '5e-5-step8000' branch (= SFT main by hash) the 5e-5 run at step 8,000, or a soup of the two runs?
    Gram set of p32_sft (offsets from that branch): its distance to every SFT checkpoint, and the best two-checkpoint
    linear combination (w, 1 - w) of one 1e-4 and one other 5e-5 checkpoint. Applying the pre-registered duplicate
    rule (a byte-identical pair belongs where its distances fit the neighbours): if the best soup's residual is
    below 5 % of the distance to the nearest real SFT checkpoint, the branch is the soup (= main) and its step name is
    excluded from the 5e-5 run's chain."""
    D = agg.load("p32_sft", stats_root)
    if not D["gram"]:
        return None
    ref, mem, G = gram_sum(D)["0"]
    names = [ref] + mem
    Gf = np.zeros((len(names), len(names)))
    Gf[1:, 1:] = G
    ix = {m: i for i, m in enumerate(names)}

    def dist(a, b):
        i, j = ix[a], ix[b]
        return math.sqrt(max(Gf[i, i] - 2 * Gf[i, j] + Gf[j, j], 0))
    real = [m for m in names if m not in (SOUP, "32B/dpo")]
    nearest = min(real, key=lambda m: dist(SOUP, m))
    fits = []
    for a in real:
        if "/sft1e-4/" not in a:
            continue
        for b in real:
            if "/sft5e-5/" not in b:
                continue
            ia, ib = ix[a], ix[b]
            dd = Gf[ia, ia] - 2 * Gf[ia, ib] + Gf[ib, ib]
            w = (Gf[ib, ib] - Gf[ia, ib]) / dd
            res2 = w * w * Gf[ia, ia] + 2 * w * (1 - w) * Gf[ia, ib] + (1 - w) ** 2 * Gf[ib, ib]
            fits.append(dict(a=a, b=b, w_on_a=w, residual=math.sqrt(max(res2, 0))))
    fits.sort(key=lambda f: f["residual"])
    out = dict(branch=SOUP, nearest_real=nearest, d_nearest_real=dist(SOUP, nearest),
               d_to_5e5_7000=dist(SOUP, "32B/sft5e-5/7000"), d_to_5e5_9000=dist(SOUP, "32B/sft5e-5/9000"),
               d_5e5_7000_to_9000=dist("32B/sft5e-5/7000", "32B/sft5e-5/9000"), best_soups=fits[:5],
               d_dpo=dist(SOUP, "32B/dpo"), d_soup_to_5e5_10790=dist(SOUP, "32B/sft5e-5/10790"),
               d_soup_to_1e4_10790=dist(SOUP, "32B/sft1e-4/10790"))
    out["is_soup"] = fits[0]["residual"] < 0.05 * out["d_nearest_real"]
    return out


def apply_exclusions(IV, excl, soup):
    """Mark intervals that touch an excluded name (kind 'excluded', off the main path) and add derived intervals:
    the 5e-5 run bridged 7,000 -> 9,000 (lag dot products), and the SFT soup as a merge after the runs' last step."""
    for r in IV:
        if r["a"] in excl or r["b"] in excl:
            if not (r["chain"] == "sftmain-to-dpo"):     # the soup -> DPO interval is the real DPO interval
                r["kind"], r["main_path"] = "excluded", False
    if soup and soup.get("is_soup"):
        rows = sorted([r for r in IV if r["job"] == "p32_sft" and r["chain"] == "sft-5e-5"], key=lambda r: r["idx"])
        by = {r["idx"]: r for r in rows}
        mem = chain_members("p32_sft", "sft-5e-5")["members"]
        i7, i9 = mem.index("32B/sft5e-5/7000"), mem.index("32B/sft5e-5/9000")
        dd = pair_distance(by, i7, i9)
        a_row = by[i7]
        if dd is not None:
            rel = dd / a_row["norm_b"]
            lrm = LR.mean_lr("32B", "sft-5e-5", 7000, 9000)
            IV.append(dict(family="32B", job="p32_sft", chain="sft-5e-5", idx=i7 + 0.5, a="32B/sft5e-5/7000",
                           b="32B/sft5e-5/9000", kind="within", stage="sft", steps=2000, lr_mean=lrm, rel=rel,
                           rel_per_step=rel / 2000, rel_per_step_per_lr=rel / 2000 / lrm, norm_d=dd,
                           norm_a=a_row["norm_b"], main_path=True, derived="bridged over the excluded name via lag dots"))
        last = by[max(by)]
        IV.append(dict(family="32B", job="p32_sft", chain="sft-5e-5", idx=max(by) + 0.5, a="32B/sft5e-5/10790",
                       b="32B/sft-soup(main)", kind="merge", stage="sft", steps=0, rel=soup["d_soup_to_5e5_10790"] / last["norm_b"],
                       norm_d=soup["d_soup_to_5e5_10790"], norm_a=last["norm_b"], main_path=True,
                       derived="SFT soup = equal-weight merge of 1e-4@10790 and 5e-5@10790 (Gram set)"))


if __name__ == "__main__":
    main()
