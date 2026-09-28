"""Renaming-class disjointness between the Stage-1 set and every evaluation pool (reviewer's own canonicaliser:
atoms renamed in order of first appearance, minimised over premise orderings)."""
import json, itertools, hashlib, collections, rvlib
def canon(thm):
    lhs, rhs = thm.split('|-')
    # split premises at top-level commas
    prems, depth, cur = [], 0, []
    for t in lhs.split():
        if t == ',' and depth == 0:
            prems.append(' '.join(cur)); cur = []; continue
        depth += (t == '(') - (t == ')'); cur.append(t)
    if cur: prems.append(' '.join(cur))
    best = None
    for perm in itertools.permutations(prems) if len(prems) <= 5 else [prems]:
        m = {}; out = []
        for t in (' , '.join(perm) + ' |- ' + rhs.strip()).split():
            if t.isalpha() and t.isupper() and len(t) == 1 and t != 'F':
                m.setdefault(t, 'x%d' % len(m)); out.append(m[t])
            else: out.append(t)
        s = ' '.join(out)
        best = s if best is None or s < best else best
    return best
TR = '/home/dan/nd-takehome/data/p2/train_depth3_f0_a1.jsonl'
tr = set(); n = 0; d3 = 0; bad = 0; md5 = hashlib.md5()
for l in open(TR, 'rb'):
    md5.update(l); r = json.loads(l); n += 1; tr.add(canon(r['thm']))
    try: d3 += rvlib.is_d3(r['proof'])
    except ValueError: bad += 1
res = dict(train=TR, train_md5=md5.hexdigest(), train_n=n, train_classes=len(tr), train_depth3_reviewer=d3, train_parse_fail=bad, pools={})
for f in ['targets_depth3', 'transfer_depth3', 'heldout']:
    P = [json.loads(l) for l in open('../data/p2/%s.jsonl' % f)]
    cs = [canon(r['thm']) for r in P]
    res['pools'][f] = dict(n=len(P), classes=len(set(cs)), overlap_with_train=sum(c in tr for c in cs))
pc = {f: set(canon(json.loads(l)['thm']) for l in open('../data/p2/%s.jsonl' % f)) for f in ['targets_depth3', 'transfer_depth3', 'heldout']}
res['pool_pairs'] = {a + '&' + b: len(pc[a] & pc[b]) for a, b in itertools.combinations(pc, 2)}
print(json.dumps(res, indent=1)); json.dump(res, open('splits.json', 'w'), indent=1)
