#!/usr/bin/env python3
"""ND (spec.md Fitch proofs) -> Lean 4 term-mode proofs; an English surface form; a batched Lean checker.

Translation (deterministic; parsing shared with nd_verify so both checkers see the same structure):
  atoms P Q R S -> (P Q R S : Prop);  F -> False;  ~ & v > -> ¬ ∧ ∨ →;  premises -> hypotheses h1..hm.
  line N<i> ... : RULE refs  ->  have n<i> : <formula> := <term>
    PR    -> h<k> (k-th PR line)          AS    -> the binder of the enclosing box's `fun`
    R     -> n<j>                         ANDI  -> And.intro n<a> n<b>
    ANDE1 -> n<a>.1   ANDE2 -> n<a>.2     IMPE  -> n<a> n<b>
    ORI1  -> Or.inl n<a>   ORI2 -> Or.inr n<a>
    IMPI  -> b<s>  (the box s..e, emitted when it closes as  have b<s> : A → E := fun n<s> : A => (… n<e>))
    NEGI  -> b<s>  (same box, at type ¬A)  ORE -> Or.elim n<j> b<s1> b<s2>
    NEGE  -> n<b> n<a>   BOTE -> False.elim n<a>   DN -> Classical.not_not.mp n<a>
  A box's `fun` body ends with the last line at the box's own depth (the AS line itself if nothing else).
  NEGI is ascribed `(b<s> : ¬A)` so that a NEGI line must really be a negation (Lean unfolds ¬A to A → False).
  Structural malformations Lean has no counterpart for (bad depth, wrong ref count, PR beyond the premises,
  a box cite whose start is not a closed box's AS line or whose end is not that box's last line) raise
  Untranslatable — reported separately from Lean rejections.

Lean acceptance: `lean` exit 0, no "error", no `sorry`/`admit` message; the body may not contain
sorry / admit / axiom / by / native_decide / unsafe / implemented_by / extern / theorem / opaque.

CLI
  python nd2lean.py --demo
  python nd2lean.py --check FILE.jsonl --out OUT.jsonl [--field proof] [--limit N] [--procs P] [--batch B]
  python nd2lean.py --mutate FILE.jsonl --n 2000 --seed 0 --out OUT.jsonl
  python nd2lean.py --table OUT1.jsonl [OUT2.jsonl ...] > agreement.md
"""
import argparse, json, os, re, sys, subprocess, tempfile, random, collections, gzip, multiprocessing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from nd_verify.verify import parse_formula, parse_proof_tokens, ParseError, RULE_NAMES

LEAN = os.environ.get('LEAN', os.path.expanduser('~/.elan/bin/lean'))
ARITY = {'ANDI': 2, 'ANDE1': 1, 'ANDE2': 1, 'IMPE': 2, 'IMPI': 2, 'ORI1': 1, 'ORI2': 1, 'ORE': 5,
         'NEGE': 2, 'NEGI': 2, 'BOTE': 1, 'DN': 1, 'R': 1, 'PR': 0, 'AS': 0}
FORBIDDEN = ('sorry', 'admit', 'axiom', 'native_decide', 'unsafe', 'implemented_by', 'extern',
             'theorem', 'lemma', 'opaque', 'def ', 'instance', 'macro', 'syntax', 'elab', 'set_option',
             'open ', 'import', 'namespace', 'section', 'variable', 'decide')
FORBIDDEN_RE = re.compile(r'(?<![A-Za-z0-9_.])(' + '|'.join(re.escape(w).replace(r'\ ', r'\s') for w in FORBIDDEN) + r')(?![A-Za-z0-9_])')
BY_RE = re.compile(r'(?<![A-Za-z0-9_.])by(?![A-Za-z0-9_])')
FILE_HEADER = 'set_option linter.unusedVariables false\n'


class Untranslatable(Exception):
    pass


