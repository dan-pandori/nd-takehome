#!/usr/bin/env python3
"""R4b (reviewer, phase 1): every distinct accepted literal text of the six S_Kal theta* capability reads (plain on all
256, guided on the 128 test theorems), Lean-checked, because those arms have < 100 test theorems with an accepted
attempt; plus the style of what the Kalmar-trained theta* proves (my parse: lines, boxes, does it use the X v ~X split).
  python3 r4b_kal_lean.py -> out/r4b_kal_lean.json
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'


def main():
    allp = {r['name']: r['prompt'] for r in C.jl(f'{C.WS}/data/style_edl/sets/all256.jsonl')}
    test = {r['name'] for r in C.jl(f'{C.WS}/data/style_edl/sets/test128.jsonl')}
    items, out = [], {}
    for s in (0, 1, 2):
        for arm in ('plain', 'logical'):
            tag = f's{s}_S_Kal/{arm}'
            rows = C.jl(f'{A}/cap/s{s}_S_Kal__{arm}_k32_seed2.rows.jsonl.gz')
            n_test_samples = sum(r['n_ok'] for r in rows if r['name'] in test)
            lines, kal_like, own_like = [], 0, 0
            for r in rows:
                for t, cnt in r['accepted'].items():
                    items.append((tag, r['name'] in test, allp[r['name']], t, cnt))
                    try:
                        L = C.ls_to_nd(allp[r['name']], t)
                        lines.append(len(L))
                        kal_like += any(f == ('or', ('a', 'P'), ('not', ('a', 'P'))) and rule == 'DN' for _, f, rule, _ in L)
                    except C.Bad:
                        pass
            out[tag] = {'accepted_samples_test': n_test_samples, 'distinct_texts_all': sum(len(r['accepted']) for r in rows),
                        'mean_lines_of_accepted': sum(lines) / max(1, len(lines)), 'with_P_or_notP_by_DN': kal_like,
                        'parsed': len(lines)}
    srcs = [C.ls_wrap(pr, t, f'k{i}') for i, (_, _, pr, t, _) in enumerate(items)]
    res = C.lean_check(srcs, tag='kal', chunk=20, workers=1)
    for (tag, is_test, _, _, cnt), (ok, e) in zip(items, res):
        o = out[tag]
        o.setdefault('lean_checked', 0); o.setdefault('lean_accepted', 0); o.setdefault('lean_checked_test', 0)
        o['lean_checked'] += 1; o['lean_accepted'] += ok; o['lean_checked_test'] += is_test
        o.setdefault('samples_covered', 0); o['samples_covered'] += cnt
    out['rejected'] = [(items[i][0], e) for i, (ok, e) in enumerate(res) if not ok][:10]
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r4b_kal_lean.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
