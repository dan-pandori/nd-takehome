#!/usr/bin/env python3
"""ladder-A leaderboard: re-derives every number from the pulled files.

  python ladder_analysis.py [--arms la_frozen_s0 la_T1_s0 ...] --out ladder.md --json artifacts/ladder/summary.json

Per arm (artifacts/ladder/<arm>/): found_transfer_<R>.jsonl and found_<R>.jsonl (found_union_<R>.jsonl for T6
siblings), novelty_proofs.jsonl (base log p at T = 0.8 under stage1_abs.pt, marginalised over start index).
Counts: distinct proofs after start-index normalisation (normalize.norm; re-applied here), theorems solved per L_true
bin (L_true = the pool record's n_lines) with Wilson 95 % intervals, L* = max L with >= 5 theorems solved at
L_true >= L, base-reachability split of the counted proofs (p >= 1e-5: elicitation; else creation; also the 1/256 line).
"""
import argparse, json, os, sys, glob, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)

RUNGS = {'frozen': 'frozen control', 'T1': 'EI baseline', 'T2': 'EI + difficulty-weighted sampling', 'T3': 'EI + hindsight relabelling',
         'T4': 'EI + moving target window', 'T5': 'EI + precursor injection', 'T6': 'EI + sibling ensemble (2 x k=16)'}
BINS = list(range(7, 15))


def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def load_found(fn, pool):
    """-> name -> set(norm proofs); verify every proof string is distinct after normalisation."""
    by = collections.defaultdict(set)
    for x in rd(fn):
        by[x['name']].add(norm(x['proof']))
    return by


