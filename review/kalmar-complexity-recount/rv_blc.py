#!/usr/bin/env python3
"""Reviewer-owned BLC toolkit (review of run kalmar-complexity).  Independent of the executor's blc.py:

- `parse_bits(s)`: BLC bit string -> de Bruijn term  (lambda 00, application 01, variable i>=1 1^i 0); checks closedness.
- `M`: a call-by-need Krivine-style machine with update frames (own implementation), read-back through markers.
- encoders / decoders for the documented interface (README of programs/blc: Church booleans / numerals, Scott lists,
  pairs, Scott formulas Atom k|F|Not|And|Or|Imp with a Scott atom index, Church words over an alphabet).
- `to_cl(t)`: bracket abstraction with the nine rules the executor names (Tromp), own implementation; `cl_bits`.

Terms: ('v', i) 1-based de Bruijn, ('l', body), ('a', f, x).
"""
import sys
sys.setrecursionlimit(100000)

V, L, A = 'v', 'l', 'a'


def parse_bits(s):
    s = s.strip()
    pos = 0
    # iterative parser: explicit stack of pending constructors
    out_stack = []      # partially built nodes
    # use recursion-free approach with a work stack
    def parse_at(p, depth):
        # returns (term, newpos); recursive but terms are not that deep; use manual stack instead
        raise NotImplementedError
    # manual stack: frames are ('l',) waiting for body, ('a1',) waiting for fun, ('a2', f) waiting for arg
    frames = []
    depth = 0
    maxfree = 0
    res = None
    while True:
        if s[pos:pos + 2] == '00':
            pos += 2
            frames.append(('l',))
            depth += 1
            continue
        if s[pos:pos + 2] == '01':
            pos += 2
            frames.append(('a1',))
            continue
        # variable
        i = 0
        while s[pos] == '1':
            i += 1
            pos += 1
        assert s[pos] == '0', 'bad variable'
        pos += 1
        assert i >= 1
        if i > depth:
            maxfree = max(maxfree, i - depth)
        node = (V, i)
        # reduce frames
        while True:
            if not frames:
                res = node
                break
            fr = frames.pop()
            if fr[0] == 'l':
                depth -= 1
                node = (L, node)
                continue
            if fr[0] == 'a1':
                frames.append(('a2', node))
                node = None
                break
            if fr[0] == 'a2':
                node = (A, fr[1], node)
                continue
        if res is not None:
            break
    assert pos == len(s), f'trailing bits {len(s) - pos}'
    assert maxfree == 0, 'term not closed'
    return res


def to_bits(t):
    out = []
    st = [t]
    while st:
        x = st.pop()
        if x[0] == L:
            out.append('00'); st.append(x[1])
        elif x[0] == A:
            out.append('01'); st.append(x[2]); st.append(x[1])
        else:
            out.append('1' * x[1] + '0')
    return ''.join(out)


def size_bits(t):
    n = 0
    st = [t]
    while st:
        x = st.pop()
        if x[0] == L:
            n += 2; st.append(x[1])
        elif x[0] == A:
            n += 2; st.append(x[1]); st.append(x[2])
        else:
            n += x[1] + 1
    return n


# ------------------------------------------------------------------------------------------------ machine

class Th:
    __slots__ = ('t', 'e', 'v')

    def __init__(self, t, e, v=None):
        self.t, self.e, self.v = t, e, v


LAMV, NEU = 0, 1


