"""Supplementary: every double-quoted fragment of >= 4 words in notes/*.md and REVIEW.md, searched in ALL fetched
sources (~/cd_sources) with the s4 normaliser (exact, then alphanumeric-only). Fragments found nowhere are listed for
manual inspection. Writes s6_quotes.txt."""
import glob
import os
import re

import s4_reverify as M
from common import LIT, OUT, SRC

srcs = {}
for fn in sorted(os.listdir(SRC)):
    raw = open(f"{SRC}/{fn}", encoding="utf-8", errors="replace").read()
    n = M.norm(raw)
    srcs[fn] = (n, re.sub(r"[^a-z0-9]", "", n))


def frags(text):
    t = re.sub(r"\s*\n\s*", " ", M.norm_chars(text))   # quotes may span line breaks
    out = []
    for f in re.findall(r'"([^"]{3,600})"', t):
        for piece in re.split(r"\s*(?:…|\.\.\.)\s*", f):
            piece = piece.strip(" ,;:")
            if len(re.findall(r"[A-Za-z0-9]+", piece)) >= 4:
                out.append(piece)
    return out


def find(f):
    p = M.norm(f)
    a = re.sub(r"[^a-z0-9]", "", p)
    for fn, (n, al) in srcs.items():
        if p in n:
            return "exact", fn
    for fn, (n, al) in srcs.items():
        if len(a) >= 12 and a in al:
            return "alnum", fn
    return "notfound", None


if __name__ == "__main__":
    lines = []
    for label, files in [("notes", sorted(glob.glob(f"{LIT}/notes/*.md"))), ("REVIEW.md", [f"{LIT}/REVIEW.md"])]:
        tot = found = 0
        miss = []
        for f in files:
            t = open(f, encoding="utf-8").read()
            for q in frags(t):
                tot += 1
                lvl, fn = find(q)
                if lvl != "notfound":
                    found += 1
                else:
                    miss.append((os.path.basename(f), q[:160]))
        lines.append(f"{label}: quoted fragments (>= 4 words) {tot}; found in a fetched source {found}; not found {len(miss)}")
        for m in miss:
            lines.append(f"    NOT FOUND [{m[0]}] {m[1]}")
    open(f"{OUT}/s6_quotes.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
