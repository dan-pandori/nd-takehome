#!/usr/bin/env python3
"""Reviewer: check the executor's ledgers with the reviewer's own normaliser (qcheck.norm), plus negative controls.
Prints counts and failing row ids only (no values), so it can run in phase 1 without reading the executor's numbers.
Controls: (1) one digit in each digit-bearing quote changed -> must NOT be found; (2) quote checked against a different
source file (next file in sorted order) -> should mostly NOT be found; (3) quote with two words swapped -> must NOT be found
when the swap changes the text."""
import csv, glob, os, random, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcheck import norm, text
L = '/home/dan/work/rl-compute-share/rl_compute_share/ledger'
rng = random.Random(7)
res = {}
allfiles = sorted({os.path.join('rcs_sources', f) for f in os.listdir(os.path.expanduser('~/rcs_sources'))})
for f in sorted(glob.glob(f'{L}/*.tsv')):
    rows = list(csv.DictReader(open(f), delimiter='\t', quoting=csv.QUOTE_NONE))
    ok = bad = 0; bad_ids = []; c1 = [0, 0]; c2 = [0, 0]; c3 = [0, 0]; empty = 0
    for r in rows:
        q = r['quote']; src = r['source_file'].replace('~/', '').replace('/home/dan/', '')
        if '/' not in src: src = 'rcs_sources/' + src
        if not q.strip() or q.strip() == '-':
            empty += 1; continue
        t = text(src)
        if t is not None and norm(q) in t: ok += 1
        else: bad += 1; bad_ids.append(r['claim_id'])
        # control 1: digit mutation
        ds = [i for i, ch in enumerate(q) if ch.isdigit()]
        if ds and t is not None:
            i = rng.choice(ds); q1 = q[:i] + str((int(q[i]) + 1) % 10) + q[i+1:]
            c1[0] += 1; c1[1] += norm(q1) in t
        # control 2: wrong file
        other = allfiles[(allfiles.index(src) + 1) % len(allfiles)] if src in allfiles else allfiles[0]
        t2 = text(other)
        if t2 is not None:
            c2[0] += 1; c2[1] += norm(q) in t2
        # control 3: swap two adjacent words
        w = q.split()
        if len(w) >= 4:
            j = rng.randrange(len(w) - 1)
            if w[j] != w[j+1]:
                w[j], w[j+1] = w[j+1], w[j]; q3 = ' '.join(w)
                if t is not None:
                    c3[0] += 1; c3[1] += norm(q3) in t
    res[os.path.basename(f)] = dict(rows=len(rows), found=ok, not_found=bad, empty=empty, not_found_ids=bad_ids,
                                    ctl_digit=f'{c1[1]}/{c1[0]} still found', ctl_wrongfile=f'{c2[1]}/{c2[0]} found',
                                    ctl_swap=f'{c3[1]}/{c3[0]} still found')
print(json.dumps({k: {kk: (vv if kk != 'not_found_ids' else vv[:40]) for kk, vv in v.items()} for k, v in res.items()}, indent=1))
tot = sum(v['rows'] for v in res.values()); fnd = sum(v['found'] for v in res.values())
print('TOTAL rows', tot, 'found', fnd)
