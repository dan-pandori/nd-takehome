#!/usr/bin/env python3
"""Join per-state measures (q4_states.py) with kalmar-pretrain's teacher-forced verdicts (run kalmar-complexity).

  python3 kalmar_complexity/q4_join.py      # -> artifacts/kc/q4/per_type.json, a table on stdout

Verdicts: `artifacts/kalmar/tf/<model>__tf1200.json` (committed by kalmar-pretrain; rows in tf1200 order, `agree` =
one '1' / '0' per state in the algorithm's order).  The state order of q4_states.py is the same (decompose order), so
the i-th character of record r's string is state (r, i).  Checks: string lengths equal the state counts; the overall
agreement equals the file's stored `agreement['all']`.

Step types: the builder's tags, with every `close:*` grouped as `close` (the review's E1 grouping) -- types with
>= 500 states are analysed.  Per type: states, error = 1 - agreement per model, and the mean of each per-state measure.
"""
import collections, gzip, json, math, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = ['kalD_s0', 'kalD_s1', 'kalD_s2', 'kalDA_s0', 'kalDA_s1', 'kalDA_s2', 'kalC_s0', 'kalC_s1', 'kalC_s2'] + \
    [f'kalD_s{s}_step{t}' for s in range(3) for t in (24020, 100000, 200000, 350000, 500000)]
MEAS = ['depth', 'act_len', 'decl_len', 'state_len', 'n_hyp', 'ref_dist', 'focus_h', 'target_h', 'explored', 'ops']


def group(tag):
    return 'close' if tag.startswith('close:') else tag


def load_tf(m):
    p = os.path.join(ROOT, f'artifacts/kalmar/tf/{m}__tf1200.json')
    if os.path.exists(p):
        return json.load(open(p))
    return json.loads(subprocess.run(['git', '-C', ROOT, 'show', f'HEAD:artifacts/kalmar/tf/{m}__tf1200.json'],
                                     capture_output=True, text=True, check=True).stdout)


def main():
    S = json.load(gzip.open(os.path.join(ROOT, 'artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))
    byrec = collections.defaultdict(list)
    for s in S:
        byrec[s['rec']].append(s)
    agree = {}
    for m in MODELS:
        d = load_tf(m)
        rows = d['rows']
        assert len(rows) == len(byrec), m
        v = []
        for r, row in enumerate(rows):
            a = row['agree']
            assert len(a) == len(byrec[r]), (m, r)
            assert row['name'] == byrec[r][0]['name'], (m, r)
            v += [c == '1' for c in a]
        tot = sum(v) / len(v)
        assert abs(tot - d['agreement']['all']) < 1e-9 if isinstance(d['agreement']['all'], float) else True, (m, tot)
        agree[m] = v
    types = collections.Counter(group(s['tag']) for s in S)
    out = {'n_states': len(S), 'models': MODELS, 'types': {}}
    for t, n in types.items():
        idx = [i for i, s in enumerate(S) if group(s['tag']) == t]
        row = {'states': n}
        for m in MODELS:
            row['err_' + m] = 1 - sum(agree[m][i] for i in idx) / n
        for k in MEAS:
            row['mean_' + k] = sum(S[i][k] for i in idx) / n
        row['mean_log2_ops'] = sum(math.log2(1 + S[i]['ops']) for i in idx) / n
        out['types'][t] = row
    out['overall'] = {m: sum(agree[m]) / len(S) for m in MODELS}
    json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/q4/per_type.json'), 'w'), indent=1)
    print(f"{'type':12} {'states':>7} " + ' '.join(f'{x:>7}' for x in ['errD0', 'errD1', 'errD2', 'errDA0', 'focus_h', 'decl',
                                                                     'explor', 'refd', 'log2op', 'depth']))
    for t, r in sorted(out['types'].items(), key=lambda kv: -kv[1]['err_kalD_s0']):
        print(f"{t:12} {r['states']:7} {r['err_kalD_s0']:7.3f} {r['err_kalD_s1']:7.3f} {r['err_kalD_s2']:7.3f} "
              f"{r['err_kalDA_s0']:7.3f} {r['mean_focus_h']:7.2f} {r['mean_decl_len']:7.1f} {r['mean_explored']:7.1f} "
              f"{r['mean_ref_dist']:7.1f} {r['mean_log2_ops']:7.2f} {r['mean_depth']:7.2f}")
    print('overall agreement', {m: round(v, 4) for m, v in out['overall'].items() if m.count('_') == 1})


if __name__ == '__main__':
    main()
