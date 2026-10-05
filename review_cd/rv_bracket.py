#!/usr/bin/env python3
"""Reviewer: J1-based quantities.  Known-proof sum LB(t) = log sum_{y in F(t)} pi_ck(y|t) (exact 33-base term where
stage 2 scored y, else the stage-1 bound b0 - ln 33), base sampling p-hat / CP bounds from every standard-cap pend
attempt, budgets from trajectory's compute rows.  Q3, Q4, Q5, Q6, Q7, Q15, J1 stage-1 expectation, replay failures."""
import json, os, sys, glob, gzip, math, collections
import numpy as np
from scipy.stats import beta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
LN33 = math.log(33)
CD = L.CD
SETS = json.load(open(f'{CD}/j1/sets.json'))
MY = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
# budgets: trajectory compute.json (T1 ladder GPU-s, reads GPU-s / attempts); J2 cost 470 s / 131,072 attempts (s0_c00)
TC = json.load(open(os.path.expanduser('~/work/trajectory/artifacts/tj/compute.json')))
def lse(v):
    v = [x for x in v if x is not None and x > -math.inf]
    if not v: return -math.inf
    m = max(v); return m + math.log(sum(math.exp(x - m) for x in v))
def cpu(c, n, a=0.05): return 1.0 if c >= n else float(beta.ppf(1 - a, c + 1, n - c))
def cpl(c, n, a=0.05): return 0.0 if c == 0 else float(beta.ppf(a, c, n - c + 1))

BUD = {}
for s in (0, 1, 2):
    lad = TC[f'T1 ladder|{s}']; rd = TC[f'reads|{s}']
    rs = rd['gpu_seconds'] / rd['attempts']
    Kt = lad['gpu_seconds'] / rs
    BUD[s] = dict(K_total=Kt, K_total_att=lad['attempts'], K_per=Kt / 4495, K_per_att=lad['attempts'] / 4495,
                  K_es=lad['gpu_seconds'] / (322 * 470 / 131072), read_s=rs)
    print(f's{s}: ladder r8 {lad["gpu_seconds"]:,.0f} GPU-s, {lad["attempts"]:,} attempts; read {1e3 * rs:.2f} ms/attempt -> '
          f'K_total {Kt:,.0f} (attempts {lad["attempts"]:,}); K_per {Kt / 4495:,.0f} (attempts {lad["attempts"] / 4495:,.0f}); K_eval-set {BUD[s]["K_es"]:,.0f}')

def j1(s):
    """{name: {tid: {label: (t10, t08, exact?)}}}, replay stats"""
    by = collections.defaultdict(dict); rep = collections.Counter()
    for p in sorted(glob.glob(f'{CD}/j1/b1_s{s}_p*/compact.jsonl.gz')):
        for r in L.rows(p):
            rep['s1_ok' if r['replay_ok'] else 's1_fail'] += 1
            if r['replay_ok']:
                by[r['name']][r['tid']] = {k: (v[0] - LN33, v[2] - LN33, False) for k, v in r['sc'].items()}
    for r in L.rows(f'{CD}/j1/b33_s{s}/compact.jsonl.gz'):
        rep['s2_ok' if r['replay_ok'] else 's2_fail'] += 1
        if r['replay_ok']:
            d = by[r['name']].setdefault(r['tid'], {})
            for k, v in r['sc'].items():
                d[k] = (v[0], v[2], True)
    return by, rep

def pend_samples(s):
    """all standard-cap pend attempts: x0, x1 (trajectory), x2 (mcts pool), x4 (mcts C), J2 c/cal/d/b, J9."""
    c = collections.defaultdict(lambda: [0, 0])
    for x in (0, 1, 2):
        for n, v in L.both(12, s, 'pend', x).items():
            c[n][0] += v[0]; c[n][1] += v[1]
    for n, v in L.read(12, s, 'pend', 'C', 4).items():
        c[n][0] += v[0]; c[n][1] += v[1]
    for p in glob.glob(f'{CD}/j2/s{s}_*.jsonl'):
        if os.path.basename(p).split('_')[1].startswith('t'):
            continue
        for r in L.rows(p):
            c[r['name']][0] += r['n_ok']; c[r['name']][1] += r['n_tried']
    for p in glob.glob(f'{CD}/j9/s{s}_k*.jsonl'):
        if p.endswith('.full.jsonl'): continue
        for r in L.rows(p):
            c[r['name']][0] += r['n_ok']; c[r['name']][1] += r['n_tried']
    return c

def ev_scores(s):
    """trajectory tj_score eventual (r8 best x0) proofs: {name: {ck: (T1 total, T0.8 total)}}"""
    D = os.path.expanduser(f'~/work/trajectory/artifacts/tj/score/s{s}')
    out = collections.defaultdict(dict)
    for ck in ('p0', 'pend', 'r8'):
        for r in L.rows(f'{D}/s{s}_{ck}.jsonl'):
            if r['tid'].startswith('ev:'):
                out[r['tid'][3:]][ck] = (r['T1.0']['total'], r['T0.8']['total'])
    return out

