#!/usr/bin/env python3
"""cap-horizon: term size (formula nodes over the PRUNED proof) beside every line count.

Proposal 10 asked for this and no run has reported it; ds-composition's reviewer found the
training-set mean term size tracked A4's held-out damage better than the length histogram did.

  term_size('N1 ... QED')                 -> (pruned_lines, term_size) or None if it does not parse
A node is an atom, `F`, a negation or a binary connective -- i.e. the node count of the formula
tree, summed over the kept lines of the dependency-pruned proof.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import parse, prune_lines


def fnodes(f):
    if f[0] in ('atom', 'bot'):
        return 1
    if f[0] == 'not':
        return 1 + fnodes(f[1])
    return 1 + fnodes(f[1]) + fnodes(f[2])


def term_size(proof):
    """-> (n_pruned_lines, term_size) over the dependency-pruned proof, or None if it does not parse."""
    lines = parse(proof)
    if lines is None:
        return None
    kept = prune_lines(lines)
    return len(kept), sum(fnodes(ln['formula']) for ln in kept)


if __name__ == '__main__':
    import json, statistics, collections, argparse
    ap = argparse.ArgumentParser(description='per-length term-size table of a jsonl with a `proof` field')
    ap.add_argument('files', nargs='+')
    ap.add_argument('--field', default='proof')
    a = ap.parse_args()
    for fn in a.files:
        per = collections.defaultdict(list)
        for l in open(fn):
            r = json.loads(l)
            t = term_size(r[a.field])
            if t:
                per[t[0]].append(t[1])
        allv = [v for vs in per.values() for v in vs]
        print(fn, 'n', len(allv), 'mean_term_size', round(statistics.mean(allv), 2) if allv else None)
        for L in sorted(per):
            print(f'  L {L:3d}  n {len(per[L]):7d}  term size mean {statistics.mean(per[L]):7.2f} median {statistics.median(per[L]):6.1f} max {max(per[L]):5d}')
