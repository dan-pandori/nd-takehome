#!/usr/bin/env python3
"""long-pool: shape table of data/ladder/transfer_long.jsonl per L_true bin (from the minlen label proof and the prompt).
  python3 lp_shape.py data/ladder/transfer_long.jsonl > artifacts/lp/shape.md"""
import json, sys, collections, statistics as st
recs = [json.loads(l) for l in open(sys.argv[1])]
by = collections.defaultdict(list)
for r in recs:
    by[r['L_true']].append(r)
def feats(r):
    lines = [x.strip() for x in r['minlen_proof'].split(';') if x.strip() and x.strip() != 'QED']
    rules = [l.rsplit(':', 1)[1].split()[0] for l in lines]
    depth = max(l.split(':')[0].count('|') for l in lines)
    return rules, depth
print('| L_true | n | gen / textbook | premises (mean) | prompt tokens (median / max) | generated lines (median) | label term size (median, range) | max box depth (median / max) | label proofs using ORE / DN / NEGI / IMPI (%) |')
print('|---|---:|---|---:|---|---:|---|---|---|')
for L in sorted(by):
    rs = by[L]; n = len(rs)
    g = sum(r['source'] == 'gen' for r in rs)
    pt = [len(r['prompt'].split()) - 3 for r in rs]
    gl = [r['gen_lines'] for r in rs if r['gen_lines']]
    ts = [r['label_term_size'] for r in rs]
    F = [feats(r) for r in rs]; dp = [d for _, d in F]
    pct = lambda rule: 100 * sum(rule in ru for ru, _ in F) / n
    print(f"| {L} | {n} | {g} / {n-g} | {st.mean(r['n_prem'] for r in rs):.2f} | {st.median(pt):.0f} / {max(pt)} | {st.median(gl) if gl else '–'} | {st.median(ts):.0f} ({min(ts)}–{max(ts)}) | {st.median(dp):.0f} / {max(dp)} | {pct('ORE'):.0f} / {pct('DN'):.0f} / {pct('NEGI'):.0f} / {pct('IMPI'):.0f} |")
