#!/usr/bin/env python3
"""Reviewer (paper-clean): own ND -> Lean 4 renderer + checker (independent of nd2lean / lean_judge and of the earlier
reviewer's lean4.py). Each ND proof becomes `theorem tN (P Q R S : Prop) (h1 : ...) : G := by have ...; exact nK`.
Boxes (AS lines, '|' depth) are rendered inside the lambda of the rule that closes them. A proof counts iff Lean
reports no error in its line range and `#print axioms` shows no sorryAx. Prints counts only (some theorems are
textbook72 problems)."""
import json, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
LEAN = os.path.expanduser(os.environ.get('LEAN', '~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean'))

# --- formulas (generator syntax) ---
def ftoks(s): return s.split()
def parse_f(toks, i=0):
    t = toks[i]
    if t == '(':
        if toks[i + 1] == '~':
            a, j = parse_f(toks, i + 2); assert toks[j] == ')'; return ('not', a), j + 1
        a, j = parse_f(toks, i + 1); op = toks[j]; b, k = parse_f(toks, j + 1); assert toks[k] == ')'
        return ({'>': 'imp', '&': 'and', 'v': 'or'}[op], a, b), k + 1
    if t == '~':
        a, j = parse_f(toks, i + 1); return ('not', a), j
    if t == 'F': return ('bot',), i + 1
    assert t in ('P', 'Q', 'R', 'S', 'T'), t
    return ('atom', t), i + 1
def F(s):
    f, j = parse_f(ftoks(s)); assert j == len(ftoks(s)), s; return f
def lean(f):
    if f[0] == 'atom': return f[1]
    if f[0] == 'bot': return 'False'
    if f[0] == 'not': return f'(¬{lean(f[1])})'
    return '(' + lean(f[1]) + {'imp': ' → ', 'and': ' ∧ ', 'or': ' ∨ '}[f[0]] + lean(f[2]) + ')'
def split_top(toks):
    out, cur, d = [], [], 0
    for t in toks:
        if t == ',' and d == 0: out.append(cur); cur = []; continue
        d += t == '('; d -= t == ')'; cur.append(t)
    if cur: out.append(cur)
    return out
def thm(prompt):
    t = prompt.split(); assert t[0] == 'THM' and t[-1] == 'PRF'; k = t.index('SEQ')
    prem = [F(' '.join(p)) for p in split_top(t[1:k])] if k > 1 else []
    return prem, F(' '.join(t[k + 1:-1]))

# --- ND proofs ---
def nd_lines(proof):
    L = []
    for seg in proof.split(' ; '):
        seg = seg.strip()
        if not seg or seg == 'QED': continue
        head, _, tail = seg.rpartition(' : ')
        toks = head.split(); idx = int(toks[0][1:])
        depth = sum(1 for t in toks[1:] if t == '|'); body = ' '.join(t for t in toks[1:] if t != '|')
        rt = tail.split()
        L.append({'i': idx, 'd': depth, 'f': F(body), 'rule': rt[0], 'refs': [int(r[1:]) for r in rt[1:]]})
    return L

class Bad(Exception): pass

def render(prem, goal, L):
    pos = {l['i']: k for k, l in enumerate(L)}
    def box_end(a):                       # index (in L) of the last line of the box opened at L[a]
        e = L[a]['d']; k = a + 1
        while k < len(L) and (L[k]['d'] > e or (L[k]['d'] == e and L[k]['rule'] != 'AS')): k += 1
        return k - 1
    def lam(a_i, b_i, ind):
        a, b = pos[a_i], pos[b_i]
        if L[a]['rule'] != 'AS' or b < a or b > box_end(a): raise Bad('box')
        body = block(a + 1, box_end(a) + 1, L[a]['d'], ind + 2)
        return f"(fun (n{a_i} : {lean(L[a]['f'])}) => by\n{body}{' ' * (ind + 2)}exact n{b_i})"
    def term(l, ind):
        r, x = l['rule'], l['refs']
        n = lambda j: f'n{j}'
        if r == 'PR':
            for j, p in enumerate(prem):
                if p == l['f']: return f'h{j + 1}'
            raise Bad('premise')
        if r == 'R': return n(x[0])
        if r in ('IMPI', 'NEGI'): return lam(x[0], x[1], ind)
        if r == 'IMPE': return f'by first | exact {n(x[0])} {n(x[1])} | exact {n(x[1])} {n(x[0])}'
        if r == 'NEGE': return f'by first | exact {n(x[1])} {n(x[0])} | exact {n(x[0])} {n(x[1])}'
        if r == 'DN': return f'Classical.byContradiction (fun hh => {n(x[0])} hh)'
        if r == 'ANDI': return f'by first | exact ⟨{n(x[0])}, {n(x[1])}⟩ | exact ⟨{n(x[1])}, {n(x[0])}⟩'
        if r == 'ANDE1': return f'{n(x[0])}.1'
        if r == 'ANDE2': return f'{n(x[0])}.2'
        if r in ('ORI1', 'ORI2'): return f'by first | exact Or.inl {n(x[0])} | exact Or.inr {n(x[0])}'
        if r == 'ORE': return f'Or.elim {n(x[0])} {lam(x[1], x[2], ind)} {lam(x[3], x[4], ind)}'
        if r == 'BOTE': return f'False.elim {n(x[0])}'
        raise Bad('rule ' + r)
    def block(s, e, depth, ind):
        out, k = [], s
        while k < e:
            l = L[k]
            if l['rule'] == 'AS':
                k = box_end(k) + 1; continue          # rendered inside the closing rule's lambda
            if l['d'] != depth: raise Bad('depth')
            out.append(f"{' ' * ind}have n{l['i']} : {lean(l['f'])} := {term(l, ind)}\n")
            k += 1
        return ''.join(out)
    if L[-1]['d'] != 0: raise Bad('last line in a box')
    body = block(0, len(L), 0, 2)
    hyps = ' '.join(f'(h{j + 1} : {lean(p)})' for j, p in enumerate(prem))
    return hyps, f"{body}  exact n{L[-1]['i']}\n"

def check(items, tag='chk'):
    """items: list of (premises, goal, nd_proof_text). Returns list of (accepted: bool, reason)."""
    src, ranges, res = [], [], [None] * len(items)
    line = 1
    for k, (prem, goal, proof) in enumerate(items):
        try:
            hyps, body = render(prem, goal, nd_lines(proof))
        except (Bad, AssertionError, KeyError, IndexError, ValueError) as e:
            res[k] = (False, f'render: {e}'); continue
        txt = f"theorem t{k} (P Q R S T : Prop) {hyps} : {lean(goal)} := by\n{body}#print axioms t{k}\n\n"
        n = txt.count('\n'); ranges.append((k, line, line + n - 1)); line += n; src.append(txt)
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as fh:
        fh.write(''.join(src)); path = fh.name
    p = subprocess.run([LEAN, path], capture_output=True, text=True, timeout=3600)
    out = p.stdout + p.stderr
    errs = [int(m.group(1)) for m in re.finditer(r'^\S+?:(\d+):\d+: error', out, re.M)]
    axioms = {int(m.group(1)): m.group(2) for m in re.finditer(r"'t(\d+)' (depends on axioms: \[[^\]]*\]|does not depend on any axioms)", out)}
    for k, a, b in ranges:
        bad = [e for e in errs if a <= e <= b]
        ax = axioms.get(k)
        if bad: res[k] = (False, 'lean error')
        elif ax is None: res[k] = (False, 'no axioms line')
        elif 'sorryAx' in ax: res[k] = (False, 'sorry')
        else: res[k] = (True, ax)
    os.unlink(path)
    return res
