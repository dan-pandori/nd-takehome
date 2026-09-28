#!/usr/bin/env python3
"""Phase-2 checks: per-theorem-best control medians, secondary-logp agreement, worst-token alternatives, non-EI survivor proofs."""
import json, glob, collections, statistics as st, math
from review_sf_d_helpers import steps, stats, my_cls
D = [json.loads(l) for l in open('artifacts/sf/d_steps.jsonl')]
SURV = {l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()}
out = {}
for T in ('1.0',):
    for S in ('S', 'C1', 'C2', 'C3'):
        best = {}
        for r in D:
            if r['set'] == S and (r['name'] not in best or r['base']['logp_total'][T] > best[r['name']]['base']['logp_total'][T]): best[r['name']] = r
        xs = []
        for r in best.values():
            lp = r['base']['tok_lp'][T]
            sl = sorted(sum(lp[a:e]) for a, e in steps(r['tokens']))
            xs.append(dict(total=sum(lp), w1=sl[0], w2=sl[1] if len(sl) > 1 else 0, w3=sl[2] if len(sl) > 2 else 0,
                           rest=sum(sl[2:]), rest3=sum(sl[3:]), s2=(sl[0] + (sl[1] if len(sl) > 1 else 0)) / sum(lp),
                           nlow=sum(1 for x in sl if x < math.log(0.1)), kind=stats(r, T)['kind']))
        out[S] = {'n_thm': len(xs), **{k: round(st.median(x[k] for x in xs), 2) for k in ('total', 'w1', 'w2', 'w3', 'rest', 'rest3', 's2', 'nlow')},
                  'kinds': dict(collections.Counter(x['kind'] for x in xs))}
        print(S, out[S])
# secondary agreement distribution
sec = {}
for l in open('artifacts/sc/secondary_logp.jsonl'):
    x = json.loads(l); lp = x['logp']; lp = eval(lp) if isinstance(lp, str) else lp; sec[(x['name'], x['proof'])] = lp
d = sorted(abs(r['base']['logp_total']['1.0'] - sec[(r['name'], r['proof'])]['base']['logp_T1']) for r in D if (r['name'], r['proof']) in sec)
out['sec_absdiff'] = {'n': len(d), 'median': d[len(d)//2], 'p90': d[int(.9*len(d))], 'max': d[-1], 'n_over_0.03': sum(1 for x in d if x > 0.03)}
print('secondary', out['sec_absdiff'])
# worst-token alternatives
A = [json.loads(l) for l in open('artifacts/sf/d_alternatives.jsonl')]
top = [math.exp(a['worst'][0]['base_top3'][0][1]) for a in A]; eil = [a['worst'][0]['ei_lp_at_shift'] for a in A]
alt = collections.Counter()
for a in A:
    w = a['worst'][0]; b = w['base_top3'][0][0]
    alt[('eos' if b == '<eos>' else 'exact' if b == 'exact' else 'formula' if b in ('P','Q','R','S','¬','∧','∨','→','False','(') and w['tok'] not in ('⟨',) else 'other', w['tok'], b)] += 1
out['alt'] = {'n': len(A), 'base_top1_mass_median': st.median(top), 'min': min(top), 'ei_lp_median': st.median(eil), 'ei_lp_min': min(eil),
              'pairs': {f'{k[1]}->{k[2]}': v for k, v in alt.most_common()}}
print('alt', {k: v for k, v in out['alt'].items() if k != 'pairs'}); print(out['alt']['pairs'])
# non-EI survivor proofs vs every EI proof on record
EI = collections.defaultdict(set)
for f in glob.glob('artifacts/sc/s*_ei_*.jsonl') + glob.glob('artifacts/sf/a_ei_*.jsonl'):
    for l in open(f):
        r = json.loads(l)
        for p in r['proofs']: EI[r['name']].add(p['proof'])
non = []
for f in glob.glob('artifacts/sf/[abc]*_T*.jsonl'):
    if '/a_ei' in f: continue
    for l in open(f):
        r = json.loads(l)
        if r['name'] in SURV:
            for p in r['proofs']:
                non.append((f.split('/')[-1], r['model'], r['seed'], r['name'], p['n_lines'], p['term_size'], p['proof'] in EI[r['name']]))
out['non_ei_survivor_proofs'] = non
for x in non: print('non-EI', x)
# EI proofs of la_transfer_1932: base log p range
print('1932 EI base logp T1', sorted(round(r['base']['logp_total']['1.0'], 1) for r in D if r['name'] == 'la_transfer_1932' and r['set'] == 'S'))
# peak mem, big model jobs
pm = [json.loads(l)['peak_mem_gb'] for f in glob.glob('artifacts/sf/c[12]_*.jsonl') for l in open(f)]
print('C peak mem max', max(pm))
json.dump(out, open('rev_sf/phase2.json', 'w'), indent=1, ensure_ascii=False, default=str)
