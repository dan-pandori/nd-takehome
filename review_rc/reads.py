#!/usr/bin/env python3
"""Reviewer (rl-continue): rr1316 (k 64) / long2 (k 256) r8 vs r16 per seed, tb72/h250 r8/r12/r16 (x1) solved, per-stratum
cut-off (L_true_lb bins), row consistency, cross-seed union, pend reachability for theorems gained.  Own code."""
import json, os, collections
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'
def load(f): return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
CUT = ('action truncated', 'step cap')
def cut(r): return sum(v for z, v in r['reasons'].items() if any(c in z for c in CUT))
def pr(r): return r['proofs'] if isinstance(r['proofs'], list) else eval(r['proofs'])
out = {}
for pool, k in (('rr1316', 64), ('long2', 256)):
    G = {}
    for s in (0, 1, 2):
        for ck in ('r8', 'r16'):
            d = load(f'{A}/eval/s{s}_{ck}__{pool}_x0.jsonl'); G[(s, ck)] = d
            bad = sum(1 for r in d.values() if r['n_tried'] != k or r['n_ok'] != k - sum(r['reasons'].values()) or r['solved'] != bool(pr(r)))
            bins = collections.defaultdict(lambda: [0, 0, 0])
            for r in d.values():
                b = bins[r['L_true_lb']]; b[0] += bool(pr(r)); b[1] += cut(r); b[2] += r['n_tried']
            o = dict(solved=sum(bool(pr(r)) for r in d.values()), n=len(d), incons=bad, acc=sum(r['n_ok'] for r in d.values()) / sum(r['n_tried'] for r in d.values()),
                     by_L={L: (b[0], round(100 * b[1] / b[2], 3)) for L, b in sorted(bins.items())})
            out[f'{pool}_s{s}_{ck}'] = o
            print(f'{pool} s{s} {ck}: solved {o["solved"]}/{o["n"]} acc {o["acc"]:.3f} incons {bad}; by L_true_lb (solved, cut %) {o["by_L"]}')
        a = {n for n, r in G[(s, 'r8')].items() if pr(r)}; b = {n for n, r in G[(s, 'r16')].items() if pr(r)}
        print(f'   s{s} delta {len(b)-len(a):+d} (gained {len(b-a)}, lost {len(a-b)})')
    for ck in ('r8', 'r16'):
        U = set.union(*[{n for n, r in G[(s, ck)].items() if pr(r)} for s in (0, 1, 2)]); print(f'   {pool} {ck} union over seeds {len(U)}')
for s in (0, 1, 2):
    row = []
    for ck, dirr in (('r8', 'tj_eval'), ('r12', 'eval'), ('r16', 'eval')):
        for p in ('tb72', 'h250'):
            d = load(f'{A}/{dirr}/s{s}_{ck}__{p}_x1.jsonl'); row.append(f'{ck} {p} {sum(bool(r["proofs"]) for r in d.values())}')
    print(f's{s} x1 solved: ' + ', '.join(row))
json.dump(out, open(f'{R}/review_rc/rv/reads.json', 'w'), indent=0)
