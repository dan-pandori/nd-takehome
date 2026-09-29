"""Print the context of a regex in a fetched source: python3 lit_review/quote.py 2502.03438 '70\\.83' [width]."""
import os, re, sys
src = os.path.expanduser(f"~/lr_sources/{sys.argv[1]}" + ("" if sys.argv[1].endswith(".txt") else ".txt"))
t = re.sub(r"\s+", " ", open(src).read())
w = int(sys.argv[3]) if len(sys.argv) > 3 else 110
for n, m in enumerate(re.finditer(sys.argv[2], t)):
    if n == 3:
        break
    print(f"[{m.start()}] …{t[max(0, m.start() - w):m.end() + w]}…")
