#!/usr/bin/env python3
"""Reviewer recount (mcts-a), part 3, written for this review:
  splits: renaming-class disjointness (premise order free, all 24 atom permutations) between every training / tuning
          file (rl_targets, all of K12 train, tune200) and every evaluation pool; tune200 provenance; rrQ100 provenance.
  proofs: my own pruner -> written / pruned line counts and term size (inference nodes of the pruned proof; PR / AS 0,
          ORE 3, DN 3, others 1) per arm, pool, checkpoint (search: the one proof per solved tree; sample: the shortest
          by term size per solved theorem), and paired on theorems both arms solve.
  search: along each found proof, the hardest step (lowest prior; ties -> lowest log pi), its depth and prior rank;
          nodes per solved tree.
  compute: registry rows vs per-job files (gpu_seconds = wall clock).
Output: r3.json"""
import json, os, glob, gzip, re, random, itertools, collections, statistics, hashlib
W = os.path.expanduser('~/review/mcts-a'); E = f'{W}/artifacts/mcts'; HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: [json.loads(l) for l in (gzip.open(f, 'rt') if f.endswith('.gz') else open(f)) if l.strip()]
out = {}

# ---------------------------------------------------------------- renaming classes
PERMS = [dict(zip('PQRS', p)) for p in itertools.permutations('PQRS')]
def parts(prompt):
    m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', prompt.strip())
    lhs = m.group(1).strip()
    return ([p.strip() for p in lhs.split(' , ')] if lhs else []), m.group(2).strip()
def rkey(prompt):
    prem, c = parts(prompt)
    best = None
    for pm in PERMS:
        f = lambda s: ' '.join(pm.get(t, t) for t in s.split())
        k = (tuple(sorted(set(f(p) for p in prem))), f(c))
        best = k if best is None or k < best else best
    return best
train = {'rl_targets': rd(f'{W}/data/ladder/rl_targets.jsonl'), 'K12_train': rd('/tmp/train_k12.jsonl.gz'),
         'tune200': rd(f'{W}/data/mcts/tune200.jsonl')}
evals = {p: rd(f'{W}/data/mcts/{p}.jsonl') for p in ('tb72', 'h250', 'rrQ100', 'long2')}
for s in range(3):
    evals[f'groupC_s{s}'] = rd(f'{W}/data/mcts/groupC_s{s}.jsonl')
ek = {p: {rkey(r['prompt']) for r in R} for p, R in evals.items()}
sp = {}
for t, R in train.items():
    tk = collections.Counter(rkey(r['prompt']) for r in R)
    for p, K in ek.items():
        sp[f'{t} x {p}'] = sum(1 for k in K if k in tk)
out['splits'] = dict(sizes={**{k: len(v) for k, v in train.items()}, **{k: len(v) for k, v in evals.items()}}, overlaps=sp)

# tune200: rl_targets theorems, held out by md5 % 10 == 0, L_true >= 9
rl = {r['name']: r for r in train['rl_targets']}
held = lambda n: int(hashlib.md5(n.encode()).hexdigest(), 16) % 10 == 0
tn = train['tune200']
out['tune200'] = dict(n=len(tn), in_rl=sum(r['name'] in rl for r in tn), heldout=sum(held(r['name']) for r in tn),
                      Ltrue_ge9=sum(rl[r['name']]['L_true'] >= 9 for r in tn if r['name'] in rl),
                      all_heldout_Lge9=sum(1 for r in train['rl_targets'] if held(r['name']) and r['L_true'] >= 9))
# rrQ100 from transfer_long_rr600 at L_true 13-16
rr = rd(f'{W}/data/ladder/transfer_long_rr600.jsonl')
lk = 'L_true' if 'L_true' in rr[0] else 'len'
band = [r for r in rr if 13 <= r[lk] <= 16]
q = evals['rrQ100']; bn = {r['name'] for r in band}
rep = {}
for how, sel in (('sample', lambda: random.Random(20261002).sample(band, 100)),
                 ('shuffle', lambda: (lambda b: (random.Random(20261002).shuffle(b), b[:100])[1])(list(band)))):
    rep[how] = {r['name'] for r in sel()} == {r['name'] for r in q}
out['rrQ100'] = dict(rr600=len(rr), band_13_16=len(band), q=len(q), q_in_band=sum(r['name'] in bn for r in q), reproduced=rep)

# ---------------------------------------------------------------- my pruner / term size
def parse_nd(proof):
    L = []
    for s in proof.split(' ; '):
        s = s.strip()
        if not s or s in ('QED', 'QE'): continue
        m = re.fullmatch(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)', s)
        L.append(dict(i=int(m[1]), r=m[4], refs=[int(x[1:]) for x in m[5].split()]))
    return L
def measure(proof):
    L = parse_nd(proof); by = {x['i']: x for x in L}
    keep, stack = set(), [L[-1]['i']]
    while stack:
        i = stack.pop()
        if i in keep: continue
        keep.add(i); x = by[i]
        refs = list(x['refs'])
        if x['r'] in ('IMPI', 'NEGI'):                    # a box: its hypothesis and conclusion
            pass
        stack += refs
    w = {'PR': 0, 'AS': 0, 'ORE': 3, 'DN': 3}
    return dict(written=len(L), pruned=len(keep), term=sum(w.get(by[i]['r'], 1) for i in keep))

