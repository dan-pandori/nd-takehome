#!/usr/bin/env python3
"""Check every ledger quote against its fetched source text (run rl-compute-share).

usage: verify_ledger.py [ledger.tsv ...]   (default: rl_compute_share/ledger/*.tsv)
A quote passes if, after NFKC normalisation, whitespace collapsing and removal of PDF line-break
hyphenation, it is a substring of the source file named in its row (files live in ~/rcs_sources/).
Prints one line per failing row and a per-file tally; exit status 1 if any row fails."""
import sys, os, re, glob, csv, unicodedata
SRC = os.path.expanduser('~/rcs_sources')
COLS = ['claim_id', 'source_id', 'source_file', 'location', 'grade', 'field', 'value', 'quote']

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('­', '').replace('‐', '-').replace('‑', '-').replace('−', '-')
    s = re.sub(r'[‘’‛]', "'", s)
    s = re.sub(r'[“”‟]', '"', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

_cache = {}
def text(f):
    if f not in _cache:
        t = norm(open(os.path.join(SRC, f), errors='replace').read())
        _cache[f] = (t, t.replace('- ', ''), t.replace(' ', ''))
    return _cache[f]

def main(paths):
    bad = 0; total = 0
    for p in paths:
        ok = n = 0
        with open(p, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
        if not rows or rows[0] != COLS:
            print(f'{p}: header must be {COLS}'); bad += 1; continue
        for i, r in enumerate(rows[1:], start=2):
            if not r or not ''.join(r).strip():
                continue
            n += 1
            if len(r) != len(COLS):
                print(f'{p}:{i}: {len(r)} columns'); continue
            d = dict(zip(COLS, r))
            q = norm(d['quote'])
            if not q:
                print(f'{p}:{i}: {d["claim_id"]}: empty quote'); continue
            try:
                t, t2, t3 = text(d['source_file'])
            except FileNotFoundError:
                print(f'{p}:{i}: {d["claim_id"]}: missing source file {d["source_file"]}'); continue
            if q in t or q.replace('- ', '') in t2 or q.replace(' ', '') in t3:
                ok += 1
            else:
                print(f'{p}:{i}: {d["claim_id"]}: QUOTE NOT FOUND in {d["source_file"]}: {q[:100]}')
        print(f'{os.path.basename(p)}: {ok} / {n} quotes found')
        bad += n - ok; total += n
    print(f'TOTAL {total - bad} / {total}')
    return 1 if bad else 0

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    sys.exit(main(sys.argv[1:] or sorted(glob.glob(os.path.join(here, 'ledger', '*.tsv')))))
