#!/usr/bin/env python3
"""Reviewer recount of compute-matched reach on the 322 (textbook72 + holdout250), standard A, per new seed.
RL solves = r16 plain k 256 x0.  Base = pend x0 + x1 (512 attempts) plus, on theorems r16 solves and the base failed in
those 512, the large-k attempts in stdA_<arm>_s<S>.chunks.jsonl.  Within reach at K: p-hat >= 1 / K.
Reported at K_train(16) with and without the fine-tune child time (out_cert.json), and the created set
C = RL solves that are not within reach; Delta_cov = |RL solves| - |base within reach (over the 322)|."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
EV = f'{RV}/artifacts/coe/eval'
R1054 = list(C.rows(f'{RV}/data/coe/read1054.jsonl'))
R322 = {r['prompt']: r['name'] for r in R1054 if r['set'] in ('tb72', 'h250')}
KK = json.load(open(f'{RV}/review_coe/out_cert.json'))['K']


def solved(tag):
    out = {}
    for r in C.rows(f'{EV}/{tag}.jsonl.gz'):
        if r['prompt'] in R322:
            out[r['prompt']] = (r['n_ok'], r['n_tried'])
    return out


res = {}
for arm, seeds in (('full', range(3, 6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        rl = solved(f'r16_{arm}_s{s}_x0')
        b0 = solved(f'pend_{arm}_s{s}_x0'); b1 = solved(f'pend_{arm}_s{s}_x1')
        base = {p: [b0[p][0] + b1[p][0], b0[p][1] + b1[p][1]] for p in R322}
        nm2p = {R322[p]: p for p in R322}
        fn = f'{RV}/artifacts/coe/large/stdA_{arm}_s{s}.chunks.jsonl'
        big = collections.defaultdict(lambda: [0, 0])
        if os.path.exists(fn):
            for x in C.rows(fn):
                if 'name' in x:
                    big[x['name']][0] += x['ok']; big[x['name']][1] += x['tried']
        names_file = f'{RV}/artifacts/coe/large/stdA_names_{arm}_s{s}.txt'
        listed = [l.strip() for l in open(names_file) if l.strip()] if os.path.exists(names_file) else []
        rl_solves = {p for p in R322 if rl[p][0] > 0}
        need = {p for p in rl_solves if base[p][0] == 0}
        tot = {p: [base[p][0] + big[R322[p]][0], base[p][1] + big[R322[p]][1]] for p in R322}
        o = {'rl_solves': len(rl_solves), 'base512_solves': sum(1 for p in R322 if base[p][0] > 0), 'need_bigk': len(need),
             'listed': len(listed), 'listed_eq_need': set(listed) == {R322[p] for p in need},
             'bigk_min_n_on_need': min((tot[p][1] for p in need), default=None)}
        for kn in ('', '_ladder_rows_only'):
            K = KK[f'{arm}_{s}{kn}']
            within = {p for p in R322 if tot[p][1] and tot[p][0] / tot[p][1] >= 1 / K}
            created = rl_solves - within
            not_reached = {p for p in created if tot[p][0] == 0}
            undersampled = {p for p in not_reached if tot[p][1] < K}
            below = {p for p in created if tot[p][0] > 0}
            o[f'K{kn}'] = K
            o[f'within{kn}'] = len(within); o[f'created{kn}'] = len(created); o[f'delta_cov{kn}'] = len(rl_solves) - len(within)
            o[f'not_reached{kn}'] = len(not_reached); o[f'found_below{kn}'] = len(below); o[f'undersampled{kn}'] = len(undersampled)
            o[f'created_names{kn}'] = sorted(R322[p] for p in created)
        res[f'{arm}_s{s}'] = o
        print(f'{arm}_s{s}: RL solves {o["rl_solves"]}, base(512) {o["base512_solves"]}, need large-k {o["need_bigk"]} (listed {o["listed"]}, '
              f'same set {o["listed_eq_need"]}, min n {o["bigk_min_n_on_need"]}); '
              f'K {o["K"]:,.0f}: within {o["within"]}, created {o["created"]} (not reached {o["not_reached"]}, found below {o["found_below"]}, '
              f'n<K {o["undersampled"]}), Delta_cov {o["delta_cov"]};  K(ladder rows only) {o["K_ladder_rows_only"]:,.0f}: created '
              f'{o["created_ladder_rows_only"]}, Delta_cov {o["delta_cov_ladder_rows_only"]}, n<K {o["undersampled_ladder_rows_only"]}')
json.dump(res, open(f'{RV}/review_coe/out_stdA.json', 'w'), indent=1)
