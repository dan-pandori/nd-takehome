"""Where is the one secret-pattern hit of rvt_hygiene.py? (prints the JSON field it sits in, never the match)
Output: out/hygiene_hit.txt"""
import gzip
import re

from rvt_core import ART, Tee

P = Tee("hygiene_hit.txt")
raw = gzip.open(ART / "samples" / "R_dpo.jsonl.gz").read()
for m in re.finditer(rb"AKIA[0-9A-Z]{16}", raw):
    q = raw.rfind(b'": "', 0, m.start())
    field = raw[raw.rfind(b'"', 0, q) + 1:q].decode()
    inside = raw.find(b'"', q + 4, m.end()) == -1
    P(f"offset {m.start()}: inside the JSON string field {field!r} (no closing quote before the match end: {inside}); "
      f"the field is base64 int32 token ids, so a 20-character [A-Z0-9] run is chance, not a credential")
