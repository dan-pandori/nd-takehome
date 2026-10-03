#!/usr/bin/env python3
"""one line per finished read-out in artifacts/mcts/eval: name, solved/n, wall or budget, GPU util."""
import glob, json, os
for f in sorted(glob.glob('artifacts/mcts/eval/*.json')):
    d = json.load(open(f))
    b = os.path.basename(f)[:-5]
    if b.endswith('__sample'):
        print(f"{b:40s} {d['solved']:4d}/{d['n']:<4d} wall {d['wall_s']:.0f}")
    else:
        print(f"{b:40s} {d['solved']:4d}/{d['n']:<4d} budget {d['budget_s']:.0f} used {d['stats']['wall_s']:.0f} "
              f"util {d['gpu_util_mean'] or 0:.0f} sampled {d['sampled']} dup {d['stats'].get('dup_action', 0)}")
