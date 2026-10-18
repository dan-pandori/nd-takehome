#!/usr/bin/env python3
"""Render a pruned ND proof as a readable Lean 4 proof term (core Lean, no tactics), for the canonical examples.

One Lean construct per ND inference: →E application, ∧E `.1`/`.2`, ∧I `⟨a, b⟩`, ∨I `Or.inl`/`Or.inr`, ∨E `h.elim (fun ..)
(fun ..)`, ¬E application (¬A is A → False), →I / ¬I `fun`, ex falso `False.elim`, and double-negation elimination
`Classical.byContradiction`; a ¬I box consumed by DN (the reductio) is rendered as `Classical.byContradiction (fun (x : ¬G)
=> ..)`.  A derived line cited twice becomes a `have` (lemma reuse); other lines are inlined.  Introduction forms in a
position where Lean must infer their type get a type ascription.  Every rendering is checked by lean_check (the
free-form judge: allowlist + axioms + no errors) before it is shown anywhere.

  python3 proof_strategies/lean_render.py --selftest     # render + Lean-check the 35 unit-test proofs
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from patterns import parse, prune_lines            # noqa: E402
from strategies import Proof                       # noqa: E402
from minlen import parse_thm                       # noqa: E402

PREC = {'imp': 25, 'or': 30, 'and': 35}
SYM = {'imp': '→', 'or': '∨', 'and': '∧'}


def lean_f(f, ctx=0):
    """formula tuple -> Lean syntax with minimal parentheses (∧ 35, ∨ 30, → 25, all right-associative; ¬ binds tightest)."""
    t = f[0]
    if t == 'atom':
        return f[1]
    if t == 'bot':
        return 'False'
    if t == 'not':
        inner = lean_f(f[1], 100)
        return '¬' + inner
    p = PREC[t]
    s = f'{lean_f(f[1], p + 1)} {SYM[t]} {lean_f(f[2], p)}'
    return f'({s})' if p < ctx else s


def atoms(f, acc):
    if f[0] == 'atom':
        acc.add(f[1])
    for g in f[1:]:
        if isinstance(g, tuple):
            atoms(g, acc)
    return acc


class T:
    """a term: text pieces plus whether it is an introduction form (needs an ascription in inference position)."""

    def __init__(self, head, kids=(), intro=False, multiline=False):
        self.head, self.kids, self.intro, self.multiline = head, list(kids), intro, multiline


class Renderer:
    def __init__(self, prompt, proof):
        self.prem, self.concl = parse_thm(prompt)
        self.lines = prune_lines(parse(proof))
        self.P = Proof(self.lines, (self.prem, self.concl))
        self.by = self.P.by
        self.names = {}
        k = 0
        for ln in self.lines:
            if ln['rule'] == 'PR':
                k += 1
                self.names[ln['idx']] = f'h{k}'
        n_as = 0
        for ln in self.lines:
            if ln['rule'] == 'AS':
                n_as += 1
                self.names[ln['idx']] = f'a{n_as}'
        # shared derived lines -> have
        self.shared = {i for i, c in self.P.citers.items() if len(c) >= 2 and self.by[i]['rule'] not in ('PR', 'AS', 'R')}
        for i in self.shared:
            self.names[i] = f'l{i}'
        self.ind = []             # indentation stack of the scope being rendered

    # ---------------------------------------------------------------- terms
    def ref(self, i):
        """term for citing line i (follow R)."""
        o = self.P.origin(i)
        if o['idx'] in self.names:
            return self.names[o['idx']]
        return self.term(o)

    def synth(self, i, dot=False):
        """a cited term in a position where Lean infers its type: ascribe introduction forms; before dot notation
        (`.1`, `.elim`) parenthesise any compound term."""
        o = self.P.origin(i)
        t = self.ref(i)
        if isinstance(t, str):
            return t
        if t[1]:
            return f'({t[0]} : {lean_f(o["formula"])})'
        if t[0].startswith('fun') or (dot and (' ' in t[0] or '\n' in t[0])):
            return f'({t[0]})'
        return t[0]

    def check(self, i):
        t = self.ref(i)
        return t if isinstance(t, str) else t[0]

    def box(self, s, e, ind):
        """render box s..e as `fun (a : A) => body`."""
        name = self.names[s]
        body = self.scope(s, e, ind)
        hyp = lean_f(self.by[s]['formula'])
        return f'fun ({name} : {hyp}) =>' + body

    def scope(self, s, e, ind):
        """the haves of a box (lines strictly inside s..e at the box's own depth that are shared) and its result."""
        d = self.by[s]['depth'] if s else 0
        haves = [ln for ln in self.lines if (s or 0) < ln['idx'] <= e and ln['depth'] == d and ln['idx'] in self.shared
                 and ln['idx'] != self.P.origin(e)['idx']]
        self.ind.append(ind)
        res = self.ref(e)
        res = res if isinstance(res, str) else res[0]
        self.ind.pop()
        pad = ' ' * ind
        if not haves and '\n' not in res and len(res) < 70:
            return ' ' + res
        out = ''
        for ln in haves:
            self.ind.append(ind + 2)
            t = self.term(ln)
            self.ind.pop()
            out += f'\n{pad}have {self.names[ln["idx"]]} : {lean_f(ln["formula"])} := {t[0]}'
        return out + f'\n{pad}{res}'

    def term(self, ln):
        """-> (text, is_intro_form) for the inference at line ln."""
        r, refs = ln['rule'], ln['refs']
        ind = self.ind[-1] if self.ind else 2
        if r == 'PR' or r == 'AS':
            return (self.names[ln['idx']], False)
        if r == 'R':
            return (self.check(refs[0]), False)
        if r == 'ANDI':
            return (f'⟨{self.check(refs[0])}, {self.check(refs[1])}⟩', True)
        if r in ('ANDE1', 'ANDE2'):
            return (f'{self.synth(refs[0], dot=True)}.{1 if r == "ANDE1" else 2}', False)
        if r == 'IMPE':
            return (f'{self.synth(refs[0])} {self.arg(refs[1])}', False)
        if r == 'NEGE':
            return (f'{self.synth(refs[1])} {self.arg(refs[0])}', False)
        if r in ('ORI1', 'ORI2'):
            return (f'Or.{"inl" if r == "ORI1" else "inr"} {self.arg(refs[0])}', True)
        if r == 'BOTE':
            return (f'False.elim {self.arg(refs[0])}', True)
        if r in ('IMPI', 'NEGI'):
            return (self.box(refs[0], refs[1], ind + 2), True)
        if r == 'ORE':
            j, s1, e1, s2, e2 = refs
            b1 = self.box(s1, e1, ind + 4)
            b2 = self.box(s2, e2, ind + 4)
            pad = ' ' * (ind + 2)
            return (f'{self.synth(j, dot=True)}.elim\n{pad}({b1})\n{pad}({b2})', True)
        if r == 'DN':
            c = self.P.origin(refs[0])
            if c['rule'] == 'NEGI' and c['idx'] not in self.names:
                return (f'Classical.byContradiction ({self.box(c["refs"][0], c["refs"][1], ind + 2)})', True)
            return (f'Classical.byContradiction {self.arg(refs[0])}', True)
        raise ValueError(r)

    def arg(self, i):
        """a cited term in argument position: parenthesise compound terms."""
        t = self.ref(i)
        if isinstance(t, str):
            return t
        s = t[0]
        return s if (' ' not in s and '\n' not in s) or s.startswith('⟨') else f'({s})'

    def render(self, name='t', kind='theorem'):
        used = set()
        for f in list(self.prem) + [self.concl] + [ln['formula'] for ln in self.lines]:
            atoms(f, used)
        atom_s = ' '.join(a for a in 'PQRS' if a in used)
        hyps = ' '.join(f'(h{k + 1} : {lean_f(p)})' for k, p in enumerate(self.prem))
        head = (f'{kind} {name}' if name else kind) + (f' ({atom_s} : Prop)' if atom_s else '') + (f' {hyps}' if hyps else '') + f' : {lean_f(self.concl)} :='
        body = self.scope(0, self.lines[-1]['idx'], 2)
        return head + body


def render(prompt, proof, name='t', kind='theorem'):
    return Renderer(prompt, proof).render(name, kind)


def selftest():
    import lean_check
    from test_strategies import CASES
    srcs = [render(p, pr) for _, p, pr, *_ in CASES]
    res, wall, proc = lean_check.check(srcs)
    bad = [(c[0], s, x['reason']) for c, s, x in zip(CASES, srcs, res) if not x['ok']]
    for b in bad:
        print('FAIL', b[0], '\n', b[1], '\n', b[2][:300])
    print(f'lean_render selftest: {len(srcs) - len(bad)} / {len(srcs)} accepted by lean_check')
    return not bad


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--one')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.one:
        p, pr = a.one.split(' PRF ', 1)
        print(render(p + ' PRF', pr, kind='example', name=''))
