#!/usr/bin/env python3
"""fast-stage1: the equivalence table and the speed table, from pulled files only (no torch).

  python3 fs_analysis.py            -> artifacts/fs/summary.json, and the markdown tables on stdout

Old arm = stage1-dynamics arm C (artifacts/fs/old/{ev_c_s*.json,m_c_s*.jsonl}, copied from
origin/dan_stage1-dynamics:artifacts/sd/), seeds 0-7.  New arm = --impl fast, seeds 0-7
(artifacts/fs/ev/fast*_s{0..7}.json, artifacts/fs/m_fast*_s{0..7}.jsonl).  Arm R (r6*) is a second
old-recipe reference.  Criterion (preregistration/fast-stage1.md): |mean_new - mean_C| < 1.506 * sd, with sd =
NOISE_FLOOR.md's pooled sd (greedy) or arm C's own sd (validation loss).
"""
import glob, json, math, os, random, re, statistics as st

A = 'artifacts/fs'
K8 = 1.506                                   # (t.975 + t.80)(df 14) * sqrt(2/8), NOISE_FLOOR's formula at n = 8
NF_SD = {'all': 0.03038, 'len2': 0.003128, 'len3': 0.00486, 'len4': 0.01512, 'len5': 0.01502, 'len6': 0.1523,
         'nodepth3_len6': 0.03667}           # NOISE_FLOOR.md table; nodepth3_len6 uses its '6-line no-pattern (247)' row (pre-registered proxy)
SLICES = ['all', 'len2', 'len3', 'len4', 'len5', 'len6', 'nodepth3_len6']
A40_PEAK = 149.7e12
LEGACY_WASTE = []
SEEDS = range(8)


def seed_of(f):
    return int(re.search(r'_s(\d+)\.json', f).group(1))


def greedy(pattern, by_name=False):
    out = {}
    for f in sorted(glob.glob(pattern)):
        out[os.path.basename(f) if by_name else seed_of(f)] = {k: v['rate'] for k, v in json.load(open(f))['slices'].items()}
    return out


def final_val(pattern):
    out = {}
    for f in sorted(glob.glob(pattern)):
        L = [json.loads(l) for l in open(f)]
        steps = [r for r in L if r.get('kind') == 'step']
        done = [r for r in L if r.get('kind') == 'done']
        out[seed_of(f)] = {'val': steps[-1]['val'], 'step': steps[-1]['step'], 'done': done[-1] if done else None}
    return out


def iqm(v):
    v = sorted(v); n = len(v); lo, hi = n * 0.25, n * 0.75
    w = [max(0.0, min(i + 1, hi) - max(i, lo)) for i in range(n)]
    return sum(x * wi for x, wi in zip(v, w)) / sum(w)


def boot_iqm_diff(a, b, B=10000, seed=0):
    r = random.Random(seed); ds, ia, ib = [], [], []
    for _ in range(B):
        xa = [r.choice(a) for _ in a]; xb = [r.choice(b) for _ in b]
        ia.append(iqm(xa)); ib.append(iqm(xb)); ds.append(iqm(xa) - iqm(xb))
    q = lambda s: (sorted(s)[int(0.025 * B)], sorted(s)[int(0.975 * B) - 1])
    return q(ia), q(ib), q(ds)


def compare(new, old, sd_of, label):
    rows = []
    for s in SLICES:
        a = [new[k][s] for k in sorted(new)]; b = [old[k][s] for k in sorted(old)]
        sd = sd_of(s, b)
        mdd = K8 * sd
        d = st.mean(a) - st.mean(b)
        ci_a, ci_b, ci_d = boot_iqm_diff(a, b)
        rows.append({'quantity': label, 'slice': s, 'n_new': len(a), 'n_old': len(b), 'mean_new': st.mean(a), 'mean_old': st.mean(b),
                     'diff': d, 'sd_used': sd, 'mdd': mdd, 'pass': abs(d) < mdd, 'per_seed_new': a, 'per_seed_old': b,
                     'iqm_new': iqm(a), 'iqm_new_ci': ci_a, 'iqm_old': iqm(b), 'iqm_old_ci': ci_b,
                     'iqm_diff': iqm(a) - iqm(b), 'iqm_diff_ci': ci_d})
    return rows


