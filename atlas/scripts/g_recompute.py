#!/usr/bin/env python3
"""evidence-atlas part G: the length frontier across interfaces x caps x recipes x stage.

Regenerates atlas/data/length_frontier.csv.

Recomputed rows come from per-theorem re-read rows (.jsonl: one row per theorem, `solved`,
`pruned_lens`) or, where only per-stratum summaries exist, from the re-read summary .json
(`by_len` = solved / n per L_true stratum, `frontier_pruned` = line length of the longest
accepted (pruned) proof).  The textbook / generator split is joined from the pool file
`data/ladder/transfer_long_rr600.jsonl` (fork `dan`, field `source`).  Copied rows are lifted from
the A/B/C part metrics (summary text) and re-labelled with harmonised family names.

Sources (read-only):
  fork  /home/dan/nd-takehome  (git show origin/<branch>:<path>)
  bucket hf://buckets/dan-pandori/nd-rl/...  -> cached in /tmp/atlas/cache (fetched if missing)

Definitions
  L*  = the largest L with >= 5 theorems solved at L_true >= L (long-pool's definition), computed over
        the strata of the named pool combination.  If the cumulative count at the top stratum is >= 5,
        L* is censored at the pool ceiling -> metric `L_star_ge`.  If < 5 even at the floor (11),
        metric `L_star_lt` with value 11.
  Q   = generator theorems of rr600 at L_true 13-16 solved (/380), state-cap12's pre-registered quantity.
  solved = theorems with >= 1 Lean-accepted sample among k.
"""
import ast, csv, json, os, statistics, subprocess, sys
from collections import defaultdict

FORK = "/home/dan/nd-takehome"
CACHE = "/tmp/atlas/cache"
ATLAS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ATLAS, "data", "length_frontier.csv")

COLS = ["family", "model_label", "params", "format", "init", "train_set", "cap", "stage", "seed", "pool",
        "n_pool", "metric", "k", "temperature", "value", "checker", "judge", "date", "provenance",
        "source_file", "L", "apples_group", "pool_version", "max_new", "max_steps", "batch", "trunc_frac"]


def git_show(branch, path):
    return subprocess.run(["git", "-C", FORK, "show", f"origin/{branch}:{path}"], check=True,
                          capture_output=True).stdout.decode()


def git_blob(branch, path):
    out = subprocess.run(["git", "-C", FORK, "rev-parse", f"origin/{branch}:{path}"], check=True,
                         capture_output=True).stdout.decode().strip()
    return out[:8]


def bucket(path):
    """path relative to hf://buckets/dan-pandori/nd-rl/ ; cached under CACHE/<run>/<basename>."""
    run = path.split("/")[0]
    sub = {"state-cap12": "sc12", "best-state": "bs"}.get(run, run)
    local = os.path.join(CACHE, sub, os.path.basename(path))
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        subprocess.run(["hf", "buckets", "cp", f"hf://buckets/dan-pandori/nd-rl/{path}", local], check=True,
                       capture_output=True)
    with open(local) as f:
        return f.read()


def jl(text):
    return [json.loads(l) for l in text.splitlines() if l.strip()]


# ---------------------------------------------------------------- pools
POOL_RR600 = {r["name"]: r for r in jl(git_show("dan", "data/ladder/transfer_long_rr600.jsonl"))}
V_RR600 = "transfer_long_rr600@" + git_blob("dan", "data/ladder/transfer_long_rr600.jsonl")
V_GE17 = "transfer_long_ge17@" + git_blob("dan", "data/ladder/transfer_long_ge17.jsonl")
V_L2 = "transfer_long2@" + git_blob("dan", "data/ladder/transfer_long2.jsonl")
V_L2C = "transfer_long2_calib@" + git_blob("dan", "data/ladder/transfer_long2_calib.jsonl")
# the re-read branches must use the same pool bytes as fork dan
for br in ("dan_long-pool", "dan_best-state", "dan_long-pool-2"):
    assert git_blob(br, "data/ladder/transfer_long_rr600.jsonl") == V_RR600.split("@")[1], br

