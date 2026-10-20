#!/usr/bin/env python3
"""Markdown tables for numbers.md § kalmar-complexity, generated from the result files (run kalmar-complexity).

  .venv-tok/bin/python kalmar_complexity/numbers_tables.py > artifacts/kc/numbers_tables.md
"""
import json, math, os
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
J = lambda p: json.load(open(A(p)))


def sci(v):
    if v is None:
        return '—'
    if abs(v) < 1e5:
        return f'{v:,.0f}'
    e = int(math.floor(math.log10(abs(v))))
    return f'{v / 10 ** e:.2f} × 10^{e}'


def t_programs():
    py = J('artifacts/kc/python_sizes.json')
    blc = J('kalmar_complexity/programs/blc/results.json')['programs']
    print('| piece | Python raw B | Python DEFLATE B | Python xz B | Qwen3 tokens | GPT-2 tokens | BLC bits | binary CL bits |')
    print('|---|---|---|---|---|---|---|---|')
    rows = [('K-sl algorithm', 'K-sl algorithm', 'K-sl algorithm'),
            ('K-sl rendering, ND text', 'K-sl render ND', 'K-sl rendering'),
            ('K-sl rendering, lean_seq (canonical)', 'K-sl render lean_seq', None),
            ('parse (prompt → sequent)', 'parse (prompt -> sequent)', 'parse'),
            ('K-sl algorithm + ND rendering', 'K-sl algorithm + ND render', 'K-sl algorithm + rendering'),
            ('K-sl parse + algorithm + ND rendering', 'K-sl end to end (parse + algorithm + ND)', 'K-sl parse + algorithm + rendering'),
            ('K-sl parse + algorithm + lean_seq rendering', 'K-sl end to end (parse + algorithm + lean_seq)', None),
            ('K-tt algorithm', 'K-tt algorithm', 'K-tt algorithm'),
            ('K-tt rendering, Lean text', 'K-tt render Lean', 'K-tt rendering'),
            ('K-tt algorithm + rendering', 'K-tt algorithm + Lean render', 'K-tt algorithm + rendering'),
            ('K-tt parse + algorithm + rendering', 'K-tt end to end (parse + algorithm + Lean)', 'K-tt parse + algorithm + rendering'),
            ('K-sl per-step policy (state → action)', 'K-sl per-step policy (state -> lean_seq action)', None),
            ('mechanical: kalmar/kalmar.py', 'mech: kalmar/kalmar.py (builder + render)', None),
            ('mechanical: tt_prover.py', 'mech: tt_prover.py (whole file)', None),
            ('mechanical: policy.py', 'mech: policy.py (per-step policy)', None),
            ('mechanical: gen.py (K12 generator, all knobs)', 'mech: gen.py (K12 generator, all knobs)', None)]
    for lab, pk, bk in rows:
        p = py[pk]
        b = blc.get(bk) if bk else None
        print(f"| {lab} | {p['raw_bytes']:,} | {p['deflate_bytes']:,} | {p['xz_bytes']:,} | {p['qwen3_tokens']:,} | "
              f"{p['gpt2_tokens']:,} | {b['blc_bits']:,} | {b['cl_bits']:,} |" if b else
              f"| {lab} | {p['raw_bytes']:,} | {p['deflate_bytes']:,} | {p['xz_bytes']:,} | {p['qwen3_tokens']:,} | "
              f"{p['gpt2_tokens']:,} | — | — |")


def t_calibration():
    py = J('artifacts/kc/python_sizes.json')
    blc = J('kalmar_complexity/programs/blc/results.json')['programs']
    rasp = J('kalmar_complexity/programs/rasp/results.json')
    rr = {r['task']: r for r in rasp['calibration']['rows']}
    items = [('copy', 'calib copy', None, 'calib copy', 'copy'), ('reverse', 'calib reverse', None, 'calib reverse', 'reverse'),
             ('parity', 'calib parity', 'calib parity_nb', 'calib parity', 'parity_sp'),
             ('sort', 'calib sort', 'calib sort_nb', 'calib sort', 'sort_rep'),
             ('addition (binary)', 'calib add', 'calib add_nb', 'calib add', 'addition'),
             ('eval (formula truth value)', 'calib eval', None, 'calib eval', 'eval'),
             ('taut (truth-table validity)', 'calib taut', None, 'calib taut', 'taut'),
             ('Kalmár tt (algorithm)', 'K-tt algorithm', None, 'K-tt algorithm', None),
             ('Kalmár sl (algorithm)', 'K-sl algorithm', None, 'K-sl algorithm', 'POLICY')]
    print('| algorithm | Python DEFLATE B (builtins / none) | BLC bits | binary CL bits | Kt (BLC bits + log2 median β) | RASP-L ops / attention depth |')
    print('|---|---|---|---|---|---|')
    for lab, p1, p2, bk, rk in items:
        pv = f"{py[p1]['deflate_bytes']}" + (f" / {py[p2]['deflate_bytes']}" if p2 else '')
        b = blc[bk]
        if rk == 'POLICY':
            rv = f"{rasp['decision']['ops']} / {rasp['decision']['attn_depth']} (per-step policy)"
        elif rk:
            r = rr[rk]
            rv = f"{r['ops']} / {r['attn_depth']}" + (f" ({rk})" if rk != lab.split()[0] else '')
        else:
            rv = '—'
        print(f"| {lab} | {pv} | {b['blc_bits']:,} | {b['cl_bits']:,} | {b.get('Kt_bits_median', 0):,.0f} | {rv} |")


