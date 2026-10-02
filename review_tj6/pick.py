#!/usr/bin/env python3
"""Pick re-score targets: per seed, 40 random tids from targets_s (b0) + 4 B-eventual (full marginal); cross: 30 ev12 + 10 other-seed ev6 (b0)."""
import json, random, os
R = os.path.expanduser('~/review/trajectory-cap6'); rng = random.Random(7)
for s in (0, 1, 2):
    T = [json.loads(l) for l in open(f'{R}/artifacts/tj6/targets/targets_s{s}.jsonl')]
    b0 = rng.sample([t['tid'] for t in T], 40); full = rng.sample([t['tid'] for t in T if t['kind'] == 'ev'], 4)
    C = [json.loads(l) for l in open(f'{R}/data/tj6/cross.jsonl')]
    cr = rng.sample([c['tid'] for c in C if c['kind'] == 'ev12'], 30) + rng.sample([c['tid'] for c in C if c['kind'] == 'ev6' and not c['tid'].startswith(f'ev6s{s}')], 10)
    for n, v in (('b0', b0), ('full', full), ('cross', cr)): open(f'{R}/rv6/pick_{n}_s{s}.txt', 'w').write('\n'.join(v) + '\n')
