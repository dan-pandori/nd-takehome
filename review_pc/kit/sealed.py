#!/usr/bin/env python3
"""Reviewer (paper-clean) E3: is any theorem printed in the clean paper / blog / figures / lean files in a textbook72
renaming class?  Own code (not the executor's): own tokenizer + precedence parser for Unicode, LaTeX, Lean and
generator syntax; own keys:
  ORD  atom renaming by first appearance, premises in printed order (the gen.canon_key notion);
  INV  min over all atom bijections of (sorted premise strings, goal)  -> premise-order AND renaming invariant.
Each printed formula is tried under several readings: |- f ; for f = A1 -> ... -> Ak -> B every curried split
A1..Aj |- rest ; for (A1 & A2) -> B also A1, A2 |- B ; each printed sequent as given and with its goal's antecedents
moved left.  Schema check (informational): which textbook72 problems are substitution INSTANCES of a printed
schema/formula (metavariables match any subformula).
Output never prints a formula that hits a sealed class: hits print textbook IDs + location only."""
import itertools, json, re, subprocess, sys, os, collections, glob

# ---------------- parsing ----------------
UNI = {'¬': 'not', '∧': 'and', '∨': 'or', '→': 'imp', '↔': 'iff', '⊥': 'bot', '⊢': 'vdash'}
PREC = {'iff': 0, 'imp': 1, 'or': 2, 'and': 3}
RIGHT = {'imp', 'iff'}
ATOM_RE = re.compile(r'^(?:[A-Z]|[φψχθ]|[A-Z]_?\d|[φψχ]_?\d)$')

def lex(s, gen=False):
    """s: a candidate formula/sequent string; returns tokens or None."""
    s = s.replace('|-', '⊢').replace('->', '→').replace('/\\', '∧').replace('\\/', '∨')
    s = s.replace('False', '⊥')
    toks = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1; continue
        if c in '(),':
            toks.append(c); i += 1; continue
        if c in UNI:
            toks.append(UNI[c]); i += 1; continue
        if gen and c in '~>&':
            toks.append({'~': 'not', '>': 'imp', '&': 'and'}[c]); i += 1; continue
        m = re.match(r'[A-Za-zφψχθ][A-Za-z0-9_\']*', s[i:])
        if m:
            w = m.group()
            if gen and w == 'v': toks.append('or')
            elif gen and w == 'F': toks.append('bot')
            elif gen and w in ('SEQ',): toks.append('vdash')
            elif ATOM_RE.match(w): toks.append(('atom', w))
            else: return None
            i += len(w); continue
        return None
    return toks

class P:
    def __init__(s, toks): s.t, s.i = toks, 0
    def peek(s): return s.t[s.i] if s.i < len(s.t) else None
    def eat(s, x=None):
        tok = s.peek()
        if tok is None or (x is not None and tok != x): raise ValueError
        s.i += 1; return tok
    def formula(s, minp=0):
        lhs = s.unary()
        while True:
            op = s.peek()
            if op not in PREC or PREC[op] < minp: return lhs
            s.eat(); rhs = s.formula(PREC[op] + (0 if op in RIGHT else 1))
            lhs = (op, lhs, rhs)
    def unary(s):
        tok = s.peek()
        if tok == 'not': s.eat(); return ('not', s.unary())
        if tok == '(':
            s.eat(); f = s.formula(); s.eat(')'); return f
        if tok == 'bot': s.eat(); return ('bot',)
        if isinstance(tok, tuple): s.eat(); return tok
        raise ValueError

def parse_seq(toks):
    """-> (premises tuple, goal) or None. Accepts 'f', 'f1, f2 ⊢ g', '⊢ g'."""
    try:
        if toks.count('vdash') > 1: return None
        if 'vdash' in toks:
            k = toks.index('vdash'); left, right = toks[:k], toks[k + 1:]
            prem = []
            if left:
                p = P(left + [None]); p.t = left
                while True:
                    prem.append(p.formula())
                    if p.peek() is None: break
                    p.eat(',')
            q = P(right); g = q.formula()
            if q.peek() is not None: return None
            return (tuple(prem), g)
        p = P(toks); f = p.formula()
        if p.peek() is not None: return None
        return ((), f)
    except (ValueError, IndexError):
        return None

def ser(f, ren=None):
    if f[0] == 'atom': return ren[f[1]] if ren else f[1]
    if f[0] == 'bot': return '⊥'
    if f[0] == 'not': return '¬' + ser(f[1], ren)
    return '(' + ser(f[1], ren) + {'and': '∧', 'or': '∨', 'imp': '→', 'iff': '↔'}[f[0]] + ser(f[2], ren) + ')'

