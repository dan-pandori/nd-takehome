#!/usr/bin/env python3
"""mcts_termsize.py -- proof length of the found proofs, in lines and in Lean term size (run `mcts-a`; needs Lean).

For every read-out in artifacts/mcts/eval (sample / prior / value) and every solved theorem: the shortest accepted proof
(sampling: shortest of its distinct accepted proofs; search: the one proof the tree found) -> ND line count and the
elaborated term size from `lean_check.check`.  Output: artifacts/mcts/termsize.json
  {read-out: {theorem name: [lines, term size or null]}}
Line counts are ND lines; the pools' L_true labels are ND-derived upper bounds under Lean.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nd2lean
from lean_check import check


def lines(nd):
    return nd.count(';')


def main():
    items, keys = [], []
    for fn in sorted(glob.glob('artifacts/mcts/eval/s*__*.jsonl')):
        tag = os.path.basename(fn)[:-6]
        if 'tune200' in tag:
            continue
        for r in map(json.loads, open(fn)):
            if not r['solved']:
                continue
            if tag.endswith('__sample'):
                nd = min(r['proofs'], key=lines)
            else:
                nd = r['proof']
            try:
                items.append(nd2lean.translate(r['prompt'], nd, require_all_pr=False))
                keys.append((tag, r['name'], lines(nd)))
            except Exception as e:
                keys.append((tag, r['name'], lines(nd))); items.append(None)
    srcs = [s for s in items if s is not None]
    res, wall, proc = check(srcs, workers=int(os.environ.get('LEAN_GATE_WORKERS', 16)))
    it = iter(res)
    out = {}
    bad = 0
    for (tag, name, nl), s in zip(keys, items):
        sz = None
        if s is not None:
            r = next(it)
            if r['ok']:
                sz = r['size']
            else:
                bad += 1
        out.setdefault(tag, {})[name] = [nl, sz]
    json.dump(dict(per=out, rejected_by_lean_check=bad, n=len(keys), wall_s=wall), open('artifacts/mcts/termsize.json', 'w'))
    print('termsize', len(keys), 'rejected', bad, 'wall', wall)


if __name__ == '__main__':
    main()
