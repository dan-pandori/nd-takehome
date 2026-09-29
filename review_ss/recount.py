#!/usr/bin/env python3
"""support-state reviewer recount (own code; reads only the per-theorem records + dumps)."""
import json, gzip, re, statistics, collections, sys, os
A = os.path.expanduser('~/review/support-state/artifacts/ss/')
D = os.path.expanduser('~/review/support-state/data/')
def L(f): return [json.loads(l) for l in open(A + f) if l.strip()]
surv = [l.strip() for l in open(D + 'sc/falsifier_survivors.txt') if l.strip()]
thms = {json.loads(l)['name']: json.loads(l) for l in open(D + 'sc/theorems.jsonl')}
assert len(thms) == 383 and set(surv) <= set(thms)

# my own start-index normaliser: renumber N<k> lines/cites in order of appearance
def mynorm(nd):
    m = {}
    def f(mo):
        k = mo.group(1)
        if k not in m: m[k] = str(len(m) + 1)
        return 'N' + m[k]
    return re.sub(r'\bN(\d+)\b', f, nd)

def check_rec(r):
    # internal consistency of one record
    assert sum(p['count'] for p in r['proofs']) == r['n_ok'], r['name']
    assert r['n_ok'] + r['n_leanrej'] + r['n_parse_fail'] == r['n_tried'], (r['name'], r['n_ok'], r['n_leanrej'], r['n_parse_fail'], r['n_tried'])
    ee = r['env_end']; assert sum(ee.values()) == r['n_tried'], (r['name'], ee, r['n_tried'])
    # distinct after my normaliser
    return len({mynorm(p['proof']) for p in r['proofs']})

out = {}
def per(f):
    R = L(f); d = {}
    for r in R:
        assert r['name'] not in d; d[r['name']] = r
        nd = check_rec(r)
        if nd != r['n_distinct_ok']: print('DISTINCT MISMATCH', f, r['name'], nd, r['n_distinct_ok'])
    return d

H = {s: {T: per(f'H_base_{T}_s{s}.s0.jsonl') for T in ('T08', 'T10')} for s in (0, 1)}
print('== H (29 survivors) ==')
for s in (0, 1):
    h8, h10 = H[s]['T08'], H[s]['T10']
    assert set(h8) == set(surv)
    need10 = {n for n in surv if h8[n]['n_ok'] < 5}
    assert set(h10) == need10, (set(h10) ^ need10)
    r8 = {n for n in surv if h8[n]['n_ok'] > 0}; r10 = {n for n in h10 if h10[n]['n_ok'] > 0}
    reach = r8 | r10
    first10k = {n for n in surv if h8[n]['n_ok'] > 0 and h8[n]['first_hit'] <= 10000}
    ph = sorted(h8[n]['n_ok'] / h8[n]['n_tried'] for n in surv)
    unreached = sorted(set(surv) - reach)
    trunc8 = sum(h8[n]['n_trunc_action'] + h8[n]['n_step_cap'] for n in surv); tried8 = sum(h8[n]['n_tried'] for n in surv)
    trunc10 = sum(r['n_trunc_action'] + r['n_step_cap'] for r in h10.values()); tried10 = sum(r['n_tried'] for r in h10.values())
    print(f's{s}: reached T0.8 {len(r8)}, T1.0 adds {len(r10 - r8)} (T1.0 run on {sorted(need10)}; reached {sorted(r10)}); '
          f'union {len(reach)}/29; unreached {unreached}; within first 10k at T0.8: {len(first10k)}; '
          f'median p_hat T0.8 {statistics.median(ph):.3g} (min {ph[0]:.2g}, max {ph[-1]:.3g}); '
          f'attempts T0.8 {tried8}, T1.0 {tried10}; len-cap hits T0.8 {trunc8}/{tried8}, T1.0 {trunc10}/{tried10}; '
          f'batch {set(r["batch"] for r in list(h8.values()) + list(h10.values()))}; peak GB max {max(r["peak_alloc_gb"] for r in h8.values())}')
    for n in unreached:
        print('   unreached', n, 'T0.8 tried', h8[n]['n_tried'], 'T1.0 tried', h10.get(n, {}).get('n_tried'))
    for n in sorted(r10 - r8): print('   T1.0-only', n, 'T0.8 tried', h8[n]['n_tried'], 'T1.0 n_ok', h10[n]['n_ok'], '/', h10[n]['n_tried'], 'first', h10[n]['first_hit'])
    out[f'H_s{s}'] = dict(reach=sorted(reach), unreached=unreached, first10k=len(first10k), med=statistics.median(ph),
                         phat={n: h8[n]['n_ok'] / h8[n]['n_tried'] for n in surv})
