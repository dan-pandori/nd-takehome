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
for k, v in out.items():
    print(k, v)
json.dump(out, open(os.path.join(ROOT, 'paper/data/stats_extra.json'), 'w'), indent=1, default=float)