class M:
    """call-by-need machine.  values: (LAMV, body, env) | (NEU, marker_id, args_tuple).  env: (thunk, parent) | None"""

    def __init__(self, limit=50_000_000):
        self.beta = 0
        self.nm = 0
        self.limit = limit

    def marker(self):
        self.nm += 1
        return Th(None, None, (NEU, self.nm, ()))

    def run(self, t, e, stack, val=None):
        beta = self.beta
        limit = self.limit
        while True:
            if val is None:
                tag = t[0]
                if tag == A:
                    stack.append((0, Th(t[2], e)))
                    t = t[1]
                    continue
                if tag == V:
                    en = e
                    for _ in range(t[1] - 1):
                        en = en[1]
                    th = en[0]
                    if th.v is None:
                        stack.append((1, th))
                        t, e = th.t, th.e
                        continue
                    val = th.v
                else:
                    val = (LAMV, t[1], e)
            # return val
            while True:
                if not stack:
                    self.beta = beta
                    return val
                kind, th = stack.pop()
                if kind == 1:
                    th.v = val
                    th.t = th.e = None
                    continue
                if val[0] == LAMV:
                    t, e = val[1], (th, val[2])
                    beta += 1
                    if beta > limit:
                        raise RuntimeError('step limit')
                    val = None
                    break
                val = (NEU, val[1], val[2] + (th,))

    def force(self, th):
        if th.v is not None:
            return th.v
        v = self.run(th.t, th.e, [(1, th)])
        return v

    def apply(self, th, args):
        stack = [(0, a) for a in reversed(args)]
        if th.v is None:
            stack.append((1, th))
            return self.run(th.t, th.e, stack)
        return self.run(None, None, stack, th.v)

    def closed(self, t):
        return Th(t, None)


def neu(r, what):
    if r[0] != NEU:
        raise ValueError(what + ': WHNF is a lambda')
    return r


# ------------------------------------------------------------------------------------------------ encoders

def lam(n, b):
    for _ in range(n):
        b = (L, b)
    return b


def app(*xs):
    t = xs[0]
    for x in xs[1:]:
        t = (A, t, x)
    return t


TRUE = lam(2, (V, 2))
FALSE = lam(2, (V, 1))


def e_bool(b):
    return TRUE if b else FALSE


def e_church(n):
    b = (V, 1)
    for _ in range(n):
        b = app((V, 2), b)
    return lam(2, b)


def e_scott(n):                 # zero = \z s. z ; succ m = \z s. s m
    t = lam(2, (V, 2))
    for _ in range(n):
        t = lam(2, app((V, 1), t))
    return t


def e_list(xs, enc):            # nil = \n c. n ; cons h t = \n c. c h t
    t = lam(2, (V, 2))
    for x in reversed(list(xs)):
        t = lam(2, app((V, 1), enc(x), t))
    return t


def e_pair(a, b):
    return lam(1, app((V, 1), a, b))


def e_formula(f):               # \t f n a o i.  (binders 6..1)
    k = f[0]
    if k == 'atom':
        return lam(6, app((V, 6), e_scott('PQRS'.index(f[1]))))
    if k == 'bot':
        return lam(6, (V, 5))
    if k == 'not':
        return lam(6, app((V, 4), e_formula(f[1])))
    i = {'and': 3, 'or': 2, 'imp': 1}[k]
    return lam(6, app((V, i), e_formula(f[1]), e_formula(f[2])))


def e_sequent(prem, goal):
    return e_pair(e_list(prem, e_formula), e_formula(goal))


def e_word(tokens, alphabet):
    """\\e s1..sK. t1 (t2 (... e)); a token is a letter or (letter, numeral-term)"""
    K = len(alphabet)
    pos = {}
    for i, s in enumerate(alphabet):
        pos.setdefault(s, i)
    t = (V, K + 1)
    for tok in reversed(tokens):
        if isinstance(tok, tuple):
            head = app((V, K - pos[tok[0]]), tok[1])
        else:
            head = (V, K - pos[tok])
        t = app(head, t)
    return lam(K + 1, t)


# ------------------------------------------------------------------------------------------------ decoders

def d_bool(m, th):
    t, f = m.marker(), m.marker()
    r = neu(m.apply(th, [t, f]), 'bool')
    if r[2]:
        raise ValueError('bool with args')
    if r[1] == t.v[1]:
        return True
    if r[1] == f.v[1]:
        return False
    raise ValueError('not a bool')


