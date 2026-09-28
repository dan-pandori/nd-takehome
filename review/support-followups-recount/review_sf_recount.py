#!/usr/bin/env python3
"""Reviewer's blind recount of support-followups stages A, B, C (raw records only)."""
import json, glob, collections, os, re, math
SF = 'artifacts/sf'; SC = 'artifacts/sc'
def rows(pat):
    out = []
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            if l.strip():
                r = json.loads(l); r['_f'] = os.path.basename(f); out.append(r)
    return out
lines = lambda p: [l.strip() for l in open(p) if l.strip()]
SURV = set(lines('data/sc/falsifier_survivors.txt')); CRUX = set(lines('data/sc/crux_forward.txt'))
THM = {json.loads(l)['name']: json.loads(l) for l in open('data/sc/theorems.jsonl')}
R = {}
def solved(rs):
    d = collections.defaultdict(int); t = collections.defaultdict(int)
    for r in rs:
        # consistency: n_ok>0 iff proofs nonempty
        assert (r['n_ok'] > 0) == bool(r['proofs']), (r['_f'], r['name'])
        d[r['name']] += r['n_ok']; t[r['name']] += r['n_tried']
    return d, t
def settings(rs):
    return dict(collections.Counter((r['_f'][:30], r.get('batch'), r.get('max_new'), r.get('temperature'), r.get('k_requested'), r.get('stop_at'), r.get('ckpt_md5','')[:8], r.get('sampling_seed')) for r in rs))

# ---------------- A ----------------
aB = rows(f'{SF}/a_base_T08_s1.s*.jsonl'); aE = rows(f'{SF}/a_ei_T08_s1rerun.s*.jsonl')
oB = rows(f'{SC}/s3_base_T08_s1.s*.jsonl'); oE = rows(f'{SC}/s3_ei_T08_s1.s*.jsonl'); e0 = rows(f'{SC}/s1_ei_T08_s0.s*.jsonl')
b0 = rows(f'{SC}/s1_base_T08_s0.s*.jsonl')
for nm, rs in [('aB', aB), ('aE', aE)]:
    c = collections.Counter(r['name'] for r in rs)
    assert len(c) == 383 and max(c.values()) == 1 and set(c) == set(THM), nm
S = {k: {n for n, v in solved(rs)[0].items() if v > 0} for k, rs in dict(aB=aB, aE=aE, oB=oB, oE=oE, e0=e0, b0=b0).items()}
ALL = set(THM)
def agree(a, b): return sum(1 for n in ALL if (n in a) == (n in b))
A = {'base_s1_redraw': len(S['aB']), 'ei_s1rerun': len(S['aE']), 'lost_ei_s1': len(S['oE']), 'base_s1_old': len(S['oB']),
     'ei_s0': len(S['e0']), 'base_s0': len(S['b0']),
     'crux_fwd_new': len(S['aE'] - S['aB']), 'crux_fwd_old': len(S['oE'] - S['oB']),
     'crux_rev_new': len(S['aB'] - S['aE']),
     'surv_ei_s1rerun': len(SURV & S['aE']), 'surv_base_s1_redraw': len(SURV & S['aB']),
     'surv_lost_ei_s1': len(SURV & S['oE']), 'surv_base_s1_old': len(SURV & S['oB']),
     'surv_base_s1_redraw_names': sorted(SURV & S['aB']), 'surv_missed_by_rerun': sorted(SURV - S['aE']),
     'agree_rerun_vs_lost': agree(S['aE'], S['oE']), 'agree_rerun_vs_ei_s0': agree(S['aE'], S['e0']),
     'agree_baseredraw_vs_old': agree(S['aB'], S['oB']),
     'rerun_only_vs_lost': len(S['aE'] - S['oE']), 'lost_only_vs_rerun': len(S['oE'] - S['aE']),
     'base_redraw_only': len(S['aB'] - S['oB']), 'base_old_only': len(S['oB'] - S['aB']),
     'crux_new_overlap_crux_old': len((S['aE'] - S['aB']) & (S['oE'] - S['oB'])),
     'crux_new_overlap_sc_crux_s0': len((S['aE'] - S['aB']) & CRUX),
     'n_no_eos_aB': sum(r['n_no_eos'] for r in aB), 'n_no_eos_aE': sum(r['n_no_eos'] for r in aE),
     'tried_aB': sum(r['n_tried'] for r in aB), 'tried_aE': sum(r['n_tried'] for r in aE),
     'peak_mem': sorted({r['peak_mem_gb'] for r in aB + aE})[-1:],
     'settings': {**settings(aB), **settings(aE)}}
# forward crux (new) that are among the 29 survivors under seed-1 definition: base s1 0 & ei >0
R['A'] = {k: (v if not isinstance(v, dict) else {str(kk): vv for kk, vv in v.items()}) for k, v in A.items()}

# ---------------- B ----------------
bb = rows(f'{SF}/b_*.jsonl')
R['B'] = {'rows': [{k: r[k] for k in ('name', 'L_true', 'n_tried', 'n_ok', 'n_distinct_ok', 'n_no_eos', 'n_parse_fail', 'sampling_seed', 'temperature', 'batch', 'max_new', 'peak_mem_gb')} for r in bb],
          'total_ok': sum(r['n_ok'] for r in bb), 'total_tried': sum(r['n_tried'] for r in bb),
          'no_eos_frac': sum(r['n_no_eos'] for r in bb) / sum(r['n_tried'] for r in bb),
          'p95_upper_each(3/n)': {r['name']: 3 / r['n_tried'] for r in bb},
          'exact_95_upper_each': {r['name']: 1 - 0.05 ** (1 / r['n_tried']) for r in bb}}
