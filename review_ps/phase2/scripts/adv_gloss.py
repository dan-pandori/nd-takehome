"""C6 gloss shares, root (psub) vs any instance (sub), from the executor's K12 labels (= reviewer's per R2) and the
reviewer's theorem labels. Counts only."""
import gzip, json
from collections import Counter
W = '/home/dan/work/proof-strategies/artifacts/ps/labels/k12.jsonl.gz'
T = '/home/dan/review/proof-strategies/review_ps/out/thm_k12.jsonl.gz'
D = Counter()
for le, lt in zip(gzip.open(W, 'rt'), gzip.open(T, 'rt')):
    a = json.loads(le); t = json.loads(lt)
    assert a['i'] == t['i']
    if a['pri'] == 'cases':
        D['ca.n'] += 1
        D['ca.inc'] += t['inc']
        D['ca.root_redundant'] += 'cases.redundant' in a['psub']
        D['ca.any_redundant'] += 'cases.redundant' in a['sub']
    if a['pri'] == 'contradiction':
        D['co.n'] += 1
        for k in ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free'):
            D['co.root.' + k] += ('contradiction.' + k) in a['psub']
            D['co.any.' + k] += ('contradiction.' + k) in a['sub']
        D['co.inc'] += t['inc']
n = D['ca.n']; m = D['co.n']
print(dict(D))
print('cases: inc %.2f root_red %.2f any_red %.2f' % (100*D['ca.inc']/n, 100*D['ca.root_redundant']/n, 100*D['ca.any_redundant']/n))
print('#10: ' + ' '.join('%s root %.2f any %.2f' % (k, 100*D['co.root.'+k]/m, 100*D['co.any.'+k]/m) for k in ('vacuous','scaffolded','neg_goal','free','pointless')))
