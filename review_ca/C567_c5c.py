#!/usr/bin/env python3
"""Cross-run pair: cap-12 eventual proofs scored under the same cap-12 checkpoints by trajectory (score/s<S>) and by
trajectory-cap6 (score/rev12_s<S>, tid ev12s<S>:). Max |w1 difference| per checkpoint."""
import json
R = '/home/dan/review/claim-audit/rv/C567_raw'
for s in range(3):
    for ck in ('p1600', 'pend', 'r8'):
        a = {json.loads(l)['tid'][3:]: json.loads(l)['T1.0']['w1'] for l in open(f'{R}/trajectory/artifacts/tj/score/s{s}/s{s}_{ck}.jsonl') if l.startswith('{"tid": "ev:')}
        b = {}
        for l in open(f'{R}/trajectory-cap6/artifacts/tj6/score/rev12_s{s}/s{s}_{ck}.jsonl'):
            r = json.loads(l)
            if r['tid'].startswith(f'ev12s{s}:'): b[r['tid'].split(':', 1)[1]] = r['T1.0']['w1']
        k = set(a) & set(b)
        print(f's{s} {ck:5s} n={len(k)} (traj {len(a)}, cap6-run {len(b)}) max|dw1| {max(abs(a[x] - b[x]) for x in k):.2e}')
