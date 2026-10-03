#!/usr/bin/env python3
"""Copied for the textbook72 review from review_se/lean_recheck.py (reviewer-owned, run state-env); change: the
error regex also matches Lean 4.34's `error(code):` form.  Original docstring: Reviewer Lean re-check for run state-env.  Two renderings of each stored ND proof, both checked by Lean 4 core:
  mine : my own ND -> Lean term-mode translator (written for this review; does not import nd2lean / lean_tok)
  seq  : lean_tok.proof_tokens + statement, i.e. the lean_seq text the environment would assemble (modulo names)
One theorem per line, `#print axioms` on the next line; any error in a theorem's line range rejects it; axioms must be a
subset of {propext, Classical.choice, Quot.sound}.  Renumbering happens where the file is written (no recursion)."""
import json, re, os, subprocess, tempfile, sys, collections
LEAN = os.path.expanduser('~/.elan/bin/lean')
SYM = {'&': '∧', 'v': '∨', '>': '→', '~': '¬', 'F': 'False'}
OKAX = {'propext', 'Classical.choice', 'Quot.sound'}

def lf(s):
    return ' '.join(SYM.get(t, t) for t in s.split())

def parse_prompt(prompt):
    m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', prompt.strip())
    lhs, c = m.group(1).strip(), m.group(2).strip()
    prem = [p.strip() for p in lhs.split(' , ')] if lhs else []
    return prem, c

def parse_nd(proof):
    out = []
    for s in proof.split(' ; '):
        s = s.strip()
        if s == 'QED' or not s: continue
        m = re.fullmatch(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)', s)
        if not m: raise ValueError('line: ' + s)
        out.append({'i': int(m.group(1)), 'd': len(m.group(2)) // 2, 'f': m.group(3).strip(), 'r': m.group(4),
                    'refs': [int(x[1:]) for x in m.group(5).split()]})
    return out

class Box:
    def __init__(self, hyp, body): self.hyp, self.body = hyp, body

def build(L):
    boxes = {}
    def box(i, d):
        hyp = L[i]; i += 1; body = []
        while i < len(L) and L[i]['d'] >= d:
            if L[i]['d'] == d:
                if L[i]['r'] == 'AS': break
                body.append(L[i]); i += 1
            else:
                b, i = box(i, L[i]['d']); body.append(b)
        bx = Box(hyp, body); boxes[hyp['i']] = bx
        return bx, i
    top = []; i = 0
    while i < len(L):
        if L[i]['d'] == 0:
            if L[i]['r'] == 'AS': raise ValueError('AS at depth 0')
            top.append(L[i]); i += 1
        else:
            b, i = box(i, L[i]['d']); top.append(b)
    return top, boxes

def translate(prompt, proof, thm_name):
    prem, c = parse_prompt(prompt)
    L = parse_nd(proof)
    F = {x['i']: x['f'] for x in L}
    top, boxes = build(L)
    npr = [0]
    def n(i): return f'n{i}'
    def rbox(s, e):
        b = boxes[s]
        st = [stmt(x) for x in b.body if isinstance(x, dict)]
        return f'(fun ({n(s)} : {lf(b.hyp["f"])}) => by ' + ''.join(x + '; ' for x in st) + f'exact {n(e)})'
    def app2(r):
        a, b = r
        fa, fb = F[a], F[b]
        if fa.startswith('( ') and fa.endswith(' )') and (fa == f'( {fb} > {fa[2 + len(fb) + 3:-2]} )' if fa.startswith(f'( {fb} > ') else False):
            return f'{n(a)} {n(b)}'
        if fb.startswith(f'( {fa} > ') or fb == f'( ~ {fa} )':
            return f'{n(b)} {n(a)}'
        if fa == f'( ~ {fb} )':
            return f'{n(a)} {n(b)}'
        return f'{n(a)} {n(b)}'
    def stmt(x):
        r, rf = x['r'], x['refs']
        if r == 'PR': npr[0] += 1; t = f'h{npr[0]}'
        elif r == 'R': t = n(rf[0])
        elif r == 'ANDI': t = f'⟨{n(rf[0])}, {n(rf[1])}⟩'
        elif r == 'ANDE1': t = f'{n(rf[0])}.1'
        elif r == 'ANDE2': t = f'{n(rf[0])}.2'
        elif r in ('IMPE', 'NEGE'): t = app2(rf)
        elif r == 'ORI1': t = f'Or.inl {n(rf[0])}'
        elif r == 'ORI2': t = f'Or.inr {n(rf[0])}'
        elif r == 'BOTE': t = f'{n(rf[0])}.elim'
        elif r == 'DN': t = f'Classical.byContradiction (fun hh => {n(rf[0])} hh)'
        elif r in ('IMPI', 'NEGI'): t = rbox(rf[0], rf[1])
        elif r == 'ORE': t = f'Or.elim {n(rf[0])} {rbox(rf[1], rf[2])} {rbox(rf[3], rf[4])}'
        else: raise ValueError(r)
        return f'have {n(x["i"])} : {lf(x["f"])} := {t}'
    st = [stmt(x) for x in top if isinstance(x, dict)]
    last = [x for x in top if isinstance(x, dict)][-1]['i']
    hs = ''.join(f' (h{k + 1} : {lf(p)})' for k, p in enumerate(prem))
    return f'theorem {thm_name} (P Q R S : Prop){hs} : {lf(c)} := by ' + ''.join(s + '; ' for s in st) + f'exact {n(last)}'

