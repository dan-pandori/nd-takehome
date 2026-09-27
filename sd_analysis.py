#!/usr/bin/env python3
"""Everything run stage1-dynamics reports, derived from the pulled files only.

  python3 sd_analysis.py --ev artifacts/sd/ev --metrics artifacts/sd --out artifacts/sd/summary.json

Inputs
  <ev>/<stem>.json      one per evaluated checkpoint, written by sd_eval.py (Lean-alone judge)
  <metrics>/m_<tag>.jsonl   one per training run, written by train.py --metrics
Checkpoint stems name the arm, the seed and the step:
  c_s<k>            arm C   cosine 6,000, control set
  w_s<k>            arm W   WSD 24,000 final (decayed), control set
  w_s<k>.step<N>    arm W's trajectory at step N (stable phase up to 19,000; decaying after)
  w6_s<k>/w12_s<k>  arm W's decay branches from the step-4,800 / step-9,600 state
  f_s<k>[.step<N>]  arm F   WSD 24,000 on the 572,759-record fresh set
  r6<a-d>_s<k>      arm R   same-command replicate of c_s<k>
  r24<a-b>_s0       arm R   same-command replicate of w_s0
Every number printed here is reproducible from those files; nothing is read from a write-up.
"""
import argparse, glob, json, math, os, re, sys, collections, statistics as st

SLICES = ['all', 'len2', 'len3', 'len4', 'len5', 'len6', 'depth3', 'nodepth3_len6']
D3_CUT = 0.44          # NOISE_FLOOR.md's high-mode cut for the depth-3 slice


