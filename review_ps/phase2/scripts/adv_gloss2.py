"""#10 typical gloss: share of primary-#10 K12 proofs whose premises contain (~G > F); cases gloss: any ORE on a
BOTE-derived disjunction (after R) among primary-cases proofs. Counts only."""
import gzip, json, sys
from collections import Counter
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
W = '/home/dan/work/proof-strategies/artifacts/ps/labels/k12.jsonl.gz'
K = '/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz'
D = Counter()
def lines_of(proof):
    out = {}
    for part in proof.split(';'):
        t = part.split()
        if not t or t[0] == 'QED':
            continue
        k = int(t[0][1:]); i = 1
        while t[i] == '|':
            i += 1
        c = t.index(':', i)
        out[k] = {'f': ' '.join(t[i:c]), 'rule': t[c + 1], 'refs': [int(x[1:]) for x in t[c + 2:]]}
    return out
for le, lk in zip(gzip.open(W, 'rt'), gzip.open(K, 'rt')):
    a = json.loads(le); r = json.loads(lk)
    if a['pri'] == 'contradiction':
        body = r['prompt'].strip()[4:-4]
        prem, concl = body.split(' SEQ ')
        G = concl.strip()
        D['co.n'] += 1
        D['co.prem_notG_imp_F'] += ('( ( ~ ' + G + ' ) > F )') in prem
        D['co.prem_notnotG'] += ('( ~ ( ~ ' + G + ' ) )') in prem
    if a['pri'] == 'cases':
        D['ca.n'] += 1
        L = lines_of(r['proof'])
        anyb = False
        for k, x in L.items():
            if x['rule'] == 'ORE':
                j = x['refs'][0]
                while L[j]['rule'] == 'R':
                    j = L[j]['refs'][0]
                if L[j]['rule'] == 'BOTE':
                    anyb = True
        D['ca.any_ore_on_bote'] += anyb
print(dict(D))
print('#10 prem (~G>F) %.2f%%, prem ~~G %.2f%%; cases any ORE on BOTE disjunction %.2f%%' % (
    100*D['co.prem_notG_imp_F']/D['co.n'], 100*D['co.prem_notnotG']/D['co.n'], 100*D['ca.any_ore_on_bote']/D['ca.n']))
