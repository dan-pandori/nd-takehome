"""Reviewer (fast-stage1): independent Lean 4 re-check of literal lean_seq proof texts.
check(items) -> list[bool]; items = [(prompt, text)].  One theorem per line, `#print axioms` on the next;
a theorem is accepted iff no `error` message falls on its line(s) and its axioms are a subset of
{propext, Classical.choice, Quot.sound}.  Theorem names are assigned at file-write time (no recursion)."""
import sys, os, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lean_tok import prompt_tokens

OK_AX = {'propext', 'Classical.choice', 'Quot.sound'}


def header(prompt, name):
    toks = prompt_tokens(prompt)
    assert toks[0] == 'theorem' and toks[1] == 't'
    return ' '.join(['theorem', name] + toks[2:])


def check_file(items, chunk_id=0):
    lines = ['set_option maxHeartbeats 400000']
    where = {}
    for k, (prompt, text) in enumerate(items):
        name = f'rv{chunk_id}_{k}'
        where[len(lines) + 1] = k                # 1-based line of the theorem
        lines.append(header(prompt, name) + ' ' + text.replace('\n', ' '))
        where[len(lines) + 1] = k
        lines.append(f'#print axioms {name}')
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write('\n'.join(lines) + '\n'); fn = f.name
    p = subprocess.run(['lean', '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=3600)
    os.unlink(fn)
    out = p.stdout + p.stderr
    bad = set()
    axioms = {}
    cur = None
    for m in re.finditer(r'^\S+?:(\d+):\d+: (error|warning|info)[^:]*: ?(.*)$', out, re.M):
        ln, kind, msg = int(m.group(1)), m.group(2), m.group(3)
        k = where.get(ln)
        if k is None:
            if kind == 'error':
                raise RuntimeError('error outside a theorem line: ' + m.group(0))
            continue
        if kind == 'error':
            bad.add(k)
    # axioms: info messages "'name' depends on axioms: [..]" / "'name' does not depend on any axioms"
    for m in re.finditer(r"'(rv\d+_(\d+))' depends on axioms: \[([^\]]*)\]", out):
        axioms[int(m.group(2))] = {x.strip() for x in m.group(3).replace('\n', ' ').split(',') if x.strip()}
    for m in re.finditer(r"'(rv\d+_(\d+))' does not depend on any axioms", out):
        axioms[int(m.group(2))] = set()
    res = []
    for k in range(len(items)):
        ok = (k not in bad) and (k in axioms) and axioms[k] <= OK_AX
        res.append(ok)
    return res, out


def check(items, per=400):
    res = []
    for c in range(0, len(items), per):
        r, _ = check_file(items[c:c + per], c // per)
        res += r
    return res
