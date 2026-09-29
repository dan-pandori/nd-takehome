import json, re, collections
D = [json.loads(l) for l in open('/tmp/ssrev/d_steps.jsonl')]
S = [d for d in D if d['set'] == 'S']
def steps(toks, lp):
    out = []; cur = None
    for i, t in enumerate(toks):
        if t in ('have', 'exact'):
            if cur: out.append(cur)
            cur = [[], 0.0]
        if cur is None: continue
        cur[0].append(t); cur[1] += lp[i]
    if cur: out.append(cur)
    return out
def ab(ts):   # abstract names, drop trailing structure
    s = ' '.join(ts); s = re.sub(r'\bn\d+\b', 'n', s); s = s.replace(' .elim', '.elim').replace(' .1', '.1').replace(' .2', '.2')
    return s.split(' ;')[0].replace('<eos>', '').strip()
recs = {}
for s in (0, 1):
    for T in ('T08', 'T10'):
        for l in open(f'artifacts/ss/H_base_{T}_s{s}.s0.jsonl'):
            r = json.loads(l); recs.setdefault((s, r['name']), []).extend(p['lean_text'] for p in r['proofs'])
bythm = collections.defaultdict(list)
for d in S: bythm[d['name']].append(d)
res = {0: [0, 0], 1: [0, 0]}; kinds = collections.Counter()
for n, ds in bythm.items():
    d = max(ds, key=lambda x: x['count'])
    lp = d['base']['tok_lp']['0.8']; toks = d['tokens']
    assert len(lp) == len(toks), (len(lp), len(toks))
    st = steps(toks, lp); w = min(st, key=lambda x: x[1]); wl = ab(w[0])
    kinds[wl.split()[0] + (':' + wl.split(':=')[1].split()[0] if ':=' in wl else '')] += 1
    for s in (0, 1):
        texts = recs.get((s, n), [])
        if not texts: continue
        res[s][1] += 1
        hit = any(wl in re.sub(r'\bn\d+\b', 'n', t) for t in texts)
        res[s][0] += hit
print('E10: reached survivors whose SN-base proof(s) contain the whole-proof EI worst step (names abstracted):', res, 'kinds', kinds.most_common(6))
# stricter: only worst steps that are not a bare `exact n`
res = {0: [0, 0], 1: [0, 0]}; ex = 0
for n, ds in bythm.items():
    d = max(ds, key=lambda x: x['count']); st = steps(d['tokens'], d['base']['tok_lp']['0.8']); wl = ab(min(st, key=lambda x: x[1])[0])
    if re.fullmatch(r'exact n( : False \))?|exact \( n : False \)', wl): ex += 1; continue
    for s in (0, 1):
        texts = recs.get((s, n), [])
        if texts: res[s][1] += 1; res[s][0] += any(wl in re.sub(r'\bn\d+\b', 'n', t) for t in texts)
print('excluding bare-exact worst steps (%d theorems):' % ex, res)
# informative only: worst step carries a formula other than False
res = {0: [0, 0], 1: [0, 0]}; kinds = collections.Counter()
for n, ds in bythm.items():
    d = max(ds, key=lambda x: x['count']); st = steps(d['tokens'], d['base']['tok_lp']['0.8']); wl = ab(min(st, key=lambda x: x[1])[0])
    if wl.startswith('exact'): kinds['exact (cite a name)'] += 1; continue
    if wl.startswith('have n : False'): kinds['have False := n n'] += 1; continue
    kinds['formula-bearing'] += 1
    for s in (0, 1):
        texts = recs.get((s, n), [])
        if texts: res[s][1] += 1; res[s][0] += any(wl in re.sub(r'\bn\d+\b', 'n', t) for t in texts)
print('worst-step kinds', dict(kinds), '; formula-bearing worst step present in SN-base proofs:', res)
