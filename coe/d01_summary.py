#!/usr/bin/env python3
"""coe-dose01 summary (pre-registration `preregistration/coe-dose01.md`): per ladder, the figure's y (strict sigma-covered
held-out members first solved by round r, k 32 per round) against x (cumulative RL / pretraining FLOPs after round r's
sampling), both from rl_needed/rl_curve.json; the crossing of the bar (the full bases' median at round 1); free positive
reductio proofs per round (artifacts/coe/rounds/<ladder>.json); the k 256 reads of the 0.1 % seeds (base and r16, per
family, cut-offs on the strict stratum); the pre-registered tests, IQMs and reading rule.  Inherited arms' read values come
from create-or-elicit's artifacts/coe/dose_summary.json.  Read-only.
  python3 coe/d01_summary.py --out artifacts/coe-dose01/summary.json > artifacts/coe-dose01/summary.md"""
import argparse, json, os, random, statistics as st, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

ARMS = ('full', 'dose1', 'dose01', 'knockout')


def pos_free(rounds_json, r):
    v = rounds_json.get('sigma_subtypes_by_round', {}).get(str(r), {})
    return sum(n for k, n in v.items() if k and k.startswith('pos_free'))


def crossing(o, thr, upto=None):
    for r in o['rounds']:
        if upto is not None and r['round'] > upto:
            break
        if r['heldout_cum'] >= thr:
            return r
    return None


def boschloo(a1, n1, a2, n2, alt):
    """One-sided Boschloo; scipy takes the two groups as COLUMNS (rows = success / failure)."""
    from scipy.stats import boschloo_exact
    if (a1 == 0 and a2 == 0) or (a1 == n1 and a2 == n2):
        return 1.0
    return float(boschloo_exact([[a1, a2], [n1 - a1, n2 - a2]], alternative=alt).pvalue)


def mw(x, y, alt):
    from scipy.stats import mannwhitneyu
    return float(mannwhitneyu(x, y, alternative=alt, method='exact').pvalue)


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = int(n * 0.25)
    core = xs[k:n - k] if n - 2 * k > 0 else xs
    return sum(core) / len(core)


def boot_iqm(xs, b=10000, seed=0):
    rng = random.Random(seed)
    vals = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(b))
    return [vals[int(0.025 * b)], vals[int(0.975 * b) - 1]]


