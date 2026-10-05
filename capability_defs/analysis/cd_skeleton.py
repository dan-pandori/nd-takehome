#!/usr/bin/env python3
"""capability-defs Part 3, definition N1 (novelty relative to the pretraining data): proof skeletons.

  python3 capability_defs/analysis/cd_skeleton.py   -> out/skeleton.json + printed summary

Skeleton of an ND proof = the sequence of (box depth, rule, citation offsets) per line; formulas, atoms and absolute
line numbers are abstracted away (a citation is stored as the distance back to the cited line).  Rules: PR AS ORI1/2
(as ORI) IMPI IMPE ORE ANDI ANDE1/2 (as ANDE) R NEGE NEGI DN BOTE ...
Index: every skeleton in K12 (`train_k12.jsonl`, 155,000) and in the cap-6 set (`data/p2/train_depth3_f0_a1.jsonl` if
present).  For every theorem of tb72 + h250 and each cap-12 seed: the share of RL's known accepted proofs (r8 / r16
reads, x0 / x1) whose skeleton occurs in K12, and whether *any* known proof (any model) has an in-data skeleton.
**Skeleton-novel theorem** (seed s, RL ckpt R): R solves t and none of R's accepted proofs of t has a K12 skeleton.
"""
import json, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
LINE = re.compile(r'N(\d+)\s+((?:\|\s*)*)(.*?)\s*:\s*([A-Z]+)(\d*)\s*((?:N\d+\s*)*)$')


def skeleton(proof):
    parts = [p.strip() for p in proof.split(';')]
    sk = []
    for p in parts:
        if not p or p == 'QED':
            continue
        m = LINE.match(p)
        if not m:
            return None
        num = int(m.group(1)); depth = m.group(2).count('|'); rule = m.group(4)
        refs = [int(x[1:]) for x in m.group(6).split()] if m.group(6).strip() else []
        sk.append((depth, rule, tuple(num - r for r in refs)))
    return tuple(sk)


def main():
    idx = set(); n = bad = 0
    for path in (os.path.expanduser('~/work/best-state/data/kh/train_k12.jsonl'),):
        for line in open(path):
            r = json.loads(line); n += 1
            sk = skeleton(r['proof'])
            if sk is None:
                bad += 1; continue
            idx.add(sk)
    print(f'K12: {n} records, {len(idx)} distinct skeletons ({bad} unparsed)')
    names = R.all_names()
    res = {}
    for s in R.SEEDS:
        for ck, xs in (('r8', (0, 1)), ('r16', (0, 1)), ('pend', (0, 1))):
            novel, solved, share = [], 0, []
            for nm in names:
                proofs = set()
                for x in xs:
                    for pool in R.POOLS:
                        d = R.read(12, s, ck, pool, x)
                        if d and nm in d:
                            proofs.update(d[nm][2])
                if not proofs:
                    continue
                solved += 1
                sks = [skeleton(p) for p in proofs]
                ind = [sk in idx for sk in sks if sk is not None]
                share.append(sum(ind) / len(ind) if ind else 0)
                if ind and not any(ind):
                    novel.append(nm)
            res[f's{s}_{ck}'] = {'novel': novel, 'solved': solved}
            print(f's{s} {ck:4s}: solves {solved}; theorems where none of its proofs has a K12 skeleton: {len(novel)}; '
                  f'mean share of its proofs with a K12 skeleton {sum(share) / max(1, len(share)):.3f}')
    json.dump(res, open(f'{OUT}/skeleton.json', 'w'))


if __name__ == '__main__':
    main()
