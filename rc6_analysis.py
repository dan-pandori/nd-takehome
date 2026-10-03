#!/usr/bin/env python3
"""rl-continue-cap6: per-round table r1-r16, the rounds 1-16 figure (cap 12 overlaid), r8 / r16 read-outs, pre-registered checks.

Model (every number): trajectory-cap6's best-cap6 T1 ladders, seeds 0-2 -- ALiBiGPT 9,560,832 params, lean_staten, from
scratch on the cap-6 set (data/p2/train_depth3_f0_a1.jsonl, 155,000 records), Stage-1 1,200 s, EI rounds k 32 T 0.8 on
the 4,495 rl_targets (r1-r8 trajectory-cap6, r9-r16 here).  Overlay: trajectory's best-cap12 ladders (same recipe on
K12, cap 12), r1-r8 from trajectory and r9-r16 from rl-continue when present.  Lean alone decides.  Inputs (pulled files):
  artifacts/rc6/tj6_rounds/s<S>_round_<r>.json        trajectory-cap6's r1-r8 round JSONs (origin/dan_trajectory-cap6)
  artifacts/rc6/la_T1_best6_s<S>/round_<r>.json       r9-r16
  artifacts/rc6/tj6_eval/s<S>_{pend,r8}__{tb72,h250}_x{0,1}.jsonl  trajectory-cap6's reads (bucket trajectory-cap6/artifacts/tj6/eval)
  artifacts/rc6/eval/s<S>_r<r>__<read>_x<x>.jsonl      this run's reads
  artifacts/rc6/cap12_rounds/s<S>_round_<r>.json      cap 12 overlay (trajectory r1-r8 via rl-continue's tj_rounds; rl-continue r9-r16)
Groups (trajectory-cap6's definition, tj6_analysis.groups): seed-0 samples at pend and r8; A pend solves; B r8 not pend; C neither.

  python3 rc6_analysis.py > artifacts/rc6/analysis_stdout.txt      (writes artifacts/rc6/summary.json, figures/rc6_rounds.png)
"""
import json, math, os
import numpy as np

SEEDS = (0, 1, 2)
TJ, RC = 'artifacts/rc6/tj6_rounds', 'artifacts/rc6'
POOLS = ('tb72', 'h250')


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def passk(n, c, k):
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


def round_json(s, r):
    p = f'{TJ}/s{s}_round_{r}.json' if r <= 8 else f'{RC}/la_T1_best6_s{s}/round_{r}.json'
    return json.load(open(p)) if os.path.exists(p) else None


def round_json12(s, r):
    p = f'{RC}/cap12_rounds/s{s}_round_{r}.json'
    return json.load(open(p)) if os.path.exists(p) else None


def read(s, ck, pool, x, fallback=False):
    """{name: (n_ok, n_tried)} or None."""
    p = f'{RC}/tj6_eval/s{s}_{ck}__{pool}_x{x}.jsonl' if ck in ('pend', 'r8') and pool in POOLS else f'{RC}/eval/s{s}_{ck}__{pool}_x{x}.jsonl'
    if fallback and not os.path.exists(p) and pool == 'h250':       # budget fallback: holdout250 read on the seed's group-C theorems only
        p = f'{RC}/eval/s{s}_{ck}__h250C_x{x}.jsonl'
    if not os.path.exists(p):
        return None
    return {r['name']: (r['n_ok'], r['n_tried']) for r in rj(p)}


def groups(s):
    g = {}
    for pool in POOLS:
        a, b = read(s, 'pend', pool, 0), read(s, 'r8', pool, 0)
        for n in a:
            g[n] = 'A' if a[n][0] > 0 else 'B' if b[n][0] > 0 else 'C'
    return g


