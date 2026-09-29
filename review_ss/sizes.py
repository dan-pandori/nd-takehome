import json, re, statistics, os, collections
A = 'artifacts/ss/'
NODE = set('PQRSF') | {'~', '>', 'v', '&'}
def nd_size(nd):
    lines = [s.strip() for s in nd.split(';') if s.strip() and s.strip() != 'QED']
    ts = 0
    for s in lines:
        f = s.split(':')[0].split()[1:]; ts += sum(t in NODE for t in f if t != '|')
    return len(lines), ts
def lean_size(tx):
    toks = tx.replace('(', ' ( ').replace(')', ' ) ').split()
    return sum(t in ('have', 'exact') for t in toks), len(toks)
surv = set(l.strip() for l in open('data/sc/falsifier_survivors.txt'))
arms = {'H_s0': ['H_base_T08_s0', 'H_base_T10_s0'], 'H_s1': ['H_base_T08_s1', 'H_base_T10_s1'],
        'S1_base': ['S1_base_T08_s0'], 'S1_ei': ['S1_ei_T08_s0']}
mism = 0; tab = {}
for arm, fs in arms.items():
    rows = []
    for f in fs:
        for l in open(A + f + '.s0.jsonl'):
            r = json.loads(l)
            for p in r['proofs']:
                nl, ts = nd_size(p['proof'])
                if (nl, ts) != (p['n_lines'], p['term_size']): mism += 1
                la, lt = lean_size(p['lean_text'])
                rows.append((r['name'], nl, ts, la, lt, r['L_true']))
    med = lambda i: statistics.median(x[i] for x in rows)
    sv = [x for x in rows if x[0] in surv]
    tab[arm] = rows
    print(f'{arm}: {len(rows)} distinct proofs; median ND lines {med(1)}, ND term size {med(2)}, Lean actions {med(3)}, Lean tokens {med(4)}; '
          f'shorter-than-L_true share {sum(x[1] < x[5] for x in rows)/len(rows):.3f}; survivors: {len(sv)} proofs, median term {statistics.median(x[2] for x in sv) if sv else None}')
print('records whose stored n_lines/term_size differ from my count:', mism)
# shortest proof per survivor: SN base s0 vs whole-proof EI (support-followups d_steps)
D = [json.loads(l) for l in open('/tmp/ssrev/d_steps.jsonl') if json.loads(l)['set'] == 'S']
wp = collections.defaultdict(lambda: 10**9)
for d in D: wp[d['name']] = min(wp[d['name']], nd_size(d['proof'])[1])
sn = collections.defaultdict(lambda: 10**9)
for x in tab['H_s0']: sn[x[0]] = min(sn[x[0]], x[2])
c = collections.Counter('shorter' if sn[n] < wp[n] else 'equal' if sn[n] == wp[n] else 'longer' for n in sn if n in wp)
print('min term size per reached survivor, SN base s0 vs whole-proof EI (d_steps):', dict(c))
