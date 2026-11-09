"""Bucket / MANIFEST / secrets / hard-constraint checks for run olmo-ifladder (reviewer's code).

1. The bucket listing (hf buckets ls -R, ~/review/oifl_rv/bucket_ls.txt) vs my full copy (hf buckets sync ->
   ~/review/oifl_rv/bucket_copy): every object present with its listed size; sha256 of every copied object vs the
   MANIFEST.jsonl entries for olmo-ifladder and vs the phase-1 workspace file at the same path.
2. Secret-pattern scan of the CONTENTS of every copied object (gzip members decompressed; binary files scanned as
   bytes in 64 MB chunks with overlap). Only the file name and a 3-byte prefix + length of a hit are printed.
3. Model weights: no file over 1 GB and no full-model safetensors shards in the bucket (adapters only).
4. Hard constraints: nd_verify/ and artifacts/TEST_RUN_DONE byte-identical to origin/main; no run code imports
   nd_verify; lora.py reads only the training manifest (and its own log).
Writes out/hygiene.txt.
"""
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

from rvl_core import OUT, RAW, SCR, Tee

P = Tee("hygiene.txt")
WT = Path.home() / "work" / "olmo-ifladder"
BC = SCR / "bucket_copy"
from rvl_hygiene_pat import PAT  # noqa: E402

ls = []
for l in open(SCR / "bucket_ls.txt"):
    f = l.split()
    if len(f) >= 4 and f[0].isdigit():
        ls.append((int(f[0]), f[-1]))
P(f"[1] bucket objects listed {len(ls)}, bytes {sum(s for s, _ in ls)}")
man = {}
for l in open(RAW / "artifacts" / "MANIFEST.jsonl"):
    r = json.loads(l)
    if r.get("run") == "olmo-ifladder" or "/olmo-ifladder/" in r.get("uri", ""):
        man[r["uri"].split("nd-rl/", 1)[1]] = r
missing, size_bad, sha_bad, loc_bad, loc_missing, n_man = [], [], [], [], 0, 0


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


hits, scanned, big = [], 0, []
for size, path in ls:
    rel = path.split("/", 1)[1]
    p = BC / rel
    if not p.exists():
        missing.append(path)
        continue
    if p.stat().st_size != size:
        size_bad.append(path)
    h = sha_file(p)
    if path in man:
        n_man += 1
        if man[path]["sha256"] != h:
            sha_bad.append(path)
    loc = RAW / rel
    if loc.exists():
        if sha_file(loc) != h:
            loc_bad.append(rel)
    else:
        loc_missing += 1
    if size > 1 << 30 or (rel.endswith(".safetensors") and "adapter" not in rel):
        big.append(rel)
    # 2. scan
    data_iter = []
    if rel.endswith(".gz"):
        try:
            with gzip.open(p, "rb") as f:
                for b in iter(lambda: f.read(1 << 26), b""):
                    data_iter.append(b)
                    if len(data_iter) > 1:
                        data_iter = [data_iter[-2][-256:] + data_iter[-1]]
                    for m in PAT.finditer(data_iter[-1]):
                        hits.append((rel, m.group(0)[:3] + b"... len %d" % len(m.group(0))))
        except Exception as e:  # noqa: BLE001
            hits.append((rel, f"gunzip failed {e}".encode()))
    else:
        prev = b""
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 26), b""):
                for m in PAT.finditer(prev[-256:] + b):
                    hits.append((rel, m.group(0)[:3] + b"... len %d" % len(m.group(0))))
                prev = b
    scanned += 1
P(f"    missing from my copy {len(missing)} {missing[:3]}; size mismatches {len(size_bad)} {size_bad[:3]}")
P(f"    MANIFEST entries for the run {len(man)}; bucket objects with an entry {n_man}; sha != MANIFEST {len(sha_bad)} "
  f"{sha_bad[:3]}; MANIFEST entries not in the bucket {len(set(man) - {p for _, p in ls})}")
P(f"    bucket objects with a phase-1 workspace file at the same path: {len(ls) - len(missing) - loc_missing}; "
  f"of these differing {len(loc_bad)} {loc_bad[:5]}; without a local file {loc_missing}")
P(f"[2] secret-pattern scan over {scanned} objects: hits {len(hits)}")
for h in hits[:20]:
    P(f"      {h[0]}: {h[1]!r}")
P(f"[3] objects > 1 GB or non-adapter safetensors: {big}; adapter files "
  f"{[rel for _, rel in ls if rel.endswith('.safetensors')]}")
# 4. hard constraints
def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout


files = git("ls-files", "nd_verify").split()
same = [git("show", f"origin/main:{f}") == (WT / f).read_text() for f in files]
P(f"[4] nd_verify files {files}: identical to origin/main {sum(same)}/{len(same)}; TEST_RUN_DONE identical: "
  f"{git('show', 'origin/main:artifacts/TEST_RUN_DONE') == (WT / 'artifacts/TEST_RUN_DONE').read_text()}")
imp = subprocess.run(["grep", "-rln", r"nd_verify\|verify_text", str(WT / "olmo_ifladder"), str(WT / "pod" / "olmo_ifladder")],
                     capture_output=True, text=True).stdout.split()
P(f"    run code importing nd_verify / verify_text: {imp}")
src = (WT / "olmo_ifladder" / "lora.py").read_text()
opens = re.findall(r"open\(([^)]*)\)", src)
P(f"    lora.py open() calls: {opens}")
