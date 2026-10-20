#!/usr/bin/env python3
"""Markdown tables for review_kalmar-complexity.md §Recount, generated from out/*.json (no hand-copied numbers)."""
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, 'out', f)))


def f(x, nd=0):
    if x is None:
        return '—'
    if isinstance(x, float) and nd:
        return f'{x:,.{nd}f}'
    return f'{x:,.0f}' if isinstance(x, (int, float)) else str(x)


def sci(x, nd=3):
    return f'{x:.{nd}g}'


def py_table():
    p = J('python_sizes.json')
    rows = ['| program (hand-golfed Python) | raw bytes | raw DEFLATE | gzip -9 | raw xz (9e) | Qwen3 tokens | GPT-2 tokens |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in p.items():
        rows.append(f"| {k} | {v['raw']:,} | {v['deflate']:,} | {v['gzip9']:,} | {v['xz_raw']:,} | {v['qwen3']:,} | {v['gpt2']:,} |")
    return '\n'.join(rows)


def blc_table():
    b = J('blc_recheck.json'); c = J('calib_blc.json')
    rows = ['| program | BLC bits | binary CL bits (own bracket abstraction) | CL / BLC | fresh-sample check |', '|---|---:|---:|---:|---|']
    names = {'parse': 'parse (prompt word → sequent)', 'ksl': 'K-sl algorithm', 'ksl_render': 'K-sl rendering (ND)',
             'ktt': 'K-tt algorithm', 'ktt_render': 'K-tt rendering (Lean)'}
    chk = {'parse': f"{b['ok']['parse']}/{b['n']}", 'ksl': f"{b['ok']['ksl_alg']}/{b['n']} (alone); {b['ok']['ksl_e2e']}/{b['n']} end to end",
           'ksl_render': f"{b['ok']['ksl_e2e']}/{b['n']} end to end", 'ktt': f"{b['ok']['ktt_e2e']}/{b['n']} end to end",
           'ktt_render': f"{b['ok']['ktt_e2e']}/{b['n']} end to end"}
    for k in ['parse', 'ksl', 'ksl_render', 'ktt', 'ktt_render']:
        rows.append(f"| {names[k]} | {b['bits'][k]:,} | {b['cl_bits'][k]:,} | {b['cl_bits'][k] / b['bits'][k]:.1f} | {chk[k]} |")
    s = lambda ks: sum(b['bits'][k] for k in ks); sc = lambda ks: sum(b['cl_bits'][k] for k in ks)
    rows.append(f"| K-sl algorithm + rendering (+ parse) | {s(['ksl', 'ksl_render']):,} ({s(['parse', 'ksl', 'ksl_render']):,}) | "
                f"{sc(['ksl', 'ksl_render']):,} ({sc(['parse', 'ksl', 'ksl_render']):,}) | | |")
    rows.append(f"| K-tt algorithm + rendering (+ parse) | {s(['ktt', 'ktt_render']):,} ({s(['parse', 'ktt', 'ktt_render']):,}) | "
                f"{sc(['ktt', 'ktt_render']):,} ({sc(['parse', 'ktt', 'ktt_render']):,}) | | |")
    for k, v in c.items():
        rows.append(f"| calibration {k} | {v['bits']:,} | {v['cl_bits']:,} | {v['cl_bits'] / v['bits']:.1f} | {v['ok']}/{v['n']} own random cases |")
    return '\n'.join(rows)


def b1_table():
    b = J('b1_recount.json')
    rows = ['| model | N loss tokens / epoch (own count) | pairs | curve points in epoch 1 | L_preq bits (interval mean) | bits/token | '
            'L_preq, next-point variant | EDL (a) final train | EDL (b) final held-out | EDL (c) end-of-epoch-1 train |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in b.items():
        e = v['EDL_bits']
        rows.append(f"| {k} | {v['N_loss_tokens']:,} | {v['pairs']:,} | {v['curve_points_epoch1']} | {sci(v['L_preq_bits'])} | "
                    f"{v['bits_per_token']:.4f} | {sci(v['L_preq_right_bits'])} | {sci(e['a'])} | {sci(e['b'])} | {sci(e['c'])} |")
    return '\n'.join(rows)


def b2_table():
    d = J('b2_recount.json')
    rows = ['| job | task | size | seed | protocol | L_preq bits | N loss tokens | L∞ bits/token | EDL bits | block-0 share of L / of EDL | '
            'at 8,192 thm: L / EDL | blocks at the step cap | training GPU-h (sum of block `secs`) |',
            '|---|---|---|---:|---|---:|---:|---:|---:|---|---|---:|---:|']
    for k, v in d.items():
        p = v['prefix_8192']
        rows.append(f"| {k} | {v['task']} | {v['size']} | {v['seed']} | {'v2 (patience 3,000 steps, ≥ 5,000)' if v['v2'] else 'v1 (4 evals)'} | "
                    f"{sci(v['L_preq'], 4)} | {v['N']:,} | {v['L_inf_bits_per_tok']:.4f} | {sci(v['EDL'], 4)} | "
                    f"{v['block0_share_of_L']:.2f} / {v['block0_share_of_EDL']:.2f} | "
                    f"{(sci(p['L'], 4) + ' / ' + sci(p['EDL'], 4)) if p else '—'} | {v['cap_hits']}/{len(v['blocks']) - 1} | {v['gpu_secs'] / 3600:.2f} |")
    return '\n'.join(rows)


def b3_table():
    d = J('b3_recount.json'); x = J('b3_other_excl_pr.json')
    s = d['summary']
    rows = ['| quantity | STD s0 / s1 / s2 | FOC s0 / s1 / s2 | 3-seed means STD → FOC | relative change (of means; per seed) |',
            '|---|---|---|---|---|']
    for k, lab in (('opener_err', f"opener-state error ({d['n_opener']:,} states)"), ('other_err', f"other-state error ({d['n_states'] - d['n_opener']:,})"),
                   ('all_err', 'all states')):
        v = s[k]
        rows.append(f"| {lab} | {' / '.join(f'{a:.4f}' for a in v['STD'])} | {' / '.join(f'{a:.4f}' for a in v['FOC'])} | "
                    f"{v['STD_mean']:.4f} → {v['FOC_mean']:.4f} | {v['rel_change_of_means']:+.3f}; {', '.join(f'{a:+.3f}' for a in v['rel_change_per_seed'])} |")
    so, fo = x['other_excl_pr']['STD'], x['other_excl_pr']['FOC']
    ms, mf = sum(so) / 3, sum(fo) / 3
    rows.append(f"| other states without `pr` | {' / '.join(f'{a:.4f}' for a in so)} | {' / '.join(f'{a:.4f}' for a in fo)} | {ms:.4f} → {mf:.4f} | "
                f"{mf / ms - 1:+.3f}; {', '.join(f'{b / a - 1:+.3f}' for a, b in zip(so, fo))} |")
    rows.append(f"| `pr` states (1,409) | {' / '.join(f'{a:.3f}' for a in x['pr_err']['STD'])} | {' / '.join(f'{a:.3f}' for a in x['pr_err']['FOC'])} | | |")
    rows2 = ['| step type | states | opener states | STD error (mean) | FOC error (mean) | relative change | mean `explored` |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for t in d['types']:
        v = d['per_type'][t]
        rows2.append(f"| {t} | {v['states']:,} | {v['openers']:,} | {v['STD_mean']:.4f} | {v['FOC_mean']:.4f} | "
                     f"{v['rel_change']:+.2f} | {d['explored_per_type'][t]:.2f} |")
    sp = d['spearman_explored']
    line = 'Spearman across the 15 types of error vs mean `explored`: ' + '; '.join(
        f"{k} {v[0]:+.2f} (p {v[1]:.3f})" for k, v in sp.items())
    tr = ', '.join(f"{k} {v['train_steps']:,}/{v['max_steps']:,} (best {v['best_step']:,})" for k, v in d['runs'].items())
    return '\n'.join(rows) + '\n\n' + '\n'.join(rows2) + '\n\n' + line + '\n\nTraining steps / cap (best validation step): ' + tr


def q4_table():
    d = J('q4_recount.json')
    sp = d['spearman']; part = d['partial_given_log_freq']
    rows = ['| predictor (per step type, n = 15) | source | ρ vs KAL-D mean error (perm. p) | s0 / s1 / s2 | vs KAL-D+A mean | partial ρ given log frequency (p) |',
            '|---|---|---|---|---|---|']
    src = lambda k: 'executor (`rasp_per_type.json`)' if k.startswith('exec_rasp') else 'executor (`states_tf1200`, policy ops)' if k == 'exec_log2_ops' else 'own'
    for k in sorted(sp, key=lambda k: -abs(sp[k]['kalD_mean'][0])):
        v = sp[k]
        rows.append(f"| {k} | {src(k)} | {v['kalD_mean'][0]:+.2f} ({v['kalD_mean'][1]:.3f}) | "
                    f"{v['kalD_s0'][0]:+.2f} / {v['kalD_s1'][0]:+.2f} / {v['kalD_s2'][0]:+.2f} | {v['kalDA_mean'][0]:+.2f} | "
                    + (f"{part[k][0]:+.2f} ({part[k][1]:.3f})" if k in part else '—') + ' |')
    st = d['state_level']
    line = 'State level (logistic regression, type dummies ± 6 standardised demand measures, LR test, df 6): ' + '; '.join(
        f"{m} LR {v['LR']:,.0f} (p {v['p']:.1g}); best single: " + ', '.join(f"{k} {x:,.0f}" for k, x in sorted(v['single_LR'].items(), key=lambda kv: -kv[1])[:3])
        for m, v in st.items())
    pe = d['per_type_error']
    rows3 = ['| step type | states | KAL-D s0 / s1 / s2 error | mean | KAL-D+A mean | KAL-C s0 |', '|---|---:|---|---:|---:|---:|']
    for t in d['types']:
        rows3.append(f"| {t} | {d['type_states'][t]:,} | {pe['kalD_s0'][t]:.4f} / {pe['kalD_s1'][t]:.4f} / {pe['kalD_s2'][t]:.4f} | "
                     f"{pe['kalD_mean'][t]:.4f} | {pe['kalDA_mean'][t]:.4f} | {pe['kalC_s0'][t]:.4f} |")
    return '\n'.join(rows3) + '\n\n' + '\n'.join(rows) + '\n\n' + line + '\n\nPer-state measures equal to the executor\'s on all 137,984 states: ' + \
        ', '.join(f"{k} {v:,}" for k, v in d['state_measures_agree_with_executor'].items())


if __name__ == '__main__':
    import sys
    for name in sys.argv[1:] or ['py', 'blc', 'b1', 'b2', 'b3', 'q4']:
        print(f'\n<!-- {name} -->\n')
        print({'py': py_table, 'blc': blc_table, 'b1': b1_table, 'b2': b2_table, 'b3': b3_table, 'q4': q4_table}[name]())
