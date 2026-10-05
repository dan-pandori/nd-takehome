#!/usr/bin/env python3
"""capability-defs: the markdown tables of REPORT.md §3, rendered from the analysis outputs (no hand-copied numbers).

  python3 capability_defs/analysis/cd_report_tables.py > capability_defs/analysis/out/report_tables.md

Inputs: out/part3.json (cd_part3.py), out/bracket.json (cd_bracket.py), out/j3.json (cd_j3.py), out/lem.json
(cd_lem.py), artifacts/cd/j9/ (J9 certification chunks).  Model: cap-12 best-cap12 (`best_model.ALiBiGPT`, 9,560,832
params, `lean_staten`, from scratch on K12) unless a row says cap 6.
"""
import glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cd_bracket import cp_upper, cp_lower
from cd_defs import LADDER_S

ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(HERE, 'out')
SEEDS = (0, 1, 2)
LAB = {'eqk': 'equal-k (`passk-equal-k`)', 'cm': 'compute-matched (`passk-budget`)', 'cm0': '… of which 0 base successes',
       'rel': 'reliable (`reliability`)', 'tfmax': 'best known proof < 1 / K (`tf-proof-prob`)',
       'brk_ne': 'not certified elicited (`marginal-bracket`)', 'irt': 'IRT DIF+ (`irt-ability`, unmatched)',
       'schema': 'family members (`schema-acquisition`)', 'guided': 'guided read fails too (`capability-vs-propensity`)',
       'sharp': 'expansion share ρ ≥ ½ (`sharpen-expand`)', 'npnt': 'new rule set + cm (`new-proof-new-theorem`)',
       'chain': 'chain depth ≥ 2 + cm (`chain-reachability`)', 'ood': 'rule set not in K12 (`out-of-data-novelty`)',
       'cm_recipe': 'cm, no seed\'s base ever solves t', 'cm_j7': 'cm, J7 continuation fails t (draw x0)'}


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else float('nan')


def f3(v):
    return '–' if v is None or (isinstance(v, float) and math.isnan(v)) else f'{v:.2f}'


def sizes(P, key, d):
    S = P['sets'].get(key)
    return None if S is None else len(S.get(d, []))


def t_defs(P):
    print('| definition (card) | r8, x0: s0 / s1 / s2 | net of replay-only | r16, x1 | redraw Jaccard (r8) | seed Jaccard (r8, pairs) |')
    print('|---|---|---|---|---|---|')
    for d in ['eqk', 'cm', 'cm0', 'cm_recipe', 'cm_j7', 'rel', 'tfmax', 'brk_ne', 'guided', 'schema', 'irt', 'sharp',
              'npnt', 'chain', 'ood']:
        r8 = [sizes(P, f's{s}_r8_x0', d) for s in SEEDS]
        nt = [sizes(P, f's{s}_r8_x0', d + '_net') for s in SEEDS]
        r16 = [sizes(P, f's{s}_r16_x1', d) for s in SEEDS]
        rd = [jac(P['sets'][f's{s}_r8_x0'].get(d, []), P['sets'][f's{s}_r8_x1'].get(d, []))
              if f's{s}_r8_x1' in P['sets'] else float('nan') for s in SEEDS]
        sd = [jac(P['sets'][f's{i}_r8_x0'].get(d, []), P['sets'][f's{j}_r8_x0'].get(d, [])) for i, j in ((0, 1), (0, 2), (1, 2))]
        fmt = lambda v: ' / '.join('–' if x is None else str(x) for x in v)
        print(f'| {LAB.get(d, d)} | {fmt(r8)} | {fmt(nt)} | {fmt(r16)} | {" / ".join(f3(x) for x in rd)} | '
              f'{" / ".join(f3(x) for x in sd)} |')


def t_cov(P):
    print('| seed | base within reach at K_eval-set (r8 / r16 budget) | replay-only r8, k 256 | J7 continuation, k 256 | r8, k 256 | r16, k 256 | Δ_cov r8 / r16 |')
    print('|---|---|---|---|---|---|---|')
    for s in SEEDS:
        a, b = P['cov'].get(f's{s}_r8'), P['cov'].get(f's{s}_r16')
        if a and b:
            j7 = a.get('j7_solved_256')
            print(f'| s{s} | {a["base_within_K"]} / {b["base_within_K"]} | {a.get("ctrl8_solved_256", "–")} | {j7 if j7 is not None else "–"} | '
                  f'{a["rl_solved_256"]} | {b["rl_solved_256"]} | {a["rl_solved_256"] - a["base_within_K"]:+d} / '
                  f'{b["rl_solved_256"] - b["base_within_K"]:+d} |')


