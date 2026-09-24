"""Reviewer: term size (formula nodes over the pruned proof) beside the line counts, for the
ladder transfer proofs each arm actually wrote."""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib

ROOT = '/home/dan/review/cap-horizon'
out = {}
for d in sorted(glob.glob(f'{ROOT}/artifacts/kh/la_*')) + sorted(glob.glob(f'{ROOT}/artifacts/dsc_inherited/la_*')):
    fn = f'{d}/found_transfer_8.jsonl'
    if not os.path.isdir(d) or not os.path.exists(fn):
        continue
    seen = set()
    ts, pl = [], []
    for r in rvlib.rd(fn):
        k = (r['name'], rvlib.norm_start(r['proof']))
        if k in seen:
            continue
        seen.add(k)
        ts.append(rvlib.term_size(r['proof']))
        pl.append(rvlib.pruned_length(r['proof']))
    out[os.path.basename(d)] = {'distinct_proofs': len(ts),
                                'mean_term_size': round(sum(ts) / len(ts), 2), 'max_term_size': max(ts),
                                'mean_pruned': round(sum(pl) / len(pl), 2), 'max_pruned': max(pl)}
    print(os.path.basename(d), out[os.path.basename(d)])
    sys.stdout.flush()
json.dump(out, open(f'{ROOT}/rv/out_termsize.json', 'w'), indent=1)
