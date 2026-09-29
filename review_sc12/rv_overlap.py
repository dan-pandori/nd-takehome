import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, class_key
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
k12 = collections.defaultdict(list)
for r in rd(f'{B}/data/kh/train_k12.jsonl.gz'):
    k12[class_key(r['prompt'])].append(r)
tg = collections.defaultdict(list)
for r in rd(f'{B}/data/ladder/rl_targets.jsonl'):
    tg[class_key(r['prompt'])].append(r)
for en, fn in (('orig', 'data/ladder/transfer.jsonl'), ('heldout', 'data/p2/heldout.jsonl')):
    for r in rd(f'{B}/{fn}'):
        k = class_key(r['prompt'])
        for src, D in (('k12', k12), ('rl_targets', tg)):
            for t in D.get(k, []):
                print(en, src, 'exact_key_equal=', t.get('key') == r.get('key'), '| eval:', r['thm'], '| train:', t['thm'], '| eval n_lines', r.get('n_lines'))
