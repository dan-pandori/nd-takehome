#!/usr/bin/env python3
"""Numbers for run `state-frontier` -> artifacts/sf2/summary.json and a printed table.

  python3 sf_analysis.py [--term_size] > artifacts/sf2/tables.txt

Question 1 (re-sample): every artifacts/sf2/rs/<label>.jsonl is one checkpoint sampled k = 256, T 0.8 on the 224
transfer theorems with L_true >= 11 (`n_ok` = Lean-accepted samples of 256; `lean_judge`, Lean alone).
Question 2 (lottery): the depth-3 slice (`pat.depth3` of data/p2/heldout.jsonl, 500) of held-out greedy for every
state-conditioned Stage-1 seed: on file (state-env, commit b0926966) and new (artifacts/sf2/heldout_*.jsonl),
against the control configuration's 52 cells (artifacts/nf/summary.json, `NOISE_FLOOR.md`).
Ladders: artifacts/sf2/ladders.json (`se_analysis.py` on this run's ladders) and state-env's summary (b0926966).
L_true is ND-derived: an upper bound on proof length under Lean.
"""
import argparse, collections, glob, json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SE = 'b09269662d46f74a51c3af92c6e805f3fa2681ab'      # origin/dan_state-env, the reviewed state-env artifacts
HIGH = 0.44                                           # NOISE_FLOOR.md rule 5: high mode iff depth-3 rate > 0.44
P_CTRL = 24 / 52


def git(path, rev='HEAD'):
    return subprocess.check_output(['git', 'show', f'{rev}:{path}']).decode()


def jl(text):
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - r) / d, 4), round((c + r) / d, 4))


def iqm(xs):
    xs = sorted(xs); n = len(xs); lo, hi = n / 4, 3 * n / 4
    w = [max(0.0, min(i + 1, hi) - max(i, lo)) for i in range(n)]      # fractional-weight IQM (Agarwal et al.)
    return sum(x * wi for x, wi in zip(xs, w)) / sum(w)


def boot_iqm(xs, B=10000, seed=0):
    rng = random.Random(seed); n = len(xs)
    v = sorted(iqm([xs[rng.randrange(n)] for _ in range(n)]) for _ in range(B))
    return (round(v[int(0.025 * B)], 3), round(v[int(0.975 * B) - 1], 3))


def binom_tail_ge(k, n, p):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def family(label):
    return label.split('_')[1]          # T1_S_s0 -> S ; base_C0_s1 -> C0


