#!/usr/bin/env python3
"""Test of the BLC programs (run kalmar-complexity).

  python3 test_blc.py --n 1000 --seed 20261020          # the run's sample; a reviewer uses any other seed

1. Builds every .lam program (parse + the deterministic optimiser of blc.py), writes the bit string to <name>.blc and
   checks that decoding the .blc gives the term that is run.  Bracket-abstracts it to S/K (binary CL) and checks on a
   few inputs that the CL term (graph reduction, CLMachine) gives the same decoded result as the lambda term.
2. For every sampled K12 theorem (kalmar_complexity.common.sample_prompts):
     parse      prompt word -> sequent, compared with nd2lean.parse_prompt
     K-sl       algorithm on the encoded sequent -> structured proof; the BLC renderer on (the canonical encoding of)
                that structure -> ND tokens, compared token for token with ref_sl(prompt)['proof']
     K-tt       algorithm -> proof-term tree; the BLC renderer on (sequent, tree) -> Lean tokens, joined by the
                documented spacing rule and compared with ref_tt(prompt)
   beta-steps are counted separately for each program (call-by-need machine, read-out of the result included).
3. Calibration programs: >= 200 randomized cases each against Python.
Writes results.json (bits, CL bits, beta stats, pass counts).
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nd_codec as nc  # noqa: E402
import tt_codec as tc  # noqa: E402
import blc  # noqa: E402
import calib_check  # noqa: E402
from nd2lean import parse_prompt  # noqa: E402
from kalmar_complexity.common import sample_prompts, ref_sl, ref_tt, TEST_SEED  # noqa: E402

PROGRAMS = [('parse', 'parse.lam'),
            ('K-sl algorithm', 'ksl.lam'), ('K-sl rendering', 'ksl_render.lam'),
            ('K-tt algorithm', 'ktt.lam'), ('K-tt rendering', 'ktt_render.lam')] + \
           [(f'calib {c}', f'calib/{c}.lam') for c in calib_check.CALIB]


def build_all():
    out = {}
    for name, f in PROGRAMS:
        path = os.path.join(HERE, f)
        prog = blc.optimise_best(path)
        db = prog.debruijn()
        bits = blc.blc_encode(db)
        with open(path[:-4] + '.blc', 'w') as fh:
            fh.write(bits + '\n')
        with open(path[:-4] + '.blc') as fh:
            assert blc.blc_decode(fh.read().strip()) == db
        assert blc.db_closed(db)
        cl = blc.to_cl_best(db)
        out[name] = {'file': f, 'db': db, 'bits': len(bits), 'cl': cl, 'cl_bits': blc.cl_bits(cl),
                     'definitions': prog.definition_costs()}
    return out


SYNTHETIC = ['THM ( F > F ) , ( ~ F ) SEQ ( F > F ) PRF', 'THM ( F > F ) , ( F > F ) SEQ ( F > F ) PRF',
             'THM P , P SEQ P PRF', 'THM ( P & Q ) , ( P & Q ) SEQ ( P & Q ) PRF',
             'THM ( ~ ( ~ ( P v ( ~ P ) ) ) ) SEQ ( ( ~ ( ~ ( P v ( ~ P ) ) ) ) v Q ) PRF',
             'THM ( P v ( ~ P ) ) SEQ ( P v ( ~ P ) ) PRF', 'THM SEQ ( P > P ) PRF', 'THM F SEQ F PRF',
             'THM ( F > F ) SEQ ( F > F ) PRF', 'THM ( ~ F ) , ( F > F ) SEQ ( ~ F ) PRF', 'THM P , ( P > Q ) , P SEQ Q PRF',
             'THM ( P v ( ~ P ) ) , ( Q v ( ~ Q ) ) SEQ ( ( P v ( ~ P ) ) & ( Q v ( ~ Q ) ) ) PRF',
             'THM Q , ( ~ ( ~ ( Q v ( ~ Q ) ) ) ) SEQ ( ~ ( ~ ( Q v ( ~ Q ) ) ) ) PRF']


def edge_prompts():
    """K12's atom-free sequents and those with a premise ~~(X v ~X), 40 with a premise P v ~P, and synthetic cases
    (duplicate premises, goal among the premises) that K12 does not contain."""
    from kalmar_complexity.common import k12_prompts
    ps = k12_prompts()
    sel = [p for p in ps if not any(x in p.split() for x in 'PQRS')
           or any(f'( ~ ( ~ ( {x} v ( ~ {x} ) ) ) )' in p for x in 'PQRS')]
    return sel + [p for p in ps if '( P v ( ~ P ) )' in p][:40] + SYNTHETIC


def check_theorem(progs, p):
    """-> (ok parse, ok K-sl, ok K-tt, steps per program, algorithm-alone ok sl, tt)"""
    prem, goal = parse_prompt(p)
    seq = blc.enc_sequent(prem, goal)
    st_ = {}
    m = blc.Machine()
    got = dec_seq(m, run(m, progs['parse']['db'], nc.prompt_word(p)))
    st_['parse'] = m.beta
    m = blc.Machine()
    lines = nc.dec_proof(m, run(m, progs['K-sl algorithm']['db'], seq))
    st_['K-sl algorithm'] = m.beta
    want = ref_sl(p)['proof']
    alg_sl = ' '.join(nc.render_py(lines)) == want
    m = blc.Machine()
    toks = blc.dec_word(m, run(m, progs['K-sl rendering']['db'], nc.enc_proof(lines)), nc.ND_ALPHABET, numbered=('N',))
    st_['K-sl rendering'] = m.beta
    m = blc.Machine()
    tree = tc.dec_tree(m, run(m, progs['K-tt algorithm']['db'], seq))
    st_['K-tt algorithm'] = m.beta
    want_tt = ref_tt(p)
    alg_tt = tc.join(tc.render(tree, prem, goal)) == want_tt
    m = blc.Machine()
    ltoks = blc.dec_word(m, run(m, progs['K-tt rendering']['db'], seq, tc.enc_tree(tree)), tc.LEAN_ALPHABET,
                         numbered=tc.NUMBERED)
    st_['K-tt rendering'] = m.beta
    return (got == (prem, goal), toks == want.split(), tc.join(ltoks) == want_tt, st_, alg_sl, alg_tt)


def dec_seq(m, th):
    return blc.dec_pair(m, th, lambda m, t: blc.dec_list(m, t, blc.dec_formula), blc.dec_formula)


def run(m, db, *args):
    t = db
    for a in args:
        t = (2, t, a)
    return m.closed(t)


def cl_run(c, *args):
    cm = blc.CLMachine()
    t = c
    for a in args:
        t = blc.capp(t, blc.to_cl_best(a))
    return cm, cm.load(t)


def cl_checks(progs, prompts):
    """the CL term of each program gives the lambda term's result on a few inputs"""
    res = {}
    for name, _ in PROGRAMS:
        P = progs[name]
        if name.startswith('calib'):
            c = name.split()[1]
            import random
            ins = [((i,), d) for i, _e, d in calib_check.cases(c, random.Random(7), 5)]
        else:
            ins = []
            for p in prompts:
                prem, goal = parse_prompt(p)
                seq = blc.enc_sequent(prem, goal)
                if name == 'parse':
                    ins.append(((nc.prompt_word(p),), dec_seq))
                elif name == 'K-sl algorithm':
                    ins.append(((seq,), nc.dec_proof))
                elif name == 'K-sl rendering':
                    from ksl_mirror import ksl
                    ins.append(((nc.enc_proof(ksl(prem, goal)),),
                                lambda m, t: blc.dec_word(m, t, nc.ND_ALPHABET, numbered=('N',))))
                elif name == 'K-tt algorithm':
                    ins.append(((seq,), tc.dec_tree))
                else:
                    ins.append(((seq, tc.enc_tree(tc.tree(prem, goal))),
                                lambda m, t: blc.dec_word(m, t, tc.LEAN_ALPHABET, numbered=tc.NUMBERED)))
        ok = 0
        for args, dec in ins:
            m = blc.Machine()
            want = dec(m, run(m, P['db'], *args))
            cm, node = cl_run(P['cl'], *args)
            got = dec(cm, node)
            ok += got == want
        res[name] = (ok, len(ins))
    return res


