"""Reviewer's own helpers (state-cap12 review). Independent of the executor's analysis code."""
import json, gzip, itertools, re

ATOMS = ('P', 'Q', 'R', 'S')


def rd(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                yield json.loads(l)


def parse_prompt(p):
    """'THM a , b SEQ c PRF' -> ([premise token lists], goal tokens). Commas only split at depth 0."""
    t = p.split()
    assert t[0] == 'THM' and t[-1] == 'PRF', p
    t = t[1:-1]
    i = t.index('SEQ') if 'SEQ' in t else None
    # SEQ is never inside a formula
    lhs, goal = t[:i], t[i + 1:]
    prem, cur, d = [], [], 0
    for x in lhs:
        if x == '(':
            d += 1
        elif x == ')':
            d -= 1
        if x == ',' and d == 0:
            prem.append(cur); cur = []
        else:
            cur.append(x)
    if cur:
        prem.append(cur)
    return prem, goal


LEANSYM = {'v': '∨', '&': '∧', '>': '→', '~': '¬', 'F': 'False'}


def to_lean(toks):
    return ' '.join(LEANSYM.get(x, x) for x in toks)


def header(prompt):
    prem, goal = parse_prompt(prompt)
    hyps = ' '.join(f'(h{i + 1} : {to_lean(p)})' for i, p in enumerate(prem))
    return f'theorem t (P Q R S : Prop) {hyps} : {to_lean(goal)} := by'


def class_key(prompt):
    """renaming class, invariant to atom renaming AND premise order (min over the 24 atom permutations of
    (sorted premises, goal))."""
    prem, goal = parse_prompt(prompt)
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        ren = lambda ts: ' '.join(m.get(x, x) for x in ts)
        k = (tuple(sorted(set(ren(p) for p in prem))), ren(goal))
        if best is None or k < best:
            best = k
    return best


def class_key_thm(thm):
    """same key from the 'thm' field  'a , b |- c'."""
    lhs, rhs = thm.split('|-')
    return class_key('THM ' + lhs.strip() + ' SEQ ' + rhs.strip() + ' PRF')


TYPE_HAVE = re.compile(r'have (\w+) : .*?:=')


def strip_types(text):
    """remove every type ascription of the literal lean_seq text: `have n : T :=` -> `have n :=`,
    `fun ( n : T ) =>` -> `fun n =>`.  Types are balanced paren groups or single atoms."""
    toks = text.split()
    out, i = [], 0
    while i < len(toks):
        x = toks[i]
        if x == ':' and i > 0:
            # skip the type: until ':=' (have) or the ')' that closes a binder '( n : T )'
            j = i + 1; d = 0
            while j < len(toks):
                y = toks[j]
                if d == 0 and y in (':=',):
                    break
                if y == '(':
                    d += 1
                elif y == ')':
                    if d == 0:
                        break
                    d -= 1
                j += 1
            i = j; continue
        out.append(x); i += 1
    return out


KEYWORDS = {'have', ':=', ';', 'by', 'exact', 'fun', '=>', '(', ')', ',', '⟩'}


def term_size(text):
    """number of proof-term atoms after stripping types: hypothesis names, constants (Or.elim, Or.inl, absurd, ...),
    anonymous constructors (⟨ counts 1), binders (the bound name counts 1).  Invariant to line layout."""
    return sum(1 for x in strip_types(text) if x not in KEYWORDS)


def n_haves(text):
    return len(re.findall(r'\bhave\b', text))
