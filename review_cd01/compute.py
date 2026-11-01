#!/usr/bin/env python3
"""Reviewer (coe-dose01): per-ladder compute totals from the registry (via out/flops.json, built by flops.py) and the
1.25x check against the 1 % arm's mean.  Stage-1 GPU-s from stage1 rows; read jobs from 'job'/'read' rows."""
import json, glob, collections, statistics as st
W = '/home/dan/work'
F = json.load(open(f'{W}/coe-dose01/review_cd01/out/flops.json'))
keys = ['gen_sample', 'gen_eval', 'prefill', 'ft_tokens', 'ft_steps', 'attempts', 'gpu_s_sample', 'gpu_s_eval', 'gpu_s_ft', 'lean_sample', 'lean_eval']
tot = {}
for lad, o in F.items():
    rr = [r for r in o['rows'] if (lad != 'la_ko_s1' or r['round'] >= 25)]
    tot[lad] = {k: sum((r[k] or 0) for r in rr) for k in keys}
    tot[lad]['rounds'] = len(rr)
    tot[lad]['gpu_s_total'] = tot[lad]['gpu_s_sample'] + tot[lad]['gpu_s_eval'] + tot[lad]['gpu_s_ft']
    tot[lad]['secs_roundfiles'] = sum(r['secs'] or 0 for r in rr)
ref = {k: st.mean(tot[f'la_dose1_s{S}'][k] for S in range(3)) for k in keys + ['gpu_s_total']}
print(f"{'ladder':14s} " + ' '.join(f'{k:>13s}' for k in keys + ['gpu_s_total']))
for lad, t in tot.items():
    print(f"{lad:14s} " + ' '.join(f'{t[k]:13.4g}' for k in keys + ['gpu_s_total']))
print('ratios dose01 / mean(1 %):')
flags = []
for S in range(3):
    lad = f'la_dose01_s{S}'
    rat = {k: tot[lad][k] / ref[k] if ref[k] else None for k in keys + ['gpu_s_total']}
    print(f'  {lad}: ' + ' '.join(f'{k} {v:.3f}' for k, v in rat.items() if v is not None))
    flags += [(lad, k, round(v, 3)) for k, v in rat.items() if v is not None and (v > 1.25 or v < 0.8)]
print('outside 0.8-1.25x:', flags)
# stage 1 and read jobs
rows = []
for f in sorted(glob.glob(f'{W}/coe-dose01/artifacts/coe-dose01/registry/*.jsonl')):
    rows += [json.loads(l) for l in open(f)]
s1 = [(r['seed'], r['metric'], r['value'], (r.get('labels') or {}).get('gpu')) for r in rows if r.get('role') == 'stage1' and (r.get('labels') or {}).get('phase') == 'job']
print('stage1 job rows:', s1)
jobs = collections.defaultdict(dict)
for r in rows:
    lab = r.get('labels') or {}
    if lab.get('phase') in ('job', 'read') and r.get('role') != 'stage1':
        k = (r.get('arm'), r.get('ckpt') or (r.get('config') or {}).get('ckpt'), lab.get('phase'), (r.get('config') or {}).get('out') or (r.get('config') or {}).get('summary'), r.get('utc'))
        jobs[k][r['metric']] = r['value']
for k, v in sorted(jobs.items(), key=lambda z: str(z[0][4])):
    print('job', k, {m: (round(x) if isinstance(x, float) else x) for m, x in v.items()})
json.dump(dict(totals=tot, ref_mean_1pct=ref, flags=flags), open(f'{W}/coe-dose01/review_cd01/out/compute.json', 'w'), indent=1)