def atoms(f, acc):
    if f[0] == 'atom':
        if f[1] not in acc: acc.append(f[1])
    elif f[0] != 'bot':
        for g in f[1:]: atoms(g, acc)
    return acc

def nconn(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + sum(nconn(g) for g in f[1:])

CAN = 'abcdefghij'
SCHEMA_LETTERS = set('ABCDGφψχ')
def key_ord(seq):
    prem, goal = seq; acc = []
    for f in list(prem) + [goal]: atoms(f, acc)
    ren = {a: CAN[i] for i, a in enumerate(acc)}
    return (tuple(ser(f, ren) for f in prem), ser(goal, ren))

def key_inv(seq):
    prem, goal = seq; acc = []
    for f in list(prem) + [goal]: atoms(f, acc)
    best = None
    for perm in itertools.permutations(CAN[:len(acc)]):
        ren = dict(zip(acc, perm))
        k = (tuple(sorted(ser(f, ren) for f in prem)), ser(goal, ren))
        if best is None or k < best: best = k
    return best

def readings(seq):
    """all sequent readings of a printed sequent / formula"""
    prem, goal = seq
    out = {seq}
    # move antecedents of the goal to the left (curried splits)
    cur_p, cur_g = list(prem), goal
    while cur_g[0] == 'imp':
        cur_p = cur_p + [cur_g[1]]; cur_g = cur_g[2]
        out.add((tuple(cur_p), cur_g))
        if cur_g[0] == 'imp' or True:
            pass
    # uncurry a conjunctive antecedent: (A1 & A2) -> B  => A1, A2 |- B
    if goal[0] == 'imp' and goal[1][0] == 'and':
        out.add((tuple(prem) + (goal[1][1], goal[1][2]), goal[2]))
    # split conjunctive premises A & B |- C  => A, B |- C
    for i, p in enumerate(prem):
        if p[0] == 'and':
            out.add((tuple(prem[:i]) + (p[1], p[2]) + tuple(prem[i + 1:]), goal))
    # iff as two implications
    if goal[0] == 'iff' and not prem:
        out.add(((goal[1],), goal[2])); out.add(((goal[2],), goal[1]))
    return out

def match(pat, f, sub):
    """one-way matching: metavariables (atoms of pat) match any subformula, consistently"""
    if pat[0] == 'atom':
        if pat[1] in sub: return sub[pat[1]] == f
        sub[pat[1]] = f; return True
    if pat[0] != f[0]: return False
    if pat[0] == 'bot': return True
    return all(match(a, b, sub) for a, b in zip(pat[1:], f[1:]))

def instance_of(pseq, tseq):
    pp, pg = pseq; tp, tg = tseq
    if len(pp) != len(tp): return False
    for perm in itertools.permutations(tp):
        sub = {}
        if match(pg, tg, sub) and all(match(a, b, sub) for a, b in zip(pp, perm)): return True
    return False

# ---------------- textbook72 ----------------
def tb_seq(prompt):
    t = prompt.split()
    assert t[0] == 'THM' and t[-1] == 'PRF'
    return parse_seq(lex(' '.join(t[1:-1]).replace('SEQ', '⊢'), gen=True))

TB = [json.loads(l) for l in open(os.path.expanduser('~/review/paper-clean/data/bs/textbook72.jsonl'))]
TBS = [(r['name'], tb_seq(r['prompt'])) for r in TB]
assert all(s is not None for _, s in TBS), 'textbook72 parse failure'
ORD, INV = collections.defaultdict(list), collections.defaultdict(list)
for n, s in TBS:
    ORD[key_ord(s)].append(n); INV[key_inv(s)].append(n)

# ---------------- candidate extraction ----------------
LATEX_MAP = [(r'\\(neg|lnot)\b', '¬'), (r'\\(to|rightarrow|Rightarrow|supset|implies|limplies)\b', '→'),
             (r'\\(land|wedge)\b', '∧'), (r'\\(lor|vee)\b', '∨'), (r'\\(bot|perp|falsum)\b', '⊥'),
             (r'\\vdash\b', '⊢'), (r'\\(leftrightarrow|iff|Leftrightarrow)\b', '↔'),
             (r'\\(varphi|phi)\b', 'φ'), (r'\\psi\b', 'ψ'), (r'\\chi\b', 'χ'), (r'\\Gamma\b', 'Γ'),
             (r'\\(mathit|mathrm|mathsf|texttt|text|ensuremath|mathbf)\b', ''), (r'\\[,;:! ]', ' '), (r'\\(left|right|big|Big|bigl|bigr)\b', ''),
             (r'\$', ' '), (r'[{}]', ' '), (r'~', ' ')]

def latex_to_text(s):
    s = re.sub(r'(?<!\\)%.*', '', s)
    s = s.replace('(*', ' ').replace('*)', ' ')          # lstlisting escapeinside markers
    for a, b in LATEX_MAP: s = re.sub(a, b, s)
    return s

TOKRX = re.compile(r"[A-Za-z][A-Za-z0-9_']*|[φψχθ⊥¬∧∨→↔⊢(),]|\S")
def is_ftok(t):
    return t in ('⊥', '¬', '∧', '∨', '→', '↔', '⊢', '(', ')', ',') or bool(ATOM_RE.match(t))
def spans(text):
    """maximal runs of formula tokens (standalone atoms, connectives, parens, commas, turnstile)"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\bFalse\b', '⊥', text)
    toks = [(m.group(), m.start(), m.end()) for m in TOKRX.finditer(text)]
    i = 0
    while i < len(toks):
        if not is_ftok(toks[i][0]):
            i += 1; continue
        j = i
        while j < len(toks) and is_ftok(toks[j][0]): j += 1
        run = toks[i:j]
        if any(t[0] in ('¬', '∧', '∨', '→', '↔', '⊢') for t in run):
            yield run, text[max(0, run[0][1] - 60):run[-1][2] + 40]
        i = j

def trim_parse(run):
    """longest parseable sub-spans of a token run, greedy left to right; strips wrapping prose parentheses"""
    words = [t[0] for t in run]
    out = []; i = 0; n = len(words)
    while i < n:
        best = None
        for j in range(n, i, -1):
            cand = ' '.join(words[i:j])
            if not any(c in cand for c in '¬∧∨→↔⊢'): break
            toks = lex(cand)
            q = parse_seq(toks) if toks else None
            if q is None and cand.startswith('(') and cand.endswith(')'):
                toks = lex(cand[1:-1]); q = parse_seq(toks) if toks else None
            if q and (nconn(q[1]) + sum(nconn(p) for p in q[0]) > 0):
                best = (j, q); break
        if best:
            out.append(best[1]); i = best[0]
        else:
            i += 1
    return out

def lean_seqs(text):
    """balanced-paren parser for Lean headers: theorem/lemma/example NAME (binders)* : GOAL :="""
    out = []
    for m in re.finditer(r'\b(?:theorem|lemma|example)\b', text):
        i = m.end()
        mm = re.match(r'\s*[\w.\']*\s*', text[i:]); i += mm.end()
        prem = []
        while i < len(text) and text[i] == '(':
            depth, j = 0, i
            while j < len(text):
                depth += text[j] == '('; depth -= text[j] == ')'
                if depth == 0: break
                j += 1
            binder = text[i + 1:j]
            name, _, ty = binder.partition(':')
            if ty.strip() and ty.strip() != 'Prop': prem.append(ty.strip())
            i = j + 1
            while i < len(text) and text[i].isspace(): i += 1
        if i < len(text) and text[i] == ':':
            k = text.find(':=', i + 1)
            if k < 0: continue
            goal = text[i + 1:k]
            toks = lex(', '.join(prem) + ' ⊢ ' + goal)
            q = parse_seq(toks) if toks else None
            out.append((q, text[m.start():m.start() + 80]))
    return out

def gen_spans(text):
    """generator-syntax formulas inside code: sequences of ( ~ > & v F P Q R S ) tokens"""
    for m in re.finditer(r'(?:(?:\(|\)|~|>|&|\bv\b|\bF\b|\b[PQRSTAB]\b|,|\|-|SEQ)\s*){5,}', text):
        toks = lex(m.group().replace('SEQ', '⊢'), gen=True)
        if toks:
            q = parse_seq(toks)
            if q: yield q, m.group()

VERBAL = [(re.compile(r'\b([A-Z]) or not \1\b'), lambda m: f'{m.group(1)} ∨ ¬{m.group(1)}'),
          (re.compile(r'\bnot not ([A-Z])\b'), lambda m: f'¬¬{m.group(1)}')]

def scan(label, text, kind):
    """returns list of (sequent, context, how)"""
    found = []
    if kind == 'latex': text = latex_to_text(text)
    if kind in ('latex', 'text', 'md', 'lean'):
        for run, ctx in spans(text):
            for q in trim_parse(run):
                found.append((q, ctx, 'span'))
        for rx, fn in VERBAL:
            for m in rx.finditer(text):
                q = parse_seq(lex(fn(m)))
                if q: found.append((q, text[max(0, m.start()-40):m.end()+40], 'verbal'))
    if kind in ('lean', 'md', 'latex', 'text'):
        for q, ctx in lean_seqs(text):
            if q: found.append((q, ctx, 'lean-thm'))
    if kind in ('md', 'latex', 'code', 'text'):
        for q, ctx in gen_spans(text):
            found.append((q, ctx, 'gen'))
    return [(label, q, re.sub(r'\s+', ' ', ctx), how) for q, ctx, how in found]

def collect(root, pdf_txt, fig_glob, extra_lean, blog):
    items = []
    for f in sorted(glob.glob(os.path.join(root, 'sections', '*.tex'))) + [os.path.join(root, 'main.tex')]:
        items += scan(os.path.relpath(f, root), open(f, encoding='utf-8').read(), 'latex')
    if blog: items += scan('blog.md', open(os.path.join(root, 'blog.md'), encoding='utf-8').read(), 'md')
    for f in sorted(glob.glob(os.path.join(root, 'lean', '*.lean'))):
        items += scan(os.path.relpath(f, root), open(f, encoding='utf-8').read(), 'lean')
    if pdf_txt: items += scan('main.pdf (pdftotext)', open(pdf_txt, encoding='utf-8').read(), 'text')
    for f in sorted(glob.glob(os.path.join(root, 'figures', '*.pdf'))):
        t = subprocess.run(['pdftotext', f, '-'], capture_output=True, text=True).stdout
        items += scan(os.path.relpath(f, root), t, 'text')
    return items

def report(name, items, show_ok=True, quiet=False):
    print(f'\n######## {name}: {len(items)} extracted occurrences')
    seen = {}
    for label, q, ctx, how in items:
        for r in readings(q):
            ko, ki = key_ord(r), key_inv(r)
            hit_o, hit_i = ORD.get(ko, []), INV.get(ki, [])
            k = ki
            e = seen.setdefault(k, {'hit_o': set(), 'hit_i': set(), 'where': set(), 'repr': None, 'primary': False})
            e['hit_o'] |= set(hit_o); e['hit_i'] |= set(hit_i); e['where'].add(f'{label} [{how}]')
            if r == q: e['primary'] = True; e['repr'] = e['repr'] or q
            e['repr'] = e['repr'] or r
    hits = {k: e for k, e in seen.items() if e['hit_o'] or e['hit_i']}
    nprim = sum(e['primary'] for e in seen.values())
    print(f'distinct printed sequents/formulas (premise-order+renaming classes): {nprim}; with readings: {len(seen)}; HITS: {len(hits)}')
    for k, e in hits.items():
        print(f"  HIT  <withheld>  order-sensitive {sorted(e['hit_o']) or '-'}  invariant {sorted(e['hit_i']) or '-'}  primary={e['primary']}  where: {'; '.join(sorted(e['where']))[:400]}")
    if show_ok and not quiet:
        for k, e in sorted(seen.items(), key=lambda kv: -kv[1]['primary']):
            if e['primary'] and not (e['hit_o'] or e['hit_i']):
                q = e['repr']
                s = (', '.join(ser(p) for p in q[0]) + ' ⊢ ' + ser(q[1]))
                print(f"  ok   {s:60s} | {'; '.join(sorted(e['where']))[:200]}")
    # schema-instance check (informational)
    inst = collections.defaultdict(set)
    for k, e in seen.items():
        q = e['repr']
        if e['hit_o'] or e['hit_i']: continue
        al = atoms(q[1], []) + [a for p in q[0] for a in atoms(p, [])]
        if not al or not set(al) <= SCHEMA_LETTERS or nconn(q[1]) + sum(nconn(p) for p in q[0]) < 2: continue
        for n, t in TBS:
            if instance_of(q, t): inst[k].add(n)
    if inst:
        print(f'  schema-instance matches (a textbook72 problem is a substitution instance of a printed, non-hit formula/sequent reading): {len(inst)} readings')
        for k, ns in inst.items():
            e = seen[k]; q = e['repr']
            s = (', '.join(ser(p) for p in q[0]) + ' ⊢ ' + ser(q[1]))
            print(f"    inst {s:50s} primary={e['primary']} -> {len(ns)} textbook72 problems {sorted(ns)[:6]} | {'; '.join(sorted(e['where']))[:160]}")
    return hits

if __name__ == '__main__':
    print(f'textbook72: {len(TB)} problems; {len(ORD)} order-sensitive classes; {len(INV)} premise-order-invariant classes')
    mode = sys.argv[1]
    if mode == 'clean':
        items = collect(os.path.expanduser('~/review/paper-clean/paper'), '/tmp/pc_build/clean_committed.txt', None, None, True)
        report('CLEAN (paper sections + main.tex + blog + lean/ + main.pdf text + figures/*.pdf text)', items)
    elif mode == 'marked':
        items = collect(os.path.expanduser('~/review/paper-clean/review_pc/marked'), '/tmp/pc_build/marked.txt', None, None, True)
        report('MARKED (positive control)', items, quiet=True)
    elif mode == 'files':      # executor's records: counts + masked hits only
        for f in sys.argv[2:]:
            items = scan(f, open(f, encoding='utf-8').read(), 'md')
            report(f, items, quiet=True)
