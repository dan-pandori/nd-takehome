#!/usr/bin/env python3
"""Q4 extension: which per-step-type measure predicts which error class? (run kalmar-complexity)
kalmar-pretrain's classes of KAL-D s2's teacher-forced disagreements on tf1200 (artifacts/kalmar/error_classes_kalD_s2.json,
from kalmar/error_classes.py; only s2 was classified).  Per step type (close:* grouped, >= 500 states): rate of a class =
its count / the type's states.  Spearman rho (permutation p) with the demand measures.  -> artifacts/kc/q4/error_classes.json"""
import collections, json, os, subprocess
import numpy as np
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = lambda t: 'close' if t.startswith('close:') else t
E = json.loads(subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:artifacts/kalmar/error_classes_kalD_s2.json'],
                              capture_output=True, text=True, check=True).stdout)
R = json.load(open(os.path.join(ROOT, 'artifacts/kc/q4/q4_results.json')))
PT = json.load(open(os.path.join(ROOT, 'artifacts/kc/q4/per_type.json')))['types']
types = R['types']
cnt = collections.defaultdict(collections.Counter)
for t, d in E['by_tag'].items():
    for c, n in d.items():
        cnt[g(t)][c] += n
out = {'classes_total': E['classes'], 'n_errors': E['n'], 'rho': {}}
rng = np.random.default_rng(0)
for cl in ('other-subformula', 'corrupted', 'close-timing', 'malformed', 'same-formula'):
    y = [cnt[t][cl] / PT[t]['states'] for t in types]
    for k in ('rasp_eff_depth', 'explored', 'log2_ops', 'decl_len', 'act_len', 'focus_h', 'py_bytes', 'log_freq'):
        x = [R['predictors'][t][k] for t in types]
        r = stats.spearmanr(x, y)[0]
        perm = [stats.spearmanr(x, rng.permutation(y))[0] for _ in range(20000)]
        p = float(np.mean(np.abs(perm) >= abs(r) - 1e-12))
        out['rho'][f'{cl} ~ {k}'] = {'rho': float(r), 'p': p}
    best = sorted(((k.split(' ~ ')[1], v) for k, v in out['rho'].items() if k.startswith(cl + ' ~')), key=lambda kv: -abs(kv[1]['rho']))
    print(f"{cl:17} ({E['classes'].get(cl, 0):5} errors): " + ', '.join(f"{k} {v['rho']:+.2f} (p {v['p']:.3f})" for k, v in best[:4]))
json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/q4/error_classes.json'), 'w'), indent=1)
