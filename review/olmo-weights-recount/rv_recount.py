"""Reviewer (olmo-weights): recount every pre-registered quantity from the executor's raw per-tensor statistics, with
my own code (rv_load.py). Writes rv_intervals.csv, rv_chains.csv, rv_modules.csv, rv_recount.json.
Usage: python3 rv_recount.py ROOT OUTDIR
"""
import csv, json, math, os, statistics as stt, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_load import load, module_of

ROOT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
D, J = load(ROOT)

# ----------------------------------------------------------------------------------------------- labels and steps
MERGES = {"s2merge", "s3merge"}
MAINS = {"sftmain", "rlmain", "zifmain", "zmathmain"}
# DPO optimizer steps (one jump; to be checked against Table 48 in phase 1): pairs / batch, 1 epoch
DPO_STEPS = {"32B": 200_000 / 128, "7B": 150_000 / 128}
STAGE = {"s1": "s1", "s2i1": "s2", "s2i2": "s2", "s2": "s2", "s2merge": "s2", "s3": "s3", "s3merge": "s3",
         "sft1e-4": "sft", "sft5e-5": "sft", "sft": "sft", "sftmain": "sft", "dpo": "dpo", "rl": "rl",
         "rlmain": "rl", "zif": "rlz", "zifmain": "rlz", "zmath": "rlz", "zmathmain": "rlz", "zcode": "rlz"}


def parse(lab):
    p = lab.split("/")
    return p[0], p[1], (int(p[2]) if len(p) > 2 else None)


def kind_steps(a, b):
    fa, ka, sa = parse(a)
    fb, kb, sb = parse(b)
    assert fa == fb
    if kb in MERGES:
        return "merge", 0
    if kb in MAINS:
        return "to_main", None
    if kb == "dpo":
        return "sft_to_dpo", DPO_STEPS[fb]
    if ka == kb and sa is not None and sb is not None:
        if ka == "s1" and sb - sa != 1000:
            return "gap", sb - sa
        return "within", sb - sa
    if STAGE[ka] != STAGE[kb] or ka in MERGES:
        return "boundary", sb
    raise ValueError((a, b))


# ----------------------------------------------------------------------------------------------- learning rates
def lr_sched(fam, lab):
    """LR as a function of the stage step for the labelled checkpoint's run; None if not modelled."""
    _, k, _ = parse(lab)
    if k == "rl":
        return (lambda t: 2e-6) if fam == "32B" else (lambda t: 1e-6)
    if k in ("zif", "zmath", "zcode"):
        return lambda t: 1e-6
    if k in ("sft1e-4", "sft5e-5", "sft"):
        peak = {"sft1e-4": 1e-4, "sft5e-5": 5e-5, "sft": 5e-5}[k]
        T = 10790 if fam == "32B" else 45.4e9 / 1048576
        W = 0.03 * T

        def f(t, peak=peak, T=T, W=W):
            return peak * t / W if t < W else peak * max(T - t, 0) / (T - W)
        return f
    return None


def mean_lr(fam, a, b, n):
    f = lr_sched(fam, b)
    _, ka, sa = parse(a)
    _, kb, sb = parse(b)
    if f is None or n is None or n <= 0:
        return None
    t0 = sa if (ka == kb and sa is not None) else 0
    ts = np.arange(t0 + 1, sb + 1)
    return float(np.mean([f(t) for t in ts])) if ts.size < 50_000 else None


