#!/usr/bin/env python3
"""capability-defs Part 3, definitions S2 / L-marginal (Dan's (a) and (b) made strict): bracket pend's solve probability.

  python3 capability_defs/analysis/cd_bracket.py [--seeds 0,1,2]  -> out/bracket.json + printed summary

For seed s and theorem t in H_s (hard: pend 0 / 512 on x0 + x1) or CAL_s (calibration):
  LB(t)  = log sum_{y in F(t)} pi_pend(y | t), F(t) = every known Lean-accepted proof (J1 targets).  Stage 1 (1 name
           base): each term is replaced by its valid lower bound b0_total - ln 33, so LB1 <= LB.  Where stage-2 exact
           33-base scores exist (out/j1s2_*), they replace the stage-1 terms (exact >= b0 - ln 33 always).
  UB(t)  = one-sided 95 % Clopper-Pearson upper bound from every pend sample of t: trajectory x0 + x1, mcts-a x2 (+ x4
           for group C) and J2 (16,384 or 4,096 more, when pulled).  p-hat = c / n.
  best1  = the largest single-proof term (the "specific proof" view); share of the sum carried by the best proof.
Also, for RL checkpoints, sum_{F} pi_R(y) vs p-hat_R from reads: how much of RL's success mass the known proofs cover.
Verdicts at budget K (budgets from cd_defs.budgets): elicited if exp(LB) >= 1 / K or p-hat-based lower 95 % bound >= 1/K;
created if UB < 0.05 / K and RL solves t; else undetermined.  Temperature: T 0.8 (the sampler's) unless stated.
"""
import argparse, collections, glob, gzip, json, math, os, sys
import numpy as np
from scipy.stats import beta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R
from cd_defs import budgets

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
LN33 = math.log(33)


def lse(xs):
    if not xs:
        return -math.inf
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


def cp_upper(c, n, a=0.05):
    return 1.0 if c >= n else float(beta.ppf(1 - a, c + 1, n - c))


def cp_lower(c, n, a=0.05):
    return 0.0 if c == 0 else float(beta.ppf(a, c, n - c + 1))


def load_j1(s):
    """{name: [ {tid, src, sc{label: [t10, w10, t08, w08]}} ... ]} from stage-1 compact files (+ stage-2 overrides)."""
    out = collections.defaultdict(list)
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/b1_s{s}_p*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    out[r['name']].append(r)
    exact = {}
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/b33_s{s}*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    exact[r['tid']] = r['sc']
    return out, exact


def j2_counts(s):
    out = {}
    for p in glob.glob(f'{ROOT}/artifacts/cd/j2/s{s}_*.jsonl'):
        if p.endswith('.args.json'):
            continue
        for l in open(p):
            r = json.loads(l)
            c = out.setdefault(r['name'], [0, 0, []])
            c[0] += r['n_ok']; c[1] += r['n_tried']; c[2].extend(r.get('proofs') or [])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', default='0,1,2')
    a = ap.parse_args()
    T = json.load(open(f'{OUT}/table_c12.json'))
    sets = json.load(open(f'{ROOT}/artifacts/cd/j1/sets.json'))
    res = {}
    for s in [int(x) for x in a.seeds.split(',')]:
        F, exact = load_j1(s)
        if not F:
            print(f's{s}: no J1 results yet'); continue
        J2 = j2_counts(s)
        S = T['seeds'][str(s)]
        rows = {}
        for grp in ('H', 'CAL'):
            for n in sets[str(s)][grp]:
                c = S[n]['counts']
                cb = [c['pend'][x] for x in ('0', '1', '2', '4') if x in c.get('pend', {})]
                n_b = sum(v[1] for v in cb); c_b = sum(v[0] for v in cb)
                if n in J2:
                    c_b += J2[n][0]; n_b += J2[n][1]
                def lb(label, ti):
                    terms = []
                    for r in F.get(n, []):
                        if r['tid'] in exact and label in exact[r['tid']]:
                            terms.append(exact[r['tid']][label][ti])
                        elif label in r['sc']:
                            terms.append(r['sc'][label][ti] - LN33)
                    return terms
                t08 = lb(f's{s}_pend', 2); t10 = lb(f's{s}_pend', 0)
                row = {'grp': grp, 'n_proofs': len(F.get(n, [])), 'c': c_b, 'n': n_b,
                       'phat': c_b / n_b if n_b else float('nan'), 'ub': cp_upper(c_b, n_b), 'lo': cp_lower(c_b, n_b),
                       'LB08': lse(t08), 'LB10': lse(t10), 'best08': max(t08) if t08 else -math.inf,
                       'j2': n in J2}
                for rl in ('r8', 'r16', 'init'):
                    row[f'LB08_{rl}'] = lse(lb(f's{s}_{rl}', 2))
                for rl, xs in (('r8', ('0', '1', '2')), ('r16', ('1',))):
                    cr = [c[rl][x] for x in xs if x in c.get(rl, {})]
                    row[f'phat_{rl}'] = sum(v[0] for v in cr) / max(1, sum(v[1] for v in cr)) if cr else float('nan')
                rows[n] = row
        res[s] = rows
        # ---- summaries
        cal = [r for r in rows.values() if r['grp'] == 'CAL' and r['c'] > 0]
        ratio = [math.exp(r['LB08']) / r['phat'] for r in cal]
        print(f'\ns{s}: H {sum(r["grp"] == "H" for r in rows.values())}, CAL {len(cal)}; J2 pulled for {sum(r["j2"] for r in rows.values())} theorems')
        if ratio:
            print(f'  calibration: exp(LB) / p-hat (T 0.8): median {np.median(ratio):.3f} [IQR {np.percentile(ratio, 25):.3f}, {np.percentile(ratio, 75):.3f}], '
                  f'share of the bound carried by the best single proof: median {np.median([math.exp(r["best08"] - r["LB08"]) for r in cal]):.2f}')
        for rl in ('r8', 'r16'):
            B = budgets(s, rl)
            H = [(n, r) for n, r in rows.items() if r['grp'] == 'H' and r[f'phat_{rl}'] > 0]
            el = [n for n, r in H if r['LB08'] >= -math.log(B['K_total'])]
            el_p = [n for n, r in H if r['LB08'] >= -math.log(B['K_per'])]
            el_s = [n for n, r in H if r['lo'] >= 1 / B['K_per']]
            cr_p = [n for n, r in H if r['ub'] < 0.05 / B['K_per']]
            cr_t = [n for n, r in H if r['ub'] < 0.05 / B['K_total']]
            margin = [r['LB08'] - r['best08'] for n, r in H]
            print(f'  {rl}: RL-solved hard theorems {len(H)}; certified elicited at K_total by LB: {len(el)} ({len(el) / max(1, len(H)):.0%}); '
                  f'at K_per by LB: {len(el_p)}, by sampling lower bound: {len(el_s)}; certified created at K_per: {len(cr_p)}, at K_total: {len(cr_t)}')
            print(f'       LB - best single proof (nats): median {np.median(margin):.2f}; coverage of RL success mass by F: '
                  f'median sum_F pi_{rl} / p-hat_{rl} = {np.median([math.exp(r["LB08_" + rl]) / r["phat_" + rl] for n, r in H]):.3f} (stage-1 bound)')
    json.dump({str(k): v for k, v in res.items()}, open(f'{OUT}/bracket.json', 'w'))


if __name__ == '__main__':
    main()
