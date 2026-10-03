#!/usr/bin/env python3
"""Reviewer recount for guided-tts (own code). Reads only data/gt/*.jsonl and artifacts/gt/eval/*.{json,rows.jsonl.gz}."""
import gzip, json, os, sys, math, random
from math import comb
R = os.path.expanduser('~/review/guided-tts')
FILES = ['tb72_textbook_dev', 'tb72_textbook_train', 'candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14']
REL = FILES[2:]
MODELS = [f'best{c}_s{s}' for c in (12, 6) for s in (0, 1, 2)]
ARMS = ['plain', 'structural', 'logical']
KS = [1, 2, 4, 8, 16, 32, 64, 128, 256]

# --- my own problem table
probs = []
for f in FILES:
    for l in open(f'{R}/data/gt/{f}.jsonl'):
        if l.strip():
            r = json.loads(l)
            src = r.get('source') if isinstance(r.get('source'), dict) else {}
            ml = r.get('min_lines', r.get('reference_lines'))
            probs.append(dict(file=f, name=r['name'], prompt=r['prompt'], ml=ml, sid=src.get('id')))
def groups(p):
    g = {'all', 'file:' + p['file']}
    if p['file'].startswith('tb72'): g.add('tb72')
    if p['file'] in REL:
        g.add('release')
        g.add('bin<=10' if p['ml'] <= 10 else ('bin11-20' if p['ml'] <= 20 else 'bin>20'))
        if p['ml'] > 10: g.add('long')
    if p['file'] in ('candidate_v1', 'hand_proved_14') and p['sid'] == 'roy': g.add('roy')
    if p['file'] in ('batch3', 'hand_proved_14') and p['sid'] == 'pelletier': g.add('pelletier')
    if p['file'] == 'batch3': g.add('batch3')
    return g
for p in probs: p['g'] = groups(p)
GN = ['all', 'tb72', 'release', 'long', 'roy', 'pelletier', 'batch3', 'bin<=10', 'bin11-20', 'bin>20'] + ['file:' + f for f in FILES]
gsize = {g: sum(g in p['g'] for p in probs) for g in GN}

def passk(n, c, k):
    if k <= 0: return 0.0
    if n - c < k: return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)
def passk_frac(n, c, k):
    k = min(k, n)
    lo = math.floor(k); hi = math.ceil(k)
    if lo == hi: return passk(n, c, lo)
    return passk(n, c, lo) + (k - lo) * (passk(n, c, hi) - passk(n, c, lo))

def load(m, a):
    rows = [json.loads(l) for l in gzip.open(f'{R}/artifacts/gt/eval/{m}_{a}.rows.jsonl.gz', 'rt')]
    summ = json.load(open(f'{R}/artifacts/gt/eval/{m}_{a}.json'))
    assert len(rows) == len(probs)
    for r, p in zip(rows, probs):
        assert (r['file'], r['name'], r['prompt']) == (p['file'], p['name'], p['prompt']), (r['name'], p['name'])
        assert len(r['ok']) == 256 and sum(r['ok']) == r['n_ok']
    return rows, summ

D = {(m, a): load(m, a) for m in MODELS for a in ARMS}
out = {'gsize': gsize}
# solved@256 per group
solved = {}
for (m, a), (rows, s) in D.items():
    for g in GN:
        solved[f'{m}|{a}|{g}'] = sum(1 for r, p in zip(rows, probs) if g in p['g'] and r['n_ok'] > 0)
out['solved'] = solved
# cross-check vs the executor's own summary json (per file)
mism = []
for (m, a), (rows, s) in D.items():
    for f in FILES:
        if s['solved'][f] != solved[f'{m}|{a}|file:{f}']: mism.append((m, a, f))
out['summary_mismatch'] = mism

def secs(s):
    st = s['stats']; return st['gpu_s'] + st['check_s'] + st['env_s'] + st['lean_s']
def curve(m, a, g, mode):
    rp, sp = D[(m, 'plain')]; ra, sa = D[(m, a)]
    res = []
    for k in KS:
        tot = 0.0; n = 0
        for rP, rA, p in zip(rp, ra, probs):
            if g not in p['g']: continue
            n += 1
            if mode == 'attempt': kk = k
            elif mode == 'tokens': kk = k * (sum(rP['tokens']) / 256) / (sum(rA['tokens']) / 256)
            elif mode == 'wall': kk = k * (secs(sp) / sp['attempts']) / (secs(sa) / sa['attempts'])
            tot += passk_frac(256, rA['n_ok'], min(kk, 256))
        res.append(tot / n)
    return res
curves = {}
for m in MODELS:
    for a in ARMS:
        for g in GN:
            for mode in ('attempt', 'tokens', 'wall'):
                curves[f'{m}|{a}|{g}|{mode}'] = curve(m, a, g, mode)
out['curves'] = curves

# paired theorem-bootstrap CI on the long-group difference at k=64 and 256 (tokens), per model
random.seed(0)
def per_thm(m, a, k, g, mode='tokens'):
    rp, sp = D[(m, 'plain')]; ra, sa = D[(m, a)]
    v = []
    for rP, rA, p in zip(rp, ra, probs):
        if g not in p['g']: continue
        kk = k * (sum(rP['tokens']) / sum(rA['tokens'])) if mode == 'tokens' else k
        v.append(passk_frac(256, rA['n_ok'], min(kk, 256)) - passk_frac(256, rP['n_ok'], k))
    return v
