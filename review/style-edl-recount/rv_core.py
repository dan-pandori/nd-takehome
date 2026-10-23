"""Reviewer-owned core for the style-edl review (phase 1).  Independent of the run's code (style_edl/, state_env,
lean_tok, lean_gate, split.py): my own ND parser, my own literal-lean_seq parser (-> ND lines), my own renaming-class
key, my own term size, my own ND -> Lean 4 renderer and a chunked Lean driver.

Formulas are tuples: ('a', 'P') | ('F',) | ('not', X) | ('and', X, Y) | ('or', X, Y) | ('imp', X, Y).
ND line = (depth, formula, rule, refs) with refs 1-based line numbers.
"""
import itertools, json, os, re, subprocess, tempfile, time

WS = os.path.expanduser('~/review/style-edl')          # phase-1 workspace (data + artefacts)
HERE = os.path.dirname(os.path.abspath(__file__))
LEAN = os.path.expanduser('~/.elan/bin/lean')
ATOMS = ('P', 'Q', 'R', 'S')


class Bad(Exception):
    pass


# ---------------------------------------------------------------- formulas
def _pf(toks, i, ops, neg, false):
    if i >= len(toks):
        raise Bad('eof in formula')
    t = toks[i]
    if t == '(':
        if toks[i + 1] == neg:
            a, j = _pf(toks, i + 2, ops, neg, false)
            if toks[j] != ')':
                raise Bad('neg paren')
            return ('not', a), j + 1
        a, j = _pf(toks, i + 1, ops, neg, false)
        op = ops.get(toks[j])
        if op is None:
            raise Bad(f'op {toks[j]}')
        b, j = _pf(toks, j + 1, ops, neg, false)
        if toks[j] != ')':
            raise Bad('bin paren')
        return (op, a, b), j + 1
    if t == false:
        return ('F',), i + 1
    if t in ATOMS:
        return ('a', t), i + 1
    raise Bad(f'formula token {t!r}')


ND_OPS = {'&': 'and', 'v': 'or', '>': 'imp'}
LS_OPS = {'∧': 'and', '∨': 'or', '→': 'imp'}


def nd_formula(toks, i=0):
    return _pf(toks, i, ND_OPS, '~', 'F')


def ls_formula(toks, i=0):
    return _pf(toks, i, LS_OPS, '¬', 'False')


ND_SYM = {'and': '&', 'or': 'v', 'imp': '>'}
LS_SYM = {'and': '∧', 'or': '∨', 'imp': '→'}


def fstr(f):
    """canonical string (ND syntax)"""
    k = f[0]
    if k == 'a':
        return f[1]
    if k == 'F':
        return 'F'
    if k == 'not':
        return f'( ~ {fstr(f[1])} )'
    return f'( {fstr(f[1])} {ND_SYM[k]} {fstr(f[2])} )'


def lean_f(f):
    k = f[0]
    if k == 'a':
        return f[1]
    if k == 'F':
        return 'False'
    if k == 'not':
        return f'(¬{lean_f(f[1])})'
    return f'({lean_f(f[1])} {LS_SYM[k]} {lean_f(f[2])})'


def rename(f, m):
    k = f[0]
    if k == 'a':
        return ('a', m[f[1]])
    if k == 'F':
        return f
    return (k,) + tuple(rename(x, m) for x in f[1:])


def atoms_of(f, acc=None):
    acc = set() if acc is None else acc
    if f[0] == 'a':
        acc.add(f[1])
    else:
        for x in f[1:]:
            if isinstance(x, tuple):
                atoms_of(x, acc)
    return acc


def fsize(f):
    return 1 if f[0] in ('a', 'F') else 1 + sum(fsize(x) for x in f[1:])


