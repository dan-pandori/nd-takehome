#!/usr/bin/env python3
"""K12-Kalmár (sl) as an explicit per-step policy: proof state -> next action (run kalmar-complexity).

The state is what kalmar-pretrain's models see (`state_env`, canonical names): the hypotheses in scope, in order, as
`name : formula`, then `⊢ goal`.  No history.  This module computes the builder's next action from that alone, and
`test_policy.py` checks it against `kalmar.build(…, 'sl')` on every state of the test theorems.

How the state determines the step:
- **Frames from names.**  Canonical names are `max index in scope + 1`; a box-opening `have n_k … ( fun ( n_k+1 : A )`
  leaves n_k out of scope until the box closes, so every missing index j < max marks an open box whose binder is
  n_{j+1}.  Frames = top + one per gap, each holding its binder and the lines after it.
- **Phase** from the top frame and the frame stack: premise lines; excluded middle for each atom (9 fixed steps inside
  two boxes); splits (∨E on X ∨ ¬X, atoms in the order P Q R S); leaf.
- **Leaf** (all atoms split; valuation = the split binders).  Target: ¬p for the first false premise p (ex falso),
  else the goal.  Outside lemma boxes the next step is the first node, in post-order, of Kalmár's lemma recursion
  whose line is not in scope (memo = lookup in scope, innermost frame first, first line of that formula).  Inside a
  lemma box the steps are fixed by the box type, read off the binder, the goal, truth values and the box's lines.
"""
import itertools

ATOMS = ('P', 'Q', 'R', 'S')
BOT = ('bot',)
CON = {'∧': 'and', '∨': 'or', '→': 'imp'}
SYM = {v: k for k, v in CON.items()}


# ---------------------------------------------------------------- formulas
def parse_f(t, i):
    """state formula tokens t[i:] -> (formula, next index).  atom | False | ( ¬ A ) | ( A op B )."""
    x = t[i]
    if x in ATOMS:
        return ('atom', x), i + 1
    if x == 'False':
        return BOT, i + 1
    assert x == '(', (t, i)
    if t[i + 1] == '¬':
        a, j = parse_f(t, i + 2)
        assert t[j] == ')'
        return ('not', a), j + 1
    a, j = parse_f(t, i + 1)
    op = CON[t[j]]
    b, k = parse_f(t, j + 1)
    assert t[k] == ')'
    return (op, a, b), k + 1


def ftok(f):
    k = f[0]
    if k == 'atom':
        return [f[1]]
    if k == 'bot':
        return ['False']
    if k == 'not':
        return ['(', '¬'] + ftok(f[1]) + [')']
    return ['('] + ftok(f[1]) + [SYM[k]] + ftok(f[2]) + [')']


def val(f, v):
    k = f[0]
    if k == 'atom':
        return v[f[1]]
    if k == 'bot':
        return False
    if k == 'not':
        return not val(f[1], v)
    a, b = val(f[1], v), val(f[2], v)
    return (a and b) if k == 'and' else (a or b) if k == 'or' else ((not a) or b)


def atoms_of(fs):
    seen = set()

    def go(f):
        if f[0] == 'atom':
            seen.add(f[1])
        else:
            for g in f[1:]:
                go(g)
    for f in fs:
        go(f)
    return [a for a in ATOMS if a in seen]


def neg(f):
    return ('not', f)


def em(x):
    return ('or', ('atom', x), neg(('atom', x)))


# ---------------------------------------------------------------- state
def parse_state(toks):
    """-> (premises [formula], hyps [(index, formula)] for the n-names in order, goal)."""
    assert toks[0] == '<st>' and toks[-1] == '<act>'
    body = toks[1:-1]
    k = body.index('⊢')
    goal, j = parse_f(body, k + 1)
    assert j == len(body)
    prem, hyps = [], []
    i = 0
    while i < k:
        name = body[i]
        assert body[i + 1] == ':'
        f, i = parse_f(body, i + 2)
        if name[0] == 'h':
            prem.append(f)
        else:
            hyps.append((int(name[1:]), f))
        if body[i] == '<nl>':
            i += 1
    return prem, hyps, goal


