#!/usr/bin/env python3
"""blc.py -- a small binary lambda calculus (BLC, Tromp) toolchain for run kalmar-complexity.

Source language (.lam files)
----------------------------
    -- comment to the end of the line
    param x y ...          program parameters: lambda binders of the program, in this order
    name a b = expr        top-level definition (sugar for  name = \\a b. expr); continuation lines are indented
    main = expr            the program body, under all parameters and definitions
  expr ::= \\x y. e | e e | (e) | e $ e | let f a = e in e | #n | name
  (`$` is low-precedence right-associative application, `#n` is the Church numeral n, `let f a = e1 in e2` is
  `(\\f. e2) (\\a. e1)`.)

A program is the closed term  B1 (B2 (... (Bk main)))  where every binder Bi is a parameter  \\x. []  or a definition
(\\x. []) e  (so a shared definition costs its body once plus 4 bits plus its uses).  Parameters keep their order;
the optimiser may move a definition (to any place after everything it uses), inline it (substitute its body at every
use), or drop it if unused -- whatever gives the shortest BLC encoding.  Every such step is a beta-equivalence, and the
tests re-run the optimised term.

BLC:  lambda = 00, application = 01, de Bruijn variable i >= 1 = 1^i 0.  bits(program) = len(BLC(program)).

Evaluator
---------
A call-by-need (lazy Krivine / Sestoft) machine with an explicit stack, update frames and sharing; it computes weak
head normal forms; results are read out by applying them to fresh free variables ("markers") and recursing into the
arguments, which is how a normal form of a data term is computed (Scott / Church data are read back up to eta).
`Machine.beta` counts beta-reductions (a lambda consuming an argument, markers included).

Combinatory logic
-----------------
`to_cl` = bracket abstraction with Tromp's rules (Binary Lambda Calculus and Combinatory Logic, 2006/2018):
    1 \\x. S K M = S K      2 \\x. M = K M (x not in M)   3 \\x. x = S K K   4 \\x. M x = M (x not in M)
    5 \\x. x M x = \\x. S S K x M        6 \\x. M (N L) = \\x. S (K M) N L   (M, N combinators)
    7 \\x. M N L = \\x. S M (K L) N      8 \\x. M L (N L) = \\x. S M N L     (M, L / M, N combinators)
    9 \\x. M N = S (\\x. M) (\\x. N)
binary CL: S = 00, K = 01, application = 1 (prefix).  `CLMachine` is a graph reducer (S, K, sharing) with the same
marker read-out, used to check that a CL term computes what its lambda term computes.
"""
import re
import sys

sys.setrecursionlimit(1000000)

# =====================================================================================================================
# source language
# =====================================================================================================================

_TOK = re.compile(r"\s*(?:(--[^\n]*)|(\\|λ)|(\.)|(\()|(\))|(=)|(\$)|(#\d+)|([A-Za-z_][A-Za-z0-9_']*))")


class LamError(Exception):
    pass


def _tokens(s):
    out, i = [], 0
    s = s.rstrip()
    while i < len(s):
        m = _TOK.match(s, i)
        if not m or m.end() == i:
            if s[i:].strip() == '':
                break
            raise LamError(f'bad character at {s[i:i + 20]!r}')
        i = m.end()
        if m.group(1):
            continue
        tok = m.group(0).strip()
        if tok == 'λ':
            tok = '\\'
        out.append(tok)
    return out


class _Parser:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise LamError(f'expected {want!r}, got {tok!r} in {" ".join(self.t)[:200]}')
        self.i += 1
        return tok

    def expr(self):
        e = self.app()
        if self.peek() == '$':
            self.take('$')
            return ('a', e, self.expr())
        return e

    def lam(self):
        self.take('\\')
        names = []
        while self.peek() != '.':
            names.append(self.ident())
        self.take('.')
        if not names:
            raise LamError('lambda without variables')
        body = self.expr()
        for n in reversed(names):
            body = ('l', n, body)
        return body

    def let(self):
        self.take('let')
        name = self.ident()
        args = []
        while self.peek() != '=':
            args.append(self.ident())
        self.take('=')
        val = self.expr()
        self.take('in')
        body = self.expr()
        for a in reversed(args):
            val = ('l', a, val)
        return ('a', ('l', name, body), val)

    def ident(self):
        tok = self.take()
        if not re.match(r"[A-Za-z_][A-Za-z0-9_']*$", tok) or tok in ('let', 'in'):
            raise LamError(f'expected identifier, got {tok!r}')
        return tok

    def app(self):
        items = []
        while True:
            tok = self.peek()
            if tok is None or tok in (')', '$', 'in', '.', '='):
                break
            if tok == '\\':
                items.append(self.lam())
                break
            if tok == 'let':
                items.append(self.let())
                break
            items.append(self.atom())
        if not items:
            raise LamError(f'empty expression near {" ".join(self.t[self.i:self.i + 10])}')
        e = items[0]
        for x in items[1:]:
            e = ('a', e, x)
        return e

    def atom(self):
        tok = self.peek()
        if tok == '(':
            self.take('(')
            e = self.expr()
            self.take(')')
            return e
        if tok.startswith('#'):
            self.take()
            return church_named(int(tok[1:]))
        return ('v', self.ident())


def church_named(n):
    body = ('v', 'x#')
    for _ in range(n):
        body = ('a', ('v', 'f#'), body)
    return ('l', 'f#', ('l', 'x#', body))


def parse_expr(s):
    p = _Parser(_tokens(s))
    e = p.expr()
    if p.peek() is not None:
        raise LamError(f'trailing tokens: {p.t[p.i:p.i + 10]}')
    return e