def t_b1():
    B = J('artifacts/kc/b1_preq.json')
    print('| model | N loss tokens (epoch) | first-epoch prequential code, bits | bits / token | L∞ final train / final held-out / end of epoch 1 (nats/token) | EDL (residual = final held-out) | EDL (final train) | EDL (end of epoch 1) | bias bound (steps 1–19) |')
    print('|---|---|---|---|---|---|---|---|---|')
    for k, v in B.items():
        L = v['L_inf_nats']
        print(f"| {k} | {v['N_loss_tokens']:,} | {sci(v['L_preq_bits'])} | {v['bits_per_token']:.4f} | "
              f"{L['a_final_train']:.4f} / {L['b_final_val']:.4f} / {L['c_epoch1_end']:.4f} | {sci(v['EDL_bits']['b_final_val'])} | "
              f"{sci(v['EDL_bits']['a_final_train'])} | {sci(v['EDL_bits']['c_epoch1_end'])} | ≤ {sci(v['bias_bound_bits'])} |")


def t_b2():
    S = J('artifacts/kc/b2_summary.json')
    print('| run | task | size | seed | protocol | theorems | prequential bits | EDL bits | L∞ (bits/token) | prequential @ 8,192 | EDL @ 8,192 | train steps | job seconds |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for k, v in sorted(S.items()):
        a = v['args']
        print(f"| {k} | {a['task']} | {a['size']} | {a['seed']} | {'v2' if a.get('patience_steps') else 'v1'} | "
              f"{v['summary']['theorems']:,} | {sci(v['summary']['prequential_bits'])} | {sci(v['summary']['EDL_bits'])} | "
              f"{v['summary']['L_inf_bits_per_token']:.4f} | {sci(v['preq_8192'])} | {sci(v['EDL_8192'])} | "
              f"{v['train_steps']:,} | {v['train_secs']:,.0f} |")


def t_q4():
    R = J('artifacts/kc/q4/q4_results.json')
    sp = R['spearman']
    print('| predictor (per step type) | ρ, KAL-D 3-seed mean (p) | ρ s0 / s1 / s2 | ρ, KAL-D+A mean |')
    print('|---|---|---|---|')
    order = sorted(sp, key=lambda k: -abs(sp[k]['kalD_mean']['rho']))
    for k in order:
        s = sp[k]
        print(f"| {k} | {s['kalD_mean']['rho']:+.2f} ({s['kalD_mean']['p']:.3f}) | {s['kalD_s0']['rho']:+.2f} / "
              f"{s['kalD_s1']['rho']:+.2f} / {s['kalD_s2']['rho']:+.2f} | {s['kalDA_mean']['rho']:+.2f} |")
    print()
    print('| seed | LR χ² (df 9), demand added to step type | p | best single measure (LR, df 1) |')
    print('|---|---|---|---|')
    for m, v in R['state_level'].items():
        best = max(v['single_lr'].items(), key=lambda kv: kv[1]['lr'])
        print(f"| {m} | {v['lr']:,.0f} | {v['p']:.1g} | {best[0]} ({best[1]['lr']:,.0f}) |")


def t_types():
    R = J('artifacts/kc/q4/q4_results.json')
    P, O = R['predictors'], R['outcomes']
    cols = ['rasp_eff_depth', 'rasp_cone_depth', 'explored', 'log2_ops', 'target_h', 'focus_h', 'decl_len',
            'py_bytes', 'log_freq', 'snap_final_nats_per_tok'] + [c for c in ('b2_bits_S', 'b2_bits_M', 'b2_bits_L')
                                                                  if any(c in P[t] for t in P)]
    print('| step type | error KAL-D s0 / s1 / s2 | error KAL-D+A mean | ' + ' | '.join(cols) + ' |')
    print('|---|---|---|' + '---|' * len(cols))
    for t in sorted(R['types'], key=lambda t: -O['kalD_mean'][t]):
        cells = [f"{P[t][c]:.3g}" if P[t].get(c) is not None else '—' for c in cols]
        print(f"| {t} | {100 * O['kalD_s0'][t]:.1f} / {100 * O['kalD_s1'][t]:.1f} / {100 * O['kalD_s2'][t]:.1f} % | "
              f"{100 * O['kalDA_mean'][t]:.1f} % | " + ' | '.join(cells) + ' |')


if __name__ == '__main__':
    for f in (t_programs, t_calibration, t_b1, t_b2, t_q4, t_types):
        print(f'\n<!-- {f.__name__} -->')
        f()