def resample():
    rows, meta = {}, {}
    for fn in sorted(glob.glob('artifacts/sf2/rs/*.jsonl')):
        lab = os.path.basename(fn)[:-6]
        rows[lab] = {r['name']: r for r in map(json.loads, open(fn))}
        s = json.load(open(fn[:-6] + '.json'))
        m = {'ckpt': s.get('src_ckpt'), 'k': s['k'], 'temperature': s['temperature'], 'wall_s': s.get('wall_s')}
        if 'gen_stats' in s:        # whole-proof: samples that hit max_new
            g = s['gen_stats']; m.update(max_new=s['max_new'], batch=s['batch'], hit_max_new=g['hit_max_new'], rows=g['rows'],
                                         peak_alloc_gb=s.get('peak_alloc_gb'))
        if 'env' in s:
            e = s['env']; m.update(batch=s['batch'], max_action=s['max_action'], max_steps=s['max_steps'],
                                   env_end=e['env_end'], peak_alloc_gb=e.get('peak_alloc_gb'),
                                   hit_max_action=e['action_declen_hist'].get(str(s['max_action']), 0))
        meta[lab] = m
    # pre-registered: a whole-proof model with > 0.1 % of samples at max_new is re-run at 1,024 and that run is the one
    # reported; the 512 run is kept as '<label>_mn512'.  '_ma512' (state, max_action 512) is a diagnostic only.
    for lab in [l for l in rows if l.endswith('_mn1024')]:
        base = lab[:-len('_mn1024')]
        if base in rows:
            rows[base + '_mn512'], meta[base + '_mn512'] = rows.pop(base), meta.pop(base)
        rows[base], meta[base] = rows.pop(lab), meta.pop(lab)
        meta[base]['rerun_of_max_new_512'] = True
    out = {}
    for lab, R in rows.items():
        by = collections.defaultdict(lambda: [0, 0, 0])     # L_true -> [solved, n, successes]
        for r in R.values():
            b = by[r['L_true']]; b[0] += r['solved']; b[1] += 1; b[2] += r['n_ok']
        ge13 = {n: r['n_ok'] for n, r in R.items() if r['L_true'] >= 13 and r['n_ok']}
        att13 = sum(r['n_tried'] for r in R.values() if r['L_true'] >= 13)
        out[lab] = {'family': family(lab), 'kind': lab.split('_')[0], **meta[lab],
                    'N13': len(ge13), 'succ13': sum(ge13.values()), 'att13': att13,
                    'rate13': sum(ge13.values()) / max(1, att13), 'ge13': ge13,
                    'solved_11_12': sum(by[L][0] for L in (11, 12)),
                    'by_L_true': {str(L): {'solved': v[0], 'n': v[1], 'succ': v[2], 'rate': round(v[2] / (256 * v[1]), 5)}
                                  for L, v in sorted(by.items())}}
    return rows, out


def q1_readings(rows, rs):
    main = [l for l in rs if l.count('_') == 2]          # T1_S_s0 etc.; diagnostics carry a 4th field
    st = [l for l in main if l.startswith('T1_') and rs[l]['family'] in ('S', 'SN')]
    c0 = [l for l in main if l.startswith('T1_C0')]
    names13 = sorted({n for l in rows for n, r in rows[l].items() if r['L_true'] >= 13})
    by_thm = {n: {l: rows[l][n]['n_ok'] for l in rows} for n in names13}
    succ = {n: sum(by_thm[n][l] for l in st) for n in names13}
    tot = sum(succ.values())
    nmod = {n: sum(1 for l in st if by_thm[n][l] > 0) for n in names13}
    share1126 = succ.get('la_transfer_1126', 0) / tot if tot else None
    multi = [n for n in names13 if nmod[n] >= 2]
    other_multi = [n for n in multi if n != 'la_transfer_1126']
    if share1126 is not None and share1126 >= 0.8 and not other_multi:
        reading = 'one lucky theorem'
    elif len(multi) >= 3:
        reading = 'a real, low rate'
    else:
        reading = 'narrow (between the pre-registered readings)'

    def sign(Ls, a_labels, b_labels):       # per theorem: pooled state T1 vs pooled C0 T1 success rate (paired by theorem)
        wins = loss = 0
        for n, r0 in rows[a_labels[0]].items():
            if r0['L_true'] not in Ls:
                continue
            a = sum(rows[l][n]['n_ok'] for l in a_labels) / len(a_labels)
            b = sum(rows[l][n]['n_ok'] for l in b_labels) / len(b_labels)
            wins += a > b; loss += b > a
        m = wins + loss
        p = min(1.0, 2 * binom_tail_ge(max(wins, loss), m, 0.5)) if m else None
        return {'state_better': wins, 'c0_better': loss, 'ties_excluded': True, 'two_sided_p': p}
    return {'state_T1_models': st, 'c0_T1_models': c0, 'ge13_by_theorem': by_thm,
            'state_T1_successes_ge13': succ, 'state_T1_models_solving': nmod,
            'share_la_transfer_1126': share1126, 'theorems_solved_by_ge2_state_T1': multi, 'reading': reading,
            'sign_ge13': sign({13, 14}, st, c0) if st and c0 else None,
            'sign_11_12': sign({11, 12}, st, c0) if st and c0 else None}


