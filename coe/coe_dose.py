#!/usr/bin/env python3
"""create-or-elicit Phase 3 (only if run): a small-dose pretraining set K12^d -- K12- with a share d of its records replaced by
sigma records drawn from the K12 records the knockout removed.  Per pruned length L, the number of sigma records put back is
proportional to K12's own sigma count at L (so the dose has K12's sigma length mix), and the same number of K12- REFILL
records of length L are taken out (uniformly, seeded), so per-length counts stay those of K12 and K12-.

  python3 coe/coe_dose.py --k12 data/coe/src/train_k12.jsonl.gz --ko data/coe/train_k12ko.jsonl.gz --share 0.01 --out data/coe/train_k12dose1.jsonl.gz
"""
import argparse, collections, gzip, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_assemble import knock
from coe.coe_sigma import flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--k12', required=True)
    ap.add_argument('--ko', required=True)
    ap.add_argument('--share', type=float, required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    sig = collections.defaultdict(list)      # strict sigma records of K12 by length (the knockout removed them)
    for l in gzip.open(a.k12, 'rt'):
        r = json.loads(l)
        fl = flags(r['proof'])
        if fl['w']['sigma_strict'] or fl['p']['sigma_strict']:
            sig[r['n_lines']].append(l if l.endswith('\n') else l + '\n')
    ko = [l for l in gzip.open(a.ko, 'rt')]
    N = len(ko)
    total_sig = sum(len(v) for v in sig.values())
    want = round(a.share * N)
    per = {L: int(round(want * len(v) / total_sig)) for L, v in sig.items()}
    # fix rounding
    while sum(per.values()) != want:
        L = max(per, key=lambda x: len(sig[x]))
        per[L] += 1 if sum(per.values()) < want else -1
    refill_idx = collections.defaultdict(list)
    for i, l in enumerate(ko):
        r = json.loads(l)
        if r.get('coe_refill'):
            refill_idx[r['n_lines']].append(i)
    drop = set()
    add = []
    for L, k in sorted(per.items()):
        assert len(refill_idx[L]) >= k, (L, k, len(refill_idx[L]))
        drop.update(rng.sample(refill_idx[L], k))
        for l in rng.sample(sig[L], k):
            r = json.loads(l); r['coe_dose'] = True
            add.append(json.dumps(r) + '\n')
    out = [l for i, l in enumerate(ko) if i not in drop] + add
    rng.shuffle(out)
    assert len(out) == N
    with gzip.open(a.out, 'wt') as f:
        f.writelines(out)
    n_sig = sum(1 for l in out if knock(json.loads(l)['proof'])[0])
    rep = {'out': a.out, 'records': len(out), 'share': a.share, 'sigma_records_added': len(add), 'per_length_added': per,
           'refill_records_removed': len(drop), 'records_with_sigma_plus': n_sig, 'sigma_share': n_sig / len(out)}
    json.dump(rep, open(a.out.replace('.jsonl.gz', '') + '_report.json', 'w'), indent=1)
    print(rep)


if __name__ == '__main__':
    main()
