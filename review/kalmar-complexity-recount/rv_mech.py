#!/usr/bin/env python3
"""Mechanical minification sizes (python-minifier, the executor's settings) + rank agreement across languages from my
own counts.  ~/review/kalmar-complexity/.venv-tok/bin/python rv_mech.py"""
import json, os, sys, zlib, lzma
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
import python_minifier
from scipy import stats


def defl(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return len(c.compress(b) + c.flush())


MECH = {'builder kalmar/kalmar.py': ['kalmar/kalmar.py'], 'tt_prover.py': ['kalmar_complexity/ref/tt_prover.py'],
        'K12 generator gen.py': ['gen.py'], 'policy.py': ['kalmar_complexity/programs/policy/policy.py'],
        'dtree features (features.py + policy.py)': ['kalmar_complexity/programs/dtree/features.py',
                                                     'kalmar_complexity/programs/policy/policy.py']}
out = {'python_minifier_version': python_minifier.__version__ if hasattr(python_minifier, '__version__') else '?', 'mech': {}}
for k, fs in MECH.items():
    src = ''.join(python_minifier.minify(open(os.path.join(WS, f)).read(), remove_literal_statements=True,
                                         rename_globals=False, rename_locals=True) + '\n' for f in fs)
    b = src.encode()
    out['mech'][k] = {'raw': len(b), 'deflate': defl(b)}
    print(k, out['mech'][k])
py = json.load(open(os.path.join(HERE, 'out', 'python_sizes.json')))
bl = json.load(open(os.path.join(HERE, 'out', 'calib_blc.json')))
bk = json.load(open(os.path.join(HERE, 'out', 'blc_recheck.json')))
ra = json.load(open(os.path.join(HERE, 'out', 'calib_rasp.json')))
rm = json.load(open(os.path.join(HERE, 'out', 'rasp_metrics.json')))
items = ['copy', 'reverse', 'parity', 'sort', 'addition', 'eval', 'taut', 'Kalmar tt', 'Kalmar sl']
L = {'Python DEFLATE (no-builtins variants)': [py['calib copy']['deflate'], py['calib reverse']['deflate'],
        py['calib parity_nb']['deflate'], py['calib sort_nb']['deflate'], py['calib add_nb']['deflate'],
        py['calib eval']['deflate'], py['calib taut']['deflate'], py['K-tt algorithm']['deflate'], py['K-sl algorithm']['deflate']],
     'Python raw (builtins)': [py['calib copy']['raw'], py['calib reverse']['raw'], py['calib parity']['raw'],
        py['calib sort']['raw'], py['calib add']['raw'], py['calib eval']['raw'], py['calib taut']['raw'],
        py['K-tt algorithm']['raw'], py['K-sl algorithm']['raw']],
     'BLC': [bl[k]['bits'] for k in ['copy', 'reverse', 'parity', 'sort', 'add', 'eval', 'taut']] + [bk['bits']['ktt'], bk['bits']['ksl']],
     'binary CL': [bl[k]['cl_bits'] for k in ['copy', 'reverse', 'parity', 'sort', 'add', 'eval', 'taut']] + [bk['cl_bits']['ktt'], bk['cl_bits']['ksl']],
     'RASP-L ops (incl. selects)': [ra['copy_prog']['ops_incl_selects'], ra['reverse_prog']['ops_incl_selects'],
        ra['parity_sp_prog']['ops_incl_selects'], ra['sort_rep_prog']['ops_incl_selects'], ra['addition_prog']['ops_incl_selects'],
        ra['eval_prog']['ops_incl_selects'], ra['taut_prog']['ops_incl_selects'], None,
        rm['decision outputs']['ops_excl_inputs_consts']]}
out['rank_values'] = {'items': items, **L}
out['rho'] = {}
names = list(L)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        idx = [j for j in range(len(items)) if L[a][j] is not None and L[b][j] is not None]
        r, p = stats.spearmanr([L[a][j] for j in idx], [L[b][j] for j in idx])
        r7, p7 = stats.spearmanr([L[a][j] for j in idx if j < 7], [L[b][j] for j in idx if j < 7])
        out['rho'][f'{a} vs {b}'] = {'rho_with_kalmar': float(r), 'n': len(idx), 'rho_calib_only': float(r7)}
        print(f'{a:38} vs {b:28} rho {r:+.2f} (n {len(idx)}); calibration items only {r7:+.2f}')
for a in names:
    order = sorted([j for j in range(len(items)) if L[a][j] is not None], key=lambda j: -L[a][j])
    out.setdefault('order', {})[a] = [items[j] for j in order]
    vals = [L[a][j] for j in order]
    print(f'{a:38} largest first:', [f'{items[j]}={L[a][j]}' for j in order])
json.dump(out, open(os.path.join(HERE, 'out', 'mech_rank.json'), 'w'), indent=1)
