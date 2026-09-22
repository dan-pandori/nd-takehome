#!/usr/bin/env python3
"""Relabel the pools in both units: L_true (lines, on file) and ts_minlen = term size of minlen.py's shortest proof (an upper bound
on the minimum term size), obtained by nd2lean.translate + lean_check.  Run on a pod with Lean.

  python3 relabel_size.py            # reads artifacts/lo/minlen_<pool>.jsonl, writes data/lo/<pool>.jsonl + artifacts/lo/relabel_summary.json
Output records = the pool record + {ts_minlen, minlen_lines, minlen_proof, minlen_timeout, minlen_bound}.  A pool record whose
minlen line count differs from its L_true label is reported (label_mismatch) and keeps its L_true.
"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd2lean import translate, TranslationError
from nd_verify import verify_text
import lean_check

POOLS = [('data/ladder/transfer.jsonl', 'artifacts/lo/minlen_la_transfer.jsonl', 'data/lo/la_transfer.jsonl'),
         ('data/ladder/rl_targets.jsonl', 'artifacts/lo/minlen_la_rl_targets.jsonl', 'data/lo/la_rl_targets.jsonl'),
         ('data/p2/targets_depth3.jsonl', 'artifacts/lo/minlen_targets_depth3_b12.jsonl', 'data/lo/targets_depth3.jsonl'),
         ('data/p2/transfer_depth3.jsonl', 'artifacts/lo/minlen_transfer_depth3_b12.jsonl', 'data/lo/transfer_depth3.jsonl')]


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]: j += 1
            for k in range(i, j + 1): r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys); n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float('nan')


def main():
    os.makedirs('data/lo', exist_ok=True)
    summary = {}
    for pool, mlf, out in POOLS:
        recs = [json.loads(l) for l in open(pool)]
        ml = {r['name']: r for r in (json.loads(l) for l in open(mlf))}
        srcs, idx = [], []
        for k, r in enumerate(recs):
            m = ml.get(r['name'])
            if m and m.get('proof'):
                assert verify_text(r['prompt'] + ' ' + m['proof'])[0], (r['name'], m['proof'])
                srcs.append(translate(r['prompt'], m['proof'])); idx.append(k)
        res, wall, cpu = lean_check.check(srcs)
        ts = {k: r for k, r in zip(idx, res)}
        n_lean_rej = sum(1 for r in ts.values() if not r['ok'])
        assert n_lean_rej == 0, f'{pool}: lean_check rejected {n_lean_rej} minlen proofs'
        mism = []; rows = []
        for k, r in enumerate(recs):
            m = ml.get(r['name'], {})
            o = dict(r)
            o['minlen_lines'] = m.get('min_lines_ub'); o['minlen_proof'] = m.get('proof'); o['minlen_timeout'] = m.get('timeout'); o['minlen_bound_rerun'] = m.get('bound')
            o['ts_minlen'] = ts[k]['size'] if k in ts else None
            L = r.get('L_true', r.get('n_lines'))
            if o['minlen_lines'] is not None and o['minlen_lines'] != L:
                mism.append({'name': r['name'], 'L_true': L, 'minlen_rerun': o['minlen_lines']})
            rows.append(o)
        with open(out, 'w') as f:
            for o in rows: f.write(json.dumps(o) + '\n')
        have = [o for o in rows if o['ts_minlen'] is not None]
        byL = collections.defaultdict(list)
        for o in have: byL[o.get('L_true', o.get('n_lines'))].append(o['ts_minlen'])
        s = {'n': len(rows), 'labelled_ts': len(have), 'unlabelled': len(rows) - len(have), 'timeouts': sum(1 for o in rows if o['minlen_timeout']),
             'label_mismatch': mism, 'n_label_mismatch': len(mism),
             'spearman_L_true_ts': spearman([o.get('L_true', o.get('n_lines')) for o in have], [o['ts_minlen'] for o in have]),
             'ts_hist': dict(sorted(collections.Counter(o['ts_minlen'] for o in have).items())),
             'ts_by_L_true': {str(L): {'n': len(v), 'min': min(v), 'median': sorted(v)[len(v) // 2], 'max': max(v)} for L, v in sorted(byL.items())},
             'ts_median': sorted(o['ts_minlen'] for o in have)[len(have) // 2], 'lean_wall_s': wall, 'lean_proc_s': cpu}
        summary[out] = s
        print(out, {k: v for k, v in s.items() if k not in ('label_mismatch', 'ts_by_L_true', 'ts_hist')}, flush=True)
        print('  ts_by_L_true', s['ts_by_L_true'])
    json.dump(summary, open('artifacts/lo/relabel_summary.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
