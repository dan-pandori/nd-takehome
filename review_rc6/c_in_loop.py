#!/usr/bin/env python3
"""Reviewer: were the h250 group-C theorems solved by the ladders' own per-round transfer sampling (k 32, never trained)?
And were the two transfer/rl_targets class-overlap theorems among the new transfer solves?"""
import json, os, collections
R = os.path.expanduser('~/review/rl-continue-cap6'); D = os.path.expanduser('~/review/rc6_data')
G = json.load(open(f'{R}/review_rc6/rv/groupc.json'))
for s in (0, 1, 2):
    C = {json.loads(l)['name'] for l in open(f'{R}/data/rc6/h250_C_s{s}.jsonl')}
    first = {}
    for l in open(f'{D}/s{s}/found_transfer_16.jsonl'):
        x = json.loads(l)
        if x['name'] in C or x['name'] in ('la_transfer_307', 'la_transfer_842'): first[x['name']] = min(first.get(x['name'], 99), x['round'])
    g16 = {n.split(':')[1] for n in G[str(s)]['r16']['C_solved'] if n.startswith('h250:')}
    inl = {n: r for n, r in first.items() if n in C}
    print(f's{s}: h250-C {len(C)}; solved in-loop by r8 {sum(r <= 8 for r in inl.values())}, by r16 {len(inl)} (first rounds {sorted(inl.values())}); '
          f'r16 read solved {len(g16)}; read-solved also in-loop {len(g16 & set(inl))}; overlap-class transfer first rounds',
          {n: first.get(n) for n in ('la_transfer_307', 'la_transfer_842')})
