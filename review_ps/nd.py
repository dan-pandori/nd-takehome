"""Reviewer's own ND parser, rule checker and proof structure (proof-strategies review).

Written from spec.md only (independent of nd_verify / patterns.py / proof_strategies/strategies.py).
Formulas: 'P','Q','R','S' atoms, 'F' falsum, ('~',A), ('&',A,B), ('v',A,B), ('>',A,B).
"""
ATOMS = {"P", "Q", "R", "S"}
BIN = {"&", "v", ">"}


class ParseError(Exception):
    pass


def parse_formula(toks, i=0):
    t = toks[i]
    if t in ATOMS or t == "F":
        return t, i + 1
    if t != "(":
        raise ParseError("bad token " + t)
    if toks[i + 1] == "~":
        a, j = parse_formula(toks, i + 2)
        if toks[j] != ")":
            raise ParseError("expected )")
        return ("~", a), j + 1
    a, j = parse_formula(toks, i + 1)
    op = toks[j]
    if op not in BIN:
        raise ParseError("bad op " + op)
    b, k = parse_formula(toks, j + 1)
    if toks[k] != ")":
        raise ParseError("expected ) after binary")
    return (op, a, b), k + 1


def pf(s):
    toks = s.split()
    f, j = parse_formula(toks, 0)
    if j != len(toks):
        raise ParseError("trailing tokens")
    return f


def show(f):
    if isinstance(f, str):
        return f
    if f[0] == "~":
        return "( ~ " + show(f[1]) + " )"
    return "( " + show(f[1]) + " " + f[0] + " " + show(f[2]) + " )"


def parse_prompt(prompt):
    p = prompt.strip()
    assert p.startswith("THM") and p.endswith("PRF"), p[:40]
    body = p[3:-3].strip()
    lhs, rhs = body.split("SEQ")
    lhs = lhs.strip()
    prem = [pf(x) for x in lhs.split(" , ")] if lhs else []
    return prem, pf(rhs.strip())


def parse_thm(thm):
    lhs, rhs = thm.split("|-")
    lhs = lhs.strip()
    prem = [pf(x) for x in lhs.split(" , ")] if lhs else []
    return prem, pf(rhs.strip())


def subformulas(f, acc):
    acc.add(f)
    if isinstance(f, tuple):
        for g in f[1:]:
            subformulas(g, acc)
    return acc


def neg(f):
    return ("~", f)


class Proof:
    """Parsed ND proof. Lines keyed by their N index. Attributes per line: depth, f, rule, refs, ctx (open boxes)."""

    def __init__(self, prem, concl, proof):
        self.prem, self.concl = prem, concl
        body = proof.strip()
        parts = [x.strip() for x in body.split(";")]
        if parts[-1] != "QED":
            raise ParseError("no QED")
        parts = parts[:-1]
        self.order = []
        self.L = {}
        for part in parts:
            toks = part.split()
            if not toks[0].startswith("N"):
                raise ParseError("no index")
            k = int(toks[0][1:])
            d = 0
            i = 1
            while toks[i] == "|":
                d += 1
                i += 1
            c = toks.index(":", i)
            f = pf(" ".join(toks[i:c]))
            rule = toks[c + 1]
            refs = [int(x[1:]) for x in toks[c + 2:]]
            if k in self.L:
                raise ParseError("dup index")
            self.L[k] = {"d": d, "f": f, "rule": rule, "refs": refs}
            self.order.append(k)
        self._ctx()
        self.last = self.order[-1]

    def _ctx(self):
        stack = []
        for k in self.order:
            x = self.L[k]
            d = x["d"]
            if x["rule"] == "AS":
                if d < 1 or d > len(stack) + 1:
                    raise ParseError("bad AS depth")
                stack = stack[: d - 1] + [k]
            else:
                if d > len(stack):
                    raise ParseError("depth beyond open boxes")
                stack = stack[:d]
            x["ctx"] = tuple(stack)

    # ---- rule check (sanity only; never used to count anything) ----
    def check(self):
        L = self.L
        idx = {k: n for n, k in enumerate(self.order)}
        npr = 0

        def citable(j, i):
            return j in L and idx[j] < idx[i] and L[i]["ctx"][: len(L[j]["ctx"])] == L[j]["ctx"]

        def box(s, e, i):
            if s not in L or e not in L or L[s]["rule"] != "AS":
                return False
            if not (idx[s] <= idx[e] < idx[i]):
                return False
            cs = L[s]["ctx"]
            if L[e]["ctx"] != cs:  # e directly inside box s
                return False
            parent = cs[:-1]
            ci = L[i]["ctx"]
            return s not in ci and ci[: len(parent)] == parent

        for k in self.order:
            x = L[k]
            r, refs, G = x["rule"], x["refs"], x["f"]
            f = lambda j: L[j]["f"]  # noqa: E731
            if r == "PR":
                if x["d"] != 0 or npr >= len(self.prem) or self.prem[npr] != G or refs:
                    return False, f"PR N{k}"
                npr += 1
                continue
            if r == "AS":
                if refs:
                    return False, f"AS N{k}"
                continue
            one = {"R", "ANDE1", "ANDE2", "ORI1", "ORI2", "BOTE", "DN"}
            two = {"ANDI", "IMPE", "NEGE"}
            if r in one:
                if len(refs) != 1 or not citable(refs[0], k):
                    return False, f"cite N{k}"
                a = f(refs[0])
                ok = {
                    "R": G == a,
                    "ANDE1": isinstance(a, tuple) and a[0] == "&" and a[1] == G,
                    "ANDE2": isinstance(a, tuple) and a[0] == "&" and a[2] == G,
                    "ORI1": isinstance(G, tuple) and G[0] == "v" and G[1] == a,
                    "ORI2": isinstance(G, tuple) and G[0] == "v" and G[2] == a,
                    "BOTE": a == "F",
                    "DN": a == ("~", ("~", G)),
                }[r]
            elif r in two:
                if len(refs) != 2 or not all(citable(j, k) for j in refs):
                    return False, f"cite N{k}"
                a, b = f(refs[0]), f(refs[1])
                ok = {
                    "ANDI": G == ("&", a, b),
                    "IMPE": a == (">", b, G),
                    "NEGE": b == ("~", a) and G == "F",
                }[r]
            elif r in ("IMPI", "NEGI"):
                if len(refs) != 2 or not box(refs[0], refs[1], k):
                    return False, f"box N{k}"
                a, b = f(refs[0]), f(refs[1])
                ok = G == (">", a, b) if r == "IMPI" else (b == "F" and G == ("~", a))
            elif r == "ORE":
                if len(refs) != 5 or not citable(refs[0], k) or not box(refs[1], refs[2], k) or not box(refs[3], refs[4], k):
                    return False, f"ore N{k}"
                j, s1, e1, s2, e2 = (f(t) for t in refs)
                ok = j == ("v", s1, s2) and e1 == G and e2 == G
            else:
                return False, f"rule {r}"
            if not ok:
                return False, f"rule {r} N{k}"
        if npr != len(self.prem):
            return False, "premises"
        lx = L[self.last]
        if lx["d"] != 0 or lx["f"] != self.concl or lx["rule"] == "AS":
            return False, "last line"
        if lx["rule"] == "PR" and len(self.order) > len(self.prem) and False:
            pass
        return True, "ok"
