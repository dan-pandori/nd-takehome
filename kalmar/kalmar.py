#!/usr/bin/env python3
"""K12-Kalmár: Kalmár-construction proofs of a sequent as ND records (run kalmar-pretrain).

The construction is nd-rl `dan:code/tools/tt_prover.py` (Kalmár's completeness proof), written as an ND proof in the
project's format (spec.md) so that the existing pipeline applies: `lean_tok` renders it as `lean_seq`, and
`state_env.decompose` cuts it into (state, action) pairs.

  1. Case-split on excluded middle for every atom that occurs, in the fixed order P, Q, R, S.  X ∨ ¬X is derived as
     the prover derives it, `Classical.byContradiction (fun h : ¬(X ∨ ¬X) => h (Or.inr (fun p : X => h (Or.inl p))))`:
     in ND, a ¬I box giving ¬¬(X ∨ ¬X) and DN (9 lines).  The split is an ∨E on that line.
  2. In each of the <= 16 branches every formula has a truth value.  A branch where some premise is false (the first
     one, in premise order) closes by ex falso: prove ¬p, then ⊥ by ¬E with the premise line, then the goal by ⊥E.
     Otherwise the goal is proved.  "Prove" is Kalmár's lemma: a line of formula A if A is true in the branch, of ¬A if
     it is false, by recursion on A (the prover's `prove`, case by case):

        atom          the branch hypothesis
        ⊥             ¬⊥: a one-line ¬I box
        ¬A, A false   the line for ¬A                  ¬A, A true    ¬¬A: ¬I box, ¬E with A
        A ∧ B true    ∧I                               A ∧ B false   ¬(A ∧ B): ¬I box, ∧E, ¬E (left conjunct if false)
        A ∨ B true    ∨I (left disjunct if true)       A ∨ B false   ¬(A ∨ B): ¬I box, ∨E, ¬E in each branch
        A → B, B true →I box, R                        A → B, A false →I box, ¬E, ⊥E
        A → B false   ¬(A → B): ¬I box, →E, ¬E

     Sub-proofs are derived before (outside) the box that uses them, as the prover builds `a` and `b` before the
     lambda.  Only the sub-proofs a case uses are derived (the prover computes both but the term keeps only these).
  3. **Memo** (the one choice the term prover does not make, because a term has no shared lines): a formula already
     on a line in scope -- a premise, an excluded-middle line, a branch hypothesis, an earlier line of the branch -- is
     cited, not derived again.  This keeps every step a function of the visible state (the policy cannot count how
     often a subformula occurred before; it can see whether it is in scope).  A branch's last line must be the goal: if
     the goal was found in scope (outside the box), an R line restates it.

Two variants (both split in the order P, Q, R, S):
  pb  per-branch (the prover's): X ∨ ¬X is derived inside each branch that splits X (1 + 2 + 4 + 8 = 15 derivations for
      four atoms);
  sl  shared lemma: X ∨ ¬X is derived once per atom at the top level, before the first split (4 derivations).

Every line and every state-environment action carries a step-type tag (see TAGS), so teacher-forced agreement can be
broken down by step type.  `build(prompt, variant)` -> dict with the ND body, the per-action tags and statistics.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nd2lean import parse_prompt
from lean_tok import fnd

ATOMS = ('P', 'Q', 'R', 'S')
BOT = ('bot',)

# step types, for the action tags
#   lem       a line of an excluded-middle derivation (and the box closings inside it)
#   split     the ∨E on X ∨ ¬X that opens the two branches (and its two closing `exact`s)
#   efq       ex falso at a leaf: ¬E with the false premise, then ⊥E
#   leaf:<c>  Kalmár's lemma on a subformula whose main connective / polarity is <c>: atom never needs a line;
#             bot- (¬⊥), not+ (¬¬A), and+, and-, or+, or-, imp+B (B true), imp+A (A false), imp-
#   reit      the R line that restates a goal found in scope at the end of a branch
#   pr        a premise line
#   end       the final `exact` at the top level
#   close:<t> the `exact` that closes a box opened by a step of type <t> (close:split closes a branch; the environment
#             then opens branch 2 itself)
TAGS = ('pr', 'lem', 'split', 'efq', 'reit', 'end', 'leaf:bot-', 'leaf:not+', 'leaf:and+', 'leaf:and-', 'leaf:or+',
        'leaf:or-', 'leaf:imp+B', 'leaf:imp+A', 'leaf:imp-')


def val(f, v):
    t = f[0]
    if t == 'atom':
        return v[f[1]]
    if t == 'bot':
        return False
    if t == 'not':
        return not val(f[1], v)
    a, b = val(f[1], v), val(f[2], v)
    return (a and b) if t == 'and' else (a or b) if t == 'or' else ((not a) or b)


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


def countermodel(prem, goal):
    import itertools
    at = atoms_of(prem + [goal])
    for bits in itertools.product([True, False], repeat=len(at)):
        v = dict(zip(at, bits))
        if all(val(p, v) for p in prem) and not val(goal, v):
            return v
    return None


class Line:
    """one ND line.  rule in PR AS R ANDI ANDE1 ANDE2 IMPE ORI1 ORI2 NEGE BOTE DN IMPI NEGI ORE.
    refs: Line objects (for ORE the major premise); boxes: Box objects (IMPI / NEGI one, ORE two)."""
    __slots__ = ('f', 'rule', 'refs', 'boxes', 'tag', 'idx')

    def __init__(self, f, rule, refs=(), boxes=(), tag=''):
        self.f, self.rule, self.refs, self.boxes, self.tag, self.idx = f, rule, list(refs), list(boxes), tag, None


class Box:
    __slots__ = ('hyp', 'stmts', 'tag', 'close_tag')

    def __init__(self, f, tag):
        self.hyp = Line(f, 'AS', tag=tag)
        self.stmts = []
        self.tag = tag
        self.close_tag = 'close:' + tag


class Builder:
    def __init__(self, prem, goal, variant='sl'):
        assert variant in ('pb', 'sl')
        self.prem, self.goal, self.variant = prem, goal, variant
        self.top = []
        self.cur = self.top             # statement list being written
        self.scopes = [{}]              # formula -> Line, innermost last
        self.prlines = []

    # ---- scope ----
    def lookup(self, f):
        for sc in reversed(self.scopes):
            if f in sc:
                return sc[f]
        return None

    def emit(self, f, rule, refs=(), boxes=(), tag=''):
        ln = Line(f, rule, refs, boxes, tag)
        self.cur.append(ln)
        self.scopes[-1].setdefault(f, ln)
        return ln

    def box(self, hyp, tag, body, end=None):
        """open a box assuming `hyp`, run body() (which returns the line the box must end with, or None for the
        binder itself), make sure that line is the box's last statement (R otherwise), close.  -> Box"""
        b = Box(hyp, tag)
        saved = self.cur
        self.cur = b.stmts
        self.scopes.append({hyp: b.hyp})
        ln = body(b.hyp)
        last = b.stmts[-1] if b.stmts else b.hyp
        if ln is not None and ln is not last:
            self.emit(ln.f, 'R', [ln], tag='reit')
        self.scopes.pop()
        self.cur = saved
        return b

    # ---- Kalmár's lemma ----
    def lit(self, f, v):
        """a line proving f if f is true under v, else ¬f."""
        t = val(f, v)
        target = f if t else ('not', f)
        ln = self.lookup(target)
        if ln is not None:
            return ln
        k = f[0]
        if k == 'atom':
            raise AssertionError(f'atom {f} not in scope')
        if k == 'bot':                                                  # ¬⊥: fun h : False => h
            b = self.box(BOT, 'leaf:bot-', lambda h: None)
            return self.emit(target, 'NEGI', boxes=[b], tag='leaf:bot-')
        if k == 'not':
            a = self.lit(f[1], v)
            if t:                                                       # ¬A with A false: the line for ¬A
                return a
            tg = 'leaf:not+'                                            # ¬¬A from A
            b = self.box(f, tg, lambda h: self.emit(BOT, 'NEGE', [a, h], tag=tg))
            return self.emit(target, 'NEGI', boxes=[b], tag=tg)
        x, y = f[1], f[2]
        vx, vy = val(x, v), val(y, v)
        if k == 'and':
            if t:
                a = self.lit(x, v); b_ = self.lit(y, v)
                return self.emit(f, 'ANDI', [a, b_], tag='leaf:and+')
            tg = 'leaf:and-'
            if not vx:
                a = self.lit(x, v)
                b = self.box(f, tg, lambda h: self.emit(BOT, 'NEGE', [self.emit(x, 'ANDE1', [h], tag=tg), a], tag=tg))
            else:
                a = self.lit(y, v)
                b = self.box(f, tg, lambda h: self.emit(BOT, 'NEGE', [self.emit(y, 'ANDE2', [h], tag=tg), a], tag=tg))
            return self.emit(target, 'NEGI', boxes=[b], tag=tg)
        if k == 'or':
            if t:
                if vx:
                    return self.emit(f, 'ORI1', [self.lit(x, v)], tag='leaf:or+')
                return self.emit(f, 'ORI2', [self.lit(y, v)], tag='leaf:or+')
            tg = 'leaf:or-'
            na, nb = self.lit(x, v), self.lit(y, v)

            def inner(h):
                b1 = self.box(x, tg, lambda h1: self.emit(BOT, 'NEGE', [h1, na], tag=tg))
                b2 = self.box(y, tg, lambda h2: self.emit(BOT, 'NEGE', [h2, nb], tag=tg))
                return self.emit(BOT, 'ORE', [h], boxes=[b1, b2], tag=tg)
            b = self.box(f, tg, inner)
            return self.emit(target, 'NEGI', boxes=[b], tag=tg)
        # implication
        if vy:                                                          # fun _ : A => b
            tg = 'leaf:imp+B'
            bl = self.lit(y, v)
            b = self.box(x, tg, lambda h: self.emit(y, 'R', [bl], tag=tg))
            return self.emit(f, 'IMPI', boxes=[b], tag=tg)
        if not vx:                                                      # fun z : A => False.elim (a z)
            tg = 'leaf:imp+A'
            a = self.lit(x, v)
            b = self.box(x, tg, lambda h: self.emit(y, 'BOTE', [self.emit(BOT, 'NEGE', [h, a], tag=tg)], tag=tg))
            return self.emit(f, 'IMPI', boxes=[b], tag=tg)
        tg = 'leaf:imp-'                                                # fun h : A → B => b (h a)
        a, nb = self.lit(x, v), self.lit(y, v)
        b = self.box(f, tg, lambda h: self.emit(BOT, 'NEGE', [self.emit(y, 'IMPE', [h, a], tag=tg), nb], tag=tg))
        return self.emit(target, 'NEGI', boxes=[b], tag=tg)

    # ---- the construction ----
    def lem(self, x):
        """X ∨ ¬X (9 lines), or the line already in scope."""
        X = ('atom', x)
        em = ('or', X, ('not', X))
        ln = self.lookup(em)
        if ln is not None:
            return ln
        nem = ('not', em)

        def outer(h):
            nx = self.emit(('not', X), 'NEGI', boxes=[self.box(X, 'lem', lambda p: self.emit(
                BOT, 'NEGE', [self.emit(em, 'ORI1', [p], tag='lem'), h], tag='lem'))], tag='lem')
            return self.emit(BOT, 'NEGE', [self.emit(em, 'ORI2', [nx], tag='lem'), h], tag='lem')
        nn = self.emit(('not', nem), 'NEGI', boxes=[self.box(nem, 'lem', outer)], tag='lem')
        return self.emit(em, 'DN', [nn], tag='lem')

    def leaf(self, v):
        for i, p in enumerate(self.prem):
            if not val(p, v):
                np_ = self.lit(p, v)
                f = self.emit(BOT, 'NEGE', [self.prlines[i], np_], tag='efq')
                return f if self.goal == BOT else self.emit(self.goal, 'BOTE', [f], tag='efq')
        return self.lit(self.goal, v)

    def split(self, atoms, v, ems):
        if not atoms:
            return self.leaf(v)
        x, rest = atoms[0], atoms[1:]
        em = ems[x] if ems is not None else self.lem(x)
        X = ('atom', x)
        b1 = self.box(X, 'split', lambda h: self.split(rest, {**v, x: True}, ems))
        b2 = self.box(('not', X), 'split', lambda h: self.split(rest, {**v, x: False}, ems))
        return self.emit(self.goal, 'ORE', [em], boxes=[b1, b2], tag='split')

    def run(self):
        for p in self.prem:
            self.prlines.append(self.emit(p, 'PR', tag='pr'))
        atoms = atoms_of(self.prem + [self.goal])
        ems = {x: self.lem(x) for x in atoms} if self.variant == 'sl' else None
        g = self.split(atoms, {}, ems)
        last = self.top[-1] if self.top else None
        if g is not last:                       # only an atom-free sequent whose goal is a premise can get here
            self.emit(self.goal, 'R', [g], tag='reit')
        return self.top


