"""review_coep/splits.py -- renaming-class disjointness of this run's evaluation pools (strict106, tb72, the C4 inputs)
against every training file of the models it evaluated: K12 (full arm, old full seeds), K12- (knockout), K12+1 % sigma
(dose), and the ladders' RL targets (data/ladder/rl_targets.jsonl).

Own keys: `ordered` = atoms relabelled by first appearance in the premises-then-conclusion string (premise order
matters); `canon` = the lexicographic minimum over all 24 bijections of {P,Q,R,S} of (sorted premise multiset,
conclusion), which is premise-order invariant (review-auditability-requirements)."""
import gzip, json, os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import lean4

BIG = os.path.expanduser('~/review/coep_big/train')
PERMS = [dict(zip('PQRS', p)) for p in itertools.permutations('PQRS')]


def rename(f, m):
    if f[0] == 'a':
        return ('a', m[f[1]])
    if f[0] == 'bot':
        return f
    if f[0] == 'not':
        return ('not', rename(f[1], m))
    return (f[0], rename(f[1], m), rename(f[2], m))


def s(f):
    return lean4.lean_f(f)


def keys(prompt):
    prem, concl = lean4.sequent(prompt)
    canon = min((tuple(sorted(s(rename(p, m)) for p in prem)), s(rename(concl, m))) for m in PERMS)
    order = []
    for t in ' '.join([s(p) for p in prem] + [s(concl)]):
        if t in 'PQRS' and t not in order:
            order.append(t)
    m = {a: 'PQRS'[i] for i, a in enumerate(order)}
    for a in 'PQRS':
        m.setdefault(a, a)
    ordered = (tuple(s(rename(p, m)) for p in prem), s(rename(concl, m)))
    return canon, ordered


def load_train(path):
    op = gzip.open if path.endswith('.gz') else open
    out = []
    with op(path, 'rt') as f:
        for l in f:
            r = json.loads(l)
            out.append((r.get('name'), r['prompt']))
    return out


TRAIN = {'K12 (full, old full)': f'{BIG}/train_k12.jsonl.gz', "K12- (knockout)": f'{BIG}/train_k12ko.jsonl.gz',
         'K12+1% sigma (dose)': f'{BIG}/train_k12dose1.jsonl.gz', 'ladder rl_targets': P('data/ladder/rl_targets.jsonl')}
EVALP = {'strict106': P('data/coe_paper/strict106.jsonl'), 'tb72': P('data/coe_paper/tb72.jsonl'),
         'c4_ko_s1': P('data/coe_paper/c4_ko_s1.jsonl'), 'c4_ko_s3': P('data/coe_paper/c4_ko_s3.jsonl')}
ev = {}
for e, p in EVALP.items():
    ev[e] = [(r['name'], r['prompt']) for r in jl(p)]
evk = {e: [(n, *keys(pr)) for n, pr in rs] for e, rs in ev.items()}
# C4 inputs must be strict members; tb72 file == textbook72 names of read1054
s106 = set(strict_names())
print('C4 inputs strict members:', all(n in s106 for e in ('c4_ko_s1', 'c4_ko_s3') for n, _ in ev[e]))
tbn = [r['name'] for r in jl(P('data/coe/read1054.jsonl')) if r['set'] == 'tb72']
print('tb72.jsonl == read1054 textbook72 rows:', sorted(tbn) == sorted(n for n, _ in ev['tb72']), len(tbn))
out = {}
for t, p in TRAIN.items():
    tr = load_train(p)
    kc, ko = {}, {}
    for n, pr in tr:
        c, o = keys(pr)
        kc.setdefault(c, n); ko.setdefault(o, n)
    print(f'== {t}: {len(tr)} records, {len(kc)} canonical classes, {len(ko)} ordered classes')
    for e, rows in evk.items():
        hc = [(n, kc[c]) for n, c, o in rows if c in kc]
        ho = [(n, ko[o]) for n, c, o in rows if o in ko]
        print(f'   vs {e:9s} ({len(rows):3d}): canonical hits {len(hc)}  ordered hits {len(ho)}  {hc[:4]}')
        out[f'{t} | {e}'] = dict(canonical=hc, ordered=ho)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_splits.json'), 'w'), indent=1)
