#!/usr/bin/env python3
"""organism-analysis Q3 (entropy side): on-policy and hard-step entropy per round, and the Cui et al. fit.

Inputs: artifacts/oa/entropy/<list>_s<S>/<label>.json (oa_entropy.py on the pod), the stored reads, the ladders'
round_<r>.json (data/oa_in/rounds/).  Ladders: c12 s0-s2, c6 s0-s2 (r0 = pend, r1..r8) and rfc s0-s2 x 4 starts
(r0 = the start checkpoint, r2, r4, r8).
  H(k)  = mean token entropy of the T 0.8 policy over on-policy generated action tokens (4 x 1,024 RL targets).
  R_tr(k) = EI training-target sample accuracy of the samples drawn FROM checkpoint k (round_<k+1>.json), k = 0..7.
  R_ev(k) = mean x1 pass@1 over the 322 evaluation theorems at checkpoint k.
  Fit R = -a * exp(H) + b (least squares, linear in exp(H)); report a, b, R^2, b - a (R predicted at H = 0).
Hard-step entropy: teacher-forced mean token entropy (T 1.0) at reference steps with r0 log p < -4 vs the other
reference steps, per round.  Writes artifacts/oa/q3_entropy.json and prints the tables.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oa_load import ROOT, SEEDS, STARTS, read_both, rfc_label

E = 'artifacts/oa/entropy'


def ent(lst, seed, label):
    f = os.path.join(E, f'{lst}_s{seed}', f'{label}.json')
    return json.load(open(f)) if os.path.exists(f) else None


def round_acc(ladder, r):
    f = os.path.join(ROOT, 'rounds', ladder, f'round_{r}.json')
    return float(json.load(open(f))['target_sample_acc']) if os.path.exists(f) else None


def pass1(run, label):
    d = read_both(run, label, 1)
    return None if d is None else float(np.mean([v[0] / v[1] for v in d.values()]))


def ladders():
    """-> list of (name, [(k, entropy json, R_tr, R_ev, ckpt label)])."""
    out = []
    for run, lst, lad in (('c12', 'c12', 'la_T1_best12_s{s}'), ('c6', 'c6', 'la_T1_best6_s{s}')):
        for s in SEEDS:
            pts = []
            for k in range(9):
                lab = 'pend' if k == 0 else f'r{k}'
                pts.append((k, ent(lst, s, f'{lst}_s{s}_{lab}'), round_acc(lad.format(s=s), k + 1) if k < 8 else None,
                            pass1(run, f's{s}_{lab}')))
            out.append((f'{run} s{s}', pts))
    for s in SEEDS:
        for X in STARTS:
            pts = [(0, ent('c12', s, f'c12_s{s}_{X}'), round_acc(f'la_T1_best12_s{s}_{X}', 1), pass1('c12', f's{s}_{X}'))]
            for k in (2, 4, 8):
                pts.append((k, ent(f'rfc_{X}', s, f'rfc_s{s}_{X}_r{k}'), round_acc(f'la_T1_best12_s{s}_{X}', k + 1) if k < 8 else None,
                            pass1('rfc', f's{s}_{X}_r{k}')))
            out.append((f'rfc {X} s{s}', pts))
    return out


def fit(H, R):
    H, R = np.array(H), np.array(R)
    X = np.column_stack([-np.exp(H), np.ones(len(H))])
    (a, b), *_ = np.linalg.lstsq(X, R, rcond=None)
    pred = X @ np.array([a, b])
    ss = float(np.sum((R - R.mean()) ** 2))
    return {'a': round(float(a), 4), 'b': round(float(b), 4), 'r2': round(1 - float(np.sum((R - pred) ** 2)) / ss, 3) if ss > 0 else None,
            'b_minus_a': round(float(b - a), 4), 'n': len(H)}


def main():
    res = {'ladders': {}, 'fits': {}}
    print('on-policy entropy (T 0.8 policy, nats / token) by checkpoint; R_tr = EI training sample accuracy of samples drawn from it; R_ev = eval pass@1 (x1)')
    for name, pts in ladders():
        rows = [(k, e['onpol']['H08_tok'] if e else None, e['onpol']['H1_tok'] if e else None, rt, rv) for k, e, rt, rv in pts]
        res['ladders'][name] = [{'k': k, 'H08': h, 'H1': h1, 'R_tr': rt, 'R_ev': rv} for k, h, h1, rt, rv in rows]
        print(f'  {name:<16} ' + ' '.join(f'r{k}:{h:.4f}' if h is not None else f'r{k}:  -   ' for k, h, *_ in rows))
        for key, idx in (('tr', 3), ('ev', 4)):
            ok = [(r[1], r[idx]) for r in rows if r[1] is not None and r[idx] is not None]
            if len(ok) >= 3:
                res['fits'][f'{name}|{key}'] = fit([o[0] for o in ok], [o[1] for o in ok])
            ok1 = [(r[1], r[idx]) for r in rows if r[0] >= 1 and r[1] is not None and r[idx] is not None]
            if len(ok1) >= 3:     # within RL only (r >= 1): does entropy track performance once the r0 -> r1 jump is out?
                res['fits'][f'{name}|{key}_rl'] = fit([o[0] for o in ok1], [o[1] for o in ok1])
    print('\nCui fit R = -a exp(H) + b (H = T 0.8 on-policy token entropy):')
    for k, v in res['fits'].items():
        name, key = k.split('|')
        obs = [p[f'R_{key[:2]}'] for p in res['ladders'][name] if p[f'R_{key[:2]}'] is not None]
        print(f'  {name:<16} {key}: a {v["a"]:.3f} b {v["b"]:.3f} R2 {v["r2"]} b-a {v["b_minus_a"]:.3f} (max observed {max(obs):.3f}, n {v["n"]})')
    # hard-step entropy (teacher-forced, reference proofs), c12 / c6
    steps = [json.loads(l) for l in open('data/oa/q2_steps.jsonl')]
    hard = {(s['run'], s['seed'], s['name'], s['i']): s['hard'] for s in steps if s['run'] in ('c12', 'c6')}
    print('\nteacher-forced token entropy (T 1.0) on reference steps, median over steps: hard (r0 lp < -4) / other, by round')
    for run in ('c12', 'c6'):
        line_h, line_o, firsts = [], [], []
        for k in range(9):
            lab = 'pend' if k == 0 else f'r{k}'
            hv, ov, fv = [], [], []
            for s in SEEDS:
                e = ent(run, s, f'{run}_s{s}_{lab}')
                if e is None:
                    continue
                for tid, st in e['tf'].items():
                    if not tid.startswith('ref:'):
                        continue
                    for i, x in enumerate(st):
                        h = hard.get((run, s, tid[4:], i))
                        if h is None:
                            continue
                        (hv if h else ov).append(x['H1'])
                        if h:
                            fv.append(x['H1_first'])
            line_h.append(round(float(np.median(hv)), 4) if hv else None)
            line_o.append(round(float(np.median(ov)), 4) if ov else None)
            firsts.append(round(float(np.median(fv)), 4) if fv else None)
        res[f'tf_hard_{run}'] = line_h; res[f'tf_other_{run}'] = line_o; res[f'tf_hard_first_{run}'] = firsts
        print(f'  {run} hard  {line_h}\n  {run} other {line_o}\n  {run} hard, first token {firsts}')
    json.dump(res, open('artifacts/oa/q3_entropy.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
