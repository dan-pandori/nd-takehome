#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Reviewer's independent Lean re-check of counted proofs.

I do not import the run's code.  My own ND-prompt parser builds the Lean theorem
statement, my own batching sends it to Lean 4 core together with the stored literal
sampled text, and I additionally require `#print axioms` to show only the three
classical axioms -- so a `sorry`/`sorryAx` proof could not pass my check even if it
passed the run's.

usage: review_sd_lean.py <spec.json>   where spec.json is {tag: [ {stmt, text, name, arm} ... ]}
"""
import json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

LEAN = os.path.expanduser('~/.elan/bin/lean')
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

# ---------------- my own ND -> Lean statement translator ----------------
ATOMS = {'P', 'Q', 'R', 'S'}
BIN = {'&': '∧', 'v': '∨', '>': '→'}


def parse_nd(toks, i=0):
    t = toks[i]
    if t in ATOMS:
        return t, i + 1
    if t == 'F':
        return 'False', i + 1
    if t != '(':
        raise ValueError('bad token ' + t)
    if toks[i + 1] == '~':
        a, j = parse_nd(toks, i + 2)
        if toks[j] != ')':
            raise ValueError('unclosed not')
        return f'(¬ {a})', j + 1
    a, j = parse_nd(toks, i + 1)
    op = toks[j]
    if op not in BIN:
        raise ValueError('bad op ' + op)
    b, k = parse_nd(toks, j + 1)
    if toks[k] != ')':
        raise ValueError('unclosed bin')
    return f'({a} {BIN[op]} {b})', k + 1


def nd_formula(s):
    toks = s.split()
    f, j = parse_nd(toks, 0)
    assert j == len(toks), (s, j)
    return f


def statement(prompt, k):
    """'THM p1 , p2 SEQ c PRF' -> 'theorem tK ( P Q R S : Prop ) ( h1 : .. ) : c :='"""
    m = re.match(r'^THM\s*(.*?)\s*SEQ\s+(.*?)\s+PRF$', prompt)
    assert m, prompt
    prem_s, concl = m.group(1), m.group(2)
    prems = [p.strip() for p in prem_s.split(',') if p.strip()] if prem_s.strip() else []
    hyps = ''.join(f' (h{j+1} : {nd_formula(p)})' for j, p in enumerate(prems))
    return f'theorem t{k} (P Q R S : Prop){hyps} : {nd_formula(concl)} := by'


# ---------------- my own Lean driver ----------------
def check(lines, tags, wd, tag):
    """lines: full one-line theorem sources.  Returns dict tag -> bool."""
    fn = os.path.join(wd, f'r_{tag}.lean')
    src = ['set_option linter.unusedVariables false']
    for i, l in enumerate(lines):
        # renumber to the LOCAL index of this file, so that a recursive split cannot
        # leave `#print axioms t0` pointing at a theorem named t20 (the bug my controls caught)
        src.append(re.sub(r'^theorem t\d+ ', f'theorem t{i} ', l, count=1))
        src.append(f'#print axioms t{i}')
    open(fn, 'w').write('\n'.join(src) + '\n')
    try:
        p = subprocess.run([LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True,
                           timeout=120 + 3 * len(lines))
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = '', -9
    os.remove(fn)
    ax = {}
    for m in re.finditer(r"'t(\d+)' depends on axioms: \[([^\]]*)\]", out):
        ax[int(m.group(1))] = {x.strip() for x in m.group(2).split(',') if x.strip()}
    for m in re.finditer(r"'t(\d+)' does not depend on any axioms", out):
        ax[int(m.group(1))] = set()
    clean = (rc == 0 and 'error' not in out and len(ax) == len(lines)
             and all(ax[i] <= ALLOWED for i in range(len(lines))))
    if clean:
        return {t: True for t in tags}, out
    if len(lines) == 1:
        return {tags[0]: False}, out
    h = len(lines) // 2
    a, _ = check(lines[:h], tags[:h], wd, tag + 'a')
    b, _ = check(lines[h:], tags[h:], wd, tag + 'b')
    a.update(b)
    return a, out


def main():
    spec = json.load(open(sys.argv[1]))
    held = {r['name']: r for r in (json.loads(l) for l in open('data/p2/heldout.jsonl'))}
    jobs = []            # (tag, source line)
    for tag, items in spec.items():
        for it in items:
            k = len(jobs)
            st = statement(held[it['name']]['prompt'], k)
            jobs.append((f"{tag}|{it.get('ckpt')}|{it['name']}|{k}", st + ' ' + it['text']))
    wd = tempfile.mkdtemp(prefix='revlean_')
    CH = 40
    chunks = [(list(range(i, min(i + CH, len(jobs)))), i) for i in range(0, len(jobs), CH)]
    print(f'{len(jobs)} proofs, {len(chunks)} chunks', flush=True)
    t0 = time.time()
    res = {}

    def do(c):
        ii, off = c
        # renumber so theorem names inside a file are t0..: statement already has tK with global k,
        # which is unique per file too, so leave it -- but #print axioms uses local index.
        lines = [jobs[k][1] for k in ii]
        tags = [jobs[k][0] for k in ii]
        r, _ = check(lines, tags, wd, str(off))
        return r

    with ThreadPoolExecutor(2) as ex:
        for i, r in enumerate(ex.map(do, chunks)):
            res.update(r)
            print(f'  chunk {i+1}/{len(chunks)} done, {time.time()-t0:.0f}s', flush=True)
    json.dump(res, open(sys.argv[1].replace('.json', '') + '.verdicts.json', 'w'), indent=1)
    bad = {k: v for k, v in res.items() if not v}
    print(f'{len(res)} re-checked, {len(bad)} rejected by my Lean pass')
    for k in sorted(bad):
        print('  REJECT', k)


main()
