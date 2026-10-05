"""Task 1: unique screened papers, new vs the two earlier reviews, in-depth notes.

Writes s1_screened_rows.tsv, s1_overlaps.tsv, s1_notes.tsv, s1_summary.txt in the output folder.
"""
import difflib
import glob
import json
import os
import re
from collections import Counter, defaultdict

from common import (LIT, OUT, PRIOR_DIRS, SRC, arxiv_ids, clean_title_cell, dois, norm_title,
                    table_rows, urls)

out_lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out_lines.append(s)


# ---------------------------------------------------------------- merged table
merged = []
for ln, c in table_rows(f"{LIT}/screened.md"):
    if not re.fullmatch(r"\d+", c[0]):
        continue
    assert len(c) == 11, (ln, len(c), c[:3])
    merged.append(dict(line=ln, n=int(c[0]), reader=c[1], title_cell=c[2], year=c[3], id=c[4],
                       thread=c[5], defn=c[6], rel=c[7], depth=c[8], claims=c[9], status=c[10]))
say(f"screened.md: {len(merged)} numbered rows; numbering 1..{max(r['n'] for r in merged)}; "
    f"distinct numbers {len(set(r['n'] for r in merged))}")
say("  rows per reader:", dict(sorted(Counter(r['reader'] for r in merged).items())))
say("  status values:", dict(Counter(r['status'] for r in merged)))

# ---------------------------------------------------------------- per-reader tables
per_reader = []
for f in sorted(glob.glob(f"{LIT}/_screen_L*.md")):
    tag = re.search(r"_screen_(L\d)\.md", f).group(1)
    for ln, c in table_rows(f):
        if c[0].lower().startswith("title"):
            continue
        assert len(c) == 8, (f, ln, len(c))
        per_reader.append(dict(reader=tag, line=ln, title_cell=c[0], year=c[1], id=c[2], depth=c[6],
                               claims=c[7]))
say(f"per-reader tables: {len(per_reader)} rows;",
    dict(sorted(Counter(r['reader'] for r in per_reader).items())))


def keys_of(row):
    k = set()
    idc = row["id"]
    for a in arxiv_ids(idc):
        k.add("arxiv:" + a)
    for d in dois(idc):
        k.add("doi:" + d)
    if not k:
        for u in urls(idc):
            k.add("url:" + u)
    if not k:
        k.add("idcell:" + norm_title(idc))
    t = norm_title(clean_title_cell(row["title_cell"]))
    k.add("title:" + t)
    return k


# check merged vs per-reader correspondence (by reader + first key)
def primary(row):
    a = arxiv_ids(row["id"])
    if a:
        return "arxiv:" + a[0]
    d = dois(row["id"])
    if d:
        return "doi:" + d[0]
    u = urls(row["id"])
    if u:
        return "url:" + u[0]
    return "idcell:" + norm_title(row["id"])


m_set = Counter((r["reader"], primary(r)) for r in merged)
p_set = Counter((r["reader"], primary(r)) for r in per_reader)
say("merged rows not in per-reader tables:", sorted(set(m_set) - set(p_set)))
say("per-reader rows not in merged table:", sorted(set(p_set) - set(m_set)))
# depth / claims consistency between per-reader and merged rows
pr_idx = {(r["reader"], primary(r)): r for r in per_reader}
dd = []
for r in merged:
    p = pr_idx.get((r["reader"], primary(r)))
    if p and (p["depth"] != r["depth"] or p["claims"].replace(" ", "") != r["claims"].replace(" ", "")):
        dd.append((r["n"], r["reader"], r["id"], "merged:", r["depth"], r["claims"], "| reader:", p["depth"],
                   p["claims"]))
say(f"merged rows whose depth/claims differ from the reader's table: {len(dd)}")
for x in dd:
    say("   ", *x)

