#!/usr/bin/env python3
"""support-followups D: classify where the base's improbability of each proof sits.  Reads artifacts/sf/d_steps.jsonl
(sf_steps.py), prints tables, writes artifacts/sf/d_summary.json.  Pre-registered rules: preregistration/support-followups.md §D.

Primary unit: for each survivor, its EI proof with the highest base log p (T 1.0).
  concentrated: s2 >= 0.50 and w1 <= -6;  spread: s2 < 0.50 and w1 > -6;  else mixed.
  reading: new move if >= 20 of 29 concentrated; compounding if >= 20 spread; else mixed.
"""
import json, statistics as st, collections, sys

W1_CUT, S2_CUT, N_READ = -6.0, 0.50, 20
MODEL = ('base s0 = ckpts/lf/stage1_a1_seq_s0.pt md5 9bde44c0 (3,214,336 params, from scratch, lean_seq, cap 6, '
         'Stage 1 on data/p2/train_depth3_f0_a1.jsonl)')


def label(sm):
    if sm['s2'] >= S2_CUT and sm['w1'] <= W1_CUT:
        return 'concentrated'
    if sm['s2'] < S2_CUT and sm['w1'] > W1_CUT:
        return 'spread'
    return 'mixed'


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main(path='artifacts/sf/d_steps.jsonl', T='T1', out='artifacts/sf/d_summary.json'):
    R = [json.loads(l) for l in open(path)]
    by_set = collections.defaultdict(list)
    for r in R:
        by_set[r['set']].append(r)
    res = {'model': MODEL, 'temperature': T, 'source': path, 'sets': {}}
    print(f'D at {T} under {MODEL}\n')
    print('set  proofs theorems | total logp med [min,max] | steps med | w1 med | s1 med | s2 med | labels (all proofs)')
    best = {}
    for s in ('S', 'C1', 'C2', 'C3'):
        rs = by_set[s]
        sm = [r['base'][T] for r in rs]
        labs = collections.Counter(label(x) for x in sm)
        # per-theorem best (highest total) proof
        b = {}
        for r in rs:
            if r['name'] not in b or r['base'][T]['total'] > b[r['name']]['base'][T]['total']:
                b[r['name']] = r
        best[s] = b
        bl = collections.Counter(label(r['base'][T]) for r in b.values())
        tot = [x['total'] for x in sm]
        # per-step lp excluding the worst step
        rest = [st.mean(sorted(p['lp'] for p in x['steps'])[1:]) for x in sm if len(x['steps']) > 1]
        cl = collections.Counter(); cl2 = collections.Counter(); wt = collections.Counter(); wt2 = collections.Counter()
        wk = collections.Counter(x['worst_step_kind'].split(':')[0] + (':' + x['worst_step_kind'].split(':')[1] if ':' in x['worst_step_kind'] else '') for x in sm)
        for x in sm:
            for k, v in x['class_lp'].items(): cl[k.split(':')[0]] += v
            for k, v in x['class_lp_pos'].items(): cl2[k.split(':')[0]] += v
            for w in x['worst_tokens']:
                wt[w['cls'].split(':')[0]] += 1; wt2[w['cls_pos'].split(':')[0]] += 1
        ctot = sum(cl.values()); ctot2 = sum(cl2.values()); nw = sum(wt.values())
        d = {'n_proofs': len(rs), 'n_theorems': len(b),
             'total_med': st.median(tot), 'total_min': min(tot), 'total_max': max(tot),
             'steps_med': st.median(x['n_steps'] for x in sm), 'w1_med': st.median(x['w1'] for x in sm),
             'w1_p05': pct([x['w1'] for x in sm], 0.05), 's1_med': st.median(x['s1'] for x in sm),
             's2_med': st.median(x['s2'] for x in sm), 'rest_step_mean_med': st.median(rest) if rest else None,
             'labels_all': dict(labs), 'labels_best_per_theorem': dict(bl),
             'surprisal_share_prereg_class': {k: round(v / ctot, 3) for k, v in cl.items()},
             'surprisal_share_position_class': {k: round(v / ctot2, 3) for k, v in cl2.items()},
             'worst3_tokens_prereg_class': {k: round(v / nw, 3) for k, v in wt.items()},
             'worst3_tokens_position_class': {k: round(v / nw, 3) for k, v in wt2.items()},
             'worst_step_kind': dict(wk.most_common())}
        res['sets'][s] = d
        print(f"{s:4s} {len(rs):6d} {len(b):8d} | {d['total_med']:7.2f} [{d['total_min']:.1f},{d['total_max']:.1f}] | "
              f"{d['steps_med']:5.1f} | {d['w1_med']:6.2f} | {d['s1_med']:.2f} | {d['s2_med']:.2f} | {dict(labs)}")
    print('\nsurprisal share by class (pre-registered | position-based):')
    for s, d in res['sets'].items():
        print(f"  {s:3s} {d['surprisal_share_prereg_class']} | {d['surprisal_share_position_class']}")
    print('worst-3 tokens by class (pre-registered | position-based):')
    for s, d in res['sets'].items():
        print(f"  {s:3s} {d['worst3_tokens_prereg_class']} | {d['worst3_tokens_position_class']}")
    print('worst step kind:')
    for s, d in res['sets'].items():
        print(f"  {s:3s} {d['worst_step_kind']}")

    # the pre-registered primary: 29 survivors, best proof each
    bS = best['S']
    c2_w1 = [r['base'][T]['w1'] for r in by_set['C2']]
    p05 = pct(c2_w1, 0.05)
    rows = []
    for n, r in sorted(bS.items(), key=lambda kv: (kv[1]['L_true'], kv[1]['base'][T]['total'])):
        x = r['base'][T]
        rows.append({'name': n, 'L_true': r['L_true'], 'n_lines': r['n_lines'], 'term_size': r['term_size'],
                     'total': round(x['total'], 2), 'n_steps': x['n_steps'], 'w1': round(x['w1'], 2), 'w2': round(x['w2'], 2),
                     's1': round(x['s1'], 3), 's2': round(x['s2'], 3), 'label': label(x),
                     'worst_step_kind': x['worst_step_kind'], 'below_C2_w1_p05': x['w1'] < p05,
                     'worst_tokens': [(w['tok'], w['cls'], w['cls_pos'], round(w['lp'], 2)) for w in x['worst_tokens']],
                     'ei_logp_total': round(r['ei']['logp_total']['1.0' if T == 'T1' else '0.8'], 2) if 'ei' in r else None})
    lab = collections.Counter(r['label'] for r in rows)
    reading = ('a new move' if lab['concentrated'] >= N_READ else 'compounding reliability' if lab['spread'] >= N_READ else 'mixed')
    below = sum(r['below_C2_w1_p05'] for r in rows)
    rest_S = res['sets']['S']['rest_step_mean_med']; rest_C1 = res['sets']['C1']['rest_step_mean_med']
    print(f'\nPRIMARY ({len(rows)} survivors, best EI proof each, {T}): {dict(lab)}  -> reading: {reading}')
    print(f'  survivors with w1 below C2 5th percentile ({p05:.2f}): {below} / {len(rows)}')
    print(f'  median mean-per-step log p excluding the worst step: S {rest_S:.3f}, C1 {rest_C1:.3f}, C2 {res["sets"]["C2"]["rest_step_mean_med"]:.3f}')
    print('\n name              L  lines term total steps   w1    w2   s1   s2  label         worst step  worst tokens')
    for r in rows:
        print(f" {r['name']:17s} {r['L_true']:2d} {r['n_lines']:3d} {r['term_size']:4d} {r['total']:6.1f} {r['n_steps']:4d} "
              f"{r['w1']:6.1f} {r['w2']:5.1f} {r['s1']:.2f} {r['s2']:.2f}  {r['label']:12s} {r['worst_step_kind']:11s} "
              + ' '.join(f"{t}[{c.split(':')[0][:3]}/{c2.split(':')[0][:3]}]{v}" for t, c, c2, v in r['worst_tokens']))
    res['primary'] = {'labels': dict(lab), 'reading': reading, 'below_C2_w1_p05': below, 'C2_w1_p05': p05, 'rows': rows}
    json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False)
    print('->', out)


