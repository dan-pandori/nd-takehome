#!/usr/bin/env python3
"""Reviewer: GRPO mechanics (E6) and compute (E7) from steps.jsonl / round_*.json (own code)."""
import json, os, glob, statistics
R = os.path.expanduser('~/review/grpo-best/artifacts/gb')
out = {}
for d in sorted(glob.glob(f'{R}/gb_*_s[012]')):
    name = os.path.basename(d)
    st = [json.loads(l) for l in open(f'{d}/steps.jsonl')]
    rounds = {}
    for f in glob.glob(f'{d}/round_*.json'):
        r = json.load(open(f)); rounds[r['round']] = r
    # secs is cumulative within a process; detect resets (resume) and sum per-process maxima
    segs, prev, tot = [], 0, 0.0
    for s in st:
        if s['secs'] < prev: tot += prev
        prev = s['secs']
    tot += prev
    pre = sum(json.loads(l)['secs'] for f in glob.glob(f'{d}/steps_before_resume_*.jsonl') for l in [open(f).readlines()[-1]]) if glob.glob(f'{d}/steps_before_resume_*.jsonl') else 0
    v = [s['frac_groups_with_variance'] for s in st]
    r1 = [s['mean_reward'] for s in st[:5]]; rl = [s['mean_reward'] for s in st[-5:]]
    o = {'steps': len(st), 'last_round': max(rounds) if rounds else None,
         'secs_steps_cum': tot, 'secs_round_last': rounds[max(rounds)]['secs'] if rounds else None,
         'secs_before_resume_logs': pre,
         'sample_judge_s': sum(s['sample_judge_s'] for s in st), 'update_s': sum(s['update_s'] for s in st),
         'train_tokens': sum(s['update_tokens'] for s in st), 'update_pairs': sum(s['update_pairs'] for s in st),
         'actions': sum(s['actions'] for s in st), 'samples': st[-1]['samples'],
         'var_mean': statistics.mean(v), 'var_first': v[0], 'var_last': v[-1],
         'allfail_mean': statistics.mean(s['frac_groups_all_fail'] for s in st),
         'reward_first': st[0]['mean_reward'], 'reward_last': st[-1]['mean_reward'],
         'reward_first5': statistics.mean(r1), 'reward_last5': statistics.mean(rl),
         'peak_alloc_gb': max(s['peak_alloc_gb'] for s in st),
         'targets_cum': {k: rounds[k]['targets_cum']['solved'] for k in sorted(rounds)},
         'heldout_greedy': {k: rounds[k]['heldout_greedy']['rate'] for k in sorted(rounds) if rounds[k].get('heldout_greedy')},
         'var_by_round': {k: rounds[k]['frac_groups_with_variance_mean'] for k in sorted(rounds)}}
    out[name] = o
    print(f"{name:17s} steps {o['steps']:3d} rnd {o['last_round']} secs(cum,steps) {o['secs_steps_cum']:8.0f} secs(round) {o['secs_round_last'] or 0:8.0f} "
          f"train_tok {o['train_tokens']/1e6:6.1f}M actions {o['actions']/1e6:5.1f}M var {o['var_mean']:.3f} ({o['var_first']:.2f}->{o['var_last']:.2f}) "
          f"reward {o['reward_first']:.3f}->{o['reward_last']:.3f} peak {o['peak_alloc_gb']:.1f}GB tgt_cum {list(o['targets_cum'].values())[-1] if o['targets_cum'] else None} "
          f"held {o['heldout_greedy']}")
json.dump(out, open(os.path.expanduser('~/review/grpo-best/review_gb/compute.json'), 'w'), indent=0)
