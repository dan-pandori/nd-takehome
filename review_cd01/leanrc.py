#!/usr/bin/env python3
"""Reviewer (coe-dose01): own Lean 4 harness for literal sampled texts.

check(items) -> list of (ok, reason).  items: (prompt 'THM ... SEQ ... PRF', lean tactic text).
Each theorem is ONE line `theorem t<k> (P Q R S : Prop) (h1 : ..) .. : C := by <text>` followed by `#print axioms t<k>`.
Accept iff (a) no `error` message on the theorem's line, (b) its axioms line was printed, and (c) the axioms are a subset of
{propext, Classical.choice, Quot.sound} (so `sorry` -> sorryAx is rejected).  Numbering is per file, assigned where the
file is written; a crashed file is re-run one theorem per file.

sizes(items) -> list of term sizes (inference nodes, the project's lean_check definition re-implemented in my own meta
code: 1 per application headed by a logical inference constant, 1 per argument of an application headed by a local
hypothesis, 1 per proof `fun` binder, 1 per projection; `letFun v (fun x => b)` = size v + size b; variables, types,
mdata 0).  Needs `import Lean` (~1.6 GB per process on the VPS): run one process at a time, small files.
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import lean_statement

LEAN = os.path.expanduser('~/.elan/bin/lean')
PRE = 'set_option linter.unusedVariables false\nset_option maxRecDepth 4000\n'
OKAX = {'propext', 'Classical.choice', 'Quot.sound'}
ERR = re.compile(r':(\d+):\d+: error')
AX = re.compile(r"'t(\d+)' depends on axioms: \[([^\]]*)\]")
NOAX = re.compile(r"'t(\d+)' does not depend on any axioms")


def _file(items):
    lines = PRE.splitlines()
    tline = {}
    for k, (prompt, text) in enumerate(items):
        stmt = lean_statement(prompt, name=f't{k}')
        body = ' '.join(text.split('\n'))
        lines.append(f'{stmt} {body}')
        tline[len(lines)] = k            # 1-based line number of theorem k
        lines.append(f'#print axioms t{k}')
    return '\n'.join(lines) + '\n', tline


def _run(items, timeout=None):
    src, tline = _file(items)
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write(src); fn = f.name
    try:
        p = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=timeout or 120 + 3 * len(items))
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        out, rc = '', -9
    os.unlink(fn)
    bad = {}
    for m in ERR.finditer(out):
        ln = int(m.group(1))
        k = tline.get(ln)
        if k is None:
            k = tline.get(ln - 1)        # an error reported on the #print line belongs to the theorem above
        if k is not None:
            bad.setdefault(k, 'error')
    ax = {}
    for m in AX.finditer(out):
        ax[int(m.group(1))] = {a.strip() for a in m.group(2).split(',') if a.strip()}
    for m in NOAX.finditer(out):
        ax[int(m.group(1))] = set()
    res = []
    for k in range(len(items)):
        if k in bad:
            res.append((False, bad[k]))
        elif k not in ax:
            res.append((False, 'no axioms line'))
        elif not ax[k] <= OKAX:
            res.append((False, 'axioms ' + ','.join(sorted(ax[k] - OKAX))))
        else:
            res.append((True, 'ok'))
    crashed = rc not in (0, 1) or (rc == 1 and not bad)
    return res, crashed, out


def check(items, chunk=250):
    res = []
    for i in range(0, len(items), chunk):
        part = items[i:i + chunk]
        r, crashed, _ = _run(part)
        if crashed and len(part) > 1:
            r = [_run([it])[0][0] for it in part]
        res += r
    return res


SIZE_PRE = r'''import Lean
open Lean Elab Command Meta
set_option linter.unusedVariables false
set_option maxRecDepth 4000
def rvInf : List Name := [``And.intro, ``And.left, ``And.right, ``Or.inl, ``Or.inr, ``Or.elim, ``False.elim, ``absurd,
  ``Iff.intro, ``Iff.mp, ``Iff.mpr, ``Classical.byContradiction, ``And.rec, ``And.casesOn, ``Or.rec, ``Or.casesOn,
  ``False.rec, ``Iff.rec, ``Iff.casesOn, ``Not.elim, ``Not.intro, ``And.elim, ``Iff.elim]
partial def rvSize (e : Expr) : Nat :=
  match e with
  | .mdata _ b => rvSize b
  | .proj _ _ b => 1 + rvSize b
  | .lam _ ty b _ => (if ty.isSort then 0 else 1) + rvSize b
  | .letE _ _ v b _ => rvSize v + rvSize b
  | .app .. =>
    let f := e.getAppFn
    let args := e.getAppArgs
    if f.isConstOf ``letFun && args.size == 4 then
      rvSize args[2]! + (match args[3]! with | .lam _ _ b _ => rvSize b | o => rvSize o)
    else if f.isConst && rvInf.contains f.constName! then
      1 + (args.foldl (fun s a => s + rvSize a) 0)
    else if f.isFVar || f.isBVar then
      args.size + (args.foldl (fun s a => s + rvSize a) 0)
    else
      args.foldl (fun s a => s + rvSize a) 0
  | _ => 0
partial def rvStrip : Nat → Expr → Expr
  | 0, e => e
  | n+1, .lam _ _ b _ => rvStrip n b
  | _, e => e
elab "#rvsize " id:ident n:num : command => do
  let env ← getEnv
  match env.find? id.getId with
  | some (.thmInfo t) => logInfo m!"RVSIZE {id.getId} {rvSize (rvStrip n.getNat t.value)}"
  | _ => logInfo m!"RVSIZE {id.getId} NA"
'''


def sizes(items):
    """term sizes (None where the theorem does not elaborate)"""
    lines = SIZE_PRE.splitlines()
    for k, (prompt, text) in enumerate(items):
        stmt = lean_statement(prompt, name=f't{k}')
        n_par = 4 + stmt.count('(h')
        lines.append(f"{stmt} {' '.join(text.split(chr(10)))}")
        lines.append(f'#rvsize t{k} {n_par}')
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write('\n'.join(lines) + '\n'); fn = f.name
    p = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=600 + 5 * len(items))
    os.unlink(fn)
    got = {int(m.group(1)): (None if m.group(2) == 'NA' else int(m.group(2))) for m in re.finditer(r'RVSIZE t(\d+) (\d+|NA)', p.stdout + p.stderr)}
    return [got.get(k) for k in range(len(items))]


if __name__ == '__main__':
    # test sequents are compound instances checked not to be textbook72 renaming classes
    tests = [('THM ( ( P & R ) > Q ) , ( P & R ) SEQ Q PRF', 'exact h1 h2', True),
             ('THM ( ( P & R ) > Q ) , ( P & R ) SEQ Q PRF', 'sorry', False),
             ('THM ( ( P & R ) > Q ) , ( P & R ) SEQ Q PRF', 'exact h2', False),
             ('THM SEQ ( ( P & Q ) v ( ~ ( P & Q ) ) ) PRF', 'exact Classical.byContradiction ( fun hh => hh ( Or.inr ( fun p => hh ( Or.inl p ) ) ) )', True),
             ('THM ( P & R ) SEQ ( ( P & R ) & ( P & R ) ) PRF', 'have n1 : ( P ∧ R ) := h1 ; exact ⟨ n1 , n1 ⟩', True)]
    r = check([(a, b) for a, b, _ in tests])
    print('harness unit tests:', ['PASS' if ok == e else f'FAIL {why}' for (ok, why), (_, _, e) in zip(r, tests)])
    print('sizes:', sizes([(a, b) for a, b, e in tests if e]))
