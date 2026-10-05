#!/usr/bin/env python3
"""capability-defs Part 3: created sets under each definition, their noise floors, and the agreement matrix.

  python3 capability_defs/analysis/cd_defs.py [--cap 12]  -> out/defs_c<cap>.json and a printed summary

Comparisons: base = pend_s, RL = r8_s (draw x0 defines, x1 checks) and r16_s (x1 only; cap 12).  Definitions here use
existing files (out/table_c<cap>.json, out/irt_c<cap>*.json); the J1 / J2 / J3 / J4 definitions are added by
cd_defs_pod.py once those jobs are pulled.  Card slugs in brackets.

  eqk     [passk-equal-k]   pend 0 / 256 and RL >= 1 / 256 on the same draw (Yue et al.'s equal-k support test)
  rel     [reliability]     p-hat_pend < 0.05 and p-hat_RL >= 0.5 on the same draw (reliable success, Harding & Sharadin)
  irt     [irt-ability]     DIF+ item (RL success beyond the PT-only 1-D prediction) that pend fails (cd_irt.py)
  spec_ev [tf-proof-prob]   RL solves t and log pi_pend(RL's eventual proof) < -ln K_total (T 0.8): "RL's proof is new"
  spec_ref[tf-proof-prob]   RL solves t and log pi_pend(shortest known proof) < -ln K_total (T 0.8)
  w1_ev   [tf-proof-prob]   RL solves t and the worst step of RL's eventual proof under pend < ln(1 / K_per) per step
  nullbits[bits-over-null]  RL's share of the bits over random init on its eventual proof > 0.5
  schema  [schema-acq]      t belongs to a textbook schema family whose holdout250 instances pend solves at mean
                            pass@256 <= 0.05 while RL solves them at >= 0.5 (family-level verdict, then per member)
"""
import argparse, collections, itertools, json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
# RL compute as base-attempt equivalents (trajectory / rl-continue compute rows; read cost per attempt from
# trajectory's 44 reads per seed: 24,257 / 27,007 / 26,196 GPU-s for 3,792k / 3,627k / 4,157k attempts).
READ_S = {0: 24257 / 3.792e6, 1: 27007 / 3.627e6, 2: 26196 / 4.157e6}
LADDER_S = {'r8': {0: 22350, 1: 24467, 2: 27021}, 'r16': {0: 22350 + 33248, 1: 24467 + 32830, 2: 27021 + 31457}}
N_TARGETS = 4495


def budgets(s, rl):
    kt = LADDER_S[rl][s] / READ_S[s]
    return {'K_total': kt, 'K_per': kt / N_TARGETS, 'k_eval': 256}


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else float('nan')


def draw_counts(rec, ck, x):
    v = rec['counts'].get(ck, {}).get(str(x))
    return v if v else None


