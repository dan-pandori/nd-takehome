#!/usr/bin/env python3
"""B3 analysis (run kalmar-complexity, pre-registration addendum 2): STD vs FOC, size M, seeds 0-2.

  .venv-tok/bin/python kalmar_complexity/b3_analysis.py   # -> artifacts/kc/b3_summary.json + tables on stdout

Inputs: artifacts/kc/b3/{STD,FOC}_s{0,1,2}.json (`per_state_exact`, tf1200 order) and, recomputed here, each tf1200
state's step tag, class (opener = gets a focus under FOC) and whether it is the first state of its proof.
Two read-outs:
  as pre-registered   every state; error = some action token's argmax is wrong given the correct prefix;
  first states out    the 1,200 first states excluded.  There no name is in scope, so under the trainer's random name
                      shift the first action's name is undetermined by the state (kalmar-pretrain's E1 masks the
                      environment-assigned names, which removes the same artifact).  Same in both arms.
Tests (pre-registered): opener error falls >= 50 % (relative, 3-seed means); other states change < 30 %; ∧ true, ∨ true,
¬⊥, →I-B-true each fall >= 40 %; across-type Spearman of error with in-scope lookups (q4 `explored`, tf1200 means):
STD >= 0.6, FOC <= 0.3.  Falsified if opener error falls < 25 %.
"""
import collections, gzip, json, os, sys
import numpy as np
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
g = lambda t: 'close' if t.startswith('close:') else t
KEY4 = ('leaf:and+', 'leaf:or+', 'leaf:bot-', 'leaf:imp+B')


def main():
    S = json.load(gzip.open(A('artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))       # tags, explored, record index
    R = {f'{a}_s{s}': json.load(open(A(f'artifacts/kc/b3/{a}_s{s}.json'))) for a in ('STD', 'FOC') for s in range(3)}
    # opener flag = FOC model's state got a focus; recompute from the run's per-type/class counts? -> recompute directly
    sys.path.insert(0, A('kalmar_complexity'))
    from b3_focus import focus_of
    from state_env import decompose
    opener, first = [], []
    for line in open(A('data/kalmar/tf1200_kal_sl.jsonl')):
        r = json.loads(line)
        steps, _, _ = decompose(r['prompt'], r['proof'], canon=True)
        for j, (st, act, hs) in enumerate(steps):
            opener.append(focus_of(st) is not None)
            first.append(j == 0)
    assert len(opener) == len(S) == len(R['STD_s0']['per_state_exact'])
    n_open = sum(opener)
    assert n_open == R['STD_s0']['read']['class:opener']['states'], 'opener count differs from the pod read'
    out = {'n_states': len(S), 'n_opener': n_open, 'n_first': sum(first), 'readouts': {}}
    for ro, keep in (('as pre-registered', [True] * len(S)), ('first states out', [not f for f in first])):
        res = collections.defaultdict(dict)
        for run, d in R.items():
            ex = d['per_state_exact']
            acc = collections.defaultdict(lambda: [0, 0])
            for i, s in enumerate(S):
                if not keep[i]:
                    continue
                e = ex[i] == '0'
                for k in ('all', 'class:' + ('opener' if opener[i] else 'other'), 'type:' + g(s['tag'])):
                    acc[k][0] += 1; acc[k][1] += e
            for k, (n, e) in acc.items():
                res[k][run] = e / n
        rows = {}
        for k in sorted(res):
            a = [res[k].get(f'STD_s{s}') for s in range(3)]
            b = [res[k].get(f'FOC_s{s}') for s in range(3)]
            if None in a or None in b:
                continue
            ma, mb = float(np.mean(a)), float(np.mean(b))
            rows[k] = {'STD': a, 'FOC': b, 'STD_mean': ma, 'FOC_mean': mb,
                       'rel_change': (mb - ma) / ma if ma > 0 else None,
                       'paired_diff': [y - x for x, y in zip(a, b)]}
        # across-type Spearman with lookups, types with >= 500 states
        cnt = collections.Counter(g(s['tag']) for i, s in enumerate(S) if keep[i])
        types = [t for t, n in cnt.items() if n >= 500]
        expl = {t: float(np.mean([s['explored'] for i, s in enumerate(S) if keep[i] and g(s['tag']) == t])) for t in types}
        sp = {}
        for arm in ('STD', 'FOC'):
            y = [rows[f'type:{t}'][f'{arm}_mean'] for t in types]
            x = [expl[t] for t in types]
            r = float(stats.spearmanr(x, y)[0])
            rng = np.random.default_rng(0)
            p = float(np.mean([abs(stats.spearmanr(x, rng.permutation(y))[0]) >= abs(r) - 1e-12 for _ in range(5000)]))
            sp[arm] = {'rho': r, 'p': p, 'n_types': len(types)}
        op, ot = rows['class:opener'], rows['class:other']
        verdicts = {
            'opener falls >= 50 %': op['rel_change'] <= -0.5,
            'other changes < 30 %': abs(ot['rel_change']) < 0.3,
            'and+, or+, bot-, imp+B each fall >= 40 %': all(rows[f'type:{t}']['rel_change'] <= -0.4 for t in KEY4),
            'rho STD >= 0.6 and FOC <= 0.3': sp['STD']['rho'] >= 0.6 and sp['FOC']['rho'] <= 0.3,
            'falsified (opener falls < 25 %)': op['rel_change'] > -0.25}
        out['readouts'][ro] = {'rows': rows, 'spearman_lookups': sp, 'verdicts': verdicts}
        print(f'\n== {ro}: opener {100 * op["STD_mean"]:.2f} -> {100 * op["FOC_mean"]:.2f} % ({100 * op["rel_change"]:+.0f} %), '
              f'other {100 * ot["STD_mean"]:.2f} -> {100 * ot["FOC_mean"]:.2f} % ({100 * ot["rel_change"]:+.0f} %); '
              f'rho(lookups) STD {sp["STD"]["rho"]:+.2f} (p {sp["STD"]["p"]:.3f}), FOC {sp["FOC"]["rho"]:+.2f} (p {sp["FOC"]["p"]:.3f})')
        for k, v in verdicts.items():
            print(f'   {k}: {v}')
        for t in KEY4 + ('pr',):
            r = rows[f'type:{t}']
            print(f'   {t:11} STD ' + ' / '.join(f'{100 * x:.2f}' for x in r['STD']) + '  FOC ' +
                  ' / '.join(f'{100 * x:.2f}' for x in r['FOC']) + f'  ({100 * r["rel_change"]:+.0f} %)')
    tr = {run: d['train'] for run, d in R.items()}
    out['train'] = tr
    json.dump(out, open(A('artifacts/kc/b3_summary.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
