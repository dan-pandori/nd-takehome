#!/usr/bin/env python3
"""Reviewer: J10 (long pool) selection and outcome; J9 certification totals per (seed, theorem)."""
import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
CD = L.CD
# ---------------- J10
long2 = [r['name'] for r in L.rows(f'{L.RV}/data/ladder/transfer_long2.jsonl')]
print('long2 theorems', len(long2))
tot_pairs = tot_hit = 0
for s in (0, 1, 2):
    pend2 = L.read(12, s, 'pend', 'long2', 2)
    r8 = {r['name']: r for r in L.rows(f'{L.RC}/s{s}_r8__long2_x0.jsonl')}
    r16 = {r['name']: r for r in L.rows(f'{L.RC}/s{s}_r16__long2_x0.jsonl')}
    sel = [n for n in long2 if (r8[n]['n_ok'] > 0 or r16[n]['n_ok'] > 0) and pend2[n][0] == 0]
    eqk8 = [n for n in long2 if r8[n]['n_ok'] > 0 and pend2[n][0] == 0]
    files = sorted(glob.glob(f'{CD}/j10/s{s}_c*.jsonl'))
    got = {}
    for p in files:
        for r in L.rows(p):
            got[r['name']] = (r['n_ok'], r['n_tried'], r.get('proofs') or [], collections.Counter(r['reasons'] if isinstance(r['reasons'], list) else r['reasons']))
    inp = [r['name'] for p in sorted(glob.glob(f'{L.RV}/data/cd/j10/s{s}_c*.jsonl')) for r in L.rows(p)]
    hit = [n for n in sel if got[n][0] > 0]
    tr = sum(got[n][3]['lean_seq parse: env: action truncated'] + got[n][3]['lean_seq parse: env: step cap'] for n in got)
    att = sum(got[n][1] for n in got)
    print(f's{s}: r8 x0 solves & pend x2 fails (equal-k gap, r8): {len(eqk8)}; selected (r8 or r16 x0, pend x2 = 0): {len(sel)}; input == selection: {set(inp) == set(sel)}; '
          f'k {set(v[1] for v in got.values())}; >=1 success {len(hit)}/{len(sel)} {[(n, got[n][0]) for n in hit]}; truncated {tr}/{att} = {100 * tr / att:.3f} %')
    for n in sel:
        if got[n][3]:
            t = got[n][3]['lean_seq parse: env: action truncated'] + got[n][3]['lean_seq parse: env: step cap']
            if t / got[n][1] > 0.001:
                print(f'     {n}: {got[n][0]}/{got[n][1]} cut off {100 * t / got[n][1]:.2f} %')
    tot_pairs += len(sel); tot_hit += len(hit)
print(f'J10: {tot_hit}/{tot_pairs} theorem-seed pairs get >= 1 base success = {tot_hit / tot_pairs:.3f}')

# ---------------- J9
print()
for s in (0, 1, 2):
    sel = [r['name'] for r in L.rows(f'{L.RV}/data/cd/j9/s{s}.jsonl')]
    tot = collections.defaultdict(lambda: [0, 0, set()])
    chunks = sorted(p for p in glob.glob(f'{CD}/j9/s{s}_k*.jsonl') if not p.endswith('.full.jsonl'))
    for p in chunks:
        for r in L.rows(p):
            t = tot[r['name']]; t[0] += r['n_ok']; t[1] += r['n_tried']; t[2].update(r.get('proofs') or [])
    # add J2 standard-cap attempts (stage A c*, A' d*, B b*)
    j2 = collections.defaultdict(lambda: [0, 0])
    for p in glob.glob(f'{CD}/j2/s{s}_*.jsonl'):
        b = os.path.basename(p).split('_')[1]
        if b[0] in 'cdb' and not b.startswith('cal'):
            for r in L.rows(p):
                j2[r['name']][0] += r['n_ok']; j2[r['name']][1] += r['n_tried']
    print(f's{s}: J9 selection {sel}; chunk files {len(chunks)}')
    for n in sel:
        print(f'   {n}: J9 {tot[n][0]}/{tot[n][1]:,}  J2 {j2[n][0]}/{j2[n][1]:,}  total attempts {tot[n][1] + j2[n][1]:,}  proofs found in J9: {len(tot[n][2])}')
