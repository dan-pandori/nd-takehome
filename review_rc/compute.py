#!/usr/bin/env python3
"""Reviewer (rl-continue): per-seed / per-round compute from the registry rows (own sums), vs round-JSON secs."""
import json, glob, os, collections
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'
rows = [json.loads(l) for f in sorted(glob.glob(f'{R}/artifacts/rl-continue/registry/*.jsonl')) for l in open(f) if l.strip()]
M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'lean_checks', 'train_steps', 'train_tokens')
lad = collections.defaultdict(collections.Counter); per = collections.defaultdict(collections.Counter); jobs = collections.defaultdict(collections.Counter)
gpus = collections.Counter(); jobsrc = collections.defaultdict(list); seen = collections.Counter()
for x in rows:
    if x['metric'] not in M: continue
    lab = x.get('labels') or {}; s = x.get('seed'); ph = lab.get('phase'); gpus[lab.get('gpu')] += 1
    seen[(x['metric'], s, lab.get('round'), ph, x.get('role'), x.get('source'), lab.get('compute_id'))] += 1
    if ph == 'job':
        jobs[s][x['metric']] += x['value']
        if x['metric'] == 'gpu_seconds': jobsrc[s].append((os.path.basename(str(x.get('source') or x.get('data'))), os.path.basename(str(x.get('ckpt'))), round(x['value'])))
    else:
        lad[s][x['metric']] += x['value']; per[(s, lab.get('round'))][x['metric']] += x['value']
out = {}
for s in (0, 1, 2):
    secs = {r: json.load(open(f'{A}/la_T1_best12_s{s}/round_{r}.json'))['secs'] for r in range(9, 17)}
    gs = {r: per[(s, r)]['gpu_seconds'] for r in range(9, 17)}
    out[s] = dict(ladder={k: round(v) for k, v in lad[s].items()}, reads={k: round(v) for k, v in jobs[s].items()}, json_secs=round(sum(secs.values())),
                  per_round_gpu_s={r: round(v) for r, v in gs.items()}, per_round_json_secs={r: round(v) for r, v in secs.items()})
    print(f"s{s} ladder r9-16: {out[s]['ladder']}  (round-json secs sum {out[s]['json_secs']})")
    print(f"    per-round registry GPU-s {out[s]['per_round_gpu_s']}\n    per-round json secs     {out[s]['per_round_json_secs']}")
    print(f"    reads: {out[s]['reads']}  jobs {sorted(jobsrc[s])}")
print('gpu classes', dict(gpus), '; duplicate keys', sum(v > 1 for v in seen.values()))
tl = sum(out[s]['ladder']['gpu_seconds'] for s in out); tr = sum(out[s]['reads'].get('gpu_seconds', 0) for s in out)
print(f'total ladder GPU-h {tl/3600:.2f}, reads GPU-h {tr/3600:.2f}, sum {(tl+tr)/3600:.2f}')
json.dump(out, open(f'{R}/review_rc/rv/compute.json', 'w'), indent=1)
