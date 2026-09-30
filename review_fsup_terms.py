"""Reviewer's own term size: parse ND lines; size(PR)=size(AS)=1, size(R x)=size(x), else 1+sum(size(refs)) (tree size,
shared subproofs duplicated); dag = distinct reachable lines excluding R. Min over a theorem's accepted proofs."""
import json, glob, os, statistics as S, collections, sys
R = os.path.expanduser('~/review/frontier-supply')
def parse_nd(p):
    L = {}; last = None
    for seg in p.split(' ; '):
        seg = seg.strip()
        if seg == 'QED' or not seg: continue
        idx = int(seg.split()[0][1:]); rhs = seg.rsplit(' : ', 1)[1].split()
        L[idx] = (rhs[0], [int(x[1:]) for x in rhs[1:]]); last = idx
    return L, last
def sizes(p):
    L, last = parse_nd(p); memo = {}
    sys.setrecursionlimit(10000)
    def tree(i):
        if i in memo: return memo[i]
        rule, refs = L[i]
        v = 1 if rule in ('PR', 'AS') else tree(refs[0]) if rule == 'R' else 1 + sum(tree(j) for j in refs)
        memo[i] = v; return v
    seen = set()
    def dag(i):
        if i in seen: return
        rule, refs = L[i]
        if rule == 'R': return dag(refs[0])
        seen.add(i)
        for j in refs: dag(j)
    dag(last)
    return tree(last), len(seen), len(L)
lenof = {json.loads(l)['name']: json.loads(l)['L_true'] for l in open(f'{R}/data/fsup/rr600_13_16.jsonl')}
def arm_stats(pat):
    out = collections.defaultdict(list)
    for fn in sorted(glob.glob(f'{R}/artifacts/fsup/rr/{pat}__*.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            if not r['proofs']: continue
            L = r.get('L_true_lb') if '__lp2' in fn else lenof[r['name']]
            b = 'lp17' if L == 17 else 'lp18' if L and L >= 18 and '__lp2' in fn else f'rr{L}'
            ss = [sizes(p) for p in r['proofs']]
            out[b].append((min(s[0] for s in ss), min(s[1] for s in ss), min(s[2] for s in ss)))
    return out
for arm, pat in [('C', 'la_C_s*'), ('S', 'la_S_s*'), ('R', 'la_R_s*'), ('B', 'stage1_s*')]:
    st = arm_stats(pat)
    print(arm, '  '.join(f"{b}: n={len(v)} tree {S.median([x[0] for x in v])} dag {S.median([x[1] for x in v])} lines {S.median([x[2] for x in v])}"
                        for b, v in sorted(st.items())))
# supply training proofs vs rl_targets training proofs (S seeds)
sup = []; 
for fn in glob.glob(f'{R}/artifacts/fsup/la_S_s*/supply_found_8.jsonl'):
    for l in open(fn):
        r = json.loads(l); sup.append((sizes(r['proofs'] if 'proofs' in r else r['proof']), r['source'], r['ub']))
for src in 'ab':
    v = [x[0] for x in sup if x[1] == src]
    print(f'supply proofs src {src}: n={len(v)} median tree {S.median([t for t,_,_ in v])} dag {S.median([d for _,d,_ in v])} lines {S.median([n for _,_,n in v])}; lines>=17: {sum(n>=17 for *_,n in v)}; tree p90 {sorted(t for t,_,_ in v)[int(.9*len(v))]}')
rl = []
for fn in glob.glob(f'{R}/artifacts/fsup/la_S_s*/found_8.jsonl'):
    for l in open(fn):
        r = json.loads(l); rl.append(sizes(r['proof']))
print(f'rl_targets proofs (S): n={len(rl)} median tree {S.median([t for t,_,_ in rl])} dag {S.median([d for _,d,_ in rl])} lines {S.median([n for *_,n in rl])}; lines>=17 {sum(n>=17 for *_,n in rl)}')