rows = []


def trunc_of(summ):
    """truncation fraction of one read: whole-proof `trunc_frac` (max_new hit), state
    (max_action truncated + max_steps step_cap) / samples."""
    if summ is None:
        return ""
    if summ.get("trunc_frac") is not None:
        return round(summ["trunc_frac"], 6)
    env = summ.get("env")
    if isinstance(env, str):  # best-state stores env repr'd; not needed beyond env_end
        try:
            env = ast.literal_eval(env)  # literal dict repr written by the reader
        except Exception:
            env = None
    if isinstance(env, dict) and "env_end" in env and summ.get("n_samples"):
        e = env["env_end"]
        return round((e.get("truncated", 0) + e.get("step_cap", 0)) / summ["n_samples"], 6)
    return ""


def emit(meta, pool, n_pool, metric, value, src, prov="recomputed", L="", group="", pver="", summ=None,
         settings=None):
    s = dict(meta.get("settings", {}))
    if settings:
        s.update(settings)
    rows.append(dict(
        family=meta["family"], model_label=meta["label"], params=meta["params"], format=meta["format"],
        init="scratch", train_set=meta["train_set"], cap=meta["cap"], stage=meta["stage"], seed=meta["seed"],
        pool=pool, n_pool=n_pool, metric=metric, k=s.get("k", 256), temperature=s.get("T", 0.8), value=value,
        checker="lean_only", judge="lean_judge (Lean 4.34)", date=meta["date"], provenance=prov,
        source_file=src, L=L, apples_group=group, pool_version=pver, max_new=s.get("max_new", ""),
        max_steps=s.get("max_steps", ""), batch=s.get("batch", ""), trunc_frac=trunc_of(summ)))


def hist_max(summ):
    """longest accepted (pruned) proof, in ND lines, over the distinct accepted proofs of one read."""
    h = summ["pruned_hist"]
    if isinstance(h, str):
        h = ast.literal_eval(h)
    return max((int(k) for k in h), default=0)


def frontier(summ, meta, pool, n_pool, src, group, pver):
    """`frontier_pruned` of the reader = largest pruned length with >= 5 accepted distinct proofs."""
    emit(meta, pool, n_pool, "frontier_pruned_ge5proofs", summ["frontier_pruned"], src, group=group, pver=pver,
         summ=summ)


def lstar(strata):
    """strata: list of (L, solved) in ascending L; last may be an open '>= L' stratum."""
    best = None
    for i, (L, _) in enumerate(strata):
        if sum(s for _, s in strata[i:]) >= 5:
            best = L
    if best is None:
        return "L_star_lt", strata[0][0]
    top = strata[-1][0]
    return ("L_star_ge", best) if best == top else ("L_star", best)


def rr600_from_rows(trows):
    by = defaultdict(lambda: [0, 0]); byg = defaultdict(lambda: [0, 0]); maxlines = 0; solved_names = set()
    for r in trows:
        p = POOL_RR600[r["name"]]
        L = p["L_true"]
        assert L == r["L_true_lb"], r["name"]
        by[L][1] += 1; by[L][0] += bool(r["solved"])
        if p["source"] == "gen":
            byg[L][1] += 1; byg[L][0] += bool(r["solved"])
        if r["solved"]:
            solved_names.add(r["name"])
            if r["pruned_lens"]:
                maxlines = max(maxlines, max(r["pruned_lens"]))
    assert sum(v[1] for v in by.values()) == 600
    return by, byg, maxlines, solved_names


