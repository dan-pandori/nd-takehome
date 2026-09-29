import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, class_key
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
def keys(fn):
    return collections.Counter(class_key(r['prompt']) if 'prompt' in r else None for r in rd(fn))
def keys_k12(fn):
    c = collections.Counter()
    for r in rd(fn):
        p = r.get('prompt')
        if p is None:
            lhs, rhs = r['thm'].split('|-'); p = 'THM ' + lhs.strip() + ' SEQ ' + rhs.strip() + ' PRF'
        c[class_key(p)] += 1
    return c
train = {'train_k12': keys_k12(f'{B}/data/kh/train_k12.jsonl.gz'), 'ladder_rl_targets': keys(f'{B}/data/ladder/rl_targets.jsonl')}
evals = {'rr600': keys(f'{B}/data/ladder/transfer_long_rr600.jsonl'), 'ge17': keys(f'{B}/data/ladder/transfer_long_ge17.jsonl'),
         'orig_transfer': keys(f'{B}/data/ladder/transfer.jsonl'), 'p2_heldout': keys(f'{B}/data/p2/heldout.jsonl')}
out = {}
for tn, tk in train.items():
    for en, ek in evals.items():
        inter = set(tk) & set(ek)
        out[f'{tn} x {en}'] = {'train_classes': len(tk), 'eval_classes': len(ek), 'shared_classes': len(inter),
                               'eval_items_in_shared': sum(ek[k] for k in inter)}
        print(tn, en, out[f'{tn} x {en}'], flush=True)
json.dump(out, open(f'{B}/rv/splits.json', 'w'), indent=1)
