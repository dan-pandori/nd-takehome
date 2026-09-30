#!/usr/bin/env python3
"""Reviewer (lit-measures) M1 sets, built independently from support-state's raw records."""
import json, glob, collections, random
IN = '/home/dan/review/lit-measures/rv/in'
rd = lambda f: [json.loads(l) for l in open(f)]
TH = {r['name']: r for r in rd(f'{IN}/theorems.jsonl')}
base_reach = collections.Counter(); base_tried = collections.defaultdict(lambda: collections.Counter())
ei = collections.defaultdict(dict)    # name -> proof -> record
base_pr = collections.defaultdict(dict)
for f in sorted(glob.glob(f'{IN}/ss/S*.jsonl')):
    for r in rd(f):
        T = r['temperature']
        if r['model'] == 'base':
            base_tried[r['name']][T] += r['n_tried']
            if r['n_ok'] > 0 or r['proofs']:
                base_reach[r['name']] += len(r['proofs'])
                for p in r['proofs']:
                    base_pr[r['name']].setdefault(p['proof'], p)
        else:
            assert r['model'] == 'ei' and r['ckpt_md5'].startswith('fb448247'), (f, r['ckpt_md5'])
            for p in r['proofs']:
                ei[r['name']].setdefault(p['proof'], p)
S = sorted(n for n in ei if n not in base_reach and ei[n])
print('EI-solved', sum(1 for n in ei if ei[n]), 'base-reached', len(base_reach))
print('S (EI solves, base never):', len(S))
for n in S:
    print(' ', n, 'L_true', TH[n]['L_true'], 'base tried', dict(base_tried[n]), 'EI distinct', len(ei[n]))

S7 = ['la_transfer_' + x for x in '1108 1185 1352 198 2089 394 988'.split()]
S7r = sorted(n for n in S if min(base_tried[n].values()) >= 200000)
assert sorted(S7) == S7r, S7r
nS = collections.Counter(TH[n]['L_true'] for n in S7)
R = random.Random(0)
C1 = []
for L in sorted(nS):
    cand = sorted(n for n in ei if ei[n] and n in base_reach and TH[n]['L_true'] == L)
    k = min(5 * nS[L], len(cand))
    pick = sorted(R.sample(cand, k))
    print('L_true', L, 'S', nS[L], 'candidates', len(cand), 'picked', k)
    C1 += pick
out = open('/home/dan/review/lit-measures/rv/m1_proofs.jsonl', 'w')
cnt = collections.Counter()
for st, names, src in (('S', S7, ei), ('C1', C1, ei), ('C2', C1, base_pr)):
    for n in names:
        for p, rec in src[n].items():
            out.write(json.dumps({'set': st, 'name': n, 'prompt': TH[n]['prompt'], 'L_true': TH[n]['L_true'], 'proof': p,
                                  'n_lines': rec.get('n_lines'), 'term_size': rec.get('term_size'), 'count': rec.get('count'),
                                  'lean_text': rec.get('lean_text')}) + '\n')
            cnt[st] += 1
print(dict(cnt), 'C1 theorems', len(C1), 'C2 theorems with base proofs', sum(1 for n in C1 if base_pr[n]))
json.dump({'C1': C1}, open('/home/dan/review/lit-measures/rv/m1_c1.json', 'w'))