def rr600_rows_out(meta, by, byg, src, group, summ, gen_ok=True):
    for L in range(11, 17):
        emit(meta, "rr600", by[L][1], "solved", by[L][0], src, L=L, group=group, pver=V_RR600, summ=summ)
        if gen_ok:
            emit(meta, "rr600_gen", byg[L][1], "solved", byg[L][0], src, L=L, group=group, pver=V_RR600,
                 summ=summ)
    emit(meta, "rr600", 600, "solved", sum(by[L][0] for L in range(11, 17)), src, group=group, pver=V_RR600,
         summ=summ)
    if gen_ok:
        q = sum(byg[L][0] for L in range(13, 17)); nq = sum(byg[L][1] for L in range(13, 17))
        assert nq == 380
        emit(meta, "rr600_gen_L13-16", 380, "Q", q, src, group=group, pver=V_RR600, summ=summ)


def by_from_summary(summ):
    return defaultdict(lambda: [0, 0], {int(k): [v["solved"], v["n"]] for k, v in summ["by_len"].items()})


# ================================================================ 1. long-pool pass 2 (rr2)
LP_MODELS = {
    # key: (family, label, format, cap, stage, seed, train_set)
    "state-env__la_T1_S_s0_r8": ("ours-3.2M-lean_state-cap6", "S T1 (state-env la_T1_S_s0_r8)", "lean_state", 6, "T1", "S1s0"),
    "state-env__la_T1_S_s1_r8": ("ours-3.2M-lean_state-cap6", "S T1 (state-env la_T1_S_s1_r8)", "lean_state", 6, "T1", "S1s1"),
    "state-env__la_T1_SN_s0_r8": ("ours-3.2M-lean_staten-cap6", "SN-v2 T1 (state-env la_T1_SN_s0_r8)", "lean_staten", 6, "T1", "S1s0"),
    "state-env__la_T1_SN_s1_r8": ("ours-3.2M-lean_staten-cap6", "SN-v2 T1 (state-env la_T1_SN_s1_r8)", "lean_staten", 6, "T1", "S1s1"),
    "ds-generator__la_T1_c0_s0_r8": ("ours-3.2M-lean_seq-cap6", "C0 T1 (ds-generator la_T1_c0_s0_r8)", "lean_seq", 6, "T1", "S1s0"),
    "ds-generator__la_T1_c0_s1_r8": ("ours-3.2M-lean_seq-cap6", "C0 T1 (ds-generator la_T1_c0_s1_r8)", "lean_seq", 6, "T1", "S1s1"),
    "state-env__stage1_S_s0": ("ours-3.2M-lean_state-cap6", "S frozen (state-env stage1_S_s0)", "lean_state", 6, "frozen", "S1s0"),
    "state-env__stage1_S_s1": ("ours-3.2M-lean_state-cap6", "S frozen (state-env stage1_S_s1)", "lean_state", 6, "frozen", "S1s1"),
    "state-env__stage1_SN_s0": ("ours-3.2M-lean_staten-cap6", "SN frozen (state-env stage1_SN_s0)", "lean_staten", 6, "frozen", "S1s0"),
    "state-env__stage1_SN_s1": ("ours-3.2M-lean_staten-cap6", "SN frozen (state-env stage1_SN_s1)", "lean_staten", 6, "frozen", "S1s1"),
    "lean-format__stage1_a1_seq_s0": ("ours-3.2M-lean_seq-cap6", "C0 frozen (lean-format stage1_a1_seq_s0)", "lean_seq", 6, "frozen", "S1s0"),
    "lean-format__stage1_a1_seq_s1": ("ours-3.2M-lean_seq-cap6", "C0 frozen (lean-format stage1_a1_seq_s1)", "lean_seq", 6, "frozen", "S1s1"),
    "cap-horizon__stage1_k12_s0": ("ours-3.2M-lean_seq-cap12", "K12 frozen (cap-horizon stage1_k12_s0)", "lean_seq", 12, "frozen", "S1s0"),
    "cap-horizon__stage1_k14_s0": ("ours-3.2M-lean_seq-cap14", "K14 frozen (cap-horizon stage1_k14_s0)", "lean_seq", 14, "frozen", "S1s0"),
}
TRAIN = {6: "cap-6 control depth3_f0_a1 155k", 12: "K12 flat 2-12 155k", 14: "K14 155k"}
G_MS48 = "A:rr600+ge17_70 k256 T0.8 seed0 (state ms48 b2048 / wp max_new1536 b1024)"
G_MS96 = "B:rr600 k256 T0.8 seed0 state ms96 b2048 (best-state settings)"
G_L2_91 = "C:long2_91 k256 T0.8 seed0 state ms96 b2048 / wp max_new1536 b1024"
G_L2_21 = "D:long2_21(new) k256 T0.8 seed0 state ms96 b2048"

