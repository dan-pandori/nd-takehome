"""C3C4 reviewer helpers (own code; no fork modules except where noted)."""
import json, gzip, re, os, subprocess, tempfile, itertools
ROOT = '/home/dan/review/claim-audit'
RAW = ROOT + '/audit/raw'
MY = ROOT + '/rv/raw'
LEAN = os.path.expanduser('~/.elan/bin/lean')

def jl(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        for l in f:
            if l.strip():
                yield json.loads(l)

def truthy(v):
    return v is True or v == 'True' or v == 'true'

# ---------- formula parsing (own) ----------
def parse_f(toks, i):
    t = toks[i]
    if t == '(':
        if toks[i+1] == '~':
            a, j = parse_f(toks, i+2); assert toks[j] == ')'; return ('not', a), j+1
        a, j = parse_f(toks, i+1); op = toks[j]; b, k = parse_f(toks, j+1); assert toks[k] == ')', toks[k]
        return ({'&': 'and', 'v': 'or', '>': 'imp'}[op], a, b), k+1
    if t == 'F': return ('bot',), i+1
    assert re.fullmatch(r'[A-Z]', t), t
    return ('atom', t), i+1

def parse_prompt(p):
    toks = p.split(); assert toks[0] == 'THM' and toks[-1] == 'PRF'
    i = 1; prem = []
    while toks[i] != 'SEQ':
        f, i = parse_f(toks, i); prem.append(f)
        if toks[i] == ',': i += 1
    c, i = parse_f(toks, i+1); assert i == len(toks)-1
    return prem, c

def lean_f(f):
    t = f[0]
    if t == 'atom': return f[1]
    if t == 'bot': return 'False'
    if t == 'not': return '( ¬ ' + lean_f(f[1]) + ' )'
    return '( %s %s %s )' % (lean_f(f[1]), {'and': '∧', 'or': '∨', 'imp': '→'}[t], lean_f(f[2]))

def statement(prompt, name='t'):
    prem, c = parse_prompt(prompt)
    hs = ' '.join('( h%d : %s )' % (k+1, lean_f(p)) for k, p in enumerate(prem))
    return 'theorem %s ( P Q R S : Prop ) %s : %s := by' % (name, hs, lean_f(c))

# ---------- canonical key invariant to atom renaming AND premise order (own) ----------
def fstr(f, m):
    t = f[0]
    if t == 'atom': return m[f[1]]
    if t == 'bot': return 'F'
    if t == 'not': return '~' + fstr(f[1], m)
    return '(' + fstr(f[1], m) + {'and': '&', 'or': 'v', 'imp': '>'}[t] + fstr(f[2], m) + ')'

def atoms(f, acc):
    if f[0] == 'atom': acc.add(f[1])
    elif f[0] == 'bot': pass
    else:
        for g in f[1:]: atoms(g, acc)
    return acc

def canon(prompt):
    prem, c = parse_prompt(prompt)
    A = set(); [atoms(p, A) for p in prem]; atoms(c, A); A = sorted(A)
    best = None
    for perm in itertools.permutations('abcd'[:len(A)]):
        m = dict(zip(A, perm))
        k = '|'.join(sorted(set(fstr(p, m) for p in prem))) + '=>' + fstr(c, m)   # premise multiset->set, order-free
        if best is None or k < best: best = k
    return best

# ---------- Lean driver (own) ----------
def lean_batch(srcs, tag='b'):
    """srcs: list of full theorem sources named t0..; returns list of (ok, msgs). Reject on ANY error/sorry."""
    body = 'set_option maxRecDepth 4000\n' + '\n'.join(s.replace('theorem t ', 'theorem t%d ' % k, 1) for k, s in enumerate(srcs)) + '\n'
    starts = []; line = 2
    for s in srcs:
        starts.append(line); line += s.count('\n') + 1
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, 'x.lean'); open(fn, 'w').write(body)
        r = subprocess.run(['flock', '/tmp/ca_lean.lock', 'nice', '-n', '10', LEAN, '-DmaxErrors=100000', fn],
                           capture_output=True, text=True, timeout=1800)
    out = r.stdout + r.stderr
    bad = [set() for _ in srcs]; msgs = [[] for _ in srcs]
    import bisect
    for m in re.finditer(r'x\.lean:(\d+):\d+: (error|warning)([^\n]*)', out):
        ln = int(m.group(1)); k = bisect.bisect_right(starts, ln) - 1
        if m.group(2) == 'error' or 'sorry' in m.group(3):
            bad[k].add(m.group(2)); msgs[k].append(m.group(3)[:120])
    unparsed = r.returncode != 0 and not any(bad)
    return [(not bad[k] and not unparsed, msgs[k]) for k in range(len(srcs))], out

def term_size(text):
    """own measure: nodes of the proof term = tokens of the literal text after deleting every type ascription
    `: <formula>` (have / fun binders, `( e : False )`) and the layout tokens have exact by ; := ( ) => , ⟩ fun.
    So names (n*, h*, hh), ⟨, Or.inl/Or.inr/Or.elim, Classical.byContradiction and glued projections each count 1."""
    toks = text.split(); out = []; i = 0
    while i < len(toks):
        if toks[i] == ':':
            i += 1
            if toks[i] == '(':
                d = 0
                while True:
                    d += toks[i] == '('; d -= toks[i] == ')'; i += 1
                    if d == 0: break
            else:
                i += 1
            continue
        out.append(toks[i]); i += 1
    drop = set('have exact by ; := ( ) => , ⟩ fun'.split())
    return sum(1 for t in out if t not in drop)

def nd_lines(nd):
    return len([x for x in nd.split(';') if x.strip().startswith('N')])
