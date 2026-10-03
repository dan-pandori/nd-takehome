#!/usr/bin/env python3
"""gt_compute.py -- per-arm compute for run guided-tts (AGENT_POLICY: GPU-seconds + GPU type, generated tokens and
attempts/actions, training steps/tokens (none: no training), Lean / environment checks).

Sources: artifacts/gt/analysis.json `jobs` (from each read's summary json: sampling-loop GPU seconds, sampled and
prefill tokens, draws = actions, checker / env seconds) and the registry rows artifacts/guided-tts/registry/*.jsonl
(`lean_checks` = distinct finished texts sent to Lean by lean_gate, per read; the smoke reads and the OOM'd first
best12 s0 structural attempt are excluded by matching the read's --out path and keeping its last row).
  python3 gt_compute.py > artifacts/gt/compute_stdout.txt
"""
import collections, glob, json
A = json.load(open('artifacts/gt/analysis.json'))['jobs']
lean = {}
for fn in sorted(glob.glob('artifacts/guided-tts/registry/*.jsonl')):
    for l in open(fn):
        d = json.loads(l)
        out = (d.get('config') or {}).get('out', '')
        if d['metric'] == 'lean_checks' and out.startswith('artifacts/gt/eval/'):
            lean[out.split('/')[-1]] = d['value']
print('per read: model_s_arm | GPU (sampling loop) s | wall s | sampled tokens M | prefill tokens M | attempts | actions (draws) | step checks (checker calls) | Lean checks (finished texts) | GPU type, batch')
agg = collections.defaultdict(lambda: collections.Counter())
for k, j in sorted(A.items()):
    m, s, arm = k.split('_')
    chk = (j.get('cache_hits') or 0) + (j.get('cache_miss') or 0)
    print(f"{k} | {j['gpu_s']:.0f} | {j['wall_s']:.0f} | {j['sampled_tokens'] / 1e6:.2f} | {j['prefill_tokens'] / 1e6:.1f} | "
          f"{j['attempts']} | {j['draws']} | {chk} | {lean.get(k, 'n/a')} | {j['gpu']}, {j.get('batch')}")
    a = agg[(m, arm)]
    a['gpu_s'] += j['gpu_s']; a['tok'] += j['sampled_tokens']; a['pre'] += j['prefill_tokens']; a['draws'] += j['draws']
    a['lean'] += lean.get(k, 0); a['n'] += 1
print('\nper arm, mean over the 3 model seeds: GPU s | sampled tokens M | prefill tokens M | actions | Lean checks | ratio to plain (GPU s, sampled tokens)')
for (m, arm), a in sorted(agg.items()):
    p = agg[(m, 'plain')]
    print(f"{m} {arm} | {a['gpu_s'] / a['n']:.0f} | {a['tok'] / a['n'] / 1e6:.2f} | {a['pre'] / a['n'] / 1e6:.1f} | {a['draws'] / a['n']:.0f} | "
          f"{a['lean'] / a['n']:.0f} | {a['gpu_s'] / p['gpu_s']:.2f}x, {a['tok'] / p['tok']:.2f}x")
print('training steps / tokens: 0 / 0 in every arm (no training).  Arms compared at matched sampled tokens and matched '
      'wall-clock by construction of the curves; at equal attempts (k 256) every guided arm used > 1.25x plain on GPU s '
      'and sampled tokens (flagged).')
