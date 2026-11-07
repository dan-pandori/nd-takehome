#!/usr/bin/env python3
"""Check every ledger quote against its fetched source text (run olmo-novelty; adapted from rl-compute-share).

usage: verify_ledger.py [--neg] [ledger.tsv ...]   (default: olmo_novelty/ledger/*.tsv)
A quote passes if, after NFKC normalisation, quote/dash folding, whitespace collapsing and removal of PDF line-break
hyphenation, it is a substring of the source file named in its row. Source texts live in ~/onv_sources/ (copyrighted:
never committed or uploaded). Also flags quotes over 25 words. --neg runs negative controls: every quote with one
word swapped for a nonsense token must fail; prints how many (wrongly) still pass.
Exit status 1 if any row fails."""
import sys, os, re, glob, csv, unicodedata
SRC = os.path.expanduser('~/onv_sources')
COLS = ['claim_id', 'source_id', 'source_file', 'location', 'quote', 'supports', 'used_for']

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('­', '').replace('‐', '-').replace('‑', '-').replace('−', '-')
    s = s.replace('–', '-').replace('—', '-')
    s = re.sub(r'[‘’‛`]', "'", s)
    s = re.sub(r'[“”‟]', '"', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

_cache = {}
def text(f):
    if f not in _cache:
        t = norm(open(os.path.join(SRC, f), errors='replace').read())
        _cache[f] = (t, t.replace('- ', ''), t.replace(' ', ''))
    return _cache[f]

def found(q, f):
    t, t2, t3 = text(f)
    return q in t or q.replace('- ', '') in t2 or q.replace(' ', '') in t3

def rows_of(p):
    with open(p, newline='') as fh:
        rows = list(csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
    return rows

def main(argv):
    neg = '--neg' in argv
    paths = [a for a in argv if a != '--neg']
    if not paths:
        here = os.path.dirname(os.path.abspath(__file__))
        paths = sorted(glob.glob(os.path.join(here, 'ledger', '*.tsv')))
    bad = total = long_ = neg_pass = neg_n = 0
    for p in paths:
        ok = n = 0
        rows = rows_of(p)
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
            if len(q.split()) > 25:
                long_ += 1; print(f'{p}:{i}: {d["claim_id"]}: quote has {len(q.split())} words (> 25)')
            try:
                hit = found(q, d['source_file'])
            except FileNotFoundError:
                print(f'{p}:{i}: {d["claim_id"]}: missing source file {d["source_file"]}'); continue
            if hit:
                ok += 1
            else:
                print(f'{p}:{i}: {d["claim_id"]}: QUOTE NOT FOUND in {d["source_file"]}: {q[:100]}')
            if neg:
                w = q.split()
                if len(w) >= 4:
                    j = len(w) // 2
                    w[j] = 'zqxjv' + w[j]
                    neg_n += 1
                    if found(' '.join(w), d['source_file']):
                        neg_pass += 1; print(f'{p}:{i}: NEGATIVE CONTROL PASSED (bad): {d["claim_id"]}')
        print(f'{os.path.basename(p)}: {ok} / {n} quotes found')
        bad += n - ok; total += n
    print(f'TOTAL {total - bad} / {total} found; {long_} over 25 words')
    if neg:
        print(f'NEGATIVE CONTROLS: {neg_pass} / {neg_n} altered quotes wrongly found (must be 0)')
    return 1 if (bad or (neg and neg_pass)) else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
