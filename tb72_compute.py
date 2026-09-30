#!/usr/bin/env python3
"""Per-checkpoint compute of the textbook72 read-outs, from the results-registry rows state_eval.py wrote
(artifacts/textbook72/registry/*.jsonl).  GPU: one NVIDIA A40.  No training.  -> artifacts/textbook72/compute.tsv"""
import collections, glob, json
M = ('gpu_seconds', 'attempts', 'actions', 'gen_tokens', 'lean_checks')
agg = collections.defaultdict(lambda: collections.Counter())
for f in sorted(glob.glob('artifacts/textbook72/registry/*.jsonl')):
    for l in open(f):
        r = json.loads(l)
        if r.get('metric') in M:
            agg[f"{r['arm']}_s{r['seed']}"][r['metric']] += r['value']
with open('artifacts/textbook72/compute.tsv', 'w') as o:
    o.write('checkpoint\tgpu\t' + '\t'.join(M) + '\ttrain_steps\ttrain_tokens\n')
    for k in sorted(agg):
        o.write(f'{k}\tA40\t' + '\t'.join(f'{agg[k][m]:.1f}' if m == 'gpu_seconds' else str(int(agg[k][m])) for m in M) + '\t0\t0\n')
    tot = sum((agg[k] for k in agg), collections.Counter())
    o.write('total\tA40\t' + '\t'.join(f'{tot[m]:.1f}' if m == 'gpu_seconds' else str(int(tot[m])) for m in M) + '\t0\t0\n')
print(open('artifacts/textbook72/compute.tsv').read())
