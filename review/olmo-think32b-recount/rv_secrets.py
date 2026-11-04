"""Secret-pattern scan (reviewer) over the local copies of every file under artifacts/olmo32, olmo32/, pod/olmo32
(what the bucket holds); prints file names and pattern names only, never matches."""
import gzip, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAT = {"hf": re.compile(r"hf_[A-Za-z0-9]{30,}"), "runpod": re.compile(r"rpa_[A-Za-z0-9]{20,}"),
       "openai": re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "github": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
       "env_assign": re.compile(r"(HF_TOKEN|HUGGING_FACE_HUB_TOKEN|RUNPOD_API_KEY|GH_TOKEN|GITHUB_TOKEN)\s*=\s*\S{8,}"),
       "aws": re.compile(r"AKIA[0-9A-Z]{16}"), "bearer": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}")}
hits = {}; n = 0
for base in ("artifacts/olmo32", "olmo32", "pod/olmo32"):
    for dp, _, fs in os.walk(os.path.join(ROOT, base)):
        for fn in fs:
            p = os.path.join(dp, fn); n += 1
            op = gzip.open if fn.endswith(".gz") else open
            try:
                with op(p, "rt", errors="ignore") as f:
                    s = f.read()
            except Exception as e:
                hits[p] = [f"unreadable {e!r}"[:60]]; continue
            h = [k for k, r in PAT.items() if r.search(s)]
            if h:
                hits[os.path.relpath(p, ROOT)] = h
print(f"scanned {n} files; files with a pattern hit: {len(hits)}")
for k, v in hits.items():
    print(" ", k, v)
