#!/usr/bin/env python3
"""Generic proof-state features and action templates for the decision procedure (run kalmar-complexity).

`features(state_tokens) -> dict` computes properties of the state that do not mention the algorithm's choices:
  ph   phase: premise (fewer premise lines than premises), lem (top level, some atom lacks X ∨ ¬X in scope),
       lembox (inside an excluded-middle box), split (some atom not yet split), leaf
  fk   kind of the innermost frame: top, lemout, lemin, split, box (a box opened at the leaf), inner (a box inside a box)
  nl   lines in the innermost frame (0, 1, 2, 3 = three or more)
  hl   the innermost frame has a line whose formula is ¬¬(X ∨ ¬X) (lem phase)
  efq  some premise is false under the branch valuation (leaf)
  fc   connective of the focus node, or 'none' if the leaf target's line is in scope.  The focus is the first node, in
       post-order, of the target's subformula tree (target = ¬p for the first false premise p, else the goal) that is
       *needed* -- the root is needed; a child is needed if its parent is needed, the parent's literal (the formula if
       true, its negation if false) is not in scope, and the parent's truth-table case uses the child -- and whose
       literal is not in scope.  (The case table is the one place the features know Kalmár's lemma: which children a
       connective's case reads.)
  ft, fp, fq   truth value of the focus and of its left / right child ('-' if none)
  fl   the leaf frame has a False line; gb  goal is False; ga  a line of the goal's formula follows the False line
  gs   goal formula in scope; gl  the goal formula is the frame's last statement
  bc   connective of the innermost box binder; bt  its truth value; bp, bq  its children's; nb  ¬binder in scope;
  gt   truth value of the goal
  xl   lines in the top frame beyond the premise lines and complete X ∨ ¬X pairs (0, 1 = one or more)
`label(tag, action_tokens)` -> the action template: the builder's step tag plus the rule the action applies.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'policy'))
from policy import Policy, val, neg, em, atoms_of, BOT, _atom, ATOMS


def conn(f):
    return {'atom': 'atom', 'bot': 'bot', 'not': 'not', 'and': 'and', 'or': 'or', 'imp': 'imp'}[f[0]]


def needed_children(f, v):
    """which children Kalmár's lemma reads for f under v (the case table)."""
    k = f[0]
    if k in ('atom', 'bot'):
        return []
    if k == 'not':
        return [f[1]]
    x, y = f[1], f[2]
    t, p, q = val(f, v), val(x, v), val(y, v)
    if k == 'and':
        return [x, y] if t else ([x] if not p else [y])
    if k == 'or':
        return ([x] if p else [y]) if t else [x, y]
    return [y] if q else ([x] if not p else [x, y])


def focus(pol, f):
    """first needed node in post-order whose literal is not in scope; None if f's literal is in scope."""
    v = pol.v
    lit = f if val(f, v) else neg(f)
    if pol.lookup(lit) is not None:
        return None
    for c in needed_children(f, v):
        r = focus(pol, c)
        if r is not None:
            return r
    return f


def tv(f, v):
    try:
        return int(val(f, v))
    except KeyError:
        return '-'


def features(toks):
    pol = Policy(toks)
    act, tag = pol.act()          # only to read the frame analysis the policy made (v, leaf); act is not used
    F = {k: '-' for k in FEATS}
    fr = pol.fr
    m = len(pol.prem)
    inner = fr[-1]
    lines = inner.lines if len(fr) > 1 else inner.lines[m:]
    F['nl'] = min(len(lines), 3)
    F['gb'] = int(pol.goal == BOT)
    F['gs'] = int(pol.lookup(pol.goal) is not None)
    last = inner.lines[-1][0] if inner.lines else (inner.binder[0] if inner.binder else None)
    F['gl'] = int(last is not None and pol.lookup(pol.goal) == last)
    T, t = fr[0].lines[m:], 0
    while t + 1 < len(T) and T[t + 1][1][0] == 'or' and _atom(T[t + 1][1]) is not None and T[t][1] == neg(neg(T[t + 1][1])):
        t += 2
    F['xl'] = int(len(T) > t)
    if len(fr) == 1 and len(fr[0].lines) < m:
        F['ph'], F['fk'] = 'premise', 'top'
        return F
    b1 = fr[1].binder[1] if len(fr) > 1 else None
    if len(fr) == 1:
        atoms = atoms_of(pol.prem + [pol.goal])
        if any(pol.lookup(em(x)) is None for x in atoms):
            F['ph'], F['fk'] = 'lem', 'top'
            F['hl'] = int(bool(lines) and lines[-1][1][0] == 'not' and lines[-1][1][1][0] == 'not')
            return F
    if b1 is not None and b1[0] == 'not' and b1[1][0] == 'or' and _atom(b1[1]) is not None and \
            not hasattr(pol, 'v'):
        F['ph'] = 'lembox'
        F['fk'] = 'lemin' if len(fr) == 3 else 'lemout'
        return F
    if not hasattr(pol, 'v'):
        F['ph'] = 'split'
        F['fk'] = 'split' if len(fr) > 1 else 'top'
        return F
    v = pol.v
    F['ph'] = 'leaf'
    s = pol.leaf
    if len(fr) > s + 1:                                       # inside a box opened at the leaf
        F['fk'] = 'inner' if len(fr) > s + 2 else 'box'
        bi, f = inner.binder
        F['bc'], F['bt'] = conn(f), tv(f, v)
        if f[0] in ('and', 'or', 'imp'):
            F['bp'], F['bq'] = tv(f[1], v), tv(f[2], v)
        F['nb'] = int(pol.lookup(neg(f)) is not None)
        F['gt'] = tv(pol.goal, v)
        return F
    F['fk'] = 'split' if s else 'top'
    fp_ = next((i for i, p in enumerate(pol.prem) if not val(p, v)), None)
    F['efq'] = int(fp_ is not None)
    tgt = pol.prem[fp_] if fp_ is not None else pol.goal
    fo = focus(pol, tgt)
    if fo is None:
        F['fc'] = 'none'
    else:
        F['fc'], F['ft'] = conn(fo), tv(fo, v)
        if fo[0] in ('and', 'or', 'imp'):
            F['fp'], F['fq'] = tv(fo[1], v), tv(fo[2], v)
        elif fo[0] == 'not':
            F['fp'] = tv(fo[1], v)
    fl = [i for i, (_, f) in enumerate(lines) if f == BOT]
    F['fl'] = int(bool(fl))
    F['ga'] = int(bool(fl) and any(f == pol.goal for _, f in lines[fl[0] + 1:]))
    return F


def label(tag, act):
    """template = step tag + the rule the action applies (open box / Or.elim / exact / term head)."""
    if act[0] == 'exact':
        return tag
    j = act.index(':=')
    t = act[j + 1:-1] if act[-1] == ';' else act[j + 1:]
    if t[0] == '(':
        head = 'open'
    elif t[0] == 'Or.elim':
        head = 'ORE'
    elif t[0] == '⟨':
        head = 'ANDI'
    elif t[0] in ('Or.inl', 'Or.inr', 'Classical.byContradiction'):
        head = t[0]
    elif len(t) == 2 and t[1] in ('.1', '.2', '.elim'):
        head = t[1]
    elif len(t) == 2:
        head = 'app'
    else:
        head = 'cite'
    return f'{tag}|{head}'


FEATS = ('ph', 'fk', 'nl', 'xl', 'hl', 'efq', 'fc', 'ft', 'fp', 'fq', 'fl', 'gb', 'ga', 'gs', 'gl', 'bc', 'bt', 'bp',
         'bq', 'nb', 'gt')
