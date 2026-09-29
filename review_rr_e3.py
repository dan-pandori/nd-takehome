# Reviewer's own reader of every registry row (live .jsonl + backfill .jsonl.gz); E3 filter; row counts.
import json, gzip, glob, os, collections
REG = os.path.expanduser('~/review/results-registry/artifacts/results-registry/registry')
rows = []
for fn in sorted(glob.glob(REG + '/*')):
    op = gzip.open if fn.endswith('.gz') else open
    for l in op(fn, 'rt'):
        if l.strip(): r = json.loads(l); r['_f'] = os.path.basename(fn); rows.append(r)
print('rows', len(rows), 'backfilled', sum(bool(r.get('backfilled')) for r in rows), 'live', sum(not r.get('backfilled') for r in rows))
print('files', len(glob.glob(REG + '/*')), 'backfill files', len(glob.glob(REG + '/backfill_*')))
# exact duplicates
keys = collections.Counter(json.dumps({k: v for k, v in r.items() if k != '_f'}, sort_keys=True) for r in rows)
print('exact duplicate rows (extra copies):', sum(c - 1 for c in keys.values()))
print('run_ids', sorted(collections.Counter(r['run_id'] for r in rows).items()))
lab = lambda r, k: r.get(k) if k in r else (r.get('labels') or {}).get(k)
def q(roles):
    sel = [r for r in rows if r['metric'] == 'heldout_greedy_acc' and r.get('role') in roles
           and lab(r, 'L') is None and lab(r, 'slice') is None]
    by = collections.defaultdict(list)
    for r in sel: by[r['run_id']].append(r)
    return sel, by
for roles in ({'stage1', 'control', 'frozen'}, {'stage1', 'init', 'frozen'}):
    sel, by = q(roles)
    print(sorted(roles), 'rows', len(sel), 'runs', len(by))
    for k, v in sorted(by.items()):
        vals = [r['value'] for r in v]
        print('   %-20s %4d rows %3d ckpts data=%s roles=%s min %.4f max %.4f' % (k, len(v), len({r.get('ckpt') for r in v}),
              sorted({str(r.get('data')) for r in v}), dict(collections.Counter(r['role'] for r in v)), min(vals), max(vals)))
print('roles overall', collections.Counter(r.get('role') for r in rows))
# runs with any heldout_greedy_acc at all, and runs with none
hg = {r['run_id'] for r in rows if r['metric'] == 'heldout_greedy_acc'}
print('runs with no heldout_greedy_acc rows:', sorted({r['run_id'] for r in rows} - hg))
print('checker labels', collections.Counter((r.get('labels') or {}).get('checker') for r in rows if r.get('backfilled')))
json.dump(None, open('/dev/null', 'w'))
import pickle; pickle.dump(rows, open('/tmp/rrrev/rows.pkl', 'wb'))
