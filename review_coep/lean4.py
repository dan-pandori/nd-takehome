"""review_coep/lean4.py -- the reviewer's own Lean 4 harness (independent of lean_gate / lean_judge / nd2lean / lean_tok /
review_coe.rlean, which the executor's C5 used).

* stmt(prompt): `THM p1 , p2 SEQ c PRF` (ND tokens) -> Lean header `(P Q R S : Prop) (h1 : ..) .. : C` (own parser).
* nd_to_tactic(nd): an ND proof (spec.md format) -> a Lean tactic text (own renderer: one `have` per line, boxes as
  `fun (x : A) => by ...`, DN as `Classical.byContradiction`).
* check(items): items = [(header, tactic_text)] -> [bool]. One theorem per line, each followed by its own
  `#print axioms`; pass iff no `error` on the theorem's line or on its `#print` line, exactly one axioms report, and
  axioms within {propext, Classical.choice, Quot.sound}. Crashed / timed-out files are split recursively; numbering
  is local to the file being written, so a split cannot misalign names (review-harness-negative-controls).
"""
import os, re, subprocess, tempfile, concurrent.futures

LEAN = os.environ.get('RV_LEAN', os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean'))
OK_AX = {'propext', 'Classical.choice', 'Quot.sound'}
PRELUDE = 'set_option linter.unusedVariables false\nset_option maxRecDepth 4000\n'
CHUNK = int(os.environ.get('RV_CHUNK', '300'))
WORKERS = int(os.environ.get('RV_WORKERS', '2'))

# ---------------- formulas (ND token format) ----------------
ATOMS = {'P', 'Q', 'R', 'S'}
BIN = {'&': '∧', 'v': '∨', '>': '→'}


def parse_f(toks, i=0):
    """-> (tree, next index). tree: ('a', X) | ('bot',) | ('not', t) | (op, t1, t2)"""
    t = toks[i]
    if t in ATOMS:
        return ('a', t), i + 1
    if t == 'F':
        return ('bot',), i + 1
    if t != '(':
        raise ValueError(f'formula token {t!r}')
    if toks[i + 1] == '~':
        a, j = parse_f(toks, i + 2)
        if toks[j] != ')':
            raise ValueError('neg )')
        return ('not', a), j + 1
    a, j = parse_f(toks, i + 1)
    op = toks[j]
    if op not in BIN:
        raise ValueError(f'op {op!r}')
    b, k = parse_f(toks, j + 1)
    if toks[k] != ')':
        raise ValueError('bin )')
    return (op, a, b), k + 1


def F(s):
    toks = s.split()
    f, j = parse_f(toks, 0)
    if j != len(toks):
        raise ValueError(f'trailing tokens in {s!r}')
    return f


def lean_f(f):
    if f[0] == 'a':
        return f[1]
    if f[0] == 'bot':
        return 'False'
    if f[0] == 'not':
        return f'(¬ {lean_f(f[1])})'
    return f'({lean_f(f[1])} {BIN[f[0]]} {lean_f(f[2])})'


def split_top(toks, sep):
    """split a token list on `sep` at parenthesis depth 0"""
    out, cur, d = [], [], 0
    for t in toks:
        if t == '(':
            d += 1
        elif t == ')':
            d -= 1
        if t == sep and d == 0:
            out.append(cur); cur = []
        else:
            cur.append(t)
    out.append(cur)
    return out


def sequent(prompt):
    toks = prompt.split()
    assert toks[0] == 'THM' and toks[-1] == 'PRF', prompt
    toks = toks[1:-1]
    k = toks.index('SEQ')
    prem = [F(' '.join(p)) for p in split_top(toks[:k], ',')] if k > 0 else []
    return prem, F(' '.join(toks[k + 1:]))


def stmt(prompt):
    prem, concl = sequent(prompt)
    hs = ''.join(f' (h{j + 1} : {lean_f(p)})' for j, p in enumerate(prem))
    return f'(P Q R S : Prop){hs} : {lean_f(concl)}'


# ---------------- ND -> Lean tactic text ----------------
LINE = re.compile(r'^N(\d+)$')


def parse_nd(nd):
    """-> list of dict(idx, depth, f, rule, refs)"""
    body = nd.strip()
    if body.endswith('QED'):
        body = body[:-3]
    out = []
    for part in body.split(';'):
        toks = part.split()
        if not toks:
            continue
        m = LINE.match(toks[0])
        if not m:
            raise ValueError(f'line head {toks[0]!r}')
        d = 0
        j = 1
        while toks[j] == '|':
            d += 1; j += 1
        c = toks.index(':', j)
        f = F(' '.join(toks[j:c]))
        rule = toks[c + 1]
        refs = []
        for r in toks[c + 2:]:
            mm = LINE.match(r)
            if not mm:
                raise ValueError(f'ref {r!r}')
            refs.append(int(mm.group(1)))
        out.append(dict(idx=int(m.group(1)), depth=d, f=f, rule=rule, refs=refs))
    return out


def nd_to_tactic(nd, prompt):
    """Render an ND proof as a Lean tactic text.  Boxes are rendered at the line that discharges them (IMPI / NEGI /
    ORE).  Scoping is left to Lean: a citation of a line that is out of scope becomes an unknown identifier."""
    lines = parse_nd(nd)
    prem, concl = sequent(prompt)
    by = {l['idx']: l for l in lines}
    # box structure: an AS line at depth d opens a box that contains the following lines of depth >= d
    box_end = {}
    for i, l in enumerate(lines):
        if l['rule'] == 'AS':
            e = i
            for j in range(i + 1, len(lines)):
                if lines[j]['depth'] < l['depth'] or (lines[j]['depth'] == l['depth'] and lines[j]['rule'] == 'AS'):
                    break
                e = j
            box_end[l['idx']] = lines[e]['idx']
    pos = {l['idx']: i for i, l in enumerate(lines)}

    def nm(k):
        return f'x{k}'

    def term(l):
        r, a = l['rule'], l['refs']
        if r == 'PR':
            k = [j for j, p in enumerate(prem) if p == l['f']]
            if not k:
                raise ValueError('PR not a premise')
            # PR lines reproduce the premises in order; use the first unused matching premise
            return 'PR'
        if r == 'R':
            return nm(a[0])
        if r == 'ANDI':
            return f'⟨{nm(a[0])}, {nm(a[1])}⟩'
        if r == 'ANDE1':
            return f'{nm(a[0])}.1'
        if r == 'ANDE2':
            return f'{nm(a[0])}.2'
        if r == 'IMPE':
            return f'{nm(a[0])} {nm(a[1])}'
        if r == 'NEGE':
            return f'{nm(a[1])} {nm(a[0])}'
        if r == 'ORI1':
            return f'Or.inl {nm(a[0])}'
        if r == 'ORI2':
            return f'Or.inr {nm(a[0])}'
        if r == 'BOTE':
            return f'False.elim {nm(a[0])}'
        if r == 'DN':
            return f'Classical.byContradiction (fun hh => {nm(a[0])} hh)'
        if r in ('IMPI', 'NEGI'):
            return box(a[0], a[1])
        if r == 'ORE':
            return f'Or.elim {nm(a[0])} {box(a[1], a[2])} {box(a[3], a[4])}'
        raise ValueError(f'rule {r}')

    def box(s, e):
        if s not in box_end or box_end[s] != e:
            raise ValueError(f'box N{s}..N{e} is not a box')
        h = by[s]
        body = render(pos[s] + 1, pos[e] + 1, h['depth'])
        stmts = '; '.join(body + [f'exact {nm(e)}'])
        return f'(fun ({nm(s)} : {lean_f(h["f"])}) => by {stmts})'

    pr_used = []

    def render(a, b, depth):
        """statements for lines[a:b] at `depth`; nested boxes are skipped (rendered where discharged)"""
        out = []
        i = a
        while i < b:
            l = lines[i]
            if l['rule'] == 'AS' and l['depth'] == depth + 1:
                i = pos[box_end[l['idx']]] + 1
                continue
            if l['depth'] != depth:
                raise ValueError(f'depth N{l["idx"]}')
            if l['rule'] == 'AS':
                raise ValueError('AS at own depth')
            if l['rule'] == 'PR':
                if depth != 0:
                    raise ValueError('PR inside a box')
                cand = [j for j, p in enumerate(prem) if p == l['f'] and j not in pr_used]
                if not cand:
                    raise ValueError('PR not a premise')
                pr_used.append(cand[0])
                out.append(f'have {nm(l["idx"])} : {lean_f(l["f"])} := h{cand[0] + 1}')
            else:
                out.append(f'have {nm(l["idx"])} : {lean_f(l["f"])} := {term(l)}')
            i += 1
        return out

    top = render(0, len(lines), 0)
    last = lines[-1]
    if last['depth'] != 0:
        raise ValueError('last line not at depth 0')
    return '; '.join(top + [f'exact {nm(last["idx"])}'])


# ---------------- checking ----------------
ERRLINE = re.compile(r'^[^\n]*?\.lean:(\d+):\d+: error', re.M)
AXLINE = re.compile(r"^'(t\d+)' (depends on axioms: \[(.*)\]|does not depend on any axioms)", re.M)


def _run(items, timeout=1200):
    """items: [(header, text)] -> list of bool, or None if the lean process crashed / timed out."""
    off = PRELUDE.count('\n')
    src = [PRELUDE]
    for k, (h, b) in enumerate(items):
        assert '\n' not in h and '\n' not in b
        src.append(f'theorem t{k} {h} := by {b}\n')
        src.append(f'#print axioms t{k}\n')
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write(''.join(src)); fn = f.name
    try:
        r = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.unlink(fn); return None
    os.unlink(fn)
    out = r.stdout + r.stderr
    if r.returncode not in (0, 1) or 'PANIC' in out or 'Stack overflow' in out:
        return None
    bad = set()
    for m in ERRLINE.finditer(out):
        ln = int(m.group(1))                    # 1-based; theorem k on line off+2k+1, its #print on off+2k+2
        k = (ln - off - 1) // 2
        bad.add(k)
    ax = {}
    for m in AXLINE.finditer(out):
        k = int(m.group(1)[1:])
        axs = set() if m.group(3) is None else {a.strip() for a in m.group(3).split(',') if a.strip()}
        ax.setdefault(k, []).append(axs)
    res = []
    for k in range(len(items)):
        ok = k not in bad and len(ax.get(k, [])) == 1 and ax[k][0] <= OK_AX
        res.append(ok)
    return res


def _check_rec(items):
    if not items:
        return []
    r = _run(items)
    if r is not None:
        return r
    if len(items) == 1:
        return [False]
    h = len(items) // 2
    return _check_rec(items[:h]) + _check_rec(items[h:])


def check(items, workers=WORKERS, chunk=CHUNK):
    chunks = [items[i:i + chunk] for i in range(0, len(items), chunk)]
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        parts = list(ex.map(_check_rec, chunks))
    return [x for p in parts for x in p]
