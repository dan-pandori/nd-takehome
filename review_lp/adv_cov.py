import sys, os, json, collections, re
sys.path.insert(0, '.'); sys.path.insert(0, 'review_lp')
exec(open('review_lp/adv.py').read().split('# keep texts')[0])
from lean_prefilter import reject_reason
from lean_tok import LeanTokenizer
tok = LeanTokenizer('lean_seq')
c = collections.Counter()
for prem, prompt, text in tests:
    if reject_reason(tok.statement(prompt), text) is None:
        body = text.split(':= ', 3)[-1] if False else text.split(' have n50 : ')[1].split(' := ', 1)[1].rsplit(' ; exact n50', 1)[0]
        form = re.sub(r'\( fun.*', 'box', body)[:40]
        decl = re.findall(r'have (n\d) : (.*?) := h\d', text)
        d = dict(decl)
        m = re.match(r'(n\d)\.elim', body)
        key = form if not m else f'{m.group(1)}.elim on {d[m.group(1)][:12]}'
        c[key] += 1
for k, v in c.most_common(): print(v, k)