# ---------------------------------------------------------------- formulas
def parse_sequent(prompt):
    """'THM p1 , p2 SEQ c PRF' -> (premises, conclusion) as verifier tuples."""
    toks = prompt.split()
    if not toks or toks[0] != 'THM':
        raise ParseError('missing THM')
    i, prem = 1, []
    if toks[i] != 'SEQ':
        while True:
            f, i = parse_formula(toks, i)
            prem.append(f)
            if toks[i] == ',':
                i += 1
                continue
            break
    if toks[i] != 'SEQ':
        raise ParseError('missing SEQ')
    c, i = parse_formula(toks, i + 1)
    if i >= len(toks) or toks[i] != 'PRF':
        raise ParseError('missing PRF')
    return prem, c


def lean_f(f):
    if f[0] == 'atom':
        return f[1]
    if f[0] == 'bot':
        return 'False'
    if f[0] == 'not':
        return '¬' + lean_f(f[1])
    op = {'and': '∧', 'or': '∨', 'imp': '→'}[f[0]]
    return f'({lean_f(f[1])} {op} {lean_f(f[2])})'


def tok_f(f):
    if f[0] == 'atom':
        return f[1]
    if f[0] == 'bot':
        return 'F'
    if f[0] == 'not':
        return f'( ~ {tok_f(f[1])} )'
    op = {'and': '&', 'or': 'v', 'imp': '>'}[f[0]]
    return f'( {tok_f(f[1])} {op} {tok_f(f[2])} )'


def eng_f(f):
    """English/Unicode surface: same parenthesisation as the token form, no spaces inside."""
    if f[0] == 'atom':
        return f[1]
    if f[0] == 'bot':
        return '⊥'
    if f[0] == 'not':
        return f'(¬{eng_f(f[1])})'
    op = {'and': '∧', 'or': '∨', 'imp': '→'}[f[0]]
    return f'({eng_f(f[1])} {op} {eng_f(f[2])})'


def lean_header(prompt, name='thm'):
    prem, c = parse_sequent(prompt)
    hs = ' '.join(f'(h{k + 1} : {lean_f(p)})' for k, p in enumerate(prem))
    return f'theorem {name} (P Q R S : Prop) {hs} : {lean_f(c)} :='.replace('  :', ' :')


# ---------------------------------------------------------------- ND -> Lean
def _close_box(box, parent):
    s, A = box['s'], box['A']
    e = box['last_at_depth']
    E = box['fml'][e]
    inner = ''.join(box['out'])
    parent['box_end'][s] = e
    ind = '  ' * (box['depth'] + 1)
    parent['out'].append(f"{'  ' * box['depth']}have b{s} : {lean_f(A)} → {lean_f(E)} := fun n{s} : {lean_f(A)} => (\n"
                         f"{inner}{ind}n{e})\n")


def _box_cite(s, e, box_end, idx):
    """A box cite (s, e) must name a closed box's AS line and its last line; anything else has no Lean counterpart."""
    if s not in box_end:
        raise Untranslatable(f'box cite {s}-{e} at line {idx}: {s} is not the start of a closed box')
    if box_end[s] != e:
        raise Untranslatable(f'box cite {s}-{e} at line {idx}: box {s} ends at {box_end[s]}')


