"""Task 2 (claim ledgers) and Task 3 (executor re-check). Also: depth distribution of the 185 unique papers and
consistency of the screened tables' 'claims V / total' column with the ledgers.
Writes s2_claims.json (parsed ledger rows) and s2_claims.txt."""
import glob
import json
import os
import re
from collections import Counter, defaultdict

from common import LIT, OUT, PRIOR_DIRS, SRC, arxiv_ids, table_rows

lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def status_class(s):
    s2 = s.strip().strip("*").strip()
    if re.match(r"^V\b", s2):
        return "V"
    if s2.upper().startswith("UNVERIFIED"):
        return "UNVERIFIED"
    return "OTHER"


ledger = []
for f in sorted(glob.glob(f"{LIT}/_claims_L*.md")):
    tag = re.search(r"_claims_(L\d)\.md", f).group(1)
    raw_rows = [(ln, c) for ln, c in table_rows(f) if c and re.fullmatch(r"\d+", c[0])]
    nums = [int(c[0]) for _, c in raw_rows]
    odd = [(ln, len(c)) for ln, c in raw_rows if len(c) != 5]
    for ln, c in raw_rows:
        ledger.append(dict(reader=tag, line=ln, n=int(c[0]), pid=c[1], claim=" | ".join(c[2:-2]), loc=c[-2],
                           status=c[-1], cls=status_class(c[-1])))
    say(f"{tag}: {len(raw_rows)} rows; numbering {min(nums)}..{max(nums)}, dup numbers "
        f"{[n for n, k in Counter(nums).items() if k > 1]}, gaps {sorted(set(range(1, max(nums) + 1)) - set(nums))}; "
        f"rows with !=5 cells (pipe inside a claim): {odd}")

say("\nstatus values (raw):", dict(Counter(r["status"] for r in ledger)))
tot = Counter()
for tag in sorted({r["reader"] for r in ledger}):
    c = Counter(r["cls"] for r in ledger if r["reader"] == tag)
    n = sum(c.values())
    tot.update(c)
    say(f"{tag}: n={n}  V={c['V']}  UNVERIFIED={c['UNVERIFIED']}  OTHER={c['OTHER']}  V share={c['V'] / n:.4f}")
n = sum(tot.values())
say(f"ALL: n={n}  V={tot['V']}  UNVERIFIED={tot['UNVERIFIED']}  OTHER={tot['OTHER']}  V share={tot['V'] / n:.4f}")
say("non-V rows:")
for r in ledger:
    if r["cls"] != "V":
        say(f"   {r['reader']} #{r['n']} (line {r['line']}) {r['pid']} | {r['claim'][:150]} | {r['loc']} | {r['status'][:150]}")
# V rows whose claim text itself hedges (e.g. 'not found', 'paraphrase', 'UNVERIFIED' inside the claim)
hedge = [r for r in ledger if r["cls"] == "V" and re.search(r"unverified|not found|paraphrase|not checked|could not",
                                                            r["claim"] + " " + r["status"], re.I)]
say(f"V rows whose claim/status text contains a hedge word (unverified / not found / paraphrase / not checked / "
    f"could not): {len(hedge)}")
for r in hedge:
    say(f"   {r['reader']} #{r['n']} {r['pid']} | {r['claim'][:220]} | {r['loc']} | {r['status'][:80]}")

# ---------------------------------------------------------------- source text availability per ledger paper id
src_files = os.listdir(SRC)


def src_for(pid):
    cands = [pid, re.sub(r"v\d+$", "", pid)]
    for k in cands:
        for ext in (".txt", ".abs.txt"):
            if f"{k}{ext}" in src_files:
                return f"{k}{ext}"
    return None


pids = sorted({r["pid"] for r in ledger})
missing = [p for p in pids if src_for(p) is None]
absonly = [p for p in pids if src_for(p) and src_for(p).endswith(".abs.txt")]
say(f"\ndistinct paper ids in ledgers: {len(pids)}; with no source file in ~/cd_sources: {missing}")
say(f"ids whose only source file is an abstract (.abs.txt): {len(absonly)}")

# ---------------------------------------------------------------- ledger ids vs screened rows and the prior list
merged = json.load(open(f"{OUT}/s1_merged_parsed.json"))["merged"]
scr_ids = set(a for r in merged for a in arxiv_ids(r["id"]))
prior = set()
for d in PRIOR_DIRS:
    for rr, _, fs in os.walk(d):
        for fn in fs:
            prior.update(arxiv_ids(open(os.path.join(rr, fn), encoding="utf-8", errors="replace").read()))
led_ar = defaultdict(int)
for r in ledger:
    for a in arxiv_ids(r["pid"]):
        led_ar[a] += 1
say("ledger arXiv ids not in screened.md:", {a: k for a, k in led_ar.items() if a not in scr_ids})
say("ledger arXiv ids that are earlier-review papers:", {a: k for a, k in led_ar.items() if a in prior})
say("non-arXiv ledger ids:", sorted(p for p in pids if not arxiv_ids(p)))

