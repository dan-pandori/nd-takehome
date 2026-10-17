"""Reviewer's own formula / sequent tools for the peer-rl-review recount (written independently of the run's scripts).

Prompt format: `THM p1 , p2 SEQ c PRF`; atoms P Q R S; `F` is falsum (a constant, never an atom);
`( ~ A )`, `( A & B )`, `( A v B )`, `( A > B )`.
Formulas are tuples: ('a', 'P'), ('F',), ('~', x), ('&', x, y), ('v', x, y), ('>', x, y).
"""
import itertools

ATOMS = ("P", "Q", "R", "S")
BIN = ("&", "v", ">")


def parse_formula(toks, i=0):
    t = toks[i]
    if t in ATOMS:
        return ("a", t), i + 1
    if t == "F":
        return ("F",), i + 1
    if t != "(":
        raise ValueError(f"unexpected token {t!r} at {i}")
    if toks[i + 1] == "~":
        x, j = parse_formula(toks, i + 2)
        if toks[j] != ")":
            raise ValueError("missing ) after negation")
        return ("~", x), j + 1
    x, j = parse_formula(toks, i + 1)
    op = toks[j]
    if op not in BIN:
        raise ValueError(f"expected binary op, got {op!r}")
    y, k = parse_formula(toks, j + 1)
    if toks[k] != ")":
        raise ValueError("missing )")
    return (op, x, y), k + 1


def parse_list(toks):
    """comma-separated formulas (possibly empty)"""
    out, i = [], 0
    while i < len(toks):
        f, i = parse_formula(toks, i)
        out.append(f)
        if i < len(toks):
            if toks[i] != ",":
                raise ValueError(f"expected , got {toks[i]!r}")
            i += 1
    return out


def parse_prompt(prompt):
    toks = prompt.split()
    if toks[0] != "THM" or toks[-1] != "PRF":
        raise ValueError("bad prompt frame: " + prompt)
    s = toks.index("SEQ")
    prem = parse_list(toks[1:s])
    concl = parse_list(toks[s + 1:-1])
    if len(concl) != 1:
        raise ValueError("conclusion must be one formula: " + prompt)
    return tuple(prem), concl[0]


def atoms(f, acc=None):
    acc = set() if acc is None else acc
    if f[0] == "a":
        acc.add(f[1])
    elif f[0] != "F":
        for c in f[1:]:
            atoms(c, acc)
    return acc


def size(f):
    if f[0] in ("a", "F"):
        return 1
    return 1 + sum(size(c) for c in f[1:])


def show(f):
    if f[0] == "a":
        return f[1]
    if f[0] == "F":
        return "F"
    if f[0] == "~":
        return "¬" + show(f[1])
    o = {"&": "∧", "v": "∨", ">": "→"}[f[0]]
    return f"({show(f[1])} {o} {show(f[2])})"


def show_seq(prem, concl):
    return ", ".join(show(p) for p in prem) + " ⊢ " + show(concl)


def match(pat, tgt, sub):
    """extend substitution `sub` (atom -> formula) so that sub(pat) == tgt; return new dict or None"""
    if pat[0] == "a":
        a = pat[1]
        if a in sub:
            return sub if sub[a] == tgt else None
        s2 = dict(sub)
        s2[a] = tgt
        return s2
    if pat[0] == "F":
        return sub if tgt == ("F",) else None
    if tgt[0] != pat[0]:
        return None
    for pc, tc in zip(pat[1:], tgt[1:]):
        sub = match(pc, tc, sub)
        if sub is None:
            return None
    return sub


def match_seq(pseq, tseq, ordered=False):
    """is tseq a substitution instance of pseq?  Premises matched as a multiset (any bijection) unless ordered.
    Returns a witnessing substitution or None."""
    pp, pc = pseq
    tp, tc = tseq
    if len(pp) != len(tp):
        return None
    s0 = match(pc, tc, {})
    if s0 is None:
        return None
    if ordered:
        perms = [tuple(range(len(tp)))]
    else:
        perms = itertools.permutations(range(len(tp)))
    for perm in perms:
        s = s0
        for i, j in enumerate(perm):
            s = match(pp[i], tp[j], s)
            if s is None:
                break
        if s is not None:
            return s
    return None


def is_renaming(sub):
    """substitution maps atoms injectively to atoms"""
    vals = list(sub.values())
    return all(v[0] == "a" for v in vals) and len({v[1] for v in vals}) == len(vals)


def rename_canon(prem, concl):
    """premise-order-invariant renaming-class key: lexicographic minimum over the 24 bijections of {P,Q,R,S}
    of (sorted premise strings, conclusion string)"""
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))

        def ren(f):
            if f[0] == "a":
                return ("a", m[f[1]])
            if f[0] == "F":
                return f
            return (f[0],) + tuple(ren(c) for c in f[1:])

        key = (tuple(sorted(show(ren(p)) for p in prem)), show(ren(concl)))
        if best is None or key < best:
            best = key
    return best


if __name__ == "__main__":
    # self-tests
    p = parse_prompt("THM ( ( P > Q ) & ( Q > P ) ) , ( ( Q > R ) & ( R > Q ) ) SEQ ( ( P > R ) & ( R > P ) ) PRF")
    assert len(p[0]) == 2
    mt = parse_prompt("THM ( P > Q ) , ( ~ Q ) SEQ ( ~ P ) PRF")
    t1 = parse_prompt("THM ( ~ R ) , ( ( P v Q ) > R ) SEQ ( ~ ( P v Q ) ) PRF")  # premise order swapped instance of MT
    s = match_seq(mt, t1)
    assert s is not None and s["P"] == parse_prompt("THM SEQ ( P v Q ) PRF")[1], s
    assert match_seq(mt, t1, ordered=True) is None
    t2 = parse_prompt("THM ( P > Q ) , ( ~ Q ) SEQ ( ~ Q ) PRF")
    assert match_seq(mt, t2) is None
    f = parse_prompt("THM ( P & ( ~ P ) ) SEQ F PRF")
    assert match_seq(f, parse_prompt("THM ( Q & ( ~ Q ) ) SEQ F PRF")) is not None
    assert match_seq(f, parse_prompt("THM ( Q & ( ~ Q ) ) SEQ Q PRF")) is None
    assert match_seq(parse_prompt("THM P SEQ P PRF"), parse_prompt("THM F SEQ F PRF")) is not None  # atom -> F allowed
    assert rename_canon(*parse_prompt("THM ( ~ P ) , ( P v Q ) SEQ Q PRF")) == rename_canon(*parse_prompt("THM ( Q v R ) , ( ~ Q ) SEQ R PRF"))
    print("fml self-tests ok")
