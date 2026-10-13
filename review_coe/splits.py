#!/usr/bin/env python3
"""Reviewer: renaming-class disjointness between every training file of this run and every evaluation pool it reads,
under the premise-order-invariant key and the order-sensitive key (common.key_inv / key_ord; F is falsum).
Training: K12 (full arm), K12- (knockout), K12^1% (dose), rl_targets (RL targets, all arms), the Phase 3a seed proof.
Evaluation: read1054 (tb72 / h250 / track732), r322, p2/heldout (5,000), heldout1000, transfer_track832, the strict 106 /
original 178 sigma-covered held-out members, the Phase 2 theorem lists."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
HO = {r['name']: r for r in C.rows(f'{RV}/data/ladder/transfer.jsonl')}
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))


def keyset(recs):
    ki, ko = collections.defaultdict(list), collections.defaultdict(list)
    for r in recs:
        pr, co = C.sequent_of(r)
        nm = r.get('name') or r['prompt'][:50]
        ki[C.key_inv(pr, co)].append(nm); ko[C.key_ord(pr, co)].append(nm)
    return ki, ko


R1054 = list(C.rows(f'{RV}/data/coe/read1054.jsonl'))
EVAL = {'tb72': [r for r in R1054 if r['set'] == 'tb72'], 'h250': [r for r in R1054 if r['set'] == 'h250'],
        'track732': [r for r in R1054 if r['set'] == 'track'], 'p2_heldout5000': list(C.rows(f'{RV}/data/p2/heldout.jsonl')),
        'heldout1000': list(C.rows(f'{RV}/data/coe/heldout1000.jsonl')), 'track832': list(C.rows(f'{RV}/data/coe/transfer_track832.jsonl')),
        'strict106': [HO[n] for n in FAM['strict_heldout']], 'orig178': [HO[n] for n in FAM['orig_sigma_heldout']],
        'phase2_lists': [r for r in R1054 if r['name'] in {l.strip() for f in ('phase2_cm_ktrain_s0.txt', 'phase2_cm_ktrain_s1.txt', 'phase2b_posctl_s0.txt')
                                                          for l in open(f'{RV}/data/coe/{f}')}]}
EK = {k: keyset(v) for k, v in EVAL.items()}
print({k: (len(v), len(EK[k][0])) for k, v in EVAL.items()})
# heldout1000 is a subset of p2/heldout?
p2p = {r['prompt'] for r in EVAL['p2_heldout5000']}
print('heldout1000 subset of p2/heldout:', all(r['prompt'] in p2p for r in EVAL['heldout1000']))
TRAIN = {'K12': f'{RV}/data/coe/src/train_k12.jsonl.gz', 'K12-': f'{RV}/data/coe/train_k12ko.jsonl.gz',
         'K12^1%': f'{RV}/data/coe/train_k12dose1.jsonl.gz', 'rl_targets': f'{RV}/data/ladder/rl_targets.jsonl',
         'p3a_seed': f'{RV}/data/coe/phase3a_seed.jsonl'}
res = {}
for tn, tp in TRAIN.items():
    tk = keyset(C.rows(tp))
    res[tn] = {}
    line = []
    for e, (ei, eo) in EK.items():
        hi = sorted(set(tk[0]) & set(ei)); ho = sorted(set(tk[1]) & set(eo))
        res[tn][e] = {'inv': len(hi), 'ord': len(ho), 'inv_names': [ei[k][0] for k in hi][:30]}
        line.append(f'{e} {len(hi)}/{len(ho)}')
    print(f'{tn:10s}: ' + ', '.join(line))
for tn in TRAIN:
    for e in ('strict106', 'orig178', 'tb72', 'h250', 'track732'):
        if res[tn][e]['inv']:
            print(f'   {tn} x {e} (inv key): {res[tn][e]["inv_names"][:12]}')
json.dump(res, open(f'{RV}/review_coe/out_splits.json', 'w'), indent=1)