class Program:
    """items: list of ('p', name) / ('d', name, expr); main: expr (named terms ('v',n) ('l',n,b) ('a',f,x))."""

    def __init__(self, items, main, name='program', beta=True):
        self.items, self.main, self.name, self.beta = items, main, name, beta

    @staticmethod
    def parse(src, name='program'):
        logical = []
        for raw in src.split('\n'):
            line = raw.split('--', 1)[0].rstrip() if '--' in raw else raw.rstrip()
            if not line.strip():
                continue
            if line[0] in ' \t':
                if not logical:
                    raise LamError('continuation line before any definition')
                logical[-1] += ' ' + line.strip()
            else:
                logical.append(line.strip())
        items, main, seen = [], None, set()
        for ln in logical:
            toks = _tokens(ln)
            if toks[0] == 'param':
                for n in toks[1:]:
                    if n in seen:
                        raise LamError(f'duplicate name {n}')
                    seen.add(n)
                    items.append(('p', n))
                continue
            if '=' not in toks:
                raise LamError(f'not a definition: {ln[:80]}')
            k = toks.index('=')
            head, body = toks[:k], toks[k + 1:]
            p = _Parser(body)
            e = p.expr()
            if p.peek() is not None:
                raise LamError(f'trailing tokens in {head[0]}: {p.t[p.i:p.i + 10]}')
            for a in reversed(head[1:]):
                e = ('l', a, e)
            if head[0] == 'main':
                if main is not None:
                    raise LamError('two mains')
                main = e
                continue
            if head[0] in seen:
                raise LamError(f'duplicate name {head[0]}')
            seen.add(head[0])
            items.append(('d', head[0], e))
        if main is None:
            raise LamError('no main')
        prog = Program(items, main, name)
        prog.rename_locals()
        prog.check_closed()
        return prog

    @staticmethod
    def load(path):
        with open(path) as fh:
            return Program.parse(fh.read(), name=path)

    # ---- hygiene ----
    def rename_locals(self):
        top = {it[1] for it in self.items}
        cnt = [0]

        def ren(t, env):
            if t[0] == 'v':
                return ('v', env.get(t[1], t[1]))
            if t[0] == 'a':
                return ('a', ren(t[1], env), ren(t[2], env))
            cnt[0] += 1
            new = f'{t[1]}~{cnt[0]}'
            env2 = dict(env)
            env2[t[1]] = new
            return ('l', new, ren(t[2], env2))
        self.items = [it if it[0] == 'p' else ('d', it[1], ren(it[2], {})) for it in self.items]
        self.main = ren(self.main, {})
        del top

    def check_closed(self):
        known = set()
        for it in self.items:
            if it[0] == 'd':
                bad = free_vars(it[2]) - known
                if bad:
                    raise LamError(f'{it[1]} uses undefined (or later) names {sorted(bad)}')
            known.add(it[1])
        bad = free_vars(self.main) - known
        if bad:
            raise LamError(f'main uses undefined names {sorted(bad)}')

    # ---- compilation ----
    def term(self, items=None):
        t = self.main
        for it in reversed(self.items if items is None else items):
            t = ('l', it[1], t) if it[0] == 'p' else ('a', ('l', it[1], t), it[2])
        return t

    def debruijn(self, items=None):
        t = db_eta(to_debruijn(self.term(items)))
        return db_eta(db_beta(t)) if self.beta else t

    def bits(self, items=None):
        return db_size_fast(self.debruijn(items))

    def copy(self):
        return Program(list(self.items), self.main, self.name, self.beta)

    # ---- optimisation ----
    def optimise(self, verbose=False, reorder=True, inline=True, eta=True, cse=True):
        """greedy: drop unused definitions, eta-reduce, inline where shorter, move definitions where shorter."""
        if eta:
            self.items = [it if it[0] == 'p' else ('d', it[1], eta_reduce(it[2])) for it in self.items]
            self.main = eta_reduce(self.main)
        self.drop_unused()
        best = self.bits()
        improved = True
        while improved:
            improved = False
            if inline:
                for name in [it[1] for it in self.items if it[0] == 'd']:
                    trial = self.copy()
                    trial.inline(name)
                    b = trial.bits()
                    if b < best:
                        if verbose:
                            print(f'  inline {name}: {best} -> {b}')
                        self.items, self.main, best, improved = trial.items, trial.main, b, True
            if reorder:
                for name in [it[1] for it in self.items if it[0] == 'd']:
                    pos = [i for i, it in enumerate(self.items) if it[1] == name][0]
                    it = self.items.pop(pos)
                    deps = free_vars(it[2])
                    lo = max([i + 1 for i, x in enumerate(self.items) if x[1] in deps] + [0])
                    users = [i for i, x in enumerate(self.items) if x[0] == 'd' and name in free_vars(x[2])]
                    hi = min(users + [len(self.items)])
                    cands = []
                    for p in range(lo, hi + 1):
                        items = self.items[:p] + [it] + self.items[p:]
                        cands.append((self.bits(items), p != pos, p, items))
                    cands.sort(key=lambda c: (c[0], c[1]))
                    b, _, p, items = cands[0]
                    if b < best:
                        if verbose:
                            print(f'  move {name}: {best} -> {b}')
                        best, improved = b, True
                    self.items = items
            if cse and not improved:
                b = self.cse(verbose=verbose)
                if b < best:
                    best, improved = b, True
        return best

    def cse(self, verbose=False, max_rounds=200):
        """sharing: a lambda-free subterm that occurs at least twice and mentions only top-level names (parameters,
        definitions; a bare name counts -- an alias for a far-away binder) becomes a new definition, placed where
        the encoding is shortest; kept only if the total gets shorter.  Greedy, repeated."""
        best = self.bits()
        tried = set()
        for _ in range(max_rounds):
            cands = self._cse_candidates()
            order = sorted(cands.items(), key=lambda kv: -(kv[1] * named_size_free(kv[0])))
            improved = False
            for sub, cnt in order:
                if (sub, best) in tried:
                    continue
                tried.add((sub, best))
                r = self._try_cse(sub, best)
                if r is not None:
                    b, items, main = r
                    if verbose:
                        print(f'  share {show_named(sub)[:60]} x{cnt}: {best} -> {b}')
                    self.items, self.main, best, improved = items, main, b, True
                    break
            if not improved:
                break
        return best

    def _cse_candidates(self):
        top = {it[1] for it in self.items}
        cands = {}
        bodies = [it[2] for it in self.items if it[0] == 'd'] + [self.main]

        def go(t):
            """-> (lambda-free?, free names)"""
            if t[0] == 'v':
                ok = t[1] in top
                if ok:
                    cands[t] = cands.get(t, 0) + 1
                return ok
            if t[0] == 'l':
                go(t[2])
                return False
            a, b = go(t[1]), go(t[2])
            if a and b:
                cands[t] = cands.get(t, 0) + 1
                return True
            return False
        for body in bodies:
            go(body)
        return {k: v for k, v in cands.items() if v >= 2}

    def _try_cse(self, sub, best):
        fv = free_vars(sub)
        k = 0
        names = {it[1] for it in self.items}
        while f'_s{k}' in names:
            k += 1
        name = f'_s{k}'
        lo = max([i + 1 for i, it in enumerate(self.items) if it[1] in fv] + [0])
        users = [i for i, it in enumerate(self.items) if it[0] == 'd' and contains_sub(it[2], sub)]
        hi = min(users + [len(self.items)])
        bestr = None
        for p in range(lo, hi + 1):
            items = self.items[:p] + [('d', name, sub)] + \
                [it if (it[0] == 'p') else ('d', it[1], replace_sub(it[2], sub, name)) for it in self.items[p:]]
            main = replace_sub(self.main, sub, name)
            b = Program(items, main, beta=self.beta).bits()
            if b < best and (bestr is None or b < bestr[0]):
                bestr = (b, items, main)
        return bestr

    def drop_unused(self):
        changed = True
        while changed:
            changed = False
            used = set(free_vars(self.main))
            for it in self.items:
                if it[0] == 'd':
                    used |= free_vars(it[2])
            keep = [it for it in self.items if it[0] == 'p' or it[1] in used]
            if len(keep) != len(self.items):
                self.items, changed = keep, True

    def inline(self, name):
        pos = [i for i, it in enumerate(self.items) if it[1] == name][0]
        it = self.items.pop(pos)
        body = it[2]
        self.items = [x if x[0] == 'p' else ('d', x[1], subst(x[2], name, body)) for x in self.items]
        self.main = subst(self.main, name, body)

    def definition_costs(self):
        """bits attributable to each binder (its 4-bit let overhead + body) in the current order (diagnostic)."""
        out = []
        depth_names = []
        for it in self.items:
            if it[0] == 'p':
                out.append((it[1], 2))
            else:
                out.append((it[1], 4 + named_size(it[2], depth_names[::-1])))
            depth_names.append(it[1])
        out.append(('main', named_size(self.main, depth_names[::-1])))
        return out


