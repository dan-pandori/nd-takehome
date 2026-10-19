"""Do any blog snippet sequents fall in a renaming class (4 keys) of any prompt in Charles's private release? Prints counts only."""
import json, sys, glob
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt
from sealkey import keys
sys.path.insert(0, '/home/dan/review/proof-strategies/phase2/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('s5', '/home/dan/review/proof-strategies/phase2/scripts/s5_lean_snippets.py')
src = open('/home/dan/review/proof-strategies/phase2/scripts/s5_lean_snippets.py').read()
# reuse the parser functions only (exec the definitions part, not the run part)
defs = src[:src.index('T = TB72(')]
ns = {}
exec(defs, ns)
snips = ns['snips']; statement = ns['statement']
K = {"po": set(), "set": set(), "cur": set(), "curneg": set()}
nprompts = 0
for fn in glob.glob('/home/dan/review/proof-strategies/data/ps/in/charles/*.jsonl'):
    for l in open(fn):
        r = json.loads(l)
        p = r.get('prompt')
        if not p: continue
        try:
            pr, c = parse_prompt(p)
        except Exception:
            continue
        nprompts += 1
        for k, v in keys(pr, c).items(): K[k].add(v)
print('charles prompts keyed:', nprompts)
for ln, code in snips:
    pr, c = statement(code)
    hits = sorted(k for k, v in keys(pr, c).items() if v in K[k])
    print('blog line', ln, 'charles-class hits:', hits)