def d_church(m, th):
    f, x = m.marker(), m.marker()
    r = neu(m.apply(th, [f, x]), 'church')
    n = 0
    while True:
        if r[1] == x.v[1] and not r[2]:
            return n
        if r[1] != f.v[1] or len(r[2]) != 1:
            raise ValueError('not church')
        n += 1
        r = neu(m.force(r[2][0]), 'church')


def d_scott(m, th):
    n = 0
    while True:
        z, s = m.marker(), m.marker()
        r = neu(m.apply(th, [z, s]), 'scott')
        if r[1] == z.v[1] and not r[2]:
            return n
        if r[1] != s.v[1] or len(r[2]) != 1:
            raise ValueError('not scott')
        n += 1
        th = r[2][0]


def d_list(m, th, dec):
    out = []
    while True:
        n, c = m.marker(), m.marker()
        r = neu(m.apply(th, [n, c]), 'list')
        if r[1] == n.v[1] and not r[2]:
            return out
        if r[1] != c.v[1] or len(r[2]) != 2:
            raise ValueError('not a list')
        out.append(dec(m, r[2][0]))
        th = r[2][1]


def d_pair(m, th, da, db):
    s = m.marker()
    r = neu(m.apply(th, [s]), 'pair')
    if r[1] != s.v[1] or len(r[2]) != 2:
        raise ValueError('not a pair')
    return da(m, r[2][0]), db(m, r[2][1])


FC = ('atom', 'bot', 'not', 'and', 'or', 'imp')


def d_formula(m, th):
    ms = [m.marker() for _ in range(6)]
    r = neu(m.apply(th, ms), 'formula')
    ids = [x.v[1] for x in ms]
    k = ids.index(r[1])
    args = r[2]
    assert len(args) == (1, 0, 1, 2, 2, 2)[k], 'formula arity'
    if k == 0:
        i = d_scott(m, args[0])
        return ('atom', 'PQRS'[i])
    if k == 1:
        return ('bot',)
    if k == 2:
        return ('not', d_formula(m, args[0]))
    return (FC[k], d_formula(m, args[0]), d_formula(m, args[1]))


def d_word(m, th, alphabet, numbered):
    """numbered: {letter: decoder} for letters that take a numeral argument -> list of tokens (str or (letter, n))"""
    e = m.marker()
    ls = [m.marker() for _ in alphabet]
    ids = {x.v[1]: i for i, x in enumerate(ls)}
    r = neu(m.apply(th, [e] + ls), 'word')
    out = []
    while True:
        if r[1] == e.v[1] and not r[2]:
            return out
        i = ids[r[1]]
        letter = alphabet[i]
        if letter in numbered:
            assert len(r[2]) == 2, ('numbered letter arity', letter, len(r[2]))
            out.append((letter, numbered[letter](m, r[2][0])))
            r = neu(m.force(r[2][1]), 'word')
        else:
            assert len(r[2]) == 1, ('letter arity', letter, len(r[2]))
            out.append(letter)
            r = neu(m.force(r[2][0]), 'word')


# ------------------------------------------------------------------------------------------------ combinatory logic

def _free(t, i):
    """does de Bruijn index i (1-based at this level) occur free in t?  CL nodes: ('S',) ('K',) ('a', f, x)"""
    st = [(t, i)]
    while st:
        x, j = st.pop()
        k = x[0]
        if k == V:
            if x[1] == j:
                return True
        elif k == L:
            st.append((x[1], j + 1))
        elif k == A:
            st.append((x[1], j)); st.append((x[2], j))
    return False


def _shift_down(t, cut=1):
    """remove binder: indices > cut decrease by one (t must not contain index cut free)."""
    k = t[0]
    if k == V:
        return (V, t[1] - 1) if t[1] > cut else t
    if k == L:
        return (L, _shift_down(t[1], cut + 1))
    if k == A:
        return (A, _shift_down(t[1], cut), _shift_down(t[2], cut))
    return t