lean_size = defaultdict(dict)
for r in jl(git_show("dan_long-pool", "artifacts/lpool/rr2_shortest_lean.jsonl")):
    m, t = r["name"].split("|")
    if r.get("lean_ok"):
        lean_size[m][t] = r["size"]

LP_RESULTS = {}
for key, (fam, label, fmt, cap, stage, seed) in LP_MODELS.items():
    wp = fmt == "lean_seq"
    settings = dict(k=256, T=0.8, batch=1024 if wp else 2048, max_new=1536 if wp else "",
                    max_steps="" if wp else 48)
    meta = dict(family=fam, label=label, params="3.2M", format=fmt, cap=cap, stage=stage, seed=seed,
                train_set=TRAIN[cap], date="2026-09-28", settings=settings)
    src = f"fork:dan_long-pool:artifacts/lpool/rr2/{key}.jsonl"
    trows = jl(git_show("dan_long-pool", f"artifacts/lpool/rr2/{key}.jsonl"))
    summ = json.loads(git_show("dan_long-pool", f"artifacts/lpool/rr2/{key}.json"))
    g17 = jl(git_show("dan_long-pool", f"artifacts/lpool/rr2/{key}__ge17.jsonl"))
    g17s = json.loads(git_show("dan_long-pool", f"artifacts/lpool/rr2/{key}__ge17.json"))
    by, byg, maxl, solved = rr600_from_rows(trows)
    rr600_rows_out(meta, by, byg, src, G_MS48, summ)
    n17 = sum(bool(r["solved"]) for r in g17)
    for r in g17:
        if r["solved"] and r["pruned_lens"]:
            maxl = max(maxl, max(r["pruned_lens"]))
            solved.add(r["name"])
    emit(meta, "ge17_70", 70, "solved", n17, src.replace(".jsonl", "__ge17.jsonl"), L="17+", group=G_MS48,
         pver=V_GE17, summ=g17s)
    m, v = lstar([(L, by[L][0]) for L in range(11, 17)] + [(17, n17)])
    emit(meta, "rr600+ge17_70", 670, m, v, src + " + __ge17.jsonl", group=G_MS48, pver=V_RR600 + ";" + V_GE17,
         summ=summ)
    emit(meta, "rr600+ge17_70", 670, "max_accepted_lines", maxl, src + " + __ge17.jsonl", group=G_MS48,
         pver=V_RR600 + ";" + V_GE17, summ=summ)
    sizes = [lean_size[key][t] for t in solved if t in lean_size[key]]
    if sizes:
        emit(meta, "rr600+ge17_70", 670, "max_term_size_shortest", max(sizes),
             "fork:dan_long-pool:artifacts/lpool/rr2_shortest_lean.jsonl", group=G_MS48,
             pver=V_RR600 + ";" + V_GE17, summ=summ)
        emit(meta, "rr600+ge17_70", 670, "median_term_size_shortest", statistics.median(sizes),
             "fork:dan_long-pool:artifacts/lpool/rr2_shortest_lean.jsonl", group=G_MS48,
             pver=V_RR600 + ";" + V_GE17, summ=summ)
    LP_RESULTS[key] = (by, n17, len(sizes), len(solved))

