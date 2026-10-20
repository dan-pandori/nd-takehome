#!/usr/bin/env python3
"""K12-Kalmár's per-step policy (state -> next action) as a RASP-L program (run kalmar-complexity).

Spec: `kalmar_complexity/programs/policy/policy.py` (the builder's next action on every state).  The program
reads the state tokens `<st> h1 : F <nl> ... n7 : F <nl> ⊢ G <act>` and computes, at the last position (`<act>`),
the action *content*:

  tmpl            term template (EXACT, PRT `h_j ;`, BOX `( fun ( n_K+1 : B ) => by`, ORE `Or.elim n_c1 ( fun ...`,
                  DN, ORINL, ORINR, APP2 `n_c1 n_c2 ;`, ANDI, ELIM `n_c1 .elim ;`, REIT `n_c1 ;`, PROJ1, PROJ2)
  Ft, Fp, At      the declared formula: SPAN / NEGSPAN of the formula whose last token is at position Fp, or an
                  atom pattern (EM `( X ∨ ( ¬ X ) )`, NEM, NNEM, NATOM, ATOM) of atom At, or FALSE
  Bt, Bp          the box binder, same encoding (atom At)
  c1, c2          cited names (n-numbers; the premise number for PRT)
  K               the next canonical name (max n-index in scope + 1)

`render_content` (plain Python) and `build_render` (RASP, autoregressive, flagged index arithmetic) turn content
into the action tokens.  How the program works (mirrors policy.py):

  1. parse      Dyck depth (FLAG: difference of two counts), matching '(' and main connective of every ')'
  2. formulas   H bottom-up levels: canonical pointer of every subformula occurrence = position of the first
                occurrence of an equal formula (an attention on (connective, canon(left), canon(right)): FLAG
                multi-field select), its 16-row truth table over P Q R S (FLAG: composite value), and a small
                shape code (literal / X∨¬X / ¬(X∨¬X) / ¬¬(X∨¬X)) for the first 4 levels
  3. lines      frames from name gaps (a binder is an n-line whose predecessor index is missing), the
                innermost binder of every position, first line of a formula in its frame (memo order)
  4. phase      premise lines / excluded middle (top or inside its boxes) / splits / leaf / lemma box,
                from max-aggregates of per-atom status codes, binder names and the last line
  5. leaf       valuation from the first literal binder of each atom; first false premise (truth table at the
                valuation); Kalmár's recursion as an H-level top-down descent from the target root: at each level
                attend to the current node, look up its children's targets among the lines, move to the first
                needed child that is missing (post-order first missing node)
  6. boxes      fixed steps inside the excluded-middle boxes and the lemma boxes
  7. assembly   a case code and the content fields selected by it
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rasp as R
from rasp import (tokens, indices, tok_map, seq_map, select, aggr, sel_width, kqv, shift_right, index_select,
                  where, mask, equals, lt, leq, TRUE, kflag, pfn)

# ------------------------------------------------------------------ vocabulary (token ids < 128: int8)
FORM = ['(', ')', '¬', '∧', '∨', '→', 'P', 'Q', 'R', 'S', 'False']
SPEC = ['<st>', '<act>', '<nl>', ':', '⊢', '<end>']
ACTT = ['have', ':=', 'fun', '=>', 'by', 'exact', 'Or.elim', 'Or.inl', 'Or.inr', 'Classical.byContradiction', 'hh',
        '⟨', ',', '⟩', ';', '.1', '.2', '.elim']
ITOS = dict(enumerate(['<pad>'] + FORM + SPEC + ACTT))
for _j in range(1, 10):
    ITOS[39 + _j] = f'h{_j}'
for _j in range(1, 65):
    ITOS[49 + _j] = f'n{_j}'
STOI = {t: i for i, t in ITOS.items()}
T = STOI
# DECISION_HELPERS BEGIN
LP, RP, NEG, AND, OR, IMP, FALSE_T = T['('], T[')'], T['¬'], T['∧'], T['∨'], T['→'], T['False']
ATOM_T = {T['P']: 1, T['Q']: 2, T['R']: 3, T['S']: 4, FALSE_T: 5}          # token -> node code
CONN_T = {NEG: 6, AND: 7, OR: 8, IMP: 9}                                   # connective token -> node code
ATOMS = ['P', 'Q', 'R', 'S']
TT_ATOM = {1: 0xFF00, 2: 0xF0F0, 3: 0xCCCC, 4: 0xAAAA, 5: 0}             # valuation v = 8P + 4Q + 2R + S
FULL = 0xFFFF

# shape codes
SH_FALSE = 5


def SH_LIT(x, neg):
    return x + 5 if neg else x                 # P..S = 1..4, ¬P..¬S = 6..9


def SH_EM(x): return 9 + x                     # 10..13
def SH_NEM(x): return 13 + x                   # 14..17
def SH_NNEM(x): return 17 + x                  # 18..21


# content codes
(EXACT, PRT, BOX, ORE, DN, ORINL, ORINR, APP2, ANDI, ELIM, REIT, PROJ1, PROJ2) = range(13)
TMPL_NAMES = 'EXACT PRT BOX ORE DN ORINL ORINR APP2 ANDI ELIM REIT PROJ1 PROJ2'.split()
(F_NONE, F_SPAN, F_NEGSPAN, F_EM, F_NEM, F_NNEM, F_NATOM, F_ATOM, F_FALSE) = range(9)

# case codes (one per distinct output rule)
CASES = ['PR', 'LB_IN0', 'LB_IN1', 'LB_OUT0', 'LB_OUT1', 'LB_OUT2', 'LEM_DN', 'LEM_BOX', 'SPLIT_ORE', 'BX_IN0',
         'BX_NOT0', 'BX_AND0L', 'BX_AND0R', 'BX_NEGC', 'BX_OR0', 'BX_IMP0', 'BX_B0', 'BX_A0', 'BX_A1', 'LF_NEG',
         'LF_IMP', 'LF_ANDI', 'LF_ORL', 'LF_ORR', 'EF1', 'EF_ELIM', 'REIT', 'EXK1', 'EXBL',
         'EX_LB', 'EX_SPLIT', 'EX_BOX', 'EX_EFQ', 'EX_LEAF']
C = {c: i + 1 for i, c in enumerate(CASES)}
# per case: (tmpl, F type, B type)
CASE_SPEC = {
    'PR': (PRT, F_SPAN, F_NONE), 'LB_IN0': (ORINL, F_EM, F_NONE), 'LB_IN1': (APP2, F_FALSE, F_NONE),
    'LB_OUT0': (BOX, F_NATOM, F_ATOM), 'LB_OUT1': (ORINR, F_EM, F_NONE), 'LB_OUT2': (APP2, F_FALSE, F_NONE),
    'LEM_DN': (DN, F_EM, F_NONE), 'LEM_BOX': (BOX, F_NNEM, F_NEM), 'SPLIT_ORE': (ORE, F_SPAN, F_ATOM),
    'BX_IN0': (APP2, F_FALSE, F_NONE), 'BX_NOT0': (APP2, F_FALSE, F_NONE), 'BX_AND0L': (PROJ1, F_SPAN, F_NONE),
    'BX_AND0R': (PROJ2, F_SPAN, F_NONE), 'BX_NEGC': (APP2, F_FALSE, F_NONE), 'BX_OR0': (ORE, F_FALSE, F_SPAN),
    'BX_IMP0': (APP2, F_SPAN, F_NONE), 'BX_B0': (REIT, F_SPAN, F_NONE), 'BX_A0': (APP2, F_FALSE, F_NONE),
    'BX_A1': (ELIM, F_SPAN, F_NONE), 'LF_NEG': (BOX, F_NEGSPAN, F_SPAN), 'LF_IMP': (BOX, F_SPAN, F_SPAN),
    'LF_ANDI': (ANDI, F_SPAN, F_NONE), 'LF_ORL': (ORINL, F_SPAN, F_NONE), 'LF_ORR': (ORINR, F_SPAN, F_NONE),
    'EF1': (APP2, F_FALSE, F_NONE), 'EF_ELIM': (ELIM, F_SPAN, F_NONE), 'REIT': (REIT, F_SPAN, F_NONE),
    'EXK1': (EXACT, F_NONE, F_NONE), 'EXBL': (EXACT, F_NONE, F_NONE), 'EX_LB': (EXACT, F_NONE, F_NONE),
    'EX_SPLIT': (EXACT, F_NONE, F_NONE), 'EX_BOX': (EXACT, F_NONE, F_NONE), 'EX_EFQ': (EXACT, F_NONE, F_NONE),
    'EX_LEAF': (EXACT, F_NONE, F_NONE)}
EXK1_LIKE = ('EXK1', 'EX_LB', 'EX_SPLIT', 'EX_BOX', 'EX_EFQ', 'EX_LEAF')


def _bit(t, v):
    return (t >> v) & 1


def _tt_apply(o, l, r):
    if o in TT_ATOM:
        return TT_ATOM[o]
    if o == 6:
        return (~r) & FULL
    if o == 7:
        return l & r
    if o == 8:
        return l | r
    if o == 9:
        return ((~l) | r) & FULL
    return 0


def _need(o, l, r, side):
    """per-valuation table: is the left / right child needed by Kalmár's recursion at this node?"""
    c = _tt_apply(o, l, r)
    if o == 6:
        return 0 if side == 0 else FULL
    if o == 7:
        return (c | (~l & FULL)) if side == 0 else (c | l)
    if o == 8:
        return ((~c & FULL) | l) if side == 0 else ((~c & FULL) | (~l & FULL))
    if o == 9:
        return (~r & FULL) if side == 0 else (r | l)
    return 0


