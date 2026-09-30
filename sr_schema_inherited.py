#!/usr/bin/env python3
"""state-readouts: per-schema textbook solves from existing found_transfer files (inherited arms).
Usage: python3 sr_schema_inherited.py LABEL=gitref:path [LABEL=localpath ...]  -> table to stdout, json to artifacts/state-readouts/inherited_schema.json"""
import json, sys, subprocess, collections
pool = [json.loads(l) for l in open('data/ladder/transfer.jsonl')]
tb = {r['name']: r['schema'] for r in pool if r['source'] == 'textbook'}
schemas = sorted(set(tb.values()))
out = {}
for arg in sys.argv[1:]:
    lab, src = arg.split('=', 1)
    txt = subprocess.run(['git', 'show', src], capture_output=True, text=True, check=True).stdout if ':' in src else open(src).read()
    solved = {json.loads(l)['name'] for l in txt.splitlines() if l.strip()}
    c = collections.Counter(tb[n] for n in solved if n in tb)
    out[lab] = {s: c.get(s, 0) for s in schemas}
print('schema'.ljust(26) + ''.join(l[:9].rjust(10) for l in out))
for s in schemas:
    print(s.ljust(26) + ''.join(str(out[l][s]).rjust(10) for l in out))
print('total'.ljust(26) + ''.join(str(sum(out[l].values())).rjust(10) for l in out))
json.dump(out, open('artifacts/state-readouts/inherited_schema.json', 'w'), indent=1)