# ---------------------------------------------------------------- dedupe (union-find on shared keys)
parent = list(range(len(merged)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


key_owner = {}
for i, r in enumerate(merged):
    r["keys"] = keys_of(r)
    for k in r["keys"]:
        if k in key_owner:
            parent[find(i)] = find(key_owner[k])
        else:
            key_owner[k] = i
# fuzzy title merge (ratio >= 0.9) as a second pass, reported separately
titles = [norm_title(clean_title_cell(r["title_cell"])) for r in merged]
fuzzy_pairs = []
for i in range(len(merged)):
    for j in range(i + 1, len(merged)):
        if find(i) == find(j):
            continue
        rt = difflib.SequenceMatcher(None, titles[i], titles[j]).ratio()
        if rt >= 0.85:
            fuzzy_pairs.append((merged[i]["n"], merged[j]["n"], round(rt, 3), titles[i], titles[j]))
groups = defaultdict(list)
for i in range(len(merged)):
    groups[find(i)].append(i)
say(f"unique papers by exact keys (arXiv id w/o version, DOI, URL, normalised title): {len(groups)}")
say("fuzzy title pairs (ratio>=0.85) not merged by keys:", fuzzy_pairs if fuzzy_pairs else "none")
dups = [g for g in groups.values() if len(g) > 1]
say(f"duplicate groups: {len(dups)} (extra rows: {sum(len(g) - 1 for g in dups)})")
for g in dups:
    say("   ", [(merged[i]["n"], merged[i]["reader"], merged[i]["id"], merged[i]["status"], merged[i]["depth"][:40])
               for i in g])
# do the file's dup markings match?
marked_dup = {r["n"] for r in merged if r["status"].lower().startswith("dup")}
my_dup = {merged[i]["n"] for g in dups for i in sorted(g, key=lambda i: merged[i]["n"])[1:]}
say("rows marked dup in the file:", sorted(marked_dup))
say("rows I find to be later duplicates:", sorted(my_dup))

# ---------------------------------------------------------------- earlier reviews
prior_files = []
for d in PRIOR_DIRS:
    for root, _, files in os.walk(d):
        for fn in files:
            prior_files.append(os.path.join(root, fn))
say(f"earlier-review files scanned: {len(prior_files)}")
prior_arx = defaultdict(set)
prior_doi = defaultdict(set)
prior_url = defaultdict(set)
prior_text = {}
for f in prior_files:
    t = open(f, encoding="utf-8", errors="replace").read()
    prior_text[f] = norm_title(t)
    for a in arxiv_ids(t):
        prior_arx[a].add(os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])))
    for d in dois(t):
        prior_doi[d].add(os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])))
    for u in urls(t):
        prior_url[u].add(os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])))
say(f"distinct arXiv ids mentioned anywhere in the earlier reviews: {len(prior_arx)}; DOIs: {len(prior_doi)}")

# prior screened titles (tables of the earlier reviews) for fuzzy title matching
prior_titles = []
for f in prior_files:
    if not f.endswith(".md"):
        continue
    for ln, c in table_rows(f):
        if len(c) >= 4 and re.fullmatch(r"\d+", c[0] or "x") and len(c[1]) > 8:
            prior_titles.append((os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0])), ln,
                                 norm_title(clean_title_cell(c[1]))))
say(f"title cells read from numbered rows of earlier-review tables: {len(prior_titles)}")

# the run's own prior list
tsv = [l.rstrip("\n").split("\t") for l in open(f"{LIT}/_prior_screened.tsv", encoding="utf-8") if l.strip()]
tsv_ids = set(a for r in tsv for a in arxiv_ids(r[1]))
tsv_dois = set(d for r in tsv for d in dois("\t".join(r)))
say(f"_prior_screened.tsv: {len(tsv)} rows, {len(tsv_ids)} arXiv ids, {len(tsv_dois)} DOIs; non-arXiv rows:",
    [r for r in tsv if not arxiv_ids(r[1])])

