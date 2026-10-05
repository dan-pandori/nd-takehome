#!/usr/bin/env python3
"""Reviewer re-implementation of the run's 12 final created-set definitions (cd_part3.py protocol, own code) + the
pre-registered variants, agreement matrix (Q14), redraw / seed floors.  Comparisons: r8 (x0 defines, x1 redraw), r16
(x1 defines, x0 redraw).  K = K_eval-set = ladder GPU-s / (322 x 3.6 ms)."""
import json, os, sys, glob, gzip, math, collections, re, itertools
import numpy as np
from scipy.stats import beta, binom
from scipy.special import expit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L, g4ip
LN33 = math.log(33); CD = L.CD; N = L.names(); PR = L.prompts()
SETS = json.load(open(f'{CD}/j1/sets.json'))
TC = json.load(open(os.path.expanduser('~/work/trajectory/artifacts/tj/compute.json')))
RCC = {0: 33261, 1: 32844, 2: 31471}          # rl-continue r9-r16 ladder GPU-s (compute_stdout.txt)
LAD = {'r8': {s: TC[f'T1 ladder|{s}']['gpu_seconds'] for s in (0, 1, 2)}}
LAD['r16'] = {s: LAD['r8'][s] + RCC[s] for s in (0, 1, 2)}
KES = lambda s, rl: LAD[rl][s] / (322 * 3.6e-3)
def cpl(c, n, a=0.05): return 0.0 if c == 0 else float(beta.ppf(a, c, n - c + 1))
def lse(v):
    v = [x for x in v if x > -math.inf]
    if not v: return -math.inf
    m = max(v); return m + math.log(sum(math.exp(x - m) for x in v))
def jac(a, b):
    a, b = set(a), set(b); return len(a & b) / len(a | b) if a | b else float('nan')
RULE = re.compile(r':\s*([A-Z]+)\d*\s*((?:N\d+\s*)*)$')
def ruleset(p):
    out = set()
    for part in p.split(';'):
        part = part.strip()
        if not part or part == 'QED': continue
        m = RULE.search(part)
        if not m: return None
        out.add(m.group(1))
    return frozenset(out)
# ---- J1 scores: per tid (bound08, point08) under each label
def j1(s):
    by = collections.defaultdict(dict)
    for p in sorted(glob.glob(f'{CD}/j1/b1_s{s}_p*/compact.jsonl.gz')):
        for r in L.rows(p):
            if r['replay_ok']:
                by[r['name']][r['tid']] = {k: (v[2] - LN33, v[2]) for k, v in r['sc'].items()}
    for r in L.rows(f'{CD}/j1/b33_s{s}/compact.jsonl.gz'):
        if r['replay_ok']:
            d = by[r['name']].setdefault(r['tid'], {})
            for k, v in r['sc'].items(): d[k] = (v[2], v[2])
    return by
# ---- pend: all standard-cap attempts (x0 x1 x2 x4 + J2 c/cal/d/b + J9) and its accepted proofs
def pend_all(s):
    c = collections.defaultdict(lambda: [0, 0]); proofs = collections.defaultdict(set)
    for x in (0, 1, 2):
        for n, v in L.both(12, s, 'pend', x).items():
            c[n][0] += v[0]; c[n][1] += v[1]
            if x in (0, 1): proofs[n].update(v[2])
    for n, v in L.read(12, s, 'pend', 'C', 4).items(): c[n][0] += v[0]; c[n][1] += v[1]
    for p in glob.glob(f'{CD}/j2/s{s}_*.jsonl'):
        if os.path.basename(p).split('_')[1].startswith('t'): continue
        for r in L.rows(p):
            c[r['name']][0] += r['n_ok']; c[r['name']][1] += r['n_tried']; proofs[r['name']].update(r.get('proofs') or [])
    for p in glob.glob(f'{CD}/j9/s{s}_k*.jsonl'):
        if p.endswith('.full.jsonl'): continue
        for r in L.rows(p):
            c[r['name']][0] += r['n_ok']; c[r['name']][1] += r['n_tried']
    return c, proofs
PA = {s: pend_all(s) for s in (0, 1, 2)}
def guided(s):
    return {r['name']: r['n_ok'] for r in L.rows(f'{CD}/j3/s{s}_pend_logical.rows.jsonl.gz')}
