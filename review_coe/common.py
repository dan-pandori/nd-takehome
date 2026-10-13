#!/usr/bin/env python3
"""Reviewer's own shared code for the create-or-elicit recount (written independently of coe/; no import of coe/,
patterns.py, gen.py or intuit.py).

Formulas in the ND prompt syntax: atoms P Q R S, falsum F, '( ~ X )', '( A & B )', '( A v B )', '( A > B )'.
Tree form (G4ip encoding): ('a', 'P') | ('F',) | ('&', A, B) | ('v', A, B) | ('>', A, B); ~A is ('>', A, F).
"""
import functools, gzip, itertools, json, os, re, collections

RV = os.environ.get('RV_ROOT', os.path.expanduser('~/review/create-or-elicit'))
BIG = os.path.expanduser('~/review/coe_big')
FALSE = ('F',)


def opener(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)


def rows(p):
    with opener(p) as f:
        for l in f:
            if l.strip():
                yield json.loads(l)


# ---------------------------------------------------------------- formulas
def parse_toks(t, i=0):
    x = t[i]
    if x == '(':
        if t[i + 1] == '~':
            a, j = parse_toks(t, i + 2); assert t[j] == ')'; return ('>', a, FALSE), j + 1
        a, j = parse_toks(t, i + 1); op = t[j]; b, k = parse_toks(t, j + 1); assert t[k] == ')', (t, k)
        return ({'&': '&', 'v': 'v', '>': '>'}[op], a, b), k + 1
    if x == 'F':
        return FALSE, i + 1
    assert x in ('P', 'Q', 'R', 'S'), x
    return ('a', x), i + 1


def parse(s):
    t = s.split() if isinstance(s, str) else s
    f, j = parse_toks(t); assert j == len(t), (s, j)
    return f


def split_prompt(prompt):
    """-> (list of premise strings, conclusion string); top-level commas only."""
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    toks = prem.split(); out = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0:
            out.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur:
        out.append(' '.join(cur))
    return out, concl.strip()


def split_thm(thm):
    """'A , B |- C' -> ([A, B], C)."""
    prem, concl = thm.split('|-')
    toks = prem.split(); out = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0:
            out.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur:
        out.append(' '.join(cur))
    return out, concl.strip()


def sequent_of(rec):
    if rec.get('prompt'):
        return split_prompt(rec['prompt'])
    return split_thm(rec['thm'])


# ---------------------------------------------------------------- G4ip (reviewer's own, from review_cd/g4ip.py)
@functools.lru_cache(maxsize=None)
def prove(G, C):
    if C in G or FALSE in G:
        return True
    if C[0] == '&':
        return prove(G, C[1]) and prove(G, C[2])
    if C[0] == '>':
        return prove(G | {C[1]}, C[2])
    for A in G:
        if A[0] == '&':
            return prove((G - {A}) | {A[1], A[2]}, C)
        if A[0] == 'v':
            return prove((G - {A}) | {A[1]}, C) and prove((G - {A}) | {A[2]}, C)
        if A[0] == '>':
            a, b = A[1], A[2]
            if a == FALSE:
                return prove(G - {A}, C)
            if a[0] == 'a' and a in G:
                return prove((G - {A}) | {b}, C)
            if a[0] == '&':
                return prove((G - {A}) | {('>', a[1], ('>', a[2], b))}, C)
            if a[0] == 'v':
                return prove((G - {A}) | {('>', a[1], b), ('>', a[2], b)}, C)
    if C[0] == 'v' and (prove(G, C[1]) or prove(G, C[2])):
        return True
    for A in G:
        if A[0] == '>' and A[1][0] == '>':
            (_, (_, a, b), d) = A
            rest = G - {A}
            if prove(rest | {('>', b, d)}, ('>', a, b)) and prove(rest | {d}, C):
                return True
    return False


def intuit(prem, concl):
    return prove(frozenset(parse(p) for p in prem), parse(concl))


@functools.lru_cache(maxsize=None)
def classical_valid(prem_t, concl):
    """truth-table validity (classical) of a sequent of parsed trees."""
    atoms = set()

    def at(f):
        if f[0] == 'a': atoms.add(f[1])
        elif f[0] != 'F':
            at(f[1]); at(f[2])
    for p in prem_t: at(p)
    at(concl)
    atoms = sorted(atoms)

    def ev(f, v):
        if f[0] == 'a': return v[f[1]]
        if f[0] == 'F': return False
        if f[0] == '&': return ev(f[1], v) and ev(f[2], v)
        if f[0] == 'v': return ev(f[1], v) or ev(f[2], v)
        return (not ev(f[1], v)) or ev(f[2], v)
    for bits in itertools.product([False, True], repeat=len(atoms)):
        v = dict(zip(atoms, bits))
        if all(ev(p, v) for p in prem_t) and not ev(concl, v):
            return False
    return True