class Frame:
    __slots__ = ('binder', 'lines')       # binder: (index, formula) or None for top; lines: [(index, formula)]

    def __init__(self, binder):
        self.binder, self.lines = binder, []


def frames_of(hyps):
    idx = {i for i, _ in hyps}
    top = max(idx) if idx else 0
    binders = {j + 1 for j in range(1, top) if j not in idx}
    if 1 not in idx and 2 in idx:            # a box opened by the very first action (no premises)
        binders.add(2)
    fr = [Frame(None)]
    for i, f in hyps:
        if i in binders:
            fr.append(Frame((i, f)))
        else:
            fr[-1].lines.append((i, f))
    return fr


# ---------------------------------------------------------------- actions (lean_seq text)
def n(i):
    return f'n{i}'


def have(k, f, term):
    return ['have', n(k), ':'] + ftok(f) + [':='] + term + [';']


def have_box(k, f, a):
    return ['have', n(k), ':'] + ftok(f) + [':=', '(', 'fun', '(', n(k + 1), ':'] + ftok(a) + [')', '=>', 'by']


def have_ore(k, f, maj, a):
    return ['have', n(k), ':'] + ftok(f) + [':=', 'Or.elim', n(maj), '(', 'fun', '(', n(k + 1), ':'] + ftok(a) + \
        [')', '=>', 'by']


def exact(i):
    return ['exact', n(i)]


