#!/usr/bin/env python3
"""round3-run4a: write the targets an EI arm acquired (strict reductio, normalised + pruned; same rule as run4a_analysis.arm)
to data/r3_4a/acq_<tag>.jsonl, the input of the base pass@1e4 run.   usage: python3 r3_4a_acquired.py <tag> [--all]"""
import json, sys
from run4a_analysis import arm, read, A, TARGETS, TRANSFER
tag = sys.argv[1]
T, TR = read(TARGETS), read(TRANSFER)
m = arm(f'{A}/ei_{tag}', T, TR)
names = set(m['acquired_names']) if '--all' not in sys.argv else {t['name'] for t in T}
with open(f'data/r3_4a/acq_{tag}.jsonl', 'w') as f:
    for t in T:
        if t['name'] in names:
            f.write(json.dumps(t) + '\n')
print(tag, 'rounds', m['rounds'], 'acquired', m['acquired'], 'written', len(names))
