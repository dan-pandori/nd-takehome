#!/usr/bin/env python3
"""Compute behind every arm of run kalmar-pretrain, from the results-registry rows (AGENT_POLICY: GPU-seconds,
generated tokens, attempts / actions, training steps / tokens, Lean checks).

  hf buckets sync hf://buckets/dan-pandori/nd-rl/registry/kalmar-pretrain/ artifacts/kalmar-pretrain/registry/
  python3 kalmar/compute.py [--reg artifacts/kalmar-pretrain/registry] > artifacts/kalmar/compute_stdout.txt

Arm and seed come from the row's checkpoint (`ckpts/kalmar/stage1_kal{D,C}_s{S}[_step{N}].pt`, ladder checkpoints
`ckpts/kalmar/ladder/la_kal_{ei,frozen}_s{S}_r{R}.pt`, `ckpts/ctl/stage1_best12_s{S}_b1200.pt`) or, for training rows,
from config.out.  Phase: `train` (state_train.py Stage 1), `read` (every evaluation script), `ladder` (state_ladder_ei.py
and its fine-tunes).  Smoke-test rows (outputs under /tmp, smoke names) are dropped.  GPU-seconds of processes that
shared a card each count in full (none did here except the Lean-check beside KAL-C s0's first launch, which recorded
no GPU time).  GPU types: Stage-1 training and greedy / teacher-forced reads on RTX 3090 (community, $0.22/h; the two
early-snapshot reads on A40), sampled reads and the ladder on A40 (secure, $0.59/h).
The control's own Stage-1 compute is best-state's (1,200 A40-seconds, 23,951-24,123 steps; not re-run here).
"""
import argparse, collections, glob, json, os, re

METRICS = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')


def arm_of(r):
    cfg = r.get('config') or {}
    for s in (r.get('ckpt') or '', cfg.get('ckpt') or '', cfg.get('init') or '', cfg.get('out') or '', cfg.get('name') or ''):
        m = re.search(r'stage1_kal([DC])_s(\d)(?:_step(\d+))?', s)
        if m:
            return f'KAL-{m.group(1)}' + (f' snapshot {m.group(3)}' if m.group(3) else ''), int(m.group(2))
        m = re.search(r'la_kal_(ei|frozen)_s(\d)', s)
        if m:
            return f'ladder {m.group(1)}', int(m.group(2))
        m = re.search(r'stage1_best12_s(\d)_b1200', s)
        if m:
            return 'control', int(m.group(1))
    return None, None


def phase_of(r):
    sc = r.get('script') or ''
    cfg = r.get('config') or {}
    if 'state_ladder_ei' in sc or 'ladder' in str(cfg.get('out') or '') or 'mix_' in str(cfg.get('data') or ''):
        return 'ladder'
    if sc.endswith('state_train.py'):
        return 'train'
    return 'read'


def smoke(r):
    cfg = r.get('config') or {}
    blob = json.dumps(cfg)
    return '"/tmp/' in blob or 'smoke' in blob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reg', default='artifacts/kalmar-pretrain/registry')
    ap.add_argument('--out', default='artifacts/kalmar/compute.json')
    a = ap.parse_args()
    tot = collections.defaultdict(collections.Counter)
    skipped = collections.Counter()
    for fn in sorted(glob.glob(f'{a.reg}/*.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            if r.get('metric') not in METRICS:
                continue
            if smoke(r):
                skipped['smoke'] += 1
                continue
            arm, seed = arm_of(r)
            if arm is None:
                skipped['unattributed'] += 1
                continue
            tot[(arm, seed, phase_of(r))][r['metric']] += r['value'] or 0
    out = {f'{k[0]}|s{k[1]}|{k[2]}': dict(v) for k, v in sorted(tot.items())}
    json.dump({'rows': out, 'skipped': dict(skipped)}, open(a.out, 'w'), indent=1)
    print('| arm | seed | phase | GPU-s | gen tokens | attempts | actions | train steps | train tokens | Lean checks |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for (arm, seed, ph), v in sorted(tot.items()):
        print(f"| {arm} | {seed} | {ph} | {v['gpu_seconds']:,.0f} | {v['gen_tokens']:,.0f} | {v['attempts']:,.0f} | "
              f"{v['actions']:,.0f} | {v['train_steps']:,.0f} | {v['train_tokens']:,.0f} | {v['lean_checks']:,.0f} |")
    per_arm = collections.defaultdict(collections.Counter)
    for (arm, seed, ph), v in tot.items():
        per_arm[(arm.split(' snapshot')[0], ph)].update(v)
    print('\nper arm (seeds summed):')
    for (arm, ph), v in sorted(per_arm.items()):
        print(f"  {arm:14s} {ph:6s} GPU-s {v['gpu_seconds']:>12,.0f}  gen tokens {v['gen_tokens']:>16,.0f}  "
              f"train tokens {v['train_tokens']:>16,.0f}  Lean checks {v['lean_checks']:>10,.0f}")
    print('skipped', dict(skipped))


if __name__ == '__main__':
    main()
