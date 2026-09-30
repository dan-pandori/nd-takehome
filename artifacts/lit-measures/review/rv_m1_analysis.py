#!/usr/bin/env python3
"""Reviewer M1 analysis from rv/m1_scores.jsonl: three step-attribution variants, best proof per theorem, E1.1-E1.3."""
import json, math, random, statistics as st, collections, sys
R = '/home/dan/review/lit-measures'
rows = [json.loads(l) for l in open(f'{R}/rv/m1_scores.jsonl')]
def lse(v):
    m = max(v); return m + math.log(sum(math.exp(x - m) for x in v))
def attrib(M, mean):
    """M[b][t] step log p per base.  L(t) = log(sum or mean)_b exp(cum_b(t)), L(0) = 0; step t gets L(t) - L(t-1)."""
    nb, T = len(M), len(M[0]); cum = [0.0] * nb; prev = 0.0; out = []
    for t in range(T):
        cum = [cum[b] + M[b][t] for b in range(nb)]
        L = lse(cum) - (math.log(nb) if mean else 0.0)
        out.append(L - prev); prev = L
    return out
def summ(c):
    tot = sum(c); s = sorted(c); w1 = s[0]; w2 = s[1] if len(s) > 1 else 0.0
    return dict(total=tot, w1=w1, w2=w2, rest=tot - w1 - w2, s1=w1 / tot if tot else 0, s2=(w1 + w2) / tot if tot else 0)
def label(m):
    if m['s2'] >= 0.5 and m['w1'] <= -6: return 'concentrated'
    if m['s2'] < 0.5 and m['w1'] > -6: return 'spread'
    return 'mixed'
V = {
 'exec_sum_allbases_full': lambda o, T: attrib(o[f'full_{T}'], False),
 'sampler_mean_b0to32_skipname': lambda o, T: attrib(o[f'skip_{T}'][:33], True),
 'sampler_mean_b0to32_full': lambda o, T: attrib(o[f'full_{T}'][:33], True),
 'raw_b0_full': lambda o, T: o[f'full_{T}'][0],
}
E = {(e['set'], e['name'], e['proof']): e for e in map(json.loads, open(f'{R}/artifacts/lit-measures/m1/steps.jsonl'))}
out = {}
for T in ('0.8', '1.0'):
    for vn, f in V.items():
        per = collections.defaultdict(list)
        for o in rows:
            c = f(o, float(T)); m = summ(c); m['label'] = label(m); m['o'] = o
            per[(o['set'], o['name'])].append(m)
        best = {k: max(v, key=lambda m: m['total']) for k, v in per.items()}
        S = [m for (s, n), m in best.items() if s == 'S']; C1 = [m for (s, n), m in best.items() if s == 'C1']
        C2 = [m for (s, n), m in best.items() if s == 'C2']
        lab = lambda X: dict(collections.Counter(m['label'] for m in X))
        w1S = [m['w1'] for m in S]; w1C = [m['w1'] for m in C1]
        obs = st.median(w1C) - st.median(w1S)
        pool = w1S + w1C; rng = random.Random(0); ge = 0; NP = 100000 if (vn.startswith('exec') or vn.startswith('sampler_mean_b0to32_skip')) and T == '0.8' else 20000
        for _ in range(NP):
            rng.shuffle(pool)
            ge += (st.median(pool[7:]) - st.median(pool[:7])) >= obs - 1e-12
        p = (ge + 1) / (NP + 1)
        e13 = {N: sum(x < math.log(3 / N) for x in w1S) for N in (400000, 200000)}
        e13c = {N: sum(x < math.log(3 / N) for x in w1C) for N in (400000, 200000)}
        print(f"T{T} {vn:30s} S labels {lab(S)} | C1 {lab(C1)} | C2 {lab(C2)} | med w1 S {st.median(w1S):.2f} C1 {st.median(w1C):.2f} "
              f"diff {obs:.2f} p {p:.4f} | w1<ln3/N S {e13[400000]}/7 (400k) {e13[200000]}/7 (200k); C1 {e13c[400000]}/35, {e13c[200000]}/35")
        out[(T, vn)] = best
        if vn == 'exec_sum_allbases_full':
            # reproduce executor's steps.jsonl per-proof numbers
            dmax = 0
            for o in rows:
                c = f(o, float(T)); m = summ(c); e = E[(o['set'], o['name'], o['proof'])][f'T{T}']
                dmax = max(dmax, abs(m['total'] - e['total']), abs(m['w1'] - e['w1']))
            print(f'    vs executor steps.jsonl T{T}: max |diff| total/w1 over {len(rows)} proofs = {dmax:.2e}')
b = out[('0.8', 'sampler_mean_b0to32_skipname')]
print('\nS theorems, best proof, sampler-mixture skip-name T0.8 vs exec variant:')
for (s, n), m in sorted(b.items()):
    if s != 'S': continue
    e = out[('0.8', 'exec_sum_allbases_full')][(s, n)]; r0 = out[('0.8', 'raw_b0_full')][(s, n)]
    wk = m['o']['actions'][[i for i, _ in sorted(enumerate(V['sampler_mean_b0to32_skipname'](m['o'], 0.8)), key=lambda x: x[1])][0]]
    print(f"  {n}: total {m['total']:.2f} w1 {m['w1']:.2f} s2 {m['s2']:.2f} {m['label']} | exec total {e['total']:.2f} w1 {e['w1']:.2f} {e['label']} | raw b0 w1 {r0['w1']:.2f} | worst step: {wk[:90]}")
