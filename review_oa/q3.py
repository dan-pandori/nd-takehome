"""Reviewer Q3 recount: on-policy entropy trend, hard vs easy TF entropy, Cui fit, diversity, collapse vs stall."""
import json, os, statistics as st, collections
import numpy as np
from scipy.optimize import curve_fit
import rvc
E = f'{rvc.R}/artifacts/oa/entropy'
def ent(run, seed, ck, start=None):
    if run == 'rfc':
        p = f'{E}/c12_s{seed}/c12_s{seed}_{start}.json' if ck == 'r0' else f'{E}/rfc_{start}_s{seed}/rfc_s{seed}_{start}_{ck}.json'
    else: p = f'{E}/{run}_s{seed}/{run}_s{seed}_{ck}.json'
    return json.load(open(p)) if os.path.exists(p) else None
LAD = [(r, s, None) for r in ('c12', 'c6') for s in range(3)] + [('rfc', s, x) for s in range(3) for x in rvc.STARTS]
def rounds(run): return ['r0', 'r2', 'r4', 'r8'] if run == 'rfc' else ['pend'] + [f'r{k}' for k in range(1, 9)]
def lab(run, seed, ck, start):
    if run == 'rfc': return ('c12', f's{seed}_{start}') if ck == 'r0' else ('rfc', f's{seed}_{start}_{ck}')
    return run, f's{seed}_{ck}'
def rdir(run, seed, start):
    return f'{rvc.D}/rounds/la_T1_best{12 if run != "c6" else 6}_s{seed}' + (f'_{start}' if run == 'rfc' else '')
def cui(H, R):
    f = lambda h, a, b: -a * np.exp(h) + b
    (a, b), _ = curve_fit(f, H, R, p0=(1, 1), maxfev=20000)
    pr = f(np.array(H), a, b); r2 = 1 - ((np.array(R) - pr) ** 2).sum() / ((np.array(R) - np.mean(R)) ** 2).sum()
    return round(a, 3), round(b, 3), round(float(r2), 3), round(b - a, 3)
res = {}; peak = []; trunc = []
for run, seed, start in LAD:
    key = f'{run}_s{seed}' + (f'_{start}' if start else ''); cks = rounds(run)
    E_ = [ent(run, seed, c, start) for c in cks]
    if any(e is None for e in E_): print('missing', key, [c for c, e in zip(cks, E_) if e is None]); continue
    H = [e['onpol']['H08_tok'] for e in E_]; H1 = [e['onpol']['H1_tok'] for e in E_]
    peak += [e['onpol']['peak_alloc_gb'] for e in E_]; trunc += [(e['onpol']['trunc_rate'], e['label'], e['onpol']['ends']) for e in E_]
    mono = all(H[i + 1] <= H[i] for i in range(len(H) - 1)); drop = 1 - H[-1] / H[0]
    # hard vs easy teacher-forced entropy on the reference proofs: hard = step lp < -4 at r0 (from scores)
    S0 = rvc.score(run if run != 'rfc' else 'rfc', seed, 'pend' if run != 'rfc' else 'r0', start)
    hard_e, easy_e = [], []
    for e in E_:
        hh, ee = [], []
        for t, steps in e['tf'].items():
            if not t.startswith('ref:') or t not in S0: continue
            for i, s in enumerate(steps): (hh if S0[t]['step_lp'][i] < -4 else ee).append(s['H1'])
        hard_e.append(np.mean(hh)); easy_e.append(np.mean(ee))
    # x1 pass@1 on the 322
    p1 = []
    for c in cks:
        r = rvc.rd(*lab(run, seed, c, start), 1); p1.append(np.mean([d['n_ok'] / d['n_tried'] for d in r.values()]))
    # training-target sample accuracy: round_k.json is sampled from ckpt r(k-1)
    acc = {}
    for k in range(1, 9):
        f = f'{rdir(run, seed, start)}/round_{k}.json'
        if os.path.exists(f): acc[k] = json.load(open(f))['target_sample_acc']
    idx = [0, 2, 4, 8] if run == 'rfc' else list(range(9))
    # pairing A: H(ckpt r) with acc of round r+1 (samples drawn by ckpt r); r = 0..7
    pa = [(H[j], acc[r + 1]) for j, r in enumerate(idx) if r + 1 in acc]
    # pairing B (as the pre-registration literally reads): H(r) with round_r acc, r >= 1
    pb = [(H[j], acc[r]) for j, r in enumerate(idx) if r in acc]
    out = dict(H08=[round(h, 4) for h in H], H1=[round(h, 4) for h in H1], mono=mono, drop=round(drop, 3),
               drop_r0_r2_share=round((H[0] - H[2 if run != 'rfc' else 1]) / (H[0] - H[-1]), 3) if H[0] != H[-1] else None,
               hard_H1=[round(x, 3) for x in hard_e], easy_H1=[round(x, 3) for x in easy_e],
               pass1_x1=[round(x, 4) for x in p1], acc=acc)
    try: out['cui_acc_A'] = cui(*zip(*pa)) + (round(acc.get(8), 3) if run != 'rfc' else None,)
    except Exception as ex: out['cui_acc_A'] = str(ex)
    try: out['cui_acc_B'] = cui(*zip(*pb))
    except Exception as ex: out['cui_acc_B'] = str(ex)
    try: out['cui_pass1'] = cui(H, p1) + (round(p1[-1], 4),)
    except Exception as ex: out['cui_pass1'] = str(ex)
    # diversity & collapse vs stall (c12/c6 only: all rounds read)
    if run != 'rfc':
        rd0 = rvc.solved(run, f's{seed}_pend', 0); rd8 = rvc.solved(run, f's{seed}_r8', 0); names = set(rvc.rd(run, f's{seed}_pend', 0))
        A = rd0; C = names - rd0 - rd8
        div = []; cum = set(); ccount = []
        for c in cks:
            r0_ = rvc.rd(run, f's{seed}_{c}', 0)
            div.append(st.median(len(set(' '.join(p.split()) for p in r0_[n]['proofs'])) for n in A))
            if c != 'pend':
                for x in (0, 1): cum |= rvc.solved(run, f's{seed}_{c}', x) & C
            ccount.append(len(cum))
        mx = max(div); im = int(np.argmax(div)); collapse = next((i for i, v in enumerate(div) if i > im and v < 0.5 * mx), None)
        stall = next(i for i, v in enumerate(ccount) if v == ccount[-1])
        out.update(nA=len(A), nC=len(C), div_med_A=div, div_peak_round=int(np.argmax(div)), div_drop=round(1 - div[-1] / mx, 3),
                   C_cum=ccount, collapse_round=collapse, stall_round=stall,
                   collapse_before_stall=(collapse is not None and collapse < stall))
    res[key] = out; print(key, json.dumps(out), flush=True)
res['_peak_gb'] = [min(peak), max(peak)]; res['_trunc_max'] = sorted(trunc)[-4:]; res['_n_over_0p1pct'] = sum(t[0] > 1e-3 for t in trunc); res['_n_ck'] = len(trunc)
print('peak', res['_peak_gb'], 'trunc max', res['_trunc_max'])
json.dump(res, open('rv/q3.json', 'w'), indent=1)
