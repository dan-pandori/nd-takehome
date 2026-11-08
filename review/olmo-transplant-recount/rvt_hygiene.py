"""Bucket / MANIFEST / secrets checks for run olmo-transplant (reviewer's code).

1. Every MANIFEST.jsonl entry this run added: the bucket object's sha256 (streamed with `hf buckets cp <uri> -`) vs
   the manifest's sha256 and bytes, and vs the local file in the phase-1 workspace.
2. Secret-pattern scan of the CONTENTS of every object under hf://buckets/dan-pandori/nd-rl/olmo-transplant/
   (listing in ~/review/otr_rv/bucket_ls.txt), gzip members decompressed. Patterns: HF / GitHub / OpenAI-style / AWS /
   RunPod-like keys, `*_TOKEN=` / `API_KEY=` assignments, private-key headers.
Sequential (one download at a time). Output: out/hygiene.txt
"""
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

from rvt_core import OUT, RAW, SCR, Tee

P = Tee("hygiene.txt")
WT = Path.home() / "work" / "olmo-transplant"
BASE = "c0c6e05355051d49ac5cd2781d286a8095b563b5"
PAT = re.compile(rb"(hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{30,}|"
                 rb"AKIA[0-9A-Z]{16}|rpa_[A-Za-z0-9]{20,}|[A-Z_]*(TOKEN|API_KEY|SECRET)[A-Z_]*\s*=\s*\S{8,}|"
                 rb"-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def fetch(uri):
    r = subprocess.run(["hf", "buckets", "cp", uri, "-"], capture_output=True, timeout=600)
    return r.returncode, r.stdout


diff = subprocess.run(["git", "-C", str(WT), "diff", BASE, "HEAD", "--", "artifacts/MANIFEST.jsonl"],
                      capture_output=True, text=True).stdout
entries = [json.loads(l[1:]) for l in diff.splitlines() if l.startswith("+{")]
P(f"[1] MANIFEST entries added by the run: {len(entries)}")
for e in entries:
    rc, b = fetch(e["uri"])
    h = hashlib.sha256(b).hexdigest()
    loc = RAW / e["path"]
    lh = hashlib.sha256(loc.read_bytes()).hexdigest() if loc.exists() else None
    P(f"    {e['path']}: bucket rc {rc} bytes {len(b)} (manifest {e['bytes']}); sha bucket==manifest {h == e['sha256']}; "
      f"local==manifest {lh == e['sha256']}")
ls = [l.split()[-1] for l in open(SCR / "bucket_ls.txt") if l.strip()]
P(f"[2] secrets scan over {len(ls)} bucket objects")
hits, failed = [], []
for path in ls:
    uri = f"hf://buckets/dan-pandori/nd-rl/{path}"
    rc, b = fetch(uri)
    if rc != 0:
        failed.append(path)
        continue
    if path.endswith(".gz"):
        try:
            b = gzip.decompress(b)
        except Exception:
            failed.append(path + " (gunzip)")
    for m in PAT.finditer(b):
        hits.append((path, m.group(0)[:3] + b"... len %d" % len(m.group(0))))  # never print a secret
P(f"    fetch failures: {failed}")
P(f"    pattern hits: {len(hits)}")
for h in hits[:40]:
    P(f"      {h[0]}: {h[1]!r}")
