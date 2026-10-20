#!/usr/bin/env python3
"""Split disjointness by renaming class (own keys: premise-order-invariant min over 24 atom bijections; and the same with
premises as a set), between every training file and every evaluation pool of the run.

Training: K12-Kalmár (data/kalmar/train_kal_sl.jsonl.gz = the K12 theorems; also checked equal to data/kh/train_k12.jsonl),
the anneal replay sets (subsets of it, regenerated with kalmar/make_replay.py's rule: random.Random(s).sample(range(N), 20000)),
the EI ladder's targets (data/kalmar/ei_targets1000.jsonl: EI trains on their proofs).
Pools: every read set.  Prints counts only (no theorem text).

  python3 review_kal/splits.py -> out/splits.json
"""
import collections, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

D = os.path.join(kc.ROOT, 'data')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def keys(path):
    ki, ks = collections.Counter(), collections.Counter()
    n = 0
    for r in kc.rows(path):
        p, g = kc.sequent(r)
        ki[kc.key_inv(p, g)] += 1
        ks[kc.key_set(p, g)] += 1
        n += 1
    return n, ki, ks


res = {}
tr_n, tr_i, tr_s = keys(os.path.join(D, 'kalmar', 'train_kal_sl.jsonl.gz'))
k12 = [kc.sequent(r) for r in kc.rows(os.path.join(D, 'kh', 'train_k12.jsonl'))]
same = all(kc.sequent(r) == k for r, k in zip(kc.rows(os.path.join(D, 'kalmar', 'train_kal_sl.jsonl.gz')), k12))
res['train_equals_k12_in_order'] = same and len(k12) == tr_n
print('train', tr_n, 'distinct classes inv', len(tr_i), 'set', len(tr_s), 'same theorems as K12 in order:', res['train_equals_k12_in_order'], flush=True)
replay = {s: set(random.Random(s).sample(range(tr_n), 20000)) for s in (0, 1, 2)}
res['replay_sizes'] = {s: len(v) for s, v in replay.items()}
tg_n, tg_i, tg_s = keys(os.path.join(D, 'kalmar', 'ei_targets1000.jsonl'))
pools = {
    'tf1200': 'kalmar/tf1200_kal_sl.jsonl', 'val300': 'kalmar/val300_kal_sl.jsonl', 'holdout250': 'bs/holdout250.jsonl',
    'rr600': 'ladder/transfer_long_rr600.jsonl', 'ge17': 'ladder/transfer_long_ge17.jsonl', 'long2': 'ladder/transfer_long2.jsonl',
    'candidate_v0': 'gt/candidate_v0.jsonl', 'candidate_v1': 'gt/candidate_v1.jsonl', 'batch3': 'gt/batch3.jsonl',
    'hand_proved_14': 'gt/hand_proved_14.jsonl', 'textbook72': 'bs/textbook72.jsonl', 'g1_premises': 'kalmar/g1_premises.jsonl',
    'g2_large': 'kalmar/g2_large.jsonl', 'g3_classical': 'kalmar/g3_classical.jsonl', 'ei_transfer200': 'kalmar/ei_transfer200.jsonl'}
for name, rel in pools.items():
    n, pi, ps = keys(os.path.join(D, rel))
    row = {'n': n,
           'K12/K12-Kalmar_inv': sum(c for k, c in pi.items() if k in tr_i), 'K12/K12-Kalmar_set': sum(c for k, c in ps.items() if k in tr_s),
           'ei_targets_inv': sum(c for k, c in pi.items() if k in tg_i), 'ei_targets_set': sum(c for k, c in ps.items() if k in tg_s)}
    res[name] = row
    print(f'{name:16s}', row, flush=True)
# the EI targets themselves vs K12 (not an evaluation pool, for the record)
res['ei_targets_vs_K12'] = {'n': tg_n, 'inv': sum(c for k, c in tg_i.items() if k in tr_i)}
print('ei_targets vs K12', res['ei_targets_vs_K12'])
json.dump(res, open(os.path.join(OUT, 'splits.json'), 'w'), indent=1)
