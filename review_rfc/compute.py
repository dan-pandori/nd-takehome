#!/usr/bin/env python3
"""Reviewer compute per arm from raw round_*.json (ladders: per-round wall secs = 1 GPU each, sampling rows x mean
decoded action length as generated tokens, target + transfer samples as attempts, 600 fine-tune steps x 128 records per
trained round); controls: round secs, 600 steps x 128 per round.  End arm (pend) from trajectory's round files."""
import json, glob, os, collections
R = os.path.expanduser('~/review/rl-from-ckpt/artifacts/rfc'); TJ = os.path.expanduser('~/review/trajectory/artifacts/tj')
def ladder(d):
    t = collections.Counter()
    for f in sorted(glob.glob(f'{d}/round_*.json')):
        r = json.load(open(f)); e = r.get('env', {})
        t['rounds'] += 1; t['secs'] += r['secs']; t['tsamples'] += r.get('target_samples', 0)
        t['gen_tok'] += e.get('rows', 0) * e.get('action_declen_mean', 0); t['prefill_tok'] += e.get('prompt_tokens', 0)
        tr = r.get('mix_rl_records', 0) + r.get('mix_inject_records', 0) > 0
        t['train_steps'] += 600 * tr; t['train_recs'] += 600 * 128 * tr; t['mix_rl'] += r.get('mix_rl_records', 0)
    return t
rows = {}
for d in sorted(glob.glob(f'{R}/la_T1_best12_s?_p*')): rows['L ' + d.split('best12_')[1]] = ladder(d)
for s in (0, 1, 2):
    for d in glob.glob(f'{TJ}/la_T1_best12_s{s}'): rows[f'L s{s}_pend (trajectory)'] = ladder(d)
for d in sorted(glob.glob(f'{R}/rc_best12_s?_p*')):
    t = collections.Counter()
    for f in glob.glob(f'{d}/round_*.json'): r = json.load(open(f)); t['rounds'] += 1; t['secs'] += r['secs']; t['train_steps'] += 600; t['train_recs'] += 600 * 128
    rows['C ' + d.split('best12_')[1]] = t
print('arm | rounds | wall s (1 GPU) | target samples | gen tok (M) | prefill tok (M) | train steps | train recs (M) | RL recs in mixes')
for k, t in rows.items():
    print(f"{k} | {t['rounds']} | {t['secs']:.0f} | {t['tsamples']} | {t['gen_tok']/1e6:.1f} | {t['prefill_tok']/1e6:.0f} | {t['train_steps']} | {t['train_recs']/1e6:.2f} | {t['mix_rl']}")
json.dump({k: dict(v) for k, v in rows.items()}, open(os.path.expanduser('~/review/rl-from-ckpt/review_rfc/rv/compute.json'), 'w'), indent=0)