def contains_sub(t, sub):
    if t == sub:
        return True
    if t[0] == 'a':
        return contains_sub(t[1], sub) or contains_sub(t[2], sub)
    if t[0] == 'l':
        return contains_sub(t[2], sub)
    return False


def replace_sub(t, sub, name):
    """replace occurrences of a lambda-free subterm over top-level names (locals carry a ~ and never clash)"""
    if t == sub:
        return ('v', name)
    if t[0] == 'v':
        return t
    if t[0] == 'a':
        return ('a', replace_sub(t[1], sub, name), replace_sub(t[2], sub, name))
    return ('l', t[1], replace_sub(t[2], sub, name))

def named_size_free(t):
    """rough size of a term with free names counted as 4 bits (for ordering candidates)"""
    if t[0] == 'v':
        return 4
    if t[0] == 'a':
        return 2 + named_size_free(t[1]) + named_size_free(t[2])
    return 2 + named_size_free(t[2])


def show_named(t):
    if t[0] == 'v':
        return t[1].split('~')[0]
    if t[0] == 'a':
        return f'({show_named(t[1])} {show_named(t[2])})'
    return f'(\\{t[1].split("~")[0]}. {show_named(t[2])})'


def free_vars(t):
    out = set()
    stack = [(t, frozenset())]
    while stack:
        t, bound = stack.pop()
        if t[0] == 'v':
            if t[1] not in bound:
                out.add(t[1])
        elif t[0] == 'a':
            stack.append((t[1], bound))
            stack.append((t[2], bound))
        else:
            stack.append((t[2], bound | {t[1]}))
    return out


def subst(t, name, val):
    if t[0] == 'v':
        return val if t[1] == name else t
    if t[0] == 'a':
        return ('a', subst(t[1], name, val), subst(t[2], name, val))
    if t[1] == name:
        return t
    return ('l', t[1], subst(t[2], name, val))


