"""Reviewer's own renaming-class key (premise-order and premise-multiplicity-insensitive) and disjointness."""
import json, itertools, re, sys, collections

def split_prem(lhs):
    prem, d, cur = [], 0, []
    for t in lhs.split():
        if t == ',' and d == 0: prem.append(tuple(cur)); cur = []; continue
        d += t.count('(') - t.count(')'); cur.append(t)
    if cur: prem.append(tuple(cur))
    return prem

def rename(toks):
    m = {}; out = []
    for t in toks:
        if re.fullmatch(r'[PQRS]', t):
            if t not in m: m[t] = 'abcdefgh'[len(m)]
            out.append(m[t])
        else: out.append(t)
    return ' '.join(out)

def key(thm):
    lhs, rhs = thm.split('|-')
    prem = sorted(set(split_prem(lhs)))
    goal = rhs.split()
    best = None
    for perm in itertools.permutations(prem):
        toks = [t for p in perm for t in list(p) + [',']] + ['|-'] + goal
        k = rename(toks)
        if best is None or k < best: best = k
    return best

def keys(path):
    ks = collections.Counter()
    for l in open(path):
        ks[key(json.loads(l)['thm'])] += 1
    return ks

if __name__ == '__main__':
    A = keys('../data/ca/heldout_A.jsonl'); B = keys('../data/ca/heldout_B.jsonl')
    print('A', sum(A.values()), len(A), 'B', sum(B.values()), len(B), 'A&B classes', len(set(A) & set(B)))
    for tr in ['/tmp/rv_ca/data/train_depth3_f0_a1.jsonl', '/tmp/rv_ca/data/train_fresh.jsonl']:
        T = keys(tr)
        print(tr, 'records', sum(T.values()), 'classes', len(T), 'shared with A', len(set(T) & set(A)), 'with B', len(set(T) & set(B)), flush=True)