both = set(out['H_s0']['reach']) & set(out['H_s1']['reach'])
print('reached by both seeds', len(both), '; unreached by s0', out['H_s0']['unreached'], 'by s1', out['H_s1']['unreached'])
lo = sorted(surv, key=lambda n: out['H_s0']['phat'][n])[:6]
print('lowest p_hat s0 T0.8:', [(n, f"{out['H_s0']['phat'][n]:.2g}", f"{out['H_s1']['phat'][n]:.2g}") for n in lo])

print('== S1 (383, k 10k, stop 50, T0.8) ==')
S1 = {m: per(f'S1_{m}_T08_s0.s0.jsonl') for m in ('base', 'ei')}
for m in S1:
    d = S1[m]; assert set(d) == set(thms)
    sol = {n for n in d if d[n]['n_ok'] > 0}
    bc = collections.Counter(r['batch'] for r in d.values())
    tr = sum(r['n_trunc_action'] + r['n_step_cap'] for r in d.values()); tt = sum(r['n_tried'] for r in d.values())
    capped = sum(1 for r in d.values() if r['n_ok'] == 0 and r['n_tried'] != 10000)
    print(f'{m}: solved {len(sol)}/383 (survivors solved {len(sol & set(surv))}/29); batches {dict(bc)}; len-cap {tr}/{tt} = {tr/tt:.2e}; '
          f'unsolved with n_tried != 10000: {capped}; max per-theorem cap rate {max((r["n_trunc_action"]+r["n_step_cap"])/r["n_tried"] for r in d.values()):.3g}')
    out[f'S1_{m}'] = sol
b, e = S1['base'], S1['ei']
fwd = sorted(n for n in thms if b[n]['n_ok'] == 0 and e[n]['n_ok'] > 0)
rev = sorted(n for n in thms if e[n]['n_ok'] == 0 and b[n]['n_ok'] > 0)
print('forward crux (base 0 / EI>=1):', len(fwd), '; reverse crux:', len(rev), rev, [(b[n]['n_ok'], b[n]['n_tried']) for n in rev])
fl = [l.strip() for l in open(D + 'ss/sn_crux_forward.txt') if l.strip()]
rl = [l.strip() for l in open(D + 'ss/sn_crux_reverse.txt') if l.strip()]
print('file sn_crux_forward matches:', sorted(fl) == fwd, '; reverse matches:', sorted(rl) == rev)
print('survivors in SN forward crux:', len(set(fwd) & set(surv)))

print('== S2 forward crux deepening ==')
F = {k: per(f) for k, f in [('08_30', 'S2fwd08k30_base_T08_s0.s0.jsonl'), ('08_60', 'S2fwd08k60_base_T08_s0.s0.jsonl'),
                             ('08_160', 'S2fwd08k160_base_T08_s0.s0.jsonl'), ('10_40', 'S2fwd10k40_base_T10_s0.s0.jsonl'),
                             ('10_60', 'S2fwd10k60_base_T10_s0.s0.jsonl'), ('10_160', 'S2fwd10k160_base_T10_s0.s0.jsonl')]}
