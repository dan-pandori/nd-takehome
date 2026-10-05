#!/usr/bin/env python3
"""Reviewer: J8 target soundness -- every J8 target (name, proof) must appear in some Lean-accepted read (any model,
incl. rl-from-ckpt ladders / controls) or be a reference.  md5 digests to keep memory small."""
import json, os, sys, glob, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
def h(n, p): return hashlib.md5((n + '\t' + p).encode()).digest()[:10]
names = set()
for s in (0, 1, 2):
    for v in json.load(open(f'{L.CD}/j8/sets.json'))[str(s)].values(): names |= set(v)
seen = set(); nfiles = 0
paths = glob.glob(f'{L.TJ}/s*__*_x*.jsonl') + glob.glob(f'{L.TJ6}/s*__*_x*.jsonl') + glob.glob(f'{L.RC}/s*__*_x*.jsonl') + \
        glob.glob(f'{L.RC6}/s*__*_x*.jsonl') + glob.glob(f'{L.RFC}/*__*_x*.jsonl') + glob.glob(f'{L.CD}/in/mcts*/*.jsonl') + glob.glob(f'{L.CD}/j5/*.jsonl')
for p in paths:
    nfiles += 1
    for r in L.rows(p):
        if r['name'] in names:
            for pf in r.get('proofs') or []:
                seen.add(h(r['name'], pf))
for r in L.rows(os.path.expanduser('~/work/trajectory/data/tj/ref_targets.jsonl')):
    seen.add(h(r['name'], r['proof']))
print('read files', nfiles, 'distinct (theorem, proof) in reads for J8 theorems', len(seen))
for s in (0, 1, 2):
    tot = miss = 0; ex = []
    for p in sorted(glob.glob(f'{L.CD}/j8/targets_s{s}_p*.jsonl')):
        for r in L.rows(p):
            tot += 1
            if h(r['name'], r['proof']) not in seen:
                miss += 1
                if len(ex) < 3: ex.append((r['tid'], r['proof'][:120]))
    print(f's{s}: J8 targets {tot}; not found in any read or reference: {miss}', ex)
