#!/usr/bin/env python3
"""Reviewer's own shared code for the kalmar-pretrain recount (agent:claude, reviewer, 2026-10-20).

Written independently of the executor's `kalmar/` package: nothing here imports kalmar/, lean_judge, gen, nd_verify.
The construction is re-implemented from nd-rl `dan:code/tools/tt_prover.py` (`prove`, `split`) plus the memo rule as
the pre-registration words it ("a formula already on a line in scope is cited, not re-derived"; a box's last line
must be its conclusion, restated by R if it was found outside).

Formulas (ND prompt syntax): atoms P Q R S, falsum F, '( ~ X )', '( A & B )', '( A v B )', '( A > B )'.
Tree form: ('a', 'P') | ('F',) | ('~', A) | ('&', A, B) | ('v', A, B) | ('>', A, B).
"""
import gzip, itertools, json, os, collections

ROOT = os.environ.get('RV_ROOT', os.path.expanduser('~/review/kalmar-pretrain'))
BIG = os.path.expanduser('~/review/kal_big')
ATOMS = ('P', 'Q', 'R', 'S')
FALSE = ('F',)


def opener(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)


def rows(p):
    with opener(p) as f:
        for l in f:
            if l.strip():
                yield json.loads(l)


# ------------------------------------------------------------------ formulas
def ptoks(t, i=0):
    x = t[i]
    if x == '(':
        if t[i + 1] == '~':
            a, j = ptoks(t, i + 2)
            assert t[j] == ')'
            return ('~', a), j + 1
        a, j = ptoks(t, i + 1)
        op = t[j]
        b, k = ptoks(t, j + 1)
        assert op in ('&', 'v', '>') and t[k] == ')', (t, k)
        return (op, a, b), k + 1
    if x == 'F':
        return FALSE, i + 1
    assert x in ATOMS, x
    return ('a', x), i + 1


def parse(s):
    t = s.split() if isinstance(s, str) else list(s)
    f, j = ptoks(t)
    assert j == len(t), (s, j)
    return f


def show(f):
    """tree -> ND prompt syntax"""
    k = f[0]
    if k == 'a':
        return f[1]
    if k == 'F':
        return 'F'
    if k == '~':
        return f'( ~ {show(f[1])} )'
    return f'( {show(f[1])} {k} {show(f[2])} )'


def split_top(toks):
    out, cur, d = [], [], 0
    for t in toks:
        if t == ',' and d == 0:
            out.append(' '.join(cur)); cur = []; continue
        d += (t == '(') - (t == ')')
        cur.append(t)
    if cur:
        out.append(' '.join(cur))
    return out