def translate_lines(lines, n_prem):
    """lines: parsed proof lines (nd_verify dicts). Returns the Lean body (string after ':='), or raises Untranslatable."""
    if not lines:
        raise Untranslatable('empty proof')
    fml = {}
    box_end = {}         # AS line -> last line of its (closed) box
    top = {'s': None, 'A': None, 'depth': 0, 'out': [], 'last_at_depth': None, 'fml': fml, 'box_end': box_end}
    stack = [top]        # stack[0] = top level (depth 0); stack[d] = open box at depth d
    pr_count = 0
    for ln in lines:
        idx, d, rule, refs, G = ln['idx'], ln['depth'], ln['rule'], ln['refs'], ln['formula']
        if rule == 'AS':
            if d < 1 or d > len(stack):
                raise Untranslatable(f'bad AS depth at line {idx}')
            while len(stack) > d:
                b = stack.pop()
                _close_box(b, stack[-1])
            box = {'s': idx, 'A': G, 'depth': d, 'out': [], 'last_at_depth': idx, 'fml': fml, 'box_end': box_end}
            stack.append(box)
            fml[idx] = G
            continue
        if d > len(stack) - 1:
            raise Untranslatable(f'depth jump at line {idx}')
        while len(stack) - 1 > d:
            b = stack.pop()
            _close_box(b, stack[-1])
        if rule not in ARITY:
            raise Untranslatable(f'unknown rule {rule}')
        if len(refs) != ARITY[rule]:
            raise Untranslatable(f'wrong ref count for {rule} (line {idx})')
        n = lambda r: f'n{r}'
        if rule == 'PR':
            pr_count += 1
            if pr_count > n_prem:
                raise Untranslatable(f'PR line {idx} beyond the {n_prem} premises')
            term = f'h{pr_count}'
        elif rule == 'R':
            term = n(refs[0])
        elif rule == 'ANDI':
            term = f'And.intro {n(refs[0])} {n(refs[1])}'
        elif rule == 'ANDE1':
            term = f'{n(refs[0])}.1'
        elif rule == 'ANDE2':
            term = f'{n(refs[0])}.2'
        elif rule == 'IMPE':
            term = f'{n(refs[0])} {n(refs[1])}'
        elif rule in ('IMPI', 'NEGI'):
            _box_cite(refs[0], refs[1], box_end, idx)
            term = f'b{refs[0]}' if rule == 'IMPI' else f'(b{refs[0]} : ¬{lean_f(fml[refs[0]])})'
        elif rule == 'ORI1':
            term = f'Or.inl {n(refs[0])}'
        elif rule == 'ORI2':
            term = f'Or.inr {n(refs[0])}'
        elif rule == 'ORE':
            _box_cite(refs[1], refs[2], box_end, idx)
            _box_cite(refs[3], refs[4], box_end, idx)
            term = f'Or.elim {n(refs[0])} b{refs[1]} b{refs[3]}'
        elif rule == 'NEGE':
            term = f'{n(refs[1])} {n(refs[0])}'
        elif rule == 'BOTE':
            term = f'False.elim {n(refs[0])}'
        elif rule == 'DN':
            term = f'Classical.not_not.mp {n(refs[0])}'
        cur = stack[-1]
        cur['out'].append(f"{'  ' * (d + 1)}have n{idx} : {lean_f(G)} := {term}\n")
        cur['last_at_depth'] = idx
        fml[idx] = G
    while len(stack) > 1:
        b = stack.pop()
        _close_box(b, stack[-1])
    last = lines[-1]['idx']
    return ''.join(top['out']) + f'  n{last}\n'


def to_lean(prompt, proof, name='thm'):
    """-> (header, body). Raises ParseError (either part unparsable) or Untranslatable."""
    prem, c = parse_sequent(prompt)
    lines = parse_proof_tokens(proof.split())
    return lean_header(prompt, name), translate_lines(lines, len(prem))


def split_text(text):
    """'THM ... PRF body' -> (prompt, body)."""
    toks = text.split()
    i = toks.index('PRF')
    return ' '.join(toks[:i + 1]), ' '.join(toks[i + 1:])


# ---------------------------------------------------------------- Lean checking
def body_forbidden(body):
    m = FORBIDDEN_RE.search(body)
    if m:
        return f'forbidden token {m.group(1)!r}'
    if BY_RE.search(body):
        return 'tactic block (by)'
    return None


def run_lean(src, timeout=120):
    """Compile one source string. -> (ok, messages)."""
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write(src)
        fn = f.name
    try:
        p = subprocess.run([LEAN, fn], capture_output=True, text=True, timeout=timeout)
        out = (p.stdout + p.stderr).replace(fn, '<f>')
        ok = p.returncode == 0 and 'error' not in out and 'sorry' not in out
        return ok, out
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    finally:
        os.unlink(fn)


