#!/usr/bin/env python3
"""Smallest exact decision tree found over the state features (run kalmar-complexity).

  python3 kalmar_complexity/programs/dtree/fit_tree.py artifacts/kc/dtree/rows_1000.json artifacts/kc/dtree/tree.json

Tests are binary, `feature == value`.  The search is a memoised recursion over row sets that, at every node, tries the
`--beam` best tests by information gain over the distinct feature vectors and keeps the subtree with the fewest
leaves (beam 1 = greedy ID3).  Exact = every distinct (vector, template) row is classified correctly.  Not guaranteed
minimal; the beam is reported.

Size in bits (a stated prefix code): every node costs 1 bit (leaf / test); a test costs log2(#features) +
log2(#values of its feature); a leaf costs log2(#templates).  Also reported: the same tree as a decision list (one
rule per leaf, its path as a conjunction) and the number of (feature, value) literals.
"""
import argparse, functools, json, math, sys, time
from collections import Counter


def entropy(ys):
    n = len(ys)
    return -sum(c / n * math.log2(c / n) for c in Counter(ys).values()) if n else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rows')
    ap.add_argument('out')
    ap.add_argument('--beam', type=int, default=3)
    a = ap.parse_args()
    D = json.load(open(a.rows))
    feats = D['feats']
    X = [tuple(r['x']) for r in D['rows']]
    Y = [r['y'] for r in D['rows']]
    vals = [sorted({x[j] for x in X}) for j in range(len(feats))]
    labels = sorted(set(Y))
    tests = [(j, v) for j in range(len(feats)) for v in vals[j] if len(vals[j]) > 1]
    sys.setrecursionlimit(10000)
    t0 = time.time()

    @functools.lru_cache(maxsize=None)
    def best(rows):
        ys = [Y[i] for i in rows]
        if len(set(ys)) == 1:
            return (1, ('leaf', ys[0]))
        h = entropy(ys)
        cand = []
        for j, v in tests:
            L = tuple(i for i in rows if X[i][j] == v)
            if not L or len(L) == len(rows):
                continue
            R = tuple(i for i in rows if X[i][j] != v)
            g = h - (len(L) * entropy([Y[i] for i in L]) + len(R) * entropy([Y[i] for i in R])) / len(rows)
            cand.append((g, j, v, L, R))
        cand.sort(key=lambda c: -c[0])
        out = None
        for g, j, v, L, R in cand[:a.beam]:
            nl, tl = best(L)
            if out is not None and nl >= out[0]:
                continue
            nr, tr = best(R)
            if out is None or nl + nr < out[0]:
                out = (nl + nr, ('test', feats[j], v, tl, tr))
        return out

    n_leaves, tree = best(tuple(range(len(X))))
    nF = len(feats)

    def size(t):
        if t[0] == 'leaf':
            return 1 + math.log2(len(labels)), 0, 1
        j = feats.index(t[1])
        b = 1 + math.log2(nF) + math.log2(len(vals[j]))
        bl, il, ll = size(t[3])
        br, ir, lr = size(t[4])
        return b + bl + br, 1 + il + ir, ll + lr

    def classify(t, x):
        while t[0] == 'test':
            t = t[3] if x[feats.index(t[1])] == t[2] else t[4]
        return t[1]

    ok = sum(classify(tree, x) == y for x, y in zip(X, Y))
    bits, n_int, n_leaf = size(tree)

    def rules(t, path):
        if t[0] == 'leaf':
            return [(path, t[1])]
        return rules(t[3], path + [(t[1], t[2], True)]) + rules(t[4], path + [(t[1], t[2], False)])

    R = rules(tree, [])
    lits = sum(len(p) for p, _ in R)
    res = {'rows_file': a.rows, 'beam': a.beam, 'distinct_rows': len(X), 'templates': len(labels),
           'features': nF, 'feature_values': {f: len(vals[j]) for j, f in enumerate(feats)}, 'exact_rows': ok,
           'leaves': n_leaf, 'tests': n_int, 'bits': bits, 'depth': max(len(p) for p, _ in R),
           'decision_list_literals': lits, 'secs': time.time() - t0, 'tree': tree,
           'used_features': sorted({l[0] for p, _ in R for l in p})}
    json.dump(res, open(a.out, 'w'), indent=0)
    print(f"beam {a.beam}: exact {ok}/{len(X)} distinct rows; {n_leaf} leaves, {n_int} tests, depth {res['depth']}, "
          f"{bits:.0f} bits; features used {len(res['used_features'])}/{nF}; {res['secs']:.0f}s")


if __name__ == '__main__':
    main()
