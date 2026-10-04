#!/usr/bin/env python3
"""Reviewer phase 2 (rl-continue): executor claims on s1's burst (schema / L_true / cross-seed), s1's new C solves (by
statement), cap concentration in reads."""
import json, os, collections
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'; D = os.path.expanduser('~/review/rc_data')
rc = json.load(open(f'{R}/review_rc/rv/recount.json')); G = json.load(open(f'{R}/review_rc/rv/groupc.json'))
TG = {json.loads(l)['name']: json.loads(l) for l in open(f'{R}/data/ladder/rl_targets.jsonl')}
first = {}
for s in (0, 1, 2):
    f = {}
    for l in open(f'{D}/s{s}/found_16.jsonl'):
        x = json.loads(l); f[x['name']] = min(f.get(x['name'], 99), x['round'])
    first[s] = f
new1 = rc['1']['targets']['new_names']
late = [n for n in new1 if first[1][n] >= 13]
L9 = [n for n in late if TG[n]['n_lines'] == 9]
print('s1 new', len(new1), '; first in r13-16', len(late), '; of those L_true 9:', len(L9), '; schema of those:', collections.Counter(TG[n]['schema'] for n in L9))
print('s1 new by schema (all 68):', collections.Counter(TG[n]['schema'] for n in new1).most_common(8))
allL9 = [n for n in new1 if TG[n]['n_lines'] == 9]
for S in (0, 2):
    print(f's{S} solves by r16: of s1 late-L9 {sum(n in first[S] for n in L9)}/{len(L9)}; of all s1 new L9 {sum(n in first[S] for n in allL9)}/{len(allL9)}; of all 68 {sum(n in first[S] for n in new1)}; '
          f'of the excluded_middle ones {sum(n in first[S] for n in new1 if TG[n]["schema"]=="excluded_middle")}/{sum(TG[n]["schema"]=="excluded_middle" for n in new1)}')
L9em = [n for n in L9 if TG[n]['schema'] == 'excluded_middle']
print('of the 34 late excluded_middle: s0 solves', sum(n in first[0] for n in L9em), 's2 solves', sum(n in first[2] for n in L9em), '; the non-EM late-L9 one:', [(n, TG[n]['thm'], n in first[0], n in first[2]) for n in L9 if n not in L9em])
em = [n for n in TG if TG[n]['schema'] == 'excluded_middle']
print('excluded_middle targets in pool', len(em), '; solved by r8 / r16 per seed', [(sum(first[s].get(n, 99) <= 8 for n in em), sum(n in first[s] for n in em)) for s in (0, 1, 2)])
# s1's new C solves: statements
ev = {p: {json.loads(l)['name']: json.loads(l) for l in open(f'{A}/eval/s1_r16__{p}_x1.jsonl')} for p in ('tb72', 'h250')}
for t in G['1']['C_gained_r16']:
    p, n = t.split(':'); r = ev[p][n]; print(f'   {t:40s} {r["thm"] or r["prompt"]}  n_ok {r["n_ok"]}')
# cap concentration in r16 tb72 reads
for s in (0, 1, 2):
    d = [json.loads(l) for l in open(f'{A}/eval/s{s}_r16__tb72_x1.jsonl')]
    it = lambda r: r['reasons'].items() if isinstance(r['reasons'], dict) else collections.Counter(r['reasons']).items()
    c = sorted(((sum(v for z, v in it(r) if 'truncat' in z or 'step cap' in z), r['name']) for r in d), reverse=True)
    tot = sum(x for x, _ in c)
    print(f's{s} r16 tb72 cut samples {tot} in {sum(x > 0 for x, _ in c)} rows; top-2 rows hold {sum(x for x, _ in c[:2])} ({c[:2]})')
