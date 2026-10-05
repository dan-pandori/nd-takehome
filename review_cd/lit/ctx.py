"""Print raw-source context around a literal or regex (read-only helper): python3 ctx.py <file> <regex> [width]"""
import os, re, sys
t = open(os.path.expanduser("~/cd_sources/" + sys.argv[1]), encoding="utf-8", errors="replace").read()
w = int(sys.argv[3]) if len(sys.argv) > 3 else 200
for k, m in enumerate(re.finditer(sys.argv[2], t)):
    if k >= 4: break
    line = t.count("\n", 0, m.start()) + 1
    print(f"line {line}: ...{t[max(0, m.start()-w):m.end()+w]}...".replace("\n", " "))
    print("---")