# ---------------------------------------------------------------- match each unique paper
rows_out = []
overlaps = []
for gi, (root, g) in enumerate(sorted(groups.items(), key=lambda kv: min(merged[i]["n"] for i in kv[1]))):
    ks = set().union(*(merged[i]["keys"] for i in g))
    hits = []
    for k in ks:
        typ, val = k.split(":", 1)
        if typ == "arxiv" and val in prior_arx:
            hits.append(("arXiv id", val, sorted(prior_arx[val]), "in _prior_screened.tsv" if val in tsv_ids
                         else "NOT in _prior_screened.tsv"))
        if typ == "doi" and val in prior_doi:
            hits.append(("DOI", val, sorted(prior_doi[val]), ""))
        if typ == "url" and val in prior_url:
            hits.append(("URL", val, sorted(prior_url[val]), ""))
        if typ == "title" and len(val.split()) >= 3:
            for f, t in prior_text.items():
                if f" {val} " in f" {t} ":
                    hits.append(("title substring", val, [os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0]))], ""))
            pre = val.split(" ")
            # pre-colon part of the raw title
            raw = clean_title_cell(merged[g[0]]["title_cell"])
            if ":" in raw:
                head = norm_title(raw.split(":")[0])
                if len(head.split()) >= 4:
                    for f, t in prior_text.items():
                        if f" {head} " in f" {t} ":
                            hits.append(("pre-colon title substring", head,
                                         [os.path.relpath(f, os.path.dirname(PRIOR_DIRS[0]))], ""))
            for (pf, pl, pt) in prior_titles:
                if pt and difflib.SequenceMatcher(None, val, pt).ratio() >= 0.8:
                    hits.append(("fuzzy title vs earlier table", f"{val} ~ {pt}", [f"{pf}:{pl}"], ""))
    first = merged[min(g, key=lambda i: merged[i]["n"])]
    rows_out.append(dict(uid=gi + 1, rows=",".join(str(merged[i]["n"]) for i in sorted(g)),
                         readers=",".join(merged[i]["reader"] for i in sorted(g)), id=first["id"],
                         title=clean_title_cell(first["title_cell"]),
                         depths=" || ".join(merged[i]["depth"] for i in sorted(g)),
                         status=" || ".join(merged[i]["status"] for i in sorted(g)),
                         prior_hits=json.dumps(hits, ensure_ascii=False)))
    if hits:
        overlaps.append((gi + 1, first["n"], first["reader"], first["id"], clean_title_cell(first["title_cell"]), hits))

say(f"unique papers: {len(rows_out)}; with any hit in the earlier-review directories: {len(overlaps)}")
for o in overlaps:
    say("  OVERLAP", o[0], "row", o[1], o[2], o[3], "|", o[4])
    for h in o[5]:
        say("        ", h)

with open(f"{OUT}/s1_screened_rows.tsv", "w", encoding="utf-8") as fh:
    cols = ["uid", "rows", "readers", "id", "title", "depths", "status", "prior_hits"]
    fh.write("\t".join(cols) + "\n")
    for r in rows_out:
        fh.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")

# ---------------------------------------------------------------- consistency: TSV vs earlier-review tables
# Are all arXiv ids from the earlier reviews' screened tables in _prior_screened.tsv?
table_ids = set()
for f in prior_files:
    if not f.endswith(".md"):
        continue
    for ln, c in table_rows(f):
        if len(c) >= 4 and re.fullmatch(r"\d+", c[0] or "x"):
            for cell in c[1:5]:
                table_ids.update(arxiv_ids(cell))
say(f"arXiv ids in numbered rows of earlier-review tables: {len(table_ids)}; not in _prior_screened.tsv: "
    f"{sorted(table_ids - tsv_ids)}")
say(f"_prior_screened.tsv ids not found in any earlier-review file: {sorted(tsv_ids - set(prior_arx))}")

json.dump(dict(merged=[{k: v for k, v in r.items() if k != 'keys'} for r in merged]),
          open(f"{OUT}/s1_merged_parsed.json", "w"), ensure_ascii=False, indent=0)
open(f"{OUT}/s1_summary.txt", "w").write("\n".join(out_lines) + "\n")
