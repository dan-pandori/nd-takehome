"""Count textbook72-class prompts in the uploaded fixtures file (counts only; nothing printed from either file)."""
import json, sys
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt
from sealkey import TB72, keys
tb = TB72(path='/home/dan/review/proof-strategies/data/bs/textbook72.jsonl')
fn = '/home/dan/work/proof-strategies/data/ps/validation/second_impl_fixtures_v1.2.jsonl'
n = hit_po = hit_any = 0
for l in open(fn):
    r = json.loads(l); n += 1
    p, c = parse_prompt(r['prompt'])
    k = keys(p, c)
    po = k['po'] in tb.K['po']
    an = any(k[x] in tb.K[x] for x in tb.K)
    hit_po += po; hit_any += an
print(dict(file='second_impl_fixtures_v1.2.jsonl', n=n, tb72_premise_order_key=hit_po, tb72_any_key=hit_any))
