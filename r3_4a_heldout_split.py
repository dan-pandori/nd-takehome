#!/usr/bin/env python3
"""round3-run4a: held-out greedy split by the held-out record's pattern label (reductio-labelled vs not).
usage: python3 r3_4a_heldout_split.py  -> artifacts/r3_4a/heldout_split.json"""
import json, glob, re
h = {json.loads(l)['prompt']: json.loads(l) for l in open('data/p2/heldout.jsonl')}
out = {}
for fn in sorted(glob.glob('artifacts/r3_4a/heldout_greedy_*.jsonl')):
    tag = re.findall(r'heldout_greedy_(.*)\.jsonl', fn)[0]
    rows = [json.loads(l) for l in open(fn)]
    red = [r for r in rows if h[r['prompt']]['pat']['reductio']]; non = [r for r in rows if not h[r['prompt']]['pat']['reductio']]
    out[tag] = {'all': sum(r['solved'] for r in rows) / len(rows), 'n': len(rows), 'non_reductio_solved': sum(r['solved'] for r in non), 'non_reductio_n': len(non),
                'non_reductio': sum(r['solved'] for r in non) / len(non), 'reductio_solved': sum(r['solved'] for r in red), 'reductio_n': len(red)}
    print(tag, out[tag])
json.dump(out, open('artifacts/r3_4a/heldout_split.json', 'w'), indent=1)
