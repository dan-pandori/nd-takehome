#!/usr/bin/env python3
"""Phase 2 (reviewer): the exploratory pooled cross-fit attribution (EDL_c of the differing / same proofs, summed over
the primary and the swapped direction, divided by all differing / same proofs of the 256) from the per-proof lists."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
A = f'{C.WS}/artifacts/style_edl'
r3 = json.load(open(os.path.join(C.HERE, 'out', 'r3_edl.json')))['cells']


def cls_edl(fn, lr, own, recs):
    d = json.load(open(fn))
    sn, tn = d['stream_names'], d['test_names']
    same_s = [recs[n] == own[n] for n in sn]; same_t = [recs[n] == own[n] for n in tn]
    b0s, b0t = d['base']['stream']['bits'], d['base']['test']['bits']
    runs = [r for r in d['runs'] if abs(r['lr'] - lr) < 1e-12]
    out = {}
    for cls, want in (('same', True), ('differ', False)):
        ii = [i for i, v in enumerate(same_s) if v == want]; jj = [j for j, v in enumerate(same_t) if v == want]
        tot = 0.0
        for r in runs:
            pb = [None] * len(sn)
            for b in r['blocks']:
                for k, x in zip(range(b['lo'], b['hi']), b['block']['bits']):
                    pb[r['perm'][k]] = x
            sav = sum(b0s[i] - pb[i] for i in ii)
            th = sum(r['theta']['test']['bits'][j] for j in jj) / len(jj) if jj else 0.0
            L0t = sum(b0t[j] for j in jj) / len(jj) if jj else 0.0
            tot += len(ii) * (L0t - th) - sav
        out[cls] = (tot / len(runs), len(ii), len(jj))
    return out


res = {}
for S in ('S_own2', 'S_seed', 'S_short', 'S_RL'):
    for s in (0, 1, 2):
        own = {}; recs = {}
        for part in ('stream', 'test'):
            for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/S_own.{part}.jsonl'):
                own[r['name']] = C.parse_nd(r['nd'])
            for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl'):
                recs[r['name']] = C.parse_nd(r['nd'])
        p = cls_edl(f'{A}/edl/s{s}/{S}.json', r3[f's{s}/{S}']['lr_star'], own, recs)
        x = cls_edl(f'{A}/edl_x/s{s}/{S}.json', r3[f's{s}/{S}/xfit']['lr_star'], own, recs)
        nd = p['differ'][1] + p['differ'][2]
        ns = p['same'][1] + p['same'][2]
        res[f's{s}/{S}'] = {'pooled_differ_per_proof': (p['differ'][0] + x['differ'][0]) / nd if nd else None,
                            'pooled_same_per_proof': (p['same'][0] + x['same'][0]) / ns, 'n_differ': nd,
                            'xfit_lr': r3[f's{s}/{S}/xfit']['lr_star']}
    print(S, [(round(res[f's{s}/{S}']['pooled_differ_per_proof'], 2), round(res[f's{s}/{S}']['pooled_same_per_proof'], 3), res[f's{s}/{S}']['n_differ']) for s in (0, 1, 2)])
json.dump(res, open(os.path.join(C.HERE, 'out', 'p2_xfit_attr.json'), 'w'), indent=1)
