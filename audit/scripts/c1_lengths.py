"""C1(c): token length of accepted proofs vs max_new=400 (support-curves). Token count = lean_text split on
whitespace with .1/.2/.elim suffixes split off (lean_tok.LeanTokenizer.text inverse), +1 for <eos>."""
import json, glob, re
R = '/home/dan/work/claim-audit/audit/raw/support-curves/'
surv = set(open(R + 'data/sc/falsifier_survivors.txt').read().split())
def ntok(t):
    return sum(1 + len(re.findall(r'\.(1|2|elim)$', w)) for w in t.split()) + 1
out = {}
for f in sorted(glob.glob(R + 'artifacts/sc/s*.jsonl')):
    if 'secondary' in f: continue
    for l in open(f):
        r = json.loads(l)
        for p in r['proofs']:
            key = (r['model'], r['name'] in surv)
            out.setdefault(key, []).append(ntok(p['lean_text']))
for k, v in sorted(out.items()):
    v.sort(); print(k, 'n distinct', len(v), 'median', v[len(v)//2], 'p99', v[int(len(v)*.99)], 'max', v[-1])
