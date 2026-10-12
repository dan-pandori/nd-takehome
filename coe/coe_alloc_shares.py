#!/usr/bin/env python3
"""create-or-elicit: per-round family training shares from a ladder's alloc_<r>.json files (cumulative tried/accepted).

Per round r: successes on target t in round r = accepted_r - accepted_{r-1} (round 1 = the base's own k 32 sample).
Training share of a family in round r = share of its key-step trained members with >= 1 success in round r.
Cumulative = share with >= 1 success in any round <= r.

  python3 coe/coe_alloc_shares.py --dirs DIR_r1-r8 [DIR_r9-r16] --label s0 [--rounds 16]
"""
import argparse, glob, json, os, sys


def load_allocs(dirs, rounds):
    al = {}
    for r in range(1, rounds + 1):
        for d in dirs:
            fn = os.path.join(d, f'alloc_{r}.json')
            if os.path.exists(fn):
                al[r] = json.load(open(fn))['accepted']
                break
    return al


def shares(al, members, rounds):
    out = []
    prev = {}
    cum = set()
    for r in range(1, rounds + 1):
        if r not in al:
            out.append(None); continue
        acc = al[r]
        succ = {m for m in members if acc.get(m, 0) - prev.get(m, 0) > 0}
        cum |= {m for m in members if acc.get(m, 0) > 0}
        out.append((len(succ) / len(members), len(cum) / len(members)))
        prev = acc
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dirs', nargs='+', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--rounds', type=int, default=16)
    ap.add_argument('--families', default='data/coe/families.json')
    a = ap.parse_args()
    fam = json.load(open(a.families))
    al = load_allocs(a.dirs, a.rounds)
    print(f'## {a.label}: rounds present {sorted(al)}')
    print('| family (key-step trained) | per-round share r1..r16 | cumulative at r8 / r16 | first round share >= 0.5 |')
    print('|---|---|---|---|')
    sets = {f: d['keystep_trained'] for f, d in fam['families'].items() if d['classical']}
    sets['generated classical (σ-covered)'] = [n for n in fam['generated_classical']['rl_targets']['sigma_covered']]
    for f, mem in sets.items():
        sh = shares(al, mem, a.rounds)
        per = ' '.join('.' if x is None else f'{x[0]:.2f}' for x in sh)
        c8 = sh[7][1] if len(sh) > 7 and sh[7] else float('nan')
        c16 = sh[15][1] if len(sh) > 15 and sh[15] else float('nan')
        first = next((i + 1 for i, x in enumerate(sh) if x and x[0] >= 0.5), None)
        print(f'| {f} ({len(mem)}) | {per} | {c8:.2f} / {c16:.2f} | {first} |')


if __name__ == '__main__':
    main()