# ---------------------------------------------------------------- prompts and renaming classes
def parse_prompt(prompt):
    t = prompt.split()
    if t[0] != 'THM' or t[-1] != 'PRF' or 'SEQ' not in t:
        raise Bad('prompt')
    k = t.index('SEQ')
    body = t[1:k]
    prems = []
    i = 0
    while i < len(body):
        f, j = nd_formula(body, i)
        prems.append(f)
        if j < len(body):
            if body[j] != ',':
                raise Bad('prem sep')
            j += 1
        i = j
    c, j = nd_formula(t, k + 1)
    if j != len(t) - 1:
        raise Bad('concl trail')
    return prems, c


_PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]


def rclass(prompt):
    """renaming class: invariant to any permutation of the atoms P Q R S (F is a constant) and to premise order
    (premises as a sorted multiset)."""
    prems, c = parse_prompt(prompt)
    best = None
    for m in _PERMS:
        k = (tuple(sorted(fstr(rename(p, m)) for p in prems)), fstr(rename(c, m)))
        if best is None or k < best:
            best = k
    return best


def n_atoms(prompt):
    prems, c = parse_prompt(prompt)
    acc = set()
    for f in prems + [c]:
        atoms_of(f, acc)
    return len(acc)


# ---------------------------------------------------------------- ND proofs
RULES = {'PR': 0, 'AS': 0, 'R': 1, 'ANDI': 2, 'ANDE1': 1, 'ANDE2': 1, 'ORI1': 1, 'ORI2': 1, 'ORE': 5, 'IMPI': 2,
         'IMPE': 2, 'NEGI': 2, 'NEGE': 2, 'BOTE': 1, 'DN': 1}


def parse_nd(nd):
    parts = [p.strip() for p in nd.split(' ; ')]
    if parts[-1] != 'QED':
        raise Bad('no QED')
    out = []
    for k, p in enumerate(parts[:-1]):
        t = p.split()
        if t[0] != f'N{k + 1}':
            raise Bad('numbering')
        i = 1
        d = 0
        while t[i] == '|':
            d += 1
            i += 1
        f, j = nd_formula(t, i)
        if t[j] != ':':
            raise Bad('colon')
        rule = t[j + 1]
        if rule not in RULES:
            raise Bad(f'rule {rule}')
        refs = []
        for x in t[j + 2:]:
            if not re.fullmatch(r'N\d+', x):
                raise Bad('ref')
            refs.append(int(x[1:]))
        if len(refs) != RULES[rule]:
            raise Bad('nrefs')
        out.append((d, f, rule, tuple(refs)))
    return out


def nd_text_of(lines):
    """my own ND string (spec format) of a line list, for equality with stored strings."""
    out = []
    for k, (d, f, r, refs) in enumerate(lines):
        out.append(' '.join([f'N{k + 1}'] + ['|'] * d + [fstr(f), ':', r] + [f'N{x}' for x in refs]))
    return ' ; '.join(out + ['QED'])


# ---------------------------------------------------------------- literal lean_seq text -> ND lines
NAME = re.compile(r'n\d+$')


