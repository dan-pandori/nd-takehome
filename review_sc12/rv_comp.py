import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
P = {r['prompt']: r for r in rd(f'{B}/data/ladder/transfer_long_rr600.jsonl')}
out = {}
for fn in sorted(glob.glob(f'{B}/artifacts/sc12/lp_rr2/*.jsonl')):
    tag = os.path.basename(fn)[:-6]
    rows = list(rd(fn)); s = json.load(open(fn[:-1]))
    solved = {r['prompt'] for r in rows if r['solved']}
    d = {'solved': len(solved), 'n': len(rows), 'ckpt': s.get('ckpt'), 'batch': s.get('batch'), 'k': s.get('k'),
         'max_steps': s.get('max_steps'), 'max_action': s.get('max_action'), 'max_new': s.get('max_new'), 'trunc_frac': s.get('trunc_frac'),
         'step_cap_frac': (s['env']['env_end'].get('step_cap', 0) / s['n_samples']) if 'env' in s else None, 'temperature': s.get('temperature'), 'seed': s.get('seed')}
    if '__ge17' not in tag:
        bins = collections.Counter(int(P[p]['L_true']) for p in solved if P[p]['source'] == 'gen')
        d['Q'] = sum(bins[L] for L in (13, 14, 15, 16)); d['bins_gen'] = dict(sorted(bins.items()))
        d['textbook_solved'] = sum(1 for p in solved if P[p]['source'] == 'textbook')
    out[tag] = d; print(tag, d)
json.dump(out, open(f'{B}/rv/comparators.json', 'w'), indent=1)
