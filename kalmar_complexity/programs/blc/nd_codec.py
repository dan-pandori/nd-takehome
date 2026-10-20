#!/usr/bin/env python3
"""Encodings specific to the ND programs (README.md documents them).

ND alphabet (words, both the prompt and the proof): tokenizer.py's SYMS, then the number letter N, then tokenizer.py's
RULES.  A number token N17 is the letter N applied to the Church numeral 17.

Structured proof (K-sl algorithm output = renderer input):
    \\L e PR AS R ANDI ANDE1 ANDE2 IMPE IMPI ORI1 ORI2 ORE NEGE NEGI BOTE DN.  L n1 d1 f1 r1 c1 (L n2 ... (... e))
one L per line in proof order; n line number, d depth (Church), f formula, r one of the 15 rule variables,
c cited line numbers as a Church list  \\c z. c a (c b z).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar'))
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity', 'ref'))

import blc  # noqa: E402

SYMS = ['THM', ',', 'SEQ', 'PRF', 'QED', '|', ':', ';', '(', ')', '~', '&', 'v', '>', 'P', 'Q', 'R', 'S', 'F']
RULES = ['PR', 'AS', 'R', 'ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'IMPI', 'ORI1', 'ORI2', 'ORE', 'NEGE', 'NEGI', 'BOTE', 'DN']
ND_ALPHABET = SYMS + ['N'] + RULES


# ---- structured proof ----

def enc_church_list(xs):
    body = (0, 1)
    for x in reversed(xs):
        body = (2, (2, (0, 2), blc.enc_church(x)), body)
    return (1, (1, body))


def dec_church_list(m, th):
    c, z = m.marker(), m.marker()
    out = []
    r = m.apply(th, [c, z])
    while True:
        blc._expect_neu(r, 'church list')
        if r[1] == z[1] and not r[2]:
            return out
        if r[1] != c[1] or len(r[2]) != 2:
            raise ValueError('not a Church list')
        out.append(blc.dec_church(m, r[2][0]))
        r = m.force(r[2][1])


def enc_proof(lines):
    """lines: (n, d, formula, rule, refs) -> structured proof term"""
    t = (0, 16)                                   # e
    for n, d, f, rule, refs in reversed(lines):
        ln = (0, 17)                              # L
        for a in (blc.enc_church(n), blc.enc_church(d), blc.enc_formula(f), (0, 15 - RULES.index(rule)),
                  enc_church_list(refs), t):
            ln = (2, ln, a)
        t = ln
    return blc._lam(17, t)


def dec_proof(m, th):
    mL, me = m.marker(), m.marker()
    mr = m.markers(15)
    rid = {x[1]: RULES[i] for i, x in enumerate(mr)}
    out = []
    r = m.apply(th, [mL, me] + mr)
    while True:
        blc._expect_neu(r, 'proof')
        if r[1] == me[1] and not r[2]:
            return out
        if r[1] != mL[1] or len(r[2]) != 6:
            raise ValueError(f'proof: bad line head ({len(r[2])} args)')
        a = r[2]
        n = blc.dec_church(m, a[0])
        d = blc.dec_church(m, a[1])
        f = blc.dec_formula(m, a[2])
        rr = m.force(a[3])
        if rr[0] != blc.NEU or rr[1] not in rid or rr[2]:
            raise ValueError('proof: bad rule')
        refs = dec_church_list(m, a[4])
        out.append((n, d, f, rid[rr[1]], refs))
        r = m.force(a[5])


# ---- Python rendering of a decoded structured proof (reference for the BLC renderer) ----

def fnd_toks(f):
    t = f[0]
    if t == 'atom':
        return [f[1]]
    if t == 'bot':
        return ['F']
    if t == 'not':
        return ['(', '~'] + fnd_toks(f[1]) + [')']
    return ['('] + fnd_toks(f[1]) + [{'and': '&', 'or': 'v', 'imp': '>'}[t]] + fnd_toks(f[2]) + [')']


def render_py(lines):
    out = []
    for n, d, f, rule, refs in lines:
        out += [f'N{n}'] + ['|'] * d + fnd_toks(f) + [':', rule] + [f'N{r}' for r in refs] + [';']
    return out + ['QED']


def prompt_word(prompt):
    return blc.enc_word(prompt.split(), ND_ALPHABET)


def proof_tokens_to_word(toks):
    out = []
    for t in toks:
        if t[0] == 'N' and t[1:].isdigit():
            out.append(('N', int(t[1:])))
        else:
            out.append(t)
    return blc.enc_word(out, ND_ALPHABET)
