#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 1: every read-out, solved counts re-derived by Lean.
For each eval file and each target the file marks solved, check stored ND proofs with my own ND -> Lean translator
(rlean.translate, copied from the textbook72 review) until one is accepted; a target counts iff one is.
Also: a target the file marks unsolved must store no proofs.  The prompt is checked against the pool by name.
Held-out greedy (5,000 x 3): every solved row is checked.  Output: recount_evals.json"""
import json, os, sys, collections, math
sys.path.insert(0, os.path.dirname(__file__)); import rlean
W = os.path.expanduser('~/review/compute-match'); E = os.environ.get('RV_E', f'{W}/artifacts/cm/eval')
POOLS = {'tb72': 'data/bs/textbook72.jsonl', 'dev': 'data/bs/dev1108.jsonl', 'h250': 'data/bs/holdout250.jsonl',
         'held': 'data/p2/heldout.jsonl', 'rr600': 'data/ladder/transfer_long_rr600.jsonl', 'long2': 'data/ladder/transfer_long2.jsonl'}
pool = {r: {x['name']: x for x in map(json.loads, open(f'{W}/{p}'))} for r, p in POOLS.items()}
dev58 = {json.loads(l)['name'] for l in open(f'{W}/data/eval_only/textbook72/textbook_dev.jsonl')}
def passk(n, c, k): return 1.0 if n - c < k else 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))
out = {}
for fn in sorted(os.listdir(E)):
    if not fn.endswith('.jsonl') or '.tmp' in fn: continue
    lab, rd = fn[:-6].split('__'); rows = [json.loads(l) for l in open(f'{E}/{fn}')]
    P = pool[rd]; assert len(rows) == len(P), (fn, len(rows), len(P))
    bad_prompt = sum(r['prompt'] != P[r['name']]['prompt'] for r in rows)
    unsolved_with_proofs = sum((not r['solved']) and len(r['proofs']) > 0 for r in rows)
    todo = {r['name']: list(r['proofs']) for r in rows if r['solved']}
    ok = set(); tries = 0; rejected = []
    while todo:
        items = [(n, P[n]['prompt'], pf.pop(0)) for n, pf in todo.items()]
        res = rlean.check([(p, q) for _, p, q in items], rlean.translate)
        tries += len(items)
        for (n, p, q), (a, why) in zip(items, res):
            if a: ok.add(n)
            else: rejected.append((n, why[:120]))
        todo = {n: pf for n, pf in todo.items() if n not in ok and pf}
    d = {'file_solved': sum(r['solved'] for r in rows), 'lean_solved': len(ok), 'n': len(rows), 'lean_checked': tries,
         'first_proof_rejected': len(rejected), 'rejected_examples': rejected[:5], 'bad_prompt': bad_prompt,
         'unsolved_with_proofs': unsolved_with_proofs}
    if rd == 'tb72':
        d['dev58'] = len(ok & dev58); d['train14'] = len(ok - dev58)
    if rd == 'rr600':
        d['Q'] = sum(1 for n in ok if P[n]['source'] == 'gen' and 13 <= P[n]['L_true'] <= 16)
        d['Q_den'] = sum(1 for x in P.values() if x['source'] == 'gen' and 13 <= x['L_true'] <= 16)
    if rd == 'h250':
        d['passk'] = {k: round(sum(passk(r['n_tried'], r['n_ok'], k) for r in rows) / len(rows), 4) for k in (1, 16, 256)}
    if rd == 'held': d['rate'] = len(ok) / len(rows)
    d['n_tried'] = sorted({r['n_tried'] for r in rows})
    out[f'{lab}__{rd}'] = d
    print(lab, rd, {k: v for k, v in d.items() if k != 'rejected_examples'}, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), os.environ.get('RV_OUT', 'recount_evals.json')), 'w'), indent=1)
