#!/usr/bin/env python3
"""long-pool: per-chunk, per-stage labelling table (entered / labelled by L / no proof / timeouts / mean s) from data/lp/*_ml*.jsonl."""
import json, collections, sys
chunks = sys.argv[1:] or ['g1', 'g2', 'g3', 'g4', 'tb']
print('| chunk | stage (bound / time limit) | entered | labelled (L: n) | no proof → next stage | timeouts (rate) | mean s per theorem |')
print('|---|---|---:|---|---:|---|---:|')
tot = collections.Counter()
for c in chunks:
    for b, t in ((10, 5), (12, 30), (14, 120), (16, 600)):
        rs = [json.loads(l) for l in open(f'data/lp/{c}_ml{b}.jsonl')]
        if not rs: continue
        lab = collections.Counter(r['min_lines_ub'] for r in rs if r['min_lines_ub'] is not None)
        to = sum(1 for r in rs if r['timeout']); nop = sum(1 for r in rs if r['min_lines_ub'] is None and not r['timeout'])
        top = {L: n for L, n in sorted(lab.items()) if L >= b - 1} if b > 10 else {'≤10': sum(lab.values())}
        print(f"| {c} | {b} / {t} s | {len(rs):,} | {', '.join(f'{L}: {n:,}' for L, n in top.items())} | {nop:,} | {to} ({100*to/len(rs):.1f} %) | {sum(r['secs'] for r in rs)/len(rs):.2f} |")
        tot[(b, 'in')] += len(rs); tot[(b, 'to')] += to
print()
print('| stage | entered (all chunks) | timeouts | rate |'); print('|---|---:|---:|---:|')
for b in (10, 12, 14, 16):
    print(f"| bound {b} | {tot[(b,'in')]:,} | {tot[(b,'to')]} | {100*tot[(b,'to')]/tot[(b,'in')]:.1f} % |")
