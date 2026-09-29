"""Reviewer's own Lean re-check (state-frontier).  Independent of lean_gate / lean_judge / nd2lean.

check(items) with items = [(prompt, lean_text)] -> list of (ok, why).
The theorem statement is built from the THM prompt by this file's own translator; the body is the literal stored
text, unchanged.  ok iff Lean reports no error/warning for that theorem AND `#print axioms` lists nothing outside
{propext, Classical.choice, Quot.sound}.  Suspicious tokens (sorry, axiom, #, set_option, ...) reject outright.
"""
import os, re, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor

TR = {'~': '¬', '>': '→', 'v': '∨', '&': '∧', 'F': 'False', '(': '(', ')': ')'}
BAD = ('sorry', 'admit', 'axiom', '#', 'set_option', 'theorem', 'lemma', 'def ', 'macro', 'native', 'decide',
       'unsafe', 'import', 'open ', 'elab', 'syntax', 'instance', 'opaque', '\n', 'implemented_by', 'extern')
ALLOWED_AX = {'propext', 'Classical.choice', 'Quot.sound'}


def fml(s):
    out = []
    for t in s.split():
        if t in TR: out.append(TR[t])
        elif re.fullmatch(r'[PQRS]', t): out.append(t)
        else: raise ValueError(f'token {t!r}')
    return ' '.join(out)


def statement(prompt):
    m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', prompt.strip())
    prem, goal = m.group(1).strip(), m.group(2).strip()
    prems = [p.strip() for p in prem.split(' , ')] if prem else []
    hyps = ' '.join(f'(h{i + 1} : {fml(p)})' for i, p in enumerate(prems))
    return f'(P Q R S : Prop) {hyps} : {fml(goal)}'


def _run(chunk):
    src = []
    for k, (prompt, text) in chunk:
        src.append(f'theorem rv{k} {statement(prompt)} := by\n  {text}\n#print axioms rv{k}\n')
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write('set_option linter.all false\nset_option linter.unusedVariables false\n' + '\n'.join(src)); fn = f.name
    p = subprocess.run(['lean', '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=3600)
    os.unlink(fn)
    lines = open_lines = src_lines = None
    # map line numbers -> theorem index
    starts, ln = [], 3
    for (k, _), s in zip(chunk, src):
        starts.append((ln, k)); ln += s.count('\n') + 1
    def owner(n):
        o = None
        for a, k in starts:
            if a <= n: o = k
        return o
    bad = {}
    for m in re.finditer(r'^[^\n]*?:(\d+):\d+: (error|warning)[^\n]*', p.stdout, re.M):
        k = owner(int(m.group(1))); bad.setdefault(k, m.group(0)[-160:])
    axioms = {}
    for m in re.finditer(r"'rv(\d+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", p.stdout):
        k = int(m.group(1)); ax = {a.strip() for a in (m.group(3) or '').split(',') if a.strip()}
        axioms[k] = ax
    res = {}
    for k, _ in chunk:
        if k in bad: res[k] = (False, bad[k])
        elif k not in axioms: res[k] = (False, 'no axioms line')
        elif axioms[k] - ALLOWED_AX: res[k] = (False, f'axioms {axioms[k] - ALLOWED_AX}')
        else: res[k] = (True, 'ok')
    return res


def check(items, chunk=150, workers=2):
    out = [None] * len(items)
    todo = []
    for k, (prompt, text) in enumerate(items):
        if any(b in text for b in BAD): out[k] = (False, 'bad token')
        else: todo.append((k, (prompt, text)))
    chunks = [todo[i:i + chunk] for i in range(0, len(todo), chunk)]
    with ThreadPoolExecutor(workers) as ex:
        for res in ex.map(_run, chunks):
            for k, v in res.items(): out[k] = v
    return out
