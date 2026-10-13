"""Small statistics the paper quotes that are not in a reviewed file (this run's, recomputed from reviewed counts).
Counts: strict held-out members solved at r16 x0 (review_coe/out_acq.json; R§3).  Run: python3 paper/scripts/stats_extra.py"""
import json, os, math
from scipy.stats import mannwhitneyu, boschloo_exact, beta
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
R = json.load(open(os.path.join(ROOT, 'review_coe/out_acq.json')))['reads']
get = lambda arm, seeds, ck='r16', x='x0': [R[f'{ck}_{arm}_s{s}_{x}']['strict']['solved'] for s in seeds]
full, ko, dose = get('full', range(6)), get('ko', range(6)), get('dose1', range(3))
out = {'full_r16': full, 'ko_r16': ko, 'dose_r16': dose}
out['mw_dose_vs_full_two_sided'] = mannwhitneyu(dose, full, alternative='two-sided', method='exact').pvalue
out['mw_full_vs_ko_one_sided'] = mannwhitneyu(full, ko, alternative='greater', method='exact').pvalue
# Boschloo with the arms as columns (the review's correction): table [[a1, a2], [n1-a1, n2-a2]]
def bos(a1, n1, a2, n2):
    return boschloo_exact([[a1, a2], [n1 - a1, n2 - a2]], alternative='greater').pvalue
out['boschloo_primary_6of6_vs_0of6'] = bos(6, 6, 0, 6)
out['boschloo_rl_only_5of6_vs_0of6'] = bos(5, 6, 0, 6)
out['boschloo_dose_3of3_vs_ko_0of6'] = bos(3, 3, 0, 6)
out['boschloo_3of6_vs_0of6'] = bos(3, 6, 0, 6)
out['boschloo_1of6_vs_0of6'] = bos(1, 6, 0, 6)
# robustness: full arm restricted to the new seeds s3-s5 (same GPU class and batch as the knockout ladders)
acq16 = lambda arm, s: len(R[f'r16_{arm}_s{s}_x0']['strict']['acquired']) > 0
acq0 = lambda arm, s: set(R[f'pend_{arm}_s{s}_x0']['strict']['acquired'])
during = lambda arm, s: len(set(R[f'r16_{arm}_s{s}_x0']['strict']['acquired']) - acq0(arm, s)) > 0
n_new = sum(acq16('full', s) for s in (3, 4, 5)); n_new_rl = sum(during('full', s) for s in (3, 4, 5))
out['new_full_only'] = {'indicator': f'{n_new}/3 vs 0/6', 'p': bos(n_new, 3, 0, 6),
                        'during_rl': f'{n_new_rl}/3 vs 0/6', 'p_during_rl': bos(n_new_rl, 3, 0, 6)}
out['during_rl_all_full'] = [during('full', s) for s in range(6)]
# one-sided 95 % upper bound on the per-seed creation rate after 0 / 6
out['cp_ub95_0of6'] = beta.ppf(0.95, 1, 6)
# expected free-sigma proofs per round on the strict trained targets at the knockout bases' pooled large-k rates
att = 123 * 32
rates = {'s0': 0 / 1491420, 's1': 6 / 1120378, 's2': 1 / 1338328, 's3': 0 / 1340640, 's4': 3 / 1360222, 's5': 2 / 1419656}
out['attempts_per_round_on_strict_targets'] = att
out['expected_sigma_proofs_per_round_at_base_rate'] = {k: att * v for k, v in rates.items()}

