#!/usr/bin/env python3
"""Run ckpt-avg: split data/p2/heldout.jsonl (5,000 theorems) into half A (anything that SELECTS: the
per-length validation loss used to pick a checkpoint) and half B (every reported accuracy).

Stratified by (n_lines, depth-3 slice) -- six strata: len2..len5 (1,000 each), len6 non-depth-3 (500),
len6 depth-3 (500) -- and split 50/50 inside each stratum with random.Random(SEED).  The unit of
assignment is a renaming class, not a record, so no class straddles the halves.  The class key is
premise-order INSENSITIVE (min of gen.canon_key over premise permutations): gen.canon_key alone is
premise-order sensitive (review of stage1-dynamics) and would understate overlap.

  python3 ca_split.py            -> data/ca/heldout_A.jsonl, data/ca/heldout_B.jsonl, data/ca/split.json
"""
import collections, itertools, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key

SEED = 20260928
SRC = 'data/p2/heldout.jsonl'
OUT = 'data/ca'


def class_key(thm):
    lhs, rhs = thm.split('|-')
    # premises are separated by top-level ' , ' (each premise is a parenthesised formula or an atom)
    prem, depth, cur = [], 0, []
    for t in lhs.split():
        if t == ',' and depth == 0:
            prem.append(' '.join(cur)); cur = []
            continue
        depth += t.count('(') - t.count(')')
        cur.append(t)
    if cur:
        prem.append(' '.join(cur))
    if len(prem) > 6:                    # never happens at cap 6; guard the factorial
        return canon_key(thm)
    return min(canon_key(' , '.join(p) + ' |- ' + rhs.strip()) for p in itertools.permutations(prem))


def main():
    recs = [json.loads(l) for l in open(SRC) if l.strip()]
    stratum = lambda r: (r['n_lines'], bool((r.get('pat') or {}).get('depth3')))
    classes = collections.defaultdict(list)          # key -> record indices
    for i, r in enumerate(recs):
        classes[class_key(r['thm'])].append(i)
    mixed = sum(1 for v in classes.values() if len({stratum(recs[i]) for i in v}) > 1)
    by_stratum = collections.defaultdict(list)
    for k, v in classes.items():
        by_stratum[stratum(recs[v[0]])].append(k)
    rng = random.Random(SEED)
    half = {}
    for s in sorted(by_stratum):
        ks = sorted(by_stratum[s])
        rng.shuffle(ks)
        n_target = sum(len(classes[k]) for k in ks) / 2
        a = 0
        for k in ks:                                  # greedy fill of A to half the stratum's records
            h = 'A' if a + len(classes[k]) <= n_target else 'B'
            if h == 'A':
                a += len(classes[k])
            for i in classes[k]:
                half[i] = h
    os.makedirs(OUT, exist_ok=True)
    cnt = collections.Counter()
    with open(f'{OUT}/heldout_A.jsonl', 'w') as fa, open(f'{OUT}/heldout_B.jsonl', 'w') as fb:
        for i, r in enumerate(recs):
            (fa if half[i] == 'A' else fb).write(json.dumps(r) + '\n')
            cnt[(half[i],) + stratum(r)] += 1
    kA = {class_key(recs[i]['thm']) for i in half if half[i] == 'A'}
    kB = {class_key(recs[i]['thm']) for i in half if half[i] == 'B'}
    info = {'source': SRC, 'seed': SEED, 'n': len(recs), 'n_classes': len(classes),
            'classes_with_gt1_record': sum(1 for v in classes.values() if len(v) > 1),
            'classes_spanning_strata': mixed, 'class_overlap_A_B': len(kA & kB),
            'counts': {f'{h}/len{L}/{"d3" if d else "nd3"}': c for (h, L, d), c in sorted(cnt.items())},
            'names_A': sorted(recs[i]['name'] for i in half if half[i] == 'A')}
    json.dump(info, open(f'{OUT}/split.json', 'w'), indent=1)
    print({k: v for k, v in info.items() if k != 'names_A'})


if __name__ == '__main__':
    main()
