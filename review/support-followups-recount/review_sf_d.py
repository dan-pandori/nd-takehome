#!/usr/bin/env python3
"""Reviewer's blind re-derivation of stage D from the stored per-token log-probs (own segmentation, own classes)."""
import json, glob, collections, math, re, statistics as st
SURV = {l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()}
CRUX = {l.strip() for l in open('data/sc/crux_forward.txt') if l.strip()}
D = [json.loads(l) for l in open('artifacts/sf/d_steps.jsonl')]
out = {}
# --- set membership re-derived from sc raw records ---
def distinct(pat, names):
    s = collections.defaultdict(set)
    for f in glob.glob(pat):
        for l in open(f):
            r = json.loads(l)
            if r['name'] in names:
                for p in r['proofs']: s[r['name']].add(p['proof'])
    return s
S_raw = distinct('artifacts/sc/s1_ei_T08_s0.s*.jsonl', SURV)
for n, v in distinct('artifacts/sc/s2_ei_T10_s0.s0.jsonl', SURV).items(): S_raw[n] |= v
S_raw08 = distinct('artifacts/sc/s1_ei_T08_s0.s*.jsonl', SURV)
C1names = CRUX - SURV
C1_raw = distinct('artifacts/sc/s1_ei_T08_s0.s*.jsonl', C1names)
C1_rawT1 = distinct('artifacts/sc/s2_ei_T10_s0.s0.jsonl', C1names)
C2_raw = distinct('artifacts/sc/s1_base_T08_s0.s*.jsonl', set(json.loads(l)['name'] for l in open('data/sc/theorems.jsonl')))
bys = collections.defaultdict(list)
for r in D: bys[r['set']].append(r)
out['sets'] = {k: {'proofs': len(v), 'theorems': len({r['name'] for r in v})} for k, v in bys.items()}
out['S_raw_T08+T1'] = {'proofs': sum(map(len, S_raw.values())), 'theorems': len(S_raw)}
out['S_raw_T08_only'] = {'proofs': sum(map(len, S_raw08.values())), 'theorems': len(S_raw08)}
out['C1_raw_T08'] = {'proofs': sum(map(len, C1_raw.values())), 'theorems': len(C1_raw)}
out['C1_raw_T08+T1'] = {'proofs': sum(len(C1_raw[n] | C1_rawT1[n]) for n in set(C1_raw) | set(C1_rawT1)), 'theorems': len(set(C1_raw) | set(C1_rawT1))}
out['C2_raw'] = {'proofs': sum(map(len, C2_raw.values())), 'theorems': len(C2_raw)}
Sd = collections.defaultdict(set)
for r in bys['S']: Sd[r['name']].add(r['proof'])
out['S_d_equals_raw'] = all(Sd[n] == S_raw[n] for n in SURV)
out['S_d_minus_raw'] = sum(len(Sd[n] - S_raw[n]) for n in SURV); out['S_raw_minus_d'] = sum(len(S_raw[n] - Sd[n]) for n in SURV)
# --- sums ---
sec = {}
for l in open('artifacts/sc/secondary_logp.jsonl'):
    x = json.loads(l); lp = x['logp']
    if isinstance(lp, str): lp = eval(lp)
    sec[(x['name'], x['proof'])] = lp
bad_sum = 0; sec_cmp = []
for r in D:
    for T in ('1.0', '0.8'):
        if abs(sum(r['base']['tok_lp'][T]) - r['base']['logp_total'][T]) > 1e-3: bad_sum += 1
    k = (r['name'], r['proof'])
    if k in sec: sec_cmp.append(abs(sec[k]['base']['logp_T1'] - r['base']['logp_total']['1.0']))
out['tok_sum_mismatch'] = bad_sum
out['vs_sc_secondary'] = {'n': len(sec_cmp), 'max_abs_diff': max(sec_cmp) if sec_cmp else None, 'n_over_1e-3': sum(1 for d in sec_cmp if d > 1e-3)}
# --- my token classes ---
SYN = set('( ) ⟩ , have exact fun => by : := ; <eos>'.split()) | {'hh'}
LOGIC_RULE = {'.1', '.2', '.elim', 'Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction', '⟨'}
def my_cls(toks):
    c = []
    for i, t in enumerate(toks):
        if re.fullmatch(r'[nh]\d+', t):
            # fresh name: right after `have` or `fun (`
            fresh = i > 0 and (toks[i-1] == 'have' or (toks[i-1] == '(' and i > 1 and toks[i-2] == 'fun'))
            c.append('name:fresh' if fresh else 'name:cite')
        elif t in LOGIC_RULE: c.append('logic:rule')
        elif t == '(' and i > 0 and toks[i-1] == ':=' and i + 1 < len(toks) and toks[i+1] == 'fun': c.append('logic:rule')
        elif t in SYN: c.append('syntax')
        elif re.fullmatch(r'[A-Z]|False|¬|∧|∨|→', t): c.append('logic:formula')
        else: c.append('other:' + t)
    return c
def coarse(c): return c.split(':')[0]
agree = [0, 0]; other = collections.Counter(); confus = collections.Counter()
for r in D:
    mc = my_cls(r['tokens'])
    for a, b in zip(mc, r['token_cls']):
        agree[1] += 1; agree[0] += coarse(a) == coarse(b)
        if coarse(a) != coarse(b): confus[(a, b)] += 1
        if a.startswith('other'): other[a] += 1
