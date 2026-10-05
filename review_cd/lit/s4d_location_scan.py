"""Supplementary heuristic: for every V row with quoted fragments found (exact/alnum/fuzzy>=0.85), compare the stated
location (Abstract / Sec. N / App. X) with the nearest preceding numbered or appendix heading at any hit.
Rows whose stated location has none of these forms are 'n/a'. Writes s4d_location.txt."""
import json
import re
from collections import Counter

import s4_reverify as M
from common import OUT

ledger = json.load(open(f"{OUT}/s2_claims.json"))
V = [r for r in ledger if r["cls"] == "V"]
NUM = re.compile(r"^\s*(\d+)(\.\d+)*\.?\s+[A-Z\"'“(]")
APP = re.compile(r"^\s*(?:Appendix\s+)?([A-H])(\.\d+)*[\.:]?\s+[A-Z]")
FIRST_SEC = re.compile(r"^\s*(1\.?\s+Introduction|I\.?\s+INTRODUCTION|Introduction)\s*$", re.I)


def stated(loc):
    secs = set(int(x) for x in re.findall(r"(?:Sec(?:tion)?s?\.?|§)\s*(\d+)", loc))
    # "Sec. 1-5" style ranges
    for a, b in re.findall(r"(?:Sec(?:tion)?s?\.?|§)\s*(\d+)\s*[-–]\s*(\d+)", loc):
        secs.update(range(int(a), int(b) + 1))
    apps = set(re.findall(r"App(?:endix|\.)?\s*([A-H])\b", loc))
    abst = bool(re.search(r"abstract", loc, re.I))
    return secs, apps, abst


def where(S, li):
    """(top-level section number or None, appendix letter or None, before_intro flag)"""
    sec = app = None
    for j in range(li, -1, -1):
        s = S.lines[j].strip()
        if not s or len(s) > 140:
            continue
        m = NUM.match(s)
        if m and sec is None and app is None:
            sec = int(m.group(1))
            break
        m = APP.match(s)
        if m and sec is None and app is None and len(s) < 100 and not s.endswith("."):
            app = m.group(1)
            break
    before_intro = not any(FIRST_SEC.match(S.lines[j].strip()) or (NUM.match(S.lines[j].strip()) and
                                                                    NUM.match(S.lines[j].strip()).group(1) == "1")
                           for j in range(0, li))
    return sec, app, before_intro


srcs = {}
res = Counter()
flags = []
unlocated = []
for r in V:
    secs, apps, abst = stated(r["loc"])
    if not (secs or apps or abst):
        res["n/a (location not Sec./App./Abstract)"] += 1
        continue
    files = M.find_source(r["pid"])
    frs = M.fragments(r["claim"])
    if not files or not frs:
        res["n/a (no quote or no source)"] += 1
        continue
    hits = []
    for f in frs:
        for fn in files:
            if fn not in srcs:
                srcs[fn] = M.Source(fn)
            got = srcs[fn].search(f)
            ok = got[0] in ("exact", "exact(dehyph)", "alnum") or (got[0].startswith("fuzzy") and float(got[0][5:]) >= 0.85)
            if ok:
                for li in got[1][:6]:
                    hits.append((fn, li))
                break
    if not hits:
        res["n/a (fragment not located)"] += 1
        unlocated.append((r["reader"], r["n"], r["pid"][:30], r["loc"][:60], r["claim"][:120]))
        continue
    good = False
    seen = []
    for fn, li in hits:
        if fn.endswith(".abs.txt"):
            w = ("abs-file", None, True)
        else:
            w = where(srcs[fn], li)
        seen.append((fn, li + 1, w))
        if abst and w[2]:
            good = True
        if secs and w[0] in secs:
            good = True
        if apps and w[1] in apps:
            good = True
    if good:
        res["consistent"] += 1
    else:
        res["FLAG"] += 1
        flags.append((r["reader"], r["n"], r["pid"][:30], r["loc"][:60], seen[:4], r["claim"][:120]))
out = [f"V rows: {len(V)}", *[f"  {k}: {v}" for k, v in res.most_common()], "", "flagged rows:"]
for x in flags:
    out.append(f"  {x[0]} #{x[1]} {x[2]} | stated: {x[3]} | hits (file, line, (sec, app, before_intro)): {x[4]} | {x[5]}")
out.append("")
out.append("rows with no fragment located at >= 0.85 (location not checkable automatically):")
for x in unlocated:
    out.append(f"  {x[0]} #{x[1]} {x[2]} | stated: {x[3]} | {x[4]}")
open(f"{OUT}/s4d_location.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