def g4ip_selftest():
    T = {('', 'P v ~P'): False}
    cases = [([], '( P v ( ~ P ) )', False), ([], '( ~ ( ~ ( P v ( ~ P ) ) ) )', True), ([], '( ( P & Q ) > P )', True),
             ([], '( ( ( P > Q ) > P ) > P )', False), (['( ~ ( ~ P ) )'], 'P', False), (['P'], '( ~ ( ~ P ) )', True),
             (['( P > Q )'], '( ( ~ Q ) > ( ~ P ) )', True), (['( ( ~ Q ) > ( ~ P ) )'], '( P > Q )', False),
             (['( ~ ( P & Q ) )'], '( ( ~ P ) v ( ~ Q ) )', False), (['( ~ ( P v Q ) )'], '( ( ~ P ) & ( ~ Q ) )', True),
             ([], '( ( ~ ( ~ ( ~ P ) ) ) > ( ~ P ) )', True), (['( ~ ( P > Q ) )'], 'P', False),
             (['( ~ ( P > Q ) )'], '( ~ Q )', True), (['( ( P > F ) > F )'], 'P', False), ([], '( ( P > Q ) v ( Q > P ) )', False),
             (['( P v Q )', '( ~ P )'], 'Q', True), ([], '( ( ( P > Q ) > Q ) > ( ( Q > P ) > P ) )', False)]
    for prem, c, e in cases:
        assert intuit(prem, c) == e, (prem, c, e)
        assert classical_valid(tuple(parse(p) for p in prem), parse(c)), (prem, c)
    return len(cases)


def is_dneg(f):
    """f is (X -> F) -> F, i.e. a double negation in Lean's sense (~ ~ X, (X > F) > F, ~ (X > F), (~ X) > F)."""
    return f[0] == '>' and f[2] == FALSE and f[1][0] == '>' and f[1][2] == FALSE


def subformulas(f):
    yield f
    if f[0] in ('&', 'v', '>'):
        yield from subformulas(f[1]); yield from subformulas(f[2])


def has_dneg_syntactic(strs):
    """'( ~ ( ~' written anywhere (the executor-style written check)."""
    return any('( ~ ( ~' in s for s in strs)


def has_dneg_semantic(strs):
    return any(is_dneg(g) for s in strs for g in subformulas(parse(s)))


# ---------------------------------------------------------------- renaming-class keys
PERMS = list(itertools.permutations('PQRS'))


def _ren(s, m):
    return ' '.join(m.get(t, t) for t in s.split())


def key_inv(prem, concl):
    """premise-order-invariant canonical key: min over the 24 bijections of (sorted premises, conclusion)."""
    best = None
    for p in PERMS:
        m = dict(zip('PQRS', p))
        k = (tuple(sorted(_ren(x, m) for x in prem)), _ren(concl, m))
        if best is None or k < best:
            best = k
    return best


def key_ord(prem, concl):
    """premise-order-SENSITIVE key: atoms relabelled P,Q,R,S by first appearance in the written sequent."""
    m = {}
    for t in ' , '.join(prem).split() + ['|-'] + concl.split():
        if t in 'PQRS' and len(t) == 1 and t not in m:
            m[t] = 'PQRS'[len(m)]
    return (tuple(_ren(x, m) for x in prem), _ren(concl, m))


def keys_of_rec(rec):
    prem, concl = sequent_of(rec)
    return key_inv(prem, concl), key_ord(prem, concl)


# ---------------------------------------------------------------- ND proofs
def parse_nd(nd):
    """-> list of (idx, depth, formula_str, rule, refs); stops at QED."""
    out = []
    for part in nd.replace(' ;', ' ; ').split(' ; '):
        part = part.strip().rstrip(';').strip()
        if not part:
            continue
        if part == 'QED':
            break
        t = part.split()
        idx = int(t[0][1:]); j = 1; depth = 0
        while t[j] == '|':
            depth += 1; j += 1
        c = len(t) - 1 - t[::-1].index(':')
        out.append((idx, depth, ' '.join(t[j:c]), t[c + 1], [int(x[1:]) for x in t[c + 2:]]))
    return out


BOXRULES = {'IMPI': [(0, 1)], 'NEGI': [(0, 1)], 'ORE': [(1, 2), (3, 4)]}


def box_ranges(L):
    """for every AS line: (start_pos, end_pos) of its box in the line list (end = last line at depth >= d)."""
    pos = {x[0]: i for i, x in enumerate(L)}
    rng = {}
    for i, (idx, d, f, rule, refs) in enumerate(L):
        if rule == 'AS':
            j = i
            while j + 1 < len(L) and L[j + 1][1] >= d and not (L[j + 1][1] == d and L[j + 1][3] == 'AS'):
                j += 1
            rng[idx] = (i, j)
    return pos, rng


def origin(L, pos, idx):
    """follow reiteration (R) lines back to the line that derived the formula."""
    seen = 0
    while L[pos[idx]][3] == 'R' and seen < 100:
        idx = L[pos[idx]][4][0]; seen += 1
    return idx


def prune(L):
    """dependency-pruned line set: lines the last line depends on (a box citation pulls in its hypothesis and end)."""
    pos = {x[0]: i for i, x in enumerate(L)}
    keep = set(); todo = [L[-1][0]]
    while todo:
        k = todo.pop()
        if k in keep or k not in pos:
            continue
        keep.add(k)
        todo.extend(L[pos[k]][4])
    return [x for x in L if x[0] in keep]


