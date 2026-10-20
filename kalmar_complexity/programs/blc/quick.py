#!/usr/bin/env python3
"""Development helper: compile a program, print its size breakdown, and check it on the first N test theorems.

  python3 quick.py ksl N        K-sl algorithm (structured proof, rendered in Python) vs ref_sl
"""
import statistics as st
import sys
import time

import nd_codec as nc
import blc
from nd2lean import parse_prompt
from kalmar_complexity.common import sample_prompts, ref_sl


def compile_prog(path, show=False):
    b0 = blc.Program.load(path).bits()
    prog = blc.optimise_best(path)
    b = prog.bits()
    if show:
        print(f'{path}: {b0} bits before optimisation, {b} after')
        for name, c in prog.definition_costs():
            if c > 2:
                print(f'   {name:10s} {c}')
    return prog, prog.debruijn()


def check_ksl(db, prompts):
    ok, steps = 0, []
    for p in prompts:
        prem, goal = parse_prompt(p)
        m = blc.Machine()
        th = m.closed((2, db, blc.enc_sequent(prem, goal)))
        lines = nc.dec_proof(m, th)
        got = ' '.join(nc.render_py(lines))
        want = ref_sl(p)['proof']
        if got != want:
            print('MISMATCH', p)
            print(' got ', got[:600])
            print(' want', want[:600])
            return ok, steps
        ok += 1
        steps.append(m.beta)
    return ok, steps


if __name__ == '__main__':
    what = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    t0 = time.time()
    if what == 'ksl':
        prog, db = compile_prog(sys.argv[3] if len(sys.argv) > 3 else 'ksl.lam', show=True)
        ok, steps = check_ksl(db, sample_prompts(1000)[:n])
        print(f'{ok}/{n} ok; beta mean {st.mean(steps):.0f} median {st.median(steps):.0f} max {max(steps)}; '
              f'{time.time() - t0:.1f}s')
