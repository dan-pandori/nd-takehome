"""Task 1 (notes): match each in-depth note to screened rows; depth column; full text on disk; template bullets;
earlier-review overlap of the note's primary paper(s). Writes s1c_notes.tsv and s1c_notes.txt."""
import glob
import json
import os
import re
from collections import Counter

from common import (LIT, OUT, PRIOR_DIRS, SRC, arxiv_ids, clean_title_cell, dois, norm_title, table_rows,
                    urls)

merged = json.load(open(f"{OUT}/s1_merged_parsed.json"))["merged"]
prior_ids = set()
prior_dois = set()
for d in PRIOR_DIRS:
    for r, _, fs in os.walk(d):
        for f in fs:
            t = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
            prior_ids.update(arxiv_ids(t))
            prior_dois.update(dois(t))
src_files = set(os.listdir(SRC))
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def depth_class(d):
    d = d.lower()
    if d.startswith("full"):
        return "full"
    if d.startswith("sections") or d.startswith("method") or "sections read" in d:
        return "sections"
    if d.startswith("abstract"):
        return "abstract"
    return "other:" + d[:30]


rows = []
for f in sorted(glob.glob(f"{LIT}/notes/*.md")):
    name = os.path.basename(f)
    t = open(f, encoding="utf-8").read()
    words = len(re.findall(r"\w+", t))
    fm = re.match(r"---\n(.*?)\n---\n", t, re.S)
    papers = re.findall(r"^\s*-\s*(\S+)", fm.group(1), re.M) if fm else []
    head = t.split("## Learnings")[0]
    ids = list(dict.fromkeys(arxiv_ids(head)))
    ds = list(dict.fromkeys(dois(head)))
    us = list(dict.fromkeys(urls(head)))
    # screened rows mentioning this note file by name
    by_name = [r for r in merged if name in r["title_cell"]]
    # screened rows matching the note's ids (only if not already found by name)
    by_id = [r for r in merged if (set(arxiv_ids(r["id"])) & set(ids)) or (set(dois(r["id"])) & set(ds))]
    match = {r["n"]: r for r in by_name + by_id}
    # template sections / bullets
    bullets = {k: bool(re.search(k, t, re.I)) for k in
               [r"definition offered", r"new vs\.? better access", r"null\s*/\s*floor", r"transfer to our setting"]}
    # full text on disk for each arXiv id
    fulltext = {a: any(fn.startswith(a) and fn.endswith(".txt") and not fn.endswith(".abs.txt") for fn in src_files)
                for a in ids}
    prior_hit = sorted((set(ids) & prior_ids) | (set(ds) & prior_dois))
    rows.append(dict(note=name, words=words, papers=papers, ids=ids, dois=ds, urls=us[:2],
                     rows=sorted(match), readers=sorted({match[n]["reader"] for n in match}),
                     depths=[f'{n}:{match[n]["reader"]}:{match[n]["depth"]}' for n in sorted(match)],
                     classes=sorted({depth_class(match[n]["depth"]) for n in match}),
                     bullets=bullets, fulltext=fulltext, prior_hit=prior_hit,
                     named_in_title=[r["n"] for r in by_name]))

say(f"notes: {len(rows)}")
nomatch = [r["note"] for r in rows if not r["rows"]]
say("notes with no screened row:", nomatch)
say("notes not named in any screened title cell:", [r["note"] for r in rows if not r["named_in_title"]])
# rows that name a note file that does not exist
note_names = {r["note"] for r in rows}
named = set()
for r in merged:
    for m in re.findall(r"`([a-z0-9_]+\.md)`", r["title_cell"]):
        named.add(m)
        if m not in note_names:
            say("screened row names a missing note:", r["n"], m)
say("note files named in screened.md:", len(named))
# depth classification: a note is an in-depth read if at least one matching row says sections/full
cls = Counter()
for r in rows:
    best = "full" if "full" in r["classes"] else ("sections" if "sections" in r["classes"] else
                                                   (r["classes"][0] if r["classes"] else "none"))
    r["best"] = best
    cls[best] += 1
say("best depth class over the matching rows (full / sections / abstract):", dict(cls))
say("notes whose ONLY matching row depth is 'abstract':", [r["note"] for r in rows if r["best"] == "abstract"])
say("notes with any matching row at abstract depth (e.g. screened elsewhere at abstract level):")
for r in rows:
    if "abstract" in r["classes"]:
        say("   ", r["note"], r["depths"])
say("notes missing a template bullet:", [(r["note"], [k for k, v in r["bullets"].items() if not v]) for r in rows
                                         if not all(r["bullets"].values())])
say("notes whose arXiv id has only an abstract file on disk:",
    [(r["note"], [a for a, v in r["fulltext"].items() if not v]) for r in rows if not all(r["fulltext"].values())])
say("notes without an arXiv id in the header (non-arXiv sources):", [(r["note"], r["dois"], r["urls"]) for r in rows
                                                                    if not r["ids"]])
say("notes whose header ids hit the earlier reviews:", [(r["note"], r["prior_hit"]) for r in rows if r["prior_hit"]])
say("word counts: min", min(r["words"] for r in rows), "median", sorted(r["words"] for r in rows)[len(rows) // 2],
    "max", max(r["words"] for r in rows), "; shortest 5:", sorted((r["words"], r["note"]) for r in rows)[:5])
say("notes per reader (by matching rows):", Counter(",".join(r["readers"]) for r in rows))
# unique papers covered by notes
covered = set()
for r in rows:
    covered.update(r["rows"])
say("screened rows covered by notes:", len(covered))

with open(f"{OUT}/s1c_notes.tsv", "w", encoding="utf-8") as fh:
    fh.write("note\twords\tids\trows\tdepths\tbest\tfulltext_on_disk\tbullets_ok\tprior_hit\n")
    for r in rows:
        fh.write("\t".join([r["note"], str(r["words"]), ",".join(r["ids"] or r["dois"] or r["urls"]),
                            ",".join(map(str, r["rows"])), " || ".join(r["depths"]), r["best"],
                            str(all(r["fulltext"].values()) if r["fulltext"] else "n/a (non-arXiv)"),
                            str(all(r["bullets"].values())), ",".join(r["prior_hit"])]) + "\n")
open(f"{OUT}/s1c_notes.txt", "w").write("\n".join(lines) + "\n")
