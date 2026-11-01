"""Reviewer (coe-dose01) common helpers, written independently of the executor's code.

Formulas are the project's fully parenthesised strings: atoms P Q R S, F = falsum (NOT an atom), ( ~ X ), ( X v Y ),
( X & Y ), ( X > Y ).  Sequents: 'A , B |- C' (thm fields) or 'THM A , B SEQ C PRF' (prompts).
"""
import gzip, itertools, json, os

ATOMS = ('P', 'Q', 'R', 'S')
BIG = os.path.expanduser('~/review/cd01_big')
REPO = '/home/dan/work/coe-dose01'


def jl(fn):
    op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
    with op as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


# ---------- formula parsing ----------
def tokens(s):
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def parse_f(toks, i=0):
    """-> (tree, next index).  tree: ('atom', 'P') | ('bot',) | ('not', A) | (op, A, B) with op in and/or/imp."""
    t = toks[i]
    if t in ATOMS:
        return ('atom', t), i + 1
    if t == 'F':
        return ('bot',), i + 1
    assert t == '(', (t, toks)
    if toks[i + 1] == '~':
        a, j = parse_f(toks, i + 2)
        assert toks[j] == ')', toks
        return ('not', a), j + 1
    a, j = parse_f(toks, i + 1)
    op = {'v': 'or', '&': 'and', '>': 'imp'}[toks[j]]
    b, k = parse_f(toks, j + 1)
    assert toks[k] == ')', toks
    return (op, a, b), k + 1


def pf(s):
    t = tokens(s)
    f, j = parse_f(t)
    assert j == len(t), s
    return f


def split_top(s):
    """split 'A , B , C' at top-level commas"""
    out, depth, cur = [], 0, []
    for t in tokens(s):
        if t == '(':
            depth += 1
        elif t == ')':
            depth -= 1
        if t == ',' and depth == 0:
            out.append(' '.join(cur)); cur = []
        else:
            cur.append(t)
    if cur:
        out.append(' '.join(cur))
    return out


def seq_of_prompt(prompt):
    """'THM A , B SEQ C PRF' -> ([A, B], C) as strings"""
    p = prompt.strip()
    assert p.startswith('THM') and p.endswith('PRF'), p
    body = p[3:-3].strip()
    i = body.rindex(' SEQ ') if ' SEQ ' in body else None
    if body.startswith('SEQ '):
        prem, concl = '', body[4:]
    else:
        prem, concl = body[:i], body[i + 5:]
    return [x for x in split_top(prem) if x], concl.strip()


def seq_of_thm(thm):
    prem, concl = thm.split('|-')
    return [x for x in split_top(prem.strip()) if x], concl.strip()


def fs(f):
    """tree -> canonical string"""
    if f[0] == 'atom':
        return f[1]
    if f[0] == 'bot':
        return 'F'
    if f[0] == 'not':
        return f'( ~ {fs(f[1])} )'
    return f"( {fs(f[1])} {dict(or_='v', and_='&', imp_='>')[f[0] + '_']} {fs(f[2])} )"


def rename(f, m):
    if f[0] == 'atom':
        return ('atom', m[f[1]])
    if f[0] == 'bot':
        return f
    if f[0] == 'not':
        return ('not', rename(f[1], m))
    return (f[0], rename(f[1], m), rename(f[2], m))


PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]


def class_key(prems, concl):
    """premise-order-invariant renaming class: min over the 24 atom bijections of (sorted premises, conclusion).
    Duplicate premises are kept (multiset)."""
    P = [pf(x) for x in prems]
    C = pf(concl)
    best = None
    for m in PERMS:
        k = (tuple(sorted(fs(rename(p, m)) for p in P)), fs(rename(C, m)))
        if best is None or k < best:
            best = k
    return ' , '.join(best[0]) + ' |- ' + best[1]


def class_key_set(prems, concl):
    """weaker key: premises as a SET (duplicates merged) -- catches 'A , A |- C' vs 'A |- C'."""
    P = sorted(set(prems))
    return class_key(P, concl)


# ---------- Lean statement ----------
def lean_f(f):
    if f[0] == 'atom':
        return f[1]
    if f[0] == 'bot':
        return 'False'
    if f[0] == 'not':
        return f'(¬ {lean_f(f[1])})'
    return f"({lean_f(f[1])} {dict(or_='∨', and_='∧', imp_='→')[f[0] + '_']} {lean_f(f[2])})"


def lean_statement(prompt, name='t'):
    prems, concl = seq_of_prompt(prompt)
    hs = ' '.join(f'(h{i + 1} : {lean_f(pf(p))})' for i, p in enumerate(prems))
    return f'theorem {name} (P Q R S : Prop) {hs} : {lean_f(pf(concl))} := by'


# ---------- classical validity and G4ip intuitionistic provability ----------
def ev(f, v):
    k = f[0]
    if k == 'atom':
        return v[f[1]]
    if k == 'bot':
        return False
    if k == 'not':
        return not ev(f[1], v)
    a, b = ev(f[1], v), ev(f[2], v)
    return (a or b) if k == 'or' else (a and b) if k == 'and' else ((not a) or b)


def classical(prems, concl):
    P = [pf(x) for x in prems]; C = pf(concl)
    for bits in itertools.product((False, True), repeat=4):
        v = dict(zip(ATOMS, bits))
        if all(ev(p, v) for p in P) and not ev(C, v):
            return False
    return True


BOT = ('bot',)


def _n(f):
    """negation as implication to falsum"""
    if f[0] == 'not':
        return ('imp', _n(f[1]), BOT)
    if f[0] in ('and', 'or', 'imp'):
        return (f[0], _n(f[1]), _n(f[2]))
    return f


