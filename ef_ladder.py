#!/usr/bin/env python3
"""Run efficiency: the cumulative ladder — one row per change, each adding one fix to the row above.
Writes artifacts/ef/ladder.json and prints the markdown table that goes into numbers.md."""
import json, os, sys
A = 'artifacts/ef'
LAD = [
    ('base_orig',        'the sampler as it was (`path=base`, batch-wide multinomial, batch 512, `max_new` 512)'),
    ('base_rr',          '+ per-row deterministic RNG (same sampler; makes the two paths row-for-row comparable)'),
    ('r_base',           '+ RoPE table memoised in `model.py` (drops a `pos.max().item()` sync per decode step)'),
    ('r_eos_nc',         '+ the fast decode loop (no per-step `.any()`/`.sum()` sync, preallocated attention mask)'),
    ('r_eos',            '+ batch compaction (finished rows dropped from the batch and from the KV cache)'),
    ('r_eos_mn288',      '+ `max_new` 512 -> 288 (no accepted sample is longer than 255 decoded tokens)'),
    ('r_eos_b4096_mn288', '+ batch 512 -> 4096 (affordable only because of compaction and the cap)'),
    ('r_rec',            '= the recommended configuration, re-run with the Lean gate for the end-to-end number'),
]
DROPPED = [
    ('r_exact', 'per-sequence early stop at a top-level `exact n<k>`', 'r_eos'),
    ('r_goal',  'goal-reached stop: the sampler appends `exact n<k>` when a depth-0 `have` states the goal', 'r_eos'),
]
SWEEP = ['base_rr', 'r_base_b1024', 'r_base_b2048', 'r_base_b4096',
         'r_eos', 'r_eos_b2048', 'r_eos_b4096', 'r_eos_b4096_mn288', 'r_best']
rows = []
for tag, what in LAD:
    f = f'{A}/{tag}.json'
    if not os.path.exists(f):
        continue
    d = json.load(open(f))
    rows.append({'tag': tag, 'what': what, 'batch': d['args']['batch'], 'samples_per_s': d['samples_per_s'],
                 'sample_wall_s': d['sample_wall_s'], 'tokens_mean': d['decoded_tokens_mean'],
                 'tokens_p95': d['decoded_tokens_p95'], 'rowsteps': d['rowsteps'], 'model_steps': d['model_steps'],
                 'peak_alloc_gb': d['peak_alloc_gb'], 'eos_frac': d['frac_rows_with_eos'],
                 'accepted_samples': d.get('accepted_samples'), 'targets_solved': d.get('targets_solved'),
                 'gate_wall_s': d.get('gate_wall_s'), 'end_to_end_s': d.get('end_to_end_s')})
b = rows[0]['samples_per_s'] if rows else 1
prev = None
for r in rows:
    r['cum_speedup'] = round(r['samples_per_s'] / b, 2)
    r['step_speedup'] = round(r['samples_per_s'] / prev, 2) if prev else 1.0
    prev = r['samples_per_s']
json.dump(rows, open(f'{A}/ladder.json', 'w'), indent=1)
print()
print('### measured and dropped (each costs more wall time than it saves in tokens)')
print()
print('| fix | samples/s | vs the row it was added to | decoded tokens mean | accepted samples | targets |')
print('|---|---|---|---|---|---|')
for tag, what, ref in DROPPED:
    if not os.path.exists(f'{A}/{tag}.json'):
        continue
    d = json.load(open(f'{A}/{tag}.json')); r = json.load(open(f'{A}/{ref}.json'))
    print(f"| {what} | {d['samples_per_s']} | {d['samples_per_s'] / r['samples_per_s']:.2f}x "
          f"| {d['decoded_tokens_mean']} (vs {r['decoded_tokens_mean']}) | {d.get('accepted_samples')} "
          f"(vs {r.get('accepted_samples')}) | {d.get('targets_solved')} (vs {r.get('targets_solved')}) |")
print()
print('### batch-size sweep')
print()
print('| config | batch | max_new | samples/s | sampler s | decode steps | row-steps (M) | peak GB |')
print('|---|---|---|---|---|---|---|---|')
for tag in SWEEP:
    if not os.path.exists(f'{A}/{tag}.json'):
        continue
    d = json.load(open(f'{A}/{tag}.json'))
    nm = 'base path' if d['args']['path'] == 'base' else 'fast path (compaction)'
    print(f"| {nm} | {d['args']['batch']} | {d['args']['max_new']} | {d['samples_per_s']} | {d['sample_wall_s']} "
          f"| {d['model_steps']} | {d['rowsteps']/1e6:.2f} | {d['peak_alloc_gb']} |")
print()
print('### cumulative ladder')
print()
cols = [('what', 'change'), ('batch', 'batch'), ('samples_per_s', 'samples/s'), ('step_speedup', 'x this step'),
        ('cum_speedup', 'x cumulative'), ('sample_wall_s', 'sampler s'), ('tokens_mean', 'tokens mean'),
        ('tokens_p95', 'p95'), ('model_steps', 'decode steps'), ('peak_alloc_gb', 'peak GB'),
        ('accepted_samples', 'accepted'), ('targets_solved', 'targets')]
print('| ' + ' | '.join(c[1] for c in cols) + ' |')
print('|' + '|'.join('---' for _ in cols) + '|')
for r in rows:
    print('| ' + ' | '.join('' if r.get(c[0]) is None else str(r.get(c[0])) for c in cols) + ' |')
