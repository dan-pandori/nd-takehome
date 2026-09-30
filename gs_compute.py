#!/usr/bin/env python3
"""grpo-state: per-arm compute table from the results-registry rows (record.phase compute rows).
  python3 gs_compute.py artifacts/grpo-state/registry     -> markdown table on stdout"""
import collections, glob, json, sys
M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')
t = collections.defaultdict(float); ph = collections.defaultdict(float)
for fn in sorted(glob.glob(f'{sys.argv[1]}/*.jsonl')):
    for l in open(fn):
        r = json.loads(l)
        if r['metric'] in M:
            t[(r.get('arm'), r['metric'])] += r['value']
            if r['metric'] == 'gpu_seconds':
                ph[(r.get('arm'), r.get('phase') or (r.get('labels') or {}).get('phase'))] += r['value']
print('| arm | ' + ' | '.join(M) + ' | gpu_s by phase |'); print('|---' * (len(M) + 2) + '|')
for a in sorted({k[0] for k in t}, key=str):
    bp = ', '.join(f'{p} {v:.0f}' for (aa, p), v in sorted(ph.items(), key=str) if aa == a)
    print(f'| {a} | ' + ' | '.join(f'{t[(a, m)]:,.0f}' for m in M) + f' | {bp} |')
