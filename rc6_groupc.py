#!/usr/bin/env python3
"""rl-continue-cap6: which group-C theorems the r16 checkpoints solve (sample seed 1), the shortest accepted proof of each
in lines and in elaborated Lean term size (nd2lean.translate + lean_check.check, as se_analysis.term_sizes), overlap across
seeds, and one example in Lean.  Model: trajectory-cap6's best-cap6 T1 ladders at r16 (9,560,832 params, lean_staten,
cap-6 set), Lean alone.  VPS-runnable (Lean 4.34.1, no torch).

  python3 rc6_groupc.py > artifacts/rc6/groupc_stdout.txt      (writes artifacts/rc6/groupc.json)
"""
import collections, json
import nd2lean
from lean_check import check
from rc6_analysis import groups, read, rj

E = 'artifacts/rc6'


def rows(s, ck, x):
    out = {}
    for pool in ('tb72', 'h250'):
        p = f'{E}/tj6_eval/s{s}_{ck}__{pool}_x{x}.jsonl' if ck == 'r8' else f'{E}/eval/s{s}_{ck}__{pool}_x{x}.jsonl'
        try:
            out.update({r['name']: dict(r, pool=pool) for r in rj(p)})
        except FileNotFoundError:
            out.update({r['name']: dict(r, pool=pool) for r in rj(f'{E}/eval/s{s}_{ck}__h250C_x{x}.jsonl')})
    return out


def main():
    res, per = {}, collections.defaultdict(dict)
    srcs, keys = [], []
    for s in (0, 1, 2):
        g = groups(s); C = [n for n in g if g[n] == 'C']
        r8, r16 = rows(s, 'r8', 1), rows(s, 'r16', 1)
        for n in C:
            a, b = r8[n], r16[n]
            per[s][n] = {'pool': b['pool'], 'ref_lines': b.get('reference_lines') or b.get('n_lines'),
                         'r8_n_ok': a['n_ok'], 'r16_n_ok': b['n_ok']}
            if b['n_ok'] > 0:
                i = min(range(len(b['proofs'])), key=lambda j: b['written_lens'][j])
                per[s][n]['lines'] = b['written_lens'][i]
                try:
                    srcs.append(nd2lean.translate(b['prompt'], b['proofs'][i], require_all_pr=False)); keys.append((s, n))
                except Exception as e:
                    per[s][n]['translate_error'] = str(e)[:80]
    chk, wall, proc = check(srcs, workers=2)
    for (s, n), r, src in zip(keys, chk, srcs):
        per[s][n].update(lean_ok=r['ok'], term_size=r['size'], lean=src)
    print('## Group C (trajectory-cap6 per-seed C) solved at r16, sample seed 1: shortest accepted proof per theorem\n')
    print('| seed | theorem | pool | ref lines | r8 n_ok/256 | r16 n_ok/256 | lines | term size | lean_check |')
    print('|---|---|---|---|---|---|---|---|---|')
    solved = {}
    for s in (0, 1, 2):
        solved[s] = {n for n in per[s] if per[s][n]['r16_n_ok'] > 0}
        for n in sorted(solved[s], key=lambda n: -per[s][n]['r16_n_ok']):
            v = per[s][n]
            print(f"| s{s} | {n[:28]} | {v['pool']} | {v['ref_lines']} | {v['r8_n_ok']} | {v['r16_n_ok']} | {v.get('lines')} | "
                  f"{v.get('term_size')} | {v.get('lean_ok')} |")
    allC = set.intersection(*[set(per[s]) for s in per])
    print(f"\nC theorems common to all three seeds: {len(allC)}; solved at r16 by >= 1 seed: "
          f"{len(set.union(*solved.values()))} distinct; by all three: {len(set.intersection(*solved.values()))}")
    print('solved at r8 (x1) and at r16 (x1), per seed: ' + ', '.join(
        f"s{s} {sum(1 for n in per[s] if per[s][n]['r8_n_ok'] > 0)} -> {len(solved[s])} "
        f"(both {sum(1 for n in solved[s] if per[s][n]['r8_n_ok'] > 0)})" for s in per))
    print('summed n_ok over C (r8 -> r16): ' + ', '.join(
        f"s{s} {sum(v['r8_n_ok'] for v in per[s].values())} -> {sum(v['r16_n_ok'] for v in per[s].values())}" for s in per))
    ex = max(((s, n) for s in per for n in solved[s] if per[s][n].get('lean_ok')), key=lambda k: (per[k[0]][k[1]]['r8_n_ok'] == 0, per[k[0]][k[1]]['ref_lines'] or 0, per[k[0]][k[1]]['r16_n_ok']))
    print(f"\nExample (s{ex[0]}, {ex[1]}, ref {per[ex[0]][ex[1]]['ref_lines']} lines; r8 {per[ex[0]][ex[1]]['r8_n_ok']}/256, "
          f"r16 {per[ex[0]][ex[1]]['r16_n_ok']}/256):\n```lean\n{per[ex[0]][ex[1]]['lean']}\n```")
    json.dump({str(s): per[s] for s in per}, open(f'{E}/groupc.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
