"""Reviewer-owned FOL Fitch -> Lean 4 core renderer and checker (independent of the executor's fol2lean.py and of the
sprint verifier: own tokenizer/parser/instance matcher). Term-mode, inlined tree terms (needed so ALLI/EXE can rebind
the eigen-parameter), explicit constructor names, type ascriptions `(e : T)`, and a context holding only the symbols
that occur.  Per theorem: unique name, `#print axioms`, sentinel after it; chunks of 50, run in parallel (<= 3 procs).
  python3 rv_fol.py POOL.jsonl OUT.json [--mutate]"""
import json, re, subprocess, sys, os, tempfile, collections
from concurrent.futures import ThreadPoolExecutor
LEAN = os.path.expanduser('~/.elan/bin/lean')
PRED = {'P': 1, 'Q': 1, 'R': 2, 'S': 2}

def pf(t, i):  # returns (formula, i)
    x = t[i]
    if x == 'F': return ('F',), i + 1
    if x in PRED:
        assert t[i + 1] == '('; j = i + 2; args = []
        while t[j] != ')': args.append(t[j]); j += 1
        assert len(args) == PRED[x]
        return ('at', x, tuple(args)), j + 1
    assert x == '(', x
    if t[i + 1] == '~':
        a, j = pf(t, i + 2); assert t[j] == ')'; return ('neg', a), j + 1
    if t[i + 1] in ('A', 'E'):
        v = t[i + 2]; a, j = pf(t, i + 3); assert t[j] == ')'
        return ('all' if t[i + 1] == 'A' else 'ex', v, a), j + 1
    a, j = pf(t, i + 1); op = t[j]; b, k = pf(t, j + 1); assert t[k] == ')'
    return ({'&': 'and', 'v': 'or', '>': 'imp'}[op], a, b), k + 1

def parse(text):
    t = text.split(); i = 1; prem = []
    while t[i] != 'SEQ':
        f, i = pf(t, i); prem.append(f)
        if t[i] == ',': i += 1
    concl, i = pf(t, i + 1); assert t[i] == 'PRF'; i += 1; L = {}
    while t[i] != 'QED':
        n = int(t[i][1:]); i += 1; d = 0
        while t[i] == '|': d += 1; i += 1
        f, i = pf(t, i); assert t[i] == ':'; rule = t[i + 1]; i += 2; refs = []
        while t[i] != ';': refs.append(int(t[i][1:])); i += 1
        L[n] = dict(f=f, rule=rule, refs=refs, d=d); i += 1
    return prem, concl, L

def inst(A, x, C):
    """term s with A[x:=s] == C (None if no match; x itself if x does not occur free)."""
    w = []
    def go(a, c, bound):
        if a[0] != c[0]: return False
        if a[0] == 'F': return True
        if a[0] == 'at':
            if a[1] != c[1]: return False
            for p, q in zip(a[2], c[2]):
                if p == x and x not in bound: w.append(q)
                elif p != q: return False
            return True
        if a[0] == 'neg': return go(a[1], c[1], bound)
        if a[0] in ('and', 'or', 'imp'): return go(a[1], c[1], bound) and go(a[2], c[2], bound)
        return a[1] == c[1] and go(a[2], c[2], bound | {a[1]})
    if not go(A, C, frozenset()) or len(set(w)) > 1: return None
    return w[0] if w else x

def syms(f, acc):
    if f[0] == 'at': acc.update(f[2])
    elif f[0] == 'neg': syms(f[1], acc)
    elif f[0] in ('and', 'or', 'imp'): syms(f[1], acc); syms(f[2], acc)
    elif f[0] in ('all', 'ex'): syms(f[2], acc)

def L4(f):
    k = f[0]
    if k == 'F': return 'False'
    if k == 'at': return '(' + f[1] + ' ' + ' '.join(f[2]) + ')'
    if k == 'neg': return f'(Not {L4(f[1])})'
    if k == 'and': return f'(And {L4(f[1])} {L4(f[2])})'
    if k == 'or': return f'(Or {L4(f[1])} {L4(f[2])})'
    if k == 'imp': return f'({L4(f[1])} → {L4(f[2])})'
    return f'({"∀" if k == "all" else "∃"} {f[1]} : U, {L4(f[2])})'

