"""Own canonicaliser (claim-audit): a sequent's class invariant to atom renaming AND premise order (and premise
duplication, reported separately). Input 'A , B |- C' or prompt 'THM A , B SEQ C PRF'. 'F' is falsum, not an atom."""
import itertools, re
CONN = {'&', 'v', '>', '~', '(', ')', ',', 'F', '|-'}
def split_thm(s):
    s = s.strip()
    if s.startswith('THM'):
        s = s[3:].rsplit('PRF', 1)[0]
        lhs, rhs = s.split(' SEQ ')
    else:
        lhs, rhs = s.split('|-')
    lhs = lhs.strip()
    prem = [p.strip() for p in lhs.split(' , ')] if lhs else []
    return prem, rhs.strip()
def atoms(toks):
    seen = []
    for t in toks:
        if t not in CONN and t not in seen: seen.append(t)
    return seen
def canon(s, dedup=False):
    prem, concl = split_thm(s)
    if dedup: prem = sorted(set(prem))
    toks = ' '.join(prem + [concl]).split()
    at = atoms(toks)
    assert all(re.fullmatch(r'[A-EG-Z]', a) for a in at), at
    best = None
    names = [f'a{i}' for i in range(len(at))]
    for perm in itertools.permutations(names):
        m = dict(zip(at, perm))
        ren = lambda f: ' '.join(m.get(t, t) for t in f.split())
        key = ' , '.join(sorted(ren(p) for p in prem)) + ' |- ' + ren(concl)
        if best is None or key < best: best = key
    return best
if __name__ == '__main__':
    a = canon('( P & Q ) , ( ~ R ) |- ( P v F )'); b = canon('( ~ S ) , ( Q & P ) |- ( Q v F )')
    assert a == b, (a, b); assert canon('P |- P') != canon('P |- F'); print('canon self-test ok', a)
