"""Adversarial check of C7's pretraining claims: DN on a self-introduced ~~ hypothesis.
For ORE-case hits: is the DN in the case whose disjunct the ORI actually built ('live') or the other ('dead')?
For NEGI-box hits: what the box concludes and whether the proof also has a #10. Prints counts only."""
import gzip, json, sys
from collections import Counter
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt, Proof
from cls import A, classify

name, fn = sys.argv[1], sys.argv[2]
LAB = '/home/dan/review/proof-strategies/review_ps/out/labels_%s.jsonl.gz' % name
lab = {}
for l in gzip.open(LAB, 'rt'):
    r = json.loads(l)
    lab[r['i']] = r
op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
res = Counter(); detail = Counter()
for i, line in enumerate(op):
    r = json.loads(line)
    pr = r.get('proof')
    if not pr or ' : DN ' not in pr:
        continue
    p, c = parse_prompt(r['prompt'])
    P = Proof(p, c, pr)
    a = A(P)
    box = {}
    for k in a.keep:
        x = P.L[k]
        if x['rule'] in ('IMPI', 'NEGI'):
            box[x['refs'][0]] = ('box', x['rule'], k)
        elif x['rule'] == 'ORE':
            j, s1, e1, s2, e2 = x['refs']
            box[s1] = ('ore', j, 1, k)
            box[s2] = ('ore', j, 2, k)
    hit = False
    for k in a.keep:
        x = P.L[k]
        if x['rule'] != 'DN':
            continue
        cc = a.o(x['refs'][0])
        if P.L[cc]['rule'] != 'AS' or ('~', ('~', x['f'])) in a.sub:
            continue
        hit = True
        b = box.get(cc)
        if b is None:
            res['no_box?'] += 1; continue
        if b[0] == 'ore':
            j = a.o(b[1]); jr = P.L[j]['rule']
            if jr in ('ORI1', 'ORI2'):
                built = 1 if jr == 'ORI1' else 2
                live = (built == b[2])
                src = a.o(P.L[j]['refs'][0]); srule = P.L[src]['rule']
                res['ore_case_live' if live else 'ore_case_dead'] += 1
                if live:
                    detail['live_src_rule:' + srule] += 1
            else:
                res['ore_case_j:' + jr] += 1
        else:
            res['box_' + b[1]] += 1
            # what does the NEGI line conclude, and who cites it
            nk = b[2]
            cit = [y for y in a.keep if nk in P.L[y]['refs']]
            detail['negi_citers:' + ','.join(sorted(P.L[y]['rule'] for y in cit))] += 1
            detail['negi_is_root:' + str(a.o(P.last) == nk)] += 1
    if hit:
        L = lab[i]
        detail['rec_uses_contradiction:' + str('contradiction' in L['uses'])] += 1
        detail['rec_classical_dn_sub:' + ','.join(sorted(s for s in L['sub'] if s.startswith('dne.')))] += 1
print(name, json.dumps(dict(res)), json.dumps(dict(detail)))
