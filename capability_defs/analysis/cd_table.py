#!/usr/bin/env python3
"""capability-defs Part 3: the per-theorem master table for cap 12 (and cap 6), from existing files only.

  python3 capability_defs/analysis/cd_table.py   -> capability_defs/analysis/out/table_c12.json, table_c6.json

For each seed s and theorem t (tb72 + h250, 322):
  counts[ck][x] = [n_ok, n_tried] for every read: trajectory checkpoints (x0, x1), r12 / r16 (x1), mcts-a pend / r8
                  (x2 pool read; x4 C-only read; r8 x10 at k 2,560)
  tf[kind][ck]  = teacher-forced summaries (T1.0 and T0.8: total, w1, mean) of the reference ('ref') and r8 eventual
                  ('ev') proofs at every scored checkpoint (trajectory's tj_score; p0 = init), where they exist
  meta          = pool, length label, LEM flag, reference term size / steps
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R
from cd_pod_inputs import is_lem

HOME = os.path.expanduser('~')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
SCORE = {12: f'{HOME}/work/trajectory/artifacts/tj/score/s{{s}}', 6: f'{HOME}/work/trajectory-cap6/artifacts/tj6/score/s{{s}}'}


def rows(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    names = R.all_names(); pool = R.pool_of(); pr = R.prompts()
    lens = {}
    for r in rows(f'{HOME}/work/trajectory/data/bs/textbook72.jsonl'):
        lens[r['name']] = r.get('reference_lines')
    for r in rows(f'{HOME}/work/trajectory/data/bs/holdout250.jsonl'):
        lens[r['name']] = r.get('n_lines')
    for cap in (12, 6):
        T = {'cap': cap, 'names': names, 'meta': {}, 'seeds': {}}
        for n in names:
            T['meta'][n] = {'pool': pool[n], 'len': lens.get(n), 'lem': is_lem(pr[n]), 'prompt': pr[n]}
        for s in R.SEEDS:
            S = {n: {'counts': {}, 'tf': {'ref': {}, 'ev': {}}} for n in names}
            cks = R.CKS + (['r12', 'r16'] if cap == 12 else ['r16'])
            for ck in cks:
                for x in (0, 1):
                    for pl in R.POOLS:
                        d = R.read(cap, s, ck, pl, x)
                        for n, v in (d or {}).items():
                            S[n]['counts'].setdefault(ck, {})[str(x)] = list(v[:2])
            if cap == 12:
                for ck in ('pend', 'r8'):
                    for pl, x in (('tb72', 2), ('h250', 2), ('C', 4)):
                        for n, v in (R.read(12, s, ck, pl, x) or {}).items():
                            if n in S:
                                S[n]['counts'].setdefault(ck, {})[str(x)] = list(v[:2])
                for n, v in (R.read(12, s, 'r8', 'C', 10) or {}).items():
                    if n in S:
                        S[n]['counts'].setdefault('r8', {})['10'] = list(v[:2])
            sd = SCORE[cap].format(s=s)
            meta = {m['tid']: m for m in rows(f'{sd}/targets.jsonl')}
            for tid, m in meta.items():
                kind, nm = tid.split(':', 1)
                kind = 'ev' if kind.startswith('ev') else kind
                if nm in S and kind in ('ref', 'ev'):
                    S[nm]['tf'][kind]['_meta'] = {'n_steps': m.get('n_steps'), 'term_size': m.get('term_size'),
                                                 'replay_ok': m.get('replay_ok')}
            for ck in R.CKS:
                f = f'{sd}/s{s}_{ck}.jsonl'
                if not os.path.exists(f):
                    continue
                for r in rows(f):
                    kind, nm = r['tid'].split(':', 1)
                    kind = 'ev' if kind.startswith('ev') else kind
                    if nm in S and kind in ('ref', 'ev'):
                        S[nm]['tf'][kind][ck] = {T_: {k: r[T_][k] for k in ('total', 'w1', 'mean')} for T_ in ('T1.0', 'T0.8')}
            T['seeds'][str(s)] = S
        json.dump(T, open(f'{OUT}/table_c{cap}.json', 'w'))
        n_ev = sum(1 for s in T['seeds'].values() for v in s.values() if v['tf']['ev'])
        print(f'cap {cap}: table written; theorem-seed pairs with an eventual proof scored: {n_ev}')


if __name__ == '__main__':
    main()
