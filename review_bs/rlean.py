#!/usr/bin/env python3
"""(copied from review_sx/rlean.py on dan_search-expert, reviewer code; box cite relaxed) Reviewer's own ND-string -> literal lean_seq-style Lean text renderer and batched Lean checker.
Rendering follows the documented term map (lean_tok.py docstring); written independently.  A theorem passes iff the
file line holding it produces no error AND `#print axioms` lists only {propext, Classical.choice, Quot.sound}."""
import re, subprocess, tempfile, os, json
SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False', '(': '(', ')': ')', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S'}
def fm(toks): return ' '.join(SYM[t] for t in toks)
def stmt(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    prem = [p.split() for p in re.split(r' , (?![^()]*\))', prem.strip())] if prem.strip() else []
    # split premises on top-level commas only
    toks = body.split(' SEQ ')[0].split(); prem = []; cur = []; d = 0
    for t in toks:
        if t == ',' and d == 0: prem.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: prem.append(cur)
    return prem, concl.split()
def parse_nd(nd):
    lines = []
    for part in nd.split(' ; '):
        part = part.strip()
        if part == 'QED': break
        t = part.split(); idx = int(t[0][1:]); j = 1; depth = 0
        while t[j] == '|': depth += 1; j += 1
        c = len(t) - 1 - t[::-1].index(':')
        f = t[j:c]; rule = t[c + 1]; refs = [int(x[1:]) for x in t[c + 2:]]
        lines.append((idx, depth, f, rule, refs))
    return lines
def render(prompt, nd, flip=None):
    """-> Lean tactic-sequence text for the proof body. flip: optional (a, b) token swap for negative controls."""
    L = parse_nd(nd)
    stack = [[]]; hyp = [None]; last = [None]; boxes = {}; npr = 0
    def close():
        s = stack.pop(); h = hyp.pop(); l = last.pop(); boxes[h[0]] = (h[1], s, l)
    def box(s, e, neg):
        hf, st, l = boxes[s]
        # any in-scope line may be cited (Lean decides); the ND rule format would demand e == last
        ex = f'exact ( n{e} : False )' if neg else f'exact n{e}'
        return f'( fun ( n{s} : {fm(hf)} ) => by ' + ''.join(x + ' ; ' for x in st) + ex + ' )'
    for idx, d, f, rule, refs in L:
        if rule == 'AS':
            while len(stack) - 1 >= d: close()
            stack.append([]); hyp.append((idx, f)); last.append(idx); continue
        while len(stack) - 1 > d: close()
        n = lambda j: f'n{j}'
        if rule == 'PR': npr += 1; term = f'h{npr}'
        elif rule == 'R': term = n(refs[0])
        elif rule == 'ANDI': term = f'⟨ {n(refs[0])} , {n(refs[1])} ⟩'
        elif rule == 'ANDE1': term = f'{n(refs[0])}.1'
        elif rule == 'ANDE2': term = f'{n(refs[0])}.2'
        elif rule == 'IMPE': term = f'{n(refs[0])} {n(refs[1])}'
        elif rule == 'NEGE': term = f'{n(refs[1])} {n(refs[0])}'
        elif rule == 'ORI1': term = f'Or.inl {n(refs[0])}'
        elif rule == 'ORI2': term = f'Or.inr {n(refs[0])}'
        elif rule == 'BOTE': term = f'{n(refs[0])}.elim'
        elif rule == 'DN': term = f'Classical.byContradiction ( fun hh => {n(refs[0])} hh )'
        elif rule == 'IMPI': term = box(refs[0], refs[1], False)
        elif rule == 'NEGI': term = box(refs[0], refs[1], True)
        elif rule == 'ORE': term = f'Or.elim {n(refs[0])} ' + box(refs[1], refs[2], False) + ' ' + box(refs[3], refs[4], False)
        else: raise ValueError('rule ' + rule)
        if flip and rule in ('ORI1', 'ORI2'): term = term.replace(flip[0], '\0').replace(flip[1], flip[0]).replace('\0', flip[1])
        stack[-1].append(f'have n{idx} : {fm(f)} := {term}'); last[-1] = idx
    while len(stack) > 1: close()
    return ''.join(x + ' ; ' for x in stack[0]) + f'exact n{L[-1][0]}'
def header(prompt, k):
    prem, concl = stmt(prompt)
    hs = ' '.join(f'( h{j+1} : {fm(p)} )' for j, p in enumerate(prem))
    return f'theorem rv{k} ( P Q R S : Prop ) {hs} : {fm(concl)} := by '
OKAX = {'propext', 'Classical.choice', 'Quot.sound'}
SIZE = r'''
open Lean Elab Command in
elab "rvsize " n:ident : command => do
  let env ← getEnv
  match env.find? n.getId with
  | some ci => match (match ci with | .thmInfo t => some t.value | .defnInfo d => some d.value | _ => none) with
    | some v =>
      let rec go : Expr → Nat
        | .app f a => go f + go a
        | .lam _ _ b _ => 1 + go b
        | .letE _ _ v b _ => go v + go b
        | .mdata _ b => go b
        | .proj _ _ b => 1 + go b
        | .bvar _ => 1
        | .const _ _ => 1
        | _ => 0
      logInfo m!"RVSIZE {n.getId} {go v}"
    | none => logInfo m!"RVSIZE {n.getId} -1"
  | none => logInfo m!"RVSIZE {n.getId} -2"
'''
def check(items, per_file=200, size=False):
    """items: list of (prompt, body_text). Returns list of (ok, info, size)."""
    out = []
    for s in range(0, len(items), per_file):
        chunk = items[s:s + per_file]
        pre = ('import Lean\n' if size else '') + 'set_option linter.unusedVariables false\nset_option maxRecDepth 4000\n' + (SIZE if size else '')
        npre = pre.count('\n')
        lines = []
        for k, (p, b) in enumerate(chunk):
            lines.append(header(p, k) + b.replace('\n', ' '))
            lines.append(f'#print axioms rv{k}')
            if size: lines.append(f'rvsize rv{k}')
        with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
            f.write(pre + '\n'.join(lines) + '\n'); fn = f.name
        r = subprocess.run(['lean', fn], capture_output=True, text=True, timeout=3600)
        txt = r.stdout + r.stderr; os.unlink(fn)
        per = 3 if size else 2
        err = set(); ax = {}; sz = {}
        for m in re.finditer(r':(\d+):\d+: error', txt):
            ln = int(m.group(1)) - npre - 1
            err.add(ln // per if ln >= 0 else -1)
        # axioms messages: "'rvK' depends on axioms: [a, b]" or "'rvK' does not depend on any axioms"
        for m in re.finditer(r"'rv(\d+)' depends on axioms: \[([^\]]*)\]", txt):
            ax[int(m.group(1))] = {a.strip() for a in m.group(2).split(',')}
        for m in re.finditer(r"'rv(\d+)' does not depend on any axioms", txt):
            ax[int(m.group(1))] = set()
        for m in re.finditer(r'RVSIZE rv(\d+) (-?\d+)', txt):
            sz[int(m.group(1))] = int(m.group(2))
        for k in range(len(chunk)):
            ok = -1 not in err and k not in err and k in ax and ax[k] <= OKAX
            out.append((ok, 'err' if k in err else ('ax:' + ','.join(sorted(ax.get(k, {'?'}))) if not ok else ''), sz.get(k)))
    return out
