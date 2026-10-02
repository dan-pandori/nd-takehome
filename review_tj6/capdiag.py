#!/usr/bin/env python3
"""Reviewer: 2x-cap re-read (capdiag) — inputs == my C@r8 / B@pend sets?  how many flip?  residual cut-off at 2x."""
import json, os, collections
from recount import R, cut
G = json.load(open(f'{R}/rv6/recount.json'))['groups']
res = {}
for s in (0, 1, 2):
    for ck, grp in (('r8', 'C'), ('pend', 'B')):
        for pool in ('tb72', 'h250'):
            mine = {k.split(':', 1)[1] for k, v in G[str(s)].items() if v == grp and k.startswith(pool)}
            inp = {json.loads(l)['name'] for l in open(f'{R}/data/tj6/capdiag_s{s}_{ck}_{pool}.jsonl')}
            out = [json.loads(l) for l in open(f'{R}/artifacts/tj6/capdiag/s{s}_{ck}__{pool}_x0_2x.jsonl')]
            sol = [r['name'] for r in out if r['proofs']]
            c = sum(cut(r) for r in out); n = sum(r['n_tried'] for r in out)
            res[f's{s}_{ck}_{pool}'] = dict(input_eq_mine=inp == mine, n=len(out), solved_2x=sol, cut2x=c / n)
            print(f's{s} {ck:4s} {pool}: {grp} n {len(mine)} input==mine {inp == mine} solved at 2x {len(sol)}  cut-off at 2x {100*c/n:.3f}%')
json.dump(res, open(f'{R}/rv6/capdiag.json', 'w'), indent=0)
