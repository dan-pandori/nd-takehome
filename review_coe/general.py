#!/usr/bin/env python3
"""Reviewer recount of E1 / E6: general ability, knockout vs full (and 1 % dose) models.
  * held-out greedy (data/p2/heldout.jsonl, 5,000; T 0, 256 tokens / 48 steps): overall, on theorems whose reference proof
    has no sigma (DN on NEGI) and no sigma+ (own detector);
  * holdout250 / textbook72 (dev58, train14) pass@256 at pend and r16 (x0; old seeds' r16 only exists as x1 on h250 / tb72),
    and holdout250 restricted to non-classical (G4ip-provable) theorems for E6.
Old full seeds: trajectory's heldout_best12_s<S>_b1200.jsonl, s<S>_pend__{h250,tb72}_x0/x1, rl-continue's s<S>_r16__*_x1."""
import json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
EV = f'{RV}/artifacts/coe/eval'
TJ = os.path.expanduser('~/work/trajectory/artifacts/tj/eval')
RC = os.path.expanduser('~/work/rl-continue/artifacts/rc/eval')
P2 = list(C.rows(f'{RV}/data/p2/heldout.jsonl'))
sig = {r['prompt']: C.sigma_flags(r['proof']) for r in P2}
nosig = {p for p, f in sig.items() if not f['sigma']}
nosp = {p for p, f in sig.items() if not f['sigma_plus']}
print(f'p2/heldout: {len(P2)} theorems; reference proof with sigma {len(P2)-len(nosig)}, with sigma+ {len(P2)-len(nosp)}')
R1054 = list(C.rows(f'{RV}/data/coe/read1054.jsonl'))
H250 = {r['prompt'] for r in R1054 if r['set'] == 'h250'}
TB = {r['prompt'] for r in R1054 if r['set'] == 'tb72'}
tb_dev = {r['prompt'] for r in C.rows(f'{RV}/data/eval_only/textbook72/textbook_dev.jsonl')}
H250_nc = set()
for p in H250:
    pr, co = C.split_prompt(p)
    if C.intuit(pr, co):
        H250_nc.add(p)
print(f'holdout250: {len(H250)} ({len(H250_nc)} intuitionistic / non-classical); textbook72 {len(TB)} (dev {len(TB & tb_dev)})')


def greedy(path):
    rows = list(C.rows(path))
    ok = {r['prompt']: r['n_ok'] > 0 for r in rows}
    assert len(ok) == 5000, path
    return {'all': sum(ok.values()) / 5000, 'nosig': sum(ok[p] for p in nosig) / len(nosig), 'nosp': sum(ok[p] for p in nosp) / len(nosp),
            'sig': sum(ok[p] for p in ok if p not in nosig) / (5000 - len(nosig))}


def passk(path, S):
    if not os.path.exists(path):
        return None
    rows = {r['prompt']: r['n_ok'] > 0 for r in C.rows(path) if r['prompt'] in S}
    return rows


def frac(rows, S):
    S = [p for p in S if p in rows]
    return sum(rows[p] for p in S) / len(S) if S else None


out = {}
models = [('full', s) for s in range(6)] + [('ko', s) for s in range(6)] + [('dose1', s) for s in range(3)]
for arm, s in models:
    o = {}
    if arm == 'full' and s < 3:
        o['greedy'] = greedy(f'{TJ}/heldout_best12_s{s}_b1200.jsonl')
        for ck, d, x in (('pend', TJ, 'x0'), ('pend', TJ, 'x1'), ('r16', RC, 'x1')):
            h = passk(f'{d}/s{s}_{ck}__h250_{x}.jsonl', H250); t = passk(f'{d}/s{s}_{ck}__tb72_{x}.jsonl', TB)
            if h is not None:
                o[f'{ck}_{x}'] = {'h250': frac(h, H250), 'h250_nc': frac(h, H250_nc), 'tb72': frac(t, TB) if t else None,
                                  'tb_dev': frac(t, TB & tb_dev) if t else None, 'tb_train': frac(t, TB - tb_dev) if t else None}
    else:
        o['greedy'] = greedy(f'{EV}/heldout_{arm}_s{s}.jsonl')
        for ck in ('pend', 'r16'):
            for x in ('x0', 'x1'):
                p = f'{EV}/{ck}_{arm}_s{s}_{x}.jsonl.gz'
                if os.path.exists(p):
                    rows = {r['prompt']: r['n_ok'] > 0 for r in C.rows(p)}
                    o[f'{ck}_{x}'] = {'h250': frac(rows, H250), 'h250_nc': frac(rows, H250_nc), 'tb72': frac(rows, TB),
                                      'tb_dev': frac(rows, TB & tb_dev), 'tb_train': frac(rows, TB - tb_dev)}
    out[f'{arm}_s{s}'] = o
    g = o['greedy']
    print(f'{arm}_s{s:<2d} greedy all {g["all"]:.4f}  no-sigma {g["nosig"]:.4f}  no-sigma+ {g["nosp"]:.4f}  sigma-ref {g["sig"]:.4f} | ' +
          ' | '.join(f'{k} h250 {v["h250"]:.3f} (nc {v["h250_nc"]:.3f}) tb72 {v["tb72"]:.3f} dev {v["tb_dev"]:.3f} tr {v["tb_train"]:.3f}'
                     for k, v in o.items() if k != 'greedy' and v and v.get('tb72') is not None))


def med(xs):
    return statistics.median(xs)


def arm_vals(arm, key, sub, seeds):
    return [out[f'{arm}_s{s}'][key][sub] for s in seeds if key in out[f'{arm}_s{s}'] and out[f'{arm}_s{s}'][key]]


print()
for sub in ('all', 'nosig', 'nosp', 'sig'):
    f = [out[f'full_s{s}']['greedy'][sub] for s in range(6)]; k = [out[f'ko_s{s}']['greedy'][sub] for s in range(6)]
    print(f'greedy {sub:6s}: full mean {statistics.mean(f):.4f} (median {med(f):.4f}) knockout mean {statistics.mean(k):.4f} (median {med(k):.4f}); '
          f'diff of means {100*(statistics.mean(k)-statistics.mean(f)):+.2f} pp; full per seed {[round(x,4) for x in f]}; ko {[round(x,4) for x in k]}')
for key, sub in (('pend_x0', 'h250'), ('pend_x0', 'tb72'), ('pend_x0', 'tb_dev'), ('pend_x0', 'h250_nc'), ('r16_x1', 'h250_nc'), ('r16_x0', 'h250_nc'), ('r16_x1', 'h250'), ('r16_x0', 'h250')):
    f = arm_vals('full', key, sub, range(6)); k = arm_vals('ko', key, sub, range(6)); d = arm_vals('dose1', key, sub, range(3))
    if f and k:
        print(f'{key} {sub:8s}: full {[round(x,3) for x in f]} median {med(f):.3f} | knockout {[round(x,3) for x in k]} median {med(k):.3f} | '
              f'ratio of medians {med(k)/med(f):.3f}, diff (x n) {(med(k)-med(f)):.3f} | dose1 {[round(x,3) for x in d]}')
json.dump(out, open(f'{RV}/review_coe/out_general.json', 'w'), indent=1)
