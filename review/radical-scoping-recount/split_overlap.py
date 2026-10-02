"""Renaming-class overlap (own key: atoms renamed by first occurrence, premises kept in order and also as a sorted set)."""
import json, sys
def key(prompt):
    t = prompt.split(); t = t[1:t.index('PRF')] if 'PRF' in t else t[1:]; m = {}
    s = ' '.join(m.setdefault(x, 'ABCDEFGH'[len(m)]) if x in ('P', 'Q', 'R', 'S') else x for x in t)
    prem, concl = s.split('SEQ'); return (tuple(sorted(p.strip() for p in prem.split(' , ') if p.strip())), concl.strip())
def keys_all(prompt):  # order-free: try every premise order for first-occurrence naming
    import itertools
    t = prompt.split(); body = t[1:t.index('PRF')]; s = ' '.join(body); prem, concl = s.split('SEQ')
    ps = [p.strip() for p in prem.split(' , ') if p.strip()]; out = set()
    for perm in itertools.permutations(ps):
        out.add(key('THM ' + ' , '.join(perm) + ' SEQ ' + concl + ' PRF'))
    return out
ev = [json.loads(l) for l in open(sys.argv[1])]
EK = {}
for r in ev:
    for k in keys_all(r['prompt']): EK[k] = r['name']
hit = set()
for p in sys.argv[2:]:
    for l in open(p):
        r = json.loads(l)
        k = key(r['prompt'])
        if k in EK: hit.add(EK[k])
    print(p, 'eval items whose renaming class occurs in it:', len(hit))
