#!/usr/bin/env python3
"""Phase 2 (reviewer): style_edl/results.csv, artifacts/style_edl/{verdict,bootstrap,term_sizes}.json against my recount
(out/r3, r4, r5, r6 json) and an all-token EDL recomputed from the per-proof bits_all lists.  -> out/p2_compare.json"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
W = '/home/dan/work/style-edl'
H = os.path.join(C.HERE, 'out')
LOG3 = math.log2(3)
r3 = json.load(open(f'{H}/r3_edl.json'))['cells']; r4 = json.load(open(f'{H}/r4_cap.json'))
r5 = json.load(open(f'{H}/r5_lv.json'))['cells']; r6 = json.load(open(f'{H}/r6_attr.json'))


def all_tok(s, S):
    d = json.load(open(f'{C.WS}/artifacts/style_edl/edl/s{s}/{S}.json'))
    lr = r3[f's{s}/{S}']['lr_star']
    n, nt = d['n_stream'], d['n_test']
    runs = [r for r in d['runs'] if abs(r['lr'] - lr) < 1e-12]
    e = sum(sum(sum(b['block']['bits_all']) for b in r['blocks']) - n * sum(r['theta']['test']['bits_all']) / nt for r in runs) / len(runs) + LOG3
    M = sum(d['base']['stream']['bits_all']) - n * sum(d['base']['test']['bits_all']) / nt
    return e / n, (e - M) / n, sum(d['base']['test']['bits_all']) / nt


def main():
    rows = list(csv.DictReader(open(f'{W}/style_edl/results.csv')))
    diffs = {}
    worst = {}
    for r in rows:
        s, S = int(r['seed']), r['stream']
        c = r3[f's{s}/{S}']; cr = r4['criterion'][f's{s}/{S}']; lv = r5[f's{s}/{S}']; at = r6['attribution'][f's{s}/{S}']
        xf = r3[f's{s}/{S}/xfit']; fx = r3[f's{s}/{S}/fixed']
        ae, aec, at0 = all_tok(s, S)
        mine = {'EDL_pp': c['EDL_per_proof'], 'EDL_pa': c['EDL_per_action'], 'EDL_c_pp': c['EDL_c_per_proof'],
                'EDL_c_pa': c['EDL_c_per_action'], 'M': c['M_per_proof'] * 128, 'start_pp': c['first_block_per_proof'],
                'L_test': c['L_test_per_proof'], 'L0_test': c['learner_test_mean'], 'L0_stream': c['learner_stream_mean'],
                'tf_agree': c['learner_tf_agree_all256'], 'EDL_c_pp_o0': c['EDL_c_per_proof_by_order']['0'],
                'EDL_c_pp_o1': c['EDL_c_per_proof_by_order']['1'], 'x_EDL_pp': xf['EDL_per_proof'],
                'x_EDL_c_pp': xf['EDL_c_per_proof'], 'xfit_EDL_pp': (c['EDL_per_proof'] + xf['EDL_per_proof']) / 2,
                'lv_EDL_pp': lv['EDL_V_per_proof'], 'lv_EDL_c_pp': lv['EDL_V_c_per_proof'],
                'fixed_EDL_pp': fx['EDL_per_proof'], 'fixed_EDL_c_pp': fx['EDL_c_per_proof'],
                'plain_pass32_before': cr['before_pass32'], 'plain_pass1_before': cr['before_pass1'],
                'plain_pass32_after': cr['after_pass32'], 'plain_pass1_after': cr['after_pass1'],
                'logical_pass32_after': cr['guided_after_pass32'], 'logical_pass1_after': cr['guided_after_pass1'],
                'all_EDL_pp': ae, 'all_EDL_c_pp': aec, 'all_L0_test': at0,
                'n_differ_stream': at['differ']['n_stream'], 'n_differ_test': at['differ']['n_test'],
                'same_EDL_c_per_proof': at['same']['EDL_c_class_per_class_proof']}
        if at['differ']['n_stream']:
            mine['differ_EDL_c_per_proof'] = at['differ']['EDL_c_class_per_class_proof']
        for k, v in mine.items():
            if r.get(k) in (None, ''):
                continue
            t = float(r[k])
            dd = abs(t - v) / max(1.0, abs(v))
            diffs.setdefault(k, 0.0)
            if dd > diffs[k]:
                diffs[k] = dd; worst[k] = (s, S, t, v)
    out = {'max_rel_diff_by_column': diffs, 'worst': worst,
           'strat_EDL_c_pp': {f"s{r['seed']}/{r['stream']}": r['strat_EDL_c_pp'] for r in rows if r['strat_EDL_c_pp']},
           'all_token': {f's{s}/{S}': all_tok(s, S) for s in (0, 1, 2) for S in ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')}}
    v = json.load(open(f'{W}/artifacts/style_edl/verdict.json'))
    out['verdict_json'] = v
    json.dump(out, open(f'{H}/p2_compare.json', 'w'), indent=1, default=str)
    for k, x in sorted(diffs.items(), key=lambda kv: -kv[1]):
        print(f'{k:24s} max rel diff {x:.2e}', worst.get(k) if x > 1e-3 else '')
    print('strat', out['strat_EDL_c_pp'])


if __name__ == '__main__':
    main()
