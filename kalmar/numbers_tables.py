#!/usr/bin/env python3
"""Markdown tables for numbers.md § kalmar-pretrain, generated from kalmar/analysis.py's summary.json (no hand copying).

  python3 kalmar/numbers_tables.py [--summary artifacts/kalmar/summary.json] > artifacts/kalmar/numbers_tables.md

Cells are "s0 / s1 / s2 (IQM)"; IQM with best-state's iqm (= the mean at n = 3).
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis import iqm, boot_ci

ARMS = ('KAL-D', 'KAL-C', 'control')


def cell(xs, pct=False, d=1, ci=False):
    xs = [x for x in (xs or []) if x is not None]
    if not xs:
        return '—'
    f = (lambda v: f'{100 * v:.{d}f}') if pct else (lambda v: f'{v:.{d}f}')
    s = ' / '.join(f(x) for x in xs)
    if len(xs) > 1:
        s += f' ({f(iqm(xs))}'
        if ci:
            lo, hi = boot_ci(xs)
            s += f' [{f(lo)}, {f(hi)}]'
        s += ')'
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', default='artifacts/kalmar/summary.json')
    a = ap.parse_args()
    S = json.load(open(a.summary))
    P = print
    # TF agreement
    P('#### E1 teacher-forced agreement on tf1200 (% of states; source `artifacts/kalmar/tf/<model>__tf1200.json`)\n')
    rows = [('all', 'all states'), ('tagg=pr', 'premise line'), ('tagg=lem', 'X ∨ ¬X derivation'), ('tagg=split', 'split (∨E)'),
            ('tagg=efq', 'ex falso'), ('tagg=leaf:and+', 'leaf ∧ true'), ('tagg=leaf:and-', 'leaf ∧ false'),
            ('tagg=leaf:or+', 'leaf ∨ true'), ('tagg=leaf:or-', 'leaf ∨ false'), ('tagg=leaf:imp+B', 'leaf → (B true)'),
            ('tagg=leaf:imp+A', 'leaf → (A false)'), ('tagg=leaf:imp-', 'leaf → false'), ('tagg=leaf:not+', 'leaf ¬¬A'),
            ('tagg=leaf:bot-', 'leaf ¬⊥'), ('tagg=close', 'box close'), ('atoms=1', '1 atom'), ('atoms=2', '2 atoms'),
            ('atoms=3', '3 atoms'), ('atoms=4', '4 atoms')]
    P('| step type | ' + ' | '.join(ARMS) + ' |')
    P('|---|' + '---|' * len(ARMS))
    for k, lab in rows:
        P(f'| {lab} | ' + ' | '.join(cell(S['tf'].get(arm, {}).get(k), pct=True, d=1, ci=(k == 'all')) for arm in ARMS) + ' |')
    P(f"\nRecords whose every state agrees (of 1,200): " +
      '; '.join(f"{arm} {S['tf'][arm]['records_all_agree']}" for arm in ARMS if arm in S['tf']))
    # depth / decile
    P('\nBy box depth (frames open before the action), KAL-D: ' +
      '; '.join(f"{k.split('=')[1]}: {cell(S['tf']['KAL-D'].get(k), pct=True)}" for k in [f'depth={d}' for d in range(7)]))
    P('\nBy position decile, KAL-D: ' +
      '; '.join(f"{k.split('=')[1]}: {cell(S['tf']['KAL-D'].get(k), pct=True)}" for k in [f'decile={d}' for d in range(10)]))
    # learning curve
    P('\n#### KAL-D learning curve (snapshots are mid-schedule checkpoints; source `artifacts/kalmar/{tf,free}/kalD_s<S>_step<N>__*`)\n')
    P('| step | TF agreement % | greedy tf1200 valid % |')
    P('|---|---|---|')
    for st, v in sorted(S['curve'].items(), key=lambda x: int(x[0])):
        P(f"| {int(st):,} | {cell(v['tf'], pct=True)} | {cell(v['greedy_valid'], pct=True)} |")
    # compounding
    P('\n#### Compounding (teacher-forced; theorems whose every state agrees, observed vs independent errors)\n')
    P('| algorithm actions | n | KAL-D observed % | KAL-D independent % | KAL-D disagreements / theorem | KAL-C observed % |')
    P('|---|---|---|---|---|---|')
    cd = S['compound'].get('KAL-D', {}); cc = S['compound'].get('KAL-C', {})
    for b in ('0-49', '50-99', '100-149', '150-199', '200-299', '300-1000000'):
        vs = [cd[s][b] for s in sorted(cd) if b in cd[s]]
        vc = [cc[s][b] for s in sorted(cc) if b in cc[s]]
        if vs:
            P(f"| {b.replace('1000000', '…')} | {vs[0]['n']} | {cell([v['observed'] for v in vs], pct=True)} | "
              f"{cell([v['predicted'] for v in vs], pct=True)} | {cell([v['mean_disagreements'] for v in vs], d=2)} | "
              f"{cell([v['observed'] for v in vc], pct=True)} |")
    # leaf depth
    P('\n#### Leaf steps by the depth of the formula the step writes (TF agreement %)\n')
    P('| depth | ' + ' | '.join(ARMS) + ' |')
    P('|---|' + '---|' * len(ARMS))
    for dd in ('0', '1', '2', '3', '4', '5', '6'):
        P(f'| {dd}{"+" if dd == "6" else ""} | ' + ' | '.join(cell(S['leaf_depth'].get(arm, {}).get(dd), pct=True) for arm in ARMS) + ' |')
    # greedy free generation
    P('\n#### E2 greedy free generation on tf1200 (% of theorems; Lean on the literal text; source `artifacts/kalmar/free/<model>__tf1200_greedy.json`)\n')
    P('| | ' + ' | '.join(f'{arm} valid | {arm} exact Kalmár' for arm in ARMS) + ' |')
    P('|---|' + '---|' * (2 * len(ARMS)))
    for key in ('all', 'atoms=1', 'atoms=2', 'atoms=3', 'atoms=4'):
        P(f'| {key} | ' + ' | '.join(f"{cell(S['free'][arm][key]['valid'], pct=True)} | {cell(S['free'][arm][key]['follow'], pct=True)}"
                                   for arm in ARMS) + ' |')
    P('\nValid deviations (Lean-valid, not the algorithm\'s), % of theorems, and the shorter-than-algorithm part: ' +
      '; '.join(f"{arm} {cell(S['free'][arm]['all']['dev_valid'], pct=True)} (shorter {cell(S['free'][arm]['all']['dev_valid_shorter'], pct=True)})" for arm in ARMS))
    P('\nE3 (T 0.8, k 8, tf1200; % of attempts): ' + '; '.join(
        f"{arm} valid {cell(S['free_t08'][arm]['valid'], pct=True)}, exact Kalmár {cell(S['free_t08'][arm]['follow'], pct=True)}" for arm in ARMS if arm in S.get('free_t08', {})))
    # solve rates
    P('\n#### E4 / E5 solve rates (theorems solved, unbiased pass@k; source `artifacts/kalmar/eval/<model>_{plain,logical}_k32.rows.jsonl.gz`)\n')
    P('| set (n) | arm | plain pass@1 | plain pass@8 | plain pass@32 | guided pass@1 | guided pass@32 | plain pass@256 |')
    P('|---|---|---|---|---|---|---|---|')
    for lab in ('holdout250', 'rr600', 'ge17', 'long2', 'candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14',
                'textbook72', 'g1_premises', 'g2_large', 'g3_classical'):
        for arm in ARMS:
            pl = S['solve'].get(arm, {}).get('plain', {}).get(lab, {}); gd = S['solve'].get(arm, {}).get('logical', {}).get(lab, {})
            n = pl.get('n') or gd.get('n') or '?'
            p256 = cell(pl.get('pass@256'), d=0) if arm == 'control' else '—'
            if lab == 'rr600' and arm == 'control':
                p256 += f" (Q 13–16: {cell(pl.get('Q@256'), d=0)})"
            P(f"| {lab} ({n}) | {arm} | {cell(pl.get('pass@1'))} | {cell(pl.get('pass@8'))} | {cell(pl.get('pass@32'))} | "
              f"{cell(gd.get('pass@1'))} | {cell(gd.get('pass@32'))} | {p256} |")
    # breakdown
    P('\n#### Plain pass@32 by atom count and by the algorithm\'s proof length (standard sets pooled; % of theorems)\n')
    P('| stratum | ' + ' | '.join(ARMS) + ' |')
    P('|---|' + '---|' * len(ARMS))
    for k in ('1', '2', '3', '4'):
        P(f'| {k} atom(s) | ' + ' | '.join(cell(S['breakdown'].get(arm, {}).get('atoms', {}).get(k), pct=True) for arm in ARMS) + ' |')
    for b in ('0-99', '100-149', '150-199', '200-299', '300-1024'):
        P(f'| {b} actions | ' + ' | '.join(cell(S['breakdown'].get(arm, {}).get('algo_len', {}).get(b), pct=True) for arm in ARMS) + ' |')
    # generalisation greedy
    P('\n#### Generalisation and long sets, greedy (% of theorems valid / exact Kalmár)\n')
    P('| set | ' + ' | '.join(ARMS) + ' |')
    P('|---|' + '---|' * len(ARMS))
    for lab in ('g1_premises', 'g2_large', 'g3_classical', 'holdout250', 'rr600', 'hand_proved_14'):
        g = S['gen'].get(lab, {})
        P(f'| {lab} | ' + ' | '.join(f"{cell(g.get(arm, {}).get('valid'), pct=True)} / {cell(g.get(arm, {}).get('follow'), pct=True)}" for arm in ARMS) + ' |')
    g1 = S.get('g1_supplied', {})
    P('\nG1 with the premise lines supplied (theorems solved of 200): ' + '; '.join(
        f"{nm} {arm} {cell(g1.get(nm, {}).get(arm, {}).get('solved'), d=0)}" for nm in ('greedy', 'k32') for arm in ARMS))
    P('\nG2 by size bin (greedy % valid | plain pass@32 %): ' + '; '.join(
        f"{arm} {b}: {cell(v[0], pct=True)} | {cell(v[1], pct=True)}" for arm in ARMS for b, v in sorted(S.get('g2_bins', {}).get(arm, {}).items())))
    # cut-offs
    P('\n#### Cut-offs in the k 32 reads\n')
    for arm, d in S.get('cutoffs', {}).items():
        for read, t in d.items():
            P(f"- {arm} {read}: {t['n']:,} attempts; step cap {t.get('step_cap', 0) / t['n']:.4%}; ended by a truncated action "
              f"{t.get('truncated', 0) / t['n']:.4%}; truncation events (guided redraws) {t.get('truncation_events', 0):,}")
    # batch check
    bc = S.get('batch_check', {})
    if bc:
        P('\n#### Batch-effect check (Addendum 2): plain k 32, batch 2,048 vs 1,024, same checkpoint\n')
        P('| model | set | pass@1 b2048 | pass@1 b1024 | pass@32 b2048 | pass@32 b1024 |')
        P('|---|---|---|---|---|---|')
        for t, d in bc.items():
            for lab, v in d.items():
                P(f"| {t} | {lab} | {v['b2048_pass@1']:.1f} | {v['b1024_pass@1']:.1f} | {v['b2048_pass@32']:.0f} | {v['b1024_pass@32']:.0f} |")


if __name__ == '__main__':
    main()
