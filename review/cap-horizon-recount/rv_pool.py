"""Reviewer recount 5: the long-proof pool data/kh/pool_long_kh.jsonl."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib
from nd_verify import verify_text

ROOT = '/home/dan/review/cap-horizon'
hist = collections.Counter()
keys = set()
n = 0
d3 = 0
bad_range = 0
for r in rvlib.rd(f'{ROOT}/data/kh/pool_long_kh.jsonl'):
    n += 1
    L = rvlib.pruned_length(r['proof'])
    hist[L] += 1
    if L < 7 or L > 14:
        bad_range += 1
    keys.add(rvlib.renaming_key(r['thm']))
    if n <= 3000 and rvlib.max_box_depth(r['proof']) >= 3:
        d3 += 1
out = {'records': n, 'distinct_renaming_classes': len(keys),
       'pruned_len_hist': dict(sorted(hist.items())), 'out_of_range_7_14': bad_range,
       'depth3_written_in_first_3000': d3}
print(json.dumps(out, indent=1))
json.dump(out, open(f'{ROOT}/rv/out_pool.json', 'w'), indent=1)