def _msgs_by_decl(out, starts):
    """Attribute 'file:line:col: ...' messages to declarations by their starting line numbers."""
    res = collections.defaultdict(list)
    for m in re.finditer(r'<f>:(\d+):(\d+): (\w+): (.*)', out):
        line = int(m.group(1))
        k = max((i for i, s in enumerate(starts) if s <= line), default=0)
        res[k].append(f'{m.group(3)}: {m.group(4)}')
    return res


def lean_check_many(items, timeout=600):
    """items: list of (header, body). Batched compile; failures re-checked singly. -> list of (ok, msg)."""
    n = len(items)
    if n == 0:
        return []
    res = [None] * n
    src, starts = FILE_HEADER, []
    for i, (h, b) in enumerate(items):
        fb = body_forbidden(b)
        if fb:
            res[i] = (False, fb)
            starts.append(-1)
            src += f'theorem dummy{i} : True := trivial\n'
            continue
        starts.append(src.count('\n') + 1)
        src += re.sub(r'^theorem\s+\S+', f'theorem t{i}', h, count=1) + '\n' + b.rstrip('\n') + '\n'
    ok, out = run_lean(src, timeout=timeout)
    if out == 'timeout':
        for i in range(n):
            if res[i] is None:
                res[i] = (False, 'timeout (batch)')
        return res
    msgs = _msgs_by_decl(out, [s if s > 0 else 10 ** 9 for s in starts])
    bad = 'error' in out or 'sorry' in out
    for i in range(n):
        if res[i] is not None:
            continue
        mi = msgs.get(i, [])
        if any(('error' in m) or ('sorry' in m) for m in mi):
            res[i] = (False, ' | '.join(mi)[:400])
        elif bad:
            res[i] = None   # a neighbour failed: re-check singly to be safe against cascades
        else:
            res[i] = (True, 'ok')
    for i in range(n):
        if res[i] is None:
            h, b = items[i]
            ok1, out1 = run_lean(FILE_HEADER + h + '\n' + b)
            res[i] = (ok1, 'ok' if ok1 else out1.strip()[:400])
    return res


def check_records(recs, procs=2, batch=100):
    """recs: list of dicts with 'prompt' and 'proof' (or 'text'). Adds nd_ok, nd_reason, n_lines, lean_ok, lean_msg, translate."""
    prepared = []
    for r in recs:
        if 'text' in r and 'proof' not in r:
            r['prompt'], r['proof'] = split_text(r['text'])
        ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
        r['nd_ok'], r['nd_reason'], r['n_lines'] = ok, reason, nl
        try:
            h, b = to_lean(r['prompt'], r['proof'])
            r['translate'] = 'ok'
            prepared.append((h, b))
        except ParseError as e:
            r['translate'] = f'parse: {e}'
            prepared.append(None)
        except Untranslatable as e:
            r['translate'] = f'untranslatable: {e}'
            prepared.append(None)
    todo = [i for i, p in enumerate(prepared) if p is not None]
    chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]
    args = [[prepared[i] for i in ch] for ch in chunks]
    if procs > 1:
        with multiprocessing.Pool(procs) as pool:
            outs = pool.map(lean_check_many, args, chunksize=1)
    else:
        outs = [lean_check_many(a) for a in args]
    for ch, out in zip(chunks, outs):
        for i, (ok, msg) in zip(ch, out):
            recs[i]['lean_ok'], recs[i]['lean_msg'] = ok, msg
    for i, p in enumerate(prepared):
        if p is None:
            recs[i]['lean_ok'], recs[i]['lean_msg'] = False, recs[i]['translate']
    return recs


