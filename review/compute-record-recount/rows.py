"""Reviewer (compute-record): list the compute rows by process, and compare per-process summed gpu_seconds with the
job wall-clock from walls.jsonl (matched by the row timestamps falling inside [t0, t1])."""
import json, glob, collections, sys, os, datetime
A = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/review/compute-record/artifacts/compute-record')
rows = [json.loads(l) for f in sorted(glob.glob(f'{A}/registry/*.jsonl')) for l in open(f)]
walls = [json.loads(l) for l in open(f'{A}/gpu/walls.jsonl')]
def ts(u): return datetime.datetime.strptime(u, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
comp = [r for r in rows if 'compute_id' in (r.get('labels') or {})]
print('rows', len(rows), 'compute rows', len(comp))
byjob = collections.defaultdict(list)
for r in comp:
    t = ts(r['utc'])
    j = [w['job'] for w in walls if w['t0'] - 1 <= t <= w['t1'] + 1]
    byjob[j[0] if j else '?'].append(r)
out = {}
for w in walls:
    rs = byjob.get(w['job'], [])
    blocks = collections.OrderedDict()
    for r in rs:
        L = r['labels']; b = blocks.setdefault(L['compute_id'], {'script': r.get('script'), 'phase': L.get('phase'), 'round': L.get('round'),
                                                                   'device': L.get('device'), 'gpu': L.get('gpu'), 'status': L.get('status'), 'arm': r.get('arm'), 'seed': r.get('seed')})
        b[r['metric']] = r['value']
        if r['metric'] == 'lean_checks': b['lean_s'] = L.get('lean_s')
    gs = sum(b.get('gpu_seconds', 0) for b in blocks.values() if b['device'] == 'cuda')
    wall = w['t1'] - w['t0']
    out[w['job']] = {'wall': round(wall, 2), 'sum_gpu_seconds': round(gs, 2), 'ratio': round(gs / wall, 4) if wall else None, 'blocks': list(blocks.values())}
    print(f"\n== {w['job']}  wall {wall:.1f}s  sum gpu_seconds {gs:.1f}  ratio {gs / wall:.4f}  rc {w['rc']}")
    for b in blocks.values():
        print('   ', {k: v for k, v in b.items() if v is not None})
print('\nunmatched', len(byjob.get('?', [])))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rows.json'), 'w'), indent=1)