def lottery():
    pat = {}
    for l in open('data/p2/heldout.jsonl'):
        r = json.loads(l); pat[r['name']] = bool((r.get('pat') or {}).get('depth3'))

    def d3(rs):
        d = [r for r in rs if pat.get(r['name'])]
        return {'depth3_rate': round(sum(r['solved'] for r in d) / len(d), 4), 'depth3_n': len(d),
                'overall': round(sum(r['solved'] for r in rs) / len(rs), 4)}
    seeds = {}
    for a in ('S', 'SH', 'SN'):         # state-env's six state-conditioned Stage-1 checkpoints
        for s in (0, 1):
            p = f'artifacts/se/heldout_{a}_s{s}.jsonl'
            seeds[f'{a}_s{s}'] = {'source': f'{p} @ {SE[:8]} (state-env)', 'new': False, **d3(jl(git(p, SE)))}
    for fn in sorted(glob.glob('artifacts/sf2/heldout_*.jsonl')):
        k = os.path.basename(fn)[8:-6]
        seeds[k] = {'source': fn, 'new': True, **d3([json.loads(l) for l in open(fn)])}
    for v in seeds.values():
        v['high'] = v['depth3_rate'] > HIGH
    new = [v for v in seeds.values() if v['new']]
    nh, n = sum(v['high'] for v in new), len(new)
    ah, an = sum(v['high'] for v in seeds.values()), len(seeds)
    ctrl = list(json.loads(git('artifacts/nf/summary.json'))['floors']['heldout_depth3_slice']['values'].values())
    rates = [v['depth3_rate'] for v in seeds.values()]
    return {'seeds': seeds, 'threshold': HIGH, 'control': {'source': 'artifacts/nf/summary.json floors.heldout_depth3_slice',
            'n': len(ctrl), 'high': sum(x > HIGH for x in ctrl), 'p_high': P_CTRL, 'wilson': wilson(24, 52), 'values': ctrl},
            'new_high': nh, 'new_n': n, 'new_low': n - nh,
            'falsifier_fired': (n - nh) >= 2,
            'p_new_ge_observed_high_under_control': binom_tail_ge(nh, n, P_CTRL) if n else None,
            'all_high': ah, 'all_n': an, 'all_wilson': wilson(ah, an),
            'p_all_ge_observed_high_under_control': binom_tail_ge(ah, an, P_CTRL),
            'depth3_rate_sd_state': round((sum((x - sum(rates) / len(rates)) ** 2 for x in rates) / (len(rates) - 1)) ** .5, 4)}


def ladders():
    se = json.loads(git('artifacts/se/summary.json', SE))['ladders']['runs']
    out = {}
    for n, x in se.items():
        if '_SH_' in n:
            continue
        d = x['derived']; out[n] = {'source': f'artifacts/se/summary.json @ {SE[:8]}', 'solved': d['solved'], 'lstar': d['lstar'],
                                    'ge13': d['solved_ge13'], 'ge13_names': [t[0] for t in d['solved_ge13_names']],
                                    'solved_11_12': d['by_bin']['11']['solved'] + d['by_bin']['12']['solved']}
    if os.path.exists('artifacts/sf2/ladders.json'):
        for n, x in json.load(open('artifacts/sf2/ladders.json'))['runs'].items():
            d = x['derived']; out[n] = {'source': 'artifacts/sf2/ladders.json', 'solved': d['solved'], 'lstar': d['lstar'],
                                        'ge13': d['solved_ge13'], 'ge13_names': [t[0] for t in d['solved_ge13_names']],
                                        'solved_11_12': d['by_bin']['11']['solved'] + d['by_bin']['12']['solved'],
                                        'last_round': x.get('last_round')}
    agg = {}
    for key in ('la_T1_S', 'la_frozen_S', 'la_T1_SN', 'la_frozen_SN'):
        v = {n: out[n] for n in out if n.rsplit('_', 1)[0] == key}
        if v:
            xs = [x['solved'] for x in v.values()]
            agg[key] = {'n': len(xs), 'per_seed': {n: x['solved'] for n, x in sorted(v.items())},
                        'lstar': {n: x['lstar'] for n, x in sorted(v.items())},
                        'ge13': {n: x['ge13'] for n, x in sorted(v.items())},
                        'ge13_names': sorted({t for x in v.values() for t in x['ge13_names']}),
                        'iqm': round(iqm(xs), 1), 'iqm_ci95': boot_iqm(xs) if len(xs) > 2 else None,
                        'sd': round((sum((x - sum(xs) / len(xs)) ** 2 for x in xs) / (len(xs) - 1)) ** .5, 1) if len(xs) > 1 else None}
    return {'runs': out, 'aggregate': agg}