def t_bracket(B):
    print('| r8-solved hard theorems, verdict at K_eval-set | s0 | s1 | s2 |')
    print('|---|---|---|---|')
    rows = {}
    for s in SEEDS:
        K = LADDER_S['r8'][s] / (322 * 3.6e-3)
        H = [r for r in B[str(s)].values() if r['grp'] == 'H' and r.get('phat_r8', 0) > 0]
        el_s = [r for r in H if r['lo'] >= 1 / K]
        el_e = [r for r in H if r['lo'] < 1 / K and r['LB08'] >= math.log(2) - math.log(K)]
        nr = [r for r in H if r not in el_s and r not in el_e and r['c'] == 0 and r['n'] >= K]
        found = [r for r in H if r not in el_s and r not in el_e and r['c'] > 0]
        und = [r for r in H if r not in el_s and r not in el_e and r not in nr and r not in found]
        cert = [r for r in H if r['ub'] < 0.05 / K]
        rows[s] = (len(H), len(el_s), len(el_e), len(found), len(nr), len(und), len(cert))
    labs = ['RL-solved hard theorems', 'elicited: sampling lower bound ≥ 1 / K', 'elicited: known-proof estimate ≥ 2 / K',
            'base found it, but not certifiably within reach', 'not reached: 0 base successes in ≥ K attempts',
            'undetermined (0 successes, fewer than K attempts)', 'certified created (UB95 < 0.05 / K)']
    for i, lab in enumerate(labs):
        print(f'| {lab} | ' + ' | '.join(str(rows[s][i]) for s in SEEDS) + ' |')


def t_sens(P):
    print('| threshold (r8, x0) | s0 | s1 | s2 |')
    print('|---|---|---|---|')
    for mul in (0.1, 0.3, 1, 3):
        for d in ('cm', 'tfmax', 'brk_ne'):
            v = [P['sens'][f's{s}'][f'K x{mul}'] for s in SEEDS]
            extra = [f" ({x['cm_undet']} undet.)" if d == 'cm' and x['cm_undet'] else '' for x in v]
            print(f'| {d} at K = {mul} × K_eval-set | ' + ' | '.join(f'{x[d]}{e}' for x, e in zip(v, extra)) + ' |')
    for lab, key in (('equal-k, base sample', 'eqk base sample'), ('reliable, p̂_R ≥ q (within cm)', 'rel q'),
                     ('expansion share ρ ≥ q', 'sharp rho'), ('schema, pend ≤ lo / RL ≥ hi', 'schema (pend<=lo, RL>=hi)')):
        ks = list(P['sens']['s0'][key])
        for k in ks:
            print(f'| {lab}: {k} | ' + ' | '.join(str(P['sens'][f's{s}'][key][k]) for s in SEEDS) + ' |')


def t_j3(J):
    print('| model | textbook72 dev58: plain / guided | train14 | holdout250 | guided tokens per attempt |')
    print('|---|---|---|---|---|')
    for cap in (12, 6):
        for s in SEEDS:
            for ck in ('pend', 'r8', 'r16'):
                r = J.get(f'c{cap}_s{s}_{ck}')
                if not r:
                    continue
                g = lambda k: f"{r[k]['plain']} / {r[k]['guided']}"
                tpa = r.get('guided_tokens_per_attempt')
                print(f'| cap {cap} s{s} {ck} | {g("tb72_dev58")} | {g("tb72_train14")} | {g("h250")} | '
                      f'{tpa:.0f} |' if tpa else '| – |')


