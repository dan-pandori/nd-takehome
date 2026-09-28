import sys, os, json, gzip, random, glob, collections
sys.path.insert(0, '.'); sys.path.insert(0, 'review_lp')
import rlean
from lean_tok import LeanTokenizer
tok = LeanTokenizer('lean_seq')
random.seed(11)
A = 'artifacts/lp/'
def sample(fn, key, n_ok, n_rej, dedup=True):
    ok, rej = [], []; seen = set()
    for l in gzip.open(fn, 'rt'):
        d = json.loads(l); k = (d['prompt'], d['lean_text'])
        if k in seen: continue
        seen.add(k)
        (ok if d[key] else rej).append(k)
    return random.sample(ok, min(n_ok, len(ok))), random.sample(rej, min(n_rej, len(rej)))
jobs = []
for arm in 'ABCD':
    o, r = sample(f'{A}t1/dump_{arm}.jsonl.gz', 'lean_ok', 150, 60)
    jobs += [(f'T1_{arm}', k, True) for k in o] + [(f'T1_{arm}', k, False) for k in r]
for fn in sorted(glob.glob(A + 'corpus/*.dump.jsonl.gz')):
    o, r = sample(fn, 'lean', 150, 150)
    nm = 'C1_' + os.path.basename(fn).split('.')[0]
    jobs += [(nm, k, True) for k in o] + [(nm, k, False) for k in r]
for nm, fn in [('C2', A + 'c2/c2_checked.jsonl.gz'), ('C2r', A + 'c2/c2r_checked.jsonl.gz'), ('C3', A + 'c3/c3_checked.jsonl.gz')]:
    o, r = sample(fn, 'lean', 200, 200)
    jobs += [(nm, k, True) for k in o] + [(nm, k, False) for k in r]
srcs = [f'{tok.statement(p)} {t}' for _, (p, t), _ in jobs]
res = rlean.check(srcs)
c = collections.defaultdict(collections.Counter); bad = []
for (nm, k, stored), v in zip(jobs, res):
    c[nm][f'stored_{stored}_mine_{v}'] += 1
    if v != stored: bad.append((nm, k, stored, v))
out = {'per_set': {k: dict(v) for k, v in c.items()}, 'total': len(jobs), 'disagree': len(bad), 'disagree_examples': bad[:20]}
json.dump(out, open('review_lp/relean.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False)[:4000])
