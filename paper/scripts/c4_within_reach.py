"""C4 (Addendum 4): knockout s1's base on its 18 strict converse-contraposition held-out members and la_transfer_916, and
knockout s3's base on la_transfer_916, 18,432 plain attempts each (T 0.8, no early stopping, seed0 9500).
Per member: successes c in n, exact two-sided 95 % Clopper-Pearson interval, and the classification the round-2 soundness
critique proposed: within reach at K if the lower bound >= 1/K, not reached if the upper bound < 1/K, undetermined
otherwise (K = K_train(16): 17,189 for s1, 20,782 for s3). Also the pre-registered rule (c >= 2 at n = 18,432 => p_hat >= 1/K).
Input: artifacts/coe_paper/c4/ko_s{1,3}.json (coe/coe_bigk.py output). Output: paper/data/c4_within_reach.json."""
import json, os
from scipy.stats import beta
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
K = {1: 17189, 3: 20782}
BASE = {1: {'la_transfer_528': (1, 10240), 'la_transfer_1246': (1, 7168), 'la_transfer_1460': (3, 9216),
            'la_transfer_2256': (1, 9216), 'la_transfer_916': (1, 2048)}, 3: {'la_transfer_916': (1, 2048)}}  # review_coe/cert.log
LADDER = {'la_transfer_1019', 'la_transfer_1246', 'la_transfer_1460', 'la_transfer_2256', 'la_transfer_916'}  # s1 r20/r24 set
out = {}
for s in (1, 3):
    p = os.path.join(ROOT, f'artifacts/coe_paper/c4/ko_s{s}.json')
    if not os.path.exists(p):
        print(f'ko_s{s}: pending'); continue
    d = json.load(open(p))
    rows = {}
    for name, t in d['theorems'].items():
        c, n = t['ok'], t['tried']
        lo = beta.ppf(0.025, c, n - c + 1) if c > 0 else 0.0
        hi = beta.ppf(0.975, c + 1, n - c)
        cls = 'within reach' if lo >= 1 / K[s] else ('not reached' if hi < 1 / K[s] else 'undetermined')
        rows[name] = {'c': c, 'n': n, 'p_hat': c / n, 'ci95': [lo, hi], 'class': cls, 'prereg_within': c >= 2, 'p_hat_ge_1_over_K': c / n >= 1 / K[s],
                      'base_largek_before': BASE[s].get(name), 'ladder_s1_solves_r20_r24': name in LADDER}
    out[f'ko_s{s}'] = {'K': K[s], 'attempts': d.get('attempts'), 'wall_s': d.get('wall_s'), 'members': rows,
                       'total_successes': sum(r['c'] for r in rows.values())}
    print(f'ko_s{s}: K {K[s]}, attempts {d.get("attempts")}, total successes {out[f"ko_s{s}"]["total_successes"]}')
    for name, r in sorted(rows.items(), key=lambda kv: -kv[1]['c']):
        if r['c'] or name in LADDER or r['base_largek_before']:
            print(f'   {name:18s} {r["c"]:3d}/{r["n"]}  p {r["p_hat"]:.2e}  CI [{r["ci95"][0]:.1e}, {r["ci95"][1]:.1e}]  {r["class"]:12s}'
                  f'  prereg(c>=2) {r["prereg_within"]}  base-before {r["base_largek_before"]}  ladder {r["ladder_s1_solves_r20_r24"]}')
json.dump(out, open(os.path.join(ROOT, 'paper/data/c4_within_reach.json'), 'w'), indent=1)
