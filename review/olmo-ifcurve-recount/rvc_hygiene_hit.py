"""Locate the secret-pattern hits of rvc_hygiene.py inside the bucket's sample files: job, pid, field, whether the
match is the AWS documentation example key (AKIAIOSFODNN7EXAMPLE) or a placeholder, and the masked context (letters
of the match beyond its first 4 characters replaced by '*'). Writes out/hygiene_hit.txt."""
import gzip
import json

from rvc_core import SCR, Tee
from rvc_hygiene_pat import PAT

T = Tee("hygiene_hit.txt")
EX = b"AKIAIOSFODNN7EXAMPLE"
for job in ("M_s0050", "M_s0200", "M_s0500", "M_s1100", "M_s1600", "X_s0100"):
    p = SCR / "bucket_copy" / "artifacts" / "olmo_ifcurve" / "samples" / f"{job}.jsonl.gz"
    for ln in gzip.open(p, "rb"):
        if not PAT.search(ln):
            continue
        r = json.loads(ln)
        found = False
        for f in ("text", "ids", "pid"):
            v = r.get(f)
            if not isinstance(v, str):
                continue
            for m in PAT.finditer(v.encode()):
                g = m.group(0)
                a, b = max(0, m.start() - 60), m.end() + 40
                ctx = v.encode()[a:b].decode("utf-8", "replace")
                masked = ctx.replace(g.decode("utf-8", "replace"), g[:4].decode() + "*" * (len(g) - 4))
                found = True
                T(f"{job} {r['pid']} chunk {r['chunk']} i {r['i']} field {f}: AWS doc example key: {g == EX}; "
                  f"'EXAMPLE' in match: {b'EXAMPLE' in g}; context: {masked!r}")
        if not found:  # the match exists only in the JSON-escaped line (e.g. across a \\" escape)
            for m in PAT.finditer(ln):
                g = m.group(0)
                ctx = ln[max(0, m.start() - 80):m.end() + 30].decode("utf-8", "replace")
                T(f"{job} {r['pid']} chunk {r['chunk']} i {r['i']} raw JSON line only (len {len(g)}, prefix {g[:6]!r}); "
                  f"masked context: {ctx.replace(g.decode('utf-8', 'replace'), g[:6].decode() + '*' * (len(g) - 6))!r}")