def analyse_pool(found, pool, nov=None, ref_solved=None):
    Lt = {r['name']: r['n_lines'] for r in pool}
    solved = {n for n in found if found[n]}
    res = {'n': len(pool), 'solved': len(solved), 'distinct_proofs': sum(len(v) for v in found.values())}
    ge = {L: sum(1 for n in solved if Lt[n] >= L) for L in range(7, 16)}
    res['ge'] = ge
    res['lstar'] = max([L for L, c in ge.items() if c >= 5], default=0)
    bins = {}
    for L in BINS:
        n = sum(1 for r in pool if r['n_lines'] == L)
        k = sum(1 for r in pool if r['n_lines'] == L and r['name'] in solved)
        lo, hi = wilson(k, n)
        bins[L] = {'solved': k, 'n': n, 'rate': k / n if n else None, 'ci': [lo, hi]}
    res['bins'] = bins
    # by source
    src = collections.defaultdict(lambda: [0, 0])
    for r in pool:
        src[r.get('source')][0] += r['name'] in solved; src[r.get('source')][1] += 1
    res['by_source'] = {s: {'solved': k, 'n': n} for s, (k, n) in src.items()}
    # theorems solved at L_true >= 9 by schema
    res['schemas_ge9'] = dict(collections.Counter(r['schema'] for r in pool if r['name'] in solved and r['n_lines'] >= 9 and r.get('schema')))
    res['gen_ge9'] = sum(1 for r in pool if r['name'] in solved and r['n_lines'] >= 9 and r.get('source') == 'gen')
    # generator-only L*
    ge_gen = {L: sum(1 for r in pool if r['name'] in solved and r['n_lines'] >= L and r.get('source') == 'gen') for L in range(7, 16)}
    res['lstar_gen_only'] = max([L for L, c in ge_gen.items() if c >= 5], default=0)
    if ref_solved is not None:
        res['solved_not_in_ref'] = len(solved - ref_solved)
        res['ge8_not_in_ref'] = sum(1 for n in solved - ref_solved if Lt[n] >= 8)
    if nov is not None:
        # base reachability per theorem: max over its counted proofs of base p (T=0.8)
        best = collections.defaultdict(lambda: -1e9)
        for x in nov:
            best[x['name']] = max(best[x['name']], x['base_logp_T08'])
        reach = {}
        for L in (7, 8, 9, 10, 11, 12):
            names = [n for n in solved if Lt[n] >= L]
            scored = [n for n in names if n in best]
            reach[L] = {'theorems': len(names), 'scored': len(scored),
                        'elicit_1e-5': sum(1 for n in scored if best[n] >= math.log(1e-5)),
                        'elicit_1/256': sum(1 for n in scored if best[n] >= math.log(1 / 256))}
        res['reachability'] = reach
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='artifacts/ladder'); ap.add_argument('--round', type=int, default=8)
    ap.add_argument('--arms', nargs='*', default=None); ap.add_argument('--out', default='ladder.md'); ap.add_argument('--json', default='artifacts/ladder/summary.json')
    ap.add_argument('--pools', default='data/ladder')
    a = ap.parse_args()
    transfer, targets = rd(f'{a.pools}/transfer.jsonl'), rd(f'{a.pools}/rl_targets.jsonl')
    arms = a.arms or sorted(os.path.basename(d) for d in glob.glob(f'{a.dir}/la_*') if os.path.isdir(d))
    summ = {}
    frozen_solved = {}
    for arm in arms:
        d = f'{a.dir}/{arm}'
        ft = f'{d}/found_transfer_{a.round}.jsonl'
        if not os.path.exists(ft):
            continue
        fu = f'{d}/found_union_{a.round}.jsonl'
        fg = fu if os.path.exists(fu) else f'{d}/found_{a.round}.jsonl'
        nov = rd(f'{d}/novelty_proofs.jsonl') if os.path.exists(f'{d}/novelty_proofs.jsonl') else None
        nov_t = [x for x in nov if x['src'] == 'transfer'] if nov else None
        nov_g = [x for x in nov if x['src'] == 'targets'] if nov else None
        rung = arm.split('_')[1]; seed = arm.split('_s')[-1]
        ref = frozen_solved.get(seed)
        res = {'rung': rung, 'seed': seed, 'transfer': analyse_pool(load_found(ft, transfer), transfer, nov_t, ref), 'targets': analyse_pool(load_found(fg, targets), targets, nov_g),
               'union': os.path.exists(fu)}
        rs = [json.load(open(f)) for f in sorted(glob.glob(f'{d}/round_*.json'), key=lambda f: int(f.split('_')[-1][:-5]))]
        res['rounds'] = len(rs); res['secs'] = sum(r['secs'] for r in rs); res['heldout_greedy_final'] = rs[-1]['heldout_greedy']['rate'] if rs else None
        res['transfer_greedy_final'] = rs[-1]['transfer_greedy']['rate'] if rs else None
        res['attempts_per_target'] = rs[-1]['targets_cum'].get('attempts_per_theorem') if rs else None
        res['lstar_by_round'] = [(r['round'], r['transfer_cum']['lstar'], r['targets_cum']['lstar']) for r in rs]
        if rung == 'frozen':
            frozen_solved[seed] = {n for n, v in load_found(ft, transfer).items() if v}
        summ[arm] = res
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    json.dump(summ, open(a.json, 'w'), indent=1)
    # ---- ladder.md
    md = ['# ladder-A leaderboard (Phase A: T1–T6)\n',
          f'Re-derived by `ladder_analysis.py` from `artifacts/ladder/<arm>/found_transfer_{a.round}.jsonl`, `found_{a.round}.jsonl` (`found_union_{a.round}.jsonl` for T6) and `novelty_proofs.jsonl`; pools `data/ladder/` (`POOLS.md`). '
          'Counts are start-index-normalised distinct proofs; solved = ≥ 1 verifier-accepted proof of the prompted sequent in the cumulative attempts (256 per theorem). '
          '`L*` = largest L with ≥ 5 theorems solved at `L_true ≥ L`; `L_true` is `minlen.py`\'s minimal length in its restricted formula space at bound 14 (see POOLS.md caveat). '
          'Base reachability: a solved theorem is "elicitation" if one of its counted proofs has base p(T = 0.8) ≥ 1e-5 under `stage1_abs.pt`, else "creation".\n',
          '| arm | rung | seed | L* transfer | L* targets | L* transfer gen-only | transfer solved | targets solved | transfer thms at L_true ≥ 8 / 9 / 10 / 11 | targets thms ≥ 8 / 9 / 10 / 11 | held-out greedy | pod time |',
          '|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|']
    for arm, r in summ.items():
        t, g = r['transfer'], r['targets']
        md.append(f"| {arm} | {RUNGS.get(r['rung'], r['rung'])} | {r['seed']} | **{t['lstar']}** | {g['lstar']} | {t['lstar_gen_only']} | {t['solved']}/{t['n']} | {g['solved']}/{g['n']} | "
                  f"{t['ge'][8]} / {t['ge'][9]} / {t['ge'][10]} / {t['ge'][11]} | {g['ge'][8]} / {g['ge'][9]} / {g['ge'][10]} / {g['ge'][11]} | {r['heldout_greedy_final']:.3f} | {r['secs']/60:.0f} min |")
    md.append('\n## Transfer solve rate by `L_true` bin (Wilson 95 %)\n')
    md.append('| arm | ' + ' | '.join(f'L_true {L}' for L in BINS) + ' |')
    md.append('|---|' + '---|' * len(BINS))
    for arm, r in summ.items():
        cells = []
        for L in BINS:
            b = r['transfer']['bins'][L]
            cells.append(f"{b['solved']}/{b['n']} ({b['rate']*100:.1f} [{b['ci'][0]*100:.1f},{b['ci'][1]*100:.1f}])" if b['n'] else '–')
        md.append(f'| {arm} | ' + ' | '.join(cells) + ' |')
    md.append('\n## RL-target solve rate by `L_true` bin (Wilson 95 %)\n')
    md.append('| arm | ' + ' | '.join(f'L_true {L}' for L in BINS) + ' |')
    md.append('|---|' + '---|' * len(BINS))
    for arm, r in summ.items():
        cells = []
        for L in BINS:
            b = r['targets']['bins'][L]
            cells.append(f"{b['solved']}/{b['n']} ({b['rate']*100:.1f} [{b['ci'][0]*100:.1f},{b['ci'][1]*100:.1f}])" if b['n'] else '–')
        md.append(f'| {arm} | ' + ' | '.join(cells) + ' |')
    md.append('\n## Base reachability of solved transfer theorems (max base p over counted proofs)\n')
    md.append('| arm | L_true ≥ 7: elicit(1e-5) / elicit(1/256) / scored / solved | ≥ 8 | ≥ 9 | ≥ 10 |')
    md.append('|---|---|---|---|---|')
    for arm, r in summ.items():
        rc = r['transfer'].get('reachability')
        if not rc:
            md.append(f'| {arm} | (novelty not scored) | | | |'); continue
        md.append(f'| {arm} | ' + ' | '.join(f"{rc[L]['elicit_1e-5']} / {rc[L]['elicit_1/256']} / {rc[L]['scored']} / {rc[L]['theorems']}" for L in (7, 8, 9, 10)) + ' |')
    md.append('\n## Transfer theorems solved at `L_true ≥ 9`, by source\n')
    md.append('| arm | generator | schemata |')
    md.append('|---|---:|---|')
    for arm, r in summ.items():
        t = r['transfer']
        md.append(f"| {arm} | {t['gen_ge9']} | {', '.join(f'{k} {v}' for k, v in sorted(t['schemas_ge9'].items()))} |")
    md.append('\n## L* by round (transfer, targets)\n')
    for arm, r in summ.items():
        md.append(f"- {arm}: " + ', '.join(f'r{a_}: {b_}/{c_}' for a_, b_, c_ in r['lstar_by_round']))
    open(a.out, 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md[:12]))


if __name__ == '__main__':
    main()
