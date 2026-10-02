import json, hashlib, collections, math, glob, os
from common import *
TB = [r for f in ('textbook_dev', 'textbook_train') for r in jl(ROOT + '/data/eval_only/textbook72/%s.jsonl' % f)]
tbp = {r['prompt']: r for r in TB}
print('textbook72 records', len(TB), 'distinct prompts', len(tbp), 'distinct canon classes', len({canon(p) for p in tbp}))
def md5(fn): return hashlib.md5(open(fn, 'rb').read()).hexdigest()[:8]
def eval_solved(fn, P):
    S = set(); n = 0; incons = 0; names = collections.Counter()
    for d in jl(fn):
        n += 1
        if d['prompt'] not in P: continue
        names[d['prompt']] += 1
        s = truthy(d['solved']); has = bool(d.get('proofs'))
        if s != has: incons += 1
        if s and has: S.add(d['prompt'])
    return S, n, incons, sum(1 for v in names.values() if v > 1)
def dump_solved(fn, P):
    return {d['prompt'] for d in jl(fn) if truthy(d['lean_ok']) and d['prompt'] in P}
res = {}
T72 = RAW + '/textbook72/artifacts/textbook72/eval/'
rows = []
for lab in ['Fz_SN6_s0', 'Fz_SN6_s1', 'T1_SN6_s0', 'T1_SN6_s1'] + ['%s_SN12_s%d' % (a, s) for a in ('Fz', 'T1') for s in range(4)]:
    fn = T72 + lab + '.jsonl'
    if not os.path.exists(fn): fn = MY + '/tb/' + lab + '.jsonl'
    S, n, inc, dupn = eval_solved(fn, tbp)
    res[lab] = sorted(S); rows.append((lab, 'textbook72 eval', md5(fn), n, inc, len(S), ''))
BS = RAW + '/best-state/artifacts/bs/dump/'
for a in ('Fz', 'T1'):
    for c in ('best6', 'best12'):
        for s in range(3):
            lab = '%s_%s_s%d' % (a, c, s)
            D = dump_solved(BS + lab + '__tb72.jsonl.gz', tbp)
            E, n, inc, dupn = eval_solved(MY + '/bs/' + lab + '__tb72.jsonl', tbp)
            res[lab] = sorted(D)
            rows.append((lab, 'best-state dump|eval', md5(BS + lab + '__tb72.jsonl.gz'), n, inc, len(D), 'eval=%d dump^eval=%d' % (len(E), len(D ^ E))))
for r in rows: print('%-13s %-22s md5 %s rows %3d solved!=proofs %d  solved %2d  %s' % r)
json.dump(res, open(ROOT + '/rv/C3C4/c4_tb72_solved.json', 'w'))
# per-cell summaries
def cell(prefix, seeds): return [len(res[prefix % s]) for s in seeds]
cells = {'ours6 Fz': cell('Fz_SN6_s%d', (0, 1)), 'ours6 T1': cell('T1_SN6_s%d', (0, 1)),
         'ours12 Fz': cell('Fz_SN12_s%d', range(4)), 'ours12 T1': cell('T1_SN12_s%d', range(4)),
         'best6 Fz': cell('Fz_best6_s%d', range(3)), 'best6 T1': cell('T1_best6_s%d', range(3)),
         'best12 Fz': cell('Fz_best12_s%d', range(3)), 'best12 T1': cell('T1_best12_s%d', range(3))}
def iqm(v):
    v = sorted(v)
    if len(v) == 4: return (v[1] + v[2]) / 2
    return sum(v) / len(v)
def sd(v):
    m = sum(v) / len(v); return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
for k, v in cells.items(): print('%-10s %s mean %.2f iqm %.2f sd %.2f' % (k, v, sum(v)/len(v), iqm(v), sd(v)))
for cap in ('6', '12'):
    for a in ('Fz', 'T1'):
        b, o = cells['best%s %s' % (cap, a)], cells['ours%s %s' % (cap, a)]
        sp = math.sqrt(((len(b)-1)*sd(b)**2 + (len(o)-1)*sd(o)**2) / (len(b)+len(o)-2))
        # Welch-free pooled t
        t = (sum(b)/len(b) - sum(o)/len(o)) / (sp * math.sqrt(1/len(b) + 1/len(o)))
        print('cap %-2s %s best-ours mean %+.2f iqm %+.2f pooled sd %.2f t %.2f  sep %s' % (cap, a, sum(b)/len(b)-sum(o)/len(o), iqm(b)-iqm(o), sp, t, min(b) > max(o)))