def parse_stem(s):
    """-> (arm, seed, step, rep) or None"""
    m = re.fullmatch(r'(c|w|f)_s(\d+)(?:\.step(\d+))?', s)
    if m:
        arm, k, step = m.group(1).upper(), int(m.group(2)), m.group(3)
        final = {'C': 6000, 'W': 24000, 'F': 24000}[arm]
        return (arm if step is None else arm + 'traj', k, int(step) if step else final, None)
    m = re.fullmatch(r'w(6|12)_s(\d+)', s)
    if m:
        return ('W' + m.group(1) + 'k', int(m.group(2)), int(m.group(1)) * 1000, None)
    m = re.fullmatch(r'r(6|24)([a-d])_s(\d+)', s)
    if m:
        return ('R' + m.group(1) + 'k', int(m.group(3)), int(m.group(1)) * 1000, m.group(2))
    return None


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for t in range(i, j + 1):
            r[o[t]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ev', default='artifacts/sd/ev')
    ap.add_argument('--metrics', default='artifacts/sd')
    ap.add_argument('--out', default='artifacts/sd/summary.json')
    a = ap.parse_args()

    # ---------------- held-out accuracy cells
    cells = []
    for fn in sorted(glob.glob(os.path.join(a.ev, '*.json'))):
        stem = os.path.basename(fn)[:-5]
        p = parse_stem(stem)
        if p is None:
            continue
        d = json.load(open(fn))
        arm, seed, step, rep = p
        row = {'stem': stem, 'arm': arm, 'seed': seed, 'step': step, 'rep': rep,
               'ckpt': d['ckpt'], 'judge': d['judge'], 'n_params': d['model']['n_params'],
               'mode': d['model']['mode'], 'data': (d['model']['train_args'] or {}).get('data'),
               'sched': (d['model']['train_args'] or {}).get('sched'),
               'parse_fail': d['parse_fail'], 'lean_rej_of_parsed': d['lean_rej_of_parsed'],
               'sample_s': d['timing']['sample_s'], 'lean_wall_s': d['timing']['lean_wall_s']}
        for s in SLICES:
            if s in d['slices']:
                row[s] = d['slices'][s]['rate']
                row[s + '_k'] = d['slices'][s]['solved']
                row[s + '_n'] = d['slices'][s]['n']
        row['term_size_all'] = d['slices']['all']['mean_term_size']
        row['written_lines_all'] = d['slices']['all']['mean_written_lines']
        row['term_size_len6'] = d['slices'].get('len6', {}).get('mean_term_size')
        row['written_lines_len6'] = d['slices'].get('len6', {}).get('mean_written_lines')
        cells.append(row)
    by = {(c['arm'], c['seed'], c['step'], c['rep']): c for c in cells}

    # ---------------- training metrics (validation curves + timings)
    curves = {}
    for fn in sorted(glob.glob(os.path.join(a.metrics, 'm_*.jsonl'))):
        tag = os.path.basename(fn)[2:-6]
        args = None; steps = []; done = None
        for l in open(fn):
            r = json.loads(l)
            if r['kind'] == 'args':
                args = r
            elif r['kind'] == 'step':
                steps.append(r)
            elif r['kind'] == 'done':
                done = r
        if args is None:
            continue
        curves[tag] = {'args': {k: args['args'][k] for k in
                                ('data', 'seed', 'steps', 'sched', 'decay_frac', 'lr', 'min_lr',
                                 'warmup', 'bs', 'out', 'resume', 'ckpt_every', 'state_at')},
                       'n_params': args['n_params'], 'val_slices': args['val_slices'],
                       'steps': [{'step': s['step'], 'loss': s['loss'], 'lr': s['lr'],
                                  'val2k': s.get('val2k'), 'val': s.get('val'), 'secs': s['secs']}
                                 for s in steps],
                       'done': done}

    # ---------------- the pre-registered quantities
    out = {'utc': __import__('time').strftime('%FT%TZ', __import__('time').gmtime()),
           'model_label': {'n_params': 3214336, 'arch': '4 layers, d 256, 8 heads',
                           'format': 'lean_seq (Lean surface form)', 'from_scratch': True, 'cap': 6,
                           'bs': 128, 'lr': '1e-3 -> 1e-4', 'judge': 'Lean alone (2026-09-27 policy)',
                           'heldout': 'data/p2/heldout.jsonl, 5000 theorems, greedy k=1 T=0, sampler batch 512'},
           'cells': cells, 'curves': curves, 'questions': {}}
    Q = out['questions']

    def get(arm, seed, step=None, rep=None):
        for c in cells:
            if c['arm'] == arm and c['seed'] == seed and c['rep'] == rep and (step is None or c['step'] == step):
                return c
        return None

    def paired(a1, a2, sl):
        """[(seed, v1, v2, delta)] over the seeds present in both"""
        rs = []
        for k in range(16):
            x, y = get(a1, k), get(a2, k)
            if x and y and sl in x and sl in y:
                rs.append((k, x[sl], y[sl], y[sl] - x[sl]))
        return rs

    # Q1 saturation: within-seed W6k -> W12k -> W24k
    Q['Q1_saturation'] = {}
    for sl in ('all', 'len6', 'len5', 'len4', 'len3', 'len2', 'depth3', 'nodepth3_len6'):
        d12 = paired('W6k', 'W12k', sl); d24 = paired('W6k', 'W', sl)
        Q['Q1_saturation'][sl] = {
            'W6k_vs_W12k': {'n_seeds': len(d12), 'per_seed': d12,
                            'median_delta': st.median([d for *_, d in d12]) if d12 else None,
                            'n_up_gt_2pp': sum(1 for *_, d in d12 if d > 0.02),
                            'n_within_2pp': sum(1 for *_, d in d12 if abs(d) <= 0.02)},
            'W6k_vs_W24k': {'n_seeds': len(d24), 'per_seed': d24,
                            'median_delta': st.median([d for *_, d in d24]) if d24 else None,
                            'n_up_gt_2pp': sum(1 for *_, d in d24 if d > 0.02),
                            'n_within_2pp': sum(1 for *_, d in d24 if abs(d) <= 0.02)}}
    # E1 falsifier: both W12k and W24k within +-2pp of W6k on len6 on >=6 of 8 seeds
    both = [k for k, *_ in paired('W6k', 'W12k', 'len6')
            if abs(dict((kk, d) for kk, _, _, d in paired('W6k', 'W12k', 'len6'))[k]) <= 0.02
            and k in dict((kk, d) for kk, _, _, d in paired('W6k', 'W', 'len6'))
            and abs(dict((kk, d) for kk, _, _, d in paired('W6k', 'W', 'len6'))[k]) <= 0.02]
    Q['E1_falsifier'] = {'seeds_flat_on_both': sorted(both), 'n': len(both),
                         'fires_if_ge_6': len(both) >= 6}
    # E2 cross-seed sd of len6 at 6k and 24k
    for lab, arm in (('W6k', 'W6k'), ('W12k', 'W12k'), ('W24k', 'W'), ('C', 'C'), ('F24k', 'F')):
        vs = [c['len6'] for c in cells if c['arm'] == arm and 'len6' in c]
        ov = [c['all'] for c in cells if c['arm'] == arm and 'all' in c]
        Q.setdefault('E2_cross_seed_sd', {})[lab] = {
            'n': len(vs), 'len6_mean': st.mean(vs) if vs else None,
            'len6_sd': st.stdev(vs) if len(vs) > 1 else None,
            'all_mean': st.mean(ov) if ov else None,
            'all_sd': st.stdev(ov) if len(ov) > 1 else None}

    # Q2 depth-3 modes along W's trajectory
    traj = collections.defaultdict(dict)
    for c in cells:
        if c['arm'] == 'Wtraj' or (c['arm'] == 'W' and c['step'] == 24000):
            traj[c['seed']][c['step']] = c
    Q['Q2_depth3'] = {'cut': D3_CUT, 'per_seed': {}, 'modes_by_step': {}}
    steps_all = sorted({s for d in traj.values() for s in d})
    for k, d in sorted(traj.items()):
        Q['Q2_depth3']['per_seed'][str(k)] = [
            {'step': s, 'depth3': d[s]['depth3'], 'depth3_k': d[s]['depth3_k'],
             'ci': list(wilson(d[s]['depth3_k'], d[s]['depth3_n'])), 'len6': d[s]['len6'],
             'high_mode': d[s]['depth3'] > D3_CUT} for s in sorted(d)]
    for s in steps_all:
        v = [d[s]['depth3'] for d in traj.values() if s in d]
        hi = sum(1 for x in v if x > D3_CUT)
        lo, hiw = wilson(hi, len(v))
        Q['Q2_depth3']['modes_by_step'][str(s)] = {'n_seeds': len(v), 'n_high': hi,
                                                   'p_high': hi / max(len(v), 1),
                                                   'wilson': [lo, hiw]}
    # E7 falsifier: >=2 of 8 seeds change mode after 6,000 steps (decayed branches)
    ch = []
    for k in range(16):
        x, y = get('W6k', k), get('W', k)
        if x and y and (x['depth3'] > D3_CUT) != (y['depth3'] > D3_CUT):
            ch.append({'seed': k, 'depth3_6k': x['depth3'], 'depth3_24k': y['depth3']})
    Q['E7_mode_changes_6k_to_24k'] = {'changed': ch, 'n_changed': len(ch),
                                      'mode_set_early_dies_if_ge_2': len(ch) >= 2}
    # E9: does depth-3 at step 2,000 predict step 24,000?
    pr = [(d[2000]['depth3'], d[24000]['depth3']) for d in traj.values() if 2000 in d and 24000 in d]
    Q['E9_early_predicts_late'] = {'n': len(pr), 'pairs': pr,
                                   'spearman': spearman([p[0] for p in pr], [p[1] for p in pr]) if len(pr) > 2 else None}

    # Q3 schedule at equal steps: C vs W6k, same seed, same 6,000 batches
    Q['Q3_schedule'] = {}
    for sl in ('all', 'len6', 'len5', 'depth3', 'nodepth3_len6'):
        d = paired('C', 'W6k', sl)
        ds = [x for *_, x in d]
        Q['Q3_schedule'][sl] = {'n_seeds': len(d), 'per_seed': d,
                                'median_delta': st.median(ds) if ds else None,
                                'median_abs_delta': st.median([abs(x) for x in ds]) if ds else None,
                                'n_wsd_higher': sum(1 for x in ds if x > 0)}

    # Q4 steps vs repetition: F vs W, and each arm's own stable-phase 6k -> 24k gain
    def stable(arm_traj, k, s):
        c = get(arm_traj, k, s)
        return c['len6'] if c else None
    Q['Q4_steps_vs_data'] = {'final_F_vs_W': {}, 'own_gain_stable': {}}
    for sl in ('all', 'len6', 'depth3'):
        d = paired('W', 'F', sl)
        Q['Q4_steps_vs_data']['final_F_vs_W'][sl] = {
            'n_seeds': len(d), 'per_seed': d,
            'median_delta': st.median([x for *_, x in d]) if d else None}
    for arm, tr in (('W', 'Wtraj'), ('F', 'Ftraj')):
        rows = []
        for k in range(16):
            a6, a24 = get(tr, k, 6000), get(arm, k, 24000)
            if a6 and a24:
                rows.append({'seed': k, 'len6_6k_stable': a6['len6'], 'len6_24k_final': a24['len6'],
                             'gain': a24['len6'] - a6['len6'],
                             'depth3_6k_stable': a6['depth3'], 'depth3_24k_final': a24['depth3']})
        Q['Q4_steps_vs_data']['own_gain_stable'][arm] = {
            'per_seed': rows,
            'median_gain_len6': st.median([r['gain'] for r in rows]) if rows else None}
    gw = Q['Q4_steps_vs_data']['own_gain_stable']['W']['median_gain_len6']
    gf = Q['Q4_steps_vs_data']['own_gain_stable']['F']['median_gain_len6']
    Q['E11_F_gain_over_W_gain'] = {'W_median_gain': gw, 'F_median_gain': gf,
                                   'ratio': (gf / gw) if (gw and gf is not None) else None,
                                   'steps_not_repetition_if_ge_0.6': (gf / gw >= 0.6) if (gw and gf is not None) else None}

    # ---- POST-HOC (not pre-registered): trajectory-robust estimators.
    # The pre-registered Q4 estimator is each arm's endpoint accuracy, and arm F showed that a single
    # checkpoint's depth-3 rate is a draw from a large within-run oscillation, so the endpoint carries
    # that oscillation rather than the arm's quality.  These estimators use the whole trajectory (and
    # the 200-step loss curve, which has 120 points per run) instead of one checkpoint.  They are
    # labelled post-hoc everywhere they are reported.
    Q['oscillation'] = {}
    for arm_t, arm_f, tagf in (('Wtraj', 'W', 'w_s{}'), ('Ftraj', 'F', 'f_s{}')):
        for k in sorted({c['seed'] for c in cells if c['arm'] == arm_t}):
            pts = sorted([(c['step'], c) for c in cells if c['arm'] == arm_t and c['seed'] == k])
            late = [(s, c) for s, c in pts if s >= 6000]
            fin = get(arm_f, k)
            cur = curves.get(tagf.format(k))
            vd = [(s['step'], (s['val'] or {}).get('depth3')) for s in (cur['steps'] if cur else [])
                  if (s['val'] or {}).get('depth3') is not None]
            v6 = [(s['step'], (s['val'] or {}).get('len6')) for s in (cur['steps'] if cur else [])
                  if (s['val'] or {}).get('len6') is not None]
            d3 = [c['depth3'] for _, c in late]
            l6 = [c['len6'] for _, c in late]
            flips = sum(1 for i in range(1, len(d3)) if (d3[i] > D3_CUT) != (d3[i - 1] > D3_CUT))
            Q['oscillation'][f'{arm_f}_s{k}'] = {
                'n_traj_ckpts': len(pts), 'n_at_or_after_6000': len(late),
                'depth3': {'min': min(d3) if d3 else None, 'max': max(d3) if d3 else None,
                           'median': st.median(d3) if d3 else None,
                           'frac_high_mode': (sum(1 for x in d3 if x > D3_CUT) / len(d3)) if d3 else None,
                           'mode_flips': flips, 'final': fin['depth3'] if fin else None},
                'len6': {'min': min(l6) if l6 else None, 'max': max(l6) if l6 else None,
                         'median': st.median(l6) if l6 else None,
                         'final': fin['len6'] if fin else None},
                'val_depth3_last5k_mean': (st.mean([v for s, v in vd if s > 19000]) if vd else None),
                'val_depth3_min': (min(v for _, v in vd) if vd else None),
                'val_len6_last5k_mean': (st.mean([v for s, v in v6 if s > 19000]) if v6 else None),
                'val_len6_min': (min(v for _, v in v6) if v6 else None)}
    Q['Q4_robust_posthoc'] = {}
    for key in ('val_depth3_last5k_mean', 'val_len6_last5k_mean', 'val_depth3_min', 'val_len6_min'):
        w = [v[key] for g, v in Q['oscillation'].items() if g.startswith('W_') and v[key] is not None]
        f = [v[key] for g, v in Q['oscillation'].items() if g.startswith('F_') and v[key] is not None]
        Q['Q4_robust_posthoc'][key] = {'W_n': len(w), 'W_median': st.median(w) if w else None,
                                       'W_range': [min(w), max(w)] if w else None,
                                       'F_n': len(f), 'F_median': st.median(f) if f else None,
                                       'F_range': [min(f), max(f)] if f else None}
    for key in ('median', 'max', 'frac_high_mode'):
        for sl in ('depth3', 'len6'):
            if sl == 'len6' and key == 'frac_high_mode':
                continue
            w = [v[sl][key] for g, v in Q['oscillation'].items() if g.startswith('W_') and v[sl][key] is not None]
            f = [v[sl][key] for g, v in Q['oscillation'].items() if g.startswith('F_') and v[sl][key] is not None]
            Q['Q4_robust_posthoc'][f'traj_{sl}_{key}'] = {
                'W_n': len(w), 'W_median': st.median(w) if w else None,
                'W_range': [min(w), max(w)] if w else None,
                'F_n': len(f), 'F_median': st.median(f) if f else None,
                'F_range': [min(f), max(f)] if f else None}

    # Q5 is per-length loss a proxy?  trajectory correlation and fixed-step ranking
    def val_at(tag, step, key):
        c = curves.get(tag)
        if not c:
            return None
        for s in c['steps']:
            if s['step'] == step:
                return (s['val'] or {}).get(key) if key != 'val2k' else s['val2k']
        return None
    Q['Q5_proxy'] = {'trajectory': {}, 'fixed_step_ranking': {}}
    for key, sl in (('len6', 'len6'), ('depth3', 'depth3'), ('all', 'all'), ('val2k', 'len6')):
        xs, ys, per_seed = [], [], {}
        for k, d in sorted(traj.items()):
            vv, aa = [], []
            for s in sorted(d):
                v = val_at(f'w_s{k}', s, key)
                if v is not None and sl in d[s]:
                    vv.append(v); aa.append(d[s][sl])
            if len(vv) > 2:
                per_seed[str(k)] = {'n': len(vv), 'spearman': spearman(vv, aa)}
                xs += vv; ys += aa
        Q['Q5_proxy']['trajectory'][f'val_{key}_vs_acc_{sl}'] = {
            'n_points': len(xs), 'spearman_pooled': spearman(xs, ys) if len(xs) > 2 else None,
            'per_seed': per_seed}
    for step, arms in ((24000, ('W',)), (6000, ('C',))):
        for key, sl in (('len6', 'len6'), ('depth3', 'depth3'), ('val2k', 'len6'), ('val2k', 'all')):
            xs, ys, seeds = [], [], []
            for arm in arms:
                tagf = {'W': 'w_s{}', 'C': 'c_s{}'}[arm]
                for k in range(16):
                    c = get(arm, k, step)
                    v = val_at(tagf.format(k), step, key)
                    if c and v is not None and sl in c:
                        xs.append(v); ys.append(c[sl]); seeds.append(k)
            Q['Q5_proxy']['fixed_step_ranking'][f'step{step}_val_{key}_vs_acc_{sl}'] = {
                'n_seeds': len(xs), 'seeds': seeds, 'val': xs, 'acc': ys,
                'spearman': spearman(xs, ys) if len(xs) > 2 else None}

    # E5/E6: long-proof loss -- does it keep falling, and does val2k stay flat?
    Q['E5_long_loss'] = {}
    for k in sorted(traj):
        c = curves.get(f'w_s{k}')
        if not c:
            continue
        v6 = [(s['step'], (s['val'] or {}).get('len6')) for s in c['steps'] if (s['val'] or {}).get('len6') is not None]
        vd = [(s['step'], (s['val'] or {}).get('depth3')) for s in c['steps'] if (s['val'] or {}).get('depth3') is not None]
        v2 = [(s['step'], s['val2k']) for s in c['steps'] if s.get('val2k') is not None]
        def summ(v):
            if not v:
                return None
            at6 = next((y for x, y in v if x == 6000), None)
            end = v[-1][1]; mn = min(y for _, y in v); arg = min(v, key=lambda t: t[1])[0]
            return {'at_6000': at6, 'at_end': end, 'min': mn, 'argmin_step': arg,
                    'end_over_min': (end / mn) if mn else None,
                    'falls_6k_to_end': (at6 is not None and end < at6)}
        Q['E5_long_loss'][str(k)] = {'len6': summ(v6), 'depth3': summ(vd), 'val2k': summ(v2)}
    Q['E6_val2k_flat'] = []
    for k in sorted(traj):
        e = Q['E5_long_loss'].get(str(k))
        x, y = get('W6k', k), get('W', k)
        if e and e['val2k'] and x and y:
            Q['E6_val2k_flat'].append({'seed': k,
                                       'dval2k_6k_to_24k': e['val2k']['at_end'] - (e['val2k']['at_6000'] or 0),
                                       'dlen6_acc_6k_to_24k': y['len6'] - x['len6']})

    # arm R: the same-command replicate floor (addendum 1)
    Q['R_replicate_floor'] = {}
    for lab, arm, base in (('6k', 'R6k', 'C'), ('24k', 'R24k', 'W')):
        for seed in sorted({c['seed'] for c in cells if c['arm'] == arm}):
            reps = sorted([c for c in cells if c['arm'] == arm and c['seed'] == seed],
                          key=lambda c: c['rep'] or '')
            b = get(base, seed)
            grp = {'reps': [{'stem': c['stem'], 'all': c['all'], 'len6': c['len6'],
                             'depth3': c['depth3'], 'len5': c['len5'], 'len2': c['len2'],
                             'len3': c['len3'], 'len4': c['len4']} for c in reps],
                   'same_pod_n': len(reps)}
            if b:
                grp['cross_pod_baseline'] = {'stem': b['stem'], 'all': b['all'], 'len6': b['len6'],
                                             'depth3': b['depth3']}
            for sl in ('all', 'len6', 'len5', 'depth3'):
                v = [c[sl] for c in reps if sl in c]
                vall = v + ([b[sl]] if b and sl in b else [])
                grp[sl] = {'n_same_pod': len(v),
                           'sd_same_pod': st.stdev(v) if len(v) > 1 else None,
                           'range_same_pod': [min(v), max(v)] if v else None,
                           'n_with_baseline': len(vall),
                           'sd_with_baseline': st.stdev(vall) if len(vall) > 1 else None,
                           'range_with_baseline': [min(vall), max(vall)] if vall else None}
            d3 = [c['depth3'] for c in reps] + ([b['depth3']] if b else [])
            grp['depth3_modes'] = {'n_high': sum(1 for x in d3 if x > D3_CUT), 'n': len(d3),
                                   'straddles_cut': 0 < sum(1 for x in d3 if x > D3_CUT) < len(d3)}
            Q['R_replicate_floor'][f'{lab}_seed{seed}'] = grp

    # E16: the cost of the instrumentation
    ov = []
    for tag, c in curves.items():
        if c['done'] and c['done'].get('val_full_overhead') is not None:
            ov.append({'tag': tag, 'steps_run': c['done']['steps_run'], 'secs': c['done']['secs'],
                       'val_full_s': c['done']['val_full_s'],
                       'overhead': c['done']['val_full_overhead']})
    Q['E16_instrumentation_overhead'] = {
        'per_run': ov, 'n': len(ov),
        'median': st.median([x['overhead'] for x in ov]) if ov else None,
        'range': [min(x['overhead'] for x in ov), max(x['overhead'] for x in ov)] if ov else None}

    # proof length in lines and term size
    Q['proof_length'] = {}
    for arm in ('C', 'W6k', 'W12k', 'W', 'F'):
        rows = [c for c in cells if c['arm'] == arm]
        if rows:
            Q['proof_length'][arm] = {
                'n_ckpts': len(rows),
                'mean_term_size_all': st.mean([r['term_size_all'] for r in rows if r['term_size_all']]),
                'mean_written_lines_all': st.mean([r['written_lines_all'] for r in rows if r['written_lines_all']]),
                'mean_term_size_len6': st.mean([r['term_size_len6'] for r in rows if r['term_size_len6']]),
                'mean_written_lines_len6': st.mean([r['written_lines_len6'] for r in rows if r['written_lines_len6']])}

    json.dump(out, open(a.out, 'w'), indent=1)
    print(f'{len(cells)} evaluated checkpoints, {len(curves)} training runs -> {a.out}')
    for arm in sorted({c['arm'] for c in cells}):
        v = [c for c in cells if c['arm'] == arm]
        print(f"  {arm:7s} {len(v):3d} cells  seeds {sorted({c['seed'] for c in v})}")


if __name__ == '__main__':
    main()
