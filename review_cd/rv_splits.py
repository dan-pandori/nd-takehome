#!/usr/bin/env python3
"""Reviewer: split disjointness by renaming class.  Canonical key of a sequent = min over the 24 bijections of
{P,Q,R,S} of (sorted premise strings, conclusion string); F is falsum (not an atom).  Every training file this run
trained on (J4 / J6b mixes, the no-DN K12, full K12 for J7) vs every evaluation pool (textbook72, holdout250, the 40
held-out A v ~A, data/p2/heldout.jsonl (J6 greedy), transfer_long2).  Also: J4 demonstrations vs pools, and the
demos.json A16 list vs the mix files' contents."""
import json, os, sys, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L, g4ip
RV = L.RV
PERMS = list(itertools.permutations('PQRS'))
def split(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    toks = prem.split(); out = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: out.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: out.append(' '.join(cur))
    return out, concl.strip()
def key(prompt):
    prem, concl = split(prompt); best = None
    for p in PERMS:
        m = dict(zip('PQRS', p))
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(f(x) for x in prem)), f(concl))
        if best is None or k < best: best = k
    return best
def keys_of(path, field='prompt'):
    out = {}
    for r in L.rows(path):
        out.setdefault(key(r[field]), r.get('name') or r[field][:60])
    return out
EVAL = {'textbook72': f'{RV}/data/bs/textbook72.jsonl', 'holdout250': f'{RV}/data/bs/holdout250.jsonl',
        'lem40': f'{RV}/data/cd/j4/lem_transfer40.jsonl', 'p2_heldout': f'{RV}/data/p2/heldout.jsonl',
        'long2': f'{RV}/data/ladder/transfer_long2.jsonl'}
EK = {k: keys_of(p) for k, p in EVAL.items()}
for k, v in EK.items(): print(f'eval {k}: {len(v)} classes')
TRAIN = {f'mix_{a}': f'{RV}/data/cd/j4/mix_{a}.jsonl' for a in ('A0', 'A4', 'A16', 'C16', 'A16n', 'C16n')}
TRAIN['k12_nodn'] = f'{RV}/data/cd/k12_nodn.jsonl'; TRAIN['k12_full'] = f'{RV}/data/kh/train_k12.jsonl'
res = {}
for tn, tp in TRAIN.items():
    tk = collections.Counter(); n = 0; dn = 0
    for r in L.rows(tp):
        tk[key(r['prompt'])] += 1; n += 1
        dn += ': DN ' in r['proof'] + ' '
    hits = {e: sorted(set(tk) & set(ek)) for e, ek in EK.items()}
    res[tn] = {e: len(h) for e, h in hits.items()}
    print(f'{tn:9s}: {n:6d} records, {len(tk):6d} classes, records with a DN line {dn:6d}; overlaps: ' +
          ', '.join(f'{e} {len(h)}' + (f' {[EK[e][x] for x in h[:3]]}' if h else '') for e, h in hits.items()))
# demos: the 16 / 4 excluded-middle demonstrations and the controls
D = json.load(open(f'{RV}/data/cd/j4/demos.json'))
for arm, d in D.items():
    ks = {key(v['prompt']) if isinstance(v, dict) and 'prompt' in v else None for v in d.values()}
    print(f'demos {arm}: {len(d)} entries; example keys {list(d)[:3]}; overlaps: ' + ', '.join(f'{e} {len(ks & set(ek))}' for e, ek in EK.items()))
# the A16 demos really appear x4 in mix_A16 and mix_A16n; and are not in mix_A0 / C16
def proofs(p): return collections.Counter((r['prompt'], r['proof']) for r in L.rows(p))
M = {a: proofs(TRAIN[f'mix_{a}']) for a in ('A0', 'A4', 'A16', 'C16', 'A16n', 'C16n')}
for arm in ('A4', 'A16', 'C16', 'C16n'):
    d = D[arm]
    pairs = [(v['prompt'], v['proof']) for v in d.values()]
    for mx in ('A0', 'A4', 'A16', 'C16', 'A16n', 'C16n'):
        c = [M[mx][x] for x in pairs]
        if any(c): print(f'  demos {arm} in mix_{mx}: counts {collections.Counter(c)}')
# A16 demo theorems are classical (need DN) and their LEM status
print('A16 demo theorems intuitionistic (should be none):', [k for k, v in D['A16'].items() if g4ip.intuit_provable(v['prompt'])])
print('mix sizes:', {a: sum(M[a].values()) for a in M})
json.dump(res, open(f'{RV}/review_cd/out_splits.json', 'w'), indent=1)