def term_sizes(rows, labels):
    """lean_check term size of one shortest accepted proof per (model, L_true >= 13 theorem)."""
    import nd2lean
    from lean_check import check
    items = []
    for l in labels:
        for n, r in rows[l].items():
            if r['L_true'] >= 13 and r['proofs']:
                i = min(range(len(r['proofs'])), key=lambda j: r['written_lens'][j])
                items.append((l, n, r['L_true'], r['written_lens'][i], nd2lean.translate(r['prompt'], r['proofs'][i], require_all_pr=False)))
    res, _, _ = check([x[4] for x in items], workers=4) if items else ([], 0, 0)
    return [{'model': l, 'name': n, 'L_true': L, 'lines': w, 'term_size': r.get('size'), 'lean_check_ok': r['ok']}
            for (l, n, L, w, _), r in zip(items, res)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--term_size', action='store_true'); a = ap.parse_args()
    rows, rs = resample()
    S = {'run': 'state-frontier', 'judge': 'Lean alone (lean_judge); nd_verify judges nothing',
         'L_true_note': 'ND-derived; an upper bound on proof length under Lean',
         'resample': {'pool': 'data/sf2/long.jsonl = transfer theorems with L_true >= 11 (224)', 'models': rs},
         'q1': q1_readings(rows, rs) if rows else None, 'q2_lottery': lottery(), 'ladders': ladders()}
    if a.term_size and rows:
        S['term_size_ge13'] = term_sizes(rows, [l for l in rows])
    json.dump(S, open('artifacts/sf2/summary.json', 'w'), indent=1)
    print(f"{'model':16s} {'N13':>4s} {'succ13':>6s} {'rate13':>8s} {'sol11-12':>8s}  trunc")
    for l, m in sorted(rs.items()):
        tr = f"{m['hit_max_new']}/{m['rows']}" if 'hit_max_new' in m else f"att {m['env_end'].get('truncated', 0)}/{sum(m['env_end'].values())} act {m['hit_max_action']}"
        print(f"{l:16s} {m['N13']:4d} {m['succ13']:6d} {m['rate13']:8.5f} {m['solved_11_12']:8d}  {tr}")
    if S['q1']:
        q = S['q1']; print('Q1 reading:', q['reading'], '| share 1126', q['share_la_transfer_1126'],
                           '| solved by >=2 state T1:', q['theorems_solved_by_ge2_state_T1'])
        print('sign >=13', q['sign_ge13'], '\nsign 11-12', q['sign_11_12'])
    L = S['q2_lottery']
    print('Q2:', {k: (v['depth3_rate'], v['high']) for k, v in L['seeds'].items()})
    print(f"   new high {L['new_high']}/{L['new_n']} falsifier_fired={L['falsifier_fired']} "
          f"P(>=obs|ctrl)={L['p_new_ge_observed_high_under_control']}; all {L['all_high']}/{L['all_n']} {L['all_wilson']}")
    for k, v in S['ladders']['aggregate'].items():
        print('ladder', k, v)


if __name__ == '__main__':
    main()
