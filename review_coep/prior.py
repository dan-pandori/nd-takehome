"""review_coep/prior.py -- A2 / A3 / A3b / A4 / A5 / A5b recounted with the reviewer's own statistics code.

Inputs: per-member best known-proof log p at pend (artifacts/coe/score/summary.json and rounds_<tag>/summary.json,
`per_member_best`, one name base); r16 / pend x0 read rows (bucket, ~/review/coep_big/eval); first-solve rounds
(artifacts/coe/rounds/*.json); pooled base rates (review_coe/out_cert.json, the create-or-elicit reviewer's)."""
import json, os, sys, math, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

BIGE = os.path.expanduser('~/review/coep_big/eval')
FAM = families()
fam_of = {m: f for f, ms in FAM.items() for m in ms}
S106 = set(strict_names())
out = {}


def ranks(x):
    """average ranks (1-based) with ties"""
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float('nan')


def auc(scores, labels):
    """P(score_pos > score_neg) + 0.5 P(tie) over all pos-neg pairs"""
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return float('nan'), len(pos), len(neg)
    w = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return w / (len(pos) * len(neg)), len(pos), len(neg)


def auc_within(scores, labels, groups):
    w = n = 0
    for g in set(groups):
        idx = [i for i, gg in enumerate(groups) if gg == g]
        pos = [scores[i] for i in idx if labels[i]]
        neg = [scores[i] for i in idx if not labels[i]]
        w += sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
        n += len(pos) * len(neg)
    return (w / n if n else float('nan')), n


summ = json.load(open(P('artifacts/coe/score/summary.json')))['ckpts']


def pend_scores(tag):
    """per-member best log p at pend"""
    if tag in summ:
        a = summ[tag]['heldout']['per_member_best']
    else:
        a = None
    f = P(f'artifacts/coe/score/rounds_{tag}/summary.json')
    b = json.load(open(f))['ckpts']['pend']['heldout']['per_member_best'] if os.path.exists(f) else None
    if a is not None and b is not None:
        assert a == b, tag
    return a if a is not None else b


def solved(fname_list):
    s = set()
    for fn in fname_list:
        rows = read_rows(f'{BIGE}/{fn}.jsonl.gz')
        s |= {n for n, r in rows.items() if r['n_ok'] > 0}
    return s & S106


R16 = {'full_s0': ['r16_full_s0_x0e', 'r16_full_s0_x0h'], 'full_s3': ['r16_full_s3_x0'], 'full_s4': ['r16_full_s4_x0'],
       'full_s5': ['r16_full_s5_x0'], 'dose1_s0': ['r16_dose1_s0_x0'], 'dose1_s1': ['r16_dose1_s1_x0'],
       'dose1_s2': ['r16_dose1_s2_x0']}
R16.update({f'ko_s{s}': [f'r16_ko_s{s}_x0'] for s in range(6)})
PEND = {'full_s0': ['pend_full_s0_x0e', 'pend_full_s0_x0h'], 'full_s3': ['pend_full_s3_x0'], 'full_s4': ['pend_full_s4_x0'],
        'full_s5': ['pend_full_s5_x0'], 'dose1_s0': ['pend_dose1_s0_x0'], 'dose1_s1': ['pend_dose1_s1_x0'],
        'dose1_s2': ['pend_dose1_s2_x0']}
acq = json.load(open(P('review_coe/out_acq.json')))['reads']