recs = collections.defaultdict(dict)       # job -> name -> measure
for f in sorted(glob.glob(f'{E}/eval/*.jsonl') + glob.glob(f'{E}/eval_x10/*.jsonl')):
    lab = os.path.relpath(f, E)[:-6]; arm = lab.rsplit('__', 1)[1]
    if 'tune200' in lab: continue
    for r in rd(f):
        if not r['solved']: continue
        if arm == 'sample':
            ms = [measure(p) for p in r['proofs']]
            recs[lab][r['name']] = min(ms, key=lambda m: (m['term'], m['pruned']))
        else:
            recs[lab][r['name']] = measure(r['proof'])
def med(v): return statistics.median(v) if v else None
ts = {}
for lab, d in recs.items():
    ts[lab] = dict(n=len(d), written=med([m['written'] for m in d.values()]), pruned=med([m['pruned'] for m in d.values()]),
                   term=med([m['term'] for m in d.values()]))
out['termsize_by_job'] = ts
# pooled per (ckpt, pool, arm) over seeds, and paired search - sample on common solves
pooled = collections.defaultdict(list); paired = collections.defaultdict(list)
for lab, d in recs.items():
    m = re.fullmatch(r'eval/s(\d)_(pend|r8)__(\w+?)__(sample|prior|value)', lab)
    if not m: continue
    pooled[(m[2], m[3], m[4])] += list(d.values())
    if m[4] != 'sample':
        sd = recs.get(f'eval/s{m[1]}_{m[2]}__{m[3]}__sample', {})
        for n, x in d.items():
            if n in sd:
                paired[(m[2], m[3], m[4])].append((x['term'] - sd[n]['term'], x['pruned'] - sd[n]['pruned']))
out['termsize_pooled'] = {'/'.join(k): dict(n=len(v), pruned_med=med([x['pruned'] for x in v]), term_med=med([x['term'] for x in v]),
                                             term_mean=round(statistics.mean([x['term'] for x in v]), 2))
                          for k, v in sorted(pooled.items())}
out['termsize_paired_search_minus_sample_shortest'] = {'/'.join(k): dict(n=len(v), term_mean=round(statistics.mean([a for a, _ in v]), 2),
                                                                          pruned_mean=round(statistics.mean([b for _, b in v]), 2),
                                                                          frac_search_longer=round(sum(a > 0 for a, _ in v) / len(v), 3))
                                                       for k, v in sorted(paired.items()) if v}

# ---------------------------------------------------------------- search paths
hs = collections.defaultdict(list)
for f in sorted(glob.glob(f'{E}/eval/*.jsonl') + glob.glob(f'{E}/eval_x10/*.jsonl')):
    lab = os.path.relpath(f, E)[:-6]; arm = lab.rsplit('__', 1)[1]
    if arm == 'sample' or 'tune' in lab: continue
    m = re.search(r's\d_(pend|r8)__(\w+?)__', lab); key = ('x10/' if 'x10' in lab else '') + f'{m[2]}/{arm}'
    for r in rd(f):
        if not r['solved'] or not r['path']: continue
        p = r['path']
        h = min(p, key=lambda x: (x['prior'], x['logpi']))
        nontriv = [x for x in p if x['n_children'] > 1]
        hs[key].append(dict(depth=h['depth'], rank=h['rank'], prior=h['prior'], nodes=r['nodes'], plen=len(p),
                            n_branch=len(nontriv), rank1_all=all(x['rank'] == 1 for x in p)))
out['hardstep'] = {k: dict(n=len(v), depth_ge2=sum(x['depth'] >= 2 for x in v), depth_med=med([x['depth'] for x in v]),
                           rank_med=med([x['rank'] for x in v]), rank_hist=dict(collections.Counter(min(x['rank'], 9) for x in v)),
                           prior_med=med([x['prior'] for x in v]), nodes_med=med([x['nodes'] for x in v]),
                           all_rank1=sum(x['rank1_all'] for x in v))
                   for k, v in sorted(hs.items())}

# ---------------------------------------------------------------- compute rows
reg = rd(glob.glob(f'{W}/artifacts/mcts-a/registry/*.jsonl')[0])
chk = []
for r in reg:
    if r['metric'] != 'gpu_seconds' or not r.get('source', '').startswith('artifacts/mcts/eval'): continue
    J = json.load(open(f'{W}/{r["source"]}'))
    w = J.get('wall_s') or J.get('stats', {}).get('wall_s')
    chk.append((r['source'], r['value'], round(w, 1)))
out['registry_gpu_seconds'] = dict(n=len(chk), mismatch=[c for c in chk if abs(c[1] - c[2]) > 0.2][:10],
                                   metrics=dict(collections.Counter(r['metric'] for r in reg)),
                                   arms=dict(collections.Counter(r['arm'] for r in reg)))
json.dump(out, open(f'{HERE}/r3.json', 'w'), indent=1, default=list)
for k, v in out.items():
    if k != 'termsize_by_job': print(k, json.dumps(v, default=list)[:2500])
