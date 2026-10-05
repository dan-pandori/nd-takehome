#!/usr/bin/env python3
"""Reviewer: cut-off (action truncated / step cap) per read file and per stratum, for every read this run made."""
import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
TR = ('lean_seq parse: env: action truncated', 'lean_seq parse: env: step cap')
def tr(r):
    rs = r.get('reasons') or []
    c = collections.Counter(rs) if isinstance(rs, list) else collections.Counter(rs)
    return sum(c[t] for t in TR), sum(c.values())
for job in ('j4', 'j5', 'j6', 'j6b', 'j7', 'j9', 'j10'):
    worst = []; tot = [0, 0]; over_th = 0; nth = 0
    for p in sorted(glob.glob(f'{L.CD}/{job}/*.jsonl')):
        if p.endswith('.full.jsonl') or '_in' in os.path.basename(p): continue
        a = b = 0
        for r in L.rows(p):
            t, _ = tr(r); a += t; b += r['n_tried']; nth += 1; over_th += t / r['n_tried'] > 0.001
        tot[0] += a; tot[1] += b
        worst.append((a / b if b else 0, os.path.basename(p)))
    worst.sort(reverse=True)
    print(f'{job:4s}: cut off {tot[0]}/{tot[1]} = {100 * tot[0] / tot[1]:.3f} %; theorems > 0.1 %: {over_th}/{nth}; worst files ' +
          ', '.join(f'{f} {100 * v:.2f} %' for v, f in worst[:3]))
# J3 guided: status values
st = collections.Counter(); per = collections.Counter()
for p in glob.glob(f'{L.CD}/j3/*rows.jsonl.gz'):
    for r in L.rows(p):
        st.update(r['status'])
print('J3 guided attempt status:', st.most_common(12))
