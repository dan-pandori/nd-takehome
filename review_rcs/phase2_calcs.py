#!/usr/bin/env python3
"""Reviewer phase-2 calculations (generator for out/verdict_medians.txt, out/our_runs_ranges.txt, out/our_runs_cap6.txt,
out/phase2_numbers.txt). Run from review_rcs/: python3 phase2_calcs.py"""
import json, math, statistics as st, csv, collections, io, contextlib, sys
sys.argv = ['x']

def verdict_medians():
    R = {r['name']: r for r in json.load(open('out/lit_rows.json'))}
    from flops import ROWS as Y
    yue_hi_pre = [d['prereg'][1] for d in Y]; yue_hi_fig = [d['best'][1] for d in Y]
    own = [d for d in Y if d['name'].startswith('Yue ')]           # Yue's own VeRL runs (EasyR1 excluded: separate row)
    own_hi_pre = [d['prereg'][1] for d in own]; own_hi_fig = [d['best'][1] for d in own]
    hi = lambda n: R[n]['hi']
    base_e = {'1-shot RLVR': hi('1-shot RLVR (Qwen2.5-Math-1.5B)'), 'Spurious rewards': hi('Spurious rewards (Qwen2.5-Math-7B)'),
              'Dr. GRPO / Oat-Zero': hi('Yue: Oat-Zero-7B (steps assumed 200-500)')}
    third = {'Invisible Leash (re-tests ProRL-v2)': hi('ProRL-v2 (cumulative 3,000 steps)'), 'RL Squeezes (re-tests ProRL-v1)': hi('ProRL-v1 (1.5B)')}
    create = {'ProRL-v1': hi('ProRL-v1 (1.5B)'), 'f(g(x))': hi('f(g(x)) composition (Llama-3.1-8B-Instruct)'),
              'Olmo-3 RL-Zero': hi('Olmo-3-7B RL-Zero'), 'SimpleRL-Zoo (32B, own paper: "genuine enhancement")': hi('Yue: SimpleRL-Zoo Qwen2.5-32B')}
    out = []
    def show(label, e, c):
        me, mc = st.median(e.values()), st.median(c.values())
        out.append(f'{label}: elicit n={len(e)} median {me:.2e}; create n={len(c)} median {mc:.2e}; create/elicit = {mc/me:.1f}x')
    for rule, yhi, ohi in (('prereg-rule lengths', yue_hi_pre, own_hi_pre), ('figure-read lengths (after E-2)', yue_hi_fig, own_hi_fig)):
        out.append(f'== {rule}')
        # A: third-party re-tests count for the testing paper; Yue = median of its 19 evaluated checkpoints
        e = dict(base_e, **third, Yue=st.median(yhi)); show('A paper-level, re-tests attributed to the testing paper, Yue median', e, create)
        e2 = dict(e, Yue=max(yhi)); show('A2 same, Yue max', e2, create)
        c3 = dict(create, **{'LN-Ultra (GPU-h bound)': R['LN-Ultra reasoning RL']['gpuh_bound']}); e3 = dict(e, **{'Qwen3-8B (GPU-h bound)': R['Qwen3-8B RL stage']['gpuh_bound']})
        show('A3 same + GPU-h-bound rows', e3, c3)
        # B: each paper's verdict covers only its own runs (no third-party re-tests; Yue = its own runs)
        eb = dict(base_e, Yue=st.median(ohi)); show('B paper-level, own runs only (Yue = its own VeRL runs)', eb, create)
        show('B3 own runs only + GPU-h-bound rows', dict(eb, **{'Qwen3-8B (GPU-h bound)': R['Qwen3-8B RL stage']['gpuh_bound']}),
             dict(create, **{'LN-Ultra (GPU-h bound)': R['LN-Ultra reasoning RL']['gpuh_bound']}))
    # executor's per-model figure from compute_table.csv, before and after reclassifying Qwen2.5-Math-7B-Instruct
    rows = list(csv.DictReader(open('../rl_compute_share/compute_table.csv')))
    def mid(r):
        try: return math.sqrt(float(r['ratio_low']) * float(r['ratio_high']))
        except: return None
    llm = [r for r in rows if r['group'] in ('yue', 'lit') and mid(r) and not r['model'].startswith('100M')]
    for label, fix in (('as committed', {}), ('Qwen2.5-Math-7B-Instruct back to elicit (pre-claimcheck)', {'Qwen2.5-Math-7B-Instruct (SFT + GRPO with RM)': 'elicit'})):
        g = collections.defaultdict(list)
        for r in llm: g[fix.get(r['model'], r['verdict'])].append(mid(r))
        n_yue_el = sum(1 for r in llm if r['group'] == 'yue' and fix.get(r['model'], r['verdict']) == 'elicit')
        out.append(f"executor per-model ({label}): elicit n={len(g['elicit'])} (of which Yue rows {n_yue_el}) median {st.median(g['elicit']):.3e}; "
                   f"create n={len(g['create'])} median {st.median(g['create']):.3e}; ratio {st.median(g['create'])/st.median(g['elicit']):.1f}x")
    open('out/verdict_medians.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

def our_runs():
    import ourruns as O
    regs = {r: O.load_reg(r) for r in ('trajectory-cap6', 'rl-continue-cap6')}
    s1 = O.stage1_rows(regs['trajectory-cap6'])
    tj6 = '/home/dan/work/trajectory-cap6/artifacts/tj6'; rc6 = '/home/dan/work/rl-continue-cap6/artifacts/rc6'
    lines = []; pre = []
    for sd in (0, 1, 2):
        lad = f'la_T1_best6_s{sd}'; key = f'ckpts/tj6/stage1_best6_s{sd}_b1200.pt'; D = s1[key]['train_tokens']; g1 = s1[key]['gpu_seconds']
        for label, parts in (('trajectory-cap6 r1-8', [('trajectory-cap6', [tj6], set(range(1, 9)))]),
                             ('rl-continue-cap6 r1-16', [('trajectory-cap6', [tj6], set(range(1, 9))), ('rl-continue-cap6', [rc6], set(range(9, 17)))])):
            s = collections.Counter(); frs = []
            for (reg, dirs, rr) in parts:
                per = {k: v for k, v in O.ladder_rows(regs[reg], lad).items() if k[1] in rr}
                pt, mix = O.round_files(dirs, lad)
                pt = {k: v for k, v in pt.items() if k in rr}; mix = {k: v for k, v in mix.items() if k in rr}
                x = O.summarise(per, pt, mix, 20000, 4)
                for k in ('gen_sample', 'prefill_sample', 'gen_eval', 'prefill_eval_est', 'prefill_total', 'ft_tokens', 'gpu_sample', 'gpu_eval', 'gpu_ft'): s[k] += x[k]
                frs.append((x['f_rl'], x['n_rounds']))
            s = dict(s); s['f_rl'] = sum(a * b for a, b in frs) / sum(b for a, b in frs)
            r = O.ratios(s, D); pre.append(s['prefill_total'] / (s['gen_sample'] + s['gen_eval']))
            lines.append(f"{label:24s} s{sd} D {D:.2e} f_rl {s['f_rl']:.2f} all {r['all']:.2f} train {r['train']:.2f} rl_only {r['rl_only']:.2f} "
                         f"dec {r['decoded_only']:.2f} gpu_tr {(s['gpu_sample']+s['gpu_ft'])/g1:.1f} gpu_all {(s['gpu_sample']+s['gpu_ft']+s['gpu_eval'])/g1:.1f} "
                         f"prefill/decoded {pre[-1]:.2f}")
    open('out/our_runs_cap6.txt', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
    R = json.load(open('out/our_runs.json'))
    allpre = [r['prefill_sample'] / r['gen_sample'] for r in R] + pre    # prefill_sample/gen_sample = total prefill / (gen_s + gen_e)
    rr = []
    def rng(xs): return f"{min(xs):.1f}–{max(xs):.1f}"
    for run in ['create-or-elicit', 'trajectory', 'rl-continue', 'rl-from-ckpt']:
        xs = [r for r in R if r['run'].startswith(run)]
        x16 = [r for r in xs if r['ladder'] != 'la_ko_s1'] if run == 'create-or-elicit' else xs
        rr.append(f"{run} n={len(x16)} all {rng([r['r_all'] for r in x16])} train {rng([r['r_train'] for r in x16])} rl_only {rng([r['r_rl_only'] for r in x16])} "
                  f"dec {rng([r['r_decoded_only'] for r in x16])} gpu_tr {rng([r['gpu_ratio_train'] for r in x16])} gpu_all {rng([r['gpu_ratio_all'] for r in x16])}")
        if run == 'rl-from-ckpt':
            for p in (1600, 5000, 12000, 16000):
                ys = [r for r in xs if r['ladder'].endswith(f'_p{p}')]
                rr.append(f"   p{p} all {rng([r['r_all'] for r in ys])} train {rng([r['r_train'] for r in ys])} rl_only {rng([r['r_rl_only'] for r in ys])} dec {rng([r['r_decoded_only'] for r in ys])} gpu_tr {rng([r['gpu_ratio_train'] for r in ys])}")
    rr.append(f'prefill / (sample + eval decoded) over all {len(allpre)} ladders incl. cap6: {min(allpre):.2f}–{max(allpre):.2f}')
    open('out/our_runs_ranges.txt', 'w').write('\n'.join(rr) + '\n'); print('\n'.join(rr))

def numbers():
    out = []
    # JustRL: lit.py convention (mean 4.0-5.5K) and a piecewise variant (~8K->5K over the first 1,000 steps, then 4-5K)
    D = 19e12
    lo = 2048 * (1000 * 5000 + 3380 * 4000) + 4380 * 2048 * 100; hi = 2048 * (1000 * 8000 + 3380 * 5000) + 4380 * 2048 * 1000
    R = {r['name']: r for r in json.load(open('out/lit_rows.json'))}
    j = R['JustRL-DeepSeek-1.5B']
    out.append(f"JustRL: lit.py {j['lo']:.2e}-{j['hi']:.2e}; piecewise {8/6*lo/D:.2e}-{10/6*hi/D:.2e}; executor row 9.82e-3-1.23e-2 from Table 4 budget 4,380*2,048*16,000 = {4380*2048*16000:.3e}")
    # B-anchored gaps: in lab units (GPU-h 0.053, cost 0.1) and in FLOPs (R1-Zero, my config range)
    r1 = R['DeepSeek-R1-Zero']; r1b = R['DeepSeek-R1-Zero (mean length 5K-15K)']
    flo, fhi = min(r1['lo'], r1b['lo']), max(r1['hi'], r1b['hi'])
    out.append(f"R1-Zero FLOP ratio (B-grade inputs): {flo:.2e}-{fhi:.2e}")
    for v, lab in ((0.053, 'GPU-h share'), (0.1, 'V3.2 cost share')):
        out.append(f"  vs {lab} {v}: Yue median mid 1.15e-4 is {math.log10(v/1.15e-4):.2f} orders below; largest tested 2.1e-2 is {math.log10(v/2.1e-2):.2f}")
    out.append(f"  in FLOPs: Yue median 1.15e-4 is {math.log10(flo/1.15e-4):.2f}-{math.log10(fhi/1.15e-4):.2f} orders below R1-Zero; largest tested 2.1e-2 is {math.log10(flo/2.1e-2):.2f} to +{math.log10(fhi/2.1e-2):.2f}")
    # ScaleRL-8B at MFU 3-30 %, GB200 2.5e15
    for Dx in (15e12, 36e12):
        out.append(f"ScaleRL-8B D={Dx:.0e}: {1e5*3600*2.5e15*0.03/(6*8e9*Dx):.3f}-{1e5*3600*2.5e15*0.30/(6*8e9*Dx):.3f}")
    # FLOP / trained-token coefficient range across my rows: (2g+6E+2ref+2old+8critic)/6
    from flops import ROWS as Y
    co = []
    for d in Y:
        kw = d['kw']; g = kw.get('g', (1, 1)); old = kw.get('old', (0, 1))
        co += [(2*g[0] + 6 + 2*kw.get('ref', 0) + 2*old[0] + 8*kw.get('critic', 0)) / 6, (2*g[1] + 6 + 2*kw.get('ref', 0) + 2*old[1] + 8*kw.get('critic', 0)) / 6]
    out.append(f"FLOP / trained-token coefficient over Yue rows: {min(co):.2f}-{max(co):.2f} (ORZ critic: {(2+6+2+8)/6:.2f})")
    from flops import ROWS
    mids = [math.sqrt(d['best'][0] * d['best'][1]) for d in ROWS]
    out.append(f"Yue figure-read: median mid {st.median(mids):.2e}; median high {st.median([d['best'][1] for d in ROWS]):.2e}; lowest low {min(d['best'][0] for d in ROWS):.2e}")
    open('out/phase2_numbers.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

if __name__ == '__main__':
    verdict_medians(); our_runs(); numbers()
