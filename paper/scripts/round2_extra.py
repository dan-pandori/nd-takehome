"""Round-2 sensitivity analyses and descriptives (prereg Addendum 5; post hoc, from reviewed files).

Outputs paper/data/round2_extra.json and a printed summary:
  - per arm and seed: strict held-out (106) proved at r0 and r16 in x0, x1 and guided evaluations; RL-phase gains in the
    guided evaluations; exact one-sided Mann-Whitney tests; the hardware-matched (full s3-s5) gains test
    (review_coe/out_acq.json = the create-or-elicit review's recount);
  - per-family pooled base rates of the knockout bases at large k (review_coe/out_cert.json), plus la_transfer_916;
  - sigma / sigma+ records in the knockout fine-tune mixes, per round and over rounds 1-16 (review_coe/out_mixcheck.json);
  - A5b: the waiting-time null under the 106 pool, family weighting and a Jeffreys posterior-predictive.
"""
import itertools, json, math, os, random
from scipy.stats import mannwhitneyu, beta, gamma

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = lambda p: json.load(open(os.path.join(ROOT, p)))
R = J('review_coe/out_acq.json')['reads']
SEEDS = {'full': range(6), 'ko': range(6), 'dose1': range(3)}
out = {}

# --- evaluations at r0 and r16, all reads available
tab = {}
for arm, seeds in SEEDS.items():
    for s in seeds:
        row = {}
        for ck in ('pend', 'r16'):
            for x in ('x0', 'x1', 'g0'):
                k = f'{ck}_{arm}_s{s}_{x}'
                if k in R:
                    row[f'{ck}_{x}'] = R[k]['strict']['solved']
                    row[f'{ck}_{x}_acq'] = R[k]['strict']['acquired']
        tab[f'{arm}_s{s}'] = row
out['reads'] = tab
gain = lambda arm, x: [tab[f'{arm}_s{s}'][f'r16_{x}'] - tab[f'{arm}_s{s}'][f'pend_{x}'] for s in SEEDS[arm] if f'r16_{x}' in tab[f'{arm}_s{s}']]
out['gain_guided_full'], out['gain_guided_ko'] = gain('full', 'g0'), gain('ko', 'g0')
out['mw_gain_guided'] = mannwhitneyu(out['gain_guided_full'], out['gain_guided_ko'], alternative='greater', method='exact').pvalue
gx_full_new = [tab[f'full_s{s}']['r16_x0'] - tab[f'full_s{s}']['pend_x0'] for s in (3, 4, 5)]
gx_ko = gain('ko', 'x0')
out['gain_x0_full_new'], out['gain_x0_ko'] = gx_full_new, gx_ko
out['mw_gain_x0_full_new_vs_ko'] = mannwhitneyu(gx_full_new, gx_ko, alternative='greater', method='exact').pvalue
out['ko_pend_guided'] = [tab[f'ko_s{s}']['pend_g0'] for s in range(6)]
out['ko_pend_x1'] = [tab[f'ko_s{s}']['pend_x1'] for s in range(6)]

# --- per-family pooled base rates (knockout bases, large k)
C = J('review_coe/out_cert.json')['cert']
fam = {}
for s, v in C.items():
    for f, x in v['families'].items():
        a = fam.setdefault(f, {'n': 0, 'c': 0, 'per_seed_c': []})
        a['n'] += x['n']; a['c'] += x['c']; a['per_seed_c'].append(x['c'])
for f, a in fam.items():
    a['p_hat'] = a['c'] / a['n']
    a['ub95'] = beta.ppf(0.95, a['c'] + 1, a['n'] - a['c'])
t916 = [C[s]['t916'] for s in sorted(C)]
fam['la_transfer_916'] = {'n': sum(t[1] for t in t916), 'c': sum(t[0] for t in t916), 'per_seed_c': [t[0] for t in t916]}
out['family_base_rates'] = fam
noncc = [f for f in fam if f not in ('contraposition_conv', 'la_transfer_916')]
out['non_cc_family_total'] = {'n': sum(fam[f]['n'] for f in noncc), 'c': sum(fam[f]['c'] for f in noncc)}

# --- sigma records in the knockout mixes
M = J('review_coe/out_mixcheck.json')
mix = {}
for s in range(6):
    pr = M[f'ko_s{s}']['per_round']
    sig = [pr[str(r)].get('sigma:rl', 0) for r in range(1, 17)]
    sigp = [pr[str(r)].get('sigma_plus:rl', 0) for r in range(1, 17)]
    mix[f'ko_s{s}'] = {'sigma_r1_16': sum(sig), 'sigma_plus_r1_16': sum(sigp), 'sigma_per_round_min_max': (min(sig), max(sig))}
out['ko_mix_sigma'] = mix

# --- A5b: waiting-time null variants
cert105 = {s: (C[str(s)]['c'], C[str(s)]['n']) for s in range(6)}
cert106 = {s: (C[str(s)]['c'] + C[str(s)]['t916'][0], C[str(s)]['n'] + C[str(s)]['t916'][1]) for s in range(6)}
obs = 3; K_ATT, N = 32, 123
w_cc = (27 / 123) / (18 / 105)          # converse contraposition is 22 % of strict training targets vs 17 % of held-out


def tail(ps, k):
    t = 0.0
    for m in range(k, len(ps) + 1):
        for comb in itertools.combinations(range(len(ps)), m):
            term = 1.0
            for i in range(len(ps)):
                term *= ps[i] if i in comb else (1 - ps[i])
            t += term
    return t


def plug(cert, weight=1.0):
    ps = [1 - math.exp(-16 * K_ATT * N * weight * c / n) for c, n in cert.values()]
    return sum(ps), tail(ps, obs)


def jeffreys(cert, draws=20000, seed=0):
    rng = random.Random(seed); hits = 0; exp_sum = 0.0
    for _ in range(draws):
        ps = []
        for c, n in cert.values():
            lam = rng.gammavariate(c + 0.5, 1.0 / n)          # Gamma(c + 1/2, rate n)
            ps.append(1 - math.exp(-16 * K_ATT * N * lam))
        exp_sum += sum(ps)
        hits += sum(1 for p in ps if rng.random() < p) >= obs
    return exp_sum / draws, hits / draws


cc_share_105 = {s: None for s in range(6)}
out['A5b'] = {
    'plug_105': plug(cert105), 'plug_106': plug(cert106),
    'plug_105_family_weighted': plug(cert105, w_cc),
    'jeffreys_105': jeffreys(cert105), 'jeffreys_106': jeffreys(cert106),
    'family_weight_cc': w_cc,
}
for k, v in out.items():
    print(k, v)
json.dump(out, open(os.path.join(ROOT, 'paper/data/round2_extra.json'), 'w'), indent=1, default=str)
