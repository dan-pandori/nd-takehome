#!/usr/bin/env python3
"""capability-defs J9 selection (pre-registered rule, log.md): per seed, the strictest created candidates at r8 —
`cm_recipe_net` on draw x0 in out/part3.json (r8 solves t at k 256 on x0; pend 0 in all >= K_eval-set standard-cap
attempts, i.e. J2 stage B done; no other seed's pend ever solved t; the replay-only control fails t on x0) — ranked by
r8's pass@1 on x0 (ties: name), top 3.  Writes data/cd/j9/s<S>.jsonl (the J2 input rows of those theorems).

  python3 capability_defs/analysis/cd_j9_select.py 0 1 2
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(HERE, 'out')
TOP = 3


def main(seeds):
    P = json.load(open(f'{OUT}/part3.json'))
    T = json.load(open(f'{OUT}/table_c12.json'))
    os.makedirs(f'{ROOT}/data/cd/j9', exist_ok=True)
    for s in seeds:
        cand = P['sets'][f's{s}_r8_x0']['cm_recipe_net']
        rows = {}
        for p in sorted(glob.glob(f'{ROOT}/data/cd/j2/s{s}_*.jsonl')):
            for l in open(p):
                r = json.loads(l)
                rows.setdefault(r['name'], r)
        def p1(n):
            c, k = T['seeds'][str(s)][n]['counts']['r8']['0'][:2]
            return c / k
        ranked = sorted(cand, key=lambda n: (-p1(n), n))
        pick = [n for n in ranked if n in rows][:TOP]
        with open(f'{ROOT}/data/cd/j9/s{s}.jsonl', 'w') as f:
            for n in pick:
                f.write(json.dumps(rows[n]) + '\n')
        print(f's{s}: {len(cand)} candidates; picked ' + ', '.join(f'{n} (r8 pass@1 {p1(n):.3f})' for n in pick))


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]] or [0, 1, 2])
