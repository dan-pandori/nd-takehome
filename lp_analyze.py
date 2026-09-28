#!/usr/bin/env python3
"""long-pool: tables and figure for the re-read (artifacts/lp/rr/<model>.jsonl on transfer_long_rr600, <model>__ge17.jsonl
on the L_true >= 17 file).  stdout = markdown tables; writes artifacts/lp/rr_summary.json and figures/lp_rate_by_bin.png.
  python3 lp_analyze.py
L* = max L in 11..16 with >= 5 solved at L_true >= L on the 600-theorem subset; '>= 17' if >= 5 of the 70 lower-bound
theorems are solved too; '< 11' if fewer than 5 are solved at >= 11.  Steps check: for each solved theorem, the fewest
derivation steps (non-PR lines) of any accepted proof against L_true - n_prem (the label's derivation steps).
"""
import json, os, collections, math

RR = 'artifacts/lp/rr'
MODELS = [   # file stem, label, checkpoint (bucket path), params, format, rung, Stage-1 training set
    ('state-env__la_T1_S_s0_r8', 'S T1 s0', 'state-env/ckpts/se/ladder/la_T1_S_s0_r8.pt', '3,216,384', 'lean_state', 'T1 r8'),
    ('state-env__la_T1_S_s1_r8', 'S T1 s1', 'state-env/ckpts/se/ladder/la_T1_S_s1_r8.pt', '3,216,384', 'lean_state', 'T1 r8'),
    ('state-env__la_T1_SN_s0_r8', 'SN-v2 T1 s0', 'state-env/ckpts/se/ladder/la_T1_SN_s0_r8.pt', '3,216,384', 'lean_staten', 'T1 r8'),
    ('state-env__la_T1_SN_s1_r8', 'SN-v2 T1 s1', 'state-env/ckpts/se/ladder/la_T1_SN_s1_r8.pt', '3,216,384', 'lean_staten', 'T1 r8'),
    ('ds-generator__la_T1_c0_s0_r8', 'C0 T1 s0', 'ds-generator/ckpts/ladder/la_T1_c0_s0_r8.pt', '3,214,336', 'lean_seq', 'T1 r8'),
    ('ds-generator__la_T1_c0_s1_r8', 'C0 T1 s1', 'ds-generator/ckpts/ladder/la_T1_c0_s1_r8.pt', '3,214,336', 'lean_seq', 'T1 r8'),
    ('state-env__stage1_S_s0', 'S frozen s0', 'state-env/ckpts/se/stage1_S_s0.pt', '3,216,384', 'lean_state', 'Stage-1'),
    ('state-env__stage1_S_s1', 'S frozen s1', 'state-env/ckpts/se/stage1_S_s1.pt', '3,216,384', 'lean_state', 'Stage-1'),
    ('state-env__stage1_SN_s0', 'SN frozen s0', 'state-env/ckpts/se/stage1_SN_s0.pt', '3,216,384', 'lean_staten', 'Stage-1'),
    ('state-env__stage1_SN_s1', 'SN frozen s1', 'state-env/ckpts/se/stage1_SN_s1.pt', '3,216,384', 'lean_staten', 'Stage-1'),
    ('lean-format__stage1_a1_seq_s0', 'C0 frozen s0', 'lean-format/ckpts/lf/stage1_a1_seq_s0.pt', '3,214,336', 'lean_seq', 'Stage-1'),
    ('lean-format__stage1_a1_seq_s1', 'C0 frozen s1', 'lean-format/ckpts/lf/stage1_a1_seq_s1.pt', '3,214,336', 'lean_seq', 'Stage-1'),
    ('cap-horizon__stage1_k12_s0', 'K12 frozen s0', 'cap-horizon/ckpts/kh/stage1_k12_s0.pt', '3,214,336', 'lean_seq', 'Stage-1 (cap 12)'),
    ('cap-horizon__stage1_k14_s0', 'K14 frozen s0', 'cap-horizon/ckpts/kh/stage1_k14_s0.pt', '3,214,336', 'lean_seq', 'Stage-1 (cap 14)'),
]
BINS = list(range(11, 17))


