#!/usr/bin/env python3
"""The fixed 200-target set of run efficiency (pre-registered): data/ladder/transfer.jsonl restricted to
L_true 7-12, stratified by L_true in pool proportion, random.Random(0).sample inside each bin.
Writes artifacts/ef/targets200.jsonl (deterministic; committed)."""
import json, random, collections, os

def build(src='data/ladder/transfer.jsonl', n=200, lo=7, hi=12, seed=0):
    rows = [json.loads(l) for l in open(src)]
    cand = [r for r in rows if lo <= r['L_true'] <= hi]
    bins = collections.defaultdict(list)
    for r in cand:
        bins[r['L_true']].append(r)
    for L in bins:
        bins[L].sort(key=lambda r: r['name'])
    tot = len(cand)
    quota = {L: int(round(n * len(bins[L]) / tot)) for L in sorted(bins)}
    while sum(quota.values()) > n:                       # trim the biggest bin
        quota[max(quota, key=lambda L: quota[L])] -= 1
    while sum(quota.values()) < n:
        quota[max(quota, key=lambda L: len(bins[L]) - quota[L])] += 1
    out = []
    for L in sorted(bins):
        out += random.Random(seed + L).sample(bins[L], quota[L])
    out.sort(key=lambda r: r['name'])
    return out, quota

if __name__ == '__main__':
    out, quota = build()
    os.makedirs('artifacts/ef', exist_ok=True)
    with open('artifacts/ef/targets200.jsonl', 'w') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print('targets', len(out), 'per L_true', dict(quota))
