#!/usr/bin/env python3
"""support-followups A / B / C tables from the pulled per-theorem records (support.py output).  Lean alone decided every
count (lean_judge inside support.py).  Prints tables; writes artifacts/sf/abc_summary.json.

  A  artifacts/sf/a_{base_T08_s1,ei_T08_s1rerun}.s0.jsonl   vs  support-curves artifacts/sc/s3_*_T08_s1 (lost EI s1) and s1_*_s0
  B  artifacts/sf/b_base_T10_s0.s0.jsonl                    (+ support-curves' 400,000 prior attempts)
  C  artifacts/sf/c1_big_T08_s0.s*.jsonl, c2_big_T08_s0.s*.jsonl, c2_big_T10_s0.s*.jsonl
"""
import json, glob, collections, os

SC = 'artifacts/sc'; SF = 'artifacts/sf'
MD5 = {'9bde44c0': 'base s0 (stage1_a1_seq_s0, 3.2 M)', 'fc27e52d': 'base s1 (stage1_a1_seq_s1, 3.2 M)',
       '5cebd7ec': 'EI s0 (la_T1_sc_s0_r8)', '105be4f3': 'EI s1 LOST (la_T1_sc_s1_r8)', '12c13e61': 'EI s1rerun (la_T1_sc_s1rerun_r8)'}


def load(pat):
    out = {}
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            if l.strip():
                r = json.loads(l); out.setdefault(r['name'], []).append(r)
    return out


def pooled(d):
    """name -> (n, c, md5s)"""
    return {n: (sum(r['n_tried'] for r in rs), sum(r['n_ok'] for r in rs), {r['ckpt_md5'][:8] for r in rs}) for n, rs in d.items()}


def trunc(d, Lt):
    t = collections.defaultdict(lambda: [0, 0])
    for n, rs in d.items():
        for r in rs:
            if 'n_no_eos' in r:
                t[Lt[n]][0] += r['n_no_eos']; t[Lt[n]][1] += r['n_tried']
    return {L: {'no_eos': a, 'n': b, 'frac': a / b if b else None} for L, (a, b) in sorted(t.items())}


def agree(x, y, names):
    return sum((x[n][1] > 0) == (y[n][1] > 0) for n in names), len(names)