G = {s: guided(s) for s in (0, 1, 2)}
# chain: first ladder round solving each transfer theorem (rl-continue cumulative found_transfer_16)
FR = {}
for s in (0, 1, 2):
    fr = {}
    with open(os.path.expanduser(f'~/review/rc_data/s{s}/found_transfer_16.jsonl')) as f:
        for l in f:
            r = json.loads(l)
            if r['name'] in PR:
                fr[r['name']] = min(fr.get(r['name'], 99), r.get('round') or 99)
    FR[s] = fr
# K12 rule sets
K12R = set()
for l in open(f'{L.RV}/data/kh/train_k12.jsonl'):
    rs = ruleset(json.loads(l)['proof'])
    if rs is not None: K12R.add(rs)
print('K12 distinct rule sets', len(K12R))
# schema families (transfer labels), h250 members, key-step restriction by my G4ip
fam = collections.defaultdict(list)
for r in L.rows(f'{L.RV}/data/ladder/transfer.jsonl'):
    if r.get('schema') and r['name'] in PR and r['name'].startswith('la_transfer'):
        fam[r['schema']].append(r['name'])
H250 = set(L.pool_names('h250'))
famkey = {}
for f, mem in fam.items():
    mem = [m for m in mem if m in H250]
    if not mem: continue
    need = [m for m in mem if not g4ip.intuit_provable(PR[m])]
    famkey[f] = need if need else mem
print('schema families with holdout250 members', len(famkey))
# IRT DIF from my fit (rv_irt): need item params -> refit quickly by importing rv_irt? (re-run its fit)
import importlib.util
spec = importlib.util.spec_from_file_location('rvirt', f'{L.RV}/review_cd/rv_irt_fit.py')
rvirt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rvirt)
def dif_created(s, rl, draws):
    cn = rvirt.counts(s, rl, draws); t = rvirt.project(*cn); c, n = cn
    p = expit(rvirt.a * (t - rvirt.b))
    pc, _ = rvirt.counts(s, 'pend', (0, 1))
    out = []
    for i, nm in enumerate(N):
        tail = binom.sf(c[i] - 1, n[i], p[i]) if c[i] > 0 else 1.0
        lo = math.log((c[i] + 0.5) / (n[i] - c[i] + 0.5)) - math.log(p[i] / (1 - p[i]))
        if tail < 1e-3 and lo > math.log(10) and pc[i] == 0:
            out.append(nm)
    return out
DIF = {(s, rl): dif_created(s, rl, (0, 1) if rl == 'r8' else (1,)) for s in (0, 1, 2) for rl in ('r8', 'r16')}
RES = {}
for s in (0, 1, 2):
    by = j1(s); H = set(SETS[str(s)]['H']); (pc, pprf) = PA[s]
    pend_rs = {ruleset(p) for n in pprf for p in pprf[n]} - {None}
    ctrl = {x: L.both(12, s, 'ctrl8', x) for x in (0, 1)}
    j7 = {}
    for x in (0, 1):
        j7[x] = set()
        for pool in ('tb72', 'h250'):
            j7[x] |= {r['name'] for r in L.rows(f'{CD}/j7/s{s}_cont__{pool}_x{x}.jsonl') if r['n_ok'] > 0}
    for rl, xs in (('r8', (0, 1)), ('r16', (1, 0))):
        K = KES(s, rl); lnK = math.log(K)
        for x in xs:
            R = L.both(12, s, rl, x); B = L.both(12, s, 'pend', x)
            D = collections.defaultdict(list)
            for n in N:
                if R[n][0] == 0: continue
                pR = R[n][0] / R[n][1]; cB, nB = pc[n]
                cm = B[n][0] == 0 and nB >= K and cB / nB < 1 / K
                if B[n][0] == 0: D['eqk'].append(n)
                if cm:
                    D['cm'].append(n)
                    if cB == 0: D['cm0'].append(n)
                    if pR >= 0.5: D['rel'].append(n)
                if B[n][0] / B[n][1] < 0.05 and pR >= 0.5: D['rel_prereg'].append(n)
                T = by.get(n, {}); lb, lr = f's{s}_pend', f's{s}_{rl}'
                if B[n][0] == 0 and T:
                    if max(v[lb][0] for v in T.values() if lb in v) < -lnK: D['tfmax'].append(n)
                if n in H:
                    LBv = lse([v[lb][0] for v in T.values() if lb in v]) if T else -math.inf
                    if not (LBv >= math.log(2) - lnK or cpl(cB, nB) >= 1 / K): D['brk_ne'].append(n)
                    if T:
                        num = den = 0.0
                        for v in T.values():
                            if lb in v and lr in v:
                                w = math.exp(v[lr][1]); den += w
                                if v[lb][1] < -lnK: num += w
                        if den > 0 and num / den >= 0.5: D['sharp'].append(n)
                if cm and G[s].get(n, 1) == 0: D['guided'].append(n)
                if cm and n in H250 and FR[s].get(n, 99) >= 2: D['chain'].append(n)
                rs = [ruleset(p) for p in R[n][2]]
                if rs and not any(r in K12R for r in rs): D['ood'].append(n)
                if cm and rs and not any(r in pend_rs for r in rs): D['npnt'].append(n)
            D['irt'] = DIF[(s, rl)]
            for f, mem in famkey.items():
                rb = np.mean([pc[m][1] > 0 and pc[m][0] / pc[m][1] >= 1 / K for m in mem])
                rr = np.mean([R[m][0] > 0 for m in mem])
                if rb <= 0.05 and rr >= 0.5: D['schema'].extend(mem)
            D['cm_recipe'] = [n for n in D['cm'] if sum(PA[t][0][n][0] for t in (0, 1, 2)) == 0]
            D['cm_j7'] = [n for n in D['cm'] if n not in j7[x]]
            for d in list(D):
                D[d + '_net'] = [n for n in D[d] if ctrl[x][n][0] == 0]
            RES[f's{s}_{rl}_x{x}'] = {k: sorted(set(v)) for k, v in D.items()}
