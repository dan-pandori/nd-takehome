#!/usr/bin/env python3
"""capability-defs Q6 (pre-registered): "new proof, old theorem" share of B.

  python3 capability_defs/analysis/cd_q6.py   -> out/q6.txt (stdout)

B = the equal-k created set (cap 12, r8 solves t on draw x0, pend 0 / 256 on x0; out/defs_c12.json).  A theorem in B is
"new proof, old theorem" if RL's eventual proof (the ladder's proof of t, scored by trajectory's tj_score at 33 name
bases) has log pi_pend < -ln K_total (T 0.8) while pend's known-proof estimate (J1: sum over every known accepted proof,
exact 33-base terms where stage 2 scored them, else the stage-1 bound b0 - ln 33) is >= ln 2 - ln K_total (factor-2
margin).  Pre-registered: >= 20 % of B.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cd_bracket import lse
from cd_part3 import load_scores

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def main():
    D = json.load(open(f'{OUT}/defs_c12.json'))
    for s in (0, 1, 2):
        key = f's{s}_r8_x0'
        B = D['sets'][key]['eqk']
        ev = D['values'][key]['spec_ev']
        lnKt = math.log(D['budgets'][key]['K_total'])
        by, _ = load_scores(s)
        hit = scored = 0
        for n in B:
            if n not in ev or n not in by:
                continue
            scored += 1
            LB = lse([v[f's{s}_pend'][0] for v in by[n].values() if f's{s}_pend' in v])
            if ev[n] < -lnKt and LB >= math.log(2) - lnKt:
                hit += 1
        print(f's{s}: |B| {len(B)}, scored {scored}; new proof, old theorem {hit} ({hit / len(B):.0%} of B); '
              f'K_total {math.exp(lnKt):,.0f}')


if __name__ == '__main__':
    main()