def ls_to_nd(prompt, text):
    """parse a literal lean_seq proof text (the sampler's output format) into ND lines (depth, f, rule, refs).
    Raises Bad on anything outside the grammar.  Names are resolved by lexical scope (inner bindings shadow)."""
    prems, concl = parse_prompt(prompt)
    T = text.split()
    st = {'i': 0}
    lines = []

    def peek(o=0):
        j = st['i'] + o
        return T[j] if j < len(T) else None

    def take(x=None):
        t = peek()
        if t is None or (x is not None and t != x):
            raise Bad(f'expected {x!r} got {t!r} at {st["i"]}')
        st['i'] += 1
        return t

    def fml():
        f, j = ls_formula(T, st['i'])
        st['i'] = j
        return f

    def emit(d, f, r, refs):
        lines.append((d, f, r, tuple(refs)))
        return len(lines)

    def look(scope, nm):
        if nm not in scope:
            raise Bad(f'unbound {nm}')
        return scope[nm]

    def fun_box(d, scope):
        """( fun ( x : A ) => by BODY )  -> (as line, end line, A)"""
        take('('); take('fun'); take('('); x = take()
        if not NAME.match(x):
            raise Bad('binder')
        take(':'); A = fml(); take(')'); take('=>'); take('by')
        a = emit(d + 1, A, 'AS', [])
        e = body(d + 1, dict(scope, **{x: a}))
        take(')')
        return a, e, A

    def term(d, f, scope):
        t = peek()
        if re.fullmatch(r'h\d+', t):
            take(); j = int(t[1:])
            if d != 0 or j < 1 or j > len(prems) or prems[j - 1] != f:
                raise Bad('PR mismatch')
            return emit(d, f, 'PR', [])
        if t == '(':
            a, e, A = fun_box(d, scope)
            if f == ('not', A) and lines[e - 1][1] == ('F',):
                return emit(d, f, 'NEGI', [a, e])
            if f == ('imp', A, lines[e - 1][1]):
                return emit(d, f, 'IMPI', [a, e])
            raise Bad('box type')
        if t == 'Or.elim':
            take(); o = look(scope, take())
            a1, e1, _ = fun_box(d, scope)
            a2, e2, _ = fun_box(d, scope)
            return emit(d, f, 'ORE', [o, a1, e1, a2, e2])
        if t == 'Classical.byContradiction':
            take(); take('('); take('fun'); take('hh'); take('=>'); x = look(scope, take()); take('hh'); take(')')
            return emit(d, f, 'DN', [x])
        if t in ('Or.inl', 'Or.inr'):
            take(); x = look(scope, take())
            return emit(d, f, 'ORI1' if t == 'Or.inl' else 'ORI2', [x])
        if t == '⟨':
            take(); x = look(scope, take()); take(','); y = look(scope, take()); take('⟩')
            return emit(d, f, 'ANDI', [x, y])
        m = re.fullmatch(r'(n\d+)\.(1|2|elim)', t)
        if m:
            take(); x = look(scope, m.group(1))
            return emit(d, f, {'1': 'ANDE1', '2': 'ANDE2', 'elim': 'BOTE'}[m.group(2)], [x])
        if NAME.match(t):
            take(); x = look(scope, t)
            if peek() is not None and NAME.match(peek()):
                y = look(scope, take())
                fx = lines[x - 1][1]
                if fx[0] == 'not':
                    return emit(d, f, 'NEGE', [y, x])
                if fx[0] == 'imp':
                    return emit(d, f, 'IMPE', [x, y])
                raise Bad('application head')
            return emit(d, f, 'R', [x])
        raise Bad(f'term {t!r}')

    def body(d, scope):
        while True:
            t = peek()
            if t == 'have':
                take(); nm = take()
                if not NAME.match(nm):
                    raise Bad('have name')
                take(':'); f = fml(); take(':=')
                ln = term(d, f, scope)
                scope = dict(scope, **{nm: ln})
                take(';')
            elif t == 'exact':
                take()
                if peek() == '(':
                    take(); nm = take(); take(':'); fml(); take(')')
                else:
                    nm = take()
                return look(scope, nm)
            else:
                raise Bad(f'stmt {t!r}')

    e = body(0, {})
    if st['i'] != len(T):
        raise Bad('trailing')
    if e != len(lines):
        raise Bad('final exact is not the last line')
    if lines[-1][0] != 0 or lines[-1][1] != concl:
        raise Bad('last line is not the conclusion')
    return lines


def ls_canon(text):
    """literal text with every n-name shifted so the smallest becomes n1 (removes the sampler's name base)."""
    ns = [int(m) for m in re.findall(r'\bn(\d+)', text)]
    if not ns:
        return text
    b = min(ns) - 1
    return re.sub(r'\bn(\d+)', lambda m: f'n{int(m.group(1)) - b}', text)


# ---------------------------------------------------------------- box structure, pruning, sizes
def boxes(lines):
    """-> dict AS line (1-based) -> list of the box's lines (1-based, incl. the AS line and nested boxes)"""
    n = len(lines)
    out = {}
    for k, (d, f, r, refs) in enumerate(lines):
        if r == 'AS':
            j = k + 1
            while j < n and (lines[j][0] > d or (lines[j][0] == d and lines[j][2] != 'AS')):
                j += 1
            out[k + 1] = list(range(k + 1, j + 1))
    return out


