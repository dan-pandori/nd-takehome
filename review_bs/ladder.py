#!/usr/bin/env python3
"""Reviewer ladder recount: per ladder and round, distinct solved targets / transfer theorems and distinct proofs from
found_<r>.jsonl (own start-index normaliser: renumber N-labels in order of first appearance), vs round_<r>.json."""
import json, glob, os, re
R = os.path.expanduser('~/review/best-state')
def norm(p):
    mp = {}
    def f(m):
        k = m.group(1)
        if k not in mp: mp[k] = str(len(mp) + 1)
        return 'N' + mp[k]
    return re.sub(r'\bN(\d+)\b', f, p)
out = {}
for d in sorted(glob.glob(f'{R}/artifacts/bs/la_T1_*')):
    lad = os.path.basename(d); out[lad] = {}
    for r in range(1, 9):
        rj = json.load(open(f'{d}/round_{r}.json'))
        row = {'secs': rj['secs'], 'lstar_t': rj['targets_cum']['lstar']}
        for pool, fn, k in (('targets', f'{d}/found_{r}.jsonl', 'targets_cum'), ('transfer', f'{d}/found_transfer_{r}.jsonl', 'transfer_cum')):
            th = set(); pr = set()
            for l in open(fn):
                x = json.loads(l); th.add(x['name']); pr.add((x['name'], norm(x['proof'])))
            row[pool] = (len(th), len(pr), rj[k]['solved'], rj[k]['distinct_proofs'])
        row['heldout_greedy'] = rj['heldout_greedy']['solved']
        out[lad][r] = row
        print(lad, r, row, flush=True)
json.dump(out, open(f'{R}/review_bs/ladder.json', 'w'), indent=1)