# ================================================================ 2. state-cap12 (bucket)
SC = {
    "T1_SN12_s%d": ("ours-3.2M-lean_staten-cap12", "SN-cap12 T1 (state-cap12 la_T1_SN12_s%d_r8)", "lean_staten", "T1", range(4)),
    "stage1_SN12_s%d": ("ours-3.2M-lean_staten-cap12", "SN-cap12 frozen (state-cap12 stage1_SN12_s%d)", "lean_staten", "frozen", range(4)),
    "T1_K12_s%d": ("ours-3.2M-lean_seq-cap12", "K12 whole-proof T1 (state-cap12 la_T1_K12_s%d_r8)", "lean_seq", "T1", range(2)),
}
SC_RESULTS = {}
for pat, (fam, lab, fmt, stage, seeds) in SC.items():
    for s in seeds:
        key = pat % s
        wp = fmt == "lean_seq"
        meta = dict(family=fam, label=lab % s, params="3.2M", format=fmt, cap=12, stage=stage, seed=str(s),
                    train_set=TRAIN[12], date="2026-09-29",
                    settings=dict(batch=1024 if wp else 2048, max_new=1536 if wp else "",
                                  max_steps="" if wp else 48))
        base = f"state-cap12/artifacts/sc12/rr/{key}"
        src = "hf://buckets/dan-pandori/nd-rl/" + base
        trows = jl(bucket(base + "__rr600.jsonl"))
        summ = json.loads(bucket(base + "__rr600.json"))
        g = json.loads(bucket(base + "__ge17.json"))
        by, byg, maxl, _ = rr600_from_rows(trows)
        assert maxl == hist_max(summ), key
        rr600_rows_out(meta, by, byg, src + "__rr600.jsonl", G_MS48, summ)
        emit(meta, "ge17_70", 70, "solved", g["solved"], src + "__ge17.json", L="17+", group=G_MS48, pver=V_GE17,
             summ=g)
        m, v = lstar([(L, by[L][0]) for L in range(11, 17)] + [(17, g["solved"])])
        emit(meta, "rr600+ge17_70", 670, m, v, src + "__rr600.jsonl + __ge17.json", group=G_MS48,
             pver=V_RR600 + ";" + V_GE17, summ=summ)
        emit(meta, "rr600+ge17_70", 670, "max_accepted_lines", max(maxl, hist_max(g)),
             src + "__rr600.jsonl + __ge17.json", group=G_MS48, pver=V_RR600 + ";" + V_GE17, summ=summ)
        frontier(summ, meta, "rr600", 600, src + "__rr600.json", G_MS48, V_RR600)
        SC_RESULTS[(fam, stage, str(s))] = by