S_, K_ = ('S',), ('K',)


def is_comb(t):
    """closed combinator term (no variables)"""
    st = [t]
    while st:
        x = st.pop()
        if x[0] == V or x[0] == L:
            return False
        if x[0] == A:
            st.append(x[1]); st.append(x[2])
    return True


def abstract(t, mode='comb'):
    """\\x. t  where t is a CL-with-variables term (variables are de Bruijn indices relative to the binder: 1 = x).
    Tromp's rules 1-9 (as listed in the executor's docstring).  Returns a term with indices shifted down."""
    # 1  \x. S K M = S K
    if t[0] == A and t[1][0] == A and t[1][1] == S_ and t[1][2] == K_:
        return (A, S_, K_)
    # 2  \x. M = K M  (x not in M)
    if not _free(t, 1):
        return (A, K_, _shift_down(t))
    # 3  \x. x = S K K
    if t == (V, 1):
        return (A, (A, S_, K_), K_)
    if t[0] == A:
        Mf, Nx = t[1], t[2]
        # 4  \x. M x = M  (x not in M)
        if Nx == (V, 1) and not _free(Mf, 1):
            return _shift_down(Mf)
        # 5  \x. x M x = \x. S S K x M
        if Mf[0] == A and Mf[1] == (V, 1) and Nx == (V, 1):
            Mm = Mf[2]
            return abstract((A, (A, (A, (A, S_, S_), K_), (V, 1)), Mm), mode)
        # 6  \x. M (N L) = \x. S (K M) N L   (M, N combinators)
        cb = is_comb if mode == 'comb' else (lambda u: not _free(u, 1))
        if Nx[0] == A and cb(Mf) and cb(Nx[1]):
            Lt = Nx[2]
            return abstract((A, (A, (A, S_, (A, K_, Mf)), Nx[1]), Lt), mode)
        if Mf[0] == A:
            M1, N1, Lt = Mf[1], Mf[2], Nx
            # 7  \x. M N L = \x. S M (K L) N   (M, L combinators)
            if cb(M1) and cb(Lt):
                return abstract((A, (A, (A, S_, M1), (A, K_, Lt)), N1), mode)
            # 8  \x. M L (N L) = \x. S M N L   (M, N combinators)  -- pattern  (M L) (N L)
            if Nx[0] == A and N1 == Nx[2] and cb(M1) and cb(Nx[1]):
                return abstract((A, (A, (A, S_, M1), Nx[1]), N1), mode)
        # 9  \x. M N = S (\x. M) (\x. N)
        return (A, (A, S_, abstract(Mf, mode)), abstract(Nx, mode))
    raise ValueError('abstract: unexpected ' + str(t[0]))


def to_cl(t, mode='comb'):
    """lambda term (de Bruijn) -> CL term; innermost lambdas first."""
    k = t[0]
    if k == V:
        return t
    if k == A:
        return (A, to_cl(t[1], mode), to_cl(t[2], mode))
    if k == L:
        return abstract(to_cl(t[1], mode), mode)
    return t


def to_cl_min(t):
    a, b = to_cl(t, 'comb'), to_cl(t, 'xfree')
    return a if cl_bits(a) <= cl_bits(b) else b


def cl_bits(t):
    n = 0
    st = [t]
    while st:
        x = st.pop()
        if x == S_ or x == K_:
            n += 2
        elif x[0] == A:
            n += 1; st.append(x[1]); st.append(x[2])
        else:
            raise ValueError('variable left in CL term')
    return n


def cl_to_lambda(t):
    """S = \\x y z. x z (y z), K = \\x y. x  -> lambda term (to evaluate a CL term with the lambda machine)."""
    Sl = lam(3, app((V, 3), (V, 1), app((V, 2), (V, 1))))
    Kl = lam(2, (V, 2))
    def go(x):
        if x == S_:
            return Sl
        if x == K_:
            return Kl
        return (A, go(x[1]), go(x[2]))
    return go(t)
