"""Secret scan of everything under hf://buckets/dan-pandori/nd-rl/olmo-iffu/ (the bucket is public).

For each listed bucket file: if a local file at the same relative path has the same size, scan it (the 17 bulk
files' sha256 were checked against MANIFEST.jsonl separately); otherwise stream the bucket copy. Only pattern names
and file paths are printed, never a match.  -> out/secrets.txt
"""
import gzip
import re
import subprocess
from pathlib import Path

import rvi_core as C

PATS = {"hf_token": rb"hf_[A-Za-z0-9]{30,}", "github": rb"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
        "anthropic": rb"sk-ant-[A-Za-z0-9_\-]{20,}", "openai_like": rb"\bsk-[A-Za-z0-9]{32,}",
        "aws": rb"AKIA[0-9A-Z]{16}", "runpod": rb"(rpa_[A-Za-z0-9]{20,}|RUNPOD_API_KEY\s*=\s*\S+)",
        "bearer": rb"[Bb]earer\s+[A-Za-z0-9._\-]{20,}", "private_key": rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"}
WT = C.KIT.parent.parent  # the run's worktree


def main():
    ls = (C.SCR / "bucket_ls.txt").read_text().splitlines()
    files = []
    for ln in ls:
        p = ln.split()
        if len(p) >= 4 and p[0].isdigit():
            files.append((int(p[0]), p[-1]))
    hits, local, streamed = [], 0, 0
    for size, path in files:
        rel = path.split("/", 1)[1]
        lp = WT / rel
        if lp.exists() and lp.stat().st_size == size:
            data = lp.read_bytes()
            local += 1
        else:
            data = subprocess.run(["hf", "buckets", "cp", f"hf://buckets/dan-pandori/nd-rl/{path}", "-"],
                                  capture_output=True).stdout
            streamed += 1
        if path.endswith(".gz"):
            data = gzip.decompress(data)
        for name, pat in PATS.items():
            n = len(re.findall(pat, data))
            if n:
                hits.append((path, name, n))
    # sample files: separate the base64 token-id field (random base64 can match a key pattern) from text fields
    field = []
    for path, name, n in hits:
        if "/samples/" in path and path.endswith(".jsonl.gz"):
            import json
            pat = re.compile(PATS[name].decode())
            cnt = {"text": 0, "ids": 0, "other": 0}
            with gzip.open(WT / path.split("/", 1)[1], "rt") as f:
                for ln in f:
                    r = json.loads(ln)
                    cnt["text"] += len(pat.findall(r["text"]))
                    cnt["ids"] += len(pat.findall(r["ids"]))
                    cnt["other"] += len(pat.findall(json.dumps({k: v for k, v in r.items() if k not in ("text", "ids")})))
            field.append((path, name, cnt))
    lines = [f"bucket files {len(files)}: scanned {local} local copies (same size), streamed {streamed}",
             f"pattern hits: {hits if hits else 'none'}",
             f"hits in sample files by field: {field if field else 'n/a'}"]
    (C.OUT / "secrets.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
