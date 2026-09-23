#!/usr/bin/env python3
"""Run efficiency: one line per bench json in artifacts/ef/."""
import json, glob, sys, os
K = ['tag', 'samples_per_s', 'sample_wall_s', 'decoded_tokens_mean', 'decoded_tokens_p95', 'rowsteps',
     'model_steps', 'frac_rows_with_eos', 'stop_eos', 'stop_exact', 'stop_goal', 'peak_alloc_gb',
     'n_texts', 'distinct_checked', 'accepted_samples', 'targets_solved', 'gate_wall_s', 'lean_proc_s', 'end_to_end_s']
rows = []
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else 'artifacts/ef/*.json')):
    if os.path.basename(f) in ('targets200.json',):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if 'samples_per_s' not in d:
        continue
    d['tag'] = d.get('tag', os.path.basename(f)[:-5])
    d['batch'] = d['args']['batch']; d['max_new'] = d['args']['max_new']
    rows.append(d)
hdr = K[:1] + ['batch', 'max_new'] + K[1:]
w = {k: max(len(k), max((len(str(r.get(k, ''))) for r in rows), default=0)) for k in hdr}
print(' | '.join(k.ljust(w[k]) for k in hdr))
print('-|-'.join('-' * w[k] for k in hdr))
for r in sorted(rows, key=lambda r: (r['batch'], r['tag'])):
    print(' | '.join(str(r.get(k, '')).ljust(w[k]) for k in hdr))
