import sys, os, random, json
sys.argv=['x']
src = open('recheck.py').read().split("run = lambda")[0]
exec(src)
import rlean
rr = rlean.check([(p, rlean.render(p, b)) for p, b in flip_cand], per_file=200)
for (p, b), (o, i, _) in zip(flip_cand, rr):
    if o:
        for idx, d, f, rule, refs in rlean.parse_nd(b):
            if rule in ('ORI1', 'ORI2'): print(' '.join(f), rule); break
