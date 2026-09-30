#!/usr/bin/env python3
"""state-readouts: label each textbook theorem (and each survivor) intuitionistically provable or classical-only with
intuit.py (G4ip decision procedure; it uses nd_verify's formula PARSER only, to read the theorem; no proof is judged).
-> data/sr/intuit_labels.json {name: true (intuitionistically provable) | false (classical-only)}"""
import json
from intuit import intuit_provable
out = {}
for f in ('data/sr/textbook_transfer.jsonl', 'data/sr/textbook_long.jsonl', 'data/sc/theorems.jsonl'):
    for l in open(f):
        r = json.loads(l)
        if r['name'] not in out:
            out[r['name']] = bool(intuit_provable(r['prompt']))
json.dump(out, open('data/sr/intuit_labels.json', 'w'), indent=0, sort_keys=True)
print(len(out), 'labelled;', sum(not v for v in out.values()), 'classical-only')
