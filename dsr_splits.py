#!/usr/bin/env python3
"""Overlap of the shared training set with every evaluation pool, and the set's shape table (run ds-rendering).

All four arms train on the SAME 155,000 ND records, so this is one table for the whole run: whatever it says applies
identically to C0, R1, R3 and R2 (that is the point of a rendering experiment).

Two definitions are reported, as the proposal's protocol asks:
  order-sensitive  : the repository's `canon_key` (atoms relabelled by first appearance in the theorem string) --
                     premise ORDER matters, so 'P , Q |- R' and 'Q , P |- R' are different classes
  order-insensitive: the same, after sorting the premises of the (already atom-canonicalised) theorem

  python3 dsr_splits.py --out artifacts/dsr/splits.json
"""
import argparse, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key

TRAIN = 'data/p2/train_depth3_f0_a1.jsonl'
POOLS = [
    ('heldout', 'data/p2/heldout.jsonl'),
    ('targets_depth3', 'data/p2/targets_depth3.jsonl'),
    ('transfer_depth3', 'data/p2/transfer_depth3.jsonl'),
    ('targets_reductio_req', 'data/p2/targets_reductio_req.jsonl'),
    ('r3_1_depth3_req', 'data/r3_1/depth3_req.jsonl'),
    ('r3_1_depth3_req_transfer', 'data/r3_1/depth3_req_transfer.jsonl'),
    ('ladder_rl_targets', 'data/ladder/rl_targets.jsonl'),
    ('ladder_transfer', 'data/ladder/transfer.jsonl'),
    ('takehome_transfer', 'data/transfer.jsonl'),
    ('validation_36', 'targets/validation_36.jsonl'),
]


def unordered(key):
    """premise-order-insensitive form of an atom-canonical theorem key."""
    if '|-' not in key:
        return key
    pre, con = key.split('|-', 1)
    prem = [p.strip() for p in pre.split(' , ') if p.strip()]
    return ' , '.join(sorted(prem)) + ' |- ' + con.strip()


def keys(fn):
    ks, us = set(), set()
    for l in open(fn):
        if not l.strip():
            continue
        r = json.loads(l)
        k = r.get('key') or canon_key(r['thm'].strip())
        ks.add(k); us.add(unordered(k))
    return ks, us


def shape(fn):
    """length / box-depth / rule / premise shape of the training set."""
    n = 0
    L = collections.Counter(); D = collections.Counter(); P = collections.Counter()
    rules = collections.Counter(); proofs_with = collections.Counter()
    ore_box = 0; contra = 0; trivial = 0
    for l in open(fn):
        if not l.strip():
            continue
        r = json.loads(l); n += 1
        L[r['n_lines']] += 1; P[r['n_prem']] += 1
        lines = [x for x in r['proof'].split(' ; ') if x.strip() and x.strip() != 'QED']
        depth = 0; seen = set()
        inbox = []            # depths at which an ORE branch box is open (not tracked exactly; see boxes_in_ore below)
        for x in lines:
            d = x.count('| ')
            depth = max(depth, d)
            rule = x.split(' : ')[1].split()[0]
            rules[rule] += 1; seen.add(rule)
        D[depth] += 1
        for s in seen:
            proofs_with[s] += 1
        # a box strictly inside an ORE branch: an AS at depth >= 2 in a proof whose ORE branch opens at depth 1.
        if 'ORE' in seen and depth >= 2:
            ore_box += 1
    return {'n': n, 'len_hist': dict(sorted(L.items())), 'box_depth_hist': dict(sorted(D.items())),
            'n_prem_hist': dict(sorted(P.items())),
            'rule_lines_per_proof': {k: round(v / n, 4) for k, v in rules.most_common()},
            'share_of_proofs_with_rule': {k: round(v / n, 4) for k, v in proofs_with.most_common()},
            'proofs_with_ORE_and_depth_ge2': ore_box}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/dsr/splits.json')
    a = ap.parse_args()
    tk, tu = keys(TRAIN)
    out = {'train': TRAIN, 'train_records': None, 'train_classes_ordered': len(tk),
           'train_classes_unordered': len(tu), 'overlap': {}}
    for name, fn in POOLS:
        if not os.path.exists(fn):
            out['overlap'][name] = {'missing': fn}
            continue
        pk, pu = keys(fn)
        out['overlap'][name] = {'file': fn, 'pool_classes_ordered': len(pk), 'pool_classes_unordered': len(pu),
                                'shared_ordered': len(tk & pk), 'shared_unordered': len(tu & pu)}
        o = out['overlap'][name]
        print(f'{name:28s} n_classes {len(pk):6d}  shared (order-sensitive) {o["shared_ordered"]:5d}  '
              f'shared (premise-order-insensitive) {o["shared_unordered"]:5d}')
    out['shape'] = shape(TRAIN)
    out['train_records'] = out['shape']['n']
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    print('train classes (ordered / premise-order-insensitive):', len(tk), len(tu))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
