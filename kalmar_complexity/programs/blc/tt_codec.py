#!/usr/bin/env python3
"""Encodings for the K-tt programs (README.md documents them).

Lean alphabet: the tokens of tt_prover.py's output in the order they first occur in its source (solve's header, lean(),
prove()'s cases in order, split()).  Hypothesis names are a letter applied to an index: `hN` to a Church numeral
(h1, h2, h3: premises), `hA` to an atom index (hP ... hS: case-split hypotheses).  The text is
the tokens joined by single spaces, except: no space after ( ¬ ⟨ ; no space before ) ⟩ , .1 .2 ; and the token after
:= is preceded by a newline and two spaces.

Proof-term tree (K-tt algorithm output = renderer input), Church-encoded with 15 constructors (one per case of
tt_prover's split / prove, the tags of the sibling Python program in parentheses):
    \\Spl Efq Hyp Bot Pass NN AndI AndL AndR OrL OrR OrN ImpB ImpA ImpN. tree
    Spl k y n   (s) case split on atom k (atom index), y / n the two branches
    Efq i p     (e) ex falso with premise i (1-based, Church) and p : the proof of its negation
    and for a formula f with truth value t (Church boolean) in the branch:
    Hyp f t (h)  Bot f t (b)  Pass f t a (p)  NN f t a (n)  AndI f t a b (&)  AndL f t a (l)  AndR f t b (r)
    OrL f t a (L)  OrR f t b (R)  OrN f t a b (o)  ImpB f t b (B)  ImpA f t a (A)  ImpN f t a b (i)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nd_codec  # noqa: E402,F401  (sets sys.path)
import blc  # noqa: E402

LEAN_ALPHABET = ['theorem', 't', '(', 'P', 'Q', 'R', 'S', ':', 'Prop', ')', 'hN', ':=',
                 'False', '¬', '∧', '∨', '→',
                 'hA', 'fun', 'h', '=>', '⟨', ',', '⟩', '.1', '.2', 'Or.inl', 'Or.inr', 'Or.elim',
                 '_', 'z', 'False.elim', 'Classical.byContradiction', 'p']
NO_SPACE_AFTER = {'(', '¬', '⟨'}
NO_SPACE_BEFORE = {')', '⟩', ',', '.1', '.2'}
TAGS = ['Spl', 'Efq', 'Hyp', 'Bot', 'Pass', 'NN', 'AndI', 'AndL', 'AndR', 'OrL', 'OrR', 'OrN', 'ImpB', 'ImpA', 'ImpN']
NKIDS = {'Pass': 1, 'NN': 1, 'AndI': 2, 'AndL': 1, 'AndR': 1, 'OrL': 1, 'OrR': 1, 'OrN': 2, 'ImpB': 1, 'ImpA': 1,
         'ImpN': 2, 'Hyp': 0, 'Bot': 0}


def join(tokens):
    out = []
    for i, tok in enumerate(tokens):
        if i:
            prev = tokens[i - 1]
            if prev in NO_SPACE_AFTER or tok in NO_SPACE_BEFORE:
                pass
            elif prev == ':=':
                out.append('\n  ')
            else:
                out.append(' ')
        out.append(tok)
    return ''.join(out)


NUMBERED = {'hN': lambda m, th: f'h{blc.dec_church(m, th)}', 'hA': lambda m, th: 'h' + 'PQRS'[blc.dec_atom_index(m, th)]}


def lean_word_tokens(dec_tokens):
    """decoded word tokens are already Lean tokens (kept for compatibility)"""
    return list(dec_tokens)


# ---- Python reference: the tree and its rendering ----

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


def tree(prem, goal):
    def prove(f, v):
        t = val(f, v)
        k = f[0]
        if k == 'atom':
            return ('Hyp', f, t)
        if k == 'bot':
            return ('Bot', f, t)
        if k == 'not':
            return ('Pass' if t else 'NN', f, t, prove(f[1], v))
        x, y = f[1], f[2]
        vx, vy = val(x, v), val(y, v)
        if k == 'and':
            return ('AndI', f, t, prove(x, v), prove(y, v)) if t else \
                ('AndL', f, t, prove(x, v)) if not vx else ('AndR', f, t, prove(y, v))
        if k == 'or':
            return (('OrL', f, t, prove(x, v)) if vx else ('OrR', f, t, prove(y, v))) if t else \
                ('OrN', f, t, prove(x, v), prove(y, v))
        if vy:
            return ('ImpB', f, t, prove(y, v))
        if not vx:
            return ('ImpA', f, t, prove(x, v))
        return ('ImpN', f, t, prove(x, v), prove(y, v))

    def split(atoms, v):
        if not atoms:
            for i, p in enumerate(prem):
                if not val(p, v):
                    return ('Efq', i + 1, prove(p, v))
            return prove(goal, v)
        x = atoms[0]
        return ('Spl', 'PQRS'.index(x), split(atoms[1:], {**v, x: True}), split(atoms[1:], {**v, x: False}))

    def occ(x, f):
        return f == ('atom', x) or (f[0] not in ('atom', 'bot') and any(occ(x, g) for g in f[1:]))
    atoms = [x for x in 'PQRS' if any(occ(x, f) for f in prem + [goal])]
    return split(atoms, {})


def lean_f(f):
    t = f[0]
    if t == 'atom':
        return [f[1]]
    if t == 'bot':
        return ['False']
    if t == 'not':
        return ['¬'] + lean_f(f[1])
    return ['('] + lean_f(f[1]) + [{'and': '∧', 'or': '∨', 'imp': '→'}[t]] + lean_f(f[2]) + [')']


def render(tr, prem, goal):
    def asc(f, t, body):
        return ['('] + body + [':'] + (lean_f(f) if t else ['¬'] + lean_f(f)) + [')']

    def fh(v, ty, body):
        return ['fun', v, ':'] + ty + ['=>'] + body

    def go(n):
        tag = n[0]
        if tag == 'Spl':
            X = 'PQRS'[n[1]]
            em = ['(', 'Classical.byContradiction', '(', 'fun', 'h', ':', '¬', '(', X, '∨', '¬', X, ')', '=>', 'h',
                  '(', 'Or.inr', '(', 'fun', 'p', ':', X, '=>', 'h', '(', 'Or.inl', 'p', ')', ')', ')', ')', ':', X,
                  '∨', '¬', X, ')']
            return ['Or.elim'] + em + ['('] + fh('h' + X, [X], go(n[2])) + [')', '('] + \
                fh('h' + X, ['¬', X], go(n[3])) + [')']
        if tag == 'Efq':
            return ['(', 'False.elim', '('] + go(n[2]) + [f'h{n[1]}', ')', ':'] + lean_f(goal) + [')']
        f, t = n[1], n[2]
        kids = [go(c) for c in n[3:]]
        g = lean_f(f)
        if tag == 'Hyp':
            body = ['h' + f[1]]
        elif tag == 'Bot':
            body = fh('h', ['False'], ['h'])
        elif tag == 'Pass':
            body = kids[0]
        elif tag == 'NN':
            body = fh('h', g, ['h'] + kids[0])
        elif tag == 'AndI':
            body = ['⟨'] + kids[0] + [','] + kids[1] + ['⟩']
        elif tag == 'AndL':
            body = fh('h', g, kids[0] + ['h', '.1'])
        elif tag == 'AndR':
            body = fh('h', g, kids[0] + ['h', '.2'])
        elif tag == 'OrL':
            body = ['Or.inl'] + kids[0]
        elif tag == 'OrR':
            body = ['Or.inr'] + kids[0]
        elif tag == 'OrN':
            body = fh('h', g, ['Or.elim', 'h'] + kids[0] + kids[1])
        elif tag == 'ImpB':
            body = fh('_', lean_f(f[1]), kids[0])
        elif tag == 'ImpA':
            body = fh('z', lean_f(f[1]), ['False.elim', '('] + kids[0] + ['z', ')'])
        else:
            body = fh('h', g, kids[1] + ['(', 'h'] + kids[0] + [')'])
        return asc(f, t, body)
    head = ['theorem', 't', '(', 'P', 'Q', 'R', 'S', ':', 'Prop', ')']
    for i, p in enumerate(prem):
        head += ['(', f'h{i + 1}', ':'] + lean_f(p) + [')']
    return head + [':'] + lean_f(goal) + [':='] + go(tr)


# ---- lambda encodings of the tree ----

def enc_tree(tr):
    K = 15

    def go(n):
        tag = n[0]
        head = (0, K - TAGS.index(tag))
        if tag == 'Spl':
            args = [blc.enc_atom_index(n[1]), go(n[2]), go(n[3])]
        elif tag == 'Efq':
            args = [blc.enc_church(n[1]), go(n[2])]
        else:
            args = [blc.enc_formula(n[1]), blc.enc_bool(n[2])] + [go(c) for c in n[3:]]
        for a in args:
            head = (2, head, a)
        return head
    return blc._lam(K, go(tr))


def dec_tree(m, th):
    ms = m.markers(15)
    ids = {x[1]: TAGS[i] for i, x in enumerate(ms)}

    def go(th):
        r = m.apply(th, ms) if th is None else m.force(th)
        return node(r)

    def node(r):
        blc._expect_neu(r, 'tree')
        tag = ids.get(r[1])
        if tag is None:
            raise ValueError('tree: unknown head')
        a = r[2]
        if tag == 'Spl':
            if len(a) != 3:
                raise ValueError('Spl arity')
            return ('Spl', blc.dec_atom_index(m, a[0]), node(m.force(a[1])), node(m.force(a[2])))
        if tag == 'Efq':
            if len(a) != 2:
                raise ValueError('Efq arity')
            return ('Efq', blc.dec_church(m, a[0]), node(m.force(a[1])))
        if len(a) != 2 + NKIDS[tag]:
            raise ValueError(f'{tag} arity {len(a)}')
        return (tag, blc.dec_formula(m, a[0]), blc.dec_bool(m, a[1])) + tuple(node(m.force(c)) for c in a[2:])
    return node(m.apply(th, ms))


if __name__ == '__main__':
    from nd2lean import parse_prompt
    from kalmar_complexity.common import sample_prompts, ref_tt
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    ok = 0
    for p in sample_prompts(n):
        prem, goal = parse_prompt(p)
        got = join(render(tree(prem, goal), prem, goal))
        if got == ref_tt(p):
            ok += 1
        else:
            print('MISMATCH', p)
            print(got[:500])
            print(ref_tt(p)[:500])
            break
    print(f'{ok}/{n}')