def eta_reduce(t):
    if t[0] == 'v':
        return t
    if t[0] == 'a':
        return ('a', eta_reduce(t[1]), eta_reduce(t[2]))
    body = eta_reduce(t[2])
    if body[0] == 'a' and body[2] == ('v', t[1]) and t[1] not in free_vars(body[1]):
        return body[1]
    return ('l', t[1], body)


def named_size(t, outer=()):
    """BLC bits of a named term; `outer` = names bound outside, innermost first."""
    env = {}
    for k, n in enumerate(reversed(list(outer))):
        env.setdefault(n, []).append(k)
    depth = len(outer)
    total = 0
    stack = [(t, depth, None)]
    # iterative with explicit binder bookkeeping
    def go(t, depth):
        nonlocal total
        while True:
            tag = t[0]
            if tag == 'v':
                lst = env.get(t[1])
                if not lst:
                    raise LamError(f'free variable {t[1]}')
                total += depth - lst[-1] + 1
                return
            if tag == 'a':
                total += 2
                go(t[1], depth)
                t = t[2]
                continue
            total += 2
            env.setdefault(t[1], []).append(depth)
            go(t[2], depth + 1)
            env[t[1]].pop()
            return
    del stack
    go(t, depth)
    return total


# =====================================================================================================================
# de Bruijn terms and BLC
# =====================================================================================================================
# de Bruijn term: (0, i) variable (i >= 1), (1, body) lambda, (2, f, a) application

def to_debruijn(t, outer=()):
    env = {}
    for k, n in enumerate(reversed(list(outer))):
        env.setdefault(n, []).append(k)

    def go(t, depth):
        tag = t[0]
        if tag == 'v':
            lst = env.get(t[1])
            if not lst:
                raise LamError(f'free variable {t[1]}')
            return (0, depth - lst[-1])
        if tag == 'a':
            return (2, go(t[1], depth), go(t[2], depth))
        env.setdefault(t[1], []).append(depth)
        b = go(t[2], depth + 1)
        env[t[1]].pop()
        return (1, b)
    return go(t, len(outer))


def blc_encode(t):
    out = []

    def go(t):
        while True:
            if t[0] == 0:
                out.append('1' * t[1] + '0')
                return
            if t[0] == 1:
                out.append('00')
                t = t[1]
                continue
            out.append('01')
            go(t[1])
            t = t[2]
    go(t)
    return ''.join(out)


def blc_decode(bits):
    pos = [0]

    def go():
        i = pos[0]
        if bits[i] == '0':
            if bits[i + 1] == '0':
                pos[0] += 2
                return (1, go())
            pos[0] += 2
            f = go()
            return (2, f, go())
        j = i
        while bits[j] == '1':
            j += 1
        pos[0] = j + 1
        return (0, j - i)
    t = go()
    if pos[0] != len(bits):
        raise ValueError('trailing bits')
    return t


def db_size(t):
    return len(blc_encode(t))


def db_closed(t, depth=0):
    if t[0] == 0:
        return t[1] <= depth
    if t[0] == 1:
        return db_closed(t[1], depth + 1)
    return db_closed(t[1], depth) and db_closed(t[2], depth)


