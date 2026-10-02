"""C1(b)/C2: renaming+premise-order leakage of the 29 survivors (and all 383 sc theorems) against training data.
Own canonicaliser (canon.py). Streams files; full canonicalisation only on shape-matching lines."""
import json, sys, gzip, hashlib, os, re
sys.path.insert(0, os.path.dirname(__file__))
from canon import canon, split_thm, CONN
R = '/home/dan/work/claim-audit/audit/raw/support-curves/'
surv = set(open(R + 'data/sc/falsifier_survivors.txt').read().split())
thms = [json.loads(l) for l in open(R + 'data/sc/theorems.jsonl')]
def shape(s, dedup=False):
    prem, concl = split_thm(s)
    if dedup: prem = sorted(set(prem))
    sh = lambda f: ' '.join('x' if t not in CONN else t for t in f.split())
    return ' , '.join(sorted(sh(p) for p in prem)) + ' |- ' + sh(concl)
def shape_c(s):  # conclusion-only shape
    return shape(s).split(' |- ')[1]
T = {}
for dedup in (False, True):
    for t in thms:
        T.setdefault(dedup, {}).setdefault(shape(t['thm'], dedup), {})[canon(t['thm'], dedup)] = T.get(dedup, {}).get(shape(t['thm'], dedup), {}).get(canon(t['thm'], dedup), []) + [t['name']]
# conclusion-only class for survivors (weaker: same goal up to renaming, any premises)
concl_canon = {canon('|- ' + split_thm(t['thm'])[1]): t['name'] for t in thms if t['name'] in surv}
files = sys.argv[1:]
res = []
for f in files:
    op = gzip.open if f.endswith('.gz') else open
    n = 0; hit = {False: set(), True: set()}; chit = set(); hitlines = 0
    with op(f, 'rt') as fh:
        for l in fh:
            r = json.loads(l); s = r.get('thm') or r.get('prompt')
            if s is None: continue
            n += 1
            for dedup in (False, True):
                d = T[dedup].get(shape(s, dedup))
                if d:
                    c = canon(s, dedup)
                    if c in d: hit[dedup].update(d[c]); hitlines += (not dedup)
            if shape_c(s) and len(concl_canon):
                pass
    md5 = hashlib.md5(open(f, 'rb').read()).hexdigest()
    res.append((os.path.basename(f), md5, n, len(hit[False]), len(hit[False] & surv), len(hit[True] & surv), sorted(hit[True])[:8]))
    print(*res[-1], sep='\t', flush=True)
