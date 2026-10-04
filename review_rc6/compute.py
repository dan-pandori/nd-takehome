#!/usr/bin/env python3
"""Reviewer (rl-continue-cap6): per-seed compute from the registry rows (record.py) and the round JSONs; own sums."""
import json, glob, os, collections
R = os.path.expanduser('~/review/rl-continue-cap6'); A = f'{R}/artifacts/rc6'
rows = [json.loads(l) for f in sorted(glob.glob(f'{R}/artifacts/rl-continue-cap6/registry/*.jsonl')) for l in open(f) if l.strip()]
M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'lean_checks', 'train_steps', 'train_tokens')
tot = collections.defaultdict(lambda: collections.Counter()); per_round = collections.defaultdict(lambda: collections.Counter())
dup = collections.Counter()
for x in rows:
    if x['metric'] not in M: continue
    host = x['host']; lab = x.get('labels') or {}
    key = (x['metric'], host, lab.get('round'), lab.get('phase'), x.get('source'), x.get('ckpt'))
    dup[key] += 1
    tot[host][x['metric']] += x['value']
    per_round[(host, lab.get('round'), lab.get('phase'))][x['metric']] += x['value']
hosts = sorted(tot)
seed_of = {}
for x in rows:
    if x.get('ckpt') and 'best6_s' in str(x.get('ckpt')): seed_of[x['host']] = str(x['ckpt']).split('best6_s')[1][0]
out = {}
for h in hosts:
    s = seed_of.get(h, '?'); secs = sum(json.load(open(f'{A}/la_T1_best6_s{s}/round_{r}.json'))['secs'] for r in range(9, 17)) if s != '?' else None
    out[f's{s}'] = dict(tot[h]); out[f's{s}']['round_json_secs_r9_16'] = secs
    print(f"s{s} ({h}):", {k: (round(v) if isinstance(v, float) else v) for k, v in tot[h].items()}, 'round-json secs r9-16', round(secs) if secs else None)
print('duplicate keys', sum(1 for v in dup.values() if v > 1))
ph = collections.Counter((k[2] is None) for k in per_round); print('rows without a round label:', {str(k): v for k, v in per_round.items() if k[1] is None})
json.dump(out, open(f'{R}/review_rc6/rv/compute.json', 'w'), indent=1)
