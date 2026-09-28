"""Reviewer: re-check every parsed arm-C sample (stored literal text) in Lean with rv/leanrc.py."""
import json, sys
sys.path.insert(0, 'rv'); sys.path.insert(0, '.')
from leanrc import check
recs = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
out = open('rv/recheck_c.jsonl', 'w')
for s in range(8):
    C = [json.loads(l) for l in open(f'rv/oldc/c_s{s}.jsonl')]
    it = [(i, recs[i]['prompt'], r['text']) for i, r in enumerate(C) if r['parsed']]
    res = check([(p, t) for _, p, t in it])
    for (i, _, _), ok in zip(it, res):
        out.write(json.dumps({'seed': s, 'i': i, 'mine': ok, 'theirs': C[i]['lean_ok']}) + '\n')
    out.flush()
    print(s, len(it), 'agree', sum(ok == C[i]['lean_ok'] for (i, _, _), ok in zip(it, res)), flush=True)