def render(top):
    """-> (ND body 'N1 ... ; QED', action tags in state-env order, stats).  Box lines come before the line that
    discharges them (ND order); actions follow lean_seq order (the discharging `have` opens the box first)."""
    out, acts = [], []
    k = [0]
    st = {'max_depth': 0}

    def ref(x):
        return f'N{x.idx}'

    def lines(stmts, d):
        for ln in stmts:
            spans = []
            for b in ln.boxes:
                k[0] += 1
                b.hyp.idx = k[0]
                st['max_depth'] = max(st['max_depth'], d + 1)
                out.append(f'N{k[0]} ' + '| ' * (d + 1) + f'{fnd(b.hyp.f)} : AS ;')
                lines(b.stmts, d + 1)
                spans.append((b.hyp.idx, (b.stmts[-1] if b.stmts else b.hyp).idx))
            k[0] += 1
            ln.idx = k[0]
            if ln.rule == 'ORE':
                rs = [ref(ln.refs[0])] + [f'N{i}' for s in spans for i in s]
            elif ln.rule in ('IMPI', 'NEGI'):
                rs = [f'N{i}' for i in spans[0]]
            else:
                rs = [ref(r) for r in ln.refs]
            out.append(f'N{ln.idx} ' + '| ' * d + f'{fnd(ln.f)} : {ln.rule}' + ''.join(' ' + r for r in rs) + ' ;')

    def actions(stmts):
        for ln in stmts:
            if not ln.boxes:
                acts.append(ln.tag)
                continue
            acts.append(ln.tag)                          # the opening `have`
            for j, b in enumerate(ln.boxes):
                actions(b.stmts)
                acts.append(b.close_tag)                 # `exact` closing this box (branch 1's also opens branch 2)
    lines(top, 0)
    actions(top)
    acts.append('end')
    return ' '.join(out) + ' QED', acts, st


def build(prompt, variant='sl'):
    prem, goal = parse_prompt(prompt)
    if countermodel(prem, goal) is not None:
        return None
    top = Builder(prem, goal, variant).run()
    body, acts, st = render(top)
    return {'proof': body, 'n_lines': body.count(';'), 'tags': acts, 'n_actions': len(acts),
            'n_atoms': len(atoms_of(prem + [goal])), **st}


if __name__ == '__main__':
    import json
    for pr in sys.argv[1:] or ['THM ( P > Q ) , P SEQ Q PRF']:
        for var in ('pb', 'sl'):
            r = build(pr, var)
            print(var, json.dumps({k: v for k, v in r.items() if k != 'tags'}))