def steps(p):
    ls = [x.strip() for x in p.split(';') if x.strip() and x.strip() != 'QED']
    return sum(1 for l in ls if not l.endswith(': PR'))


def main():
    pool = {json.loads(l)['name']: json.loads(l) for l in open('data/ladder/transfer_long_rr600.jsonl')}
    out, have = {}, []
    for stem, lab, ck, par, fmt, rung in MODELS:
        fn = f'{RR}/{stem}.jsonl'
        if not os.path.exists(fn):
            continue
        rows = [json.loads(l) for l in open(fn)]
        summ = json.load(open(f'{RR}/{stem}.json'))
        assert len(rows) == 600 and {r['name'] for r in rows} == set(pool)
        by = collections.defaultdict(lambda: collections.Counter())
        stp = collections.Counter()
        for r in rows:
            p = pool[r['name']]; L = p['L_true']; src = p['source']
            c = by[L]; c['n'] += 1; c['solved'] += r['solved']; c['n_ok'] += r['n_ok']; c['n_tried'] += r['n_tried']
            c[f'{src}_n'] += 1; c[f'{src}_solved'] += r['solved']
            t = sum(v for k, v in r['reasons'].items() if 'step cap' in k or 'action truncated' in k)
            c['trunc'] += t; c['unsolved_with_trunc'] += (t > 0 and not r['solved'])
            if r['solved']:
                m = min(steps(x) for x in r['proofs']); lab_s = L - p['n_prem']
                stp['lt' if m < lab_s else 'eq' if m == lab_s else 'gt'] += 1
        g17 = None
        f17 = f'{RR}/{stem}__ge17.jsonl'
        if os.path.exists(f17):
            r17 = [json.loads(l) for l in open(f17)]
            g17 = {'solved': sum(r['solved'] for r in r17), 'n': len(r17), 'n_ok': sum(r['n_ok'] for r in r17),
                   'n_tried': sum(r['n_tried'] for r in r17)}
        Ls = None
        for L in reversed(BINS):
            if sum(by[x]['solved'] for x in BINS if x >= L) >= 5:
                Ls = L; break
        Lstar = '< 11' if Ls is None else str(Ls)
        if Ls == 16 and g17 is not None and g17['solved'] >= 5:
            Lstar = '≥ 17'
        elif Ls == 16:
            Lstar = '16' if g17 is not None else '≥ 16 (≥ 17 not read)'
        trunc = summ.get('trunc_frac')
        out[stem] = {'label': lab, 'ckpt': ck, 'params': par, 'format': fmt, 'rung': rung, 'Lstar': Lstar,
                     'by_bin': {L: dict(by[L]) for L in BINS}, 'ge17': g17, 'steps_check': dict(stp),
                     'solved_total': sum(by[L]['solved'] for L in BINS), 'whole_proof_trunc_frac': trunc,
                     'env_end': summ.get('env', {}).get('env_end'), 'peak_mem_gb': summ.get('peak_mem_gb'),
                     'batch': summ['batch'], 'wall_s': summ['wall_s']}
        have.append(stem)
    json.dump(out, open('artifacts/lp/rr_summary.json', 'w'), indent=1)
    print('Solved / 100 per `L_true` bin (k = 256, T 0.8), `transfer_long_rr600.jsonl`; ≥ 17 = solved / 70 of the lower-bound file.\n')
    print('| model | rung | ' + ' | '.join(str(L) for L in BINS) + ' | ≥ 17 | total /600 | `L*` | fewer steps than label / equal / more |')
    print('|---|---|' + '---:|' * (len(BINS) + 2) + '---|---|')
    for s in have:
        o = out[s]; g = o['ge17']
        print(f"| {o['label']} | {o['rung']} | " + ' | '.join(str(o['by_bin'][L].get('solved', 0)) for L in BINS) +
              f" | {g['solved'] if g else '–'} | {o['solved_total']} | {o['Lstar']} | {o['steps_check'].get('lt', 0)} / {o['steps_check'].get('eq', 0)} / {o['steps_check'].get('gt', 0)} |")
    print('\nBy source at 11–14 (solved / n): generator | textbook.\n')
    print('| model | ' + ' | '.join(f'{L} gen | {L} tb' for L in range(11, 15)) + ' |')
    print('|---|' + '---:|' * 8)
    for s in have:
        b = out[s]['by_bin']
        print(f"| {out[s]['label']} | " + ' | '.join(f"{b[L].get('gen_solved', 0)}/{b[L].get('gen_n', 0)} | {b[L].get('textbook_solved', 0)}/{b[L].get('textbook_n', 0)}" for L in range(11, 15)) + ' |')
    print('\nPer-sample accept rate (%) per bin, and truncation.\n')
    print('| model | ' + ' | '.join(str(L) for L in BINS) + ' | ≥ 17 | truncated samples | unsolved theorems with a truncated sample (max solves it could hide) | peak GB (batch) |')
    print('|---|' + '---:|' * (len(BINS) + 1) + '---|---|---|')
    for s in have:
        o = out[s]; b = o['by_bin']; g = o['ge17']
        tr = (f"{100 * o['whole_proof_trunc_frac']:.3f} % (max_new 768)" if o['whole_proof_trunc_frac'] is not None else
              f"{100 * sum(b[L]['trunc'] for L in BINS) / sum(b[L]['n_tried'] for L in BINS):.3f} % (max bin {max(100 * b[L]['trunc'] / b[L]['n_tried'] for L in BINS):.3f} %)")
        print(f"| {o['label']} | " + ' | '.join(f"{100 * b[L]['n_ok'] / b[L]['n_tried']:.2f}" for L in BINS) +
              f" | {(100 * g['n_ok'] / g['n_tried']) if g else float('nan'):.2f} | {tr} | {sum(b[L].get('unsolved_with_trunc', 0) for L in BINS)} | {o['peak_mem_gb']:.1f} ({o['batch']}) |")
    figure(out, have)


