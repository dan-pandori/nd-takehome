"""For (file, line) pairs print the nearest [[page N]] marker and the nearest looser heading-like lines (read-only)."""
import os, re, sys
SRC = os.path.expanduser("~/cd_sources")
H = re.compile(r"^\s*(\(\d+(\.\d+)*\)\s+\S|\\(sub)*section\*?\{|\d+(\.\d+)*\.?\s*$|\d+(\.\d+)*\.?\s+[A-Z]|[A-H](\.\d+)*\.?\s*$|Appendix|ABSTRACT|Abstract)")
for arg in sys.argv[1:]:
    fn, li = arg.rsplit(":", 1); li = int(li)
    L = open(f"{SRC}/{fn}", encoding="utf-8", errors="replace").read().split("\n")
    page = next((m.group(1) for j in range(li - 1, -1, -1) for m in [re.match(r"\s*\[\[page (\d+)\]\]", L[j])] if m), None)
    heads = []
    for j in range(li - 1, -1, -1):
        s = L[j].strip()
        if s and len(s) < 120 and H.match(s):
            nxt = L[j + 1].strip() if j + 1 < len(L) else ""
            if not nxt and j + 2 < len(L): nxt = L[j + 2].strip()
            heads.append(f"L{j+1}:{s[:60]}{' / ' + nxt[:50] if re.fullmatch(r'[\dA-H.]+', s) else ''}")
            if len(heads) >= 2: break
    print(f"{fn}:{li} page={page} heads={heads}")