def main():
    th = [json.loads(l) for l in open('data/sc/theorems.jsonl') if l.strip()]
    Lt = {r['name']: r['L_true'] for r in th}; names = [r['name'] for r in th]
    surv = [l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()]
    crux = [l.strip() for l in open('data/sc/crux_forward.txt') if l.strip()]
    S = {'models': MD5}

    # ---------------- A
    ab, ae = load(f'{SF}/a_base_T08_s1.s*.jsonl'), load(f'{SF}/a_ei_T08_s1rerun.s*.jsonl')
    if len(ab) == 383 and len(ae) == 383:
        AB, AE = pooled(ab), pooled(ae)
        LB, LE = pooled(load(f'{SC}/s3_base_T08_s1.s*.jsonl')), pooled(load(f'{SC}/s3_ei_T08_s1.s*.jsonl'))
        B0, E0 = pooled(load(f'{SC}/s1_base_T08_s0.s*.jsonl')), pooled(load(f'{SC}/s1_ei_T08_s0.s*.jsonl'))
        solved = lambda P: sum(P[n][1] > 0 for n in names)
        crux_of = lambda b, e: {n for n in names if b[n][1] == 0 and e[n][1] > 0}
        cA, cL, c0 = crux_of(AB, AE), crux_of(LB, LE), crux_of(B0, E0)
        a = {'k': 10000, 'stop_at': 50, 'T': 0.8, 'batch': 4096, 'max_new': 512,
             'base_s1_redraw_solved': solved(AB), 'base_s1_sc_solved': solved(LB),
             'ei_s1rerun_solved': solved(AE), 'ei_s1_lost_solved': solved(LE), 'ei_s0_solved': solved(E0), 'base_s0_solved': solved(B0),
             'crux_s1rerun': len(cA), 'crux_s1_lost': len(cL), 'crux_s0': len(c0),
             'crux_s1rerun_and_s0': len(cA & c0), 'crux_s1rerun_and_lost': len(cA & cL),
             'survivors_ei_s1rerun_solves': sum(AE[n][1] > 0 for n in surv), 'survivors_base_s1_redraw_solves': sum(AB[n][1] > 0 for n in surv),
             'survivors_in_crux_s1rerun': len(set(surv) & cA),
             'agree_ei_s1rerun_vs_lost': agree(AE, LE, names), 'agree_ei_s1rerun_vs_s0': agree(AE, E0, names),
             'agree_base_s1_redraw_vs_sc': agree(AB, LB, names), 'agree_base_s1_vs_s0_redraw': agree(AB, B0, names),
             'md5': {'base': sorted({m for v in AB.values() for m in v[2]}), 'ei': sorted({m for v in AE.values() for m in v[2]})},
             'truncation_base': trunc(ab, Lt), 'truncation_ei': trunc(ae, Lt),
             'peak_mem_gb': max(r.get('peak_mem_gb', 0) for rs in list(ab.values()) + list(ae.values()) for r in rs),
             'samples': sum(v[0] for v in AB.values()) + sum(v[0] for v in AE.values())}
        # per-stratum solved
        a['by_L'] = {L: {k: sum(P[n][1] > 0 for n in names if Lt[n] == L) for k, P in
                         [('base_s1_redraw', AB), ('base_s1_sc', LB), ('ei_s1rerun', AE), ('ei_s1_lost', LE), ('base_s0', B0), ('ei_s0', E0)]}
                     for L in sorted(set(Lt.values()))}
        S['A'] = a
        print('A — seed-1 column (T 0.8, k 10,000, stop 50):')
        for k in ('base_s1_redraw_solved', 'base_s1_sc_solved', 'ei_s1rerun_solved', 'ei_s1_lost_solved', 'ei_s0_solved', 'base_s0_solved',
                  'crux_s1rerun', 'crux_s1_lost', 'crux_s0', 'crux_s1rerun_and_s0', 'crux_s1rerun_and_lost', 'survivors_ei_s1rerun_solves',
                  'survivors_base_s1_redraw_solves', 'survivors_in_crux_s1rerun', 'agree_ei_s1rerun_vs_lost', 'agree_ei_s1rerun_vs_s0',
                  'agree_base_s1_redraw_vs_sc', 'agree_base_s1_vs_s0_redraw', 'md5', 'peak_mem_gb', 'samples'):
            print(f'  {k}: {a[k]}')
        print('  by L_true:', json.dumps(a['by_L']))
        print('  truncation base:', {L: f"{v['frac']:.4%}" for L, v in a['truncation_base'].items()})
        print('  truncation EI  :', {L: f"{v['frac']:.4%}" for L, v in a['truncation_ei'].items()})
    else:
        print(f'A incomplete: base {len(ab)}, ei {len(ae)} / 383')

    # ---------------- B
    b = load(f'{SF}/b_base_T10_s0.s*.jsonl')
    if b:
        prior = {}
        for n in b:
            ps = [r for f in glob.glob(f'{SC}/s*_base_*_s0.s*.jsonl') for l in open(f) for r in [json.loads(l)] if r['name'] == n]
            prior[n] = (sum(r['n_tried'] for r in ps), sum(r['n_ok'] for r in ps))
        rows = []
        for n, rs in b.items():
            nn, c = sum(r['n_tried'] for r in rs), sum(r['n_ok'] for r in rs)
            rows.append({'name': n, 'L_true': Lt[n], 'n_new': nn, 'c_new': c, 'n_prior': prior[n][0], 'c_prior': prior[n][1],
                         'p_hat': c / nn if c else None, 'ub95': (3.0 / nn) if c == 0 else None,
                         'first_hit': rs[0]['first_hit'], 'no_eos_frac': sum(r['n_no_eos'] for r in rs) / nn,
                         'proofs': [p['lean_text'] for r in rs for p in r['proofs']]})
        S['B'] = {'T': 1.0, 'stop_at': 5, 'rows': rows, 'total_new': sum(r['n_new'] for r in rows), 'successes': sum(r['c_new'] for r in rows),
                  'n_complete': len(rows)}
        print(f'\nB — base s0 (9bde44c0), T 1.0, {len(rows)} / 6 theorems done, {S["B"]["total_new"]:,} new attempts:')
        for r in rows:
            print(f"  {r['name']:17s} L{r['L_true']} new n {r['n_new']:,} ok {r['c_new']} (prior {r['n_prior']:,} / {r['c_prior']}) "
                  f"p̂ {r['p_hat']} ub95 {r['ub95']} no-eos {r['no_eos_frac']:.4%}")

    # ---------------- C
    c1 = load(f'{SF}/c1_big_T08_s0.s*.jsonl')
    if c1:
        C1 = pooled(c1)
        c = {'c1_done': len(C1), 'c1_crux_solved': sum(C1[n][1] > 0 for n in crux if n in C1),
             'c1_survivors_solved': sum(C1[n][1] > 0 for n in surv if n in C1), 'md5': sorted({m for v in C1.values() for m in v[2]}),
             'truncation_c1': trunc(c1, Lt)}
        c2 = {T: pooled(load(f'{SF}/c2_big_{T}_s0_sh*.s0.jsonl')) for T in ('T08', 'T10')}
        reach = {}
        for n in surv:
            n1, k1 = C1.get(n, (0, 0, None))[:2]
            e = {'L_true': Lt[n], 'c1': (n1, k1)}
            for T in ('T08', 'T10'):
                e[T] = c2[T].get(n, (0, 0, None))[:2]
            e['n08'] = n1 + e['T08'][0]; e['c08'] = k1 + e['T08'][1]
            e['n10'], e['c10'] = e['T10']
            e['reached'] = e['c08'] > 0 or e['c10'] > 0
            reach[n] = e
        c['survivors'] = reach
        c['survivors_reached'] = sum(e['reached'] for e in reach.values())
        c['reach_by_L'] = {L: [sum(e['reached'] for e in reach.values() if e['L_true'] == L), sum(1 for e in reach.values() if e['L_true'] == L)]
                           for L in sorted({e['L_true'] for e in reach.values()})}
        c['falsifier_fires'] = c['survivors_reached'] >= 15
        S['C'] = c
        print(f"\nC — big s0 {c['md5']}: c1 {c['c1_done']} / 82 done; crux solved at k 10,000: {c['c1_crux_solved']}; "
              f"survivors solved in c1: {c['c1_survivors_solved']}; survivors reached overall: {c['survivors_reached']} / 29 "
              f"(falsifier >= 15: {c['falsifier_fires']}); by L_true {c['reach_by_L']}")
        print('  truncation c1:', {L: f"{v['frac']:.4%}" for L, v in c['truncation_c1'].items()})
    json.dump(S, open(f'{SF}/abc_summary.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