# ---------------------------------------------------------------- English surface form
RULE_EN = {'PR': 'premise', 'AS': 'assumption', 'R': 'reiteration of {0}',
           'ANDI': 'conjunction introduction from {0} and {1}',
           'ANDE1': 'conjunction elimination (left) from {0}', 'ANDE2': 'conjunction elimination (right) from {0}',
           'IMPE': 'implication elimination from {0} and {1}', 'IMPI': 'implication introduction from subproof {0}-{1}',
           'ORI1': 'disjunction introduction (left) from {0}', 'ORI2': 'disjunction introduction (right) from {0}',
           'ORE': 'disjunction elimination from {0} with subproofs {1}-{2} and {3}-{4}',
           'NEGE': 'negation elimination from {0} and {1}', 'NEGI': 'negation introduction from subproof {0}-{1}',
           'BOTE': 'ex falso from {0}', 'DN': 'double negation elimination from {0}'}
EN_RULE = {'premise': 'PR', 'assumption': 'AS', 'reiteration': 'R', 'conjunction introduction': 'ANDI',
           'conjunction elimination (left)': 'ANDE1', 'conjunction elimination (right)': 'ANDE2',
           'implication elimination': 'IMPE', 'implication introduction': 'IMPI',
           'disjunction introduction (left)': 'ORI1', 'disjunction introduction (right)': 'ORI2',
           'disjunction elimination': 'ORE', 'negation elimination': 'NEGE', 'negation introduction': 'NEGI',
           'ex falso': 'BOTE', 'double negation elimination': 'DN'}


def eng_sequent(prompt):
    prem, c = parse_sequent(prompt)
    ps = ', '.join(eng_f(p) for p in prem) if prem else '(none)'
    return f'Premises: {ps}\nGoal: {eng_f(c)}'


def to_english(prompt, proof):
    lines = parse_proof_tokens(proof.split())
    out = []
    for ln in lines:
        bars = '| ' * ln['depth']
        out.append(f"{ln['idx']}. {bars}{eng_f(ln['formula'])} : {RULE_EN[ln['rule']].format(*ln['refs'])}")
    return '\n'.join(out) + '\nQED'


def _eng_formula_to_tokens(s):
    s = s.replace('¬', ' ~ ').replace('∧', ' & ').replace('∨', ' v ').replace('→', ' > ').replace('⊥', ' F ')
    s = s.replace('(', ' ( ').replace(')', ' ) ')
    return ' '.join(s.split())


def english_to_tokens(text):
    """Parse the English form back to the token proof body ('N1 ... ; ... QED'). Unparsable lines -> None."""
    body = []
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw or raw == 'QED':
            continue
        m = re.match(r'^(\d+)\.\s*((?:\|\s*)*)(.*?)\s*:\s*(.*?)\s*$', raw)
        if not m:
            return None
        idx, bars, f, rule = m.groups()
        depth = bars.count('|')
        rule_l = rule.lower()
        name = None
        for k in sorted(EN_RULE, key=len, reverse=True):
            if rule_l.startswith(k):
                name = EN_RULE[k]
                break
        if name is None:
            return None
        refs = re.findall(r'\d+', rule)
        body.append(f"N{idx} {'| ' * depth}{_eng_formula_to_tokens(f)} : {name} {' '.join('N' + r for r in refs)} ;".replace('  ', ' '))
    return ' '.join(body) + ' QED'


# ---------------------------------------------------------------- lenient formula repair (secondary metric)
class _Tol(Exception):
    pass


def _tol_unary(t, i):
    if i >= len(t):
        raise _Tol('eof')
    x = t[i]
    if x == '~':
        sub, j = _tol_unary(t, i + 1)
        return ('not', sub), j
    if x == '(':
        f, j = _tol_expr(t, i + 1)
        if j >= len(t) or t[j] != ')':
            raise _Tol('missing )')
        return f, j + 1
    if x in ('P', 'Q', 'R', 'S'):
        return ('atom', x), i + 1
    if x == 'F':
        return ('bot',), i + 1
    raise _Tol(f'bad token {x}')


def _tol_expr(t, i):
    left, j = _tol_unary(t, i)
    if j < len(t) and t[j] in ('&', 'v', '>'):
        op = {'&': 'and', 'v': 'or', '>': 'imp'}[t[j]]
        right, k = _tol_unary(t, j + 1)
        if k < len(t) and t[k] in ('&', 'v', '>'):
            raise _Tol('ambiguous chain of binary operators')
        return (op, left, right), k
    return left, j


