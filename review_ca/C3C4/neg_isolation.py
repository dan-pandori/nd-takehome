"""Harness validity: interleave every negative control with a known-good counted proof; the good ones must all pass
(no cascade across theorems) and every control must fail with an error attributed to its own lines."""
import json, collections
from common import *
R = json.load(open(ROOT + '/rv/C3C4/lean_recheck.json'))
good = [one for one in R['items'] if one['kind'] == 'literal' and one['ok']]
import random; rng = random.Random(1)
srcs, tags = [], []
for n in R['neg']:
    g = rng.choice(good)
    srcs += [n['src'], statement(g['prompt']) + ' ' + g['text']]; tags += [('neg', n['claim'], n['ctl']), ('good',)]
res = []
for k in range(0, len(srcs), 100):
    r, _ = lean_batch(srcs[k:k + 100]); res += r
c = collections.Counter()
for t, (ok, msg) in zip(tags, res):
    if t[0] == 'good': c[('good', 'pass' if ok else 'FAIL')] += 1
    else: c[(t[1], t[2], 'rejected-with-own-error' if (not ok and msg) else ('rejected-no-msg' if not ok else 'ACCEPTED'))] += 1
for k, v in sorted(c.items()): print(k, v)
prev = collections.Counter()
for idx, (t, (ok, msg)) in enumerate(zip(tags, res)):
    if t[0] == 'good' and not ok: prev[tags[idx - 1]] += 1
print('controls preceding the failed good proofs:', dict(prev))
