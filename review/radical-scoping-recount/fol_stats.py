import json, collections, sys
sys.path.insert(0, '.'); from rv_fol import parse, mutate, inst
P = sys.argv[1]; recs = [json.loads(l) for l in open(P)]
m = json.load(open('out/fol_pool1k_mut.json'))['res']; base = json.load(open('out/fol_pool1k.json'))['res']
ok_mut = [int(k[2:]) for k, v in m.items() if v['ok']]
why = collections.Counter()
for k in ok_mut:
    _, _, L = parse(mutate(recs[k]['text'], k)); last = L[max(L)]
    why[last['rule']] += 1
print('mutants accepted by Lean, by rule of the final line:', dict(why))
rc = collections.Counter(); lines = collections.Counter(); ax = collections.Counter(); qn = 0; vac = 0; eig = 0
for k, r in enumerate(recs):
    _, _, L = parse(r['text']); rs = {l['rule'] for l in L.values()}
    for x in rs: rc[x] += 1
    lines[len(L)] += 1; ax[base[f'rv{k}']['axioms']] += 1
    qn += bool(rs & {'ALLI', 'ALLE', 'EXI', 'EXE'})
    for l in L.values():
        if l['rule'] == 'ALLI':
            p = inst(l['f'][2], l['f'][1], L[l['refs'][0]]['f']); eig += p in 'abcde'; vac += p == l['f'][1]
print('rule -> #proofs using it', dict(sorted(rc.items(), key=lambda x: -x[1])))
print('quantifier proofs', qn, 'ALLI with constant eigen-param', eig, 'ALLI with param == bound var (no freshness check)', vac)
print('lines', sorted(lines.items())); print('axioms', dict(ax))