def read_stats(base, fam):
    """Plain k 256 read: per family solved, acquired families (>= 50 % of a family's strict held-out members), strict total,
    and the cut-off share (action truncated / step cap) of attempts on the strict members."""
    from coe.coe_reads import load_rows, summarise
    s = summarise(base, fam, {})
    if s is None:
        return None
    rows, kind = load_rows(base)
    sig = {n for f, d in fam['families'].items() if d['classical'] for n in d['strict_heldout']} | \
        set(fam['generated_classical']['transfer']['strict'])
    cut = att = 0
    for r in rows:
        if r['name'] in sig and kind == 'plain':
            att += r['n_tried']; cut += sum(1 for x in r['reasons'] if 'action truncated' in x or 'step cap' in x)
    return {'strict_solved': s['sigma_covered_solved'], 'n': s['sigma_covered_n'],
            'per_family': {f: v['solved'] for f, v in s['families_heldout'].items()},
            'acquired': s['families_acquired'], 'cut_share_strict': cut / max(1, att), 'cut_share_all': s['cut_share'],
            'proof_classes': s['proof_classes_sigma_covered']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--curve', default='rl_needed/rl_curve.json')
    ap.add_argument('--rounds', default='artifacts/coe/rounds')
    ap.add_argument('--eval', default='artifacts/coe/eval')
    ap.add_argument('--families', default='data/coe/families.json')
    ap.add_argument('--inherited', default='artifacts/coe/dose_summary.json')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    curve = json.load(open(a.curve)); fam = json.load(open(a.families)); inh = json.load(open(a.inherited))['seeds']
    thr = st.median(o['rounds'][0]['heldout_cum'] for o in curve if o['arm'] == 'full')
    lad = {}
    for o in curve:
        rf = os.path.join(a.rounds, ('la_ko_s1_r32' if o['name'] == 'la_ko_s1' and len(o['rounds']) > 24 else o['name']) + '.json')
        rj = json.load(open(rf)) if os.path.exists(rf) else {}
        c16, call = crossing(o, thr, 16), crossing(o, thr)
        last16 = next(r for r in o['rounds'] if r['round'] == min(16, o['rounds'][-1]['round']))
        lad[o['name']] = {
            'arm': o['arm'], 'seed': o['seed'], 'rounds': f"{o['rounds'][0]['round']}-{o['rounds'][-1]['round']}",
            'y_r1': o['rounds'][0]['heldout_cum'], 'y_r16': last16['heldout_cum'], 'x_r16': last16['x_train'],
            'y_last': o['rounds'][-1]['heldout_cum'], 'x_last': o['rounds'][-1]['x_train'],
            'x_total_incl_last_ft': o['x_train_total_incl_last_ft'],
            'cross_round_by16': c16['round'] if c16 else None, 'cross_x_by16': c16['x_train'] if c16 else None,
            'cross_round_any': call['round'] if call else None, 'cross_x_any': call['x_train'] if call else None,
            'pos_free_r1': pos_free(rj, 1) if rj else None, 'pos_free_last': pos_free(rj, o['rounds'][-1]['round']) if rj else None,
            'first_round_pos_free': rj.get('first_round_pos_free_sigma'),
            'sigma_targets_cum_r1': o['rounds'][0]['sigma_targets_cum'], 'sigma_targets_cum_r16': last16['sigma_targets_cum'],
            'y_by_round': [r['heldout_cum'] for r in o['rounds']], 'x_by_round': [round(r['x_train'], 4) for r in o['rounds']]}
    # k 256 reads: new seeds from the rows, inherited seeds from create-or-elicit's dose_summary.json
    reads = {}
    for s in range(3):
        for ck in ('pend', 'r16'):
            for x in ('x0', 'g0'):
                base = os.path.join(a.eval, f'{ck}_dose01_s{s}_{x}')
                if x == 'g0':
                    if os.path.exists(base + '.json'):
                        g = json.load(open(base + '.json'))
                        reads[f'{ck}_dose01_s{s}_g0'] = {'summary_file': base + '.json', 'note': 'guided; see summary file'}
                    continue
                r = read_stats(base, fam)
                if r:
                    reads[f'{ck}_dose01_s{s}_x0'] = r
    for k, v in inh.items():
        reads[f'inherited_{k}'] = {'pend_strict_solved': v.get('pend_strict_solved'), 'pend_acquired': v.get('pend_acquired'),
                                   'r16_strict_solved': v.get('r16_strict_solved'), 'r16_acquired': v.get('r16_acquired')}
    # arm-level tests and IQMs (rounds 1-16; knockout s1's later rounds are exploratory and kept out of the tests)
    by = {arm: [v for v in lad.values() if v['arm'] == arm] for arm in ARMS}
    arm_rows = {}
    for arm, vs in by.items():
        if not vs:
            continue
        y16 = [v['y_r16'] for v in vs]; y1 = [v['y_r1'] for v in vs]
        arm_rows[arm] = {'n': len(vs), 'crossed_by16': sum(v['cross_round_by16'] is not None for v in vs),
                         'y_r1': y1, 'y_r16': y16, 'iqm_y_r16': iqm(y16), 'iqm_y_r16_ci95': boot_iqm(y16),
                         'iqm_y_r1': iqm(y1), 'iqm_y_r1_ci95': boot_iqm(y1),
                         'cross_x_by16': [v['cross_x_by16'] for v in sorted(vs, key=lambda v: v['seed'])]}
    tests = {}
    if 'dose01' in arm_rows:
        d = arm_rows['dose01']
        for other, alt in (('knockout', 'greater'), ('dose1', 'less')):
            o = arm_rows[other]
            tests[f'crossed_by16_dose01_vs_{other}'] = {
                'dose01': f"{d['crossed_by16']}/{d['n']}", other: f"{o['crossed_by16']}/{o['n']}", 'alternative': alt,
                'p_boschloo': boschloo(d['crossed_by16'], d['n'], o['crossed_by16'], o['n'], alt)}
            tests[f'y_r16_dose01_vs_{other}'] = {'dose01': d['y_r16'], other: o['y_r16'], 'alternative': alt,
                                                 'p_mann_whitney_exact': mw(d['y_r16'], o['y_r16'], alt)}
    # pre-registered reading rule
    verdict = None
    if 'dose01' in arm_rows and arm_rows['dose01']['n'] == 3:
        vs = by['dose01']; hits = [v['cross_x_by16'] for v in vs if v['cross_x_by16'] is not None]
        d1max = max(v['cross_x_by16'] for v in by['dose1'])
        if not hits and all(v['y_r16'] <= 5 for v in vs):
            verdict = 'threshold (0.1 % behaves like the knockout)'
        elif len(hits) >= 2 and st.median(hits) > d1max:
            verdict = f'graded (crosses, later than the 1 % arm: median {st.median(hits):.2f}x > {d1max:.2f}x)'
        elif len(hits) >= 2:
            verdict = f'no resolvable dose effect between 0.1 % and 1 % (median {st.median(hits):.2f}x <= {d1max:.2f}x)'
        else:
            verdict = f'intermediate ({len(hits)} / 3 crossed by r16; r16 y {[v["y_r16"] for v in vs]})'
    out = {'threshold': thr, 'ladders': lad, 'reads': reads, 'arms': arm_rows, 'tests': tests, 'reading_rule': verdict}
    json.dump(out, open(a.out, 'w'), indent=1)
    # markdown
    print(f'Bar: {thr:g} of 106 (median of the full bases at round 1).\n')
    print('| ladder | arm | rounds | y r1 | y r16 | first round ≥ bar (x) | x at r16 | x incl. last ft | pos-free σ r1 | first pos-free | y last |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for n, v in sorted(lad.items(), key=lambda kv: (ARMS.index(kv[1]['arm']), kv[1]['seed'])):
        c = f"r{v['cross_round_any']} ({v['cross_x_any']:.2f}×)" if v['cross_round_any'] else 'not reached'
        print(f"| {n} | {v['arm']} | {v['rounds']} | {v['y_r1']} | {v['y_r16']} | {c} | {v['x_r16']:.2f} | "
              f"{v['x_total_incl_last_ft']:.2f} | {v['pos_free_r1']} | {v['first_round_pos_free']} | {v['y_last']} |")
    print('\n| arm | n | crossed by r16 | y r1 (IQM [95 %]) | y r16 (IQM [95 %]) |')
    print('|---|---|---|---|---|')
    for arm, v in arm_rows.items():
        print(f"| {arm} | {v['n']} | {v['crossed_by16']} | {v['y_r1']} ({v['iqm_y_r1']:.2f} [{v['iqm_y_r1_ci95'][0]:.2f}, "
              f"{v['iqm_y_r1_ci95'][1]:.2f}]) | {v['y_r16']} ({v['iqm_y_r16']:.2f} [{v['iqm_y_r16_ci95'][0]:.2f}, {v['iqm_y_r16_ci95'][1]:.2f}]) |")
    if reads:
        print('\n| read (k 256, plain) | strict solved / 106 | families acquired | cut-off share, strict stratum |')
        print('|---|---|---|---|')
        for k, v in reads.items():
            if 'strict_solved' in v:
                print(f"| {k} | {v['strict_solved']} | {', '.join(v['acquired']) or '–'} | {v['cut_share_strict']:.4f} |")
    print('\nTests:', json.dumps(tests, indent=1))
    print('\nReading rule:', verdict)


if __name__ == '__main__':
    main()