def main():
    res = {}
    gC = greedy(f'{A}/old/ev_c_s*.json'); gR = greedy(f'{A}/old/ev_r6*_s*.json', by_name=True)   # 8 replicates of seeds 0/1: keyed by file
    gN = {k: v for k, v in greedy(f'{A}/ev/fast*_s*.json').items() if k in SEEDS}
    vC = final_val(f'{A}/old/m_c_s*.jsonl'); vN = {k: v for k, v in final_val(f'{A}/m_fast*_s*.jsonl').items() if k in SEEDS}
    res['labels'] = {'model': '3,214,336-param from-scratch GPT, lean_seq, cap 6, trained on data/p2/train_depth3_f0_a1.jsonl (155,000 records, 0 depth-3), '
                              'cosine 6,000 steps bs 128 lr 1e-3', 'old': 'stage1-dynamics arm C (train.py legacy), seeds 0-7',
                     'new': 'fast-stage1 --impl fast, seeds 0-7', 'judge': 'Lean alone (sd_eval.py, batch 512, max_new 400)'}
    rows = []
    if len(gN) == 8 and len(gC) == 8:
        rows += compare(gN, gC, lambda s, b: NF_SD[s], 'held-out greedy')
    if len(vN) == 8 and len(vC) == 8:
        assert all(v['step'] == 6000 for v in list(vN.values()) + list(vC.values()))
        rows += compare({k: v['val'] for k, v in vN.items()}, {k: v['val'] for k, v in vC.items()}, lambda s, b: st.stdev(b), 'val loss')
    res['equivalence'] = rows
    res['PASS'] = bool(rows) and all(r['pass'] for r in rows) and len(rows) == 14
    hm = lambda g: sum(v['depth3'] > 0.44 for v in g.values())
    res['depth3_high_mode'] = {'new': [hm(gN), len(gN)], 'C': [hm(gC), len(gC)], 'R': [hm(gR), len(gR)],
                               'per_seed_new': [gN[k]['depth3'] for k in sorted(gN)], 'per_seed_C': [gC[k]['depth3'] for k in sorted(gC)]}
    res['R_reference'] = {s: {'mean': st.mean(v[s] for v in gR.values()), 'n': len(gR)} for s in SLICES} if gR else None
    res['C_vs_R_diff'] = {s: st.mean(v[s] for v in gR.values()) - st.mean(v[s] for v in gC.values()) for s in SLICES} if gR else None

    # ---- speed
    waves = [json.loads(l) for fn in sorted(glob.glob(f'{A}/waves*.jsonl')) for l in open(fn)]
    waves = [w for w in waves if not w['wave'].endswith('_warm')]
    sp = []
    tps_fast = []                              # useful tokens per step, from the fast waves' plans (same data, same bs: the legacy expectation)
    for w in waves:
        for s in w['seeds'].split():
            a0 = [json.loads(l) for l in open(f"{A}/m_{w['wave']}_s{s}.jsonl")][0]
            if a0.get('useful_tokens'):
                tps_fast.append(a0['useful_tokens'] / w['steps'])
    for w in waves:
        per = []
        for s in w['seeds'].split():
            f = f"{A}/m_{w['wave']}_s{s}.jsonl"
            L = [json.loads(l) for l in open(f)]
            args = [r for r in L if r['kind'] == 'args'][0]; done = [r for r in L if r['kind'] == 'done'][-1]
            per.append({'seed': int(s), 'secs': done['secs'], 'val_s': done['val_full_s'],
                        'first_step_s': done.get('first_step_s'), 'useful': args.get('useful_tokens'),
                        'computed': args.get('computed_tokens'), 'legacy_computed': args.get('legacy_computed_tokens')})
        useful = [p['useful'] for p in per if p['useful']]
        tok_per_step = (sum(useful) / len(useful) / w['steps']) if useful else (st.mean(tps_fast) if tps_fast else None)
        n_params = 3214336
        agg_tok_s = tok_per_step * w['steps'] * w['n'] / w['wall_s'] if tok_per_step else None
        sp.append({**w, 'per_model_secs': [round(p['secs'], 1) for p in per], 'mean_model_secs': st.mean(p['secs'] for p in per),
                   'val_s': st.mean(p['val_s'] for p in per), 'first_step_s': per[0]['first_step_s'],
                   'ms_per_step_per_model': 1000 * st.mean(p['secs'] - p['val_s'] - (p['first_step_s'] or 0) for p in per) / w['steps'],
                   'agg_steps_per_s': w['steps'] * w['n'] / w['wall_s'], 'useful_tok_per_step': tok_per_step,
                   'agg_useful_tok_s': agg_tok_s, 'agg_frac_peak': (6 * n_params * agg_tok_s / A40_PEAK) if agg_tok_s else None,
                   'pad_waste': (per[0]['computed'] / per[0]['useful']) if per[0]['computed'] else None,
                   'legacy_pad_waste': (per[0]['legacy_computed'] / per[0]['useful']) if per[0]['legacy_computed'] else None})
    LEGACY_WASTE[:] = [st.mean(w['legacy_pad_waste'] for w in sp if w['legacy_pad_waste'])] if any(w['legacy_pad_waste'] for w in sp) else []
    res['legacy_pad_waste'] = LEGACY_WASTE[0] if LEGACY_WASTE else None
    res['speed'] = sp
    json.dump(res, open(f'{A}/summary.json', 'w'), indent=1)

    # ---- print
    if rows:
        print('| quantity | slice | legacy (C) mean | fast mean | Δ | MDD (n=8) | within |')
        print('|---|---|---|---|---|---|---|')
        for r in rows:
            f = (lambda x: f'{100 * x:.2f} pp') if r['quantity'] == 'held-out greedy' else (lambda x: f'{x:.5f}')
            g = (lambda x: f'{x:.4f}') if r['quantity'] == 'held-out greedy' else (lambda x: f'{x:.5f}')
            print(f"| {r['quantity']} | {r['slice']} | {g(r['mean_old'])} | {g(r['mean_new'])} | {f(r['diff'])} | {f(r['mdd'])} | {'yes' if r['pass'] else '**no**'} |")
        print('PASS' if res['PASS'] else 'FAIL', '| depth-3 high mode (>0.44):', res['depth3_high_mode']['new'], 'new vs', res['depth3_high_mode']['C'], 'C')
    if sp:
        print('\n| wave | gpu | impl | N | steps | wall s | s/model | ms/step/model | agg steps/s | agg useful tok/s | agg % bf16 peak (A40) | pad waste |')
        print('|---|---|---|---|---|---|---|---|---|---|---|---|')
        for w in sp:
            f = lambda x, fmt: (fmt % x) if x is not None else '—'
            pw = f"{w['pad_waste']:.3f}" if w['pad_waste'] else f"{LEGACY_WASTE[0]:.3f} (legacy)" if LEGACY_WASTE else '—'
            print(f"| {w['wave']} | {w.get('gpu', 'NVIDIA A40')} | {w['impl']} | {w['n']} | {w['steps']} | {w['wall_s']:.0f} | {w['mean_model_secs']:.0f} | "
                  f"{w['ms_per_step_per_model']:.1f} | {w['agg_steps_per_s']:.1f} | {f(w['agg_useful_tok_s'] and w['agg_useful_tok_s'] / 1e3, '%.0fk')} | "
                  f"{f(w['agg_frac_peak'] and 100 * w['agg_frac_peak'], '%.1f') if 'A40' in w.get('gpu', 'NVIDIA A40') else '—'} | {pw} |")

if __name__ == '__main__':
    main()