def stats(xs):
    return {'mean': st.mean(xs), 'median': st.median(xs), 'max': max(xs), 'min': min(xs)} if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=TEST_SEED)
    ap.add_argument('--calib-n', type=int, default=200)
    ap.add_argument('--out', default=os.path.join(HERE, 'results.json'))
    a = ap.parse_args()
    t0 = time.time()
    progs = build_all()
    print(f'built {len(progs)} programs in {time.time() - t0:.1f}s')
    prompts = sample_prompts(a.n, a.seed)

    t1 = time.time()
    clres = cl_checks(progs, prompts[:3])
    print(f'CL checks done in {time.time() - t1:.1f}s')

    steps = {name: [] for name, _ in PROGRAMS}
    passes = {name: 0 for name, _ in PROGRAMS}
    alg_ok = {'K-sl algorithm': 0, 'K-tt algorithm': 0}
    fails = []
    t2 = time.time()
    for i, p in enumerate(prompts):
        ok_p, ok_sl, ok_tt, st_, alg_sl, alg_tt = check_theorem(progs, p)
        for k, v in st_.items():
            steps[k].append(v)
        passes['parse'] += ok_p
        passes['K-sl algorithm'] += ok_sl
        passes['K-sl rendering'] += ok_sl
        passes['K-tt algorithm'] += ok_tt
        passes['K-tt rendering'] += ok_tt
        alg_ok['K-sl algorithm'] += alg_sl
        alg_ok['K-tt algorithm'] += alg_tt
        if not (ok_p and ok_sl and ok_tt):
            fails.append(p)
        if (i + 1) % 100 == 0:
            print(f'  {i + 1}/{len(prompts)} theorems, {time.time() - t2:.0f}s, failures {len(fails)}', flush=True)
    edge = edge_prompts()
    edge_ok = sum(all(check_theorem(progs, p)[:3]) for p in edge)
    print(f'  edge cases: {edge_ok}/{len(edge)}')
    t3 = time.time()

    k12 = []
    for p in prompts[:100]:
        k12.append(parse_prompt(p))
    for c in calib_check.CALIB:
        name = f'calib {c}'
        ok, s = calib_check.check(c, progs[name]['db'], a.calib_n, seed=a.seed, k12=k12)
        passes[name] = ok
        steps[name] = s
    t4 = time.time()

    results = {'seed': a.seed, 'n': a.n, 'calib_n': a.calib_n,
               'timing_s': {'build': round(t1 - t0, 1), 'cl_checks': round(t2 - t1, 1), 'theorems': round(t3 - t2, 1),
                            'calibration': round(t4 - t3, 1)},
               'beta_steps_note': 'beta-reductions of the call-by-need machine, read-out of the result included',
               'programs': {}}
    for name, f in PROGRAMS:
        P = progs[name]
        s = stats(steps[name])
        total = a.calib_n if name.startswith('calib') else a.n
        results['programs'][name] = {
            'file': f, 'blc_bits': P['bits'], 'cl_bits': P['cl_bits'],
            'beta': s, 'Kt_bits_median': round(P['bits'] + math.log2(s['median']), 1) if s else None,
            'pass': passes[name], 'cases': total, 'cl_check': f'{clres[name][0]}/{clres[name][1]}',
        }
    for name in alg_ok:
        results['programs'][name]['algorithm_alone_pass'] = alg_ok[name]
    for lab, parts in (('K-sl algorithm + rendering', ['K-sl algorithm', 'K-sl rendering']),
                       ('K-sl parse + algorithm + rendering', ['parse', 'K-sl algorithm', 'K-sl rendering']),
                       ('K-tt algorithm + rendering', ['K-tt algorithm', 'K-tt rendering']),
                       ('K-tt parse + algorithm + rendering', ['parse', 'K-tt algorithm', 'K-tt rendering'])):
        results['programs'][lab] = {'blc_bits': sum(progs[x]['bits'] for x in parts),
                                    'cl_bits': sum(progs[x]['cl_bits'] for x in parts), 'parts': parts}
    results['edge_cases'] = {'pass': edge_ok, 'cases': len(edge)}
    results['failures'] = fails[:20]
    with open(a.out, 'w') as fh:
        json.dump(results, fh, indent=1)

    print(f'\n{"program":38s} {"BLC":>6s} {"CL":>7s} {"pass":>11s} {"CL chk":>7s} {"beta mean":>10s} '
          f'{"median":>8s} {"max":>8s}')
    for name, r in results['programs'].items():
        b = r.get('beta')
        line = f'{name:38s} {r["blc_bits"]:6d} {r["cl_bits"]:7d}'
        if 'pass' in r:
            line += f' {r["pass"]:5d}/{r["cases"]:<5d} {r["cl_check"]:>7s}'
            line += f' {b["mean"]:10.0f} {b["median"]:8.0f} {b["max"]:8d}'
        print(line)
    print(f'\ntheorems: {a.n} (seed {a.seed}), failures: {len(fails)}; time {time.time() - t0:.0f}s '
          f'({t3 - t2:.0f}s for the theorems)')
    return 0 if not fails and edge_ok == len(edge) and all(passes[n] == (a.calib_n if n.startswith('calib') else a.n) for n in passes) else 1


if __name__ == '__main__':
    sys.exit(main())
