"""Lean-check every Lean snippet in the blog (verbatim), parse its statement into an ND sequent, test it against the
textbook72 renaming classes (reviewer's sealkey, 4 keys) and against the cited K12 record's prompt. Prints no tb72 text."""
import json, re, subprocess, sys, gzip
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt, show
from sealkey import TB72, keys
BLOG = '/home/dan/work/proof-strategies/proof_strategies/blog.md'
LEAN = '/home/dan/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
txt = open(BLOG).read().split('\n')
snips = []
for ln, line in enumerate(txt, 1):
    for m in re.finditer(r'`(example [^`]*)`', line):
        snips.append((ln, m.group(1)))
# fenced lean block(s)
i = 0
while i < len(txt):
    if txt[i].strip() == '```lean':
        j = i + 1
        while txt[j].strip() != '```':
            j += 1
        snips.append((i + 2, '\n'.join(txt[i + 1:j])))
        i = j
    i += 1
snips = [s for s in snips if s[0] != 37]
print('snippets found (excluding the schematic on line 37):', len(snips))
# --- Lean statement parser -> ND tuples
TOK = re.compile(r'\s*(¬|∧|∨|→|\(|\)|[PQRS]|False)')
def tok(s):
    out, p = [], 0
    s = s.strip()
    while p < len(s):
        m = TOK.match(s, p)
        if not m: raise ValueError('tok at ' + s[p:])
        out.append(m.group(1)); p = m.end()
    return out
def parse(ts):
    pos = [0]
    def peek(): return ts[pos[0]] if pos[0] < len(ts) else None
    def eat(t=None):
        x = ts[pos[0]]; assert t is None or x == t, (x, t); pos[0] += 1; return x
    def atom():
        t = peek()
        if t == '¬': eat(); return ('~', atom())
        if t == '(':
            eat(); e = imp(); eat(')'); return e
        eat(); return 'F' if t == 'False' else t
    def conj():
        a = atom()
        if peek() == '∧': eat(); return ('&', a, conj())
        return a
    def disj():
        a = conj()
        if peek() == '∨': eat(); return ('v', a, disj())
        return a
    def imp():
        a = disj()
        if peek() == '→': eat(); return ('>', a, imp())
        return a
    e = imp(); assert pos[0] == len(ts), ts[pos[0]:]
    return e
def statement(code):
    head = code.split(':=')[0]
    rest = re.match(r'example\s*(.*)', head.strip(), re.S).group(1).strip()
    prem = []
    while rest.startswith('('):
        d = 0
        for j, ch in enumerate(rest):
            d += (ch == '(') - (ch == ')')
            if d == 0:
                break
        inner = rest[1:j]
        names, ty = inner.split(':', 1)
        if ty.strip() != 'Prop':
            prem.append(parse(tok(ty)))
        rest = rest[j + 1:].strip()
    assert rest.startswith(':'), rest
    return prem, parse(tok(rest[1:]))
T = TB72('/home/dan/review/proof-strategies/data/bs/textbook72.jsonl')
K12IDX = {53: 132941, 55: 95938, 57: 55304, 59: 16853, 61: 42672, 63: 47528, 65: 24177, 67: 43479, 69: 104971, 72: 70566, 75: 44059, 109: 131990}
want = set(K12IDX.values()); rec = {}
for i, l in enumerate(gzip.open('/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz', 'rt')):
    if i in want: rec[i] = json.loads(l)
res = []
for k, (ln, code) in enumerate(snips):
    fn = f'/tmp/blog_{k}.lean'
    body = code.replace('example', 'theorem tbk', 1)
    open(fn, 'w').write('set_option linter.unusedVariables false\n' + body + '\n#print axioms tbk\n')
    p = subprocess.run([LEAN, fn], capture_output=True, text=True, timeout=120)
    out = (p.stdout + p.stderr).strip()
    err = 'error' in out
    ax = re.findall(r"depends on axioms: \[([^\]]*)\]", out)
    axs = set(a.strip() for a in ax[0].split(',')) if ax else set()
    nodeps = 'does not depend on any axioms' in out
    ok = (not err) and (nodeps or axs <= {'propext', 'Classical.choice', 'Quot.sound'}) and (nodeps or ax)
    prem, concl = statement(code)
    hits = T.hits(prem, concl)
    idx = K12IDX.get(ln)
    srcmatch = None
    if idx is not None:
        p2, c2 = parse_prompt(rec[idx]['prompt'])
        srcmatch = ([show(x) for x in p2] == [show(x) for x in prem]) and show(c2) == show(concl)
    res.append({'k': k, 'blog_line': ln, 'lean_ok': ok, 'axioms': sorted(axs) if ax else ('none' if nodeps else '?'),
                'lean_out': out[:300], 'tb72_hits': sorted(hits), 'k12_index': idx, 'statement_equals_k12_prompt': srcmatch,
                'n_prem': len(prem)})
for r in res:
    print(json.dumps(r, ensure_ascii=False))
json.dump(res, open('/home/dan/review/proof-strategies/phase2/scripts/s5_lean_snippets.json', 'w'), indent=1, ensure_ascii=False)
