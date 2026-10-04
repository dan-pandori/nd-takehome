#!/usr/bin/env python3
"""Reviewer phase-2 checks of specific executor claims: distinct C theorems solved at r16, pairs at 0/256 at r8,
'never solved at r8 by any seed' (x1 and x0+x1), summed successes, A/B sizes."""
import json, os, collections
R = os.path.expanduser('~/review/rl-continue-cap6'); A = f'{R}/artifacts/rc6'
def load(f): return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
G = json.load(open(f'{R}/review_rc6/rv/groupc.json'))
pairs = []; summ = {}; AB = {}
r8any = collections.defaultdict(lambda: [0, 0])
for s in (0, 1, 2):
    g = {}
    for pool in ('tb72', 'h250'):
        p0 = load(f'{A}/tj6_eval/s{s}_pend__{pool}_x0.jsonl'); p8 = load(f'{A}/tj6_eval/s{s}_r8__{pool}_x0.jsonl')
        for n in p0: g[f'{pool}:{n}'] = 'A' if p0[n]['proofs'] else ('B' if p8[n]['proofs'] else 'C')
        for xs in (0, 1):
            d = load(f'{A}/tj6_eval/s{s}_r8__{pool}_x{xs}.jsonl')
            for n, r in d.items(): r8any[f'{pool}:{n}'][xs] += r['n_ok']
    AB[s] = collections.Counter(g.values())
    r8 = {**{f'tb72:{n}': r for n, r in load(f'{A}/tj6_eval/s{s}_r8__tb72_x1.jsonl').items()}, **{f'h250:{n}': r for n, r in load(f'{A}/tj6_eval/s{s}_r8__h250_x1.jsonl').items()}}
    r16 = {**{f'tb72:{n}': r for n, r in load(f'{A}/eval/s{s}_r16__tb72_x1.jsonl').items()}, **{f'h250:{n}': r for n, r in load(f'{A}/eval/s{s}_r16__h250C_x1.jsonl').items()}}
    C = [k for k, v in g.items() if v == 'C']
    summ[s] = (sum(r8[k]['n_ok'] for k in C), sum(r16[k]['n_ok'] for k in C))
    for k in G[str(s)]['r16']['C_solved']: pairs.append((s, k, r8[k]['n_ok']))
dist = {k for _, k, _ in pairs}
print('A/B/C sizes', {s: dict(v) for s, v in AB.items()})
print('summed successes over C r8 -> r16', summ)
print('pairs', len(pairs), 'distinct', len(dist), 'pairs at 0/256 at r8 (x1)', sum(1 for p in pairs if p[2] == 0))
cnt = collections.Counter(k for _, k, _ in pairs); print('solved by all 3 seeds', [k for k, v in cnt.items() if v == 3])
print('distinct never solved at r8 by any seed, x1 only:', sum(1 for k in dist if r8any[k][1] == 0), '; x0 and x1:', sum(1 for k in dist if sum(r8any[k]) == 0))
# definition check for "never solved at r8 by any seed": restricted to seeds whose C holds the theorem (x1 r8 read) vs all seeds' r8 reads
Cmem = collections.defaultdict(set)
for s in (0, 1, 2):
    for pool in ('tb72', 'h250'):
        p0 = load(f'{A}/tj6_eval/s{s}_pend__{pool}_x0.jsonl'); p8 = load(f'{A}/tj6_eval/s{s}_r8__{pool}_x0.jsonl')
        for n in p0:
            if not p0[n]['proofs'] and not p8[n]['proofs']: Cmem[f'{pool}:{n}'].add(s)
r8x1 = {s: {**{f'tb72:{n}': r['n_ok'] for n, r in load(f'{A}/tj6_eval/s{s}_r8__tb72_x1.jsonl').items()}, **{f'h250:{n}': r['n_ok'] for n, r in load(f'{A}/tj6_eval/s{s}_r8__h250_x1.jsonl').items()}} for s in (0, 1, 2)}
restricted = [k for k in dist if all(r8x1[s][k] == 0 for s in Cmem[k])]
full = [k for k in dist if all(r8x1[s][k] == 0 for s in (0, 1, 2))]
print('never solved at r8 (x1): over seeds whose C holds it', len(restricted), '; over all three seeds', len(full))
print('  in C of all 3 seeds:', sum(1 for k in dist if len(Cmem[k]) == 3), '; theorems solved at r8 x1 by a seed where they are in A/B:',
      sorted(k for k in restricted if k not in full))
# base reachability: the 29 r16 C (seed, theorem) pairs at pend on the independent sample draw x1 (C requires x0 failure only)
pend1 = {s: {**{f'tb72:{n}': r['n_ok'] for n, r in load(f'{A}/tj6_eval/s{s}_pend__tb72_x1.jsonl').items()}, **{f'h250:{n}': r['n_ok'] for n, r in load(f'{A}/tj6_eval/s{s}_pend__h250_x1.jsonl').items()}} for s in (0, 1, 2)}
pp = [(s, k) for s, k, _ in pairs if pend1[s][k] > 0]
print('r16-solved C pairs already solved at pend on sample draw x1 (same seed):', len(pp), 'of', len(pairs), pp)
anyp = [k for k in dist if any(pend1[s][k] > 0 for s in (0, 1, 2))]
print('distinct r16-solved C theorems solved at pend x1 by any seed:', len(anyp), 'of', len(dist))
allC = [k for k in Cmem if Cmem[k]]
for s in (0, 1, 2):
    C = [k for k in Cmem if s in Cmem[k]]
    print(f's{s}: C pass@256 at pend x1 {sum(pend1[s][k] > 0 for k in C)}/{len(C)}')