RES = {}
for s in (0, 1, 2):
    by, rep = j1(s)
    lab = lambda ck: f's{s}_{ck}'
    print(f'\ns{s}: replay: stage 1 ok {rep["s1_ok"]} fail {rep["s1_fail"]} ({100 * rep["s1_fail"] / (rep["s1_ok"] + rep["s1_fail"]):.2f} %); '
          f'stage 2 ok {rep["s2_ok"]} fail {rep["s2_fail"]}')
    LB, LB1, MX, NEX = {}, {}, {}, {}
    for n, d in by.items():
        LB[n] = {ck: (lse([v[lab(ck)][0] for v in d.values() if lab(ck) in v]), lse([v[lab(ck)][1] for v in d.values() if lab(ck) in v]))
                 for ck in ('init', 'pend', 'r8', 'r16')}
        MX[n] = max(v[lab('pend')][1] for v in d.values() if lab('pend') in v)
        NEX[n] = sum(1 for v in d.values() if v.get(lab('pend'), (0, 0, False))[2])
    # stage-1-only LB (all b0 - ln33)
    for p in sorted(glob.glob(f'{CD}/j1/b1_s{s}_p*/compact.jsonl.gz')):
        for r in L.rows(p):
            if r['replay_ok']:
                LB1.setdefault(r['name'], []).append(r['sc'][lab('pend')][2] - LN33)
    LB1 = {n: lse(v) for n, v in LB1.items()}
    ps = pend_samples(s)
    B = MY['eqk'][f's{s}_r8_x0']
    H = set(SETS[str(s)]['H']); CAL = SETS[str(s)]['CAL']
    Bt = BUD[s]
    # ---- Q15 / J1 stage-1 expectation: calibration
    r_all = [math.exp(LB[n]['pend'][1]) / (ps[n][0] / ps[n][1]) for n in CAL if n in LB]
    r_1 = [math.exp(LB1[n]) / (ps[n][0] / ps[n][1]) for n in CAL if n in LB1]
    r_t1 = [math.exp(LB[n]['pend'][0]) / (ps[n][0] / ps[n][1]) for n in CAL if n in LB]
    print(f'  Q15 calibration ({len(r_all)} of {len(CAL)}): median exp(LB)/p-hat (T 0.8) {np.median(r_all):.3f} '
          f'[IQR {np.percentile(r_all, 25):.3f}, {np.percentile(r_all, 75):.3f}; 10-90 % {np.percentile(r_all, 10):.2f}-{np.percentile(r_all, 90):.2f}]; '
          f'T 1.0: {np.median(r_t1):.3f};  stage-1-only bound: {np.median(r_1):.4f};  p-hat attempts per CAL theorem: {min(ps[n][1] for n in CAL)}-{max(ps[n][1] for n in CAL)}')
    # LB above the sampling UB95?
    above = [n for n in CAL if n in LB and math.exp(LB[n]['pend'][1]) > cpu(*ps[n])]
    print(f'     CAL theorems whose known-proof sum exceeds the sampling UB95: {len(above)}')
    # ---- B: Q3, Q4, Q5, Q6
    BH = [n for n in B if n in H]
    Bnot = [n for n in B if n not in H]
    scored = [n for n in B if n in LB]
    print(f'  B (eqk r8 x0) {len(B)}: in H {len(BH)}; not in H (pend solved on x1) {len(Bnot)}; J1-scored {len(scored)}')
    for kname in ('K_total', 'K_total_att', 'K_per', 'K_per_att', 'K_es'):
        K = Bt[kname]
        el_lb = [n for n in scored if LB[n]['pend'][1] >= -math.log(K)]
        el_lb2 = [n for n in scored if LB[n]['pend'][1] >= math.log(2) - math.log(K)]
        el_samp = [n for n in B if cpl(*ps[n]) >= 1 / K]
        el_any = sorted(set(el_lb) | set(el_samp))
        cr = [n for n in B if cpu(*ps[n]) < 0.05 / K]
        print(f'  {kname:11s} {K:>12,.0f}: LB certifies elicited {len(el_lb)}/{len(B)} = {len(el_lb) / len(B):.2f} (factor-2 margin {len(el_lb2)} = {len(el_lb2) / len(B):.2f}); '
              f'sampling CP-lower certifies {len(el_samp)}; either {len(el_any)} = {len(el_any) / len(B):.2f}; created (UB95 < 0.05/K) {len(cr)}')
    gaps = [LB[n]['pend'][1] - MX[n] for n in scored]
    print(f'  Q5 median over scored B of LB - max log pi_pend (T 0.8): {np.median(gaps):.3f} nats (n {len(gaps)}; IQR {np.percentile(gaps, 25):.2f}-{np.percentile(gaps, 75):.2f})')
    ev = ev_scores(s)
    lnKt = math.log(Bt['K_total'])
    q6 = [n for n in B if n in ev and n in LB and ev[n]['pend'][1] < -lnKt and LB[n]['pend'][1] >= -lnKt]
    q6m = [n for n in B if n in ev and n in LB and ev[n]['pend'][1] < -lnKt and LB[n]['pend'][1] >= math.log(2) - lnKt]
    evB = [n for n in B if n in ev]
    print(f'  Q6 new proof, old theorem: {len(q6)}/{len(B)} = {len(q6) / len(B):.2f} (factor-2 margin {len(q6m)}); B with an ev score {len(evB)}; '
          f'B with ev log pi_pend < -ln K_total: {sum(ev[n]["pend"][1] < -lnKt for n in evB)}')
    sh = []
    for n in evB:
        lr, lb, l0 = ev[n]['r8'][0], ev[n]['pend'][0], ev[n]['p0'][0]
        if lr > l0:
            sh.append((lr - lb) / (lr - l0))
    sh = np.array(sh)
    print(f'  Q7 RL share of bits over init (ev proof, T 1.0): n {len(sh)}; share < 2 %: {np.mean(sh < 0.02):.3f}; median {np.median(sh):.4f}; 95th pct {np.percentile(sh, 95):.4f}; max {sh.max():.4f}')
    RES[s] = dict(LB={n: LB[n] for n in LB}, MX=MX, ps={n: ps[n] for n in ps}, B=B, bud=Bt)
json.dump({str(s): {'LB': v['LB'], 'MX': v['MX'], 'ps': v['ps'], 'bud': v['bud']} for s, v in RES.items()},
          open(f'{L.RV}/review_cd/out_bracket.json', 'w'))