def t_j9():
    from cd_part3 import j2_counts
    T = json.load(open(f'{OUT}/table_c12.json'))
    print('| seed | theorem | r8 pass@1 (x0) | base attempts before J9 | J9 attempts | J9 successes | UB95, all base attempts | '
          '0.05 / K_eval-set | certified created at K_eval-set? |')
    print('|---|---|---|---|---|---|---|---|---|')
    for s in SEEDS:
        sel = f'{ROOT}/data/cd/j9/s{s}.jsonl'
        if not os.path.exists(sel):
            continue
        K = LADDER_S['r8'][s] / (322 * 3.6e-3)
        allc = j2_counts(s)
        j9 = {}
        for p in glob.glob(f'{ROOT}/artifacts/cd/j9/s{s}_k*.jsonl'):
            if p.endswith('.full.jsonl'):
                continue
            for l in open(p):
                r = json.loads(l)
                v = j9.setdefault(r['name'], [0, 0]); v[0] += r['n_ok']; v[1] += r['n_tried']
        for l in open(sel):
            n = json.loads(l)['name']
            c = T['seeds'][str(s)][n]['counts']
            pc = sum(v[0] for v in c.get('pend', {}).values()) + allc[n][0] if n in allc else None
            pn = sum(v[1] for v in c.get('pend', {}).values()) + allc[n][1] if n in allc else None
            jc, jn = j9.get(n, [0, 0])
            r8 = c['r8']['0']
            ub = cp_upper(pc, pn)
            cert = 'yes' if ub < 0.05 / K else ('no (a success)' if pc else f'not yet ({jn:,} J9 attempts)')
            print(f'| s{s} | `{n}` | {r8[0] / r8[1]:.2f} | {pn - jn:,} | {jn:,} | {jc} | {ub:.2e} | {0.05 / K:.2e} | {cert} |')


JOBS = {'j1': 'J1 teacher-forced scores (stage 1 + 2)', 'j2': 'J2 stage A + calibration', 'j2b': "J2 stages A', B, truncation",
        'logical': 'J3 guided reads (both caps)', 'j4': 'J4 demonstration fine-tunes + reads', 'j5': 'J5 missing plain draws',
        'j6': 'J6 no-DN knockout pretraining + fine-tunes + reads', 'j6b': 'J6b DN-free-replay fine-tunes + reads',
        'j7': 'J7 compute-matched continuation + reads', 'j8': 'J8 start-dependence scores', 'j9': 'J9 certification sampling',
        'j10': 'J10 long-pool sampling'}


def t_compute():
    rows = {}
    for l in open(f'{OUT}/compute.txt'):
        parts = l.split()
        if parts and parts[0] in JOBS and len(parts) == 8:
            rows[parts[0]] = [int(x.replace(',', '')) for x in parts[1:]]
    print('| job | A40-hours (process level) | attempts | generated tokens | training tokens | Lean checks |')
    print('|---|---|---|---|---|---|')
    tot = [0] * 7
    for k in ('j1', 'j2', 'j2b', 'logical', 'j4', 'j5', 'j6', 'j6b', 'j7', 'j8', 'j9', 'j10'):
        if k not in rows:
            continue
        g, tok, att, act, steps, ttok, lean = rows[k]
        tot = [a + b for a, b in zip(tot, rows[k])]
        print(f'| {JOBS[k]} | {g / 3600:.1f} | {att / 1e6:.2f} M | {tok / 1e6:,.0f} M | {ttok / 1e9:.2f} B | {lean:,} |')
    print(f'| **total** | **{tot[0] / 3600:.1f}** | {tot[2] / 1e6:.1f} M | {tot[1] / 1e9:.2f} B | {tot[5] / 1e9:.1f} B | {tot[6]:,} |')


def main():
    P = json.load(open(f'{OUT}/part3.json'))
    B = json.load(open(f'{OUT}/bracket.json'))
    print('## created sets\n'); t_defs(P)
    print('\n## coverage\n'); t_cov(P)
    print('\n## bracket verdicts at K_eval-set\n'); t_bracket(B)
    print('\n## threshold sensitivity\n'); t_sens(P)
    if os.path.exists(f'{OUT}/j3.json'):
        print('\n## plain vs guided\n'); t_j3(json.load(open(f'{OUT}/j3.json')))
    print('\n## J9\n'); t_j9()
    if os.path.exists(f'{OUT}/compute.txt'):
        print('\n## compute\n'); t_compute()


if __name__ == '__main__':
    main()
