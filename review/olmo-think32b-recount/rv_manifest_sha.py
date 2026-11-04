"""Bucket manifest check (reviewer): every artifacts/MANIFEST.jsonl row of run olmo-think32b -> local file sha256 and
size equal; every sample file listed; bucket listing sizes equal local sizes."""
import hashlib, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
rows = [json.loads(l) for l in open(os.path.join(ROOT, "artifacts", "MANIFEST.jsonl"))]
mine = [r for r in rows if r.get("run") == "olmo-think32b"]
ok = bad = missing = 0; badl = []
for r in mine:
    p = os.path.join(ROOT, r["path"])
    if not os.path.exists(p):
        missing += 1; badl.append(("missing", r["path"])); continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h == r["sha256"] and os.path.getsize(p) == r["bytes"]:
        ok += 1
    else:
        bad += 1; badl.append(("differs", r["path"]))
print(f"manifest rows for run: {len(mine)}; sha+size equal {ok}; differ {bad}; missing locally {missing}")
print(badl[:20])
samp = sorted(r["path"] for r in mine if "/samples/" in r["path"])
print("sample files in manifest:", len(samp))
# bucket listing vs local sizes
ls = [l.split() for l in open(os.path.join(HERE, "out", "bucket_ls.txt")) if re.match(r"\s*\d+\s", l)]
diff = []
for parts in ls:
    size, path = int(parts[0]), parts[-1].replace("olmo-think32b/", "", 1)
    lp = os.path.join(ROOT, path)
    if os.path.exists(lp) and os.path.getsize(lp) != size:
        diff.append(path)
print("bucket files:", len(ls), "| local size differs:", diff[:10])
