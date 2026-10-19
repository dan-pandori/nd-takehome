"""Scan the uploaded (bucket-listed) data files that carry prompts for textbook72 classes (counts only)."""
import json, sys, os, re
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt, ParseError
from sealkey import TB72, keys
tb = TB72(path='/home/dan/review/proof-strategies/data/bs/textbook72.jsonl')
W = '/home/dan/work/proof-strategies/'
files = ['data/ps/nec/k12_nec594.checked.jsonl', 'data/ps/nec/k12_nec594.jsonl', 'data/ps/pod/k12_min990.jsonl',
         'data/ps/pod/k12_nec594.jsonl', 'data/ps/pod/tb_schema.jsonl', 'data/ps/search/k12_min990.checked.jsonl',
         'data/ps/search/k12_min990.jsonl', 'data/ps/search/tb_schema.checked.jsonl', 'data/ps/search/tb_schema.jsonl',
         'data/ps/validation/second_impl_fixtures_v1.2.jsonl', 'artifacts/ps/validation/second_impl_fixtures_v1.2.jsonl',
         'data/ps/validation/spot_a.jsonl', 'data/ps/validation/spot_b.jsonl', 'data/ps/validation/spot_c.jsonl',
         'data/ps/validation/spot_key.jsonl']
PR = re.compile(r'THM .*? PRF')
for f in files:
    p = W + f
    if not os.path.exists(p):
        print(f, 'missing locally'); continue
    n = hit = 0
    for l in open(p):
        for m in PR.findall(l):
            try:
                pp, cc = parse_prompt(m)
            except Exception:
                continue
            n += 1
            k = keys(pp, cc)
            hit += (k['po'] in tb.K['po'])
    print(f, 'prompts', n, 'tb72 premise-order-class hits', hit)
