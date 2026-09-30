#!/usr/bin/env python3
"""Lean re-check of every counted read-out proof (all arms/seeds), with the reviewer's term size."""
import json, glob, os, sys, time
sys.path.insert(0, os.path.dirname(__file__)); import rlean
R = os.path.expanduser('~/review/search-expert'); A = f'{R}/artifacts/sx/rr'
items = []
for f in sorted(glob.glob(f'{A}/*.jsonl')):
    tag = os.path.basename(f)[:-6]
    for l in open(f):
        r = json.loads(l)
        for p in r['proofs']: items.append(dict(tag=tag, name=r['name'], prompt=r['prompt'], nd=p))
print(len(items), flush=True)
out = open(f'{R}/rv/fullcheck.jsonl', 'w')
t = time.time()
for s in range(0, len(items), 1500):
    ch = items[s:s + 1500]
    res = rlean.check([(x['prompt'], rlean.render(x['prompt'], x['nd'])) for x in ch], per_file=300, size=True)
    for x, (ok, info, sz) in zip(ch, res):
        nprem = len(rlean.stmt(x['prompt'])[0])
        out.write(json.dumps(dict(tag=x['tag'], name=x['name'], lines=x['nd'].count(';'), ok=ok, info=info,
                                  size=None if sz is None else sz - 4 - nprem, nd=x['nd'])) + '\n')
    out.flush(); print(s + len(ch), round(time.time() - t), flush=True)
