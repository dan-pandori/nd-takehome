#!/usr/bin/env python3
"""Phase 2 (reviewer): an additive same / differ decomposition of the cross-fit EDL_c (both directions), and the
class-stratified EDL_c (A1's reweighting, results.csv's strat_EDL_c_pp) recomputed.  Additive: in each direction,
EDL_c = sum_c [n_c,test x (L0_c,test - Ltheta_c,test) - savings_c] + log2 3 exactly.  -> out/p2_decomp.json"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
A = f'{C.WS}/artifacts/style_edl'
L3 = math.log2(3)
r3 = json.load(open(os.path.join(C.HERE, 'out', 'r3_edl.json')))['cells']


def direction(fn, lr, own, recs):
    d = json.load(open(fn))
    sn, tn = d['stream_names'], d['test_names']
    b0s, b0t = d['base']['stream']['bits'], d['base']['test']['bits']
    runs = [r for r in d['runs'] if abs(r['lr'] - lr) < 1e-12]
    add, strat = {'same': 0.0, 'differ': 0.0}, {'same': 0.0, 'differ': 0.0}
    for r in runs:
        pb = [None] * len(sn)
        for b in r['blocks']:
            for k, x in zip(range(b['lo'], b['hi']), b['block']['bits']):
                pb[r['perm'][k]] = x
        for cls in ('same', 'differ'):
            want = cls == 'same'
            ii = [i for i, n in enumerate(sn) if (recs[n] == own[n]) == want]
            jj = [j for j, n in enumerate(tn) if (recs[n] == own[n]) == want]
            sav = sum(b0s[i] - pb[i] for i in ii)
            gain = sum(b0t[j] - r['theta']['test']['bits'][j] for j in jj)
            add[cls] += (gain - sav) / len(runs)
            strat[cls] += ((len(ii) * gain / len(jj) if jj else 0.0) - sav) / len(runs)
    return add, strat


out = {}
for s in (0, 1, 2):
    for S in ('S_own2', 'S_seed', 'S_short', 'S_RL'):
        own, recs = {}, {}
        for part in ('stream', 'test'):
            for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/S_own.{part}.jsonl'):
                own[r['name']] = C.parse_nd(r['nd'])
            for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl'):
                recs[r['name']] = C.parse_nd(r['nd'])
        pa, ps = direction(f'{A}/edl/s{s}/{S}.json', r3[f's{s}/{S}']['lr_star'], own, recs)
        xa, xs = direction(f'{A}/edl_x/s{s}/{S}.json', r3[f's{s}/{S}/xfit']['lr_star'], own, recs)
        out[f's{s}/{S}'] = {
            'primary_EDL_c_check': (pa['same'] + pa['differ'] + L3) / 128 - r3[f's{s}/{S}']['EDL_c_per_proof'],
            'xfit_mean_same_part': (pa['same'] + xa['same']) / 256, 'xfit_mean_differ_part': (pa['differ'] + xa['differ']) / 256,
            'xfit_mean_EDL_c': (pa['same'] + pa['differ'] + xa['same'] + xa['differ'] + 2 * L3) / 256,
            'strat_EDL_c_primary': (ps['same'] + ps['differ'] + L3) / 128}
for s in (0, 1, 2):
    for S in ('S_short', 'S_RL', 'S_seed'):
        a, b = out[f's{s}/{S}'], out[f's{s}/S_own2']
        out[f's{s}/{S}']['excess_over_own2'] = {
            'xfit': a['xfit_mean_EDL_c'] - b['xfit_mean_EDL_c'],
            'xfit_same_part': a['xfit_mean_same_part'] - b['xfit_mean_same_part'],
            'xfit_differ_part': a['xfit_mean_differ_part'] - b['xfit_mean_differ_part'],
            'strat': a['strat_EDL_c_primary'] - b['strat_EDL_c_primary']}
json.dump(out, open(os.path.join(C.HERE, 'out', 'p2_decomp.json'), 'w'), indent=1)
for k, v in out.items():
    print(k, 'check', f"{v['primary_EDL_c_check']:.1e}", 'strat', round(v['strat_EDL_c_primary'], 4),
          {a: round(b, 3) for a, b in v.get('excess_over_own2', {}).items()})
