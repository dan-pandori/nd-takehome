"""Print context around a pattern in a hand-check item (reviewer confirmation helper).
Usage: rv_hand_ctx.py <item> <regex> [chars=600] [max_hits=3]"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
item, pat = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 600; mx = int(sys.argv[4]) if len(sys.argv) > 4 else 3
t = open(os.path.join(HERE, "hand", "items", f"{item}.md")).read()
t = t.split("## Response", 1)[1]
hits = [m.start() for m in re.finditer(pat, t)]
print(f"[{item}] {len(hits)} hits for /{pat}/ in {len(t)} chars; showing {min(mx, len(hits))}")
for h in hits[:mx]:
    print(f"--- @{h} ({100 * h / len(t):.0f}%)")
    print(t[max(0, h - w // 3): h + w])