def split_prompt(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split('SEQ')
    return split_top(prem.split()), concl.strip()


def split_thm(thm):
    prem, concl = thm.split('|-')
    return split_top(prem.split()), concl.strip()


def sequent(rec):
    if rec.get('prompt'):
        return split_prompt(rec['prompt'])
    return split_thm(rec['thm'])


def val(f, v):
    k = f[0]
    if k == 'a':
        return v[f[1]]
    if k == 'F':
        return False
    if k == '~':
        return not val(f[1], v)
    a, b = val(f[1], v), val(f[2], v)
    return (a and b) if k == '&' else (a or b) if k == 'v' else ((not a) or b)


def atoms_in(fs):
    s = set()

    def go(f):
        if f[0] == 'a':
            s.add(f[1])
        else:
            for g in f[1:]:
                go(g)
    for f in fs:
        go(f)
    return [a for a in ATOMS if a in s]


def valid(prem, goal):
    at = atoms_in(prem + [goal])
    for bits in itertools.product([True, False], repeat=len(at)):
        v = dict(zip(at, bits))
        if all(val(p, v) for p in prem) and not val(goal, v):
            return False
    return True


def size(f):
    """nodes, ¬ counted (atoms, F, connectives)"""
    return 1 + sum(size(g) for g in f[1:]) if f[0] not in ('a', 'F') else 1


def fdepth(f):
    return 0 if f[0] in ('a', 'F') else 1 + max(fdepth(g) for g in f[1:])


# ------------------------------------------------------------------ renaming-class keys (own)
PERMS = list(itertools.permutations('PQRS'))


def _ren(s, m):
    return ' '.join(m.get(t, t) for t in s.split())


def key_inv(prem, concl):
    """premise-order-invariant renaming class: min over the 24 atom bijections of (sorted premises, conclusion)."""
    best = None
    for p in PERMS:
        m = dict(zip('PQRS', p))
        k = (tuple(sorted(_ren(x, m) for x in prem)), _ren(concl, m))
        if best is None or k < best:
            best = k
    return best


def key_set(prem, concl):
    """as key_inv but the premises as a SET (duplicates collapsed)."""
    return key_inv(sorted(set(prem)), concl)


# ------------------------------------------------------------------ the construction (own implementation)
class St:
    """a statement: formula, rule, cited statements, boxes, step-type tag"""
    __slots__ = ('f', 'rule', 'refs', 'boxes', 'tag', 'n')

    def __init__(self, f, rule, refs=(), boxes=(), tag=''):
        self.f, self.rule, self.refs, self.boxes, self.tag, self.n = f, rule, list(refs), list(boxes), tag, None


class Bx:
    __slots__ = ('hyp', 'body', 'tag')

    def __init__(self, f, tag):
        self.hyp, self.body, self.tag = St(f, 'AS', tag=tag), [], tag


class Kal:
    """Kalmár proof of a valid sequent.  variant 'sl': X v ~X derived once per atom at the top; 'pb': in each branch."""

    def __init__(self, prem, goal, variant='sl'):
        self.prem, self.goal, self.variant = prem, goal, variant
        self.top = []
        self.out = self.top
        self.env = [{}]           # formula -> statement, innermost scope last

    def find(self, f):
        for sc in reversed(self.env):
            if f in sc:
                return sc[f]
        return None

    def put(self, f, rule, refs=(), boxes=(), tag=''):
        s = St(f, rule, refs, boxes, tag)
        self.out.append(s)
        if f not in self.env[-1]:
            self.env[-1][f] = s
        return s

    def inbox(self, hyp, tag, fill):
        """box assuming hyp; fill(hyp_stmt) writes the body and returns the statement the box concludes with (None:
        the hypothesis itself); if that statement is not the box's last, an R line restates it."""
        b = Bx(hyp, tag)
        keep = self.out
        self.out = b.body
        self.env.append({hyp: b.hyp})
        c = fill(b.hyp)
        last = b.body[-1] if b.body else b.hyp
        if c is not None and c is not last:
            self.put(c.f, 'R', [c], tag='reit')
        self.env.pop()
        self.out = keep
        return b

    def lemma(self, f, v):
        """Kalmár's lemma: a statement of f if f is true under v, else of ~f (the prover's `prove`)."""
        t = val(f, v)
        want = f if t else ('~', f)
        got = self.find(want)
        if got is not None:
            return got
        k = f[0]
        if k == 'a':
            raise AssertionError('atom not split')
        if k == 'F':
            b = self.inbox(FALSE, 'leaf:bot-', lambda h: None)
            return self.put(want, 'NEGI', boxes=[b], tag='leaf:bot-')
        if k == '~':
            a = self.lemma(f[1], v)
            if t:
                return a
            b = self.inbox(f, 'leaf:not+', lambda h: self.put(FALSE, 'NEGE', [a, h], tag='leaf:not+'))
            return self.put(want, 'NEGI', boxes=[b], tag='leaf:not+')
        x, y = f[1], f[2]
        vx, vy = val(x, v), val(y, v)
        if k == '&':
            if t:
                a = self.lemma(x, v)
                c = self.lemma(y, v)
                return self.put(f, 'ANDI', [a, c], tag='leaf:and+')
            if not vx:
                a = self.lemma(x, v)
                b = self.inbox(f, 'leaf:and-', lambda h: self.put(
                    FALSE, 'NEGE', [self.put(x, 'ANDE1', [h], tag='leaf:and-'), a], tag='leaf:and-'))
            else:
                c = self.lemma(y, v)
                b = self.inbox(f, 'leaf:and-', lambda h: self.put(
                    FALSE, 'NEGE', [self.put(y, 'ANDE2', [h], tag='leaf:and-'), c], tag='leaf:and-'))
            return self.put(want, 'NEGI', boxes=[b], tag='leaf:and-')
        if k == 'v':
            if t:
                if vx:
                    return self.put(f, 'ORI1', [self.lemma(x, v)], tag='leaf:or+')
                return self.put(f, 'ORI2', [self.lemma(y, v)], tag='leaf:or+')
            na = self.lemma(x, v)
            nb = self.lemma(y, v)

            def body(h):
                b1 = self.inbox(x, 'leaf:or-', lambda h1: self.put(FALSE, 'NEGE', [h1, na], tag='leaf:or-'))
                b2 = self.inbox(y, 'leaf:or-', lambda h2: self.put(FALSE, 'NEGE', [h2, nb], tag='leaf:or-'))
                return self.put(FALSE, 'ORE', [h], boxes=[b1, b2], tag='leaf:or-')
            b = self.inbox(f, 'leaf:or-', body)
            return self.put(want, 'NEGI', boxes=[b], tag='leaf:or-')
        # '>'
        if vy:
            c = self.lemma(y, v)
            b = self.inbox(x, 'leaf:imp+B', lambda h: self.put(y, 'R', [c], tag='leaf:imp+B'))
            return self.put(f, 'IMPI', boxes=[b], tag='leaf:imp+B')
        if not vx:
            a = self.lemma(x, v)
            b = self.inbox(x, 'leaf:imp+A', lambda h: self.put(
                y, 'BOTE', [self.put(FALSE, 'NEGE', [h, a], tag='leaf:imp+A')], tag='leaf:imp+A'))
            return self.put(f, 'IMPI', boxes=[b], tag='leaf:imp+A')
        a = self.lemma(x, v)
        nb = self.lemma(y, v)
        b = self.inbox(f, 'leaf:imp-', lambda h: self.put(
            FALSE, 'NEGE', [self.put(y, 'IMPE', [h, a], tag='leaf:imp-'), nb], tag='leaf:imp-'))
        return self.put(want, 'NEGI', boxes=[b], tag='leaf:imp-')

    def em(self, x):
        """X v ~X as the prover derives it: byContradiction (fun h : ~(X v ~X) => h (Or.inr (fun p : X => h (Or.inl p))))"""
        X = ('a', x)
        e = ('v', X, ('~', X))
        got = self.find(e)
        if got is not None:
            return got

        def outer(h):
            inner = self.inbox(X, 'lem', lambda p: self.put(FALSE, 'NEGE', [self.put(e, 'ORI1', [p], tag='lem'), h], tag='lem'))
            nx = self.put(('~', X), 'NEGI', boxes=[inner], tag='lem')
            return self.put(FALSE, 'NEGE', [self.put(e, 'ORI2', [nx], tag='lem'), h], tag='lem')
        nn = self.put(('~', ('~', e)), 'NEGI', boxes=[self.inbox(('~', e), 'lem', outer)], tag='lem')
        return self.put(e, 'DN', [nn], tag='lem')

    def branch_end(self, v):
        for i, p in enumerate(self.prem):
            if not val(p, v):
                np_ = self.lemma(p, v)
                bot = self.put(FALSE, 'NEGE', [self.prs[i], np_], tag='efq')
                return bot if self.goal == FALSE else self.put(self.goal, 'BOTE', [bot], tag='efq')
        return self.lemma(self.goal, v)

    def cases(self, ats, v):
        if not ats:
            return self.branch_end(v)
        x = ats[0]
        e = self.ems[x] if self.variant == 'sl' else self.em(x)
        b1 = self.inbox(('a', x), 'split', lambda h: self.cases(ats[1:], {**v, x: True}))
        b2 = self.inbox(('~', ('a', x)), 'split', lambda h: self.cases(ats[1:], {**v, x: False}))
        return self.put(self.goal, 'ORE', [e], boxes=[b1, b2], tag='split')

    def build(self):
        self.prs = [self.put(p, 'PR', tag='pr') for p in self.prem]
        ats = atoms_in(self.prem + [self.goal])
        if self.variant == 'sl':
            self.ems = {x: self.em(x) for x in ats}
        g = self.cases(ats, {})
        if not self.top or g is not self.top[-1]:
            self.put(self.goal, 'R', [g], tag='reit')
        return self


def nd_text(top):
    """-> (ND body 'N1 ... ; QED', list of (tag, depth) per state-env action, ND box depth max)"""
    out = []
    cnt = [0]
    mx = [0]

    def emit_list(lst, d):
        for s in lst:
            spans = []
            for b in s.boxes:
                cnt[0] += 1
                b.hyp.n = cnt[0]
                mx[0] = max(mx[0], d + 1)
                out.append(f'N{b.hyp.n} ' + '| ' * (d + 1) + f'{show(b.hyp.f)} : AS ;')
                emit_list(b.body, d + 1)
                spans.append((b.hyp.n, (b.body[-1] if b.body else b.hyp).n))
            cnt[0] += 1
            s.n = cnt[0]
            if s.rule == 'ORE':
                refs = [s.refs[0].n] + [i for sp in spans for i in sp]
            elif s.rule in ('IMPI', 'NEGI'):
                refs = list(spans[0])
            else:
                refs = [r.n for r in s.refs]
            out.append(f'N{s.n} ' + '| ' * d + f'{show(s.f)} : {s.rule}' + ''.join(f' N{r}' for r in refs) + ' ;')
    emit_list(top, 0)
    acts = []

    def act_list(lst, d):
        for s in lst:
            acts.append((s.tag, d))
            for b in s.boxes:
                act_list(b.body, d + 1)
                acts.append(('close:' + b.tag, d + 1))
    act_list(top, 0)
    acts.append(('end', 0))
    return ' '.join(out) + ' QED', acts, mx[0]


def kalmar(prompt, variant='sl'):
    prem_s, goal_s = split_prompt(prompt)
    prem, goal = [parse(p) for p in prem_s], parse(goal_s)
    if not valid(prem, goal):
        return None
    k = Kal(prem, goal, variant).build()
    body, acts, md = nd_text(k.top)
    return {'proof': body, 'acts': acts, 'n_lines': body.count(';'), 'max_depth': md,
            'n_atoms': len(atoms_in(prem + [goal]))}


# ------------------------------------------------------------------ ND parsing
def parse_nd(nd):
    """-> list of (idx, depth, formula_str, rule, refs); stops at QED"""
    out = []
    for part in nd.split(' ; '):
        part = part.strip().rstrip(';').strip()
        if not part:
            continue
        if part == 'QED':
            break
        t = part.split()
        idx = int(t[0][1:]); j = 1; depth = 0
        while t[j] == '|':
            depth += 1; j += 1
        c = len(t) - 1 - t[::-1].index(':')
        out.append((idx, depth, ' '.join(t[j:c]), t[c + 1], [int(x[1:]) for x in t[c + 2:]]))
    return out


def unbiased_pass(n, c, k):
    """pass@k from n attempts with c successes (Chen et al. 2021)"""
    if n - c < k:
        return 1.0
    p = 1.0
    for i in range(n - c + 1, n + 1):
        p *= 1 - k / i
    return 1 - p


if __name__ == '__main__':
    import sys
    for pr in sys.argv[1:] or ['THM ( P & Q ) , ( Q > R ) SEQ ( R v S ) PRF']:
        r = kalmar(pr)
        print(r['proof']); print(r['acts'])