# prior base s0 attempts on the six from sc
prior = collections.defaultdict(lambda: collections.Counter())
for r in rows(f'{SC}/s*_base_*_s0.s*.jsonl'):
    if r['name'] in {x['name'] for x in bb}:
        prior[r['name']][str(r['temperature'])] += r['n_tried']
R['B']['prior_sc_base_s0_attempts'] = {k: dict(v) for k, v in prior.items()}

# ---------------- C ----------------
C = {}
for seed in (0, 1):
    c1 = rows(f'{SF}/c1_big_T08_s{seed}.s*.jsonl')
    cnt = collections.Counter(r['name'] for r in c1)
    c2_08 = rows(f'{SF}/c2_big_T08_s{seed}_*.jsonl'); c2_10 = rows(f'{SF}/c2_big_T10_s{seed}_*.jsonl')
    s1, t1 = solved(c1); s08, t08 = solved(c2_08); s10, t10 = solved(c2_10)
    solved1 = {n for n, v in s1.items() if v > 0}
    # duplicate (name, sampling_seed) pairs would mean replayed streams
    dup = collections.Counter((r['name'], r['temperature'], r.get('sampling_seed')) for r in c1 + c2_08 + c2_10)
    per_surv = {}
    for n in sorted(SURV):
        per_surv[n] = {'c1_tried': t1.get(n, 0), 'c1_ok': s1.get(n, 0), 'T08_tried_total': t1.get(n, 0) + t08.get(n, 0),
                       'T08_ok': s1.get(n, 0) + s08.get(n, 0), 'T10_tried': t10.get(n, 0), 'T10_ok': s10.get(n, 0)}
    surv_solved = sorted(n for n, d in per_surv.items() if d['T08_ok'] + d['T10_ok'] > 0)
    C[f's{seed}'] = {'c1_rows': len(c1), 'c1_theorems': len(cnt), 'c1_dups': sum(1 for v in cnt.values() if v > 1),
                     'c1_set_eq_crux82': set(cnt) == CRUX, 'c1_tried_values': dict(collections.Counter(t1.values())),
                     'crux_solved_k1e4': len(solved1), 'crux_solved_names': sorted(solved1),
                     'surv_solved_in_c1': sorted(solved1 & SURV),
                     'c2_T08_theorems': len(t08), 'c2_T10_theorems': len(t10),
                     'c2_T08_ok_total': sum(s08.values()), 'c2_T10_ok_total': sum(s10.values()),
                     'survivors_solved_any': surv_solved, 'n_survivors_solved': len(surv_solved),
                     'survivors_T08_total_tried_hist': dict(collections.Counter(d['T08_tried_total'] for d in per_surv.values())),
                     'survivors_T10_tried_hist': dict(collections.Counter(d['T10_tried'] for d in per_surv.values())),
                     'stream_dups': [k for k, v in dup.items() if v > 1][:10], 'n_stream_dups': sum(1 for v in dup.values() if v > 1),
                     'no_eos_total': sum(r['n_no_eos'] for r in c1 + c2_08 + c2_10), 'tried_total': sum(r['n_tried'] for r in c1 + c2_08 + c2_10),
                     'ckpt_md5': sorted({r['ckpt_md5'] for r in c1 + c2_08 + c2_10}),
                     'settings': {str(k): v for k, v in {**settings(c1), **settings(c2_08), **settings(c2_10)}.items()},
                     'per_survivor': per_surv}
    # crux names solved in c1 by L_true
    C[f's{seed}']['crux_solved_by_L'] = dict(collections.Counter(THM[n]['L_true'] for n in solved1))
C['union_crux_solved'] = len(set(C['s0']['crux_solved_names']) | set(C['s1']['crux_solved_names']))
C['intersect_crux_solved'] = len(set(C['s0']['crux_solved_names']) & set(C['s1']['crux_solved_names']))
C['union_surv'] = sorted(set(C['s0']['survivors_solved_any']) | set(C['s1']['survivors_solved_any']))
# held-out greedy: recount from per-row jsonl
H = {}
for tag, f in [('big_s0', 'c_heldout_greedy_s0.jsonl'), ('big_s1', 'c_heldout_greedy_s1.jsonl'), ('base_s0', 'base_s0_heldout_greedy.jsonl')]:
    rs = [json.loads(l) for l in open(f'{SF}/{f}')]
    byL = collections.defaultdict(lambda: [0, 0])
    for r in rs: byL[r['n_lines']][0] += bool(r['solved']); byL[r['n_lines']][1] += 1
    H[tag] = {'n': len(rs), 'solved': sum(bool(r['solved']) for r in rs), 'rate': sum(bool(r['solved']) for r in rs) / len(rs),
              'by_L': {k: v for k, v in sorted(byL.items())}}
C['heldout'] = H
R['C'] = C

# ---------------- truncation per L_true stratum, every new sampling file ----------------
tr = collections.defaultdict(lambda: [0, 0])
for r in rows(f'{SF}/[abc]*_T*.jsonl'):
    key = (r['_f'].split('.')[0].rsplit('_sh', 1)[0].rsplit('_r1', 1)[0], r['L_true'])
    tr[key][0] += r['n_no_eos']; tr[key][1] += r['n_tried']
R['trunc'] = {f'{k[0]}|L{k[1]}': [v[0], v[1], v[0] / v[1] if v[1] else None] for k, v in sorted(tr.items())}
R['trunc_over_0.1pct'] = {k: v for k, v in R['trunc'].items() if v[2] and v[2] > 0.001}
json.dump(R, open('rev_sf/recount_abc.json', 'w'), indent=1, default=str)