def used_lines(lines):
    """lines reachable from the last line through refs (box citations pull in the whole box up to the cited end)."""
    bx = boxes(lines)
    need = set()
    stack = [len(lines)]
    while stack:
        x = stack.pop()
        if x in need:
            continue
        need.add(x)
        d, f, r, refs = lines[x - 1]
        stack.extend(refs)
    return need


def term_size(lines):
    """my term size: nodes of the proof term over the lines used by the conclusion.  Each used inference line = 1
    node (the rule's constant applied); IMPI / NEGI add 1 (the lambda), ORE adds 2 (its two lambdas), DN = 1
    (byContradiction applied to the cited line).  PR / AS / R lines are variable references and count 0."""
    need = used_lines(lines)
    s = 0
    for x in need:
        r = lines[x - 1][2]
        if r in ('PR', 'AS', 'R'):
            continue
        s += 1 + {'IMPI': 1, 'NEGI': 1, 'ORE': 2}.get(r, 0)
    return s


def n_lines_nd(lines):
    return len(lines)


# ---------------------------------------------------------------- ND -> Lean (my renderer)
def nd_to_lean(prompt, lines, name):
    prems, concl = parse_prompt(prompt)
    bx = boxes(lines)
    n = len(lines)
    # depth sanity (a non-AS line may not be deeper than the innermost open box; AS opens at most one level)
    cur = 0
    for d, f, r, refs in lines:
        if r == 'AS':
            if d < 1 or d > cur + 1:
                raise Bad('AS depth')
        elif d > cur:
            raise Bad('depth jump')
        cur = d
    if lines[-1][0] != 0:
        raise Bad('last line not at depth 0')
    cited = {}
    for k, (d, f, r, refs) in enumerate(lines):
        if any(x >= k + 1 for x in refs):
            raise Bad('forward ref')
        if r in ('IMPI', 'NEGI'):
            cited.setdefault(refs[0], set()).add(refs[1])
        elif r == 'ORE':
            cited.setdefault(refs[1], set()).add(refs[2]); cited.setdefault(refs[3], set()).add(refs[4])
    for s in cited:
        if s not in bx:
            raise Bad('cited box start is not AS')
    hyp = ' '.join(f'(h{j + 1} : {lean_f(p)})' for j, p in enumerate(prems))
    out = [f'theorem {name} (P Q R S : Prop) {hyp} : {lean_f(concl)} := by']

    def own_last(s):
        d = lines[s - 1][0]
        return [x for x in bx[s] if lines[x - 1][0] == d][-1]

    def tm(k):
        d, f, r, refs = lines[k - 1]
        n_ = [f'n{x}' for x in refs]
        if r == 'PR':
            js = [j for j, p in enumerate(prems) if p == f]
            if not js or d != 0:
                raise Bad('PR not a premise')
            return f'h{js[0] + 1}'
        if r in ('IMPI', 'NEGI'):
            return f'b{refs[0]}_{refs[1]}'
        if r == 'ORE':
            return f'Or.elim {n_[0]} b{refs[1]}_{refs[2]} b{refs[3]}_{refs[4]}'
        return {'R': '{0}', 'ANDI': 'And.intro {0} {1}', 'ANDE1': 'And.left {0}', 'ANDE2': 'And.right {0}',
                'ORI1': 'Or.inl {0}', 'ORI2': 'Or.inr {0}', 'IMPE': '{0} {1}', 'NEGE': '{1} {0}',
                'BOTE': 'False.elim {0}', 'DN': 'Classical.byContradiction {0}'}[r].format(*n_)

    def emit(pos, ind):
        i = 0
        while i < len(pos):
            k = pos[i]
            d, f, r, refs = lines[k - 1]
            if r == 'AS':
                body = bx[k]
                for e in sorted(cited.get(k, set()) | {own_last(k)}):
                    out.append(' ' * ind + f'have b{k}_{e} : {lean_f(f)} → {lean_f(lines[e - 1][1])} := by')
                    out.append(' ' * (ind + 2) + f'intro n{k}')
                    emit(body[1:], ind + 2)
                    out.append(' ' * (ind + 2) + f'exact n{e}')
                i += len(body)
                continue
            out.append(' ' * ind + f'have n{k} : {lean_f(f)} := {tm(k)}')
            i += 1
    emit(list(range(1, n + 1)), 2)
    out.append(f'  exact n{n}')
    return '\n'.join(out)


