#!/usr/bin/env python3
"""Rank agreement of program length across languages over the calibration items (run kalmar-complexity, Q2).
Items: copy, reverse, parity, sort, addition, eval, taut, Kalmár tt, Kalmár sl (algorithm only).  Python = DEFLATE of
the no-builtins variant where one exists; RASP-L = ops (parity with scratchpad, sort with repeats; Kalmár sl = the
per-step policy's decision; no Kalmár tt).  Spearman rho; -> artifacts/kc/rank_agreement.json"""
import json, os
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p)))
py, blc = J('artifacts/kc/python_sizes.json'), J('kalmar_complexity/programs/blc/results.json')['programs']
rasp = J('kalmar_complexity/programs/rasp/results.json'); rr = {r['task']: r['ops'] for r in rasp['calibration']['rows']}
it = ['copy', 'reverse', 'parity', 'sort', 'addition', 'eval', 'taut', 'Kalmar tt', 'Kalmar sl']
L = {'Python DEFLATE': [py[k]['deflate_bytes'] for k in ['calib copy', 'calib reverse', 'calib parity_nb', 'calib sort_nb',
                         'calib add_nb', 'calib eval', 'calib taut', 'K-tt algorithm', 'K-sl algorithm']],
     'Python raw (builtins)': [py[k]['raw_bytes'] for k in ['calib copy', 'calib reverse', 'calib parity', 'calib sort',
                         'calib add', 'calib eval', 'calib taut', 'K-tt algorithm', 'K-sl algorithm']],
     'BLC': [blc[k]['blc_bits'] for k in ['calib copy', 'calib reverse', 'calib parity', 'calib sort', 'calib add',
             'calib eval', 'calib taut', 'K-tt algorithm', 'K-sl algorithm']],
     'binary CL': [blc[k]['cl_bits'] for k in ['calib copy', 'calib reverse', 'calib parity', 'calib sort', 'calib add',
                   'calib eval', 'calib taut', 'K-tt algorithm', 'K-sl algorithm']],
     'RASP-L': [rr['copy'], rr['reverse'], rr['parity_sp'], rr['sort_rep'], rr['addition'], rr['eval'], rr['taut'], None,
                rasp['decision']['ops']]}
out = {'items': it, 'values': L, 'rho': {}}
names = list(L)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        idx = [j for j in range(len(it)) if L[a][j] is not None and L[b][j] is not None]
        r, p = stats.spearmanr([L[a][j] for j in idx], [L[b][j] for j in idx])
        out['rho'][f'{a} vs {b}'] = {'rho': float(r), 'p': float(p), 'n': len(idx)}
        print(f'{a:22} vs {b:22} rho {r:+.2f} (p {p:.3f}, n {len(idx)})')
for a in names:
    ranks = sorted(range(len(it)), key=lambda j: -(L[a][j] if L[a][j] is not None else -1))
    print(f'{a:22} largest first:', [it[j] for j in ranks if L[a][j] is not None])
json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/rank_agreement.json'), 'w'), indent=1)