# ---------------------------------------------------------------- the policy
class Policy:
    def __init__(self, toks):
        self.prem, self.hyps, self.goal = parse_state(toks)
        self.fr = frames_of(self.hyps)
        self.k = (max(i for i, _ in self.hyps) if self.hyps else 0) + 1      # the next canonical name

    def lookup(self, f, skip=0):
        """the line cited for f: innermost frame first (optionally skipping the innermost `skip` frames), first line
        of that formula in the frame (binder first)."""
        for fr in reversed(self.fr[:len(self.fr) - skip] if skip else self.fr):
            for i, g in ([fr.binder] if fr.binder else []) + fr.lines:
                if g == f:
                    return i
        return None

    def act(self):
        top = self.fr[0]
        m = len(self.prem)
        if len(self.fr) == 1 and len(top.lines) < m:                          # premise lines
            j = len(top.lines)
            return have(self.k, self.prem[j], [f'h{j + 1}']), 'pr'
        T = top.lines[m:]
        lem_atoms, t = [], 0                                                   # complete X ∨ ¬X pairs at the top
        while t + 1 < len(T) and T[t + 1][1][0] == 'or' and _atom(T[t + 1][1]) is not None \
                and T[t][1] == neg(neg(T[t + 1][1])):
            lem_atoms.append(_atom(T[t + 1][1]))
            t += 2
        rest = T[t:]
        if len(self.fr) == 1:
            atoms = atoms_of(self.prem + [self.goal])
            need = [x for x in atoms if self.lookup(em(x)) is None]
            if need:                                                           # excluded middle, at the top level
                x = need[0]
                if rest and rest[-1][1] == neg(neg(em(x))):
                    return have(self.k, em(x), ['Classical.byContradiction', '(', 'fun', 'hh', '=>',
                                                n(rest[-1][0]), 'hh', ')']), 'lem'
                return have_box(self.k, neg(neg(em(x))), neg(em(x))), 'lem'
        b1 = self.fr[1].binder if len(self.fr) > 1 else None
        if b1 is not None and b1[1][0] == 'not' and b1[1][1][0] == 'or' and b1[1] == neg(em(_atom(b1[1][1][1]))) \
                and not top.lines[m:][len(lem_atoms) * 2:]:
            return self.lem_box()
        atoms = sorted(set(atoms_of(self.prem)) | set(lem_atoms), key=ATOMS.index) if len(self.fr) > 1 else \
            atoms_of(self.prem + [self.goal])
        # split frames: fr[1..s], binder of fr[j] a literal of atoms[j-1] (lemma boxes come only after all splits)
        s = 0
        while s < len(atoms) and s + 1 < len(self.fr):
            b = self.fr[s + 1].binder[1]
            x = atoms[s]
            if b in (('atom', x), neg(('atom', x))):
                s += 1
            else:
                break
        if s < len(atoms):                                                     # split phase
            assert len(self.fr) == s + 1
            fl = self.fr[s].lines if s else top.lines[m + 2 * len(lem_atoms):]
            if fl:
                return exact(fl[-1][0]), ('close:split' if s else 'end')
            x = atoms[s]
            return have_ore(self.k, self.goal, self.lookup(em(x)), ('atom', x)), 'split'
        v = {}
        for j in range(s):
            b = self.fr[j + 1].binder[1]
            v[atoms[j]] = b[0] == 'atom'
        self.v = v
        self.leaf = s                                                          # index of the leaf frame
        if len(self.fr) > s + 1:
            return self.lemma_box()
        return self.leaf_step()

    # -- excluded middle inside its two boxes (9 fixed steps)
    def lem_box(self):
        outer = self.fr[1]
        x = _atom(outer.binder[1][1])
        X = ('atom', x)
        if len(self.fr) == 3:                                                  # inner box: binder X
            L = self.fr[2].lines
            if not L:
                return have(self.k, em(x), ['Or.inl', n(self.fr[2].binder[0])]), 'lem'
            if len(L) == 1:
                return have(self.k, BOT, [n(outer.binder[0]), n(L[0][0])]), 'lem'
            return exact(L[-1][0]), 'close:lem'
        L = outer.lines
        if not L:
            return have_box(self.k, neg(X), X), 'lem'
        if len(L) == 1:
            return have(self.k, em(x), ['Or.inr', n(L[0][0])]), 'lem'
        if len(L) == 2:
            return have(self.k, BOT, [n(outer.binder[0]), n(L[1][0])]), 'lem'
        return exact(L[-1][0]), 'close:lem'

    # -- the leaf frame: Kalmár's lemma, post-order, memo
    def tgt(self, f):
        return f if val(f, self.v) else neg(f)

    def nxt(self, f):
        """the first step of lit(f) not yet taken, or None if f's line (or its negation's) is in scope."""
        v = self.v
        t = val(f, v)
        if self.lookup(self.tgt(f)) is not None:
            return None
        k = f[0]
        K = self.k
        if k == 'atom':
            raise AssertionError('atom not in scope')
        if k == 'bot':
            return have_box(K, neg(BOT), BOT), 'leaf:bot-'
        if k == 'not':
            r = self.nxt(f[1])
            if t or r is not None:
                return r
            return have_box(K, neg(f), neg(f[1])), 'leaf:not+'
        x, y = f[1], f[2]
        vx, vy = val(x, v), val(y, v)
        if k == 'and':
            if t:
                r = self.nxt(x) or self.nxt(y)
                return r or (have(K, f, ['⟨', n(self.lookup(x)), ',', n(self.lookup(y)), '⟩']), 'leaf:and+')
            r = self.nxt(x) if not vx else self.nxt(y)
            return r or (have_box(K, neg(f), f), 'leaf:and-')
        if k == 'or':
            if t:
                if vx:
                    return self.nxt(x) or (have(K, f, ['Or.inl', n(self.lookup(x))]), 'leaf:or+')
                return self.nxt(y) or (have(K, f, ['Or.inr', n(self.lookup(y))]), 'leaf:or+')
            r = self.nxt(x) or self.nxt(y)
            return r or (have_box(K, neg(f), f), 'leaf:or-')
        if vy:
            return self.nxt(y) or (have_box(K, f, x), 'leaf:imp+B')
        if not vx:
            return self.nxt(x) or (have_box(K, f, x), 'leaf:imp+A')
        r = self.nxt(x) or self.nxt(y)
        return r or (have_box(K, neg(f), f), 'leaf:imp-')

    def leaf_step(self):
        v, L = self.v, self.fr[self.leaf]
        lines = L.lines if self.leaf else L.lines[len(self.prem):]           # atom-free sequent: leaf at the top
        g = self.goal
        fp = next((i for i, p in enumerate(self.prem) if not val(p, v)), None)
        if fp is not None:                                                     # ex falso
            p = self.prem[fp]
            r = self.nxt(p)
            if r is not None:
                return r
            fl = [i for i, (_, f) in enumerate(lines) if f == BOT]
            if not fl:
                return have(self.k, BOT, [n(self.lookup(neg(p))), n(self.fr[0].lines[fp][0])]), 'efq'
            if g == BOT:
                return exact(lines[-1][0]), ('close:split' if self.leaf else 'end')
            if any(f == g for _, f in lines[fl[0] + 1:]):
                return exact(lines[-1][0]), ('close:split' if self.leaf else 'end')
            return have(self.k, g, [n(lines[fl[0]][0]), '.elim']), 'efq'
        r = self.nxt(g)
        if r is not None:
            return r
        i = self.lookup(g)
        last = L.lines[-1][0] if L.lines else (L.binder[0] if L.binder else None)   # the frame's last statement
        if i == last:
            return exact(i), ('close:split' if self.leaf else 'end')
        return have(self.k, g, [n(i)]), 'reit'

    # -- inside a lemma box: fixed steps by box type
    def lemma_box(self):
        v, K = self.v, self.k
        B = self.fr[-1]
        bi, f = B.binder
        Ls = B.lines
        g = self.goal
        inner = len(self.fr) > self.leaf + 2                                  # inside an or- box's Or.elim branch
        if inner:
            if not Ls:
                return have(K, BOT, [n(self.lookup(neg(f))), n(bi)]), 'leaf:or-'
            return exact(Ls[-1][0]), 'close:leaf:or-'
        if g == BOT and self.lookup(neg(f)) is None:                          # ¬I box proving ¬f
            k = f[0]
            if k == 'bot':
                return exact(bi), 'close:leaf:bot-'
            if k == 'not':
                if not Ls:
                    return have(K, BOT, [n(bi), n(self.lookup(f[1]))]), 'leaf:not+'
                return exact(Ls[-1][0]), 'close:leaf:not+'
            if k == 'and':
                if not Ls:
                    if not val(f[1], v):
                        return have(K, f[1], [n(bi), '.1']), 'leaf:and-'
                    return have(K, f[2], [n(bi), '.2']), 'leaf:and-'
                if len(Ls) == 1:
                    c = Ls[0]
                    return have(K, BOT, [n(self.lookup(neg(c[1]))), n(c[0])]), 'leaf:and-'
                return exact(Ls[-1][0]), 'close:leaf:and-'
            if k == 'or':
                if not Ls:
                    return have_ore(K, BOT, bi, f[1]), 'leaf:or-'
                return exact(Ls[-1][0]), 'close:leaf:or-'
            if k == 'imp':
                if not Ls:
                    return have(K, f[2], [n(bi), n(self.lookup(f[1]))]), 'leaf:imp-'
                if len(Ls) == 1:
                    c = Ls[0]
                    return have(K, BOT, [n(self.lookup(neg(c[1]))), n(c[0])]), 'leaf:imp-'
                return exact(Ls[-1][0]), 'close:leaf:imp-'
            raise AssertionError(f'box binder {f}')
        if val(g, v):                                                          # →I box, consequent true
            if not Ls:
                return have(K, g, [n(self.lookup(g, skip=1))]), 'leaf:imp+B'
            return exact(Ls[-1][0]), 'close:leaf:imp+B'
        if not Ls:                                                             # →I box, antecedent false
            return have(K, BOT, [n(self.lookup(neg(f))), n(bi)]), 'leaf:imp+A'
        if len(Ls) == 1:
            return have(K, g, [n(Ls[0][0]), '.elim']), 'leaf:imp+A'
        return exact(Ls[-1][0]), 'close:leaf:imp+A'


def _atom(f):
    """X for X ∨ ¬X (or for a literal); None otherwise."""
    if f[0] == 'or' and f[1][0] == 'atom' and f[2] == neg(f[1]):
        return f[1][1]
    if f[0] == 'atom':
        return f[1]
    return None


def policy(toks):
    """state tokens -> (action tokens, step tag)."""
    return Policy(toks).act()
