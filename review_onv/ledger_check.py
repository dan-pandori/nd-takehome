#!/usr/bin/env python3
"""Reviewer re-verification of every olmo-novelty ledger quote against its source text, own normaliser.

    python3 review_onv/ledger_check.py --root ~/review/olmo-novelty --src ~/onv_sources [--out review_onv/ledger_out.tsv]

Per row: quote words (<= 25?), found under (1) whitespace/case/unicode normalisation with line-break hyphenation
joined, (2) only after deleting every non-alphanumeric character ("alnum" fallback, e.g. pdftotext column or
superscript debris), or not found. Negative controls per row: (a) one content token altered (a digit bumped, else
the longest word replaced) must not be found; (b) the quote looked up in a different, randomly chosen source file
must not be found. Also: source_file exists, source_id consistent with the file name, and the arXiv id printed in the
source text (identity check), reported per source file.
"""
import argparse
import csv
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹣－"), "-")
QUOTES = {ord("‘"): "'", ord("’"): "'", ord("‚"): "'", ord("‛"): "'", ord("′"): "'",
          ord("“"): '"', ord("”"): '"', ord("„"): '"', ord("″"): '"', ord("«"): '"',
          ord("»"): '"'}


def norm(t):
    t = unicodedata.normalize("NFKC", t)
    t = t.replace("­", "").replace("​", "").replace("﻿", "")
    t = t.translate(DASHES).translate(QUOTES)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)  # line-break hyphenation joined
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()


def norm_keep_hyphen(t):
    t = unicodedata.normalize("NFKC", t)
    t = t.replace("­", "").translate(DASHES).translate(QUOTES)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1-\2", t)  # a real hyphen at a line break
    return re.sub(r"\s+", " ", t).lower().strip()


def alnum(t):
    return re.sub(r"[^0-9a-z]", "", norm(t))


def alter(q, rng):
    digits = [m for m in re.finditer(r"\d", q)]
    if digits:
        m = rng.choice(digits)
        d = str((int(m.group()) + 1) % 10)
        return q[:m.start()] + d + q[m.end():]
    words = re.findall(r"[A-Za-z]{4,}", q)
    if not words:
        return q + " zebra"
    w = max(words, key=len)
    i = q.index(w)
    return q[:i] + "zebrafish" + q[i + len(w):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--src", default="~/onv_sources")
    ap.add_argument("--out", default="review_onv/ledger_out.tsv")
    a = ap.parse_args()
    root, src = Path(a.root).expanduser(), Path(a.src).expanduser()
    rng = random.Random(7)
    cache = {}

    def text(f):
        if f not in cache:
            p = src / f
            raw = p.read_text(errors="replace") if p.exists() else None
            cache[f] = None if raw is None else (raw, norm(raw), norm_keep_hyphen(raw), alnum(raw))
        return cache[f]

    files = sorted(p.name for p in src.iterdir() if p.is_file())
    rows = []
    for led in sorted((root / "olmo_novelty" / "ledger").glob("*.tsv")):
        with open(led, newline="") as fh:
            rd = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
            hdr = next(rd)
            for r in rd:
                if not r or not any(r):
                    continue
                d = dict(zip(hdr, r))
                d["_ledger"] = led.stem
                d["_ncols"] = len(r)
                d["_hdr"] = "\t".join(hdr)
                rows.append(d)
    out = []
    per = defaultdict(Counter)
    ids = Counter(d.get("claim_id", "") for d in rows)
    for d in rows:
        L = d["_ledger"]
        q = d.get("quote", "")
        f = d.get("source_file", "")
        nw = len(q.split())
        t = text(f)
        st = "nofile"
        if t is not None:
            nq, nqh, aq = norm(q), norm_keep_hyphen(q), alnum(q)
            if nq and (nq in t[1] or nqh in t[2] or nq in t[2] or nqh in t[1]):
                st = "found"
            elif aq and aq in t[3]:
                st = "alnum_only"
            else:
                st = "NOT_FOUND"
        # negative controls
        neg_alter = neg_cross = ""
        if t is not None and q:
            qa = alter(q, rng)
            na = alnum(qa)
            neg_alter = "PASSED(bad)" if (norm(qa) in t[1] or (na and na in t[3])) else "failed(ok)"
            w = q.split()
            if len(w) >= 4:
                j = rng.randrange(len(w) - 1)
                while j + 1 < len(w) and w[j] == w[j + 1]:
                    j += 1
                if j + 1 < len(w):
                    w[j], w[j + 1] = w[j + 1], w[j]
                    if norm(" ".join(w)) in t[1]:
                        neg_alter += "+SWAP_PASSED(bad)"
            pid = lambda x: (re.search(r"\d{4}\.\d{4,5}", x) or re.search(r"prorl|nemotron", x.lower()) or [x])[0]
            other = rng.choice([x for x in files if pid(x) != pid(f) and not x.endswith(".json")])
            to = text(other)
            neg_cross = "PASSED" if (to and alnum(q) and alnum(q) in to[3]) else "failed(ok)"
        # source_id vs file name
        sid = d.get("source_id", "")
        idok = (sid.split("v")[0] in f) if re.match(r"\d{4}\.\d{4,5}", sid) else None
        per[L]["rows"] += 1
        per[L][st] += 1
        per[L]["gt25w"] += nw > 25
        per[L]["neg_alter_passed"] += neg_alter.startswith("PASSED")
        per[L]["neg_swap_passed"] += "SWAP_PASSED" in neg_alter
        per[L]["neg_cross_passed"] += neg_cross == "PASSED"
        per[L]["badcols"] += d["_ncols"] != 7
        per[L]["dup_id"] += ids[d.get("claim_id", "")] > 1
        per[L]["sid_mismatch"] += idok is False
        out.append([L, d.get("claim_id", ""), sid, f, str(nw), st, neg_alter, neg_cross,
                    "" if idok is None else str(idok)])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as fh:
        fh.write("ledger\tclaim_id\tsource_id\tsource_file\twords\tstatus\tneg_alter\tneg_cross\tsid_in_file\n")
        for o in out:
            fh.write("\t".join(o) + "\n")
    tot = Counter()
    for L in sorted(per):
        print(L, dict(per[L]))
        tot.update(per[L])
    print("TOTAL", dict(tot))
    print("headers:", Counter(d["_hdr"] for d in rows).most_common())
    bad = [o for o in out if o[5] != "found"]
    for o in bad:
        print("  not exact:", o)
    # identity: does each used source file print its own arXiv id?
    print("--- identity of used source files (arXiv id printed in text?)")
    for f in sorted({d["source_file"] for d in rows}):
        t = text(f)
        m = re.match(r"(?:[A-Z]{2}_)?(\d{4}\.\d{4,5})", f)
        if t is None:
            print("  MISSING", f)
            continue
        if m:
            aid = m.group(1)
            hit = aid in t[0]
            print(f"  {f}: id {aid} in text: {hit}; first line: {t[0].strip().splitlines()[0][:90] if t[0].strip() else ''}")
        else:
            print(f"  {f}: (non-arXiv) first line: {t[0].strip().splitlines()[0][:110] if t[0].strip() else ''}")


if __name__ == "__main__":
    main()
