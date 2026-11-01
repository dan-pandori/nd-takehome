#!/usr/bin/env python3
"""Reviewer (coe-dose01): does any committed text file of the run (or this kit) PRINT a textbook72 theorem?
Per line: map Unicode / Lean notation to the ND ASCII tokens, collect every parseable formula (balanced parenthesised
groups and separator-delimited segments, precedence parser: ~ > & > v > >, right-assoc >), then a tb72 theorem is a hit if,
under one of the 24 atom renamings, its conclusion and every premise occur on that line (0-premise theorems: conclusion
with >= 2 connectives).  Prints file names and hit counts only -- never a statement.
Positive control: the tb72 prompts themselves rendered in three notations must all hit."""
import itertools, json, re, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import REPO, jl, seq_of_prompt, pf, fs, rename, PERMS, lean_f

MAP = [('¬', ' ~ '), ('∨', ' v '), ('∧', ' & '), ('→', ' > '), ('⊥', ' F '), ('False', ' F '), ('⊢', ' |- '), ('\\lnot', ' ~ '),
       ('\\lor', ' v '), ('\\land', ' & '), ('\\to', ' > '), ('\\vdash', ' |- '), ('\\bot', ' F ')]
SEP = re.compile(r'\|-|,|;|:=|:|SEQ|THM|PRF|=>|`|\$')


class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, x=None):
        v = self.peek()
        if x is not None and v != x:
            raise ValueError
        self.i += 1
        return v

    def imp(self):
        a = self.orr()
        if self.peek() == '>':
            self.eat(); return ('imp', a, self.imp())
        return a

    def orr(self):
        a = self.andd()
        while self.peek() == 'v':
            self.eat(); a = ('or', a, self.andd())
        return a

    def andd(self):
        a = self.un()
        while self.peek() == '&':
            self.eat(); a = ('and', a, self.un())
        return a

    def un(self):
        v = self.peek()
        if v == '~':
            self.eat(); return ('not', self.un())
        if v in ('P', 'Q', 'R', 'S'):
            self.eat(); return ('atom', v)
        if v == 'F':
            self.eat(); return ('bot',)
        if v == '(':
            self.eat(); a = self.imp(); self.eat(')'); return a
        raise ValueError


def parse_any(toks):
    if not toks:
        return None
    try:
        p = P(toks); f = p.imp()
        return f if p.i == len(toks) else None
    except (ValueError, IndexError):
        return None


def toks_of(s):
    for a, b in MAP:
        s = s.replace(a, b)
    s = s.replace('(', ' ( ').replace(')', ' ) ')
    return s.split()


def formulas(line):
    out = set()
    t = toks_of(line)
    # balanced groups
    st = []
    for i, x in enumerate(t):
        if x == '(':
            st.append(i)
        elif x == ')' and st:
            j = st.pop()
            f = parse_any(t[j:i + 1])
            if f:
                out.add(fs(f))
    # separator-delimited segments
    s = ' '.join(t)
    for seg in SEP.split(s):
        tt = seg.split()
        # strip unmatched leading ( / trailing )
        while tt and tt[0] == '(' and tt.count('(') > tt.count(')'):
            tt = tt[1:]
        while tt and tt[-1] == ')' and tt.count(')') > tt.count('('):
            tt = tt[:-1]
        f = parse_any(tt)
        if f:
            out.add(fs(f))
    for x in t:
        if x in ('P', 'Q', 'R', 'S'):
            out.add(x)
    return out


def nconn(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + sum(nconn(g) for g in f[1:])


def tb72_variants():
    tb = [x['prompt'] for x in jl(f'{REPO}/data/coe/read1054.jsonl') if x['name'].startswith('textbook_')]
    V = []
    for p in tb:
        pr, c = seq_of_prompt(p)
        P_ = [pf(x) for x in pr]; C = pf(c)
        vs = set()
        for m in PERMS:
            vs.add((tuple(sorted(set(fs(rename(x, m)) for x in P_))), fs(rename(C, m))))
        V.append((len(P_), nconn(C), vs, p))
    return V


def hits_in(lines, V):
    h = 0
    for ln in lines:
        if not any(ch in ln for ch in 'PQRS'):
            continue
        F = formulas(ln)
        for npre, nc, vs, _ in V:
            if npre == 0 and nc < 2:
                continue
            for pre, c in vs:
                if c in F and all(x in F for x in pre):
                    h += 1
                    break
    return h


def main(paths):
    V = tb72_variants()
    # positive control: each tb72 theorem rendered (a) as its ND prompt, (b) in Lean statement notation, (c) as 'A, B ⊢ C' Unicode
    ctl = []
    for _, _, _, p in V:
        pr, c = seq_of_prompt(p)
        ctl.append(p)
        ctl.append(' '.join(f'(h{i} : {lean_f(pf(x))})' for i, x in enumerate(pr)) + f' : {lean_f(pf(c))} := by')
        ctl.append(', '.join(lean_f(pf(x)).replace('(', '').replace(')', '') if False else lean_f(pf(x)) for x in pr) + f' ⊢ {lean_f(pf(c))}')
    eligible = sum(1 for npre, nc, _, _ in V if not (npre == 0 and nc < 2))
    print(f'positive control: {hits_in(ctl, V)} hits on {len(ctl)} rendered lines (expect >= {3 * eligible}: {eligible} eligible theorems x 3 notations)')
    tot = 0
    for fn in paths:
        try:
            lines = open(fn, errors='ignore').read().splitlines()
        except (IsADirectoryError, FileNotFoundError):
            continue
        h = hits_in(lines, V)
        tot += h
        if h:
            print(f'HIT {h} line(s): {fn}')
    print(f'scanned {len(paths)} files; total hit lines {tot}')


if __name__ == '__main__':
    main(sys.argv[1:])
