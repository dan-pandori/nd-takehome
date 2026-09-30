#!/usr/bin/env python3
"""Reviewer (long-pool-2): earlier on-file reads of the 70 >=17 theorems (calib_rows, max_steps 48) vs this run's reads (96)."""
import json, glob, os
def solved(fn): return {json.loads(l)['name']: bool(json.loads(l)['proofs']) for l in open(fn)}
RR='artifacts/lpool2/rr'
for f in sorted(glob.glob('artifacts/lpool2/calib_rows/*__ge17.jsonl')):
    tag=os.path.basename(f)[:-len('__ge17.jsonl')]
    a=solved(f); b=solved(f'{RR}/{tag}__cal.jsonl')
    assert set(a)==set(b), tag
    both=sum(a[n] and b[n] for n in a); oa=sum(a[n] and not b[n] for n in a); ob=sum(b[n] and not a[n] for n in a)
    extra=''
    if os.path.exists(f'{RR}/{tag}_ms96__ge17.jsonl'):
        c=solved(f'{RR}/{tag}_ms96__ge17.jsonl')
        extra=f' | ms96 ge17 read {sum(c.values())}, vs cal read: only-ge17 {sum(c[n] and not b[n] for n in c)} only-cal {sum(b[n] and not c[n] for n in c)}'
    print(f'{tag:16s} earlier {sum(a.values()):2d} this {sum(b.values()):2d} both {both:2d} only-earlier {oa} only-this {ob}{extra}')
