# Reviewer (results-registry): role / duplication / checker-label checks over every registry row.
#   python3 review_rr_e3.py  (writes /tmp/rrrev/rows.pkl)  then  python3 review_rr_findings.py
import pickle, collections, itertools, subprocess, json, os
rows = pickle.load(open('/tmp/rrrev/rows.pkl', 'rb'))
lab = lambda r, k: (r.get('labels') or {}).get(k)
overall = lambda r: lab(r, 'L') is None and lab(r, 'slice') is None
# 1. GRPO arms: every round row has role=init and ckpt=the Stage-1 init
g = [r for r in rows if r['run_id'] == 'run4-grpo' and 'grpo' in (r['arm'] or '')]
hg = [r for r in g if r['metric'] == 'heldout_greedy_acc' and overall(r)]
print('run4-grpo GRPO arms', len({r['arm'] for r in g}), '| rows', len(g), 'roles', collections.Counter(r['role'] for r in g),
      '| overall heldout_greedy_acc rows', len(hg), 'range', min(r['value'] for r in hg), max(r['value'] for r in hg))
ei = {r['ckpt']: r['value'] for r in rows if r['run_id'] == 'run4-grpo' and 'grpo' not in (r['arm'] or '')
      and r['metric'] == 'heldout_greedy_acc' and overall(r) and lab(r, 'round') == 1}
for r in sorted(hg, key=lambda r: (r['arm'], lab(r, 'round')))[:8]:
    print('   ', r['arm'], 'round', lab(r, 'round'), 'value', r['value'], '| same ckpt measured by an EI arm round 1:', ei.get(r['ckpt']))
# 2. rows shared between runs (same arm, value, n, round, L, slice)
by = collections.defaultdict(set)
for r in rows:
    if r['arm']:
        by[r['run_id']].add((r['metric'], r['arm'], r['value'], r['n'], lab(r, 'round'), lab(r, 'L'), lab(r, 'slice')))
for a, b in itertools.combinations(sorted(by), 2):
    c = by[a] & by[b]
    if c: print('shared named-arm rows %-17s %-17s %5d  arms e.g. %s' % (a, b, len(c), sorted({k[1] for k in c})[:3]))
# 3. superseded directories backfilled under the same arm name
dup = collections.defaultdict(set)
for r in rows:
    if r['metric'] == 'heldout_greedy_acc' and overall(r) and lab(r, 'round') is not None:
        dup[(r['run_id'], r['arm'], lab(r, 'round'), r['ckpt'], r['data'])].add((r['value'], r['source'].split('artifacts/')[2].split('/')[0] if r['source'].count('artifacts/') > 1 else r['source']))
bad = {k: v for k, v in dup.items() if len({x[0] for x in v}) > 1 and k[0] != 'run4-grpo'}
print('same (run, arm, round, ckpt, data) with two different held-out values (not GRPO):', len(bad), list(bad.items())[:2])
# 4. checker label vs artefact dates
c = collections.defaultdict(collections.Counter)
for r in rows:
    if r.get('backfilled'): c[r['run_id']][lab(r, 'checker')] += 1
print('checker labels by run:', {k: dict(v) for k, v in sorted(c.items())})
