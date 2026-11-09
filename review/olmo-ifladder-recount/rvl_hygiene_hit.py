"""Locate the secret-pattern hits of rvl_hygiene.py inside the sample rows (prints the JSON field, the character
before the match, and the match's character classes; never the match). Writes out/hygiene_hit.txt."""
import gzip
import json
import re

from rvl_core import SCR, Tee
from rvl_hygiene_pat import PAT

P = Tee("hygiene_hit.txt")
files = ["Lchk_ctrl", "Leval_ctrl", "R1cal_dpo", "R2_dpo", "R3_dpo", "R2_s2300", "R3_s2300", "R4_dpo", "R4_s2300",
         "Leval_main", "Lchk_main", "S0r2", "S0r3"]
tot = 0
for f in files:
    p = SCR / "bucket_copy" / "artifacts" / "olmo_ifladder" / "samples" / f"{f}.jsonl.gz"
    for ln in gzip.open(p, "rt"):
        r = json.loads(ln)
        for field in ("text", "ids"):
            for m in PAT.finditer(r[field].encode()):
                s = m.group(0).decode()
                prev = r[field][m.start() - 1] if m.start() > 0 else ""
                cls = ("lowercase letters and hyphens only" if re.fullmatch(r"[a-z-]+", s) else
                       "letters/digits/hyphen mix" if re.fullmatch(r"[A-Za-z0-9_-]+", s) else "other")
                hyph = s.count("-")
                tot += 1
                P(f"{f} {r['pid']} chunk {r['chunk']} i {r['i']} field {field}: len {len(s)}, preceded by "
                  f"{'a letter' if prev.isalpha() else repr(prev) if prev in ' \n\t' else 'other'}; {cls}; hyphens {hyph}")
P(f"total {tot}")
