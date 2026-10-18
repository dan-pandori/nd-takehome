#!/usr/bin/env python3
"""Compare the blind spot-check labels (data/ps/validation/spot_<g>.labels.jsonl, written by independent checkers from
TAXONOMY.md alone) with the classifier's labels for the same proofs, recomputed with the current code.

  python3 proof_strategies/spot_compare.py [--groups a b c] [--show]
"""
import argparse, collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from strategies import analyse                     # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--groups', nargs='+', default=['a', 'b', 'c'])
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--out', default='artifacts/ps/validation/spot_compare.json')
    ap.add_argument('--key', action='store_true', help='compare with the key (labels at sampling time, taxonomy v1.1)')
    a = ap.parse_args()
    key = {r['id']: r for r in map(json.loads, open('artifacts/ps/validation/spot_key.jsonl'))}
    res = collections.defaultdict(lambda: collections.Counter())
    dis = []
    for g in a.groups:
        fn = f'data/ps/validation/spot_{g}.labels.jsonl'
        if not os.path.exists(fn):
            print('missing', fn)
            continue
        items = {r['id']: r for r in map(json.loads, open(f'data/ps/validation/spot_{g}.jsonl'))}
        for lab in map(json.loads, open(fn)):
            it, k = items[lab['id']], key[lab['id']]
            proof = ' ; '.join(it['proof_lines']) + ' ; QED'
            t = it['target']
            if a.key:          # the labels the classifier gave when the sample was drawn (the version the checkers read)
                mine = {'u': [t] if k['uses_target'] else [], 'pri': k['primary']}
            else:              # recomputed with the current code
                mine = analyse(proof, it['prompt'], written=False)
            u_ok = bool(lab['uses_target']) == (t in mine['u'])
            p_ok = lab['primary'] == mine['pri']
            res[t]['n'] += 1; res[t]['uses_agree'] += u_ok; res[t]['primary_agree'] += p_ok
            res[t][k['role']] += 1
            if not u_ok or not p_ok:
                dis.append({'id': lab['id'], 'target': t, 'role': k['role'], 'checker_uses': lab['uses_target'], 'ours_uses': t in mine['u'],
                            'checker_primary': lab['primary'], 'ours_primary': mine['pri'], 'comment': lab.get('comment', '')[:300],
                            'detail': lab.get('detail', '')[:300]})
    tot = collections.Counter()
    print(f"{'target':14s} {'n':>4s} {'uses agree':>11s} {'primary agree':>14s}")
    for t, c in sorted(res.items()):
        print(f"{t:14s} {c['n']:4d} {c['uses_agree']:6d}/{c['n']:<4d} {c['primary_agree']:8d}/{c['n']:<4d}")
        tot.update({'n': c['n'], 'uses': c['uses_agree'], 'pri': c['primary_agree']})
    print(f"{'all':14s} {tot['n']:4d} {tot['uses']:6d}/{tot['n']:<4d} {tot['pri']:8d}/{tot['n']:<4d}")
    if a.show:
        for d in dis:
            print(json.dumps(d, ensure_ascii=False))
    json.dump({'per_target': {t: dict(c) for t, c in res.items()}, 'total': dict(tot), 'disagreements': dis}, open(a.out, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
