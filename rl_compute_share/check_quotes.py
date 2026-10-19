#!/usr/bin/env python3
"""Check that every quotation (>= 20 characters, in straight or curly double quotes) in the notes and REVIEW.md
occurs verbatim (after the verifier's normalisation) in some fetched source text under ~/rcs_sources/ or in a file of
this repository it names (run rl-compute-share). Prints misses; exit 1 if any."""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_ledger import norm
SRC = os.path.expanduser('~/rcs_sources')
texts = []
for p in glob.glob(os.path.join(SRC, '*.txt')) + glob.glob(os.path.expanduser('~/nd-rl/experiment-summaries/*/README.md')):
    t = norm(open(p, errors='replace').read())
    texts.append((t, t.replace('- ', ''), t.replace(' ', '')))
files = sys.argv[1:] or sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes', '*.md'))) + \
    [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'REVIEW.md')]
bad = n = 0
for f in files:
    s = open(f).read()
    quotes = []
    for para in re.split(r'\n\s*\n', s):
        para = para.replace('\n', ' ')
        para = re.sub(r'`[^`]*`', ' ', para)                  # code spans are not quotations
        segs = para.split('"')
        quotes += [segs[i] for i in range(1, len(segs), 2)]   # straight quotes pair in order within a paragraph
        quotes += re.findall('\u201c([^\u201c\u201d]+)\u201d', para)
    for raw in quotes:
        q = norm(raw).strip(' .,;:')
        q = re.sub(r'\s*\[[^\]]*\]\s*$', '', q)
        if len(q) < 20:
            continue
        n += 1
        parts = [x.strip(' .,;:') for x in re.split(r'\s*(?:\u2026|\.\.\.)\s*', q) if len(x.strip()) >= 8]
        ok = all(any(p in t or p.replace('- ', '') in t2 or p.replace(' ', '') in t3 for t, t2, t3 in texts) for p in parts)
        if not ok:
            bad += 1
            print(f'{os.path.basename(f)}: NOT FOUND: {q[:140]}')
print(f'{n - bad} / {n} quotations found')
sys.exit(1 if bad else 0)
