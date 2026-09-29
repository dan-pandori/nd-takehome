# Reviewer's own renaming-class key: premises as a sorted multiset, atoms renamed; minimum over all atom permutations
# (so neither premise order nor atom names matter).  F (falsum) is not an atom.
import json, itertools, re, sys
ATOMS = ['P', 'Q', 'R', 'S', 'T', 'U']
def key(thm):
    lhs, rhs = thm.split('|-')
    prem = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    toks = set(re.findall(r'\b[A-Z]\b', thm)) - {'F'}
    at = sorted(toks)
    best = None
    for perm in itertools.permutations(ATOMS[:len(at)]):
        m = dict(zip(at, perm))
        f = lambda s: re.sub(r'\b[A-Z]\b', lambda x: m.get(x.group(), x.group()), s)
        k = (tuple(sorted(f(p) for p in prem)), f(rhs.strip()))
        best = k if best is None or k < best else best
    return best
def keys(fn, lim=None):
    out = set()
    for i, l in enumerate(open(fn)):
        if lim and i >= lim: break
        out.add(key(json.loads(l)['thm']))
    return out
W = '/home/dan/work/results-registry/data/'
tr = keys('/tmp/rrrev/src/train_depth3_f0_a1.jsonl'); print('train classes', len(tr), flush=True)
ev = {'rr_heldout200 (heldout[:200])': keys(W + 'p2/heldout.jsonl', 200), 'rr_transfer40': keys(W + 'ladder/transfer.jsonl', 40),
      'rr_targets40': keys(W + 'ladder/rl_targets.jsonl', 40), 'heldout (full, smoke eval_set 500)': keys(W + 'p2/heldout.jsonl', 500),
      'coverage (transfer[:2])': keys(W + 'ladder/transfer.jsonl', 2)}
for k, v in ev.items(): print('%-38s %4d classes, shared with train: %d' % (k, len(v), len(v & tr)))
print('targets40 vs heldout200:', len(ev['rr_targets40'] & ev['rr_heldout200 (heldout[:200])']), ' targets40 vs transfer40:', len(ev['rr_targets40'] & ev['rr_transfer40']),
      ' transfer40 vs heldout200:', len(ev['rr_transfer40'] & ev['rr_heldout200 (heldout[:200])']))
# negative control: a renamed + premise-permuted training theorem must collide
t = json.loads(open('/tmp/rrrev/src/train_depth3_f0_a1.jsonl').readline())['thm']
m = str.maketrans('PQRS', 'SRQP'); print('control: renamed train thm in train set?', key(t.translate(m)) in tr)