def ls_wrap(prompt, text, name):
    """the literal sampled text wrapped as a theorem (premises h1.., atoms P Q R S, tactic block)."""
    prems, concl = parse_prompt(prompt)
    hyp = ' '.join(f'(h{j + 1} : {lean_f(p)})' for j, p in enumerate(prems))
    return f'theorem {name} (P Q R S : Prop) {hyp} : {lean_f(concl)} := by {text}'


BAD_TOK = re.compile(r'\b(sorry|admit|axiom|decide|native_decide|simp|aesop|tauto|omega|exact\?|apply\?|sorryAx|'
                     r'Classical\.em|Classical\.choice|propext|Quot)\b')
LS_VOCAB = re.compile(r"^(have|exact|fun|by|=>|:=|:|;|\(|\)|⟨|⟩|,|hh|Or\.inl|Or\.inr|Or\.elim|"
                      r"Classical\.byContradiction|n\d+|n\d+\.(?:1|2|elim)|h\d+|P|Q|R|S|False|¬|∧|∨|→)$")


def vocab_ok(text):
    return all(LS_VOCAB.match(t) for t in text.split())


# ---------------------------------------------------------------- Lean driver
PRELUDE = 'set_option maxRecDepth 10000\nset_option maxHeartbeats 2000000\nset_option linter.unusedVariables false\n\n'
ERR = re.compile(r':(\d+):(\d+): error')


def lean_check(sources, chunk=40, tag='x', workers=2, timeout=1800):
    """sources: list of Lean theorem sources (each a full `theorem ...` command, unique names).  -> list of
    (ok: bool, first error line or '').  Chunked files; an error is attributed to the theorem whose line range holds it."""
    os.makedirs(os.path.join(HERE, 'lean_tmp'), exist_ok=True)
    jobs = []
    for c0 in range(0, len(sources), chunk):
        part = sources[c0:c0 + chunk]
        txt = PRELUDE
        ranges = []
        for s in part:
            lo = txt.count('\n') + 1
            txt += s + '\n\n'
            ranges.append((lo, txt.count('\n')))
        fn = os.path.join(HERE, 'lean_tmp', f'{tag}_{c0:06d}.lean')
        open(fn, 'w').write(txt)
        jobs.append((c0, fn, ranges))
    res = [None] * len(sources)
    running = []

    def finish(job, p):
        c0, fn, ranges = job
        outp = p.communicate()[0]
        errs = {}
        for l in outp.splitlines():
            m = ERR.search(l)
            if m and l.startswith(fn):
                errs.setdefault(int(m.group(1)), l[len(fn):][:300])
        for i, (lo, hi) in enumerate(ranges):
            bad = [errs[x] for x in errs if lo <= x <= hi]
            res[c0 + i] = (not bad, bad[0] if bad else '')
        if p.returncode not in (0, 1):
            for i in range(len(ranges)):
                res[c0 + i] = (False, f'lean rc {p.returncode}')
        os.remove(fn)

    for job in jobs:
        while len(running) >= workers:
            for jp in list(running):
                if jp[1].poll() is not None:
                    finish(*jp); running.remove(jp)
            time.sleep(0.05)
        p = subprocess.Popen([LEAN, job[1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        running.append((job, p))
    for jp in running:
        jp[1].wait()
        finish(*jp)
    return res


def jl(fn):
    import gzip
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]