# ----------------------------------------------------------------------------------------------- per-interval sums
IV = {}          # (job, chain, idx) -> dict
MOD = defaultdict(lambda: defaultdict(float))     # (job, chain, idx, module) -> sums
LAY = defaultdict(lambda: defaultdict(float))     # (job, chain, idx, layer) -> sums
PAIR = {}
for job, d in D.items():
    s = defaultdict(lambda: defaultdict(float))
    for r in d["iv"]:
        key = (r["chain"], int(r["idx"]), r["a"], r["b"])
        o = s[key]
        for f in ("numel", "d2", "na2", "nb2", "n_eq", "n_ulp", "n_nonfinite"):
            o[f] += float(r[f])
        mname, L = module_of(r["tensor"])
        for tgt, g in ((MOD, mname), (LAY, L)):
            if g is None:
                continue
            oo = tgt[(job, r["chain"], int(r["idx"]), g)]
            for f in ("numel", "d2", "na2", "n_eq", "n_ulp"):
                oo[f] += float(r[f])
    for (chain, idx, a, b), o in s.items():
        if chain == "pair":
            PAIR[(job, a, b)] = dict(o)
        else:
            IV[(job, chain, idx)] = dict(o, a=a, b=b)
    st = defaultdict(lambda: defaultdict(float))
    for r in d["st"]:
        o = st[(r["chain"], int(r["idx"]))]
        o["s"], o["b"] = r["s"], r["b"]
        for f in ("o2", "n_eq_s", "n_ulp_s", "dot_prev"):
            o[f] += float(r[f])
        mname, _ = module_of(r["tensor"])
        mo = MOD[(job, r["chain"], int(r["idx"]), mname)]
        mo["o2"] += float(r["o2"])
        mo["n_eq_s"] += float(r["n_eq_s"])
    for (chain, idx), o in st.items():
        IV[(job, chain, idx)].update(o2=o["o2"], n_eq_s=o["n_eq_s"], n_ulp_s=o["n_ulp_s"], dot_prev=o["dot_prev"],
                                     s=o["s"])
        assert IV[(job, chain, idx)]["b"] == o["b"]
    lag = defaultdict(float)
    for r in d["lag"]:
        lag[(r["chain"], int(r["idx"]), int(r["lag"]))] += float(r["dot"])
    for (chain, idx, L), v in lag.items():
        IV[(job, chain, idx)][f"lag{L}"] = v

