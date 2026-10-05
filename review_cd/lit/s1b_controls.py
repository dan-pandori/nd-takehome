"""Task 1 controls: (a) positive control for the overlap matcher (the earlier reviews' own papers must be
detected); (b) arXiv ids mentioned in the earlier reviews but absent from _prior_screened.tsv; (c) a looser
first-author + year co-occurrence scan of the earlier reviews for the 185 unique papers (candidates for manual
inspection only)."""
import difflib
import os
import re
from collections import defaultdict

from common import LIT, OUT, PRIOR_DIRS, arxiv_ids, clean_title_cell, dois, norm_title, table_rows

prior_files = [os.path.join(r, f) for d in PRIOR_DIRS for r, _, fs in os.walk(d) for f in fs]
raw = {f: open(f, encoding="utf-8", errors="replace").read() for f in prior_files}
ntext = {f: norm_title(t) for f, t in raw.items()}
prior_arx = defaultdict(set)
for f, t in raw.items():
    for a in arxiv_ids(t):
        prior_arx[a].add(f)
tsv = [l.rstrip("\n").split("\t") for l in open(f"{LIT}/_prior_screened.tsv", encoding="utf-8") if l.strip()]
tsv_ids = set(a for r in tsv for a in arxiv_ids(r[1]))
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


# (b)
extra = sorted(set(prior_arx) - tsv_ids)
say("(b) arXiv ids in earlier-review files but not in _prior_screened.tsv:", extra)
for a in extra:
    for f in sorted(prior_arx[a]):
        for i, ln in enumerate(raw[f].split("\n"), 1):
            if a in ln:
                say("    ", os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])), i, ln.strip()[:220])

# (a) positive control: treat each TSV row as if it were a 'new' screened row and run the same matching
det_id = det_title = 0
miss = []
for r in tsv:
    ids = arxiv_ids(r[1])
    hit_id = any(a in prior_arx for a in ids) or any(
        d in "".join(raw.values()).lower() for d in dois(r[1]))
    t = norm_title(clean_title_cell(r[2]))
    hit_t = len(t.split()) >= 3 and any(f" {t} " in f" {x} " for x in ntext.values())
    det_id += hit_id
    det_title += hit_t
    if not (hit_id or hit_t):
        miss.append(r)
say(f"(a) positive control on the {len(tsv)} prior papers: detected by id/DOI {det_id}, by title substring "
    f"{det_title}, missed by both {len(miss)}", miss)

# (c) first-author + year co-occurrence (within 80 characters) in the earlier reviews' raw text
merged = [c for _, c in table_rows(f"{LIT}/screened.md") if re.fullmatch(r"\d+", c[0])]
seen = set()
cands = []
for c in merged:
    if c[10].startswith("dup"):
        continue
    m = re.search(r"\(([^()]*)\)\s*(?:[—–].*)?$", c[2].split(" — ")[0])
    author = None
    m2 = re.findall(r"\(([^()]+)\)", c[2].split(" — ")[0])
    if m2:
        author = m2[-1].split(";")[0].split(",")[0].strip()
    year = re.search(r"(19|20)\d\d", c[3])
    if not author or not year or len(author) < 3:
        continue
    pat = re.compile(re.escape(author) + r".{0,80}?" + year.group(0) + "|" + year.group(0) + r".{0,40}?" +
                     re.escape(author), re.S)
    for f, t in raw.items():
        for m in pat.finditer(t):
            cands.append((c[0], c[1], author, year.group(0), c[4], os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])),
                          t[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")))
say(f"(c) author+year co-occurrence candidates: {len(cands)}")
for x in cands:
    say("    ", x)
open(f"{OUT}/s1b_controls.txt", "w").write("\n".join(lines) + "\n")