DEFS = ['eqk', 'cm', 'rel', 'tfmax', 'brk_ne', 'irt', 'schema', 'guided', 'sharp', 'npnt', 'chain', 'ood']
keys = list(RES)
print(f'{"def":12s} ' + ' '.join(f'{k:>10s}' for k in keys))
for d in DEFS + ['cm0', 'rel_prereg', 'cm_recipe', 'cm_j7'] + [d + '_net' for d in ('eqk', 'cm')]:
    print(f'{d:12s} ' + ' '.join(f'{len(RES[k].get(d, [])):10d}' for k in keys))
print('\nredraw Jaccard r8 (x0 vs x1) per seed | r16 (x1 vs x0) | seed Jaccard r8 x0 (01, 02, 12)')
for d in DEFS:
    rr = [jac(RES[f's{s}_r8_x0'].get(d, []), RES[f's{s}_r8_x1'].get(d, [])) for s in (0, 1, 2)]
    r16 = [jac(RES[f's{s}_r16_x1'].get(d, []), RES[f's{s}_r16_x0'].get(d, [])) for s in (0, 1, 2)]
    sd = [jac(RES[f's{i}_r8_x0'].get(d, []), RES[f's{j}_r8_x0'].get(d, [])) for i, j in ((0, 1), (0, 2), (1, 2))]
    print(f'  {d:8s} ' + ' '.join(f'{v:.2f}' for v in rr) + ' | ' + ' '.join(f'{v:.2f}' for v in r16) + ' | ' + ' '.join(f'{v:.2f}' for v in sd))
for rl, x in (('r8', 0), ('r16', 1)):
    print(f'\nagreement matrix ({rl} x{x}), mean Jaccard over seeds (NaN = both empty, dropped)')
    print(' ' * 9 + ' '.join(f'{d[:7]:>7s}' for d in DEFS))
    off = []; pairs = {}
    for i, d1 in enumerate(DEFS):
        row = []
        for j, d2 in enumerate(DEFS):
            js = [jac(RES[f's{s}_{rl}_x{x}'].get(d1, []), RES[f's{s}_{rl}_x{x}'].get(d2, [])) for s in (0, 1, 2)]
            js = [v for v in js if not math.isnan(v)]
            v = float(np.mean(js)) if js else float('nan'); row.append(v)
            if i < j and not math.isnan(v): off.append(v); pairs[(d1, d2)] = v
        print(f'{d1:9s}' + ' '.join(f'{v:7.2f}' for v in row))
    lo = sorted(pairs.items(), key=lambda kv: kv[1])[:4]
    print(f'  mean off-diagonal {np.mean(off):.3f} over {len(off)} pairs; least-agreeing: ' + ', '.join(f'{a}-{b} {v:.2f}' for (a, b), v in lo))
json.dump(RES, open(f'{L.RV}/review_cd/out_defs.json', 'w'))