def dn_cites(L):
    """for every DN line: (dn_idx, rule of the cited line after following R, cited idx)."""
    pos = {x[0]: i for i, x in enumerate(L)}
    out = []
    for idx, d, f, rule, refs in L:
        if rule == 'DN' and refs:
            o = origin(L, pos, refs[0])
            out.append((idx, L[pos[o]][3], o))
    return out


def lemma_route(L, strict=True):
    """an IMPE whose function line is an IMPI box with a double-negation hypothesis inside which a DN cites that
    hypothesis (directly or via R), applied to an argument derived by NEGI (strict) / by any non-PR/AS rule."""
    pos, rng = box_ranges(L)
    lem = set()
    for idx, d, f, rule, refs in L:
        if rule == 'IMPI' and refs:
            h = refs[0]
            if h not in rng:
                continue
            i0, i1 = rng[h]
            hf = L[pos[h]][2]
            if not is_dneg(parse(hf)):
                continue
            for x in L[i0:i1 + 1]:
                if x[3] == 'DN' and x[4] and origin(L, pos, x[4][0]) == h:
                    lem.add(idx); break
    hits = []
    for idx, d, f, rule, refs in L:
        if rule == 'IMPE' and len(refs) == 2:
            fn = origin(L, pos, refs[0]); arg = origin(L, pos, refs[1])
            if fn in lem:
                ar = L[pos[arg]][3]
                if (ar == 'NEGI') if strict else (ar not in ('PR', 'AS')):
                    hits.append(idx)
    return hits


def sigma_flags(nd):
    """-> dict: sigma (DN on a NEGI-derived line), sigma_plus (DN on any derived line: not PR / AS), sigma_impi
    (DN on an IMPI line), lemma (strict lemma route), lemma_broad, dn_pr_as (DN on PR / AS only), dn (any DN),
    each for the written proof; and the same for the pruned proof with prefix 'p_'."""
    L = parse_nd(nd)
    out = {}
    for tag, LL in (('', L), ('p_', prune(L) if L else L)):
        c = dn_cites(LL) if LL else []
        rules = [r for _, r, _ in c]
        out[tag + 'dn'] = bool(c)
        out[tag + 'sigma'] = any(r == 'NEGI' for r in rules)
        out[tag + 'sigma_impi'] = any(r == 'IMPI' for r in rules)
        out[tag + 'sigma_plus'] = any(r not in ('PR', 'AS') for r in rules)
        out[tag + 'dn_pr_as_only'] = bool(c) and all(r in ('PR', 'AS') for r in rules)
        out[tag + 'lemma'] = bool(lemma_route(LL, True)) if LL else False
        out[tag + 'lemma_broad'] = bool(lemma_route(LL, False)) if LL else False
        out[tag + 'cited'] = rules
    return out


def written_depth(L):
    return max((x[1] for x in L), default=0)


def term_nodes(L):
    """a simple size of the pruned proof: number of formula tokens that are atoms/F/connectives over pruned lines."""
    n = 0
    for x in L:
        n += sum(1 for t in x[2].split() if t not in ('(', ')'))
    return n


# ---------------------------------------------------------------- reads
def read_rows(tag, d=None):
    d = d or f'{RV}/artifacts/coe/eval'
    p = f'{d}/{tag}.jsonl.gz'
    if not os.path.exists(p):
        p = f'{d}/{tag}.jsonl'
    return list(rows(p))


if __name__ == '__main__':
    print('g4ip self-test ok', g4ip_selftest())
    nd = ('N1 ( ( ~ P ) > F ) : PR ; N2 | ( ~ P ) : AS ; N3 | F : IMPE N1 N2 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; N5 P : DN N4 ; '
          'N6 ( ( ~ ( ~ Q ) ) v P ) : ORI2 N5 ; QED')
    print(sigma_flags(nd))
    nd2 = ('N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; QED')
    print(sigma_flags(nd2))
    nd3 = ('N1 | ( ~ ( ~ P ) ) : AS ; N2 | P : DN N1 ; N3 ( ( ~ ( ~ P ) ) > P ) : IMPI N1 N2 ; N4 | ( ~ P ) : AS ; N5 | | P : AS ; '
           'N6 | | F : NEGE N5 N4 ; N7 | ( ~ P ) : NEGI N5 N6 ; N8 | F : NEGE N7 N4 ; N9 ( ~ ( ~ P ) ) : NEGI N4 N8 ; N10 P : IMPE N3 N9 ; QED')
    print(sigma_flags(nd3))
    print(key_inv(['( P > Q )', 'Q'], 'P'), key_inv(['R', '( R > S )'], 'S'), key_ord(['( R > S )', 'R'], 'S'))
    print(has_dneg_semantic(['( ( ( ~ P ) > F ) > Q )']), has_dneg_semantic(['( P > Q )']), has_dneg_semantic(['( ~ ( P > F ) )']))
