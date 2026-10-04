#!/usr/bin/env python3
"""Reviewer: term size (Expr nodes, rlean.SIZE) and line counts of the first proofs of new targets and of r16 group-C proofs."""
import json, os, statistics as st
R = os.path.expanduser('~/review/rl-continue-cap6'); d = json.load(open(f'{R}/review_rc6/rv/recheck.json'))['sizes']
med = lambda v: st.median(v) if v else None
for s in (0, 1, 2):
    a = d[f's{s}_new_tg_first']
    print(f"s{s} new-target first proofs n={len(a)}: L_true median {med([x[1] for x in a])}, lines median {med([x[2] for x in a])} (lines < L_true: {sum(x[2] < x[1] for x in a)}), term size median {med([x[4] for x in a if x[4]])} range {min(x[4] for x in a if x[4])}-{max(x[4] for x in a if x[4])}; written==lines {sum(x[2]==x[3] for x in a)}")
    c = d[f's{s}_C_r16']; byth = {}
    for n, l, z in c: byth.setdefault(n, []).append((l, z))
    print(f"   r16 C proofs n={len(c)} on {len(byth)} theorems: shortest per theorem (lines, size): " + ', '.join(f"{n.split(':')[1][-6:]} {min(v)[0]}/{min(x[1] for x in v)}" for n, v in sorted(byth.items())))
