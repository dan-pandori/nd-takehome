#!/usr/bin/env python3
"""capability-defs Part 3, definition N2 (schema acquisition): per-round family curves from the EI ladders' own records.

  python3 capability_defs/analysis/cd_schema.py [--cap 12]  -> out/schema_c<cap>.json + printed table

rl_targets (trained on): alloc_<r>.json gives cumulative accepted counts; successes of round r = accepted_r -
accepted_{r-1} out of k 32, sampled from the round-(r-1) model (round 1 = pend).  For each of the 19 textbook schema
families (40 targets each) and each round: the share of family targets with >= 1 success in that round, and the mean
per-target success rate (successes / 32).
transfer (never trained on; sampled at k 32 each round): the round each theorem was first solved (found_transfer_16's
`round` field, cap 12; found_transfer_8 at cap 6) -> cumulative share of each family solved by round r.
Family verdict (pre-registered card rule): **created** if the round-1 (pend, k 32) share is <= 0.05 and the share in the
last rounds (mean of the final two rounds) is >= 0.5; **elicited** if round 1 is > 0.05 and the final share >= 0.5.
"""
import argparse, collections, json, os, sys

HOME = os.path.expanduser('~')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def alloc_dirs(cap, s):
    if cap == 12:
        return [f'{HOME}/work/trajectory/artifacts/tj/la_T1_best12_s{s}', f'{HOME}/work/rl-continue/artifacts/rc/la_T1_best12_s{s}']
    return [f'{HOME}/work/trajectory-cap6/artifacts/tj6/la_T1_best6_s{s}', f'{HOME}/work/rl-continue-cap6/artifacts/rc6/la_T1_best6_s{s}']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, default=12)
    a = ap.parse_args()
    tg = {r['name']: r for r in rj(f'{ROOT}/data/ladder/rl_targets.jsonl')}
    tr = {r['name']: r for r in rj(f'{ROOT}/data/ladder/transfer.jsonl')}
    fam_t = collections.defaultdict(list); fam_x = collections.defaultdict(list)
    for n, r in tg.items():
        if r.get('schema'):
            fam_t[r['schema']].append(n)
    for n, r in tr.items():
        if r.get('schema'):
            fam_x[r['schema']].append(n)
    out = {'families': sorted(fam_t), 'targets': {}, 'transfer': {}, 'verdict': {}}
    for s in (0, 1, 2):
        acc = {}
        for d in alloc_dirs(a.cap, s):
            for r in range(1, 17):
                f = f'{d}/alloc_{r}.json'
                if os.path.exists(f):
                    acc[r] = json.load(open(f))['accepted']
        rounds = sorted(acc)
        per = {}
        for f, mem in fam_t.items():
            share, rate = [], []
            for r in rounds:
                prev = acc.get(r - 1, {})
                succ = [acc[r].get(n, 0) - prev.get(n, 0) for n in mem]
                share.append(sum(1 for x in succ if x > 0) / len(mem)); rate.append(sum(succ) / (32 * len(mem)))
            per[f] = {'rounds': rounds, 'share': share, 'rate': rate}
        out['targets'][s] = per
        # transfer: first-found round per theorem
        ft = f'{HOME}/review/rc_data/s{s}/found_transfer_16.jsonl' if a.cap == 12 else f'{HOME}/review/rc6_data/s{s}/found_transfer_16.jsonl'
        first = {}
        if os.path.exists(ft):
            with open(ft) as fh:
                for line in fh:
                    r = json.loads(line)
                    if r['name'] in tr and tr[r['name']].get('schema'):
                        first[r['name']] = min(first.get(r['name'], 99), r.get('round') or 99)
        perx = {}
        for f, mem in fam_x.items():
            perx[f] = [sum(1 for n in mem if first.get(n, 99) <= r) / len(mem) for r in range(1, 17)]
        out['transfer'][s] = perx
        for f in fam_t:
            sh = per[f]['share']
            r1, last = sh[0], sum(sh[-2:]) / 2
            out['verdict'].setdefault(f, {})[s] = ('created' if r1 <= 0.05 and last >= 0.5 else
                                                   'elicited' if last >= 0.5 else 'neither', round(r1, 3), round(last, 3))
    print(f'cap {a.cap}: rl_targets family share with >= 1 success per round (k 32; round 1 = pend), seeds s0 / s1 / s2')
    print(f'{"family":28s} {"r1 (pend)":>16s} {"r8":>16s} {"r16":>16s}   verdicts')
    for f in sorted(fam_t):
        cells = []
        for r in (1, 8, 16):
            v = []
            for s in (0, 1, 2):
                p = out['targets'][s][f]
                v.append(f"{p['share'][p['rounds'].index(r)]:.2f}" if r in p['rounds'] else '  - ')
            cells.append('/'.join(v))
        print(f'{f:28s} {cells[0]:>16s} {cells[1]:>16s} {cells[2]:>16s}   ' + ' '.join(out['verdict'][f][s][0][:4] for s in (0, 1, 2)))
    print('\ntransfer (held out) cumulative share solved by round 1 / 8 / 16, s0 / s1 / s2, families that move most:')
    for f in sorted(fam_x, key=lambda f: -max(out['transfer'][s][f][15] - out['transfer'][s][f][0] for s in (0, 1, 2)))[:8]:
        print(f'  {f:28s} ' + '  '.join('/'.join(f"{out['transfer'][s][f][r - 1]:.2f}" for r in (1, 8, 16)) for s in (0, 1, 2)))
    json.dump(out, open(f'{OUT}/schema_c{a.cap}.json', 'w'))


if __name__ == '__main__':
    main()
