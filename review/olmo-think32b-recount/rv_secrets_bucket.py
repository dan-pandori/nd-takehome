"""Secret-pattern scan over ALL bucket files (reviewer): local copies where the bucket size equals the local size,
otherwise the file fetched to /tmp/rv_bucket_scan. Prints names and pattern names only, never matches."""
import gzip, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REV = "/home/dan/review/olmo-think32b"
src = open(os.path.join(HERE, "rv_secrets.py")).read()
ns = {}; exec("import re\nPAT = " + src.split("PAT = ")[1].split("hits = {}")[0], ns); PAT = ns["PAT"]
rows = [l.split() for l in open(os.path.join(HERE, "out", "bucket_ls.txt")) if re.match(r"\s*\d+\s", l)]
scanned = hits = fetched = missing = 0; bad = []
for parts in rows:
    size, path = int(parts[0]), parts[-1].replace("olmo-think32b/", "", 1)
    cands = [os.path.join(ROOT, path), os.path.join(REV, path), os.path.join("/tmp/rv_bucket_scan", "olmo-think32b_" + path.replace("/", "_"))]
    p = next((c for c in cands if os.path.exists(c) and os.path.getsize(c) == size), None)
    if p is None:
        missing += 1; bad.append(("not available locally", path)); continue
    fetched += p.startswith("/tmp/")
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt", errors="ignore") as f:
        s = f.read()
    scanned += 1
    h = [k for k, r in PAT.items() if r.search(s)]
    if h:
        hits += 1; bad.append((path, h))
print(f"bucket files {len(rows)}; scanned {scanned} ({fetched} fetched from the bucket); missing {missing}; files with a pattern hit {hits}")
for b in bad:
    print("  ", b)
