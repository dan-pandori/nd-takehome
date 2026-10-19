import json, sys, glob
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt
from sealkey import keys
src = open('/home/dan/review/proof-strategies/phase2/scripts/s5_lean_snippets.py').read()
ns = {}; exec(src[:src.index('T = TB72(')], ns)
code = [c for ln, c in ns['snips'] if ln == 69][0]
bk = keys(*ns['statement'](code))
for fn in sorted(glob.glob('/home/dan/review/proof-strategies/data/ps/in/charles/*.jsonl')):
    n = 0; nh = 0; roles = set()
    for l in open(fn):
        r = json.loads(l); p = r.get('prompt')
        if not p: continue
        try: pr, c = parse_prompt(p)
        except Exception: continue
        n += 1
        k = keys(pr, c)
        h = sorted(t for t in k if k[t] == bk[t])
        if h:
            nh += 1; roles.add((tuple(h), len(pr), r.get('family'), r.get('form')))
    print(fn.split('/')[-1], 'prompts', n, 'hits', nh, sorted(roles))
