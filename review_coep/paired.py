"""review_coep/paired.py -- are C1's standard / doubled reads paired draws?  If they were (same seed, same file), members
with no cut-off attempt in the standard read would get identical n_ok in both reads."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
for tag in [f'ko_s{s}' for s in range(6)] + [f'dose1_s{s}' for s in range(3)] + ['full_s4']:
    a = read_rows(f'{EVAL}/c1_{tag}_std.jsonl.gz'); b = read_rows(f'{EVAL}/c1_{tag}_dbl.jsonl.gz')
    nocut = [n for n in a if not any(x in CUTOFF for x in reasons_list(a[n]))]
    same = sum(1 for n in nocut if a[n]['n_ok'] == b[n]['n_ok'])
    same_reasons = sum(1 for n in nocut if sorted(reasons_list(a[n])) == sorted(reasons_list(b[n])))
    solved_nocut = [n for n in nocut if a[n]['n_ok'] > 0 or b[n]['n_ok'] > 0]
    same_s = sum(1 for n in solved_nocut if a[n]['n_ok'] == b[n]['n_ok'])
    print(f'{tag:9s} members with no cut-off in std: {len(nocut):3d}; identical n_ok std/dbl {same:3d}; identical failure '
          f'multiset {same_reasons:3d}; among those solved in either: {same_s}/{len(solved_nocut)} identical n_ok')