def repair_proof(body):
    """Lenient re-parse of every line formula in a token proof body: tolerates a missing outer pair of parentheses
    and unparenthesised negation (`~ P`), re-emitting the fully parenthesised form. Anything else is left as is.
    Returns the repaired body (or the input if a line cannot be split)."""
    out = []
    for line in body.split(';'):
        toks = line.split()
        if not toks or toks == ['QED']:
            out.append(line)
            continue
        if ':' not in toks:
            out.append(line)
            continue
        c = toks.index(':')
        head = [toks[0]]
        k = 1
        while k < c and toks[k] == '|':
            head.append('|')
            k += 1
        ftoks = toks[k:c]
        try:
            f, j = _tol_expr(ftoks, 0)
            if j != len(ftoks):
                raise _Tol('trailing')
            ftoks = tok_f(f).split()
        except _Tol:
            pass
        out.append(' ' + ' '.join(head + ftoks + toks[c:]) + ' ')
    return ';'.join(out).strip()


# ---------------------------------------------------------------- mutations
def mutate(prompt, proof, rng):
    """One random single-token edit. Returns (kind, new_proof)."""
    toks = proof.split()
    kinds = ['ref', 'rule', 'formula', 'depth', 'swap_refs']
    for _ in range(20):
        kind = rng.choice(kinds)
        t = toks[:]
        if kind == 'ref':
            pos = [i for i, x in enumerate(t) if i > 0 and x.startswith('N') and x[1:].isdigit() and t[i - 1] != ';' and i != 0
                   and not (t[i - 1] == 'QED')]
            pos = [i for i in pos if t[i - 1] not in (';',) and not (i == 0)]
            pos = [i for i in pos if any(t[j] == ':' for j in range(max(0, i - 40), i)) and t[i - 1] != ';']
            if not pos:
                continue
            i = rng.choice(pos)
            nmax = sum(1 for x in t if x == ';')
            new = f'N{rng.randint(1, max(1, nmax))}'
            if new == t[i]:
                continue
            t[i] = new
        elif kind == 'rule':
            pos = [i for i, x in enumerate(t) if x in RULE_NAMES and i > 0 and t[i - 1] == ':']
            if not pos:
                continue
            i = rng.choice(pos)
            new = rng.choice(sorted(RULE_NAMES - {t[i]}))
            t[i] = new
        elif kind == 'formula':
            pos = [i for i, x in enumerate(t) if x in ('P', 'Q', 'R', 'S', 'F', '&', 'v', '>')]
            if not pos:
                continue
            i = rng.choice(pos)
            if t[i] in ('&', 'v', '>'):
                t[i] = rng.choice([o for o in ('&', 'v', '>') if o != t[i]])
            else:
                t[i] = rng.choice([a for a in ('P', 'Q', 'R', 'S', 'F') if a != t[i]])
        elif kind == 'depth':
            pos = [i for i, x in enumerate(t) if x.startswith('N') and x[1:].isdigit() and (i == 0 or t[i - 1] == ';')]
            if not pos:
                continue
            i = rng.choice(pos)
            if i + 1 < len(t) and t[i + 1] == '|' and rng.random() < 0.5:
                del t[i + 1]
            else:
                t.insert(i + 1, '|')
        elif kind == 'swap_refs':
            pos = [i for i, x in enumerate(t) if x in ('IMPE', 'NEGE', 'ANDI') and i + 2 < len(t) and t[i + 1].startswith('N') and t[i + 2].startswith('N')]
            if not pos:
                continue
            i = rng.choice(pos)
            t[i + 1], t[i + 2] = t[i + 2], t[i + 1]
        new = ' '.join(t)
        if new != proof:
            return kind, new
    return None, proof


