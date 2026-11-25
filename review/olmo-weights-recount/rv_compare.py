"""Reviewer (olmo-weights): compare my on-pod recompute (rv_recompute.py task_*.json) with the executor's per-tensor
rows (stats/<job>/shard_*/{iv,st,lag,lora}.csv.gz, lora_norms.csv). Per tensor and in total:
||Delta||^2, ||theta||^2, counts (bitwise equal, <= 1 ulp), lag-1 dot / cosine, offsets from the stage start, LoRA dots.
Tolerance: 1e-4 relative (the brief); counts are compared exactly as well.
Usage: python3 rv_compare.py ROOT RECOMPUTE_OUTDIR OUT.json"""
import glob, json, math, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_load import load

ROOT, RD, OUTF = sys.argv[1], sys.argv[2], sys.argv[3]
D, J = load(ROOT)
TOL = 1e-4


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def idx_rows(job, kind, key):
    out = {}
    for r in D[job][kind]:
        out[key(r)] = r
    return out


report = {"tasks": []}
for p in sorted(glob.glob(os.path.join(RD, "task_*.json")), key=lambda x: int(x.split("_")[-1].split(".")[0])):
    T = json.load(open(p))
    t = T["task"]
    job = t["job"]
    res = dict(task=t, file=os.path.basename(p))
    iv = idx_rows(job, "iv", lambda r: (r["chain"], int(r["idx"]), r["tensor"]))
    st = idx_rows(job, "st", lambda r: (r["chain"], int(r["idx"]), r["tensor"]))
    lag = idx_rows(job, "lag", lambda r: (r["chain"], int(r["idx"]), int(r["lag"]), r["tensor"]))
    worst = defaultdict(float)
    cnt_mism = defaultdict(int)
    tot = defaultdict(float)
    n_t = 0
    if t["kind"] in ("triple", "pair"):
        ch, i = t["chain"], t["idx"]
        for r in T["rows"]:
            n_t += 1
            name = r["tensor"]
            if t["kind"] == "pair":
                e = iv[(ch, i, name)]
                assert e["a"] == t["a"] and e["b"] == t["b"]
                pairs = [("d2", r["d2"], e["d2"]), ("na2", r["na2"], e["na2"]), ("nb2", r["nb2"], e["nb2"])]
                cpairs = [("n_eq", r["n_eq"], e["n_eq"]), ("n_ulp", r["n_ulp"], e["n_ulp"]),
                          ("numel", r["numel"], e["numel"])]
            else:
                e2 = iv[(ch, i, name)]          # a -> b
                e1 = iv[(ch, i - 1, name)]      # a2 -> a
                assert (e2["a"], e2["b"], e1["a"], e1["b"]) == (t["a"], t["b"], t["a2"], t["a"])
                s2, s1 = st[(ch, i, name)], st[(ch, i - 1, name)]
                assert s2["s"] == t["s"]
                L1 = lag[(ch, i, 1, name)]
                pairs = [("d2", r["d2_2"], e2["d2"]), ("na2", r["nb2_1"], e2["na2"]), ("nb2", r["nb2_2"], e2["nb2"]),
                         ("d2_prev", r["d2_1"], e1["d2"]), ("na2_prev", r["na2_1"], e1["na2"]),
                         ("o2", r["o2_b"], s2["o2"]), ("o2_prev", r["o2_a"], s1["o2"])]
                cpairs = [("n_eq", r["eq_2"], e2["n_eq"]), ("n_ulp", r["ulp_2"], e2["n_ulp"]),
                          ("n_eq_prev", r["eq_1"], e1["n_eq"]), ("n_ulp_prev", r["ulp_1"], e1["n_ulp"]),
                          ("n_eq_s", r["eqs_b"], s2["n_eq_s"]), ("n_ulp_s", r["ulps_b"], s2["n_ulp_s"]),
                          ("n_eq_s_prev", r["eqs_a"], s1["n_eq_s"]), ("n_ulp_s_prev", r["ulps_a"], s1["n_ulp_s"]),
                          ("numel", r["numel"], e2["numel"])]
                # dots: compare as cosines (absolute difference), since a dot can be ~0
                cos_mine = r["lag1"] / math.sqrt(r["d2_1"] * r["d2_2"]) if r["d2_1"] * r["d2_2"] > 0 else 0.0
                cos_exec = float(L1["dot"]) / math.sqrt(float(e1["d2"]) * float(e2["d2"])) \
                    if float(e1["d2"]) * float(e2["d2"]) > 0 else 0.0
                worst["cos_lag1_absdiff"] = max(worst["cos_lag1_absdiff"], abs(cos_mine - cos_exec))
                if r["o2_a"] > 0 and r["d2_2"] > 0:
                    cp_m = r["dp_b"] / math.sqrt(r["o2_a"] * r["d2_2"])
                    cp_e = float(s2["dot_prev"]) / math.sqrt(float(s1["o2"]) * float(e2["d2"]))
                    worst["cos_prev_offset_absdiff"] = max(worst["cos_prev_offset_absdiff"], abs(cp_m - cp_e))
                tot["lag1_mine"] += r["lag1"]; tot["lag1_exec"] += float(L1["dot"])
                tot["dp_mine"] += r["dp_b"]; tot["dp_exec"] += float(s2["dot_prev"])
            for nm, a, b in pairs:
                b = float(b)
                tot[nm + "_mine"] += a; tot[nm + "_exec"] += b
                if b != 0 or a != 0:
                    worst[nm] = max(worst[nm], rel(a, b))
            for nm, a, b in cpairs:
                b = int(b)
                tot[nm + "_mine"] += a; tot[nm + "_exec"] += b
                if a != b:
                    cnt_mism[nm] += 1
                    worst[nm] = max(worst[nm], rel(a, b) if b else float(a != b))
        tot_rel = {k[:-5]: rel(tot[k], tot[k[:-5] + "_exec"]) for k in tot if k.endswith("_mine")}
        if t["kind"] == "triple":
            cm = tot["lag1_mine"] / math.sqrt(tot["d2_prev_mine"] * tot["d2_mine"])
            ce = tot["lag1_exec"] / math.sqrt(tot["d2_prev_exec"] * tot["d2_exec"])
            res["cos_lag1_overall"] = dict(mine=cm, exec=ce, absdiff=abs(cm - ce))
            res["r_overall"] = dict(mine=math.sqrt(tot["d2_mine"] / tot["na2_mine"]),
                                    exec=math.sqrt(tot["d2_exec"] / tot["na2_exec"]))
            res["ulp_frac_overall"] = dict(mine=tot["n_ulp_mine"] / tot["numel_mine"],
                                           exec=tot["n_ulp_exec"] / tot["numel_exec"])
            res["eq_frac_overall"] = dict(mine=tot["n_eq_mine"] / tot["numel_mine"],
                                          exec=tot["n_eq_exec"] / tot["numel_exec"])
        else:
            res["r_overall"] = dict(mine=math.sqrt(tot["d2_mine"] / tot["na2_mine"]),
                                    exec=math.sqrt(tot["d2_exec"] / tot["na2_exec"]))
            res["ulp_frac_overall"] = dict(mine=tot["n_ulp_mine"] / tot["numel_mine"],
                                           exec=tot["n_ulp_exec"] / tot["numel_exec"])
        res.update(n_tensors=n_t, worst_per_tensor=dict(worst), count_mismatches=dict(cnt_mism), total_rel=tot_rel)
        res["pass"] = (all(v <= TOL for k, v in worst.items()) and all(v <= TOL for v in tot_rel.values()))
    else:   # lora task
        lo = idx_rows(job, "lora", lambda r: (r["b"], r["tensor"]))
        nrm = {r["tensor"]: r for r in D[job]["lora_norms"]}
        sts = {(r["b"], r["tensor"]): r for r in D[job]["st"]}
        for r in T["st_rows"]:
            e = sts[(t["b"], r["tensor"])]
            assert e["s"] == t["s"]
            n_t += 1
            for nm, a, b in (("o2", r["o2"], float(e["o2"])),):
                tot[nm + "_mine"] += a; tot[nm + "_exec"] += b
                if b or a:
                    worst[nm] = max(worst[nm], rel(a, b))
            for nm, a, b in (("n_eq_s", r["n_eq_s"], int(e["n_eq_s"])), ("n_ulp_s", r["n_ulp_s"], int(e["n_ulp_s"])),
                             ("numel", r["numel"], None)):
                if b is None:
                    tot["numel_mine"] += a
                    continue
                tot[nm + "_mine"] += a; tot[nm + "_exec"] += b
                if a != b:
                    cnt_mism[nm] += 1
                    worst[nm] = max(worst[nm], rel(a, b) if b else 1.0)
        agg = defaultdict(float)
        rnd_cos = defaultdict(float)
        for r in T["lora_rows"]:
            e = lo[(t["b"], r["tensor"])]
            nn = nrm[r["tensor"]]
            for nm in ("main", "ctrl"):
                a, b = r[f"dot_{nm}"], float(e[f"dot_{nm}"])
                # per-matrix cosine difference (dots can be near 0)
                ca = a / math.sqrt(r["o2"] * r[f"n2_{nm}"])
                cb = b / math.sqrt(float(e["o2"]) * float(nn[f"n2_{nm}"]))
                worst[f"cos_{nm}_absdiff"] = max(worst[f"cos_{nm}_absdiff"], abs(ca - cb))
                worst[f"dot_{nm}_rel"] = max(worst[f"dot_{nm}_rel"], rel(a, b))
                worst[f"n2_{nm}"] = max(worst[f"n2_{nm}"], rel(r[f"n2_{nm}"], float(nn[f"n2_{nm}"])))
                agg[f"dot_{nm}_mine"] += a; agg[f"dot_{nm}_exec"] += b
                agg[f"n2_{nm}_mine"] += r[f"n2_{nm}"]; agg[f"n2_{nm}_exec"] += float(nn[f"n2_{nm}"])
            worst["dot_main_ctrl"] = max(worst["dot_main_ctrl"], rel(r["dot_main_ctrl"], float(nn["dot_main_ctrl"])))
            agg["o2_mine"] += r["o2"]; agg["o2_exec"] += float(e["o2"])
            for q in range(8):
                rnd_cos[f"q{q}"] += r[f"dot_q{q}"]
                agg[f"n2_q{q}"] += r[f"n2_q{q}"]
        cos = {}
        for nm in ("main", "ctrl"):
            for who in ("mine", "exec"):
                cos[f"{nm}_{who}"] = agg[f"dot_{nm}_{who}"] / math.sqrt(agg[f"o2_{who}"] * agg[f"n2_{nm}_{who}"])
        rc = [rnd_cos[f"q{q}"] / math.sqrt(agg["o2_mine"] * agg[f"n2_q{q}"]) for q in range(8)]
        mu = sum(rc) / 8
        sd = math.sqrt(sum((x - mu) ** 2 for x in rc) / 7)
        res.update(n_tensors=n_t, n_lora=len(T["lora_rows"]), worst_per_tensor=dict(worst),
                   count_mismatches=dict(cnt_mism), cos=cos, my_random=dict(mean=mu, sd=sd, values=rc),
                   z_main_mine=(cos["main_mine"] - mu) / sd,
                   total_rel={k[:-5]: rel(tot[k], tot[k[:-5] + "_exec"]) for k in tot if k.endswith("_mine")
                              and k[:-5] + "_exec" in tot},
                   ulp_frac_overall=dict(mine=tot["n_ulp_s_mine"] / tot["numel_mine"],
                                         exec=tot["n_ulp_s_exec"] / tot["numel_mine"]),
                   dist_overall=dict(o2_mine=tot["o2_mine"], o2_exec=tot["o2_exec"]))
        res["pass"] = (all(v <= TOL for k, v in worst.items() if not k.startswith("dot_") or k == "dot_main_ctrl")
                       and abs(cos["main_mine"] - cos["main_exec"]) <= TOL * abs(cos["main_exec"]) + 1e-9
                       and abs(cos["ctrl_mine"] - cos["ctrl_exec"]) <= TOL * abs(cos["ctrl_exec"]) + 1e-9
                       and all(v <= TOL for v in res["total_rel"].values()))
    report["tasks"].append(res)
s = os.path.join(RD, "summary.json")
if os.path.exists(s):
    S = json.load(open(s))
    report["pod"] = {k: v for k, v in S.items() if k != "files"}
    report["files"] = dict(n=len(S["files"]), all_sha_ok=S["all_sha_ok"], bytes=S["downloaded_bytes"])
json.dump(report, open(OUTF, "w"), indent=1)
for r in report["tasks"]:
    t = r["task"]
    print(t["kind"], t.get("job"), t.get("chain"), t.get("idx"), t.get("b"), "PASS" if r["pass"] else "FAIL",
          "worst", {k: f"{v:.1e}" for k, v in r["worst_per_tensor"].items()}, "count_mism", r["count_mismatches"])