# ---------------------------------------------------------------- screened 'claims V / total' vs ledgers
per_reader_sum = defaultdict(lambda: [0, 0])
bad = []
for r in merged:
    m = re.match(r"\s*(\d+)\s*/\s*(\d+)", r["claims"])
    if m:
        per_reader_sum[r["reader"]][0] += int(m.group(1))
        per_reader_sum[r["reader"]][1] += int(m.group(2))
    else:
        bad.append((r["n"], r["claims"]))
say("\nsum of screened.md 'claims V / total' per reader (all rows incl. dup rows):",
    {k: tuple(v) for k, v in sorted(per_reader_sum.items())}, "unparsed:", bad)
say("ledger per reader (V / total):", {t: (sum(1 for r in ledger if r['reader'] == t and r['cls'] == 'V'),
                                           sum(1 for r in ledger if r['reader'] == t))
                                       for t in sorted({r['reader'] for r in ledger})})
# per-row check: ledger rows per (reader, arXiv id) vs the row's stated total
cnt = Counter()
for r in ledger:
    a = arxiv_ids(r["pid"])
    if a:
        cnt[(r["reader"], a[0])] += 1
mism = []
for r in merged:
    a = arxiv_ids(r["id"])
    m = re.match(r"\s*(\d+)\s*/\s*(\d+)", r["claims"])
    if a and m and cnt[(r["reader"], a[0])] != int(m.group(2)):
        mism.append((r["n"], r["reader"], a[0], r["claims"], cnt[(r["reader"], a[0])]))
say(f"arXiv rows whose stated claim total differs from the reader's ledger row count: {len(mism)}")
for x in mism:
    say("   row", x[0], x[1], x[2], "stated", x[3], "ledger rows", x[4])

# ---------------------------------------------------------------- depth distribution over unique papers
def depth_class(d):
    d = d.lower()
    for k in ("full", "sections", "abstract", "none"):
        if d.startswith(k):
            return k
    if "sections read" in d:
        return "sections"
    return "other"


uniq = [r for r in merged if not r["status"].startswith("dup")]
say(f"\ndepth class over the {len(uniq)} unique-paper rows (first occurrence):",
    dict(Counter(depth_class(r["depth"]) for r in uniq)))
# best depth per unique paper (taking dup rows into account)
best = {}
order = {"full": 3, "sections": 2, "abstract": 1, "none": 0, "other": -1}
for r in merged:
    k = (arxiv_ids(r["id"]) or [r["id"]])[0]
    c = depth_class(r["depth"])
    if k not in best or order[c] > order[best[k]]:
        best[k] = c
say("best depth class per unique paper (dup rows merged):", dict(Counter(best.values())))
say("rows with depth other than abstract/sections/full:", [(r["n"], r["reader"], r["id"], r["depth"]) for r in merged
                                                          if depth_class(r["depth"]) in ("none", "other")])

# ---------------------------------------------------------------- note papers: claims located beyond the abstract
notes_tsv = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s1c_notes.tsv")][1:]
say("\nper-note ledger claims (all readers) and how many are located outside the abstract:")
few = []
for row in notes_tsv:
    ids = [i for i in row[2].split(",") if re.fullmatch(r"\d{4}\.\d{4,5}", i)]
    if not ids:
        continue
    main = ids[0]
    rs = [r for r in ledger if arxiv_ids(r["pid"])[:1] == [main]]
    non_abs = [r for r in rs if not re.fullmatch(r"\s*abstract\.?\s*", r["loc"], re.I)]
    if len(non_abs) < 5:
        few.append((row[0], main, len(rs), len(non_abs)))
say("notes (arXiv) whose paper has < 5 ledger claims located outside the abstract:", few if few else "none")
json.dump(ledger, open(f"{OUT}/s2_claims.json", "w"), ensure_ascii=False, indent=0)

# ---------------------------------------------------------------- Task 3: executor re-check
rc = [(ln, c) for ln, c in table_rows(f"{LIT}/_executor_recheck.md") if c and re.fullmatch(r"\d+", c[0])]
st = Counter(c[-1] for _, c in rc)
say(f"\n_executor_recheck.md: {len(rc)} rows; status counts {dict(st)}; per reader "
    f"{dict(Counter(c[1] for _, c in rc))}")
say("re-check rows not V:", [(c[0], c[1], c[2], c[-1]) for _, c in rc if c[-1].strip() != "V"])
# do re-check rows exist in the ledgers? match by reader + id + a quoted fragment
miss = []
for _, c in rc:
    frag = re.findall(r'"([^"]{12,})', c[3])
    frag = frag[0].split("…")[0][:40].strip() if frag else None
    cands = [r for r in ledger if r["reader"] == c[1] and (r["pid"] == c[2] or r["pid"].startswith(c[2]))]
    ok = any(frag and frag.lower() in r["claim"].lower() for r in cands) if frag else bool(cands)
    if not ok:
        miss.append((c[0], c[1], c[2], frag))
say("re-check rows not traceable to a ledger row (reader + id + quoted fragment):", miss if miss else "none")
open(f"{OUT}/s2_claims.txt", "w").write("\n".join(lines) + "\n")
