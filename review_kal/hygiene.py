#!/usr/bin/env python3
"""textbook72 hygiene: does any file of the run print a textbook72 theorem?  Every sequent-like span in every file is keyed
with the premise-order-invariant renaming class (kc.key_inv) and looked up among textbook72's 72 classes:
  ND prompts 'THM ... SEQ ... PRF', thm strings '... |- ...', and Lean statements / states written with ⊢.
Also every textbook72 conclusion of >= 7 nodes is searched literally, in ND and Lean syntax.  Prints file names, theorem
NAMES (hashes) and counts only.  Eval rows (artifacts/kalmar/eval/*.rows.jsonl.gz) carry textbook72 prompts by design
(the scoring read) and are counted separately.

  python3 review_kal/hygiene.py [paths...] -> stdout (default: artifacts/kalmar data/kalmar kalmar/ preregistration/kalmar-pretrain.md)
"""
import collections, gzip, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

TB = list(kc.rows(os.path.join(kc.ROOT, 'data', 'bs', 'textbook72.jsonl')))
KEYS = {}
for r in TB:
    p, g = kc.sequent(r)
    KEYS[kc.key_inv(p, g)] = r['name']
LEAN = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}


def lean_of(s):
    return ' '.join(LEAN.get(t, t) for t in s.split())


LIT = []
for r in TB:
    p, g = kc.sequent(r)
    if kc.size(kc.parse(g)) >= 7:
        LIT.append((r['name'], g, lean_of(g), lean_of(g).replace(' ', '')))
PROMPT = re.compile(r'THM ((?:[^P]|P(?!RF))*?) PRF')
THM = re.compile(r'((?:[\(\)~&v>FPQRS,]\s*)+)\|-\s*((?:[\(\)~&v>FPQRS]\s*)+)')


def check_text(txt, hits):
    for m in PROMPT.finditer(txt):
        try:
            p, g = kc.split_prompt('THM ' + m.group(1) + ' PRF')
            k = kc.key_inv(p, g)
        except Exception:
            continue
        if k in KEYS:
            hits['prompt:' + KEYS[k]] += 1
    for m in THM.finditer(txt):
        try:
            p, g = kc.split_thm(m.group(1) + ' |- ' + m.group(2))
            for x in p + [g]:
                kc.parse(x)
            k = kc.key_inv(p, g)
        except Exception:
            continue
        if k in KEYS:
            hits['thm:' + KEYS[k]] += 1
    for name, g, gl, gl2 in LIT:
        if g in txt or gl in txt or gl2 in txt:
            hits['concl:' + name] += 1


def scan(path):
    hits = collections.Counter()
    op = gzip.open if path.endswith('.gz') else open
    try:
        with op(path, 'rt', errors='replace') as f:
            for line in f:
                check_text(line, hits)
    except (OSError, EOFError):
        return None
    return hits


paths = sys.argv[1:] or [os.path.join(kc.ROOT, x) for x in ('artifacts/kalmar', 'data/kalmar', 'kalmar', 'preregistration/kalmar-pretrain.md')]
files = []
for p in paths:
    if os.path.isdir(p):
        for dp, dn, fn in os.walk(p):
            files += [os.path.join(dp, x) for x in fn]
    else:
        files.append(p)
by_design = collections.Counter(); found = {}
for fn in sorted(files):
    if fn.endswith(('.pt', '.png', '.pdf', '.tgz')) or 'train_kal_sl' in fn:
        continue
    h = scan(fn)
    if not h:
        continue
    if '/eval/' in fn and fn.endswith('.rows.jsonl.gz'):
        by_design[os.path.basename(fn)] = sum(h.values())
        continue
    found[os.path.relpath(fn, kc.ROOT)] = dict(h)
print('eval rows with textbook72 prompts (scoring read, by design):', len(by_design), 'files')
print('OTHER files with a textbook72 sequent or conclusion:', len(found))
for fn, h in found.items():
    print('  ', fn, h)