boot = {}
for m in MODELS:
    for a in ('structural', 'logical'):
        for g in ('long', 'bin<=10', 'roy', 'pelletier', 'batch3'):
            for k in (1, 64, 256):
                v = per_thm(m, a, k, g)
                bs = sorted(sum(random.choice(v) for _ in v) / len(v) for _ in range(2000))
                boot[f'{m}|{a}|{g}|{k}'] = [sum(v) / len(v), bs[50], bs[1949]]
out['diff_boot'] = boot

# falsifier: logical <= plain at every k (tokens) on long
fal = {}
for m in MODELS:
    L = curves[f'{m}|logical|long|tokens']; P = curves[f'{m}|plain|long|tokens']
    fal[m] = all(l <= p for l, p in zip(L, P))
out['falsifier_logical_le_plain_all_k_long'] = fal

# cost ratios and rates
cost = {}
for m in MODELS:
    for a in ARMS:
        rows, s = D[(m, a)]; st = s['stats']
        tok = sum(sum(r['tokens']) for r in rows); dr = sum(sum(r['draws']) for r in rows)
        steps = sum(sum(r['steps']) for r in rows); rej = sum(sum(r['rej']) for r in rows)
        ends = {}
        for r in rows:
            for x in r['status']: ends[x] = ends.get(x, 0) + 1
        rc = st['rej_cause']
        S = sum(v for k2, v in rc.items() if k2.startswith('S:')); L = sum(v for k2, v in rc.items() if k2.startswith('L:'))
        cost[f'{m}|{a}'] = dict(tokens=tok, tokens_summary=st['sampled_tokens'], draws=dr, steps=steps, rej=rej,
                               ends=ends, gpu_s=st['gpu_s'], secs=secs(s), batch=s['batch'], peak=st['peak_alloc_gb'],
                               S=S, L=L, trunc=rc.get('truncated', 0), finished=s['finished'], accepted=s['accepted'],
                               lean_rejected_final=s['finished'] - s['accepted'], repeat_mean=s.get('repeat_mean'),
                               long_tok_ratio=None)
        # long-group token ratio to plain
    for a in ARMS:
        rp, _ = D[(m, 'plain')]; ra, _ = D[(m, a)]
        num = sum(sum(r['tokens']) for r, p in zip(ra, probs) if 'long' in p['g'])
        den = sum(sum(r['tokens']) for r, p in zip(rp, probs) if 'long' in p['g'])
        cost[f'{m}|{a}']['long_tok_ratio'] = num / den
out['cost'] = cost
json.dump(out, open(f'{R}/rv/rc_count.json', 'w'), indent=0)

# ---- print
print('group sizes', gsize)
print('summary mismatches:', mism)
print('\nsolved@256 (attempt-k) per group')
for g in ['tb72', 'release', 'long', 'roy', 'pelletier', 'batch3', 'bin<=10', 'bin11-20', 'bin>20', 'all']:
    print(f'{g:10s}', '  '.join(f"{m}:" + '/'.join(str(solved[f'{m}|{a}|{g}']) for a in ARMS) for m in MODELS))
for g in ['long', 'bin<=10', 'roy', 'pelletier', 'batch3']:
    print(f'\n== {g}: matched-token solve rate at k=1,64,256 (plain / structural / logical), diff vs plain [95% theorem-bootstrap]')
    for m in MODELS:
        c = {a: curves[f'{m}|{a}|{g}|tokens'] for a in ARMS}
        w = {a: curves[f'{m}|{a}|{g}|wall'] for a in ARMS}
        line = f'{m:9s} '
        for ki, k in ((0, 1), (6, 64), (8, 256)):
            line += f' k{k}: ' + '/'.join(f'{c[a][ki]:.3f}' for a in ARMS)
        print(line)
        for a in ('structural', 'logical'):
            print('     ', a, ' '.join(f"k{k}: {boot[f'{m}|{a}|{g}|{k}'][0]*100:+.1f} [{boot[f'{m}|{a}|{g}|{k}'][1]*100:+.1f},{boot[f'{m}|{a}|{g}|{k}'][2]*100:+.1f}]" for k in (1, 64, 256)),
                  ' wall k64/256:', f'{(w[a][6]-w["plain"][6])*100:+.1f} {(w[a][8]-w["plain"][8])*100:+.1f}',
                  ' attempt k1/64/256:', ' '.join(f"{(curves[f'{m}|{a}|{g}|attempt'][i]-curves[f'{m}|plain|{g}|attempt'][i])*100:+.1f}" for i in (0, 6, 8)))
print('\nfalsifier (logical<=plain at all k, long, tokens):', fal)
print('\ncost per model|arm: tokensM, ratio, longratio, draws, steps, S-rej, L-rej, trunc/draws, ends, lean-rejected finals, gpu_s, secs, batch, peak')
for m in MODELS:
    for a in ARMS:
        c = cost[f'{m}|{a}']; cp = cost[f'{m}|plain']
        print(f"{m}|{a:10s} {c['tokens']/1e6:6.2f} {c['tokens']/cp['tokens']:.2f}x long {c['long_tok_ratio']:.2f}x dr {c['draws']} st {c['steps']} S {c['S']} ({c['S']/max(1,c['steps'])*100:.2f}%/step) L {c['L']} ({c['L']/max(1,c['steps'])*100:.2f}%) tr {c['trunc']/c['draws']*100:.3f}% ends {c['ends']} leanrej {c['lean_rejected_final']} gpu {c['gpu_s']:.0f} s {c['secs']:.0f} b {c['batch']} pk {c['peak']:.1f} rep {c['repeat_mean']}")
