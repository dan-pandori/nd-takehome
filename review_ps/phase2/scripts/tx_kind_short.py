#!/usr/bin/env python3
"""Phase-2 sub-audit: the K12 reductios with exactly one #10 kind that are SHORTER than the kind example (or primary when
the example is not): count by length / primary / the readable() clause that excludes them.  No theorem text printed."""
import collections, gzip, json, sys
sys.path.insert(0, '/home/dan/review/proof-strategies/phase2/scripts')
from tx_shortest_lib import readable_why  # noqa: E402
W = "/home/dan/work/proof-strategies"; R = "/home/dan/review/proof-strategies"
KINDS = ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free')
C = collections.Counter()
fa = gzip.open(f"{W}/artifacts/ps/labels/k12.jsonl.gz", "rt"); fs = gzip.open(f"{R}/data/ps/in/train_k12.jsonl.gz", "rt")
for la, ls in zip(fa, fs):
    a = json.loads(la)
    ks = [k for k in KINDS if f'contradiction.{k}' in a['sub']]
    if len(ks) != 1:
        continue
    kd = ks[0]
    prim = a['pri'] == 'contradiction' and f'contradiction.{kd}' in a['psub']
    if (kd == 'vacuous' and a['Lp'] <= 5) or (kd == 'neg_goal' and a['Lp'] <= 5) or (kd == 'free'):
        s = json.loads(ls)
        C[(kd, a['Lp'], 'primary' if prim else 'not primary', readable_why(s['prompt'], s['proof']) or 'readable')] += 1
for k in sorted(C):
    print(k, C[k])
