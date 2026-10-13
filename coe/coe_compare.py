#!/usr/bin/env python3
"""create-or-elicit: the pre-registered arm comparison (preregistration Phase 1 decision rule, Addendum 2 strict sets).

Per seed and checkpoint (pend / r8 / r16), from plain k 256 reads (x0 = sample seed 0): solved strict sigma-covered held-out
members per classical family (106 = families' strict_heldout + 1 generated), families acquired (>= 50 % of a family's strict
held-out members solved), the primary indicator (>= 1 family acquired), and proof classes of the accepted proofs.
New seeds: one read of data/coe/read1054.jsonl (tag <ck>_<arm>_s<S>_<x>); old full seeds s0-s2: two reads merged, the 732
tracked transfer theorems outside holdout250 (<ck>_full_s<S>_<x>e) and the 100 inside it (<ck>_full_s<S>_<x>h).
Tests (one-sided, full > knockout): primary indicator, Boschloo exact (alpha 0.05); per family, Boschloo with Holm over the 6
families; strict held-out members solved at r16, exact Mann-Whitney.

  python3 coe/coe_compare.py --ck r16 --x x0 --out artifacts/coe/compare_r16.json
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_reads import load_rows
from coe.coe_rounds import classify as classify_nd
from lean_tok import inverse

FULL_OLD = (0, 1, 2)
FULL_NEW = (3, 4, 5)
KO = (0, 1, 2, 3, 4, 5)


def solved_map(tags, d):
    out, cls = {}, collections.defaultdict(collections.Counter)
    kinds = set()
    for t in tags:
        rows, kind = load_rows(os.path.join(d, t))
        if rows is None:
            return None, None, None
        kinds.add(kind)
        for r in rows:
            if kind == 'plain':
                s = bool(r['solved']); proofs = r['proofs'] if s else []
                pc = [classify_nd(p) for p in proofs]
            else:
                s = r['n_ok'] > 0; pc = []
                for txt in (r['accepted'] if s else {}):
                    try:
                        pc.append(classify_nd(inverse(txt.split())))
                    except Exception:
                        pc.append('lean_text_unparsed')
            out[r['name']] = s
            for c in pc:
                cls[r['name']][c] += 1
    return out, cls, kinds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ck', default='r16')
    ap.add_argument('--x', default='x0')
    ap.add_argument('--dir', default='artifacts/coe/eval')
    ap.add_argument('--families', default='data/coe/families.json')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    fam = json.load(open(a.families))
    fams = {f: d['strict_heldout'] for f, d in fam['families'].items() if d['classical']}
    gen = fam['generated_classical']['transfer']['strict']
    allm = set(n for v in fams.values() for n in v) | set(gen)
    seeds = [('full', s, [f'{a.ck}_full_s{s}_{a.x}e', f'{a.ck}_full_s{s}_{a.x}h']) for s in FULL_OLD] + \
            [('full', s, [f'{a.ck}_full_s{s}_{a.x}']) for s in FULL_NEW] + [('ko', s, [f'{a.ck}_ko_s{s}_{a.x}']) for s in KO] + \
            [('dose1', s, [f'{a.ck}_dose1_s{s}_{a.x}']) for s in (0, 1, 2)]       # Phase 3 (Addendum 5): described, not tested
    res = {}
    for arm, s, tags in seeds:
        sol, cls, kinds = solved_map(tags, a.dir)
        if sol is None:
            print(f'{arm} s{s}: missing {tags}'); continue
        per = {f: sum(sol.get(n, False) for n in m) for f, m in fams.items()}
        npresent = {f: sum(n in sol for n in m) for f, m in fams.items()}
        acq = sorted(f for f in fams if npresent[f] == len(fams[f]) and per[f] / len(fams[f]) >= 0.5)
        tot = sum(per.values()) + sum(sol.get(n, False) for n in gen)
        pcs = collections.Counter()
        for n in allm:
            pcs.update(cls.get(n, {}))
        res[f'{arm}_s{s}'] = {'arm': arm, 'seed': s, 'tags': tags, 'kinds': sorted(kinds), 'per_family': per,
                              'n_family': {f: len(m) for f, m in fams.items()}, 'present': npresent,
                              'acquired': acq, 'primary': bool(acq), 'strict_heldout_solved': tot, 'proof_classes': dict(pcs)}
    # tests
    from scipy.stats import boschloo_exact, mannwhitneyu
    def bos(a1, n1, a2, n2):
        if a1 == 0 and a2 == 0:
            return 1.0                     # no acquisition in either arm: untestable, p = 1 (keeps Holm well defined)
        p = float(boschloo_exact([[a1, n1 - a1], [a2, n2 - a2]], alternative='greater').pvalue)
        return 1.0 if p != p else p
    F = [v for v in res.values() if v['arm'] == 'full']; K = [v for v in res.values() if v['arm'] == 'ko']
    tests = {}
    if F and K:
        tests['primary'] = {'full': f"{sum(v['primary'] for v in F)}/{len(F)}", 'ko': f"{sum(v['primary'] for v in K)}/{len(K)}",
                            'p_boschloo': bos(sum(v['primary'] for v in F), len(F), sum(v['primary'] for v in K), len(K))}
        ps = {}
        for f in fams:
            af = sum(f in v['acquired'] for v in F); ak = sum(f in v['acquired'] for v in K)
            ps[f] = (af, ak, bos(af, len(F), ak, len(K)))
        order = sorted(ps, key=lambda f: ps[f][2])
        holm, run = {}, 0.0
        for i, f in enumerate(order):
            run = max(run, min(1.0, (len(order) - i) * ps[f][2]))
            holm[f] = {'full': ps[f][0], 'ko': ps[f][1], 'p': ps[f][2], 'p_holm': run}
        tests['per_family'] = holm
        xf = [v['strict_heldout_solved'] for v in F]; xk = [v['strict_heldout_solved'] for v in K]
        tests['mann_whitney'] = {'full': xf, 'ko': xk, 'p': float(mannwhitneyu(xf, xk, alternative='greater', method='exact').pvalue)}
    out = {'ck': a.ck, 'x': a.x, 'seeds': res, 'tests': tests}
    json.dump(out, open(a.out, 'w'), indent=1)
    print('| seed | ' + ' | '.join(f[:14] for f in fams) + ' | strict held-out solved (of 106) | acquired | σ / σ⁺ / lemma / DN-PR-AS / no DN |')
    for k, v in res.items():
        pc = v['proof_classes']
        print(f"| {k} | " + ' | '.join(f"{v['per_family'][f]}/{v['n_family'][f]}" for f in fams) +
              f" | {v['strict_heldout_solved']} | {', '.join(v['acquired']) or '–'} | {pc.get('sigma', 0)} / {pc.get('sigma_plus_only', 0)} / {pc.get('lemma_route', 0)} / {pc.get('dn_pr_as', 0)} / {pc.get('no_dn', 0)} |")
    print(json.dumps(tests, indent=1))


if __name__ == '__main__':
    main()
