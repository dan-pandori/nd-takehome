#!/usr/bin/env python3
"""organism-analysis Q1: one row per (run, seed, start, theorem with a reference proof).

Features from the reference proof's per-step log p (T 1.0, name-base marginalised; trajectory's tj_score) under the
START checkpoint; outcome from the stored x0 / x1 reads at the start and at r8.  Writes data/oa/q1_rows.jsonl.
  starts: c12 pend, c6 pend (trajectory / trajectory-cap6), rfc p1600 / p5000 / p12000 / p16000 (rl-from-ckpt; the
  start checkpoint's score and read are trajectory's p<X>).  Slope: OLS of w1 on log10(step) over the start and the
  two pretraining checkpoints before it.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from oa_load import PT, SEEDS, STARTS, read_both, ref_inputs, score, step_of, targets_meta, nd_lines, rfc_label
from oa_common import step_class


def feats(sc, meta):
    lp = sc['step_lp']
    s = sorted(lp)
    w = s + [0.0, 0.0]
    i = sc['w1_idx']
    return {'w1': w[0], 'w2': w[1], 'w3': w[2], 'n_lt4': sum(v < -4 for v in lp), 'n_lt8': sum(v < -8 for v in lp),
            'total': sc['total'], 'n_actions': len(lp), 'term_size': meta.get('term_size'),
            'w1_class': step_class(meta['actions_b0'][i]), 'w1_idx_frac': i / max(1, len(lp) - 1)}


def slope(run, seed, start, tid):
    k = PT.index(start)
    cks = PT[k - 2:k + 1]
    xs, ys = [], []
    for ck in cks:
        sc = score('c12' if run == 'rfc' else run, seed, ck)
        if sc is None or tid not in sc:
            return None
        xs.append(math.log10(step_of(ck, 'c12' if run == 'rfc' else run, seed))); ys.append(sc[tid]['w1'])
    return float(np.polyfit(xs, ys, 1)[0])


def main():
    refs = ref_inputs()
    rows = []
    for run, starts in (('c12', ['pend']), ('c6', ['pend']), ('rfc', list(STARTS))):
        for seed in SEEDS:
            for start in starts:
                if run == 'rfc':
                    sc0 = score('rfc', seed, 'r0', start); meta = targets_meta('rfc', seed, start)
                    rd = {x: {r: read_both(*rfc_label(seed, start, r), x) for r in (0, 8)} for x in (0, 1)}
                else:
                    sc0 = score(run, seed, 'pend'); meta = targets_meta(run, seed)
                    rd = {x: {0: read_both(run, f's{seed}_pend', x), 8: read_both(run, f's{seed}_r8', x)} for x in (0, 1)}
                miss = [(x, r) for x in rd for r in rd[x] if rd[x][r] is None]
                if miss:
                    print(f'{run} s{seed} {start}: missing reads {miss}'); continue
                for name, ri in refs.items():
                    tid = 'ref:' + name
                    if tid not in sc0 or not meta.get(tid, {}).get('replay_ok'):
                        continue
                    f = feats(sc0[tid], meta[tid])
                    f.update(run=run, seed=seed, start=start, name=name, pool=ri['pool'], nd_lines=nd_lines(ri['proof']),
                             min_lines_ub=ri.get('min_lines_ub'), slope=slope(run, seed, start, tid),
                             cap=6 if run == 'c6' else 12)
                    for x in (0, 1):
                        f[f'ok0_x{x}'] = rd[x][0][name][0]; f[f'ok8_x{x}'] = rd[x][8][name][0]
                    rows.append(f)
    os.makedirs('data/oa', exist_ok=True)
    with open('data/oa/q1_rows.jsonl', 'w') as fo:
        for r in rows:
            fo.write(json.dumps(r) + '\n')
    import collections
    c = collections.Counter((r['run'], r['start'], r['seed'], r['ok0_x0'] == 0, r['ok8_x0'] > 0) for r in rows)
    for k in sorted({k[:3] for k in c}):
        print(k, 'n', sum(v for kk, v in c.items() if kk[:3] == k), 'unsolved@start', sum(v for kk, v in c.items() if kk[:3] == k and kk[3]),
              'of which solved@r8', c[k + (True, True)])


if __name__ == '__main__':
    main()