# ================================================================ 3. long-pool-2 (long2 91 = 21 new + 70 calib)
L2 = {
    "T1_SN12_s%d": ("ours-3.2M-lean_staten-cap12", "SN-cap12 T1 (la_T1_SN12_s%d_r8)", "lean_staten", 12, "T1", range(4)),
    "stage1_SN12_s%d": ("ours-3.2M-lean_staten-cap12", "SN-cap12 frozen (stage1_SN12_s%d)", "lean_staten", 12, "frozen", range(4)),
    "T1_K12_s%d": ("ours-3.2M-lean_seq-cap12", "K12 whole-proof T1 (la_T1_K12_s%d_r8)", "lean_seq", 12, "T1", range(2)),
    "T1_SNv2_s%d": ("ours-3.2M-lean_staten-cap6", "SN-v2 T1 (state-env la_T1_SN_s%d_r8)", "lean_staten", 6, "T1", range(2)),
}
for pat, (fam, lab, fmt, cap, stage, seeds) in L2.items():
    for s in seeds:
        key = pat % s
        wp = fmt == "lean_seq"
        seed = str(s) if cap == 12 else f"S1s{s}"
        meta = dict(family=fam, label=lab % s, params="3.2M", format=fmt, cap=cap, stage=stage, seed=seed,
                    train_set=TRAIN[cap], date="2026-09-30",
                    settings=dict(batch=1024 if wp else 2048, max_new=1536 if wp else "",
                                  max_steps="" if wp else 96))
        src = f"fork:dan_long-pool-2:artifacts/lpool2/rr/{key}"
        new = json.loads(git_show("dan_long-pool-2", f"artifacts/lpool2/rr/{key}__new.json"))
        cal = json.loads(git_show("dan_long-pool-2", f"artifacts/lpool2/rr/{key}__cal.json"))
        bn, bc = by_from_summary(new), by_from_summary(cal)
        for L, lab_L in ((17, "17"), (18, "18+")):
            emit(meta, "long2_91", bn[L][1] + bc[L][1], "solved", bn[L][0] + bc[L][0],
                 src + "__new.json + __cal.json", L=lab_L, group=G_L2_91, pver=V_L2 + ";" + V_L2C, summ=new)
            emit(meta, "long2_21", bn[L][1], "solved", bn[L][0], src + "__new.json", L=lab_L, group=G_L2_21,
                 pver=V_L2, summ=new)
        emit(meta, "long2_91", 91, "solved", new["solved"] + cal["solved"], src + "__new.json + __cal.json",
             group=G_L2_91, pver=V_L2 + ";" + V_L2C, summ=new)
        emit(meta, "long2_21", 21, "solved", new["solved"], src + "__new.json", group=G_L2_21, pver=V_L2,
             summ=new)
        emit(meta, "long2_91", 91, "max_accepted_lines", max(hist_max(new), hist_max(cal)),
             src + "__new.json + __cal.json", group=G_L2_91, pver=V_L2 + ";" + V_L2C, summ=new)
        # L* extended to >= 18: rr600 (state-cap12 / long-pool read, ms48) + long2_91 (this read, ms96)
        rr = SC_RESULTS.get((fam, stage, str(s)))
        if rr is None and key.startswith("T1_SNv2"):
            rr = LP_RESULTS[f"state-env__la_T1_SN_s{s}_r8"][0]
        if rr is not None:
            m, v = lstar([(L, rr[L][0]) for L in range(11, 17)] + [(17, bn[17][0] + bc[17][0]),
                                                                  (18, bn[18][0] + bc[18][0])])
            emit(meta, "rr600(ms48 read)+long2_91(ms96 read)", 691, m, v,
                 src + "__{new,cal}.json + rr600 read of rows above", group="E:mixed reads (L* to 18+)",
                 pver=V_RR600 + ";" + V_L2 + ";" + V_L2C)
# step-cap check re-reads of SN12 T1 s2/s3 at ms96 (rr600 + ge17)
for s in (2, 3):
    key = f"T1_SN12_s{s}_ms96"
    meta = dict(family="ours-3.2M-lean_staten-cap12", label=f"SN-cap12 T1 (la_T1_SN12_s{s}_r8) ms96 re-read",
                params="3.2M", format="lean_staten", cap=12, stage="T1", seed=str(s), train_set=TRAIN[12],
                date="2026-09-30", settings=dict(batch=2048, max_steps=96))
    src = f"fork:dan_long-pool-2:artifacts/lpool2/rr/{key}"
    summ = json.loads(git_show("dan_long-pool-2", f"artifacts/lpool2/rr/{key}__rr600.json"))
    g = json.loads(git_show("dan_long-pool-2", f"artifacts/lpool2/rr/{key}__ge17.json"))
    by = by_from_summary(summ)
    rr600_rows_out(meta, by, None, src + "__rr600.json", G_MS96, summ, gen_ok=False)
    emit(meta, "ge17_70", 70, "solved", g["solved"], src + "__ge17.json", L="17+", group=G_MS96, pver=V_GE17,
         summ=g)
    m, v = lstar([(L, by[L][0]) for L in range(11, 17)] + [(17, g["solved"])])
    emit(meta, "rr600+ge17_70", 670, m, v, src + "__rr600.json + __ge17.json", group=G_MS96,
         pver=V_RR600 + ";" + V_GE17, summ=summ)