def figure(out, have):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    groups = collections.OrderedDict()
    for s in have:
        o = out[s]; key = o['label'].rsplit(' s', 1)[0]
        groups.setdefault(key, []).append(o)
    xs = BINS + [17]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    cmap = plt.get_cmap('tab10')
    for i, (k, os_) in enumerate(groups.items()):
        ls = '-' if 'T1' in k else '--'
        per = []
        for o in os_:
            ys = [o['by_bin'][L]['solved'] / o['by_bin'][L]['n'] for L in BINS] + ([o['ge17']['solved'] / o['ge17']['n']] if o['ge17'] else [math.nan])
            per.append(ys)
            ax.plot(xs, ys, ls, color=cmap(i), alpha=0.35, lw=1, marker='.')
        mean = [sum(y[j] for y in per) / len(per) for j in range(len(xs))]
        ax.plot(xs, mean, ls, color=cmap(i), lw=2, label=f'{k} (n={len(per)})')
    ax.set_xticks(xs); ax.set_xticklabels([str(L) for L in BINS] + ['≥17'])
    ax.set_xlabel('L_true (minlen, ND-derived; upper bound under Lean)'); ax.set_ylabel('solved fraction (k = 256, T 0.8)')
    ax.set_title('transfer_long re-read: 100 theorems per bin (70 at ≥ 17); thin = seeds, thick = mean')
    ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.3)
    os.makedirs('figures', exist_ok=True)
    fig.tight_layout(); fig.savefig('figures/lp_rate_by_bin.png', dpi=130)


if __name__ == '__main__':
    main()