def _shape(o, sl, sr):
    if 1 <= o <= 5:
        return o
    if o == 6:
        if 1 <= sr <= 4:
            return sr + 5
        if 10 <= sr <= 17:
            return sr + 4
        return 0
    if o == 8 and 1 <= sl <= 4 and sr == sl + 5:
        return 9 + sl
    return 0


def _shape1(o, sr):
    """first half of the shape rule: atoms and ¬ are final; ∨ with a ¬X right child is remembered as 40 + X."""
    if 1 <= o <= 6:
        return _shape(o, 0, sr)
    if o == 8 and 6 <= sr <= 9:
        return 35 + sr
    return 0


def _shape2(a, sl):
    if a >= 41:
        return 9 + sl if sl == a - 40 else 0
    return a


def _vlookup(pk, nk, qc, qp):
    return np.where(qp != 0, pk == qc, nk == qc)


def _vlookup_skip(pk, nk, fb, qc, qp, qb):
    return np.where(qp != 0, pk == qc, nk == qc) & (fb < qb)


def _code2(t, v):
    """bit v of a child table: value (bit 0) and needed (bit 1)."""
    return ((t >> v) & 1) | (((t >> (16 + v)) & 1) << 1)


def _vlookup2(pk, nk, qc, qcode):
    return np.where((qcode & 1) != 0, pk == qc, nk == qc)


