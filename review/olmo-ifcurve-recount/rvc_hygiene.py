"""Bucket / secrets / weights checks for run olmo-ifcurve (reviewer's code).

1. The bucket listing (hf buckets ls -R -> ~/review/oifc_rv/bucket_ls.txt) vs my full copy (hf buckets sync ->
   ~/review/oifc_rv/bucket_copy): every object present with its listed size; sha256 of every copied object vs the
   phase-1 workspace file at the same path (artifacts/olmo_ifcurve/...), and vs MANIFEST.jsonl entries for the run.
2. Secret-pattern scan of the CONTENTS of every copied object (gzip members decompressed), plus the run's tracked
   code / docs under olmo_ifcurve/, pod/olmo_ifcurve/, preregistration/olmo-ifcurve.md. Only the file name and a
   3-byte prefix + length of a hit are printed.
3. Model weights: no object over 1 GB and no safetensors / .bin / .pt shards in the bucket.
Writes out/hygiene.txt.
"""
import gzip
import hashlib
import json
from pathlib import Path

from rvc_core import RAW, SCR, Tee
from rvc_hygiene_pat import PAT

P = Tee("hygiene.txt")
BC = SCR / "bucket_copy"
ls = []
for l in open(SCR / "bucket_ls.txt"):
    f = l.split()
    if len(f) >= 4 and f[0].isdigit():
        ls.append((int(f[0]), f[-1]))
P(f"[1] bucket objects listed {len(ls)}, bytes {sum(s for s, _ in ls):,}")
missing, size_bad, loc_bad, loc_missing = [], [], [], []
for s, uri in ls:
    rel = uri.split("olmo-ifcurve/", 1)[1]
    p = BC / rel
    if not p.exists():
        missing.append(rel)
        continue
    if p.stat().st_size != s:
        size_bad.append(rel)
    q = RAW / rel
    if q.exists():
        if hashlib.sha256(p.read_bytes()).hexdigest() != hashlib.sha256(q.read_bytes()).hexdigest():
            loc_bad.append(rel)
    else:
        loc_missing.append(rel)
P(f"    missing from my copy {len(missing)} {missing[:3]}; size mismatches {len(size_bad)}; differ from the workspace file "
  f"{len(loc_bad)} {loc_bad[:5]}; not in the workspace {len(loc_missing)} {loc_missing[:5]}")
man = [json.loads(l) for l in open(RAW / "artifacts" / "MANIFEST.jsonl")]
man = [r for r in man if "olmo-ifcurve" in json.dumps(r)]
P(f"    MANIFEST.jsonl entries mentioning olmo-ifcurve: {len(man)}")
bad_man = []
for r in man:
    uri = r.get("uri") or r.get("bucket") or ""
    rel = uri.split("olmo-ifcurve/", 1)[1] if "olmo-ifcurve/" in uri else None
    sha = r.get("sha256")
    if rel and sha and (BC / rel).exists():
        if hashlib.sha256((BC / rel).read_bytes()).hexdigest() != sha:
            bad_man.append(rel)
P(f"    MANIFEST sha256 mismatches against my copy: {len(bad_man)} {bad_man[:3]}")


def scan_bytes(b):
    return [(m.group(0)[:3], len(m.group(0))) for m in PAT.finditer(b)]


hits = []
n = 0
for p in sorted(BC.rglob("*")):
    if not p.is_file():
        continue
    n += 1
    b = p.read_bytes()
    if p.suffix == ".gz":
        try:
            b = gzip.decompress(b)
        except Exception:
            pass
    for h in scan_bytes(b):
        hits.append((str(p.relative_to(BC)), h))
for d in (RAW / "olmo_ifcurve", RAW / "pod" / "olmo_ifcurve"):
    for p in sorted(d.rglob("*")):
        if p.is_file():
            n += 1
            for h in scan_bytes(p.read_bytes()):
                hits.append((str(p.relative_to(RAW)), h))
for p in (RAW / "preregistration" / "olmo-ifcurve.md",):
    n += 1
    for h in scan_bytes(p.read_bytes()):
        hits.append((str(p.relative_to(RAW)), h))
P(f"[2] secret-pattern scan of {n} files (bucket copy, contents decompressed; tracked run code): hits {len(hits)} {hits[:10]}")
big = [(s, u) for s, u in ls if s > 1 << 30]
wts = [u for s, u in ls if u.endswith((".safetensors", ".bin", ".pt", ".pth", ".gguf"))]
P(f"[3] objects over 1 GB: {big}; weight-like files: {wts}")