def db_show(t, names=None):
    """readable form with generated names (for debugging)."""
    names = list(names or [])
    letters = 'abcdefghijklmnopqrstuvwxyz'

    def nm(d):
        return letters[d % 26] + (str(d // 26) if d >= 26 else '')

    def go(t, depth):
        if t[0] == 0:
            k = depth - t[1]
            return nm(k) if k >= 0 else f'?{t[1]}'
        if t[0] == 1:
            return f'(\\{nm(depth)}. {go(t[1], depth + 1)})'
        return f'({go(t[1], depth)} {go(t[2], depth)})'
    return go(t, 0)


def db_eta(t):
    """eta-reduce everywhere: \\. M 1  ->  M (shifted down) when 1 is not free in M."""
    if t[0] == 0:
        return t
    if t[0] == 2:
        return (2, db_eta(t[1]), db_eta(t[2]))
    b = db_eta(t[1])
    if b[0] == 2 and b[2] == (0, 1) and not _db_has_free(b[1], 1):
        return db_shift(b[1], -1)
    return (1, b)


def db_beta(t, max_body=1200):
    """safe beta-reduction where it does not lengthen the term:  (\\. M) N -> M[N]  if the variable occurs at most once
    (and, when N is not a value, not under a lambda inside M, so no shared work is lost under call-by-need), or N is a
    variable.  Every step removes a lambda, so this terminates.  Bottom-up.  Redexes whose body M is larger than
    max_body bits (the top-level definition chain, which the optimiser handles by inlining) are not examined."""
    def go(u):
        """-> (term, size)"""
        if u[0] == 0:
            return u, u[1] + 1
        if u[0] == 1:
            b, sb = go(u[1])
            return (u if b is u[1] else (1, b)), sb + 2
        (f, sf), (a, sa) = go(u[1]), go(u[2])
        node = u if (f is u[1] and a is u[2]) else (2, f, a)
        size = sf + sa + 2
        if f[0] == 1 and sf <= max_body:
            cnt, under = _occ(f[1], 1, False)
            if a[0] == 0 or cnt == 0 or (cnt == 1 and (a[0] == 1 or not under)):
                r, sr = go(_subst(f[1], 1, a))
                if sr <= size:
                    return r, sr
        return node, size
    return go(t)[0]


def db_size_fast(u):
    total = 0
    stack = [u]
    while stack:
        x = stack.pop()
        if x[0] == 0:
            total += x[1] + 1
        elif x[0] == 1:
            total += 2
            stack.append(x[1])
        else:
            total += 2
            stack.append(x[1])
            stack.append(x[2])
    return total


def _occ(t, i, under_lam):
    """(occurrences of variable i, any of them under a lambda inside t)"""
    if t[0] == 0:
        return (1, under_lam) if t[1] == i else (0, False)
    if t[0] == 1:
        return _occ(t[1], i + 1, True)
    c1, u1 = _occ(t[1], i, under_lam)
    c2, u2 = _occ(t[2], i, under_lam)
    return c1 + c2, u1 or u2


def _subst(t, j, n):
    """t[j := n] for the binder being removed (indices above j drop by one); n is valid outside that binder"""
    if t[0] == 0:
        if t[1] == j:
            return db_shift(n, j - 1)
        return (0, t[1] - 1) if t[1] > j else t
    if t[0] == 1:
        return (1, _subst(t[1], j + 1, n))
    return (2, _subst(t[1], j, n), _subst(t[2], j, n))


def _db_has_free(t, i):
    if t[0] == 0:
        return t[1] == i
    if t[0] == 1:
        return _db_has_free(t[1], i + 1)
    return _db_has_free(t[1], i) or _db_has_free(t[2], i)


def db_shift(t, d, cutoff=0):
    if t[0] == 0:
        return (0, t[1] + d) if t[1] > cutoff else t
    if t[0] == 1:
        return (1, db_shift(t[1], d, cutoff + 1))
    return (2, db_shift(t[1], d, cutoff), db_shift(t[2], d, cutoff))


# =====================================================================================================================
# call-by-need machine
# =====================================================================================================================
# thunk = Python list [tag, a, b]:
#   UNEV: a = code, b = env      CLO: a = lambda node, b = env      NEU: a = head marker id, b = tuple of arg thunks
#   HOLE: under evaluation (black hole)
# env = None | (thunk, env)

UNEV, CLO, NEU, HOLE = 0, 1, 2, 3


class Loop(Exception):
    pass


class StepLimit(Exception):
    pass


class Machine:
    def __init__(self, limit=None):
        self.beta = 0
        self.limit = limit
        self._next_marker = 0

    # ---- values ----
    def closed(self, code):
        """thunk for a closed de Bruijn term"""
        if code[0] == 1:
            return [CLO, code, None]
        return [UNEV, code, None]

    def marker(self):
        self._next_marker += 1
        return [NEU, self._next_marker, ()]

    def markers(self, n):
        return [self.marker() for _ in range(n)]

    # ---- evaluation ----
    def apply(self, th, args=()):
        """evaluate thunk `th` applied to `args` (thunks) to weak head normal form.
        -> (NEU, head_id, args) or (CLO, lambda_node, env)"""
        stack = list(reversed(args))
        t = th[0]
        if t == CLO:
            return self.run(th[1], th[2], stack, 0)
        if t == NEU:
            return (NEU, th[1], th[2] + tuple(args))
        if t == HOLE:
            raise Loop()
        stack.append((th,))
        th[0] = HOLE
        return self.run(th[1], th[2], stack, 0)

    def run(self, code, env, stack, base):
        beta = 0
        limit = self.limit
        try:
            while True:
                tag = code[0]
                if tag == 2:                                    # application
                    a = code[2]
                    at = a[0]
                    if at == 0:                                 # variable argument: share its thunk
                        i = a[1]
                        e = env
                        while i > 1:
                            e = e[1]
                            i -= 1
                        stack.append(e[0])
                    elif at == 1:
                        stack.append([CLO, a, env])
                    else:
                        stack.append([UNEV, a, env])
                    code = code[1]
                elif tag == 1:                                  # lambda
                    if len(stack) == base:
                        return (CLO, code, env)
                    top = stack.pop()
                    if top.__class__ is tuple:                  # update frame
                        th = top[0]
                        th[0] = CLO
                        th[1] = code
                        th[2] = env
                        continue
                    env = (top, env)
                    code = code[1]
                    beta += 1
                    if limit is not None and beta > limit:
                        raise StepLimit()
                else:                                           # variable
                    i = code[1]
                    e = env
                    while i > 1:
                        e = e[1]
                        i -= 1
                    th = e[0]
                    t = th[0]
                    if t == CLO:
                        code = th[1]
                        env = th[2]
                    elif t == UNEV:
                        stack.append((th,))
                        th[0] = HOLE
                        code = th[1]
                        env = th[2]
                    elif t == NEU:
                        h = th[1]
                        args = th[2]
                        while True:
                            coll = []
                            while len(stack) > base and stack[-1].__class__ is list:
                                coll.append(stack.pop())
                            if coll:
                                args = args + tuple(coll)
                            if len(stack) > base:
                                u = stack.pop()[0]
                                u[0] = NEU
                                u[1] = h
                                u[2] = args
                                continue
                            return (NEU, h, args)
                    else:
                        raise Loop()
        finally:
            self.beta += beta
            if limit is not None:
                self.limit = limit - beta

    def force(self, th):
        return self.apply(th, ())

    # ---- full normal form (generic read-back) ----
    def normalize(self, th):
        """normal form (de Bruijn term) of thunk th, by read-back: a lambda is applied to a fresh variable."""
        root = [None]
        tasks = [(th, 0, root, 0)]
        levels = {}
        while tasks:
            th, lvl, slot, idx = tasks.pop()
            r = self.force(th)
            node_slot, node_idx = slot, idx
            while r[0] == CLO:
                v = self.marker()
                levels[v[1]] = lvl
                lvl += 1
                node = [1, None]
                node_slot[node_idx] = node
                node_slot, node_idx = node, 1
                r = self.run(r[1][1], (v, r[2]), [], 0)
                self.beta += 1
            h, args = r[1], r[2]
            if h not in levels:
                raise ValueError('normal form contains a foreign marker')
            head = [0, lvl - levels[h]]
            # build spine ((head a1) a2) ...
            cur = head
            nodes = []
            for a in args:
                cur = [2, cur, None]
                nodes.append(cur)
            node_slot[node_idx] = cur
            for n, a in zip(nodes, args):
                tasks.append((a, lvl, n, 2))
        return _freeze(root[0])


def _freeze(n):
    if n[0] == 0:
        return (0, n[1])
    if n[0] == 1:
        return (1, _freeze(n[1]))
    return (2, _freeze(n[1]), _freeze(n[2]))


# =====================================================================================================================
# data encodings (the interface; see README.md)
# =====================================================================================================================
#   booleans      true = \x y. x            false = \x y. y
#   numerals      Church: n = \f x. f^n x
#   lists         Scott:  nil = \n c. n     cons h t = \n c. c h t
#   pairs         \s. s a b
#   formulas      Scott, 6 constructors in the order  Atom k | F | Not A | And A B | Or A B | Imp A B, k = Scott
#                 numeral (zero = \z s. z, succ m = \z s. s m; P=0 Q=1 R=2 S=3):  Atom k = \t f n a o i. t k,  F = \t f n a o i. f,  Not A = \... n A,
#                 And A B = \... a A B,  Or A B = \... o A B,  Imp A B = \... i A B
#   sequent       pair (Scott list of premises, goal)
#   words         a token string t1 ... tm over an alphabet s1..sK is the Church word (a right fold)
#                 \e s1 ... sK. t1 (t2 (... (tm e))) ; a number token (N17, h3) is the letter applied to a Church
#                 numeral and then to the rest.

TRUE = (1, (1, (0, 2)))
FALSE = (1, (1, (0, 1)))
NIL = (1, (1, (0, 2)))


def enc_bool(b):
    return TRUE if b else FALSE


def enc_church(n):
    body = (0, 1)
    for _ in range(n):
        body = (2, (0, 2), body)
    return (1, (1, body))


def enc_list(items, enc=lambda x: x):
    t = NIL
    for x in reversed(list(items)):
        t = (1, (1, (2, (2, (0, 1), enc(x)), t)))
    return t


def enc_pair(a, b):
    return (1, (2, (2, (0, 1), a), b))


FCONS = ('atom', 'bot', 'not', 'and', 'or', 'imp')
ATOMS = 'PQRS'
ATOM_INDEX = 'scott'           # encoding of the atom index inside Atom k: 'scott' (used) or 'church'


def enc_scott(n):
    t = (1, (1, (0, 2)))                       # zero = \z s. z
    for _ in range(n):
        t = (1, (1, (2, (0, 1), t)))            # succ m = \z s. s m
    return t


def dec_scott(m, th):
    n = 0
    while True:
        z, s = m.marker(), m.marker()
        r = m.apply(th, [z, s])
        _expect_neu(r, 'scott numeral')
        if r[1] == z[1] and not r[2]:
            return n
        if r[1] != s[1] or len(r[2]) != 1:
            raise ValueError('not a Scott numeral')
        n += 1
        th = r[2][0]


def enc_atom_index(i):
    return enc_church(i) if ATOM_INDEX == 'church' else enc_scott(i)


def dec_atom_index(m, th):
    return dec_church(m, th) if ATOM_INDEX == 'church' else dec_scott(m, th)


def _lam(n, body):
    for _ in range(n):
        body = (1, body)
    return body


def enc_formula(f):
    """f: kalmar.py tuple ('atom','P') ('bot',) ('not',A) ('and',A,B) ('or',A,B) ('imp',A,B)  ->  Scott term with the
    6 constructors  Atom k | F | Not A | And A B | Or A B | Imp A B  (k = atom index, Scott numeral, P=0 .. S=3)."""
    k = f[0]
    if k == 'atom':
        return _lam(6, (2, (0, 6), enc_atom_index(ATOMS.index(f[1]))))
    if k == 'bot':
        return _lam(6, (0, 5))
    if k == 'not':
        return _lam(6, (2, (0, 4), enc_formula(f[1])))
    idx = {'and': 3, 'or': 2, 'imp': 1}[k]
    return _lam(6, (2, (2, (0, idx), enc_formula(f[1])), enc_formula(f[2])))


def enc_sequent(prem, goal):
    return enc_pair(enc_list(prem, enc_formula), enc_formula(goal))


def enc_word(tokens, alphabet, numbered=()):
    """Church word  \\e s1 ... sK. t1 (t2 (... (tm e))).  tokens: strings, or (letter, n) for a number token."""
    K = len(alphabet)
    pos = {}
    for i, s in enumerate(alphabet):
        pos.setdefault(s, i)          # a name used twice (the ND atom R and rule R): the first letter
    t = (0, K + 1)                    # e
    for tok in reversed(tokens):
        if isinstance(tok, tuple):
            arg = enc_atom_index(tok[1][1]) if isinstance(tok[1], tuple) else enc_church(tok[1])
            head = (2, (0, K - pos[tok[0]]), arg)
        else:
            head = (0, K - pos[tok])
        t = (2, head, t)
    return _lam(K + 1, t)


# ---- decoders (read-back through any machine with .apply / .marker) ----

def dec_bool(m, th):
    t, f = m.marker(), m.marker()
    r = m.apply(th, [t, f])
    _expect_neu(r, 'bool')
    if r[1] == t[1] and not r[2]:
        return True
    if r[1] == f[1] and not r[2]:
        return False
    raise ValueError('not a boolean')


def _expect_neu(r, what):
    if r[0] != NEU:
        raise ValueError(f'{what}: weak head normal form is a lambda, not data')


def dec_church(m, th):
    f, x = m.marker(), m.marker()
    n = 0
    r = m.apply(th, [f, x])
    while True:
        _expect_neu(r, 'numeral')
        if r[1] == x[1] and not r[2]:
            return n
        if r[1] != f[1] or len(r[2]) != 1:
            raise ValueError('not a Church numeral')
        n += 1
        r = m.force(r[2][0])


def dec_list(m, th, dec):
    out = []
    while True:
        n, c = m.marker(), m.marker()
        r = m.apply(th, [n, c])
        _expect_neu(r, 'list')
        if r[1] == n[1] and not r[2]:
            return out
        if r[1] != c[1] or len(r[2]) != 2:
            raise ValueError('not a Scott list')
        out.append(dec(m, r[2][0]))
        th = r[2][1]


def dec_pair(m, th, da, db):
    s = m.marker()
    r = m.apply(th, [s])
    _expect_neu(r, 'pair')
    if r[1] != s[1] or len(r[2]) != 2:
        raise ValueError('not a pair')
    return da(m, r[2][0]), db(m, r[2][1])


def dec_formula(m, th):
    ms = m.markers(6)
    r = m.apply(th, ms)
    _expect_neu(r, 'formula')
    ids = [x[1] for x in ms]
    if r[1] not in ids:
        raise ValueError('not a formula')
    k = ids.index(r[1])
    args = r[2]
    if len(args) != (1, 0, 1, 2, 2, 2)[k]:
        raise ValueError(f'formula constructor {FCONS[k]} with {len(args)} args')
    if k == 0:
        i = dec_atom_index(m, args[0])
        if i > 3:
            raise ValueError(f'atom index {i}')
        return ('atom', ATOMS[i])
    if k == 1:
        return ('bot',)
    if k == 2:
        return ('not', dec_formula(m, args[0]))
    return (FCONS[k], dec_formula(m, args[0]), dec_formula(m, args[1]))


def dec_word(m, th, alphabet, numbered=()):
    """numbered: letters that take an argument -> function(machine, thunk) giving the token text
    (a plain tuple of letters means: Church numeral appended to the letter, as N17)."""
    if not isinstance(numbered, dict):
        numbered = {x: (lambda m, t, x=x: f'{x}{dec_church(m, t)}') for x in numbered}
    me = m.marker()
    ms = m.markers(len(alphabet))
    ids = {x[1]: i for i, x in enumerate(ms)}
    out = []
    r = m.apply(th, [me] + ms)
    while True:
        _expect_neu(r, 'word')
        if r[1] == me[1] and not r[2]:
            return out
        if r[1] not in ids:
            raise ValueError('word: unknown head')
        letter = alphabet[ids[r[1]]]
        args = r[2]
        if letter in numbered:
            if len(args) != 2:
                raise ValueError(f'number token {letter} with {len(args)} args')
            out.append(numbered[letter](m, args[0]))
        else:
            if len(args) != 1:
                raise ValueError(f'token {letter} with {len(args)} args')
            out.append(letter)
        r = m.force(args[-1])


# =====================================================================================================================
# combinatory logic
# =====================================================================================================================
# CL term: ('S', 0) ('K', 0) ('v', level, fvmask) ('a', f, x, fvmask)

CS = ('S', 0)
CK = ('K', 0)


def capp(f, x):
    return ('a', f, x, f[-1] | x[-1])


def cvar(lvl):
    return ('v', lvl, 1 << lvl)


CI = capp(capp(CS, CK), CK)


def _abstract(x, M, comb_mode):
    bit = 1 << x

    def comb(t):
        return t[-1] == 0 if comb_mode == 'comb' else not (t[-1] & bit)

    while True:
        if M[0] == 'a' and M[1][0] == 'a' and M[1][1] is CS and M[1][2] is CK:      # 1
            return capp(CS, CK)
        if not (M[-1] & bit):                                                     # 2
            return capp(CK, M)
        if M[0] == 'v':                                                           # 3
            return CI
        f, a = M[1], M[2]
        if a[0] == 'v' and a[1] == x and not (f[-1] & bit):                       # 4
            return f
        if f[0] == 'a' and f[1][0] == 'v' and f[1][1] == x and a[0] == 'v' and a[1] == x:   # 5
            M = capp(capp(capp(capp(CS, CS), CK), cvar(x)), f[2])
            continue
        if a[0] == 'a' and comb(f) and comb(a[1]):                                # 6
            M = capp(capp(capp(CS, capp(CK, f)), a[1]), a[2])
            continue
        if f[0] == 'a' and comb(f[1]) and comb(a):                                # 7
            M = capp(capp(capp(CS, f[1]), capp(CK, a)), f[2])
            continue
        if f[0] == 'a' and a[0] == 'a' and comb(f[1]) and comb(a[1]) and f[2] == a[2]:   # 8
            M = capp(capp(capp(CS, f[1]), a[1]), f[2])
            continue
        return capp(capp(CS, _abstract(x, f, comb_mode)), _abstract(x, a, comb_mode))   # 9


def to_cl(db, comb_mode='comb'):
    def go(t, depth):
        if t[0] == 0:
            return cvar(depth - t[1])
        if t[0] == 2:
            return capp(go(t[1], depth), go(t[2], depth))
        body = go(t[1], depth + 1)
        return _abstract(depth, body, comb_mode)
    r = go(db, 0)
    if r[-1] != 0:
        raise ValueError('not closed')
    return r


def to_cl_best(db):
    a, b = to_cl(db, 'comb'), to_cl(db, 'xfree')
    return a if cl_bits(a) <= cl_bits(b) else b


def cl_encode(c):
    out = []

    def go(c):
        while True:
            if c[0] == 'S':
                out.append('00')
                return
            if c[0] == 'K':
                out.append('01')
                return
            out.append('1')
            go(c[1])
            c = c[2]
    go(c)
    return ''.join(out)


def cl_bits(c):
    return len(cl_encode(c))


def cl_from_bits(bits):
    pos = [0]

    def go():
        i = pos[0]
        if bits[i] == '1':
            pos[0] += 1
            f = go()
            return capp(f, go())
        pos[0] += 2
        return CS if bits[i + 1] == '0' else CK
    return go()


class CLMachine:
    """graph reduction of S/K terms with sharing; same read-out interface as Machine.
    node = [tag, a, b]: 0 S, 1 K, 2 app(a, b), 3 marker(a = id), 4 indirection(a)."""

    def __init__(self, limit=None):
        self.steps = 0
        self.limit = limit
        self._next = 0

    def load(self, c):
        memo = {}

        def go(c):
            key = id(c)
            if key in memo:
                return memo[key]
            if c[0] == 'S':
                n = [0, None, None]
            elif c[0] == 'K':
                n = [1, None, None]
            else:
                n = [2, go(c[1]), go(c[2])]
            memo[key] = n
            return n
        return go(c)

    def marker(self):
        self._next += 1
        return [3, self._next, None]

    def markers(self, k):
        return [self.marker() for _ in range(k)]

    def apply(self, node, args=()):
        for a in args:
            node = [2, node, a]
        return self.whnf(node)

    def force(self, node):
        return self.whnf(node)

    def whnf(self, node):
        stack = []
        cur = node
        steps = 0
        try:
            while True:
                t = cur[0]
                if t == 4:
                    cur = cur[1]
                    continue
                if t == 2:
                    f = cur[1]
                    while f[0] == 4:
                        f = f[1]
                    cur[1] = f
                    stack.append(cur)
                    cur = f
                    continue
                if t == 1:
                    if len(stack) < 2:
                        return ('stuck', cur, stack)
                    a1 = stack.pop()
                    a2 = stack.pop()
                    x = a1[2]
                    a2[0] = 4
                    a2[1] = x
                    a2[2] = None
                    cur = x
                    steps += 1
                    continue
                if t == 0:
                    if len(stack) < 3:
                        return ('stuck', cur, stack)
                    a1 = stack.pop()
                    a2 = stack.pop()
                    a3 = stack.pop()
                    f, g, x = a1[2], a2[2], a3[2]
                    a3[1] = [2, f, x]
                    a3[2] = [2, g, x]
                    cur = a3
                    steps += 1
                    if self.limit is not None and self.steps + steps > self.limit:
                        raise StepLimit()
                    continue
                # marker
                args = tuple(n[2] for n in reversed(stack))
                return (NEU, cur[1], args)
        finally:
            self.steps += steps


# =====================================================================================================================
# helpers for programs
# =====================================================================================================================

def optimise_best(path, verbose=False):
    """optimise with and without the beta pass; keep the shorter (ties: with beta)"""
    best = None
    for beta in (True, False):
        prog = Program.load(path)
        prog.beta = beta
        prog.optimise(verbose=verbose)
        if best is None or prog.bits() < best.bits():
            best = prog
    return best


def build(path, optimise=True, verbose=False):
    """parse + optimise a .lam file -> (Program, de Bruijn term, bit string)"""
    if optimise:
        prog = optimise_best(path, verbose=verbose)
    else:
        prog = Program.load(path)
    db = prog.debruijn()
    return prog, db, blc_encode(db)


def run_program(db, args, machine=None):
    """thunk of (program arg1 ... argk) -- not yet evaluated.  args: de Bruijn closed terms."""
    m = machine or Machine()
    t = db
    for a in args:
        t = (2, t, a)
    return m, m.closed(t)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['bits', 'build', 'show'])
    ap.add_argument('files', nargs='+')
    ap.add_argument('-v', action='store_true')
    ap.add_argument('--no-opt', action='store_true')
    a = ap.parse_args(argv)
    for f in a.files:
        prog, db, bits = build(f, optimise=not a.no_opt, verbose=a.v)
        cl = to_cl_best(db)
        print(f'{f}: BLC {len(bits)} bits, CL {cl_bits(cl)} bits')
        if a.cmd == 'show':
            for name, c in prog.definition_costs():
                print(f'   {name:12s} {c}')
        if a.cmd == 'build':
            out = f[:-4] + '.blc' if f.endswith('.lam') else f + '.blc'
            with open(out, 'w') as fh:
                fh.write(bits + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])


def reference_costs(prog):
    """diagnostic: total bits spent on references to each name, on lambdas and on applications, in the final term."""
    from collections import Counter
    t = prog.term()
    refs, cnt = Counter(), Counter()
    tot = {'lam': 0, 'app': 0}
    env = {}

    def go(t, depth):
        if t[0] == 'v':
            c = depth - env[t[1]][-1] + 1
            base = t[1].split('~')[0]
            refs[base] += c
            cnt[base] += 1
            return
        if t[0] == 'a':
            tot['app'] += 2
            go(t[1], depth)
            go(t[2], depth)
            return
        tot['lam'] += 2
        env.setdefault(t[1], []).append(depth)
        go(t[2], depth + 1)
        env[t[1]].pop()
    go(t, 0)
    return refs, cnt, tot