print('== A2: median pend log p of the best known proof vs strict solved at r16 (13 ladders)')
xs, ys, tags = [], [], []
for tag in ['full_s0', 'full_s3', 'full_s4', 'full_s5'] + [f'ko_s{s}' for s in range(6)] + [f'dose1_s{s}' for s in range(3)]:
    sc = pend_scores(tag)
    v = sorted(sc.values())
    med = (v[len(v) // 2] + v[(len(v) - 1) // 2]) / 2
    sol = solved(R16[tag])
    ref = acq[f'r16_{tag}_x0']['strict']['solved'] if f'r16_{tag}_x0' in acq else None
    if ref is None:  # old full s0: union of x0e / x0h, as in the create-or-elicit review
        ref = acq['r16_full_s0_x0']['strict']['solved']
    print(f'  {tag:9s} members {len(sc)} median {med:8.3f} (sumfile best_median '
          f'{(summ.get(tag) or json.load(open(P(f"artifacts/coe/score/rounds_{tag}/summary.json")))["ckpts"]["pend"])["heldout"]["best_median"] if tag in summ or os.path.exists(P(f"artifacts/coe/score/rounds_{tag}/summary.json")) else "-":.3f}) '
          f'r16 strict solved {len(sol)} (review_coe {ref})')
    xs.append(med); ys.append(len(sol)); tags.append(tag)
rho = spearman(xs, ys)
dose = [(xs[i], ys[i]) for i, t in enumerate(tags) if t.startswith('dose')]
mono = sorted(dose)[0][1] <= sorted(dose)[1][1] <= sorted(dose)[2][1]
print(f'  Spearman rho (13) = {rho:.3f}; within dose (median, solved) sorted by median: {sorted(dose)}; monotone increasing: {mono}')
rho_noko = spearman([x for x, t in zip(xs, tags) if not t.startswith('ko')], [y for y, t in zip(ys, tags) if not t.startswith('ko')])
print(f'  Spearman without the knockout seeds (7) = {rho_noko:.3f}')
out['A2'] = dict(rho=rho, tags=tags, median=xs, solved=ys, dose_monotone=mono, rho_without_ko=rho_noko)

print('\n== A3: AUC of pend best-known log p for "solved at r16 x0", members with a known proof')
out['A3'] = {}
for tag in ['full_s0', 'full_s3', 'full_s4', 'full_s5', 'dose1_s0', 'dose1_s1', 'dose1_s2']:
    sc = pend_scores(tag)
    mem = sorted(sc)
    assert set(mem) <= S106
    sol = solved(R16[tag])
    lab = [m in sol for m in mem]
    a, npos, nneg = auc([sc[m] for m in mem], lab)
    aw, npairs = auc_within([sc[m] for m in mem], lab, [fam_of.get(m, 'gen') for m in mem])
    # A3b: among members not solved at pend x0, label = solved at r16
    s0 = solved(PEND[tag])
    mem_b = [m for m in mem if m not in s0]
    ab, pb, nb = auc([sc[m] for m in mem_b], [m in sol for m in mem_b])
    print(f'  {tag:9s} n {len(mem)} pos {npos} neg {nneg}: AUC {a:.3f}; within-family {aw:.3f} ({npairs} pairs); '
          f'A3b (not solved at pend: {len(mem_b)}, gained {pb}) AUC {ab:.3f}')
    out['A3'][tag] = dict(n=len(mem), pos=npos, auc=a, auc_within=aw, within_pairs=npairs, a3b_n=len(mem_b), a3b_pos=pb, a3b_auc=ab)

print('\n== A4: Spearman(pend log p, first-solve round; unsolved by r16 -> 17)')
out['A4'] = {}
RF = {'full_s0': 'old_full_s0', 'full_s3': 'la_full_s3', 'full_s4': 'la_full_s4', 'full_s5': 'la_full_s5',
      'dose1_s0': 'la_dose1_s0', 'dose1_s1': 'la_dose1_s1', 'dose1_s2': 'la_dose1_s2'}
for tag, rf in RF.items():
    sc = pend_scores(tag)
    fs = json.load(open(P(f'artifacts/coe/rounds/{rf}.json')))['heldout_first_solve_round']
    mem = sorted(sc)
    r = [fs.get(m, 17) if fs.get(m, 17) <= 16 else 17 for m in mem]
    rho = spearman([sc[m] for m in mem], r)
    fams = collections.defaultdict(list)
    for m, rr in zip(mem, r):
        fams[fam_of.get(m, 'gen')].append((sc[m], rr))
    wf = {f: spearman([a for a, _ in v], [b for _, b in v]) for f, v in fams.items() if len(v) >= 5}
    wf_ok = {f: x for f, x in wf.items() if not math.isnan(x)}
    mean_wf = sum(wf_ok.values()) / len(wf_ok) if wf_ok else float('nan')
    print(f'  {tag:9s} n {len(mem)} solved by r16 {sum(1 for x in r if x <= 16)}: rho {rho:.3f}; within-family mean '
          f'{mean_wf:.3f} over {len(wf_ok)} families (nan for constant groups: {sorted(set(wf) - set(wf_ok))})')
    out['A4'][tag] = dict(rho=rho, within_mean=mean_wf, within=wf)

print('\n== A5: waiting-time null for the knockout ladders (strict training targets, 123 x 32 per round)')
cert = json.load(open(P('review_coe/out_cert.json')))['cert']
obs = {}
for s in range(6):
    pr = json.load(open(P(f'artifacts/coe/rounds/la_ko_s{s}.json')))['per_round']
    first = [int(r) for r in sorted(pr, key=int) if int(r) <= 16 and pr[r]['sigma_targets_cum'] > 0]
    obs[s] = first[0] if first else None
ftr = {f: len(m) for f, m in families_trained().items()}
assert sum(ftr.values()) == 123, ftr


def pbinom_ge(ps, k):
    dist = [1.0]
    for p in ps:
        nd = [0.0] * (len(dist) + 1)
        for i, q in enumerate(dist):
            nd[i] += q * (1 - p); nd[i + 1] += q * p
        dist = nd
    return sum(dist[k:])


variants = {}
for var in ('point105', 'point106', 'trainmix105', 'jeffreys105', 'jeffreys106'):
    ps = []
    for s in range(6):
        c = cert[str(s)]
        n, k = c['n'], c['c']
        if '106' in var:
            n += c['t916'][1]; k += c['t916'][0]
        if var.startswith('point'):
            lam = 32 * 123 * k / n
            p = 1 - math.exp(-16 * lam)
        elif var.startswith('trainmix'):
            rate = sum(ftr[f] / 123 * c['families'][f]['c'] / c['families'][f]['n'] for f in ftr)
            p = 1 - math.exp(-16 * 32 * 123 * rate)
        else:  # Jeffreys: rate ~ Gamma(k + 1/2, n); E[exp(-t r)] = (n / (n + t))^(k + 1/2)
            t = 16 * 32 * 123
            p = 1 - (n / (n + t)) ** (k + 0.5)
        ps.append(p)
    nobs = sum(1 for s in range(6) if obs[s] is not None)
    variants[var] = dict(p=ps, expected=sum(ps), observed=nobs, P_ge_obs=pbinom_ge(ps, nobs))
    print(f'  {var:12s} P(success by r16) per seed {[round(p, 4) for p in ps]}  expected seeds {sum(ps):.3f}  '
          f'observed {nobs}  P(>= {nobs}) = {pbinom_ge(ps, nobs):.4f}')
print(f'  observed first strict-target success rounds: {obs}')
lam1 = 32 * 123 * cert['1']['c'] / cert['1']['n']
print(f'  knockout s1 point lambda {lam1:.4f}/round -> expected first-success round 1/lambda = {1 / lam1:.1f}')
out['A5'] = dict(observed=obs, variants=variants)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_prior.json'), 'w'), indent=1)
