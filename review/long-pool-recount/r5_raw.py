"""long-pool review, part 5: raw renaming-class collisions of all labelled >= 11 candidates (before exclusion), my rkey."""
import json, os, sys, glob, gzip, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open('r2_splits.py').read()
exec(src[:src.index('P = {}')])          # parts_of, rkey, sig, skey, W, files helpers
LP = W + '/data/lp'
cand = {}
for c in ['g1', 'g2', 'g3', 'g4', 'tb']:
    for b in (10, 12, 14, 16):
        for l in open(f'{LP}/{c}_ml{b}.jsonl'):
            r = json.loads(l)
            if (r['min_lines_ub'] is not None and r['min_lines_ub'] >= 11) or (b == 16 and r['min_lines_ub'] is None and not r['timeout']):
                pr, cc = parts_of(r); cand.setdefault(rkey(pr, cc), c)
print('distinct candidate classes', len(cand), flush=True)
R = json.load(open('out/r2_splits.json'))
hit = set()
for fn in R['files']:
    fp = fn.replace('~', os.path.expanduser('~'))
    fp = fp if fp.startswith('/') else W + '/' + fp
    op = gzip.open if fp.endswith('.gz') else open
    with op(fp, 'rt') as f:
        for l in f:
            if l.strip():
                pc = parts_of(json.loads(l))
                if pc and rkey(*pc) in cand:
                    hit.add(rkey(*pc))
out = {'candidates': len(cand), 'raw_collisions': len(hit), 'frac': len(hit) / len(cand)}
json.dump(out, open('out/r5_raw.json', 'w')); print(out)
