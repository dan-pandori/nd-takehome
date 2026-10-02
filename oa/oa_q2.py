#!/usr/bin/env python3
"""organism-analysis Q2: what RL learns, step by step (preregistration Q2).

Hard step = a reference-proof step with log p < -4 nats at r0 (pend for c12 / c6; the start for rfc), per-step
contributions T 1.0, name-base marginalised (trajectory's tj_score).  Class = oa_common.step_class of the action.
Theorem status per (run, seed): 'start' = r0 x0 solves; 'rl' = r0 x0 does not, some read r1..r8 (x0 or x1) does;
'never' = no read r1..r8 (x0 or x1) solves (RL never sampled a proof of it on the read side; no evaluation theorem is
ever an RL training target).  Writes artifacts/oa/q2_results.json, data/oa/q2_steps.jsonl; prints the tables.
"""
import collections, json, os, sys
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oa_load import SEEDS, STARTS, read_both, ref_inputs, score, targets_meta, rfc_label
from oa_common import step_class

HARD = -4.0
RND = ['pend', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
rng = np.random.default_rng(0)


def status_c(run, seed):
    r0 = read_both(run, f's{seed}_pend', 0)
    later = [read_both(run, f's{seed}_r{k}', x) for k in range(1, 9) for x in (0, 1)]
    return {n: ('start' if r0[n][0] > 0 else 'rl' if any(d[n][0] > 0 for d in later) else 'never') for n in r0}


def status_rfc(seed, start):
    r0 = read_both(*rfc_label(seed, start, 0), 0)
    later = [read_both(*rfc_label(seed, start, k), x) for k in (2, 4, 8) for x in (0, 1)]
    return {n: ('start' if r0[n][0] > 0 else 'rl' if any(d[n][0] > 0 for d in later) else 'never') for n in r0}


def steps():
    refs = ref_inputs()
    out = []
    for run in ('c12', 'c6'):
        for seed in SEEDS:
            st = status_c(run, seed); meta = targets_meta(run, seed)
            sc = {ck: score(run, seed, ck) for ck in RND}
            for name in refs:
                tid = 'ref:' + name
                if tid not in sc['pend']:
                    continue
                acts = meta[tid]['actions_b0']
                for i, a in enumerate(acts):
                    lp = [sc[ck][tid]['step_lp'][i] for ck in RND]
                    out.append({'run': run, 'seed': seed, 'start': 'pend', 'name': name, 'i': i, 'cls': step_class(a),
                                'status': st[name], 'lp': lp, 'hard': lp[0] < HARD, 'action': a})
    for seed in SEEDS:
        for start in STARTS:
            st = status_rfc(seed, start); meta = targets_meta('rfc', seed, start)
            sc = {ck: score('rfc', seed, ck, start) for ck in ('r0', 'r2', 'r4', 'r8')}
            for name in refs:
                tid = 'ref:' + name
                if tid not in sc['r0']:
                    continue
                for i, a in enumerate(meta[tid]['actions_b0']):
                    lp = [sc[ck][tid]['step_lp'][i] for ck in ('r0', 'r2', 'r4', 'r8')]
                    out.append({'run': 'rfc', 'seed': seed, 'start': start, 'name': name, 'i': i, 'cls': step_class(a),
                                'status': st[name], 'lp': lp, 'hard': lp[0] < HARD, 'action': a})
    return out


def boot_ci(groups_by_thm, stat, B=1000):
    """theorem-cluster bootstrap of stat(list of values)."""
    keys = list(groups_by_thm)
    if not keys:
        return [None, None]
    v = []
    for _ in range(B):
        ks = [keys[j] for j in rng.integers(0, len(keys), len(keys))]
        v.append(stat([x for k in ks for x in groups_by_thm[k]]))
    return [round(float(np.percentile(v, 2.5)), 2), round(float(np.percentile(v, 97.5)), 2)]


def main():
    S = steps()
    os.makedirs('data/oa', exist_ok=True)
    with open('data/oa/q2_steps.jsonl', 'w') as f:
        for s in S:
            f.write(json.dumps(s) + '\n')
    res = {}
    H = [s for s in S if s['hard']]
    # ---- taxonomy ----
    print('Hard steps (r0 log p < -4) by class: count (share) per run, pooled over seeds; c12 / c6 at pend, rfc at starts')
    tax = {}
    for run in ('c12', 'c6', 'rfc'):
        c = collections.Counter(s['cls'] for s in H if s['run'] == run)
        tot = sum(c.values())
        tax[run] = {k: [v, round(v / tot, 3)] for k, v in c.most_common()}
        print(f'  {run}: n {tot}: ' + ', '.join(f'{k} {v} ({v / tot:.0%})' for k, v in c.most_common()))
        box = sum(v for k, v in c.items() if k.startswith('box')) + c['and_proj']
        print(f'        box openers + and_proj: {box / tot:.0%}')
        tax[run]['_box_plus_proj'] = round(box / tot, 3)
    res['taxonomy'] = tax
    # ---- per-class per-round median log p (c12 / c6), all hard steps; and by status ----
    print('\nMedian hard-step log p by class and round (pooled seeds; n = hard steps). Rounds: r0(pend) r1..r8')
    traj = {}
    for run in ('c12', 'c6'):
        for status in ('all', 'rl', 'never'):
            for cls in [k for k, v in collections.Counter(s['cls'] for s in H if s['run'] == run).most_common()]:
                g = [s for s in H if s['run'] == run and s['cls'] == cls and (status == 'all' or s['status'] == status)]
                if len(g) < 5:
                    continue
                med = [round(float(np.median([s['lp'][k] for s in g])), 2) for k in range(9)]
                traj[f'{run}|{status}|{cls}'] = {'n': len(g), 'median': med}
                if status == 'all':
                    print(f'  {run} {cls:<13} n {len(g):>4}: ' + ' '.join(f'{m:>6}' for m in med))
    res['class_round_median'] = traj
    # rfc rounds r0 r2 r4 r8
    for start in STARTS:
        for cls in ('box:imp', 'box:neg', 'box:orelim', 'box:bycontra', 'and_proj', 'app'):
            g = [s for s in H if s['run'] == 'rfc' and s['start'] == start and s['cls'] == cls]
            if len(g) >= 5:
                traj[f'rfc {start}|all|{cls}'] = {'n': len(g), 'median': [round(float(np.median([s['lp'][k] for s in g])), 2) for k in range(4)]}
    # ---- transfer: gain of hard steps in never-solved theorems, by class, vs same class in rl-solved and vs matched control ----
    print('\nGain r0 -> r8 (nats) of hard steps, by class: rl-solved theorems vs never-solved; matched control = never-solved hard steps'
          '\nof OTHER classes in the same run/seed and r0 log p bin (1 nat); diff = class - control (stratified), 95 % theorem bootstrap.')
    tr = {}
    for run in ('c12', 'c6'):
        Hr = [s for s in H if s['run'] == run]
        for cls in [k for k, v in collections.Counter(s['cls'] for s in Hr).most_common()]:
            d = {}
            for status in ('start', 'rl', 'never'):
                g = [s['lp'][8] - s['lp'][0] for s in Hr if s['cls'] == cls and s['status'] == status]
                d[status] = [round(float(np.median(g)), 2) if g else None, len(g)]
            # matched control among never-solved
            nev = [s for s in Hr if s['status'] == 'never']
            tgt = [s for s in nev if s['cls'] == cls]
            if len(tgt) >= 5:
                bins = collections.defaultdict(lambda: ([], []))
                for s in nev:
                    k = (s['seed'], int(np.floor(s['lp'][0])))
                    bins[k][0 if s['cls'] == cls else 1].append(s)
                pairs = [(k, a, b) for k, (a, b) in bins.items() if a and b]

                def strat(sel_pairs):
                    w = sum(len(a) for _, a, _ in sel_pairs)
                    if not w:
                        return np.nan
                    return sum(len(a) * (np.mean([x['lp'][8] - x['lp'][0] for x in a]) -
                                         np.mean([x['lp'][8] - x['lp'][0] for x in b])) for _, a, b in sel_pairs) / w
                diff = strat(pairs)
                # bootstrap over theorems: resample theorem names, rebuild
                names = sorted({s['name'] for s in nev})
                bs = []
                for _ in range(500):
                    pick = collections.Counter(names[j] for j in rng.integers(0, len(names), len(names)))
                    bb = collections.defaultdict(lambda: ([], []))
                    for s in nev:
                        for _r in range(pick.get(s['name'], 0)):
                            bb[(s['seed'], int(np.floor(s['lp'][0])))][0 if s['cls'] == cls else 1].append(s)
                    v = strat([(k, a, b) for k, (a, b) in bb.items() if a and b])
                    if not np.isnan(v):
                        bs.append(v)
                d['never_matched_diff'] = [round(float(diff), 2), [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)],
                                           sum(len(a) for _, a, _ in pairs)]
            tr[f'{run}|{cls}'] = d
        print(f'  {run}: class        start-solved      rl-solved        never-solved    never: class - matched control [CI] (n matched)')
        for cls in [k for k, v in collections.Counter(s['cls'] for s in Hr).most_common()]:
            d = tr[f'{run}|{cls}']
            m = d.get('never_matched_diff')
            print(f'      {cls:<13} {str(d["start"]):<17} {str(d["rl"]):<16} {str(d["never"]):<15} '
                  + (f'{m[0]:+.2f} {m[1]} ({m[2]})' if m else '-'))
    res['transfer'] = tr
    # cross-class Spearman (classes with >= 5 hard steps in both)
    for run in ('c12', 'c6'):
        xs, ys, cl = [], [], []
        for k, d in tr.items():
            if k.startswith(run + '|') and d['rl'][1] >= 5 and d['never'][1] >= 5:
                xs.append(d['rl'][0]); ys.append(d['never'][0]); cl.append(k.split('|')[1])
        rho = spearmanr(xs, ys)[0] if len(xs) >= 3 else None
        res.setdefault('cross_class_spearman', {})[run] = [round(float(rho), 3) if rho is not None else None, len(xs), cl]
        print(f'  {run}: Spearman over {len(xs)} classes, rl-solved vs never-solved median gain: {rho:.3f}')
    # partial R^2 of class in gain ~ lp0 + seed + class (hard steps)
    for run in ('c12', 'c6'):
        for status in ('all', 'never'):
            g = [s for s in H if s['run'] == run and (status == 'all' or s['status'] == status)]
            y = np.array([s['lp'][8] - s['lp'][0] for s in g])
            base = np.column_stack([np.ones(len(g)), [s['lp'][0] for s in g]] + [[s['seed'] == k for s in g] for k in (1, 2)])
            cls_list = sorted({s['cls'] for s in g})[1:]
            full = np.column_stack([base] + [[s['cls'] == c for s in g] for c in cls_list]) if cls_list else base
            rss = lambda X: float(np.sum((y - X @ np.linalg.lstsq(X.astype(float), y, rcond=None)[0]) ** 2))
            r0, r1 = rss(base.astype(float)), rss(full.astype(float))
            res.setdefault('partial_r2_class', {})[f'{run}|{status}'] = [round(1 - r1 / r0, 3), len(g)]
            print(f'  {run} {status:<5}: partial R^2 of class (gain ~ r0 lp + seed + class) = {1 - r1 / r0:.3f}  (n {len(g)})')
    # theorem-level: do never-solved theorems gain at all?  median per-theorem worst-hard-step gain
    for run in ('c12', 'c6'):
        for status in ('rl', 'never'):
            g = collections.defaultdict(list)
            for s in H:
                if s['run'] == run and s['status'] == status:
                    g[(s['seed'], s['name'])].append(s['lp'][8] - s['lp'][0])
            v = [np.median(x) for x in g.values()]
            res.setdefault('thm_median_gain', {})[f'{run}|{status}'] = [round(float(np.median(v)), 2), len(v)]
    print('  per-theorem median hard-step gain:', res['thm_median_gain'])
    # ---- POST HOC (not pre-registered): box:neg split by whether the box proves a double negation (¬¬X) ----
    print('\nPOST HOC: box:neg hard steps split by the formula the box proves: ¬¬X vs other ¬X (gain r0 -> r8, median; by status)')
    ph = {}
    for run in ('c12', 'c6'):
        g = [s for s in H if s['run'] == run and s['cls'] == 'box:neg']
        for lab, sel in (('dneg', [s for s in g if '( ¬ ( ¬' in s['action'].split(':=')[0]]),
                         ('neg_other', [s for s in g if '( ¬ ( ¬' not in s['action'].split(':=')[0]])):
            row = {'n': len(sel), 'r0_median': round(float(np.median([s['lp'][0] for s in sel])), 2),
                   'gain_median': round(float(np.median([s['lp'][8] - s['lp'][0] for s in sel])), 2),
                   'by_status': {st: [round(float(np.median([s['lp'][8] - s['lp'][0] for s in sel if s['status'] == st])), 2),
                                      sum(s['status'] == st for s in sel)] for st in ('start', 'rl', 'never') if any(s['status'] == st for s in sel)},
                   'per_seed_gain': [round(float(np.median([s['lp'][8] - s['lp'][0] for s in sel if s['seed'] == k])), 2) for k in SEEDS]}
            ph[f'{run}|{lab}'] = row
            print(f'  {run} {lab:<10} {row}')
    res['posthoc_dneg'] = ph
    json.dump(res, open('artifacts/oa/q2_results.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