if __name__ == '__main__':
    main(*sys.argv[1:])


def alternatives(path='artifacts/sf/d_alternatives.jsonl', out='artifacts/sf/d_alternatives_summary.json'):
    """Tally of what the base preferred at each survivor's single worst token (sf_alt.py): categorised by the base's
    top-1 token there.  Categories: ends-proof (base wants <eos> where EI closes a nested box), closes-box-early
    (base wants `exact` where EI states another `have`), rule (at `:=`: base wants a different term head, e.g. ⟨ or a
    cited name, where EI opens a box, or vice versa), formula (inside a stated formula), citation (which name)."""
    rows = [json.loads(l) for l in open(path)]
    cat = collections.Counter(); ex = collections.defaultdict(list); ei_lp = []
    for r in rows:
        w = r['worst'][0]; alt = w['base_top3'][0][0]; prev = w['context'].split()[-1] if w['context'] else ''
        if alt == '<eos>': c = 'ends-proof'
        elif alt == 'exact' and w['tok'] == 'have': c = 'closes-box-early'
        elif prev == ':=': c = 'rule'
        elif w['cls_pos'] == 'logic:formula': c = 'formula'
        else: c = 'citation' if w['cls'].startswith('name') else 'other'
        cat[c] += 1; ex[c].append(r['name']); ei_lp.append(w['ei_lp_at_shift'])
    res = {'n': len(rows), 'categories': dict(cat.most_common()), 'examples': ex,
           'ei_lp_at_worst_token_median': st.median(ei_lp), 'ei_lp_at_worst_token_min': min(ei_lp),
           'base_top1_mass_median': st.median(__import__('math').exp(r['worst'][0]['base_top3'][0][1]) for r in rows)}
    json.dump(res, open(out, 'w'), indent=1)
    print(f"\nworst-token alternatives ({len(rows)} survivors): {dict(cat.most_common())}; "
          f"EI log p at that token: median {res['ei_lp_at_worst_token_median']:.3f}, min {res['ei_lp_at_worst_token_min']:.2f}; "
          f"base top-1 mass there: median {res['base_top1_mass_median']:.3f}")
    return res


if __name__ == '__main__' and len(sys.argv) == 1:
    alternatives()
