#!/usr/bin/env python3
"""Reviewer's own quote checker (independent of the executor's verify_ledger.py).
usage: qcheck.py <ledger.tsv> [...]   — every row's quote must occur in its source file after normalisation.
Normalisation: NFKC, unify quotes/dashes/minus, drop soft hyphens/zero-width chars, collapse all whitespace, casefold.
Exit status 1 if any row fails. Rows with quote '-' are skipped (not-reported placeholders)."""
import sys, csv, os, re, unicodedata
HOME = os.path.expanduser('~')
TR = str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-',
                    '−': '-', '‐': '-', '‑': '-', ' ': ' ', ' ': ' ', ' ': ' '})
def norm(s):
    s = unicodedata.normalize('NFKC', s).translate(TR)
    s = re.sub('[­​‌‍﻿]', '', s)
    return re.sub(r'\s+', ' ', s).strip().casefold()
_cache = {}
def text(path):
    if path not in _cache:
        p = path if os.path.isabs(path) else os.path.join(HOME, path)
        _cache[path] = norm(open(p, errors='replace').read()) if os.path.exists(p) else None
    return _cache[path]
def check(rows):
    bad = []
    for r in rows:
        q = r.get('quote', '')
        if q.strip() in ('', '-'):
            continue
        t = text(r['source_file'])
        if t is None:
            bad.append((r['row_id'], 'MISSING FILE ' + r['source_file']))
        elif norm(q) not in t:
            bad.append((r['row_id'], 'NOT FOUND: ' + q[:90]))
    return bad
if __name__ == '__main__':
    tot = nb = 0
    for f in sys.argv[1:]:
        rows = list(csv.DictReader(open(f), delimiter='\t', quoting=csv.QUOTE_NONE))
        bad = check(rows)
        n = sum(1 for r in rows if r.get('quote', '').strip() not in ('', '-'))
        tot += n; nb += len(bad)
        print(f'{f}: {n - len(bad)}/{n} quotes found')
        for b in bad: print('  ', *b)
    sys.exit(1 if nb else 0)
