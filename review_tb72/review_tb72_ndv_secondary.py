#!/usr/bin/env python3
"""Labelled secondary only (pre-registered; judges nothing): per checkpoint, problems with >= 1 Lean-accepted stored proof
that nd_verify also accepts, and distinct Lean-accepted proofs nd_verify rejects.  REPO=... python3 this.py OUT.json"""
import json, os, sys
REPO = os.environ['REPO']; sys.path.insert(0, REPO)
from nd_verify import verify_text
out = {}
for fn in sorted(os.listdir(f'{REPO}/artifacts/textbook72/eval')):
    if not fn.endswith('.jsonl'): continue
    ok_probs, nrej, n = 0, 0, 0
    for l in open(f'{REPO}/artifacts/textbook72/eval/{fn}'):
        r = json.loads(l); any_ok = False
        for p in r['proofs']:
            n += 1
            if verify_text(r['prompt'].strip() + ' ' + p.strip())[0]: any_ok = True
            else: nrej += 1
        ok_probs += any_ok
    out[fn[:-6]] = {'lean_and_ndverify_solved': ok_probs, 'distinct': n, 'distinct_ndverify_rejects': nrej}
    print(fn, out[fn[:-6]], flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