def main():
    out = {'rounds': {}, 'reads': {}, 'groups': {}}
    # ---------------- per round
    print('## Per round (targets: 4,495 rl_targets; transfer: 2,285; acc = sample accuracy; trunc = env truncated + step cap / samples)\n')
    print('| seed | round | new targets | targets_cum | new transfer | transfer_cum | target acc | transfer acc | trunc % | secs |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for s in SEEDS:
        rows, prev = [], None
        for r in range(1, 17):
            j = round_json(s, r)
            if j is None:
                break
            tc, fc = j['targets_cum']['solved'], j['transfer_cum']['solved']
            ee = j['env']['env_end']
            tr = (ee.get('truncated', 0) + ee.get('step_cap', 0)) / max(1, sum(ee.values()))
            row = {'round': r, 'targets_cum': tc, 'transfer_cum': fc, 'new_targets': tc - prev[0] if prev else None,
                   'new_transfer': fc - prev[1] if prev else None, 'target_acc': j['target_sample_acc'],
                   'transfer_acc': j['transfer_sample_acc'], 'trunc': tr, 'secs': j['secs'], 'batch_ckpt': j['ckpt']}
            rows.append(row); prev = (tc, fc)
            print(f"| s{s} | {r} | {row['new_targets'] if row['new_targets'] is not None else '—'} | {tc} | "
                  f"{row['new_transfer'] if row['new_transfer'] is not None else '—'} | {fc} | {row['target_acc']:.3f} | "
                  f"{row['transfer_acc']:.3f} | {100 * tr:.3f} | {j['secs']:.0f} |")
        out['rounds'][s] = rows
    print('\n## r9-r16 totals per seed (pre-registered: +40..+70 targets, +30..+60 transfer; falsifier: >= 100 targets on >= 2 seeds)\n')
    print('| seed | rounds done | new targets r9+ | new transfer r9+ | r8 targets_cum | last targets_cum | last transfer_cum |')
    print('|---|---|---|---|---|---|---|')
    tot = {}
    for s in SEEDS:
        rows = out['rounds'][s]; r8 = rows[7]; last = rows[-1]
        tot[s] = (last['targets_cum'] - r8['targets_cum'], last['transfer_cum'] - r8['transfer_cum'], last['round'])
        print(f"| s{s} | {last['round']} | {tot[s][0]} | {tot[s][1]} | {r8['targets_cum']} | {last['targets_cum']} | {last['transfer_cum']} |")
    out['totals_r9plus'] = tot
    c12 = {s: [round_json12(s, r) for r in (8, 16)] for s in SEEDS}
    print('\ncap 12 targets_cum (r8, r16): ' + ', '.join(f"s{s} {[j['targets_cum']['solved'] if j else None for j in c12[s]]}" for s in SEEDS))
    print('cap 6 reaches 4,365 (cap 12 lowest r8) on seeds: ' + str([s for s in SEEDS if out['rounds'][s][-1]['targets_cum'] >= 4365]))
    n60 = sum(1 for s in SEEDS if tot[s][0] >= 100)
    print(f'\nfalsifier 1 (>= 100 new targets on >= 2 of 3 seeds): {n60} seeds -> {"FALSIFIED (not saturated)" if n60 >= 2 else "not met"}')
    # ---------------- reads: solved counts
    print('\n## Read-outs: solved / n (k 256, T 0.8; r8 tb72/h250 = trajectory-cap6 files)\n')
    print('| seed | ckpt | read | x0 | x1 |\n|---|---|---|---|---|')
    for s in SEEDS:
        for ck in ('r8', 'r12', 'r16'):
            for pool in ('tb72', 'h250', 'h250C', 'rr1316', 'long2'):
                v = []
                for x in (0, 1):
                    d = read(s, ck, pool, x)
                    v.append(f'{sum(1 for n in d if d[n][0] > 0)} / {len(d)}' if d else '—')
                    if d:
                        out['reads'][f's{s}_{ck}_{pool}_x{x}'] = sum(1 for n in d if d[n][0] > 0)
                if v != ['—', '—']:
                    print(f'| s{s} | {ck} | {pool} | {v[0]} | {v[1]} |')
    # rr1316 by L_true_lb
    print('\n## rr600 13-16 solved by L_true_lb (ND-derived lower-bound label), sample seed 0\n')
    lab = {r['name']: r.get('L_true_lb') for r in rj('data/rc6/rr600_13_16.jsonl')}
    for s in SEEDS:
        for ck in ('r8', 'r12', 'r16'):
            d = read(s, ck, 'rr1316', 0)
            if d:
                by = {L: sum(1 for n in d if lab.get(n) == L and d[n][0] > 0) for L in (13, 14, 15, 16)}
                print(f's{s} {ck}: {by}  (of 100 each)')
    # ---------------- groups: pass@k
    print('\n## pass@k by trajectory-cap6 group (mean over the group, textbook72 + holdout250 pooled); unbiased estimator, n = 256\n')
    print('| seed | group | n | ck | x | pass@1 | pass@256 | solved |\n|---|---|---|---|---|---|---|---|')
    cvals = {}
    for s in SEEDS:
        g = groups(s); out['groups'][s] = {k: sum(1 for v in g.values() if v == k) for k in 'ABC'}
        for grp in 'ABC':
            names = [n for n in g if g[n] == grp]
            for ck in ('r8', 'r12', 'r16'):
                for x in (1, 0):
                    d = {}
                    for pool in POOLS:
                        dd = read(s, ck, pool, x, fallback=True)
                        if dd is None:
                            d = None; break
                        d.update(dd)
                    if not d or any(n not in d for n in names):     # h250C covers group C only
                        continue
                    p1 = float(np.mean([passk(d[n][1], d[n][0], 1) for n in names]))
                    p256 = float(np.mean([passk(d[n][1], d[n][0], 256) for n in names]))
                    sol = sum(1 for n in names if d[n][0] > 0)
                    cvals[(s, grp, ck, x)] = p256
                    print(f'| s{s} | {grp} | {len(names)} | {ck} | {x} | {p1:.3f} | {p256:.3f} | {sol} |')
    out['group_pass256'] = {f'{k[0]}_{k[1]}_{k[2]}_x{k[3]}': v for k, v in cvals.items()}
    c8 = [cvals.get((s, 'C', 'r8', 1)) for s in SEEDS]
    c16 = [cvals.get((s, 'C', 'r16', 1)) for s in SEEDS]
    if None not in c8 and None not in c16:
        spread = max(c8) - min(c8); d = float(np.mean(c16) - np.mean(c8)); up = sum(1 for a, b in zip(c8, c16) if b > a)
        print(f'\nfalsifier 2 (group C pass@256 x1): r8 per seed {[round(v, 3) for v in c8]} (spread {spread:.3f}); '
              f'r16 {[round(v, 3) for v in c16]}; mean change {d:+.3f}; seeds rising {up} -> '
              f'{"FALSIFIED (not saturated)" if d > spread and up >= 2 else "not met"}')
        out['falsifier2'] = {'c8': c8, 'c16': c16, 'spread': spread, 'mean_change': d, 'seeds_rising': up}
    json.dump(out, open(f'{RC}/summary.json', 'w'), indent=1, default=str)
    figure(out)


def figure(out):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    col = {0: '#2a6fdb', 1: '#e8590c', 2: '#2f9e44'}
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, key, band, title in ((axs[0], 'targets_cum', (40, 70), 'rl_targets solved (cumulative, of 4,495)'),
                                 (axs[1], 'transfer_cum', (30, 60), 'transfer solved (cumulative, of 2,285)'),
                                 (axs[2], 'new_targets', None, 'new targets per round')):
        for s in SEEDS:
            rows = out['rounds'][s]
            xs = [r['round'] for r in rows if r[key] is not None]; ys = [r[key] for r in rows if r[key] is not None]
            ax.plot(xs, ys, 'o-', ms=3, color=col[s], label=f'cap 6 seed {s}')
            r12 = [(r, round_json12(s, r)) for r in range(1, 17)]
            r12 = [(r, j[key]['solved']) for r, j in r12 if j] if key != 'new_targets' else \
                  [(r, round_json12(s, r)['targets_cum']['solved'] - round_json12(s, r - 1)['targets_cum']['solved'])
                   for r in range(2, 17) if round_json12(s, r) and round_json12(s, r - 1)]
            if r12:
                ax.plot([a for a, _ in r12], [b for _, b in r12], 's--', ms=2.5, lw=1, color=col[s], alpha=0.55,
                        label=f'cap 12 seed {s}' if s == 0 or key != 'new_targets' else None)
            if band:
                y8 = rows[7][key]
                ax.fill_between([8, 16], [y8, y8 + band[0]], [y8, y8 + band[1]], color=col[s], alpha=0.12)
        if key == 'new_targets':
            ax.set_yscale('symlog', linthresh=10); ax.axhspan(40 / 8, 70 / 8, color='0.5', alpha=0.15, label='pre-registered 40-70 / 8 rounds')
        else:
            lo = min(r[key] for s in SEEDS for r in out['rounds'][s][3:]); hi = max(r[key] for s in SEEDS for r in out['rounds'][s])
            ax.set_ylim(bottom=lo - 5); ax.set_xlim(3.5, 16.5)
        ax.axvline(8.5, color='0.6', ls=':', lw=1); ax.set_xlabel('EI round (r1-r8 trajectory[-cap6], r9-r16 rl-continue[-cap6])'); ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8)
    fig.suptitle('rl-continue-cap6: best-cap6 T1 ladders (9.56M ALiBiGPT, lean_staten, cap-6 set), rounds 1-16, solid; '
                 'best-cap12 (K12) dashed; shaded = pre-registered range from r8', fontsize=10)
    fig.tight_layout(); os.makedirs('figures', exist_ok=True); fig.savefig('figures/rc6_rounds.png', dpi=130)


if __name__ == '__main__':
    main()