def g4ip(gamma, goal, memo=None):
    """Dyckhoff's contraction-free G4ip; gamma: frozenset of formulas (with ~X written as X > F)."""
    if memo is None:
        memo = {}
    key = (gamma, goal)
    if key in memo:
        return memo[key]
    memo[key] = False      # loop guard (G4ip terminates anyway)
    res = _g4(gamma, goal, memo)
    memo[key] = res
    return res


def _g4(G, C, memo):
    if BOT in G or C in G:
        return True
    # invertible left rules
    for f in G:
        k = f[0]
        if k == 'and':
            return g4ip((G - {f}) | {f[1], f[2]}, C, memo)
        if k == 'or':
            R = G - {f}
            return g4ip(R | {f[1]}, C, memo) and g4ip(R | {f[2]}, C, memo)
        if k == 'imp':
            a, b = f[1], f[2]
            if a == BOT:
                return g4ip(G - {f}, C, memo)
            if a[0] == 'atom' and a in G:
                return g4ip((G - {f}) | {b}, C, memo)
            if a[0] == 'and':
                return g4ip((G - {f}) | {('imp', a[1], ('imp', a[2], b))}, C, memo)
            if a[0] == 'or':
                return g4ip((G - {f}) | {('imp', a[1], b), ('imp', a[2], b)}, C, memo)
    # invertible right rules
    if C[0] == 'and':
        return g4ip(G, C[1], memo) and g4ip(G, C[2], memo)
    if C[0] == 'imp':
        return g4ip(G | {C[1]}, C[2], memo)
    # non-invertible: or-right, and (A>B)>D on the left
    if C[0] == 'or' and (g4ip(G, C[1], memo) or g4ip(G, C[2], memo)):
        return True
    for f in G:
        if f[0] == 'imp' and f[1][0] == 'imp':
            a, b, d = f[1][1], f[1][2], f[2]
            R = G - {f}
            if g4ip(R | {('imp', b, d)}, ('imp', a, b), memo) and g4ip(R | {d}, C, memo):
                return True
    return False


def intuitionistic(prems, concl):
    return g4ip(frozenset(_n(pf(x)) for x in prems), _n(pf(concl)))


def has_dneg(prems, concl):
    """any ( ~ ( ~ X ) ) subformula anywhere in the sequent"""
    def rec(f):
        if f[0] == 'not':
            return f[1][0] == 'not' or rec(f[1])
        if f[0] in ('and', 'or', 'imp'):
            return rec(f[1]) or rec(f[2])
        return False
    return any(rec(pf(x)) for x in prems + [concl])


def strict_members():
    """the 106 strict sigma-covered held-out members (definition inherited from create-or-elicit's families.json)
    -> {name: family}"""
    fam = json.load(open(f'{REPO}/data/coe/families.json'))
    out = {}
    for f, d in fam['families'].items():
        if d['classical']:
            for n in d['strict_heldout']:
                out[n] = f
    for n in fam['generated_classical']['transfer']['strict']:
        out[n] = 'generated'
    return out


def selftest():
    # G4ip / classical unit cases: schema instances with COMPOUND substitutions, each checked not to be a textbook72
    # renaming class (review_cd01/tb72strict.tb_keys); expected values from theory, not from this code
    cases = [
        ([], '( ( P & Q ) > ( Q v R ) )', True, True),
        ([], '( ( P & Q ) v ( ~ ( P & Q ) ) )', True, False),                      # LEM instance: classical only
        (['( ~ ( ~ ( P & Q ) ) )'], '( P & Q )', True, False),                     # DNE instance: classical only
        (['( P v Q )'], '( ~ ( ~ ( P v Q ) ) )', True, True),                      # DNI instance: intuitionistic
        ([], '( ( ( ( P & Q ) > R ) > ( P & Q ) ) > ( P & Q ) )', True, False),   # Peirce instance: classical only
        (['( ( P & R ) > Q )', '( ~ Q )'], '( ~ ( P & R ) )', True, True),         # MT instance
        (['( ( ~ R ) > ( ~ ( P v Q ) ) )'], '( ( P v Q ) > R )', True, False),     # converse contraposition: classical only
        (['( ~ ( ( P v Q ) & R ) )'], '( ( ~ ( P v Q ) ) v ( ~ R ) )', True, False),
        (['( ~ ( ( P & Q ) v R ) )'], '( ( ~ ( P & Q ) ) & ( ~ R ) )', True, True),
        (['( ~ ( ( P v R ) > Q ) )'], '( ( P v R ) & ( ~ Q ) )', True, False),
        (['( ~ ( ( P v R ) > ( Q & S ) ) )'], '( ~ ( Q & S ) )', True, True),
        (['P'], 'Q', False, False),
        (['F'], '( Q & R )', True, True),
        ([], '( ~ ( ~ ( ( P & Q ) v ( ~ ( P & Q ) ) ) ) )', True, True),         # ~~LEM instance: intuitionistic
    ]
    bad = 0
    for pr, c, cl, it in cases:
        a, b = classical(pr, c), intuitionistic(pr, c)
        if (a, b) != (cl, it):
            bad += 1
            print('SELFTEST FAIL', pr, c, (a, b), 'expected', (cl, it))
    k1 = class_key(['( ( P & R ) > Q )', '( ~ Q )'], '( ~ ( P & R ) )')
    k2 = class_key(['( ~ S )', '( ( Q & P ) > S )'], '( ~ ( Q & P ) )')      # same sequent, premises swapped and renamed
    if k1 != k2:
        bad += 1; print('SELFTEST FAIL class_key', k1, k2)
    print('common selftest:', 'PASS' if not bad else f'FAIL {bad}')
    return bad == 0


if __name__ == '__main__':
    selftest()
