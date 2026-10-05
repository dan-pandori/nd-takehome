#!/usr/bin/env python3
"""Reviewer: J8 elicitation share by rl-from-ckpt start.  New solves of the ladder from start S at r8 (x0 or x1) that S
fails (0 / 512, x0 + x1); LB_S(t) = log sum over J8's known proofs of the stage-1 bound (b0 - ln 33) at T 0.8 under S
(streamed); pend from J1 (exact 33-base terms where stage 2 scored them).  Share with LB >= ln 2 - ln K (factor-2
margin, as the pre-registration's later protocol) and without margin, K in {777, 2e4, 3.5e6}.
Also: soundness of J8's targets (every target proof appears in some read of that theorem or is a reference)."""
import json, os, sys, glob, gzip, math, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L
LN33 = math.log(33); CD = L.CD
RFC = L.RFC
STARTS = ('p1600', 'p5000', 'p12000', 'p16000')
KS = {'777': 777, '2e4': 2e4, '3.5e6': 3.5e6}
EX = json.load(open(f'{CD}/j8/sets.json'))
BR = json.load(open(f'{L.RV}/review_cd/out_bracket.json'))
def lse2(a, b):
    if a == -math.inf: return b
    if b == -math.inf: return a
    m = max(a, b); return m + math.log(math.exp(a - m) + math.exp(b - m))
def rfc(s, st, x, pool):
    return {r['name']: r['n_ok'] for r in L.rows(f'{RFC}/s{s}_{st}_r8__{pool}_x{x}.jsonl')}
def ctrl(s, st):
    out = set()
    for x in (0, 1):
        for pool in ('tb72', 'h250'):
            p = f'{RFC}/c{s}_{st}_r8__{pool}_x{x}.jsonl'
            if os.path.exists(p):
                out |= {r['name'] for r in L.rows(p) if r['n_ok'] > 0}
    return out
N = L.names()
for s in (0, 1, 2):
    new = {}
    for st in STARTS:
        b0, b1 = L.both(12, s, st, 0), L.both(12, s, st, 1)
        solved = set()
        for x in (0, 1):
            for pool in ('tb72', 'h250'):
                solved |= {n for n, c in rfc(s, st, x, pool).items() if c > 0}
        new[st] = sorted(n for n in solved if b0[n][0] + b1[n][0] == 0)
    # pend -> r8 (trajectory ladder), same rule
    p0, p1 = L.both(12, s, 'pend', 0), L.both(12, s, 'pend', 1)
    r80, r81 = L.both(12, s, 'r8', 0), L.both(12, s, 'r8', 1)
    new['pend'] = sorted(n for n in N if (r80[n][0] + r81[n][0]) > 0 and p0[n][0] + p1[n][0] == 0)
    print(f's{s}: new solves ' + ' '.join(f'{st} {len(v)}' for st, v in new.items()) + '   equal to executor sets: ' +
          ' '.join(f'{st}:{set(EX[str(s)][st]) == set(new[st])}' for st in STARTS))
    # stream J8 scores
    LB = collections.defaultdict(lambda: collections.defaultdict(lambda: -math.inf))
    nrep = collections.Counter()
    for p in sorted(glob.glob(f'{CD}/j8/b1_s{s}_p*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                nrep[r['replay_ok']] += 1
                if not r['replay_ok']: continue
                for lab, v in r['sc'].items():
                    LB[r['name']][lab] = lse2(LB[r['name']][lab], v[2] - LN33)
    print(f'   J8 replay ok {nrep[True]} fail {nrep[False]} ({100 * nrep[False] / max(1, sum(nrep.values())):.2f} %)')
    for st in list(STARTS) + ['pend']:
        ns = new[st]
        if st == 'pend':
            lbs = [BR[str(s)]['LB'][n]['pend'][1] if n in BR[str(s)]['LB'] else -math.inf for n in ns]
        else:
            lbs = [LB[n][f's{s}_{st}'] for n in ns]
        c = ctrl(s, st) if st != 'pend' else {n for x in (0, 1) for n, v in L.both(12, s, 'ctrl8', x).items() if v[0] > 0}
        sh = {k: sum(v >= math.log(2) - math.log(K) for v in lbs) / len(ns) for k, K in KS.items()}
        sh0 = {k: sum(v >= -math.log(K) for v in lbs) / len(ns) for k, K in KS.items()}
        print(f'   {st:7s} n {len(ns):3d}  elicited share (factor 2) ' + ' '.join(f'K{k} {v:.2f}' for k, v in sh.items()) +
              '   (no margin) ' + ' '.join(f'K{k} {v:.2f}' for k, v in sh0.items()) + f'   replay-only control solves {len(c & set(ns))}/{len(ns)}  unscored {sum(v == -math.inf for v in lbs)}')