out['class_agreement_coarse'] = agree; out['class_confusions'] = {str(k): v for k, v in confus.most_common(8)}; out['unclassified'] = dict(other)
# --- my steps ---
def steps(toks):
    b = []
    for i, t in enumerate(toks):
        if t in ('have', 'exact') or (t == 'fun' and i >= 2 and toks[i-1] == '(' and toks[i-2] == ')'):
            if t == 'fun': b.append(i - 1)
            else: b.append(i)
    b = sorted(set([0] + b))
    return [(b[j], (b[j+1] if j + 1 < len(b) else len(toks))) for j in range(len(b))]
def stats(r, T, who='base'):
    lp = r[who]['tok_lp'][T]; toks = r['tokens']
    sl = sorted((sum(lp[a:e]), a, e) for a, e in steps(toks))
    tot = sum(lp); w1 = sl[0][0]; w2 = sl[1][0] if len(sl) > 1 else 0.0
    s1 = w1 / tot if tot else 0; s2 = (w1 + w2) / tot if tot else 0
    rest = [x[0] for x in sl[1:]]
    kind = 'concentrated' if (s2 >= 0.5 and w1 <= -6) else ('spread' if (s2 < 0.5 and w1 > -6) else 'mixed')
    worst3 = sorted(range(len(lp)), key=lambda i: lp[i])[:3]
    return dict(total=tot, n_steps=len(sl), w1=w1, w2=w2, s1=s1, s2=s2, kind=kind,
                med_step_ex_worst=st.median(rest) if rest else 0.0, worst_step=' '.join(toks[sl[0][1]:sl[0][2]]),
                worst3=[(toks[i], my_cls(toks)[i], round(lp[i], 2)) for i in worst3])
for T in ('1.0', '0.8'):
    res = {}
    # primary unit: survivor's most-probable EI proof under the base at T
    prim = {}
    for r in bys['S']:
        if r['name'] not in prim or r['base']['logp_total'][T] > prim[r['name']]['base']['logp_total'][T]: prim[r['name']] = r
    P = {n: stats(r, T) for n, r in prim.items()}
    res['primary_kinds'] = dict(collections.Counter(p['kind'] for p in P.values()))
    res['primary_n'] = len(P)
    # compare with the executor's own stored per-proof kind (field only, used as a cross-check of my segmentation)
    key = 'T1' if T == '1.0' else 'T08'
    res['my_vs_stored_kind_agree'] = sum(1 for n, r in prim.items() if r['base'][key].get('worst_step_kind') is not None and False)
    res['my_vs_stored_nsteps_agree'] = sum(1 for n, r in prim.items() if r['base'][key]['n_steps'] == P[n]['n_steps'])
    res['my_vs_stored_w1_agree'] = sum(1 for n, r in prim.items() if abs(r['base'][key]['w1'] - P[n]['w1']) < 1e-3)
    res['my_vs_stored_s2_agree'] = sum(1 for n, r in prim.items() if abs(r['base'][key]['s2'] - P[n]['s2']) < 1e-3)
    allS = [stats(r, T) for r in bys['S']]
    res['allS_kinds'] = dict(collections.Counter(p['kind'] for p in allS))
    for sname in ('C1', 'C2', 'C3'):
        xs = [stats(r, T) for r in bys[sname]]
        res[f'{sname}_kinds'] = dict(collections.Counter(p['kind'] for p in xs))
        res[f'{sname}_w1_median'] = st.median(p['w1'] for p in xs)
        res[f'{sname}_med_step_ex_worst_median'] = st.median(p['med_step_ex_worst'] for p in xs)
        res[f'{sname}_total_median'] = st.median(p['total'] for p in xs)
    c2w = sorted(stats(r, T)['w1'] for r in bys['C2'])
    p5 = c2w[max(0, math.ceil(0.05 * len(c2w)) - 1)]
    res['C2_w1_p5'] = p5
    res['surv_w1_below_C2p5'] = sum(1 for p in P.values() if p['w1'] < p5)
    res['surv_primary_w1_median'] = st.median(p['w1'] for p in P.values())
    res['surv_primary_s2_median'] = st.median(p['s2'] for p in P.values())
    res['surv_primary_total_median'] = st.median(p['total'] for p in P.values())
    res['surv_primary_med_step_ex_worst_median'] = st.median(p['med_step_ex_worst'] for p in P.values())
    w3 = collections.Counter(c.split(':')[0] for p in P.values() for _, c, _ in p['worst3'])
    res['worst3_primary_coarse'] = dict(w3)
    w3f = collections.Counter(c for p in P.values() for _, c, _ in p['worst3']); res['worst3_primary_fine'] = dict(w3f)
    w3a = collections.Counter(c.split(':')[0] for p in allS for _, c, _ in p['worst3']); res['worst3_allS_coarse'] = dict(w3a)
    res['worst_step_first_token'] = dict(collections.Counter(p['worst_step'].split()[0] + ('/box' if 'fun' in p['worst_step'] else '') for p in P.values()))
    # surprisal share by class over S (all proofs)
    sh = collections.Counter()
    for r in bys['S']:
        for c, x in zip(my_cls(r['tokens']), r['base']['tok_lp'][T]): sh[c] += -x
    tot = sum(sh.values()); res['S_surprisal_share'] = {k: round(v / tot, 3) for k, v in sh.most_common()}
    res['per_survivor'] = {n: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in p.items()} for n, p in sorted(P.items())}
    out[f'T{T}'] = res
json.dump(out, open('rev_sf/recount_d.json', 'w'), indent=1, ensure_ascii=False)
for k, v in out.items():
    if not k.startswith('T'): print(k, v)
for T in ('T1.0', 'T0.8'):
    print('==', T); [print(' ', k, v) for k, v in out[T].items() if k != 'per_survivor']