for k, d in F.items():
    tr = sum(r['n_trunc_action'] + r['n_step_cap'] for r in d.values()); tt = sum(r['n_tried'] for r in d.values())
    print(k, 'n', len(d), 'solved', sum(r['n_ok'] > 0 for r in d.values()), f'len-cap {tr}/{tt}', 'sets', sorted(d) == sorted(set(d) & set(fwd)))
tot = {}
for n in fwd:
    t8 = b[n]['n_tried'] + sum(F[k][n]['n_tried'] for k in ('08_30', '08_60', '08_160') if n in F[k])
    ok8 = b[n]['n_ok'] + sum(F[k][n]['n_ok'] for k in ('08_30', '08_60', '08_160') if n in F[k])
    t10 = sum(F[k][n]['n_tried'] for k in ('10_40', '10_60', '10_160') if n in F[k])
    ok10 = sum(F[k][n]['n_ok'] for k in ('10_40', '10_60', '10_160') if n in F[k])
    # at the pre-registered depth: S1 10k + k30 at T0.8 ; k40 at T1.0
    ok8_40 = b[n]['n_ok'] + F['08_30'][n]['n_ok']; ok10_40 = F['10_40'][n]['n_ok']
    tot[n] = dict(t8=t8, ok8=ok8, t10=t10, ok10=ok10, ok40=ok8_40 + ok10_40,
                  t8_40=b[n]['n_tried'] + F['08_30'][n]['n_tried'], t10_40=F['10_40'][n]['n_tried'],
                  pei=e[n]['n_ok'] / e[n]['n_tried'])
zero40 = [n for n in fwd if tot[n]['ok40'] == 0]
print('fwd crux: 0 base successes at 40k/temperature:', len(zero40), '; of which EI p_hat>=0.01:', sum(tot[n]['pei'] >= 0.01 for n in zero40),
      '; incomplete-depth among zero40 (stop_at 1 means solved ones stop early):',
      sum(1 for n in zero40 if tot[n]['t8_40'] < 40000 or tot[n]['t10_40'] < 40000))
E8 = sorted(n for n in zero40 if tot[n]['pei'] >= 0.01)
print('E8 =', len(E8))
z_all = [n for n in fwd if tot[n]['ok8'] + tot[n]['ok10'] == 0]
print('fwd crux never reached after all deepening:', len(z_all))
dist = collections.Counter((tot[n]['t8'], tot[n]['t10']) for n in z_all)
print('  depth (T0.8 attempts, T1.0 attempts) of those:', dict(dist))
print('  their EI p_hat:', sorted(round(tot[n]['pei'], 3) for n in z_all))
e8_12 = [l.strip() for l in open(D + 'ss/sn_deep_e8.txt') if l.strip()]
e8_16 = [l.strip() for l in open(D + 'ss/sn_deep_e8b.txt') if l.strip()]
print('sn_deep_e8 (12) subset of zero40:', set(e8_12) <= set(zero40), '; e8b (16):', set(e8_16) <= set(zero40), '; overlap', len(set(e8_12) & set(e8_16)),
      '; union', len(set(e8_12) | set(e8_16)), '; zero40 not deepened:', len(set(zero40) - set(e8_12) - set(e8_16)))
e8_not = sorted(set(E8) - set(z_all))
print('E8 theorems later reached by deepening:', len(e8_not), '; E8 still at 0:', len(set(E8) & set(z_all)))
# reached late: attempts to first hit
print('== reverse ==')
RV = per('S2revk20_ei_T08_s0.s0.jsonl')
for n, r in RV.items(): print(n, 'EI +', r['n_tried'], 'ok', r['n_ok'], '; base S1', b[n]['n_ok'], '/', b[n]['n_tried'])
json.dump({'fwd': fwd, 'rev': rev, 'E8': E8, 'z_all': z_all, 'tot': tot,
           'H': {k: {kk: (vv if not isinstance(vv, set) else sorted(vv)) for kk, vv in v.items()} for k, v in out.items() if k.startswith('H')}},
          open(os.path.expanduser('~/review/support-state/review_ss/recount.json'), 'w'), indent=1)
