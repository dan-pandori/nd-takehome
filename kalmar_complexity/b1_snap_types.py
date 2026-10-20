#!/usr/bin/env python3
"""B1 by step type, from the snapshots (run kalmar-complexity).  An approximation, labelled as one.

  python3 kalmar_complexity/b1_snap_types.py   # -> artifacts/kc/b1_snap_types.json + table

For KAL-D seed s and step-type group g (`close:*` grouped), the held-out per-loss-token code of the snapshot at
training step t, L_g(t) (artifacts/kc/b1_snap.json, tf1200 at name base 0), stands in for the pre-update training
loss on that type's fresh pairs at step t.  Between t0 = 24,020 and the end of epoch 1 (178,581 steps) the type's
tokens arrive at N_g / 178,581 per step (N_g = its loss tokens in K12-Kalmár, artifacts/kc/tokens_kal_sl.json), so

  code_g = integral_{t0}^{178,581} L_g(t) dt * N_g / 178,581 / ln 2   (trapezoid; L at 178,581 interpolated 100k-200k)
  excess_g = code_g - (178,581 - t0) * N_g / 178,581 * L_g(final) / ln 2

Steps 1-24,020 (where most of the first-epoch code is paid) have no per-type data: only the logged aggregate.  Check:
sum_g code_g against the logged curve's code over the same window (b1_preq.json intervals).
"""
import collections, json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
E1, T0 = 178581, 24020
LN2 = math.log(2)


def group(t):
    return 'close' if t.startswith('close:') else t


def main():
    snap = json.load(open(A('artifacts/kc/b1_snap.json')))['models']
    tk = json.load(open(A('artifacts/kc/tokens_kal_sl.json')))
    N = collections.Counter()
    for t, (n, k) in tk['per_tag'].items():
        N[group(t)] += k
    b1 = json.load(open(A('artifacts/kc/b1_preq.json')))
    out = {}
    for s in range(3):
        def per_type(ck):
            d = collections.defaultdict(lambda: [0.0, 0])
            for t, v in snap[ck]['per_tag'].items():
                d[group(t)][0] += v['nats']; d[group(t)][1] += v['loss_tokens']
            return {g: a / b for g, (a, b) in d.items()}
        C = lambda st: f'ckpts/kc_src/stage1_kalD_s{s}{st}.pt'
        L24, L100, L200, Lf = (per_type(C(x)) for x in ('_step24020', '_step100000', '_step200000', ''))
        rows = {}
        for g in N:
            if g not in Lf:
                continue
            le = L100[g] + (L200[g] - L100[g]) * (E1 - 100000) / 100000
            integ = (L24[g] + L100[g]) / 2 * (100000 - T0) + (L100[g] + le) / 2 * (E1 - 100000)
            rate = N[g] / E1
            code = integ * rate / LN2
            resid = (E1 - T0) * rate * Lf[g] / LN2
            rows[g] = {'N_loss_tokens': N[g], 'L_24020': L24[g], 'L_100k': L100[g], 'L_200k': L200[g], 'L_final': Lf[g],
                       'code_bits_24k_to_e1': code, 'excess_bits_24k_to_e1': code - resid}
        logged = sum(iv['bits'] * max(0.0, min(1.0, (iv['step'] - T0) / max(1, iv['step'] - prev)))
                     for iv, prev in zip(b1[f'KAL-D s{s}']['intervals'],
                                         [0] + [x['step'] for x in b1[f'KAL-D s{s}']['intervals'][:-1]]))
        out[f'KAL-D s{s}'] = {'types': rows, 'sum_code_bits': sum(r['code_bits_24k_to_e1'] for r in rows.values()),
                              'sum_excess_bits': sum(r['excess_bits_24k_to_e1'] for r in rows.values()),
                              'logged_code_bits_same_window': logged}
    json.dump(out, open(A('artifacts/kc/b1_snap_types.json'), 'w'), indent=1)
    gs = sorted(out['KAL-D s0']['types'], key=lambda g: -out['KAL-D s0']['types'][g]['excess_bits_24k_to_e1'])
    print(f"{'type':12} " + ' '.join(f'{"s%d excess" % s:>12} {"bits/tok":>8}' for s in range(3)))
    for g in gs:
        cells = []
        for s in range(3):
            r = out[f'KAL-D s{s}']['types'][g]
            cells.append(f"{r['excess_bits_24k_to_e1']:12.4g} {r['excess_bits_24k_to_e1'] / (r['N_loss_tokens'] * (E1 - T0) / E1):8.4f}")
        print(f'{g:12} ' + ' '.join(cells))
    for s in range(3):
        o = out[f'KAL-D s{s}']
        print(f"s{s}: sum code {o['sum_code_bits']:.4g} vs logged curve {o['logged_code_bits_same_window']:.4g}; "
              f"sum excess {o['sum_excess_bits']:.4g}")


if __name__ == '__main__':
    main()
