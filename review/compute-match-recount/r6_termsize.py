#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 6: proof length (written ND lines, PR lines excluded) and term size of the
shortest stored proof per solved target, per arm (mean over seeds of the per-file median), on tb72 / long2 / rr600 / dev,
both over all solved targets and over the targets every one of the 9 checkpoints solved (common set).
Term size (mine): ND lines that are not PR / AS / R, i.e. one node per rule application.  Output: recount_termsize.json"""
import json, os, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
D = {'cm12': os.path.expanduser('~/review/compute-match/artifacts/cm/eval'), 'SN12': os.path.expanduser('~/review/compute-match/artifacts/cm/eval'), 'best12': '/tmp/cmr/bs'}
LAB = {'cm12': 'T1_cm12k64_s{}', 'SN12': 'T1_SN12_s{}', 'best12': 'T1_best12_s{}'}
def meas(p):
    L = [x for x in p.split(' ; ') if x.strip() and x.strip() != 'QED']
    rules = [x.rsplit(' : ', 1)[1].split()[0] for x in L]
    return sum(r != 'PR' for r in rules), sum(r not in ('PR', 'AS', 'R') for r in rules)
out = {}
for rd in ('tb72', 'long2', 'rr600', 'dev'):
    best = {}
    for a in D:
        for s in (0, 1, 2):
            fn = f'{D[a]}/{LAB[a].format(s)}__{rd}.jsonl'
            if not os.path.exists(fn): continue
            best[(a, s)] = {r['name']: min(meas(p) for p in r['proofs']) for r in map(json.loads, open(fn)) if r['solved']}
    common = set.intersection(*[set(v) for v in best.values()]) if len(best) == 9 else set()
    for a in D:
        ks = [k for k in best if k[0] == a]
        if not ks: continue
        row = {}
        for nm, sel in (('all', None), ('common', common)):
            ln = [st.median([best[k][n][0] for n in best[k] if sel is None or n in sel]) for k in ks if (sel is None or sel)]
            ts = [st.median([best[k][n][1] for n in best[k] if sel is None or n in sel]) for k in ks if (sel is None or sel)]
            row[nm] = {'lines_med': round(st.mean(ln), 2) if ln else None, 'term_med': round(st.mean(ts), 2) if ts else None}
        row['n_common'] = len(common); out[f'{a}:{rd}'] = row; print(a, rd, row)
json.dump(out, open(f'{H}/recount_termsize.json', 'w'), indent=1)