# ================================================================ 4. best-state (+ compute-match) rr600 / long2(21)
BS = []
for cap in (6, 12):
    for s in range(3):
        BS.append(("dan_best-state", "artifacts/bs/eval", f"Fz_best{cap}_s{s}", f"best-9.56M-lean_staten-cap{cap}",
                   f"best (Robbie recipe) cap{cap} frozen (best-state stage1 s{s})", "9.56M", cap, "frozen", str(s)))
        BS.append(("dan_best-state", "artifacts/bs/eval", f"T1_best{cap}_s{s}", f"best-9.56M-lean_staten-cap{cap}",
                   f"best cap{cap} T1 (best-state la_T1_best{cap}_s{s}_r8)", "9.56M", cap, "T1", str(s)))
for s in range(2):
    BS.append(("dan_best-state", "artifacts/bs/eval", f"Fz_SN6_s{s}", "ours-3.2M-lean_staten-cap6",
               f"SN-v2 frozen (best-state re-read Fz_SN6_s{s})", "3.2M", 6, "frozen", f"S1s{s}"))
    BS.append(("dan_best-state", "artifacts/bs/eval", f"T1_SN6_s{s}", "ours-3.2M-lean_staten-cap6",
               f"SN-v2 T1 (best-state re-read T1_SN6_s{s})", "3.2M", 6, "T1", f"S1s{s}"))
for s in range(3):
    BS.append(("dan_compute-match", "artifacts/cm/eval", f"T1_cm12k64_s{s}", "ours-3.2M-lean_staten-cap12",
               f"SN-cap12 T1 k64-ladder (compute-match la_T1_cm12k64_s{s}_r8)", "3.2M", 12, "T1-k64", str(s)))
    BS.append(("dan_compute-match", "artifacts/cm/eval", f"T1_SN12_s{s}", "ours-3.2M-lean_staten-cap12",
               f"SN-cap12 T1 (compute-match re-read of la_T1_SN12_s{s}_r8)", "3.2M", 12, "T1", str(s)))
TRAIN_BS = {("9.56M", 6): "best recipe cap-6 set", ("9.56M", 12): "best recipe K12 155k"}
for br, d, key, fam, lab, params, cap, stage, seed in BS:
    run = br.split("_", 1)[1]
    meta = dict(family=fam, label=lab, params=params, format="lean_staten", cap=cap, stage=stage, seed=seed,
                train_set=TRAIN_BS.get((params, cap), TRAIN[cap]),
                date="2026-09-30" if run == "best-state" else "2026-10-02",
                settings=dict(batch=2048, max_steps=96))
    src = f"fork:{br}:{d}/{key}"
    summ = l2 = None
    try:
        summ = json.loads(git_show(br, f"{d}/{key}__rr600.json"))
    except subprocess.CalledProcessError:
        pass
    l2 = json.loads(git_show(br, f"{d}/{key}__long2.json"))
    b2 = by_from_summary(l2)
    for L, lab_L in ((17, "17"), (18, "18+")):
        emit(meta, "long2_21", b2[L][1], "solved", b2[L][0], src + "__long2.json", L=lab_L, group=G_L2_21,
             pver=V_L2, summ=l2)
    emit(meta, "long2_21", 21, "solved", l2["solved"], src + "__long2.json", group=G_L2_21, pver=V_L2, summ=l2)
    if summ is None:
        continue
    by = by_from_summary(summ)
    gen_rows = None
    if key.startswith("Fz_best"):  # per-theorem rows are small enough to fetch -> generator split / Q
        gen_rows = jl(bucket(f"best-state/artifacts/bs/eval/{key}__rr600.jsonl"))
    if gen_rows is not None:
        by, byg, maxl, _ = rr600_from_rows(gen_rows)
        rr600_rows_out(meta, by, byg, f"hf://buckets/dan-pandori/nd-rl/best-state/artifacts/bs/eval/{key}__rr600.jsonl",
                       G_MS96, summ)
    else:
        rr600_rows_out(meta, by, None, src + "__rr600.json", G_MS96, summ, gen_ok=False)
    emit(meta, "rr600", 600, "max_accepted_lines", hist_max(summ), src + "__rr600.json", group=G_MS96,
         pver=V_RR600, summ=summ)
    frontier(summ, meta, "rr600", 600, src + "__rr600.json", G_MS96, V_RR600)
    emit(meta, "long2_21", 21, "max_accepted_lines", hist_max(l2), src + "__long2.json", group=G_L2_21, pver=V_L2,
         summ=l2)
    m, v = lstar([(L, by[L][0]) for L in range(11, 17)] + [(17, b2[17][0]), (18, b2[18][0])])
    emit(meta, "rr600+long2_21", 621, m, v, src + "__rr600.json + __long2.json", group=G_MS96,
         pver=V_RR600 + ";" + V_L2, summ=summ)
    m, v = lstar([(L, by[L][0]) for L in range(11, 17)])
    emit(meta, "rr600", 600, m, v, src + "__rr600.json", group=G_MS96, pver=V_RR600, summ=summ)