# ---- round-1 critique additions (all from reviewed counts) ----
# RL-specific contrast: strict members gained during RL (r16 - pend, x0)
gain = lambda arm, seeds: [R[f'r16_{arm}_s{s}_x0']['strict']['solved'] - R[f'pend_{arm}_s{s}_x0']['strict']['solved'] for s in seeds]
gf, gk, gd = gain('full', range(6)), gain('ko', range(6)), gain('dose1', range(3))
out['gain_full'], out['gain_ko'], out['gain_dose'] = gf, gk, gd
out['mw_gain_full_vs_ko_one_sided'] = mannwhitneyu(gf, gk, alternative='greater', method='exact').pvalue
# the pre-registered indicator applied to the bases (pend), plain x0 and guided g0
ind = lambda arm, ck, x: sum(len(R[f'{ck}_{arm}_s{s}_{x}']['strict']['acquired']) > 0 for s in SEEDS[arm])
SEEDS = {'full': range(6), 'ko': range(6), 'dose1': range(3)}
out['pend_indicator_x0'] = (ind('full', 'pend', 'x0'), ind('ko', 'pend', 'x0'), bos(ind('full', 'pend', 'x0'), 6, ind('ko', 'pend', 'x0'), 6))
out['pend_indicator_g0'] = (ind('full', 'pend', 'g0'), ind('ko', 'pend', 'g0'), bos(ind('full', 'pend', 'g0'), 6, ind('ko', 'pend', 'g0'), 6))
pend_full = [R[f'pend_full_s{s}_x0']['strict']['solved'] for s in range(6)]
pend_ko = [R[f'pend_ko_s{s}_x0']['strict']['solved'] for s in range(6)]
out['mw_pend_full_vs_ko'] = mannwhitneyu(pend_full, pend_ko, alternative='greater', method='exact').pvalue
# Delta_cov (standard A, K_train(16)): full s3-s5 vs knockout s0-s5 (L94 / R7)
dfull, dko = [37, 36, 32], [29, 31, 35, 37, 26, 21]
out['dcov_means'] = (sum(dfull) / 3, sum(dko) / 6)
out['mw_dcov_full_vs_ko_one_sided'] = mannwhitneyu(dfull, dko, alternative='greater', method='exact').pvalue
# certificates: the 105 family members (as computed) and the pre-registered 106 (adding la_transfer_916); K_max = 0.05/UB95
CERT = {0: (23322, 0, 1491420, (0, 13180)), 1: (17189, 6, 1120378, (1, 2048)), 2: (20907, 1, 1338328, (0, 11815)),
        3: (20782, 0, 1340640, (1, 2048)), 4: (21554, 3, 1360222, (0, 12181)), 5: (22297, 2, 1419656, (0, 12600))}
ub = lambda c, n: beta.ppf(0.95, c + 1, n - c)
cert = {}
for s_, (K, c, n, (c9, n9)) in CERT.items():
    u105, u106 = ub(c, n), ub(c + c9, n + n9)
    cert[f'ko_s{s_}'] = {'K_train16': K, 'ub105': u105, 'certified105': u105 < 0.05 / K, 'Kmax105': 0.05 / u105,
                         'ub106': u106, 'certified106': u106 < 0.05 / K, 'Kmax106': 0.05 / u106,
                         'K_if_Neval_106': K * 322 / 106, 'K_if_Neval_1054': K * 322 / 1054}
out['certificates'] = cert
out['certified_105'] = sum(v['certified105'] for v in cert.values())
out['certified_106'] = sum(v['certified106'] for v in cert.values())

# test-time compute fractions (mcts-a summary, reviewed counts) and replay-only share of RL's gain (L43)
mc = json.load(open(os.path.join(ROOT, 'paper/data/mcts_a_summary.json')))['tables']
frac = {}
for pool in ('h250', 'tb72', 'rrQ100'):
    vs = [mc[f'pend/{pool}'][f'value/s{s}'] - mc[f'pend/{pool}'][f'sample/s{s}'] for s in range(3)]
    rl = [mc[f'r8/{pool}'][f'sample/s{s}'] - mc[f'pend/{pool}'][f'sample/s{s}'] for s in range(3)]
    frac[pool] = {'search_gain': vs, 'rl_gain_by_sampling': rl, 'fraction': (sum(vs) / 3) / (sum(rl) / 3)}
out['ttc_search_fraction'] = frac
rep, pend, r8 = [239, 244, 249], [232, 236, 234], [286, 286, 293]
out['replay_share_of_rl_gain'] = [(a - b) / (c - b) for a, b, c in zip(rep, pend, r8)]
# GRPO advantage of a single success among 32 binary rewards
m = 1 / 32; sd = math.sqrt(m * (1 - m)); out['grpo_lone_success_advantage'] = (1 - m) / sd

for k, v in out.items():
    print(k, v)
json.dump(out, open(os.path.join(ROOT, 'paper/data/stats_extra.json'), 'w'), indent=1, default=float)