def seq_render(prompt, proof, thm_name):
    sys.path.insert(0, os.environ.get('REPO', '.'))
    import lean_tok
    toks = lean_tok.proof_tokens(proof)
    ts = [f'n{t[1]}' if isinstance(t, tuple) else t for t in toks]
    tk = lean_tok.LeanTokenizer.__new__(lean_tok.LeanTokenizer)
    body = lean_tok.LeanTokenizer.text(tk, ts)
    st = ' '.join(lean_tok.prompt_tokens(prompt)).replace('theorem t ', f'theorem {thm_name} ', 1)
    return f'{st} {body}'

def check(items, render, chunk=300):
    """items: list of (prompt, proof) -> list of (ok, reason)"""
    res = []
    for c0 in range(0, len(items), chunk):
        part = items[c0:c0 + chunk]
        lines = ['set_option maxRecDepth 4000', 'set_option linter.unusedVariables false']
        rng = []; pre = [None] * len(part)
        for k, (p, pf) in enumerate(part):
            nm = f'rv{k}'
            try:
                src = render(p, pf, nm)
            except Exception as e:
                pre[k] = f'render: {type(e).__name__} {e}'; rng.append(None); continue
            assert '\n' not in src
            a = len(lines) + 1
            lines.append(src); lines.append(f'#print axioms {nm}')
            rng.append((a, a + 1))
        fd, fn = tempfile.mkstemp(suffix='.lean', dir='/tmp'); os.close(fd)
        open(fn, 'w').write('\n'.join(lines) + '\n')
        p = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=3600)
        o = p.stdout + p.stderr
        os.remove(fn)
        bad = collections.defaultdict(list); ax = {}
        for m in re.finditer(r'^\S*?:(\d+):\d+: error(?:\([^)]*\))?: (.*)$', o, re.M):
            ln = int(m.group(1)); hit = False
            for k, r in enumerate(rng):
                if r and r[0] <= ln <= r[1]:
                    bad[k].append(m.group(2)[:200]); hit = True
            if not hit:
                for k in range(len(part)): bad[k].append('stray error line %d' % ln)
        for m in re.finditer(r"^'rv(\d+)' (does not depend on any axioms|depends on axioms: \[(.*?)\])", o, re.M):
            ax[int(m.group(1))] = m.group(2)
        for k in range(len(part)):
            if pre[k]: res.append((False, pre[k])); continue
            if bad[k]: res.append((False, 'lean: ' + bad[k][0].replace('\n', ' ')[:160])); continue
            a = ax.get(k)
            if a is None: res.append((False, 'no axioms line')); continue
            if 'does not depend on any axioms' in a: res.append((True, '')); continue
            used = set(x.strip() for x in a.split('[', 1)[1].rstrip(']').split(','))
            if used <= OKAX: res.append((True, ''))
            else: res.append((False, f'axioms {sorted(used)}'))
    return res