# ================================================================ 5. copied rows (A/B/C part metrics)
FAMMAP = {
    "ours-3.2M-SN-cap12": "ours-3.2M-lean_staten-cap12", "ours-3.2M-SN-cap12-k64ladder": "ours-3.2M-lean_staten-cap12",
    "ours-3.2M-SN-cap6": "ours-3.2M-lean_staten-cap6", "ours-3.2M-SN-v2-cap6": "ours-3.2M-lean_staten-cap6",
    "ours-3.2M-K12-wholeproof": "ours-3.2M-lean_seq-cap12",
    "best-9.56M-cap6": "best-9.56M-lean_staten-cap6", "best-9.56M-cap12": "best-9.56M-lean_staten-cap12",
}
COPY_GROUP = {
    "transfer2285": "F:transfer2285 (old pool; 23 thms at L>=13, censored at 14)",
    "ladderA-transfer2285": "G:ladder-A transfer2285 nd_verify",
    "ladderA-targets4495": "G:ladder-A targets4495 nd_verify",
    "transfer_long282": "H:transfer_long282 textbook (state-readouts)",
}
for part in "ABC":
    with open(os.path.join(ATLAS, "raw", f"{part}_metrics.csv")) as f:
        for r in csv.DictReader(f):
            pool, metric = r["pool"], r["metric"]
            keep = (metric.startswith("L_star") and pool in COPY_GROUP) or pool.startswith("Q291") or \
                pool == "transfer_long282" or \
                (pool == "rr600_Q_Ltrue13-16" and (r["family"].startswith("best-9.56M") and r["stage"] == "T1"
                                                   or r["stage"] == "T1-k64"))
            if not keep:
                continue
            if metric.startswith("L_star") and pool not in COPY_GROUP:
                continue
            out = {c: r.get(c, "") for c in COLS}
            out["family"] = FAMMAP.get(r["family"], r["family"])
            if pool.startswith("Q291"):
                out["apples_group"] = "I:Q291 = long2_91 + rr600 gen 15-16 (frontier-supply / search-expert reads)"
            elif pool == "rr600_Q_Ltrue13-16":
                out.update(pool="rr600_gen_L13-16", metric="Q", apples_group=G_MS96, pool_version=V_RR600,
                           max_steps="96", batch="2048")
            else:
                out["apples_group"] = COPY_GROUP[pool]
            if out not in rows:
                rows.append(out)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
    w.writeheader()
    for r in rows:
        w.writerow(r)
n_re = sum(r["provenance"] == "recomputed" for r in rows)
print(f"wrote {OUT}: {len(rows)} rows ({n_re} recomputed, {len(rows) - n_re} copied)")

# ---------------------------------------------------------------- cross-check vs summary numbers (stdout only)
if "--check" in sys.argv:
    idx = defaultdict(list)
    for r in rows:
        idx[(r["family"], r["stage"], r["seed"], r["pool"], r["metric"], str(r["L"]))].append(
            (r["provenance"], r["value"], r["apples_group"][:1]))
    for k, v in sorted(idx.items()):
        vals = {str(x[1]) for x in v}
        if len(v) > 1 and len(vals) > 1:
            print("DIFF", k, v)