# derived per interval
rows = []
for (job, chain, idx), o in sorted(IV.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
    fam = o["a"].split("/")[0]
    k, n = kind_steps(o["a"], o["b"])
    o["kind"], o["n_steps"] = k, n
    o["r"] = math.sqrt(o["d2"] / o["na2"])
    o["r_per_step"] = o["r"] / n if n else None
    lr = mean_lr(fam, o["a"], o["b"], n)
    o["lr_mean"] = lr
    o["r_per_step_per_lr"] = o["r_per_step"] / lr if (lr and o["r_per_step"]) else None
    o["frac_eq"] = o["n_eq"] / o["numel"]
    o["frac_ulp"] = o["n_ulp"] / o["numel"]
    prev = IV.get((job, chain, idx - 1))
    o["cos_prev"] = o["lag1"] / math.sqrt(o["d2"] * prev["d2"]) if ("lag1" in o and prev) else None
    rows.append(dict(job=job, chain=chain, idx=idx, **{x: o.get(x) for x in
                     ("a", "b", "kind", "n_steps", "numel", "r", "r_per_step", "lr_mean", "r_per_step_per_lr",
                      "frac_eq", "frac_ulp", "cos_prev", "d2", "na2", "nb2", "o2", "s", "n_eq_s", "n_ulp_s")}))
with open(os.path.join(OUT, "rv_intervals.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow(r)


# ----------------------------------------------------------------------------------------------- chains
def chain_iv(job, chain):
    return [IV[(job, chain, i)] for i in range(1, len([c for c in J[job]["chains"] if c["name"] == chain][0]["members"]))]


def start_norm(job, chain):
    return math.sqrt(IV[(job, chain, 1)]["na2"])


def dist(job, chain, idx):
    return math.sqrt(IV[(job, chain, idx)]["o2"]) / start_norm(job, chain)


def straight(job, chain, upto=None):
    ivs = chain_iv(job, chain)
    if upto is not None:
        ivs = [x for x in ivs if x["b"] in upto] and ivs[:[x["b"] for x in ivs].index(upto[-1]) + 1]
    path = sum(math.sqrt(x["d2"]) for x in ivs)
    return math.sqrt(ivs[-1]["o2"]) / path, len(ivs), ivs[-1]["b"]


chains = []
for job in sorted(J):
    for c in J[job]["chains"]:
        assert c["start"] == c["members"][0], (job, c["name"])
        S, n, last = straight(job, c["name"])
        ivs = chain_iv(job, c["name"])
        cos = [x["cos_prev"] for x in ivs if x["cos_prev"] is not None]
        chains.append(dict(job=job, chain=c["name"], start=c["start"], end=last, n_intervals=n, S=S,
                           dist_end=dist(job, c["name"], n), median_cos=stt.median(cos) if cos else None,
                           mean_cos=stt.mean(cos) if cos else None))
with open(os.path.join(OUT, "rv_chains.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(chains[0]))
    w.writeheader()
    for r in chains:
        w.writerow(r)

# ----------------------------------------------------------------------------------------------- modules (per interval)
modrows = []
for (job, chain, idx, m), o in sorted(MOD.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], str(x[0][3]))):
    if chain == "pair":
        continue
    modrows.append(dict(job=job, chain=chain, idx=idx, module=m, numel=o["numel"],
                        r=math.sqrt(o["d2"] / o["na2"]) if o["na2"] else None, frac_eq=o["n_eq"] / o["numel"],
                        frac_ulp=o["n_ulp"] / o["numel"],
                        dist=(math.sqrt(o["o2"] / MOD[(job, chain, 1, m)]["na2"]) if MOD[(job, chain, 1, m)]["na2"]
                              else None)))
with open(os.path.join(OUT, "rv_modules.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(modrows[0]))
    w.writeheader()
    for r in modrows:
        w.writerow(r)
laysum = []
for (job, chain, idx, L), o in sorted(LAY.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])):
    if chain == "pair":
        continue
    laysum.append(dict(job=job, chain=chain, idx=idx, layer=L, r=math.sqrt(o["d2"] / o["na2"]),
                       frac_eq=o["n_eq"] / o["numel"], frac_ulp=o["n_ulp"] / o["numel"]))
with open(os.path.join(OUT, "rv_layers.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(laysum[0]))
    w.writeheader()
    for r in laysum:
        w.writerow(r)

# ----------------------------------------------------------------------------------------------- expectations
R = {}


def within(job, chain, kinds=("within",)):
    return [x for x in chain_iv(job, chain) if x["kind"] in kinds]


def med(xs):
    return stt.median(xs)


# E1
e1 = {}
for fam, (rlj, rlc), (sfj, sfc) in (("32B", ("p32_rl", "rl"), ("p32_sft", "sft-5e-5")),
                                    ("7B", ("p7_rl", "rl"), ("p7_sft", "sft-dpo"))):
    rl = [x for x in within(rlj, rlc)]
    sf = [x for x in within(sfj, sfc) if parse(x["b"])[1].startswith("sft") and parse(x["b"])[1] != "sftmain"]
    mr, ms = med([x["r_per_step"] for x in rl]), med([x["r_per_step"] for x in sf])
    e1[fam] = dict(n_rl=len(rl), n_sft=len(sf), rl_first=rl[0]["a"] + "->" + rl[0]["b"],
                   rl_last=rl[-1]["a"] + "->" + rl[-1]["b"], sft_first=sf[0]["a"] + "->" + sf[0]["b"],
                   sft_last=sf[-1]["a"] + "->" + sf[-1]["b"], median_rl=mr, median_sft=ms, ratio_sft_over_rl=ms / mr,
                   hit=ms / mr >= 10)
    # G2 on the same intervals
    gr = med([x["r_per_step_per_lr"] for x in rl])
    gs = med([x["r_per_step_per_lr"] for x in sf])
    e1[fam].update(g2_median_rl_perlr=gr, g2_median_sft_perlr=gs, g2_ratio_rl_over_sft=gr / gs, g2_hit=gr / gs >= 2)
R["E1_G2"] = e1
R["E1_hit"] = all(v["hit"] for v in e1.values())
R["G2_hit"] = all(v["g2_hit"] for v in e1.values())


def find(job, chain, b):
    for x in chain_iv(job, chain):
        if x["b"] == b:
            return x
    raise KeyError((job, chain, b))


# E2, E3
e2 = {}
x32 = find("p32_rl", "rl", "32B/rl/2300")
s32 = find("p32_sft", "sft-5e-5", "32B/sft5e-5/8000")
rl7_1375 = find("p7_rl", "rl", "7B/rl/1375")
rl7_main = find("p7_rl", "rl", "7B/rlmain")
d1375 = math.sqrt(rl7_1375["o2"]) / start_norm("p7_rl", "rl")
dmain = math.sqrt(rl7_main["o2"]) / start_norm("p7_rl", "rl")
x7 = rl7_main if dmain > d1375 else rl7_1375
s7 = find("p7_sft", "sft-dpo", "7B/sftmain")
for fam, xr, jr, xs, js in (("32B", x32, ("p32_rl", "rl"), s32, ("p32_sft", "sft-5e-5")),
                            ("7B", x7, ("p7_rl", "rl"), s7, ("p7_sft", "sft-dpo"))):
    drl = math.sqrt(xr["o2"]) / start_norm(*jr)
    dsf = math.sqrt(xs["o2"]) / start_norm(*js)
    e2[fam] = dict(rl_last=xr["b"], rl_dist=drl, sft_main=xs["b"], sft_dist=dsf, sft_start=xs["s"],
                   ratio_sft_over_rl=dsf / drl, hit=drl < dsf, rl_ulp_frac=xr["n_ulp_s"] / xr["numel"],
                   rl_eq_frac=xr["n_eq_s"] / xr["numel"], e3_hit=xr["n_ulp_s"] / xr["numel"] > 0.5)
e2["7B"]["d_rl1375"], e2["7B"]["d_rlmain"] = d1375, dmain
R["E2_E3"] = e2

# E4
e4 = {}


def S_of(job, chain, last_b):
    ivs = chain_iv(job, chain)
    k = [x["b"] for x in ivs].index(last_b)
    ivs = ivs[:k + 1]
    return math.sqrt(ivs[-1]["o2"]) / sum(math.sqrt(x["d2"]) for x in ivs), len(ivs)


def S_sub(job, chain, last_b, n_target):
    """straightness on an evenly index-spaced subsample of the chain (members 0..K); chord lengths from o2, dot_prev
    and lags 1-3 (exact when every gap <= 4 intervals). Returns (S, n_intervals, gaps) or None."""
    ivs = chain_iv(job, chain)
    K = [x["b"] for x in ivs].index(last_b) + 1
    pick = sorted({int(round(v)) for v in np.linspace(0, K, n_target + 1)})
    gaps = [b - a for a, b in zip(pick, pick[1:])]
    if max(gaps) > 4:
        return None, len(gaps), gaps
    o2 = {0: 0.0}
    for i in range(1, K + 1):
        o2[i] = IV[(job, chain, i)]["o2"]

    def dot_O_D(i, k):     # <O_i, Delta_k> for k > i
        x = IV[(job, chain, k)]
        v = x["dot_prev"]          # <Delta_k, O_{k-1}>
        for L in range(1, k - i):
            v -= x[f"lag{L}"]       # <Delta_k, Delta_{k-L}>
        return v

    path = 0.0
    for a, b in zip(pick, pick[1:]):
        # ||O_b - O_a||^2 = ||O_b||^2 - ||O_a||^2 - 2 <O_a, O_b - O_a>
        cross = sum(dot_O_D(a, k) for k in range(a + 1, b + 1))
        path += math.sqrt(max(o2[b] - o2[a] - 2 * cross, 0.0))
    return math.sqrt(o2[K]) / path, len(gaps), gaps


for fam, (rlj, rlc, rlb), (sfj, sfc, sfb) in (
        ("32B", ("p32_rl", "rl", "32B/rl/2300"), ("p32_sft", "sft-5e-5", "32B/sft5e-5/10790")),
        ("7B", ("p7_rl", "rl", "7B/rl/1375"), ("p7_sft", "sft-dpo", "7B/sft/43000"))):
    Sr, nr = S_of(rlj, rlc, rlb)
    Ss, ns = S_of(sfj, sfc, sfb)
    sub = S_sub(rlj, rlc, rlb, ns)
    sub2 = S_sub(rlj, rlc, rlb, ns + 1) if sub[0] is None else None
    e4[fam] = dict(S_rl=Sr, n_rl=nr, S_sft=Ss, n_sft=ns, hit=Sr > Ss, S_rl_sub=sub[0], sub_gaps=sub[2],
                   S_rl_sub_next=(sub2[0], sub2[1], sub2[2]) if sub2 else None)
R["E4"] = e4

# E5 (LoRA) per RL step
lo = D["p32_rl"]["lora"]
nrm = {r["tensor"]: r for r in D["p32_rl"]["lora_norms"]}
by_b = defaultdict(list)
for r in lo:
    by_b[r["b"]].append(r)
e5 = {}
names = ["main", "ctrl"] + [f"r{q}" for q in range(8)]
for b, rr in by_b.items():
    assert len(rr) == 448, (b, len(rr))
    o2 = sum(float(r["o2"]) for r in rr)
    cos = {}
    for nm in names:
        dot = sum(float(r[f"dot_{nm}"]) for r in rr)
        n2 = sum(float(nrm[r["tensor"]][f"n2_{nm}"]) for r in rr)
        cos[nm] = dot / math.sqrt(o2 * n2)
    rnd = [cos[f"r{q}"] for q in range(8)]
    pm = [float(r["dot_main"]) / math.sqrt(float(r["o2"]) * float(nrm[r["tensor"]]["n2_main"])) for r in rr]
    pc = [float(r["dot_ctrl"]) / math.sqrt(float(r["o2"]) * float(nrm[r["tensor"]]["n2_ctrl"])) for r in rr]
    e5[b] = dict(cos_main=cos["main"], cos_ctrl=cos["ctrl"], rnd_mean=stt.mean(rnd), rnd_sd=stt.stdev(rnd),
                 z_main=(cos["main"] - stt.mean(rnd)) / stt.stdev(rnd), mean_permatrix_main=stt.mean(pm),
                 mean_permatrix_ctrl=stt.mean(pc), norm_ratio_main=math.sqrt(
                     sum(float(nrm[r["tensor"]]["n2_main"]) for r in rr) / o2),
                 norm_ratio_ctrl=math.sqrt(sum(float(nrm[r["tensor"]]["n2_ctrl"]) for r in rr) / o2))
z = e5["32B/rl/2300"]
R["E5"] = dict(at_2300=z, hit=(z["cos_main"] > z["cos_ctrl"] and abs(z["cos_main"]) < 0.1 and abs(z["cos_ctrl"]) < 0.1
                               and z["z_main"] > 3),
               parts=dict(main_gt_ctrl=z["cos_main"] > z["cos_ctrl"], both_below_0p1=abs(z["cos_main"]) < 0.1 and
                          abs(z["cos_ctrl"]) < 0.1, main_gt_rnd_3sd=z["z_main"] > 3),
               cos_main_main_ctrl=sum(float(r["dot_main_ctrl"]) for r in nrm.values()) / math.sqrt(
                   sum(float(r["n2_main"]) for r in nrm.values()) * sum(float(r["n2_ctrl"]) for r in nrm.values())),
               by_step={b: (v["cos_main"], v["cos_ctrl"], v["z_main"]) for b, v in sorted(
                   e5.items(), key=lambda x: int(x[0].split("/")[-1]))})

# G1, G6
rl32 = within("p32_rl", "rl", ("within", "boundary"))
sf32 = within("p32_sft", "sft-5e-5") + within("p32_sft", "sft-1e-4")
sf32_1000 = [x for x in sf32 if x["n_steps"] == 1000]
g1 = dict(rl_eq=[x["frac_eq"] for x in rl32], sft_eq=[x["frac_eq"] for x in sf32_1000])
R["G1"] = dict(rl_min=min(g1["rl_eq"]), rl_median=med(g1["rl_eq"]), rl_max=max(g1["rl_eq"]), n_rl=len(rl32),
               rl_n_above_half=sum(v > 0.5 for v in g1["rl_eq"]),
               sft_min=min(g1["sft_eq"]), sft_median=med(g1["sft_eq"]), sft_max=max(g1["sft_eq"]),
               n_sft=len(sf32_1000), sft_n_below_0p1=sum(v < 0.1 for v in g1["sft_eq"]),
               hit_all=min(g1["rl_eq"]) > 0.5 and max(g1["sft_eq"]) < 0.1,
               hit_median=med(g1["rl_eq"]) > 0.5 and med(g1["sft_eq"]) < 0.1)
g6 = []
for x in rl32:
    i = [k for k, v in IV.items() if v is x][0]
    fr = {m: MOD[(i[0], i[1], i[2], m)]["n_eq"] / MOD[(i[0], i[1], i[2], m)]["numel"]
          for m in ("embed", "gate", "up", "down")}
    g6.append(dict(b=x["b"], **fr, holds=fr["embed"] > max(fr["gate"], fr["up"], fr["down"])))
R["G6"] = dict(n=len(g6), n_holds=sum(g["holds"] for g in g6),
               median_embed=med([g["embed"] for g in g6]),
               median_mlp_max=med([max(g["gate"], g["up"], g["down"]) for g in g6]),
               hit_all=all(g["holds"] for g in g6), first=g6[0], last=g6[-1])

# G3 boundaries
def ivb(job, chain, b):
    return find(job, chain, b)


g3 = {}
b12 = ivb("b32_s2", "ingredient1", "32B/s2i1/1000")
l1 = ivb("b32_s1", "stage1-sampled", "32B/s1/656000")
b23 = ivb("b32_s3", "stage3", "32B/s3/1000")
l2 = ivb("b32_s2", "ingredient1", "32B/s2i1/23842")
l2b = ivb("b32_s2", "ingredient2", "32B/s2i2/23842")
b12b = ivb("b32_s2", "ingredient2", "32B/s2i2/4000")
g3["32B"] = dict(s1_s2=(b12["r_per_step"], l1["r_per_step"], b12["r_per_step"] > l1["r_per_step"]),
                 s1_s2_ingr2=(b12b["r_per_step"], l1["r_per_step"]),
                 s2_s3=(b23["r_per_step"], l2["r_per_step"], b23["r_per_step"] > l2["r_per_step"]),
                 s2_s3_vs_ingr2_last=(b23["r_per_step"], l2b["r_per_step"]),
                 last_intervals=(l1["a"] + "->" + l1["b"], l2["a"] + "->" + l2["b"]))
b12 = ivb("b7_s2", "stage2", "7B/s2/1000")
l1 = ivb("b7_s1", "stage1-sampled", "7B/s1/1413814")
b23 = ivb("b7_s3", "stage3", "7B/s3/1000")
l2 = ivb("b7_s2", "stage2", "7B/s2/47684")
g3["7B"] = dict(s1_s2=(b12["r_per_step"], l1["r_per_step"], b12["r_per_step"] > l1["r_per_step"]),
                s2_s3=(b23["r_per_step"], l2["r_per_step"], b23["r_per_step"] > l2["r_per_step"]),
                last_intervals=(l1["a"] + "->" + l1["b"] + f" ({l1['n_steps']})", l2["a"] + "->" + l2["b"] +
                                f" ({l2['n_steps']})"))
R["G3"] = dict(g3, hit=all(g3[f][k][2] for f in g3 for k in ("s1_s2", "s2_s3")))


# Gram sets
def gram(job, gi):
    G = None
    members = None
    for r in D[job]["gram"]:
        if int(r["set"]) != gi:
            continue
        others = r["members"].split("|")
        v = [float(x) for x in r["gram_upper"].split()]
        n = len(others)
        M = np.zeros((n, n))
        k = 0
        for i in range(n):
            for j in range(i, n):
                M[i, j] = M[j, i] = v[k]
                k += 1
        G = M if G is None else G + M
        members = (r["ref"], others)
    return members, G


(ref, oth), G = gram("b32_s2", 0)
xx, xy, yy = G[0, 0], G[0, 1], G[1, 1]
res = math.sqrt(yy - xy + xx / 4)
R["G4_stage2"] = dict(ref=ref, others=oth, resid=res, d_i1_i2=math.sqrt(xx), ratio=res / math.sqrt(xx),
                      best_w=xy / xx, hit=res / math.sqrt(xx) < 0.01)
(ref, oth), G = gram("b32_s3", 0)
# others: 10000, 11000, 11921, merge (offsets from 9000)
iu = [oth.index(x) for x in ("32B/s3/10000", "32B/s3/11000", "32B/s3/11921")]
im = oth.index("32B/s3merge")
Guu = G[np.ix_(iu, iu)]
Gum = G[iu, im]
Gmm = G[im, im]
w = np.linalg.solve(Guu, Gum)
res4 = math.sqrt(max(Gmm - Gum @ w, 0))
eq = np.array([1 / 3, 1 / 3, 1 / 3])
res_eq = math.sqrt(max(Gmm - 2 * eq @ Gum + eq @ Guu @ eq, 0))
d_m_11921 = math.sqrt(Gmm - 2 * G[im, iu[2]] + G[iu[2], iu[2]])
# 3-checkpoint best fit over 10000/11000/11921 only (affine: weights sum to 1): offsets from 11921
P = np.array([[1, 0, -1], [0, 1, -1]], dtype=float)       # (10000-11921), (11000-11921) in terms of offsets from 9000
Gpp = P @ Guu @ P.T
mvec = np.array([0, 0, 1.0])
Gpm = P @ (Gum - Guu @ mvec)
w2 = np.linalg.solve(Gpp, Gpm)
r3 = math.sqrt(max((Gmm - 2 * mvec @ Gum + mvec @ Guu @ mvec) - Gpm @ w2, 0))
R["G4_stage3"] = dict(ref=ref, others=oth, w_4ckpt={"9000": 1 - w.sum(), "10000": w[0], "11000": w[1], "11921": w[2]},
                      resid_4ckpt=res4, resid_equal_thirds=res_eq, d_merge_11921=d_m_11921,
                      ratio_equal_thirds=res_eq / d_m_11921, ratio_best4=res4 / d_m_11921,
                      w_3ckpt={"10000": w2[0], "11000": w2[1], "11921": 1 - w2.sum()}, resid_3ckpt=r3,
                      hit=(res_eq / d_m_11921 < 0.01))
R["G4_hit"] = R["G4_stage2"]["hit"] and R["G4_stage3"]["hit"]

# G5: DPO start soup
(ref, oth), G = gram("p32_sft", 0)
idpo = oth.index("32B/dpo")
dd = G[idpo, idpo]
best = []
c1 = [i for i, x in enumerate(oth) if "sft1e-4" in x]
c5 = [i for i, x in enumerate(oth) if "sft5e-5" in x] + [None]     # None = the reference 5e-5/8000 itself
for i in c1:
    for j in c5:
        xi, gij = G[i, i], (G[i, j] if j is not None else 0.0)
        xj = G[j, j] if j is not None else 0.0
        di, dj = G[i, idpo], (G[j, idpo] if j is not None else 0.0)
        vv = xi - 2 * gij + xj                      # ||x_i - x_j||^2
        ev = (di - dj) - (gij - xj)                 # <d - x_j, x_i - x_j>
        ee = dd - 2 * dj + xj                       # ||d - x_j||^2
        wv = ev / vv
        r2 = ee - ev * ev / vv
        wc = min(max(wv, 0.0), 1.0)
        r2c = ee - 2 * wc * ev + wc * wc * vv
        best.append((math.sqrt(max(r2, 0)), wv, math.sqrt(max(r2c, 0)), wc, oth[i], oth[j] if j is not None else ref))
best.sort()
# single-checkpoint distances to DPO
single = sorted((math.sqrt(max(dd - 2 * (G[i, idpo]) + G[i, i], 0)), oth[i]) for i in range(len(oth)) if i != idpo)
single.append((math.sqrt(dd), ref))
single.sort()
R["G5"] = dict(d_dpo_sftmain=math.sqrt(dd), best_soup=best[0], best_soup_ratio=best[0][0] / math.sqrt(dd),
               best_convex=min(best, key=lambda x: x[2]), top5=best[:5], nearest_single=single[:4],
               hit=best[0][0] / math.sqrt(dd) < 0.5)

# start tests (pairs)
st = {}
for job, chain, first in (("p7_sft", "sft-dpo", "7B/sft/1000"), ("z7_if", "rlzero-if", "7B/zif/100"),
                          ("z7_math", "rlzero-math", "7B/zmath/100"), ("z7_code", "rlzero-code", "7B/zcode/100")):
    x1 = find(job, chain, first)
    p = PAIR[(job, "7B/s3/11000", first)]
    x2 = chain_iv(job, chain)[1]
    st[f"{job}:{first}"] = dict(d_from_main=math.sqrt(x1["d2"]), d_from_s3_11000=math.sqrt(p["d2"]),
                                nearer_main=x1["d2"] < p["d2"], r1_per_step=x1["r_per_step"],
                                r2_per_step=x2["r_per_step"], ratio_1_2=x1["r_per_step"] / x2["r_per_step"],
                                flag=x1["r_per_step"] > 3 * x2["r_per_step"])
p = PAIR[("b32_s3", "32B/s1/656000", "32B/s3/1000")]
x1 = find("b32_s3", "stage3", "32B/s3/1000")
st["b32_s3:stage3-start"] = dict(d_from_s2merge=math.sqrt(x1["d2"]), d_from_s1_656000=math.sqrt(p["d2"]),
                                 rel_from_s2merge=x1["r"], rel_from_s1=math.sqrt(p["d2"] / p["na2"]))
p = PAIR[("p7_sft", "7B/sft/43000", "7B/dpo")]
x1 = find("p7_sft", "sft-dpo", "7B/dpo")
xm = find("p7_sft", "sft-dpo", "7B/sftmain")
st["p7_sft:dpo-start"] = dict(d_dpo_from_sftmain=math.sqrt(x1["d2"]), d_dpo_from_sft43000=math.sqrt(p["d2"]),
                              d_sftmain_from_43000=math.sqrt(xm["d2"]), r_sftmain_from_43000=xm["r"])
R["start_tests"] = st

# duplicate-name placement: distance from base main along the chain around each duplicated name
dup = {}
for job, chain, names_ in (("z7_if", "rlzero-if", ("7B/zif/100", "7B/zif/1000")),
                           ("z7_code", "rlzero-code", ("7B/zcode/100", "7B/zcode/1000", "7B/zcode/200",
                                                       "7B/zcode/2000"))):
    ivs = chain_iv(job, chain)
    seq = [(x["b"], math.sqrt(x["o2"]) / start_norm(job, chain)) for x in ivs]
    dup[job] = dict(seq=seq)
R["duplicates"] = dup

# 7B mains: distance to last branch
mains = {}
for job, chain, b in (("p7_sft", "sft-dpo", "7B/sftmain"), ("p7_rl", "rl", "7B/rlmain"),
                      ("z7_if", "rlzero-if", "7B/zifmain"), ("z7_math", "rlzero-math", "7B/zmathmain")):
    x = find(job, chain, b)
    prev = chain_iv(job, chain)[[y["b"] for y in chain_iv(job, chain)].index(b) - 1]
    mains[b] = dict(from_=x["a"], r=x["r"], r_prev_interval=prev["r"], frac_eq=x["frac_eq"],
                    dist_start=math.sqrt(x["o2"]) / start_norm(job, chain),
                    dist_prev=math.sqrt(prev["o2"]) / start_norm(job, chain))
R["mains"] = mains

# G7
g7 = {}
d_rl1000 = math.sqrt(find("p7_rl", "rl", "7B/rl/1000")["o2"]) / start_norm("p7_rl", "rl")
for job, chain, lab in (("z7_if", "rlzero-if", "7B/zif/1000"), ("z7_math", "rlzero-math", "7B/zmath/1000"),
                        ("z7_code", "rlzero-code", "7B/zcode/1000")):
    dz = math.sqrt(find(job, chain, lab)["o2"]) / start_norm(job, chain)
    g7[lab] = dict(dist=dz, rl_from_dpo_1000=d_rl1000, holds=dz > d_rl1000)
R["G7_by_label"] = g7

# stage-level unchanged / ulp fractions (medians over each chain's within intervals)
fr = {}
for job in sorted(J):
    for c in J[job]["chains"]:
        ivs = [x for x in chain_iv(job, c["name"]) if x["kind"] == "within"]
        if ivs:
            fr[f"{job}:{c['name']}"] = dict(n=len(ivs), eq_median=med([x["frac_eq"] for x in ivs]),
                                            ulp_median=med([x["frac_ulp"] for x in ivs]),
                                            eq_min=min(x["frac_eq"] for x in ivs), eq_max=max(x["frac_eq"] for x in ivs),
                                            r_per_step_median=med([x["r_per_step"] for x in ivs]),
                                            r_median=med([x["r"] for x in ivs]))
R["fractions_by_chain"] = fr
R["n_intervals"] = len(IV)
R["n_pairs"] = len(PAIR)
R["params"] = {job: sum(float(x["numel"]) for x in [IV[(job, J[job]["chains"][0]["name"], 1)]]) for job in J}
R["n_tensors"] = {job: len(D[job]["tensors"]) for job in D}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    return o


json.dump(clean(R), open(os.path.join(OUT, "rv_recount.json"), "w"), indent=1)
print(json.dumps(clean({k: R[k] for k in ("E1_hit", "G2_hit", "n_intervals", "n_pairs", "params", "n_tensors")})))
