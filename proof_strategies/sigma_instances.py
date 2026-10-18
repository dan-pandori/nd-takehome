#!/usr/bin/env python3
"""Instance-level table of the reductio steps (DN whose double negation the proof built) in a set: kind x route x
position, and the same for the knockout's sigma (coe_sigma, written OR pruned).  Explore / validation helper.
  python3 proof_strategies/sigma_instances.py data/ps/in/train_k12.jsonl.gz > artifacts/ps/explore/sigma_instances_k12.txt
"""
import collections, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from patterns import parse, prune_lines
from strategies import Proof, get_proof, sequent_of_prompt
from coe.coe_sigma import flags, has_sigma

fn = sys.argv[1]
op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
inst = collections.Counter(); rec_kind = collections.Counter(); n = 0; coe = 0; ours = 0; both = 0
for line in op:
    r = json.loads(line); n += 1
    proof = get_proof(r)
    L = prune_lines(parse(proof)); P = Proof(L, sequent_of_prompt(r['prompt']))
    kinds = set()
    for ln in L:
        if ln['rule'] != 'DN':
            continue
        st, sub = P.line_labels(ln)
        if 'contradiction' not in st:
            continue
        k = [x.split('.')[1] for x in sub if x.split('.')[1] in ('free', 'scaffolded', 'neg_goal', 'pointless', 'vacuous')][0]
        rt = ([x.split('route_')[1] for x in sub if 'route_' in x] or ['built_other'])[0]
        pos = 'root' if 'contradiction.root' in sub else 'lemma'
        inst[(k, rt, pos)] += 1; kinds.add(k)
    if kinds:
        ours += 1
        rec_kind[min(kinds, key=['free', 'neg_goal', 'scaffolded', 'pointless', 'vacuous'].index)] += 1
    fl = flags(proof)
    c = bool(fl['w']['sigma_strict'] or fl['w']['sigma_chain'] or fl['p']['sigma_strict'] or fl['p']['sigma_chain'])
    coe += c; both += c and bool(kinds)
print(f'{fn}: {n} records; records with a reductio (ours) {ours}; coe_sigma sigma (written or pruned) {coe}; both {both}')
print('records by their "best" reductio kind (free < neg_goal < scaffolded < pointless < vacuous):', dict(rec_kind))
print('instances (kind, route, position):')
for k, v in sorted(inst.items(), key=lambda x: -x[1]):
    print(f'  {str(k):45s} {v}')
