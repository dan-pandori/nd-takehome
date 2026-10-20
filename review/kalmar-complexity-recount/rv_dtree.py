#!/usr/bin/env python3
"""Reviewer check of the decision trees (run kalmar-complexity).

  python3 rv_dtree.py --n 1000 --seed 271828

- my own template label (step tag | the rule head of the action), compared with the executor's label() on every state;
- the executor's feature extractor (features.py, the artefact under test) on every state of a fresh sample;
- every committed tree classifies every state; exact counts, unseen feature vectors, conflicting vectors;
- tree size recomputed with the stated code (node 1 bit; test log2 #features + log2 #values of its feature; leaf
  log2 #templates), with #values / #templates taken from the tree's own fitting rows file.
"""
import argparse, collections, json, math, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar'))
sys.path.insert(0, os.path.join(WS, 'kalmar_complexity', 'programs', 'dtree'))
DT = os.path.join(WS, 'artifacts', 'kc', 'dtree')


def my_label(tag, act):
    if act[0] == 'exact':
        return tag
    j = act.index(':=')
    body = act[j + 1:]
    if body and body[-1] == ';':
        body = body[:-1]
    h = body[0]
    if h == '(':
        k = 'open'
    elif h in ('Or.elim',):
        k = 'ORE'
    elif h == '⟨':
        k = 'ANDI'
    elif h in ('Or.inl', 'Or.inr', 'Classical.byContradiction'):
        k = h
    elif len(body) == 2 and body[1] in ('.1', '.2', '.elim'):
        k = body[1]
    elif len(body) == 2:
        k = 'app'
    else:
        k = 'cite'
    return tag + '|' + k


def tree_bits(tree, feats, nvals, ntemp):
    nF = len(feats)
    tot = 0.0; leaves = 0; tests = 0; depth = 0
    st = [(tree, 0)]
    while st:
        t, d = st.pop()
        depth = max(depth, d)
        if t[0] == 'leaf':
            tot += 1 + math.log2(ntemp); leaves += 1
        else:
            tot += 1 + math.log2(nF) + math.log2(nvals[t[1]]); tests += 1
            st.append((t[3], d + 1)); st.append((t[4], d + 1))
    return tot, leaves, tests, depth


def classify(t, F):
    while t[0] == 'test':
        t = t[3] if str(F[t[1]]) == t[2] else t[4]
    return t[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=271828)
    a = ap.parse_args()
    import kalmar
    from state_env import decompose
    from features import features, label, FEATS
    trees = {f: json.load(open(os.path.join(DT, f))) for f in sorted(os.listdir(DT)) if f.startswith('tree_')}
    rowsets = {}
    for f, d in trees.items():
        rf = os.path.join(WS, d['rows_file'])
        if rf not in rowsets:
            R = json.load(open(rf))
            rowsets[rf] = R
    ps = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
    idx = sorted(random.Random(a.seed).sample(range(len(ps)), a.n))
    t0 = time.time()
    rows = collections.Counter(); lab_agree = 0; nst = 0
    for i in idx:
        p = ps[i]
        r = kalmar.build(p, 'sl')
        steps, toks, env = decompose(p, r['proof'], canon=True)
        for (st, act, _h), tag in zip(steps, r['tags']):
            nst += 1
            F = features(list(st))
            y = my_label(tag, list(act))
            lab_agree += y == label(tag, list(act))
            rows[(tuple(str(F[k]) for k in FEATS), y)] += 1
    byx = collections.defaultdict(set)
    for (x, y) in rows:
        byx[x].add(y)
    conflicts = sum(1 for ys in byx.values() if len(ys) > 1)
    out = {'n_theorems': a.n, 'seed': a.seed, 'states': nst, 'label_agree': lab_agree, 'distinct_vectors': len(byx),
           'distinct_rows': len(rows), 'conflicting_vectors': conflicts, 'templates_seen': len({y for _, y in rows}),
           'trees': {}}
    for f, d in trees.items():
        R = rowsets[os.path.join(WS, d['rows_file'])]
        feats = R['feats']
        fit_x = {tuple(r['x']) for r in R['rows']}
        nvals = {ft: len({r['x'][j] for r in R['rows']}) for j, ft in enumerate(feats)}
        ntemp = len({r['y'] for r in R['rows']})
        bits, leaves, tests, depth = tree_bits(d['tree'], feats, nvals, ntemp)
        ok_states = sum(c for (x, y), c in rows.items() if classify(d['tree'], dict(zip(FEATS, x))) == y)
        unseen = sum(1 for x in byx if x not in fit_x)
        unseen_states = sum(c for (x, y), c in rows.items() if x not in fit_x)
        # fitting rows reproduced?
        fit_ok = sum(classify(d['tree'], dict(zip(feats, r['x']))) == r['y'] for r in R['rows'])
        out['trees'][f] = {'rows_file': d['rows_file'], 'beam': d['beam'], 'fit_rows_exact': [fit_ok, len(R['rows'])],
                           'my_bits': round(bits, 2), 'leaves': leaves, 'tests': tests, 'depth': depth,
                           'n_features': len(feats), 'n_templates_in_fit_rows': ntemp,
                           'fresh_states_exact': ok_states, 'fresh_states': nst,
                           'fresh_vectors_unseen_in_fit': unseen, 'fresh_states_with_unseen_vector': unseen_states}
    out['seconds'] = time.time() - t0
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'out', f'dtree_s{a.seed}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
