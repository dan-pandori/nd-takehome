#!/usr/bin/env python3
"""Reviewer (coe-dose01): proof length of the counted held-out proofs in lines (ND written / pruned, from found_transfer)
and in term size (own `import Lean` meta pass, leanrc.sizes) on a random sample of their literal texts per ladder."""
import collections, json, random, statistics as st, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl
from recheck import load, LADS
import leanrc

out = {}
rng = random.Random(3)
for lad in LADS:
    ft, dump, acc = load(lad)
    rows = [(p, t, acc[(p, t)][1]) for (p, t) in sorted(acc)]
    rng.shuffle(rows)
    samp = rows[:150]
    sz = []
    for i in range(0, len(samp), 75):
        sz += leanrc.sizes([(p, t) for p, t, _ in samp[i:i + 75]])
    # line counts for the same sampled texts, joined through the ND string
    wl = {}
    for x in jl(f'{BIG}/ft/{lad}_strict.jsonl.gz'):
        wl[(x['prompt'], x['proof'])] = (x['written'], x['pruned'])
    pairs = [(s, wl.get((p, nd))) for (p, t, nd), s in zip(samp, sz)]
    good = [(s, w) for s, w in pairs if s is not None and w is not None]
    allw = [w for w in wl.values()]
    out[lad] = dict(sample=len(samp), sized=sum(1 for s in sz if s is not None),
                    term_size_median=st.median([s for s, _ in good]) if good else None,
                    term_size_iqr=(sorted(s for s, _ in good)[len(good) // 4], sorted(s for s, _ in good)[3 * len(good) // 4]) if good else None,
                    written_median_sample=st.median([w[0] for _, w in good]) if good else None,
                    pruned_median_sample=st.median([w[1] for _, w in good]) if good else None,
                    written_median_all=st.median([w[0] for w in allw]), pruned_median_all=st.median([w[1] for w in allw]),
                    n_found_rows=len(allw),
                    spearman_size_vs_pruned=None)
    if len(good) > 5:
        def rank(v):
            o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
            i = 0
            while i < len(o):
                j = i
                while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                    j += 1
                for k in range(i, j + 1):
                    r[o[k]] = (i + j) / 2
                i = j + 1
            return r
        a = rank([s for s, _ in good]); b = rank([w[1] for _, w in good])
        ma, mb = st.mean(a), st.mean(b)
        cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        out[lad]['spearman_size_vs_pruned'] = round(cov / (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5, 3)
    print(lad, out[lad], flush=True)
json.dump(out, open(f'{REPO}/review_cd01/out/sizes.json', 'w'), indent=1)
