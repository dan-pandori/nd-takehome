#!/usr/bin/env python3
"""Reviewer (grpo-state): independent checks of grpo_adv.py.  passk against brute-force enumeration of k-subsets (Chen et
al. 2508.10751 §2.4: A_i = mean over the k-subsets containing i of (max reward - mean pass@k)); unlikely against a
direct transcription of He et al. 2506.02355 §4.1 (rank 0 = most likely, factor 1 - beta (G - rank)/G, zero-advantage
groups skipped); default and distinct by hand.  Run with REPO on sys.path."""
import itertools, math, random, sys, os, json
sys.path.insert(0, os.environ.get('REPO', '.'))
from grpo_adv import group_advantages
rng = random.Random(1)
out = {}
def bf_passk(R, k):
    n = len(R); subs = list(itertools.combinations(range(n), k))
    rbar = sum(max(R[j] for j in s) for s in subs) / len(subs)
    return [sum(max(R[j] for j in s) - rbar for s in subs if i in s) / sum(1 for s in subs if i in s) for i in range(n)]
worst = 0.0; n_cases = 0
for G in (2, 4, 8, 16):
    for k in range(1, G + 1):
        for c in range(G + 1):
            R = [1] * c + [0] * (G - c); rng.shuffle(R)
            a = group_advantages('passk', R, k=k); b = bf_passk(R, k)
            worst = max(worst, max(abs(x - y) for x, y in zip(a, b))); n_cases += 1
            if k == 1:
                d = group_advantages('default', R); worst = max(worst, max(abs(x - y) for x, y in zip(a, d)))
out['passk_vs_bruteforce'] = {'cases': n_cases, 'max_abs_diff': worst}
# pass@4, G 8: which c give all-zero advantages (every 4-subset succeeds <=> c >= 5)
out['passk_k4_G8_zero_groups_c'] = [c for c in range(9) if not any(group_advantages('passk', [1] * c + [0] * (8 - c), k=4))]
def he(R, lp, beta=0.25):
    G = len(R); m = sum(R) / G
    if all(R) or not any(R): return [0.0] * G
    order = sorted(range(G), key=lambda i: -lp[i]); rank = {i: r for r, i in enumerate(order)}
    r = [R[i] * (1 - beta * (G - rank[i]) / G) for i in range(G)]; mu = sum(r) / G
    return [x - mu for x in r]
worst = 0.0
for _ in range(2000):
    G = rng.choice([4, 8, 16]); R = [rng.randint(0, 1) for _ in range(G)]; lp = [rng.uniform(-50, 0) for _ in range(G)]
    a = group_advantages('unlikely', R, logp=lp); b = he(R, lp)
    worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
out['unlikely_vs_transcription_max_abs_diff'] = worst
R = [1, 1, 0, 0, 0, 0, 0, 0]; lp = [-1.0, -9.0, -2, -3, -4, -5, -6, -7]
a = group_advantages('unlikely', R, logp=lp)
out['unlikely_example'] = {'R': R, 'logp': lp, 'adv': [round(x, 4) for x in a],
                           'more_likely_correct_gets_less': a[0] < a[1], 'sum': round(sum(a), 12)}
out['default_example'] = group_advantages('default', [1, 0, 0, 0])
out['distinct_example'] = group_advantages('distinct', [1, 1, 1, 0], novel_keys=['a', 'a', None, None], bonus=0.5)
out['distinct_all_correct_moves'] = any(group_advantages('distinct', [1, 1, 1, 1], novel_keys=['a', None, None, None]))
out['std_passk_example'] = group_advantages('passk', [1, 0, 0, 0, 0, 0, 0, 0], k=4, std=True)
print(json.dumps(out, indent=1)); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adv_check.json'), 'w'), indent=1)
