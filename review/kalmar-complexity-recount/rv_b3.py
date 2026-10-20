#!/usr/bin/env python3
"""Reviewer recount of B3 (FOC vs STD) from the stored per-state exact strings, with my own state classes.

  python3 rv_b3.py        # needs out/states_tf1200.json.gz (rv_states.py)

error = 1 - exact (exact: every action token + <eos> is the argmax given the correct prefix).  Classes: opener (my
rv_states.py definition) / other.  Types: builder tags with close:* grouped.  Spearman across the types with >= 500
states of per-type error with per-type mean `explored` (my count), per seed and on the 3-seed mean; permutation p.
"""
import gzip, json, os, sys, collections, glob
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')


def grp(t):
    return 'close' if t.startswith('close:') else t


def perm_p(x, y, n=100000, seed=0):
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    r = np.corrcoef(rx, ry)[0, 1]
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n // 1000):
        P = np.array([rng.permutation(ry) for _ in range(1000)])
        rp = np.array([np.corrcoef(rx, p)[0, 1] for p in P])
        cnt += (np.abs(rp) >= abs(r) - 1e-12).sum()
    return float(r), float(cnt / n)


def main():
    S = json.load(gzip.open(os.path.join(HERE, 'out', 'states_tf1200.json.gz'), 'rt'))
    n = len(S)
    opener = np.array([s['opener'] for s in S], bool)
    groups = np.array([grp(s['tag']) for s in S])
    explored = np.array([s['explored'] for s in S], float)
    types = sorted(t for t in set(groups) if (groups == t).sum() >= 500)
    runs = {}
    for f in sorted(glob.glob(os.path.join(WS, 'artifacts/kc/b3/*.json'))):
        d = json.load(open(f))
        name = os.path.basename(f)[:-5]
        ex = np.array([c == '1' for c in d['per_state_exact']], bool)
        assert len(ex) == n, (name, len(ex), n)
        runs[name] = {'err': ~ex, 'json_read': d['read'], 'train': d['train'], 'args': d['args'], 'secs': d.get('secs'),
                      'gpu': d.get('gpu')}
    out = {'n_states': n, 'n_opener': int(opener.sum()), 'types': types, 'runs': {}}
    for name, r in runs.items():
        e = r['err']
        jr = r['json_read']
        row = {'opener_err': float(e[opener].mean()), 'other_err': float(e[~opener].mean()), 'all_err': float(e.mean()),
               'json_opener_states': jr['class:opener']['states'], 'json_opener_err': jr['class:opener']['error'],
               'json_other_err': jr['class:other']['error'],
               'per_type': {t: float(e[groups == t].mean()) for t in sorted(set(groups))},
               'train_steps': r['train']['steps'], 'max_steps': r['train']['max_steps'], 'best_step': r['train']['best_step'],
               'train_tokens': r['train']['train_tokens'], 'train_secs': r['train']['secs'], 'job_secs': r['secs'],
               'gpu': r['gpu'], 'best_val': r['train']['best_val_nats_per_tok']}
        # per-type vs json
        row['per_type_json_maxdiff'] = max(abs(row['per_type'][t] - jr[f'type:{t}']['error']) for t in row['per_type'])
        out['runs'][name] = row
        print(f"{name}: opener {row['opener_err']:.4f} (json {row['json_opener_err']:.4f}, json n {row['json_opener_states']}) "
              f"other {row['other_err']:.4f} all {row['all_err']:.4f} steps {row['train_steps']}/{row['max_steps']} "
              f"best {row['best_step']} typediff {row['per_type_json_maxdiff']:.2e}")
    seeds = [0, 1, 2]
    summ = {}
    for cls in ('opener_err', 'other_err', 'all_err'):
        std = [out['runs'][f'STD_s{s}'][cls] for s in seeds]
        foc = [out['runs'][f'FOC_s{s}'][cls] for s in seeds]
        summ[cls] = {'STD': std, 'FOC': foc, 'STD_mean': float(np.mean(std)), 'FOC_mean': float(np.mean(foc)),
                     'rel_change_of_means': float(np.mean(foc) / np.mean(std) - 1),
                     'rel_change_per_seed': [float(f / s - 1) for f, s in zip(foc, std)]}
    out['summary'] = summ
    tt = {}
    for t in sorted(set(groups)):
        std = [out['runs'][f'STD_s{s}']['per_type'][t] for s in seeds]
        foc = [out['runs'][f'FOC_s{s}']['per_type'][t] for s in seeds]
        tt[t] = {'states': int((groups == t).sum()), 'openers': int((opener & (groups == t)).sum()),
                 'STD_mean': float(np.mean(std)), 'FOC_mean': float(np.mean(foc)),
                 'rel_change': float(np.mean(foc) / np.mean(std) - 1) if np.mean(std) > 0 else None,
                 'STD': std, 'FOC': foc}
    out['per_type'] = tt
    # Spearman with explored across types
    exm = [float(explored[groups == t].mean()) for t in types]
    sp = {}
    for arm in ('STD', 'FOC'):
        for s in seeds + ['mean']:
            if s == 'mean':
                y = [np.mean([out['runs'][f'{arm}_s{q}']['per_type'][t] for q in seeds]) for t in types]
            else:
                y = [out['runs'][f'{arm}_s{s}']['per_type'][t] for t in types]
            sp[f'{arm}_{s}'] = perm_p(exm, y, n=20000)
    out['spearman_explored'] = sp
    out['explored_per_type'] = dict(zip(types, exm))
    json.dump(out, open(os.path.join(HERE, 'out', 'b3_recount.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))
    for t in types:
        print(f"{t:12} n={tt[t]['states']:6} open={tt[t]['openers']:6} STD {tt[t]['STD_mean']:.4f} FOC {tt[t]['FOC_mean']:.4f} "
              f"rel {tt[t]['rel_change'] if tt[t]['rel_change'] is not None else float('nan'):+.2f} explored {exm[types.index(t)]:.2f}")
    print({k: (round(v[0], 3), round(v[1], 4)) for k, v in sp.items()})


if __name__ == '__main__':
    main()
