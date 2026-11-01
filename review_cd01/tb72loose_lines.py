#!/usr/bin/env python3
"""Reviewer (coe-dose01): where are the loose (co-occurrence) textbook72 hits, and were those lines added by this run?
Prints file, line number, added-by-run flag, premise count of the matched class and the kind of line -- never the line."""
import re, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from tb72scan import tb72_variants, formulas
V = tb72_variants()
def added(fn):
    d = subprocess.run(['git', 'diff', '-U0', '8e195390', 'ec488738', '--', fn], capture_output=True, text=True).stdout
    a = set(); cur = None
    for l in d.splitlines():
        m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', l)
        if m:
            cur = int(m.group(1)); continue
        if cur is not None and l.startswith('+') and not l.startswith('+++'):
            a.add(cur); cur += 1
    return a
for fn in sys.argv[1:]:
    ad = added(fn); hits = []
    for i, ln in enumerate(open(fn, errors='ignore').read().splitlines(), 1):
        if not any(ch in ln for ch in 'PQRS'):
            continue
        F = formulas(ln)
        for npre, nc, vs, _ in V:
            if npre == 0 and nc < 2:
                continue
            if any(c in F and all(x in F for x in pre) for pre, c in vs):
                kind = 'ND proof' if (': PR' in ln or ': AS' in ln or ': IMPI' in ln) else 'Lean code' if (':=' in ln or 'have ' in ln) else 'prose/table'
                hits.append((i, i in ad, npre, kind)); break
    print(fn, '(line, added by this run, premises of matched class, kind):', hits)
