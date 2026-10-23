#!/usr/bin/env python3
"""R6 (reviewer, phase 1): addendum-1 per-proof attribution (same / differ vs the learner's greedy proof), style
distance and its rank correlation with EDL_c, per-seed values with IQM and a bootstrap 95 % interval, and the
per-proof drivers of the largest cells.  From the edl json per-proof lists only (no summaries).
  python3 r6_attr.py -> out/r6_attr.json
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')
LOG3 = math.log2(3)


def spearman(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk(x), rk(y)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))
    return num / den


def iqm(v):
    v = sorted(v)
    n = len(v)
    k = int(math.floor(0.25 * n))
    w = v[k:n - k] if n - 2 * k > 0 else v
    return sum(w) / len(w)


def boot(v, B=10000, seed=0):
    rng = random.Random(seed)
    m = sorted(iqm([rng.choice(v) for _ in v]) for _ in range(B))
    return m[int(0.025 * B)], m[int(0.975 * B) - 1]


def main():
    r3 = json.load(open(os.path.join(C.HERE, 'out', 'r3_edl.json')))['cells']
    tf = {r['name']: r for r in C.jl(f'{C.WS}/data/kalmar/tf1200_kal_sl.jsonl')}
    own = {}
    for s in SEEDS:
        own[s] = {}
        for part in ('stream', 'test'):
            for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/S_own.{part}.jsonl'):
                own[s][r['name']] = C.parse_nd(r['nd'])
    attr = {}
    drivers = {}
    for s in SEEDS:
        for S in STREAMS:
            d = json.load(open(f'{A}/edl/s{s}/{S}.json'))
            lr = r3[f's{s}/{S}']['lr_star']
            sn, tn = d['stream_names'], d['test_names']
            recs = {}
            for part in ('stream', 'test'):
                for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl'):
                    recs[r['name']] = C.parse_nd(r['nd'])
            same_s = [recs[n] == own[s][n] for n in sn]
            same_t = [recs[n] == own[s][n] for n in tn]
            b0s, b0t = d['base']['stream']['bits'], d['base']['test']['bits']
            runs = [r for r in d['runs'] if abs(r['lr'] - lr) < 1e-12]
            res = {}
            for cls, want in (('same', True), ('differ', False)):
                ii = [i for i, v in enumerate(same_s) if v == want]
                jj = [j for j, v in enumerate(same_t) if v == want]
                sav, thb = [], []
                for r in runs:
                    perm = r['perm']
                    pb = [None] * len(sn)
                    for b in r['blocks']:
                        for k, x in zip(range(b['lo'], b['hi']), b['block']['bits']):
                            pb[perm[k]] = x
                    sav.append(sum(b0s[i] - pb[i] for i in ii))
                    thb.append(sum(r['theta']['test']['bits'][j] for j in jj) / len(jj) if jj else float('nan'))
                savm = sum(sav) / len(sav)
                thm = sum(thb) / len(thb)
                L0t = sum(b0t[j] for j in jj) / len(jj) if jj else float('nan')
                L0s = sum(b0s[i] for i in ii) / len(ii) if ii else float('nan')
                e = len(ii) * (L0t - thm) - savm if jj and ii else float('nan')
                res[cls] = {'n_stream': len(ii), 'n_test': len(jj), 'learner_stream_mean': L0s, 'learner_test_mean': L0t,
                            'theta_test_mean': thm, 'online_savings_total': savm,
                            'EDL_c_class_total': e, 'EDL_c_class_per_class_proof': e / len(ii) if ii else float('nan')}
            attr[f's{s}/{S}'] = res
            # per-proof drivers of L_test: theta* minus learner on each test proof (mean over orders)
            dl = []
            for j, nm in enumerate(tn):
                dt = sum(r['theta']['test']['bits'][j] for r in runs) / len(runs) - b0t[j]
                dl.append((dt, nm, same_t[j], b0t[j]))
            dl.sort()
            drivers[f's{s}/{S}'] = {'test_worst5': [(round(a, 3), b, c, round(e, 3)) for a, b, c, e in dl[-5:]],
                                    'test_best5': [(round(a, 3), b, c, round(e, 3)) for a, b, c, e in dl[:5]],
                                    'sum_theta_minus_learner_test': sum(x[0] for x in dl)}
    # style distance and rho
    dist_all = {S: sum(1 - r3[f's{s}/{S}']['learner_tf_agree_all256'] for s in SEEDS) / 3 for S in STREAMS}
    dist_st = {S: sum(1 - r3[f's{s}/{S}']['learner_tf_agree_stream'] for s in SEEDS) / 3 for S in STREAMS}
    edlc = {S: sum(r3[f's{s}/{S}']['EDL_c_per_proof'] for s in SEEDS) / 3 for S in STREAMS}
    edl = {S: sum(r3[f's{s}/{S}']['EDL_per_proof'] for s in SEEDS) / 3 for S in STREAMS}
    rho = {'rho_dist_all256_vs_EDL_c': spearman([dist_all[S] for S in STREAMS], [edlc[S] for S in STREAMS]),
           'rho_dist_stream_vs_EDL_c': spearman([dist_st[S] for S in STREAMS], [edlc[S] for S in STREAMS]),
           'rho_dist_all256_vs_EDL': spearman([dist_all[S] for S in STREAMS], [edl[S] for S in STREAMS])}
    per_seed = {}
    for S in STREAMS:
        for q in ('EDL_per_proof', 'EDL_c_per_proof', 'EDL_per_action', 'EDL_c_per_action', 'first_block_per_proof',
                  'L_test_per_proof', 'learner_all256_mean'):
            v = [r3[f's{s}/{S}'][q] for s in SEEDS]
            lo, hi = boot(v)
            per_seed.setdefault(S, {})[q] = {'per_seed': v, 'mean': sum(v) / 3, 'iqm': iqm(v), 'ci95': [lo, hi]}
    out = {'attribution': attr, 'drivers': drivers, 'style_distance_all256': dist_all, 'style_distance_stream': dist_st,
           'EDL_c_seed_mean': edlc, 'EDL_seed_mean': edl, 'rho': rho, 'per_seed': per_seed}
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r6_attr.json'), 'w'), indent=1)
    for k, v in attr.items():
        print(k, {c: {a: (round(b, 3) if isinstance(b, float) else b) for a, b in x.items()} for c, x in v.items()})
    print(json.dumps(rho), json.dumps({S: round(v, 4) for S, v in dist_all.items()}))
    for k in ('s2/S_RL', 's0/S_short', 's1/S_short', 's2/S_short'):
        print(k, drivers[k])


if __name__ == '__main__':
    main()