def schema_of():
    out = {}
    for f in ('data/ladder/transfer.jsonl',):
        for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', f)):
            r = json.loads(l)
            if r.get('schema'):
                out[r['name']] = r['schema']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, default=12)
    a = ap.parse_args()
    T = json.load(open(f'{OUT}/table_c{a.cap}.json'))
    names = T['names']
    irt = {d: json.load(open(f'{OUT}/irt_c{a.cap}{d}.json')) for d in ('', '_x0', '_x1') if os.path.exists(f'{OUT}/irt_c{a.cap}{d}.json')}
    sch = schema_of()
    res = {'cap': a.cap, 'sets': {}, 'values': {}, 'budgets': {}}
    comps = [('r8', 0), ('r8', 1), ('r16', 1)]
    for s in map(str, R.SEEDS):
        S = T['seeds'][s]
        for rl, x in comps:
            key = f's{s}_{rl}_x{x}'
            B = budgets(int(s), rl)    # cap-12 ladder compute; at cap 6 an approximation (cap-6 ladders ran the same recipe)
            res['budgets'][key] = B
            lnKt, lnKp = math.log(B['K_total']), math.log(B['K_per'])
            sets = collections.defaultdict(list)
            vals = collections.defaultdict(dict)
            for n in names:
                rec = S[n]
                cb, cr = draw_counts(rec, 'pend', x), draw_counts(rec, rl, x)
                if cb is None or cr is None:
                    continue
                pb, pr = cb[0] / cb[1], cr[0] / cr[1]
                rl_solves = cr[0] > 0
                if cb[0] == 0 and rl_solves:
                    sets['eqk'].append(n)
                if pb < 0.05 and pr >= 0.5:
                    sets['rel'].append(n)
                ev, ref = rec['tf']['ev'], rec['tf']['ref']
                if rl_solves and 'pend' in ev:
                    lp = ev['pend']['T0.8']['total']; vals['spec_ev'][n] = lp
                    if lp < -lnKt:
                        sets['spec_ev'].append(n)
                    if ev['pend']['T0.8']['w1'] < -lnKp:
                        sets['w1_ev'].append(n)
                    if 'p0' in ev and rl == 'r8' and 'r8' in ev:
                        lr, lb, l0 = ev['r8']['T1.0']['total'], ev['pend']['T1.0']['total'], ev['p0']['T1.0']['total']
                        share = (lr - lb) / (lr - l0) if lr > l0 else float('nan')
                        vals['nullbits'][n] = share
                        if share > 0.5:
                            sets['nullbits'].append(n)
                if rl_solves and 'pend' in ref:
                    lp = ref['pend']['T0.8']['total']; vals['spec_ref'][n] = lp
                    if lp < -lnKt:
                        sets['spec_ref'].append(n)
            # IRT: pooled fit for r16 (x1 only) and r8 pooled; per-draw fits for the redraw floor
            src = irt.get('' if (rl == 'r16' or x is None) else f'_x{x}')
            if src:
                sets['irt'] = list(src['dif'].get(f's{s}_{rl}', {}).get('created', []))
            # schema families on holdout250 members
            fam = collections.defaultdict(list)
            for n in names:
                if n in sch and T['meta'][n]['pool'] == 'h250':
                    fam[sch[n]].append(n)
            for f, mem in fam.items():
                def rate(ck):
                    v = [draw_counts(S[m], ck, x) for m in mem]
                    v = [c for c in v if c]
                    return np.mean([1.0 if c[0] > 0 else 0.0 for c in v]) if v else float('nan')
                rb, rr = rate('pend'), rate(rl)
                vals['schema'][f] = (rb, rr, len(mem))
                if rb <= 0.05 and rr >= 0.5:
                    sets['schema'].extend(mem)
            # net of replay pretraining: drop theorems the replay-only control (ctrl8) solves on the same draw (x0 / x1)
            for d in list(sets):
                keep = []
                for n in sets[d]:
                    cc = draw_counts(S[n], 'ctrl8', x if x in (0, 1) else 1) if n in S else None
                    if not (cc and cc[0] > 0):
                        keep.append(n)
                sets[d + '_net'] = keep
            res['sets'][key] = {k: sorted(set(v)) for k, v in sets.items()}
            res['values'][key] = vals
    # ---- summary
    defs = ['eqk', 'rel', 'irt', 'spec_ev', 'spec_ref', 'w1_ev', 'nullbits', 'schema']
    print('net of replay (theorems the replay-only control also solves on the same draw removed): sizes')
    for d in ('eqk', 'rel', 'irt', 'schema'):
        print(f'  {d + "_net":12s} ' + ' '.join(f'{len(res["sets"][k].get(d + "_net", [])):5d}' for k in res['sets']))
    print(f'cap {a.cap}: created-set sizes (of 322) per seed; budgets K_total / K_per in base-attempt equivalents')
    for key, B in res['budgets'].items():
        if key.endswith('x0') or 'r16' in key:
            print(f'  {key}: K_total {B["K_total"]:,.0f} (ln {math.log(B["K_total"]):.2f}), K_per {B["K_per"]:,.0f} (ln {math.log(B["K_per"]):.2f})')
    print(f'{"definition":10s} ' + ' '.join(f'{k:>12s}' for k in res['sets']))
    for d in defs:
        print(f'{d:10s} ' + ' '.join(f'{len(res["sets"][k].get(d, [])):12d}' for k in res['sets']))
    print('\nredraw floor (r8: set from draw x0 vs draw x1), Jaccard per seed:')
    for d in defs:
        js = [jac(res['sets'][f's{s}_r8_x0'].get(d, []), res['sets'][f's{s}_r8_x1'].get(d, [])) for s in map(str, R.SEEDS)]
        print(f'  {d:10s} ' + ' '.join(f'{j:.2f}' for j in js))
    print('\nseed agreement (r8 x0): Jaccard s0-s1, s0-s2, s1-s2:')
    for d in defs:
        A = [set(res['sets'][f's{s}_r8_x0'].get(d, [])) for s in map(str, R.SEEDS)]
        print(f'  {d:10s} ' + ' '.join(f'{jac(A[i], A[j]):.2f}' for i, j in ((0, 1), (0, 2), (1, 2))))
    for rl, x in (('r8', 0),) + ((('r16', 1),) if a.cap == 12 else ()):
        print(f'\nagreement matrix ({rl}, draw x{x}): mean Jaccard over seeds')
        print(' ' * 10 + ' '.join(f'{d[:8]:>8s}' for d in defs))
        M = {}
        for d1 in defs:
            row = []
            for d2 in defs:
                js = [jac(res['sets'][f's{s}_{rl}_x{x}'].get(d1, []), res['sets'][f's{s}_{rl}_x{x}'].get(d2, [])) for s in map(str, R.SEEDS)]
                js = [j for j in js if not math.isnan(j)]
                row.append(np.mean(js) if js else float('nan')); M[(d1, d2)] = row[-1]
            print(f'{d1:10s}' + ' '.join(f'{v:8.2f}' for v in row))
        res[f'agree_{rl}'] = {f'{k[0]}|{k[1]}': v for k, v in M.items()}
    nb = [v for k, d in res['values'].items() if k.endswith('r8_x0') for v in d.get('nullbits', {}).values() if not math.isnan(v)]
    if nb:
        print(f'\nbits over the random-init null (r8 x0, eventual proofs, T 1.0): RL share median {np.median(nb):.4f}, '
              f'95th pct {np.percentile(nb, 95):.4f}, max {max(nb):.4f}, n {len(nb)}')
    json.dump(res, open(f'{OUT}/defs_c{a.cap}.json', 'w'))


if __name__ == '__main__':
    main()