def _boxrule(a, b):
    """lemma-box rule: a = (binder connective if a ¬I box else 0, lines, value of f[1]); b = (goal value, inner, lines)."""
    o, n, v1 = a // 8, (a // 2) % 4, a % 2
    vg_, inn, n2 = (b // 4) % 2, b // 8, b % 4
    if inn:
        return C['BX_IN0'] if n2 == 0 else C['EX_BOX']
    if o == 5:
        return C['EXBL']
    if o == 6:
        return C['BX_NOT0'] if n == 0 else C['EX_BOX']
    if o == 7:
        return (C['BX_AND0R'] if v1 else C['BX_AND0L']) if n == 0 else C['BX_NEGC'] if n == 1 else C['EX_BOX']
    if o == 8:
        return C['BX_OR0'] if n == 0 else C['EX_BOX']
    if o == 9:
        return C['BX_IMP0'] if n == 0 else C['BX_NEGC'] if n == 1 else C['EX_BOX']
    if vg_:
        return C['BX_B0'] if n2 == 0 else C['EX_BOX']
    return (C['BX_A0'], C['BX_A1'], C['EX_BOX'], C['EX_BOX'])[n2]


def _ttfalse(ttk, v):
    return ((ttk >> v) & 1) == 0


# DECISION_HELPERS END


# DECISION BEGIN
def build_decision(H=9, Hd=None):
    """-> (outputs dict name -> node, info dict).  H = formula levels (max formula height), Hd = descent levels."""
    Hd = H if Hd is None else Hd
    R.reset()
    tok, idx = tokens(), indices()
    seen = select(idx, idx, TRUE)                                      # all positions <= here
    # ---- 1. parse ------------------------------------------------------------------------------
    nnum = tok_map(tok, lambda t: t - 49 if t >= 50 else 0)          # n-name index
    hnum = tok_map(tok, lambda t: t - 39 if 40 <= t <= 48 else 0)    # premise name index
    opens = sel_width(select(tok, tok, kflag(lambda k: k == LP, '(')))
    closes = sel_width(select(tok, tok, kflag(lambda k: k == RP, ')')))
    D = seq_map(opens, closes, lambda a, b: a - b, vfn=np.subtract,
                flag='count arithmetic: Dyck depth = #( - #)')
    kpar = seq_map(D, tok, lambda d, t: d if t == LP else (100 + t if t in ATOM_T else -1))
    kcon = seq_map(D, tok, lambda d, t: d if t in CONN_T else -1)
    qcl = seq_map(D, tok, lambda d, t: d + 1 if t == RP else (100 + t if t in ATOM_T else -2))
    start = kqv(kpar, qcl, idx, equals, default=-1, reduction='max', label='span start')
    opPos = kqv(kcon, qcl, idx, equals, default=-1, reduction='max', label='main connective')
    opc = seq_map(tok, index_select(tok, opPos, default=0), lambda t, o: ATOM_T.get(t, CONN_T.get(o, 0) if t == RP
                                                                                  else 0), label='node code')
    lc = seq_map(opPos, opc, lambda p, o: p - 1 if o in (7, 8, 9) else -1, vt='index', label='left child')
    isRoot = seq_map(opc, D, lambda o, d: int(o > 0 and d == 0), label='formula root')
    # ---- 2. formulas: H bottom-up levels -------------------------------------------------------
    gsel = select(idx, lc, equals, label='left child')
    canon = seq_map(kqv(tok, tok, idx, equals, default=-1, reduction='min'), tok,
                    lambda c, t: c if t in ATOM_T else -1, vt='index', label='canon0')
    tt = tok_map(tok, lambda t: TT_ATOM.get(ATOM_T.get(t, 0), 0), vt='comp', label='tt0')
    shape = tok_map(tok, lambda t: ATOM_T.get(t, 0), label='shape0')
    for lev in range(1, H + 1):
        cr = shift_right(canon, 1, default=-1)
        cl = aggr(gsel, canon, default=-1, reduction='max', label='canon left')
        trr = shift_right(tt, 1)
        tll = aggr(gsel, tt, default=0, reduction='max')
        kop = seq_map(seq_map(opc, cr, lambda o, r: o if (1 <= o <= 5 or r >= 0) else -9),
                      cl, lambda o, l: o if (o == 6 or 1 <= o <= 5 or l >= 0) else -9, label='key op')
        m = select((kop, cl, cr), (kop, cl, cr), equals, label=f'canon match L{lev}')
        canon = seq_map(aggr(m, idx, default=-1, reduction='min'), kop, lambda c, o: c if o >= 0 else -1,
                        vt='index', label=f'canon L{lev}')
        tpack = seq_map(opc, trr, lambda o, r: o * 65536 + r, vt='comp')
        tt = seq_map(tpack, tll, lambda a, l: _tt_apply(a >> 16, l, a & FULL), vt='comp', label=f'tt L{lev}')
        if lev <= 4:
            spack = seq_map(opc, shift_right(shape, 1), _shape1)
            shape = seq_map(spack, aggr(gsel, shape, reduction='max'), _shape2, label=f'shape L{lev}')
    # per node and child: the child's truth table (low 16 bits) and whether Kalmár's recursion needs it (high)
    LT = seq_map(tpack, tll, lambda a, l: l | _need(a >> 16, l, a & FULL, 0) << 16, vt='comp', label='left table')
    RT = seq_map(tpack, tll, lambda a, l: (a & FULL) | _need(a >> 16, l, a & FULL, 1) << 16, vt='comp',
                 label='right table')
    # ---- 3. lines and frames -------------------------------------------------------------------
    prevN = kqv(idx, idx, nnum, lt, default=0, reduction='max', label='previous n-name')
    bname = seq_map(nnum, prevN, lambda b, p: b if (b >= 2 and p < b - 1) else 0, label='binder name')
    curN = aggr(seen, nnum, default=0, reduction='max', label='line n-name')
    curH = aggr(seen, hnum, default=0, reduction='max', label='line h-name')
    frameB = aggr(seen, bname, default=0, reduction='max', label='frame binder')
    afterT = aggr(seen, tok == T['⊢'], default=0, reduction='max', label='after turnstile')
    lroot = seq_map(isRoot, afterT, lambda r, a: int(r and not a), label='line root')
    nroot = seq_map(lroot, curN, lambda r, n: int(r and n > 0), label='n-line root')
    hroot = seq_map(lroot, curN, lambda r, n: int(r and n == 0), label='h-line root')
    ffp = aggr(select((mask(canon, nroot, -5), frameB), (canon, frameB), equals), idx, default=-1, reduction='min')
    lookName = seq_map(curN, seq_map(ffp, idx, lambda a, b: int(a == b), vfn=lambda a, b: (a == b).astype(np.int64)),
                       lambda n, f: n if f else 0, label='citable name (first line of its formula in its frame)')
    negKey = seq_map(cr, opc, lambda c, o: c if o == 6 else -5, vt='index', label='negated-line key')
    LK = (canon, negKey)
    isBroot = seq_map(seq_map(frameB, curN, lambda b, n: int(b == n)), nroot, lambda a, r: int(a and r),
                      label='binder root')
    litKey = seq_map(shape, isBroot, lambda s, b: (s if s <= 4 else s - 5) if (b and 1 <= s <= 9 and s != 5)
                     else 0, label='binder literal atom')
    firstLit = seq_map(seq_map(kqv(litKey, litKey, idx, equals, default=-1, reduction='min'), idx,
                               lambda a, b: int(a == b), vfn=lambda a, b: (a == b).astype(np.int64)),
                       litKey, lambda e, l: int(e and l > 0), label='split binder')
    w = seq_map(mask(shape, nroot, 0), firstLit, lambda s, f: s + 32 * f, label='line code')
    st = [aggr(seen, seq_map(tok, w, (lambda X: lambda t, c: max(
        int(ATOM_T.get(t, 0) == X),
        2 if (c & 31) == SH_EM(X) else 0,
        (3 if (c & 31) == X else 4 if (c & 31) == X + 5 else 0) if c >= 32 else 0))(X)),
        default=0, reduction='max', label=f'status {ATOMS[X - 1]}') for X in (1, 2, 3, 4)]
    # ---- 4. values at the last position --------------------------------------------------------
    m_, k1, bL = curH, curN, frameB                    # premises, last line's name (K = k1 + 1), innermost binder
    stPQ = seq_map(st[0], st[1], lambda a, b: a * 5 + b)
    stRS = seq_map(st[2], st[3], lambda a, b: a * 5 + b)

    def stat(f):
        return seq_map(stPQ, stRS, lambda a, b: f([a // 5, a % 5, b // 5, b % 5]))
    xneed = stat(lambda s: next((i + 1 for i in range(4) if s[i] == 1), 0))        # first atom without X ∨ ¬X
    xsplit = stat(lambda s: next((i + 1 for i in range(4) if s[i] in (1, 2)), 0))  # first atom not split
    vval = stat(lambda s: sum(8 >> i for i in range(4) if s[i] == 3))              # valuation index
    selB = select(isBroot, isBroot, kflag(lambda k: k != 0, 'binder root'))
    bF = aggr(selB, curN, default=0, reduction='min', label='first binder')
    bS = aggr(selB, mask(curN, firstLit, 0), default=0, reduction='max', label='last split binder')
    bP = kqv(frameB, bL, frameB, lt, default=0, reduction='max', label='previous binder')
    nameAt = mask(curN, nroot, -1, label='root name key')

    def line(j, vals):
        s = select(nameAt, j, equals)
        return [aggr(s, v, default=d, reduction='max') for v, d in vals]
    shL, cnL = line(k1, [(shape, 0), (canon, -1)])
    shL2, = line(k1 - 1, [(shape, 0)])
    shF, = line(bF, [(shape, 0)])
    fcan, fop, fcl, fcr, ftl = line(bL, [(canon, -1), (opc, 0), (cl, -1), (cr, -1), (tll, 0)])
    bL1 = bL + 1
    cnC, = line(bL1, [(canon, -1)])
    cnG = shift_right(canon, 1, default=-1, label='goal canon')
    ttG = shift_right(tt, 1, label='goal tt')
    shG = shift_right(shape, 1, label='goal shape')
    gptr = R.shift_index(-1)                                           # the goal's last token
    prPtr = kqv(mask(curH, hroot, -1), k1 + 1, idx, equals, default=-1, reduction='max', label='premise k root')
    selFP = select(mask(tt, hroot, FULL), vval, pfn(_ttfalse, 'premise false at v'))
    fpPos = aggr(selFP, idx, default=-1, reduction='min', label='first false premise')
    fpNum = aggr(selFP, curH, default=0, reduction='min')
    efq = fpPos >= 0

    def lookup(c, pol, label=None):
        return aggr(select(LK, (c, pol), pfn(_vlookup, 'line = target')), lookName, default=0, reduction='max',
                    label=label)
    # ---- 5. leaf: descent from the target root ------------------------------------------------
    cur = where(efq, fpPos, cnG)
    curs = [cur]                                                       # instrumentation
    for lev in range(Hd):
        sc = select(idx, cur, equals, label=f'descent L{lev}')
        dl, dr = aggr(sc, cl, default=-1, reduction='max'), aggr(sc, cr, default=-1, reduction='max')
        cL = seq_map(aggr(sc, LT, reduction='max'), vval, _code2, label='left: value + needed')
        cR = seq_map(aggr(sc, RT, reduction='max'), vval, _code2, label='right: value + needed')
        if lev == 0:
            rootName = lookup(aggr(sc, canon, default=-1, reduction='max'), ~efq, 'root lookup')
        nameL = aggr(select(LK, (dl, cL), pfn(_vlookup2, 'line = target')), lookName, default=0, reduction='max')
        nameR = aggr(select(LK, (dr, cR), pfn(_vlookup2, 'line = target')), lookName, default=0, reduction='max')
        goL = seq_map(cL, nameL, lambda c, n: int(c >= 2 and n == 0))
        goR = seq_map(cR, nameR, lambda c, n: int(c >= 2 and n == 0))
        mv = seq_map(goL, goR, lambda a, b: 1 if a else (2 if b else 0), label=f'move L{lev}')
        t1 = seq_map(mv, dl, lambda a, p: p if a == 1 else (-3 if a == 2 else -4), vt='index')
        t2 = seq_map(t1, dr, lambda a, p: p if a == -3 else a, vt='index')
        cur = seq_map(t2, cur, lambda a, p: p if a == -4 else a, vt='index', label=f'node L{lev + 1}')
        curs.append(cur)                                               # instrumentation
    ss = select(idx, cur, equals, label='stop node')
    sV = seq_map(aggr(ss, tt, reduction='max'), vval, _bit, vfn=_bit)
    leafCase = seq_map(seq_map(aggr(ss, opc, reduction='max'), sV, lambda o, v: o * 2 + v), cL,
                       lambda a, c: C['LF_NEG'] if a % 2 == 0 else (C['LF_ANDI'] if a // 2 == 7 else C['LF_IMP']
                                                                    if a // 2 == 9 else C['LF_ORL'] if c % 2 else
                                                                    C['LF_ORR']))
    fkey = seq_map(shape, nroot, lambda s, r: int(r and s == SH_FALSE))
    fl = kqv(mask(curN, fkey, 0), seq_map(bS, m_, max), mask(curN, fkey, 99), R.gt, default=0, reduction='min',
             label='first False line in the leaf frame')
    # ---- 6. boxes ----------------------------------------------------------------------------------
    Ls = k1 - bL                                                       # lines in the innermost frame
    f1 = seq_map(seq_map(fop, fcl, lambda o, l: l if o != 6 else -2, vt='index'), fcr,
                 lambda a, r: r if a == -2 else a, vt='index', label="binder's first child")
    zero, one = R.full(tok, 0), R.full(tok, 1)
    Lnf = lookup(fcan, zero, 'lookup ¬f')
    Lf1 = lookup(f1, one, 'lookup f[1]')
    Lnc = lookup(cnC, zero, 'lookup ¬c')
    Lgs = aggr(select((canon, negKey, frameB), (cnG, one, bL), pfn(_vlookup_skip, 'line = goal, outer frames')),
               lookName, default=0, reduction='max', label='lookup g skip 1')
    emRoot = seq_map(shape, nroot, lambda s, r: s if (r and 10 <= s <= 13) else -5)      # X ∨ ¬X lines
    ffpE = aggr(select((emRoot, frameB), (shape, frameB), equals), idx, default=-1, reduction='min')
    lookE = seq_map(seq_map(ffpE, idx, lambda a, b: int(a == b), vfn=lambda a, b: (a == b).astype(np.int64)), curN,
                    lambda f, n: n if f else 0, label='citable X ∨ ¬X line')
    lookEm = kqv(emRoot, tok_map(xsplit, SH_EM), lookE, equals, default=0, reduction='max', label='lookup em')
    vf1 = seq_map(ftl, vval, _bit, vfn=_bit)
    vg = seq_map(ttG, vval, _bit, vfn=_bit)
    gF = shG == SH_FALSE
    # ---- 7. case code --------------------------------------------------------------------------
    c_pr = k1 < m_
    c_lb = tok_map(shF, lambda s: int(14 <= s <= 17), label='first binder is ¬(X ∨ ¬X)')
    xE = tok_map(shF, lambda s: s - 13 if 14 <= s <= 17 else 0)
    c_lemtop = seq_map(bL, xneed, lambda b, x: int(b == 0 and x > 0), label='excluded middle at the top')
    c_rest = seq_map(xsplit, bL > bS, lambda x, b: 4 if x > 0 else (5 if b else 6), label='split / box / leaf')
    lbIn = seq_map(bL > bF, Ls, lambda i, n: i * 4 + min(n, 3))
    k1bF = k1 - bF
    lbCase = seq_map(lbIn, k1bF, lambda a, n: (C['LB_IN0'], C['LB_IN1'], C['EX_LB'], C['EX_LB'])[a % 4] if a >= 4
                     else (C['LB_OUT0'], C['LB_OUT1'], C['LB_OUT2'], C['EX_LB'])[min(n, 3)])
    lemCase = seq_map(shL, xneed, lambda s, x: C['LEM_DN'] if s == SH_NNEM(x) else C['LEM_BOX'])
    pairEnd = seq_map(shL, shL2, lambda a, b: int(10 <= a <= 13 and b == a + 8))
    flNE = seq_map(k1 > seq_map(bL, m_, max), pairEnd, lambda g, p: int(g and not p),
                   label='innermost split frame / top has a line after the premises and X ∨ ¬X pairs')
    inner = bP > bS
    bx1 = seq_map(seq_map(gF, Lnf == 0, lambda a, b: int(a and b)), fop, lambda n, o: o if n else 0)
    bx3 = seq_map(seq_map(bx1, Ls, lambda o, n: o * 4 + min(n, 3)), vf1, lambda a, v: a * 2 + v)
    bx4 = seq_map(seq_map(vg, inner, lambda v, i: v + 2 * i), Ls, lambda a, n: a * 4 + min(n, 3))
    boxCase = seq_map(bx3, bx4, _boxrule, label='box case')
    rootPres = rootName > 0
    ef1 = seq_map(fl, seq_map(gF, cnL == cnG, lambda a, b: int(a or b)), lambda f, e: C['EF1'] if f == 0 else (
        C['EX_EFQ'] if e else C['EF_ELIM']))
    postCase = seq_map(seq_map(efq, ef1, lambda e, c: c if e else 0), rootName == k1,
                       lambda c, x: c if c else (C['EX_LEAF'] if x else C['REIT']))
    stepCase = seq_map(seq_map(rootPres, postCase, lambda r, p: p if r else -1), leafCase,
                       lambda a, l: a if a >= 0 else l, label='leaf case')
    ph = seq_map(c_pr, c_lb, lambda p, l: 1 if p else 2 if l else 0)
    ph = seq_map(ph, c_lemtop, lambda p, l: p if p else (3 if l else 0))
    phase = seq_map(ph, c_rest, lambda p, r: p if p else r, label='phase')
    case = seq_map(seq_map(phase, lbCase, lambda p, c: C['PR'] if p == 1 else (c if p == 2 else -p)), lemCase,
                   lambda a, c: c if a == -3 else a)
    case = seq_map(case, flNE, lambda a, f: (C['EX_SPLIT'] if f else C['SPLIT_ORE']) if a == -4 else a)
    case = seq_map(case, boxCase, lambda a, c: c if a == -5 else a)
    case = seq_map(case, stepCase, lambda a, c: c if a == -6 else a, label='case')
    # ---- 8. content fields ---------------------------------------------------------------------
    spec = {C[c]: s for c, s in CASE_SPEC.items()}
    tmpl = tok_map(case, lambda c: spec[c][0], label='tmpl')
    Ft = tok_map(case, lambda c: spec[c][1], label='F type')
    Bt = tok_map(case, lambda c: spec[c][2], label='B type')
    mark = tok_map(case, lambda c: -50 - c, label='case marker')
    cvals = {}                                                         # instrumentation

    def choose(cands, vt='bint', label=None):
        """value = the candidate whose case set holds `case` (a chain of seq_maps from the case marker)."""
        out = mark
        for cs, val in cands:
            ids = {C[x] for x in cs}
            for x in cs:                                               # instrumentation
                cvals.setdefault(x, []).append(val)                    # instrumentation
            out = seq_map(out, val, (lambda ids: lambda a, v: v if (a <= -50 and -50 - a in ids) else a)(ids),
                          vt=vt, label=label)
        return out
    Fp = choose([(['PR'], prPtr), (['SPLIT_ORE', 'EF_ELIM', 'REIT', 'BX_B0', 'BX_A1'], gptr),
                 (['LF_NEG', 'LF_IMP', 'LF_ANDI', 'LF_ORL', 'LF_ORR'], cur), (['BX_AND0L'], fcl),
                 (['BX_AND0R', 'BX_IMP0'], fcr)], 'index', 'F pointer')
    At = choose([(['LEM_DN', 'LEM_BOX'], xneed), (['LB_IN0', 'LB_OUT0', 'LB_OUT1'], xE), (['SPLIT_ORE'], xsplit)],
                label='atom')
    Bp = choose([(['LF_NEG'], cur), (['LF_IMP'], dl), (['BX_OR0'], fcl)], 'index', 'B pointer')
    c1 = choose([(['PR'], k1 + 1), (['LB_IN0', 'BX_NOT0', 'BX_AND0L', 'BX_AND0R', 'BX_OR0', 'BX_IMP0', 'EXBL'], bL),
                 (['LB_IN1', 'LB_OUT2'], bF), (['LB_OUT1'], bF + 1), (['SPLIT_ORE'], lookEm),
                 (['BX_IN0', 'BX_A0'], Lnf), (['BX_NEGC'], Lnc), (['BX_B0'], Lgs), (['BX_A1'], bL1),
                 (['LF_ANDI', 'LF_ORL'], nameL), (['LF_ORR'], nameR), (['EF1', 'REIT'], rootName),
                 (['EF_ELIM'], fl)], label='c1')
    c1 = seq_map(c1, k1, lambda a, b: b if a <= -50 else a, label='c1 (otherwise the last line)')
    c2 = choose([(['LB_IN1', 'BX_NEGC'], bL1), (['LB_OUT2'], bF + 2), (['BX_IN0', 'BX_A0'], bL),
                 (['BX_NOT0', 'BX_IMP0'], Lf1), (['LF_ANDI'], nameR), (['EF1'], fpNum)], label='c2')
    K = k1 + 1
    outs = {'tmpl': tmpl, 'Ft': Ft, 'Fp': Fp, 'At': At, 'Bt': Bt, 'Bp': Bp, 'c1': c1, 'c2': c2, 'K': K}
    # DECISION END
    # per case: the nodes that decide it (phase conditions on its path + its own rule's inputs + its values)
    group = {'PR': [c_pr], 'LB': [c_pr, c_lb, lbIn, k1bF], 'LEM': [c_pr, c_lb, c_lemtop, lemCase],
             'SPLIT': [c_pr, c_lb, c_lemtop, c_rest, flNE], 'BOX': [c_pr, c_lb, c_lemtop, c_rest, bx3, bx4],
             'LEAF': [c_pr, c_lb, c_lemtop, c_rest, rootPres, leafCase],
             'POST': [c_pr, c_lb, c_lemtop, c_rest, rootPres, postCase]}
    deps = {}
    for cn in CASES:
        g = ('PR' if cn == 'PR' else 'LB' if cn.startswith('LB') or cn == 'EX_LB' else 'LEM' if cn.startswith('LEM')
             else 'SPLIT' if cn in ('SPLIT_ORE', 'EX_SPLIT') else 'BOX' if cn.startswith('BX') or cn in
             ('EXBL', 'EX_BOX') else 'LEAF' if cn.startswith('LF') else 'POST')
        deps[cn] = group[g] + cvals.get(cn, []) + ([] if CASE_SPEC[cn][0] == EXACT else [K]) + \
            ([k1] if cn in EXK1_LIKE or cn == 'LEM_DN' else [])
    info = {'case': case, 'start': start, 'phase': phase, 'cur': cur, 'curs': curs, 'efq': efq,
            'rootName': rootName, 'vval': vval, 'deps': deps, 'groups': group}
    return outs, info


# ------------------------------------------------------------------ plain-Python rendering of content
def _n(i):
    return f'n{i}'


# FORMULA_TOKENS BEGIN
def formula_tokens(typ, ptr, atom, toks, start):
    if typ == F_SPAN:
        return list(toks[start[ptr]:ptr + 1])
    if typ == F_NEGSPAN:
        return ['(', '¬'] + list(toks[start[ptr]:ptr + 1]) + [')']
    if typ == F_FALSE:
        return ['False']
    X = ATOMS[atom - 1]
    E = ['(', X, '∨', '(', '¬', X, ')', ')']
    return {F_EM: E, F_NEM: ['(', '¬'] + E + [')'], F_NNEM: ['(', '¬', '(', '¬'] + E + [')', ')'],
            F_NATOM: ['(', '¬', X, ')'], F_ATOM: [X]}[typ]


# FORMULA_TOKENS END


def render_content(c, toks, start):
    """content dict (ints) + state tokens (strings) + span starts -> action tokens."""
    tm = c['tmpl']
    if tm == EXACT:
        return ['exact', _n(c['c1'])]
    K = c['K']
    out = ['have', _n(K), ':'] + formula_tokens(c['Ft'], c['Fp'], c['At'], toks, start) + [':=']
    n1, n2 = _n(c['c1']), _n(c['c2'])
    if tm == PRT:
        return out + [f"h{c['c1']}", ';']
    if tm in (BOX, ORE):
        b = formula_tokens(c['Bt'], c['Bp'], c['At'], toks, start)
        pre = ['('] if tm == BOX else ['Or.elim', n1, '(']
        return out + pre + ['fun', '(', _n(K + 1), ':'] + b + [')', '=>', 'by']
    return out + {DN: ['Classical.byContradiction', '(', 'fun', 'hh', '=>', n1, 'hh', ')', ';'],
                  ORINL: ['Or.inl', n1, ';'], ORINR: ['Or.inr', n1, ';'], APP2: [n1, n2, ';'],
                  ANDI: ['⟨', n1, ',', n2, '⟩', ';'], ELIM: [n1, '.elim', ';'], REIT: [n1, ';'],
                  PROJ1: [n1, '.1', ';'], PROJ2: [n1, '.2', ';']}[tm]


def encode(toks):
    return [STOI[t] for t in toks]


# ------------------------------------------------------------------ RASP rendering (autoregressive)
# RENDER_HELPERS BEGIN
END_T = T['<end>']
# symbols of the rendering program (ids above every token id, still int8)
S_NC1, S_HC1, S_NC2, S_NK, S_NK1, S_BTOK, S_FTOK, S_COPY, S_COPYN, S_DEF2, S_DEF3, S_DEFER = range(114, 126)
_PRE = {BOX: ['(', 'fun', '(', S_NK1, ':'], ORE: ['Or.elim', S_NC1, '(', 'fun', '(', S_NK1, ':']}
_TERM = {PRT: [S_HC1, ';'], DN: ['Classical.byContradiction', '(', 'fun', 'hh', '=>', S_NC1, 'hh', ')', ';'],
         ORINL: ['Or.inl', S_NC1, ';'], ORINR: ['Or.inr', S_NC1, ';'], APP2: [S_NC1, S_NC2, ';'],
         ANDI: ['⟨', S_NC1, ',', S_NC2, '⟩', ';'], ELIM: [S_NC1, '.elim', ';'], REIT: [S_NC1, ';'],
         PROJ1: [S_NC1, '.1', ';'], PROJ2: [S_NC1, '.2', ';']}


def _sym(x):
    return x if isinstance(x, int) else T[x]


def _pattern(ta, j):
    """token j of a formula operand of type/atom code ta = type * 8 + atom; S_COPY(N) where it is copied."""
    t, a = ta // 8, ta % 8
    if t == F_SPAN:
        return S_COPY
    if t == F_NEGSPAN:
        return LP if j == 0 else NEG if j == 1 else S_COPYN
    if t in (F_NONE,) or j < 0:
        return END_T
    toks = formula_tokens(t, 0, max(a, 1), None, None) if t != F_FALSE else ['False']
    return T[toks[j]] if j < len(toks) else END_T


def _pack_ta(t, a):
    return t * 8 + (a if 1 <= a <= 4 else 0)        # unused fields may hold a case marker


def _plen(t):
    return {F_EM: 8, F_NEM: 11, F_NNEM: 14, F_NATOM: 4, F_ATOM: 1, F_FALSE: 1}.get(t, 0)


def _head(t, o):
    if t == EXACT:
        return (T['exact'], S_NC1)[o] if 0 <= o < 2 else END_T
    return (T['have'], S_NK, T[':'])[o] if 0 <= o < 3 else S_DEF2


def _term(t, u):
    if t in _PRE:
        pre = _PRE[t]
        return _sym(pre[u]) if 0 <= u < len(pre) else S_DEFER
    seq = _TERM.get(t, [])
    return _sym(seq[u]) if 0 <= u < len(seq) else END_T


# RENDER_HELPERS END


# RENDER BEGIN
def build_render(dec, start):
    """next-token program for the action: dec = decision outputs (read at <act>), start = span starts.  Offsets
    into the action are differences of positions (unbounded, index-typed): every map that computes one or uses one
    as a table index is flagged as index arithmetic."""
    tok, idx = tokens(), indices()
    isAct = tok == T['<act>']
    selA = select(isAct, isAct, kflag(lambda k: k != 0, '<act>'))
    get = lambda x: aggr(selA, x, default=0, reduction='max')
    actPos, tmpl, Ft, Fp, At, Bt, Bp, c1, c2, K = [get(x) for x in (idx, dec['tmpl'], dec['Ft'], dec['Fp'],
                                                                    dec['At'], dec['Bt'], dec['Bp'], dec['c1'],
                                                                    dec['c2'], dec['K'])]
    IA = 'index arithmetic: '
    o = seq_map(idx, actPos, lambda a, b: a - b, vfn=np.subtract, vt='index', flag=IA + 'offset from <act>')
    Fs = index_select(start, Fp, default=0)
    Bs = index_select(start, Bp, default=0)
    LF = seq_map(Ft, seq_map(Fp, Fs, lambda a, b: a - b, vfn=np.subtract, vt='index', flag=IA + 'span length'),
                 lambda t, d: d + 1 if t == F_SPAN else d + 4 if t == F_NEGSPAN else _plen(t), vt='index',
                 flag=IA + 'operand length')
    LB = seq_map(Bt, seq_map(Bp, Bs, lambda a, b: a - b, vfn=np.subtract, vt='index', flag=IA + 'span length'),
                 lambda t, d: d + 1 if t == F_SPAN else _plen(t), vt='index', flag=IA + 'operand length')
    u = seq_map(o, LF, lambda a, b: a - 4 - b, vt='index', flag=IA + 'offset into the term')
    jb = seq_map(u, tmpl, lambda a, t: a - (5 if t == BOX else 7), vt='index', flag=IA + 'offset into the binder')
    r = seq_map(jb, LB, lambda a, b: max(-1, min(a - b, 4)), flag=IA + 'offset after the binder')
    cF = index_select(tok, seq_map(Fs, seq_map(o, Ft, lambda a, t: a - 3 - 2 * (t == F_NEGSPAN), vt='index',
                                               flag=IA + 'offset into the formula'),
                                   lambda a, b: a + b, vfn=np.add, vt='index', flag=IA + 'copy address'))
    cB = index_select(tok, seq_map(Bs, jb, lambda a, b: a + b, vfn=np.add, vt='index', flag=IA + 'copy address'))
    fpat = seq_map(seq_map(Ft, At, _pack_ta), o, lambda ta, a: _pattern(ta, a - 3), flag=IA + 'table at an offset')
    fTok = seq_map(seq_map(fpat, u, lambda f, b: RP if (f == S_COPYN and b == -2) else f), cF,
                   lambda f, c: c if f in (S_COPY, S_COPYN) else f)
    bpat = seq_map(seq_map(Bt, At, _pack_ta), jb, _pattern, flag=IA + 'table at an offset')
    bTok = seq_map(bpat, cB, lambda b, c: c if b == S_COPY else b)
    w1 = seq_map(jb, r, lambda a, b: -1 if a < 0 else (S_BTOK if b < 0 else
                                                       (T[')'], T['=>'], T['by'], END_T, END_T)[b]))
    ts = seq_map(seq_map(tmpl, u, _term, flag=IA + 'table at an offset'), w1, lambda a, b: b if a == S_DEFER else a)
    sym = seq_map(seq_map(tmpl, o, _head, flag=IA + 'table at an offset'), u, lambda h, b: h if h != S_DEF2 else (
        S_FTOK if b <= -2 else T[':='] if b == -1 else S_DEF3))
    sym = seq_map(sym, ts, lambda a, b: b if a == S_DEF3 else a)
    sym = seq_map(sym, c1, lambda a, c: 49 + c if a == S_NC1 else 39 + c if a == S_HC1 else a)
    sym = seq_map(sym, c2, lambda a, c: 49 + c if a == S_NC2 else a)
    sym = seq_map(sym, K, lambda a, k: 49 + k if a == S_NK else 50 + k if a == S_NK1 else a)
    sym = seq_map(sym, bTok, lambda a, b: b if a == S_BTOK else a)
    nxt = seq_map(sym, fTok, lambda a, f: f if a == S_FTOK else a, label='next token')
    return nxt
# RENDER END