def render(text, name):
    prem, concl, L = parse(text)
    def T(n):
        l = L[n]; f = l['f']; r = l['rule']; R = l['refs']; g = lambda k: L[k]['f']
        if r in ('PR', 'AS'): return f'H{n}'
        if r == 'R': e = T(R[0])
        elif r == 'ANDI': e = f'(And.intro {T(R[0])} {T(R[1])})'
        elif r == 'ANDE1': e = f'(And.left {T(R[0])})'
        elif r == 'ANDE2': e = f'(And.right {T(R[0])})'
        elif r == 'ORI1': e = f'(Or.intro_left _ {T(R[0])})'
        elif r == 'ORI2': e = f'(Or.intro_right _ {T(R[0])})'
        elif r == 'IMPE':
            a, b = R
            fn, arg = (a, b) if g(a) == ('imp', g(b), f) else (b, a)
            e = f'({T(fn)} {T(arg)})'
        elif r == 'NEGE':
            a, b = R
            fn, arg = (b, a) if g(b) == ('neg', g(a)) else (a, b)
            e = f'(absurd {T(arg)} {T(fn)})'
        elif r in ('IMPI', 'NEGI'): s, t = R; e = f'(fun (H{s} : {L4(g(s))}) => {T(t)})'
        elif r == 'BOTE': e = f'(False.elim {T(R[0])})'
        elif r == 'DN': e = f'(Classical.byContradiction (fun (Hdn{n} : Not {L4(f)}) => {T(R[0])} Hdn{n}))'
        elif r == 'ORE':
            j, s1, e1, s2, e2 = R
            e = f'(Or.elim {T(j)} (fun (H{s1} : {L4(g(s1))}) => {T(e1)}) (fun (H{s2} : {L4(g(s2))}) => {T(e2)}))'
        elif r == 'ALLE': A = g(R[0]); e = f'({T(R[0])} {inst(A[2], A[1], f)})'
        elif r == 'EXI': e = f'(Exists.intro {inst(f[2], f[1], g(R[0]))} {T(R[0])})'
        elif r == 'ALLI': p = inst(f[2], f[1], g(R[0])); e = f'(fun ({p} : U) => {T(R[0])})'
        elif r == 'EXE':
            j, s, t2 = R; Ex = g(j); p = inst(Ex[2], Ex[1], g(s))
            e = f'(Exists.elim {T(j)} (fun ({p} : U) (H{s} : {L4(g(s))}) => {T(t2)}))'
        else: raise ValueError(r)
        return f'({e} : {L4(f)})'
    last = max(L); assert L[last]['f'] == concl and L[last]['d'] == 0
    S = set()
    for f in prem + [concl] + [l['f'] for l in L.values()]: syms(f, S)
    S -= {None}
    ctx = f'(U : Type) (P Q : U → Prop) (R S : U → U → Prop)' + (f' ({" ".join(sorted(S))} : U)' if S else '')
    hyp = ' '.join(f'(H{n} : {L4(L[n]["f"])})' for n in sorted(L) if L[n]['rule'] == 'PR')
    return f'theorem {name} {ctx} {hyp} : {L4(concl)} :=\n  {T(last)}\n#print axioms {name}\nexample : True := trivial\n'

def mutate(text, k):
    """deliberately wrong variants: swap the conclusion's last atom predicate or drop a premise."""
    t = text.split(); idx = [i for i, x in enumerate(t[:t.index('PRF')]) if x in PRED]
    if not idx: return None
    i = idx[-1]; t2 = list(t); t2[i] = {'P': 'Q', 'Q': 'P', 'R': 'S', 'S': 'R'}[t[i]]
    # change the same symbol in the final proof line only (statement and last line stay consistent, proof breaks)
    j = [i2 for i2, x in enumerate(t) if x in PRED][-1]; t2[j] = {'P': 'Q', 'Q': 'P', 'R': 'S', 'S': 'R'}[t[j]]
    return ' '.join(t2)

def check_chunk(srcs):
    d = tempfile.mkdtemp(); fn = os.path.join(d, 'c.lean'); open(fn, 'w').write(''.join(s for _, s in srcs))
    p = subprocess.run([LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True); out = p.stdout + p.stderr
    body = open(fn).read(); starts = [(body[:m.start()].count('\n') + 1, m.group(1)) for m in re.finditer(r'^theorem (\S+)', body, re.M)]
    bad = collections.defaultdict(list)
    for m in re.finditer(r':(\d+):\d+: error(?:\([^)]*\))?: (.*)', out):
        ln = int(m.group(1)); own = None
        for s, nm in starts:
            if s <= ln: own = nm
        bad[own].append(m.group(2)[:120])
    ax = dict(re.findall(r"'(\S+)' depends on axioms: \[([^\]]*)\]", out))
    noax = set(re.findall(r"'(\S+)' does not depend on any axioms", out))
    res = {}
    for nm, _ in srcs:
        a = ax.get(nm, '' if nm in noax else None)
        res[nm] = dict(ok=nm not in bad and a is not None and 'sorryAx' not in a, err=bad.get(nm, [])[:2], axioms=a)
    return res

if __name__ == '__main__':
    inp, outp = sys.argv[1], sys.argv[2]; mut = '--mutate' in sys.argv
    recs = [json.loads(l) for l in open(inp)]
    srcs, renderfail = [], []
    for k, r in enumerate(recs):
        txt = mutate(r['text'], k) if mut else r['text']
        if txt is None: continue
        try: srcs.append((f'rv{k}', render(txt, f'rv{k}')))
        except Exception as ex: renderfail.append((k, repr(ex)[:100]))
    chunks = [srcs[i:i + 50] for i in range(0, len(srcs), 50)]
    with ThreadPoolExecutor(3) as ex: parts = list(ex.map(check_chunk, chunks))
    res = {}; [res.update(p) for p in parts]
    json.dump(dict(n=len(recs), rendered=len(srcs), renderfail=renderfail, res=res), open(outp, 'w'))
    c = collections.Counter(v['ok'] for v in res.values())
    print(f'n={len(recs)} rendered={len(srcs)} renderfail={len(renderfail)} lean_ok={c[True]} lean_rej={c[False]}')
