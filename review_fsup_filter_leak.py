import json, glob, os, itertools, collections, gzip
R = os.path.expanduser('~/review/frontier-supply')
# ---- my own renaming class: parse, then min over atom permutations of (sorted set of premises, conclusion)
def parse(toks, i):
    t = toks[i]
    if t == '(':
        if toks[i+1] == '~':
            a, j = parse(toks, i+2); assert toks[j] == ')'; return ('~', a), j+1
        a, j = parse(toks, i+1); op = toks[j]; b, k = parse(toks, j+1); assert toks[k] == ')'; return (op, a, b), k+1
    if t == '~':
        a, j = parse(toks, i+1); return ('~', a), j
    return t, i+1
def show(f):
    if isinstance(f, str): return f
    if f[0] == '~': return f'(~{show(f[1])})'
    return f'({show(f[1])}{f[0]}{show(f[2])})'
def rn(f, m):
    if isinstance(f, str): return m.get(f, f)
    return (f[0],) + tuple(rn(x, m) for x in f[1:])
ATOMS = ['P', 'Q', 'R', 'S']
def split_thm(thm):
    lhs, rhs = thm.split('|-'); toks = lhs.split(); prem = []; i = 0
    while i < len(toks):
        f, i = parse(toks, i); prem.append(f)
        if i < len(toks): assert toks[i] == ','; i += 1
    return prem, parse(rhs.split(), 0)[0]
def cls(thm):
    prem, c = split_thm(thm); best = None
    for p in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, p))
        k = '|'.join(sorted({show(rn(x, m)) for x in prem})) + '=>' + show(rn(c, m))
        best = k if best is None or k < best else best
    return best
def thm_of(r):
    if r.get('thm'): return r['thm']
    p = r['prompt'][4:-4]; a, b = p.split(' SEQ '); return a.strip() + ' |- ' + b.strip()
# ---- filter pass rates
tot = collections.Counter(); bysrc = collections.defaultdict(collections.Counter); byround = collections.defaultdict(collections.Counter)
byseed = {}; byop = collections.defaultdict(collections.Counter)
kept_thms = []
for s in range(6):
    d = f'{R}/artifacts/fsup/la_S_s{s}'; c_seed = collections.Counter()
    for r in range(1, 9):
        for l in open(f'{d}/cands_{r}.jsonl'):
            c = json.loads(l); n = c['n_ok']; cl = 'zero' if n == 0 else 'pass' if n <= 8 else 'easy'
            for C in (tot, bysrc[c['source']], byround[r], c_seed, byop[c['source'] + ':' + c['op']]): C[cl] += 1; C['made'] += 1
            if cl == 'pass': kept_thms.append((s, r, c))
    byseed[s] = c_seed
f = lambda C: f"{C['pass']}/{C['made']} = {100*C['pass']/C['made']:.1f}% (zero {100*C['zero']/C['made']:.1f}%, easy {100*C['easy']/C['made']:.1f}%)"
print('ALL', f(tot))
for k, C in sorted(bysrc.items()): print(' src', k, f(C))
for k, C in sorted(byop.items()): print(' op', k, f(C))
for k, C in sorted(byround.items()): print(' round', k, f(C))
for k, C in sorted(byseed.items()): print(' seed', k, f(C))
# consistency: cands kept vs supply_found names
for s in range(6):
    d = f'{R}/artifacts/fsup/la_S_s{s}'
    names = {json.loads(l)['name'] for l in open(f'{d}/supply_found_8.jsonl')}
    kept = {c['name'] for ss, r, c in kept_thms if ss == s}
    sf = [json.loads(l) for l in open(f'{d}/supply_found_8.jsonl')]
    print(f's{s}: kept {len(kept)} names-in-supply_found {len(names)} equal={names == kept} proofs {len(sf)}')
# ---- disjointness
evalf = ['data/fsup/lp2_91.jsonl', 'data/fsup/rr600_13_16.jsonl', 'data/ladder/transfer_long2.jsonl', 'data/ladder/transfer_long2_calib.jsonl',
         'data/ladder/transfer_long_rr600.jsonl', 'data/ladder/transfer_long_ge17.jsonl', 'data/ladder/transfer_long.jsonl',
         'data/ladder/transfer.jsonl', 'data/heldout.jsonl', 'data/p2/heldout.jsonl', 'targets/validation_36.jsonl']
E = {}
for fn in evalf:
    p = f'{R}/{fn}'
    if os.path.exists(p): E[fn] = {cls(thm_of(json.loads(l))) for l in open(p) if l.strip()}
    else: print('missing', fn)
train = {'supply_kept(all S seeds)': {cls(c['thm']) for _, _, c in kept_thms},
         'supply_candidates(all)': set(),
         'rl_targets': {cls(thm_of(json.loads(l))) for l in open(f'{R}/data/ladder/rl_targets.jsonl')},
         'train_k12': {cls(thm_of(json.loads(l))) for l in gzip.open(f'{R}/_rev/train_k12.jsonl.gz', 'rt')}}
for s in range(6):
    for r in range(1, 9):
        for l in open(f'{R}/artifacts/fsup/la_S_s{s}/cands_{r}.jsonl'): train['supply_candidates(all)'].add(cls(json.loads(l)['thm']))
print()
print('train set', *[os.path.basename(e) for e in E], sep='\t')
for tn, T in train.items():
    print(f'{tn} ({len(T)})', *[len(T & ec) for ec in E.values()], sep='\t')
json.dump({'kept': [(s, r, c['name'], c['thm'], c['source'], c['op'], c.get('n_lines'), c['n_ok']) for s, r, c in kept_thms]},
          open(f'{R}/_rev/kept.json', 'w'))