# ---------------------------------------------------------------- IO helpers
def load_jsonl(fn, limit=None):
    op = gzip.open if fn.endswith('.gz') else open
    out = []
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                out.append(json.loads(l))
                if limit and len(out) >= limit:
                    break
    return out


def table(files):
    print('| file | n | nd ok | lean ok | both ok | nd ok, lean no | nd no, lean ok | untranslatable |')
    print('|---|---:|---:|---:|---:|---:|---:|---:|')
    for fn in files:
        recs = load_jsonl(fn)
        n = len(recs)
        nd = sum(r['nd_ok'] for r in recs)
        le = sum(r['lean_ok'] for r in recs)
        both = sum(r['nd_ok'] and r['lean_ok'] for r in recs)
        a = sum(r['nd_ok'] and not r['lean_ok'] for r in recs)
        b = sum((not r['nd_ok']) and r['lean_ok'] for r in recs)
        u = sum(r.get('translate', 'ok') != 'ok' for r in recs)
        print(f'| `{fn}` | {n} | {nd} | {le} | {both} | {a} | {b} | {u} |')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--check')
    ap.add_argument('--field', default=None, help='proof field name (default: proof, gen_proof, or text)')
    ap.add_argument('--mutate')
    ap.add_argument('--n', type=int, default=2000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--procs', type=int, default=2)
    ap.add_argument('--batch', type=int, default=100)
    ap.add_argument('--out')
    ap.add_argument('--table', nargs='*')
    a = ap.parse_args()
    if a.demo:
        ex = 'THM ( P v Q ) , ( ~ P ) SEQ Q PRF'
        pf = 'N1 ( P v Q ) : PR ; N2 ( ~ P ) : PR ; N3 | P : AS ; N4 | F : NEGE N3 N2 ; N5 | Q : BOTE N4 ; N6 | Q : AS ; N7 Q : ORE N1 N3 N5 N6 N6 ; QED'
        h, b = to_lean(ex, pf)
        print(h); print(b)
        print(lean_check_many([(h, b)]))
        print(eng_sequent(ex)); print(to_english(ex, pf))
        back = english_to_tokens(to_english(ex, pf))
        print(back); print(verify_text(ex + ' ' + back))
        return
    if a.table is not None:
        table(a.table)
        return
    if a.check:
        recs = load_jsonl(a.check, a.limit)
        for r in recs:
            if a.field:
                r['proof'] = r[a.field]
            elif 'proof' not in r and 'gen_proof' in r:
                r['proof'] = r['gen_proof']
            elif 'proof' not in r and 'reference_proof' in r:
                r['proof'] = r['reference_proof']
        recs = [r for r in recs if r.get('proof') or r.get('text')]
        keep = ('name', 'prompt', 'proof', 'src')
        recs = [{k: r[k] for k in keep if k in r} | ({'text': r['text']} if 'prompt' not in r and 'text' in r else {}) for r in recs]
        check_records(recs, procs=a.procs, batch=a.batch)
        with open(a.out, 'w') as f:
            for r in recs:
                f.write(json.dumps(r) + '\n')
        table([a.out])
        return
    if a.mutate:
        rng = random.Random(a.seed)
        src = load_jsonl(a.mutate)
        for r in src:
            if 'proof' not in r and 'gen_proof' in r:
                r['proof'] = r['gen_proof']
            if 'prompt' not in r and 'text' in r:
                r['prompt'], r['proof'] = split_text(r['text'])
        rng.shuffle(src)
        recs = []
        for r in src[:a.n]:
            kind, new = mutate(r['prompt'], r['proof'], rng)
            if kind is None:
                continue
            recs.append({'name': r.get('name'), 'prompt': r['prompt'], 'proof': new, 'mutation': kind, 'orig_proof': r['proof']})
        check_records(recs, procs=a.procs, batch=a.batch)
        with open(a.out, 'w') as f:
            for r in recs:
                f.write(json.dumps(r) + '\n')
        table([a.out])


if __name__ == '__main__':
    main()
