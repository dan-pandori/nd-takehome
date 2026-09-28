# reviewer's own renaming-class normaliser: min over the 24 permutations of P,Q,R,S of the theorem string (premise order kept)
import json, gzip, itertools, collections
perms = list(itertools.permutations('PQRS'))
def canon(thm):
    t = ' '.join(thm.split())
    best = None
    for p in perms:
        m = dict(zip('PQRS', p))
        s = ''.join(m.get(ch, ch) for ch in t)
        if best is None or s < best: best = s
    return best
def load(fn):
    op = gzip.open if fn.endswith('.gz') else open
    return {canon(json.loads(l)['thm']) for l in op(fn, 'rt')}
S = {'train_a1': load('review_lp/data/train_a1.jsonl.gz'), 'rl_targets': load('data/ladder/rl_targets.jsonl'),
     'transfer': load('data/ladder/transfer.jsonl'), 'heldout': load('review_lp/data/heldout.jsonl')}
print({k: len(v) for k, v in S.items()})
for a, b in [('train_a1', 'transfer'), ('train_a1', 'heldout'), ('rl_targets', 'transfer'), ('rl_targets', 'heldout'), ('train_a1', 'rl_targets'), ('transfer', 'heldout')]:
    print(a, b, 'overlap classes', len(S[a] & S[b]))
