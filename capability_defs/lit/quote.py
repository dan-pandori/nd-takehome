"""Verify a quoted claim against a fetched source text and report where it is (run capability-defs).

    python3 capability_defs/lit/quote.py 2504.13837v5 "base models achieve higher pass@k"
    python3 capability_defs/lit/quote.py harding2024-capability "a capability is" --context 300

Matching ignores case, whitespace runs, hyphenation at line breaks and ligatures. Prints each hit
with the nearest preceding [[page N]] marker and section-like heading, or NOT FOUND (exit 1).
"""
import os
import re
import sys

SRC = os.path.expanduser("~/cd_sources")
LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
       "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
       "−": "-"}


def norm(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = re.sub(r"-\s*\n\s*", "", s)          # de-hyphenate line breaks
    s = s.replace("$", "").replace("{", "").replace("}", "")  # HTML math alttext
    return re.sub(r"\s+", " ", s).lower()


def main():
    key, phrase = sys.argv[1], sys.argv[2]
    ctx = int(sys.argv[sys.argv.index("--context") + 1]) if "--context" in sys.argv else 160
    path = f"{SRC}/{key}.txt"
    if not os.path.exists(path):
        path = f"{SRC}/{key}.abs.txt"
    raw = open(path).read()
    # map normalised offsets back to raw lines roughly via a normalised copy per line
    lines = raw.split("\n")
    flat, starts = [], []
    pos = 0
    for ln in lines:
        n = norm(ln) + " "
        starts.append(pos)
        flat.append(n)
        pos += len(n)
    text = "".join(flat)
    text_nh = re.sub(r"- ", "", text)  # tolerate hyphenation split across our joined lines
    p = norm(phrase).strip()
    hits = [m.start() for m in re.finditer(re.escape(p), text)]
    used = text
    if not hits:
        hits = [m.start() for m in re.finditer(re.escape(p), text_nh)]
        used = text_nh
    if not hits:  # last resort: ignore all whitespace (math spacing, line-broken words)
        idx = [i for i, c in enumerate(text) if c != " "]
        nows = "".join(text[i] for i in idx)
        pn = re.sub(r" ", "", p)
        m = nows.find(pn)
        if m >= 0:
            h = idx[m]
            li = max(i for i, s in enumerate(starts) if s <= h)
            page = next((re.match(r"\[\[page (\d+)\]\]", lines[j].strip()).group(1) for j in range(li, -1, -1)
                         if re.match(r"\[\[page (\d+)\]\]", lines[j].strip())), "?")
            print(f"FOUND (whitespace-insensitive) {os.path.basename(path)} page {page} line {li}: "
                  f"...{text[max(0, h - ctx // 2):h + len(p) + ctx // 2]}...")
            sys.exit(0)
    if not hits:
        print(f"NOT FOUND in {os.path.basename(path)}: {phrase!r}")
        sys.exit(1)
    for h in hits[:5]:
        # nearest line index
        li = max(i for i, s in enumerate(starts) if s <= h) if used is text else None
        page, head = "?", "?"
        if li is not None:
            for j in range(li, -1, -1):
                m = re.match(r"\[\[page (\d+)\]\]", lines[j].strip())
                if m and page == "?":
                    page = m.group(1)
                s = lines[j].strip()
                if head == "?" and re.match(r"^(\d+(\.\d+)*\.?|[A-H](\.\d+)*\.?|Appendix [A-Z]|Section \d+)\s+[A-Z]", s) and len(s) < 120:
                    head = s
                if page != "?" and head != "?":
                    break
        print(f"FOUND {os.path.basename(path)} page {page} section '{head}' line {li if li is not None else '?'}: "
              f"...{used[max(0, h - ctx // 2):h + len(p) + ctx // 2]}...")
    if len(hits) > 5:
        print(f"({len(hits)} hits; first 5 shown)")


if __name__ == "__main__":
    main()
