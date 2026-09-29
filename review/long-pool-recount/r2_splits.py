"""long-pool review, part 2: renaming-class disjointness of transfer_long (+ >=17 file) against every training /
evaluation file I can find.  Two keys, both mine:
  rkey    atoms renamed by first appearance, premise order kept (the project's convention);
  skey    invariant to atom renaming AND premise order (min over the 24 atom permutations of sorted premises + concl).
Also counts lines per file that carry neither `prompt` nor `thm` (a silent skip would hide overlaps)."""
import json, gzip, glob, os, sys, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv import prompt_parts

W = os.path.expanduser('~/review/long-pool')
J = lambda f: [json.loads(l) for l in open(f) if l.strip()]
pool = J(W + '/data/ladder/transfer_long.jsonl'); ge17 = J(W + '/data/ladder/transfer_long_ge17.jsonl')
PERMS = [dict(zip('PQRS', p)) for p in itertools.permutations('PQRS')]


def parts_of(rec):
    if 'prompt' in rec:
        return prompt_parts(rec['prompt'])
    if 'thm' in rec:
        l, r = rec['thm'].split('|-')
        return prompt_parts('THM ' + l.strip() + ' SEQ ' + r.strip() + ' PRF') if l.strip() else prompt_parts('THM SEQ ' + r.strip() + ' PRF')
    return None


def rkey(prems, c):
    m = {}; out = []
    for x in (' , '.join(prems) + ' |- ' + c).split():
        if x in 'PQRS' and len(x) == 1:
            if x not in m: m[x] = 'abcd'[len(m)]
            out.append(m[x])
        else:
            out.append(x)
    return ' '.join(out)


def sig(prems, c):
    f = lambda s: ' '.join('X' if (len(x) == 1 and x in 'PQRS') else x for x in s.split())
    return (tuple(sorted(f(p) for p in prems)), f(c))


def skey(prems, c):
    best = None
    for m in PERMS:
        g = lambda s: ' '.join(m.get(x, x) if len(x) == 1 else x for x in s.split())
        k = (tuple(sorted(g(p) for p in prems)), g(c))
        if best is None or k < best:
            best = k
    return best


P = {}
for tag, recs in (('pool', pool), ('ge17', ge17)):
    for r in recs:
        pr, c = parts_of(r); P.setdefault(tag, []).append((rkey(pr, c), skey(pr, c), sig(pr, c), r['name']))
PR = {x[0] for t in P for x in P[t]}; PS = {x[1] for t in P for x in P[t]}; PSIG = {x[2] for t in P for x in P[t]}
R = {'internal': {
    'pool_rkey_distinct': len({x[0] for x in P['pool']}), 'pool_skey_distinct': len({x[1] for x in P['pool']}),
    'ge17_rkey_distinct': len({x[0] for x in P['ge17']}), 'pool_ge17_skey_overlap': len({x[1] for x in P['pool']} & {x[1] for x in P['ge17']}),
    'executor_key_equals_mine_rkey_up_to_letters': None}}
# files
files = set()
for pat in ('data/**/*.jsonl', 'data/**/*.jsonl.gz'):
    files |= set(glob.glob(W + '/' + pat, recursive=True))
files = {f for f in files if '/data/lp/' not in f and 'transfer_long' not in f}
files |= set(glob.glob('/tmp/longpool/excl/*')) | {'/tmp/longpool/pool_long.jsonl', '/tmp/longpool/raw_textbook.jsonl'}
files |= set(glob.glob(os.path.expanduser('~/nd-takehome/data/p2/train_*.jsonl')))
files |= {W + '/targets/validation_36.jsonl'}
out = {}
for fn in sorted(files):
    op = gzip.open if fn.endswith('.gz') else open
    n = nokey = hr = hs = 0; hit_names = set()
    with op(fn, 'rt') as f:
        for l in f:
            if not l.strip():
                continue
            n += 1
            try:
                pc = parts_of(json.loads(l))
            except Exception:
                pc = None
            if pc is None:
                nokey += 1; continue
            pr, c = pc
            if rkey(pr, c) in PR:
                hr += 1
            if sig(pr, c) in PSIG and skey(pr, c) in PS:
                hs += 1
    out[fn.replace(W + '/', '').replace(os.path.expanduser('~'), '~')] = {'records': n, 'no_prompt_or_thm': nokey, 'rkey_hits': hr, 'skey_hits': hs}
    print(fn, out[list(out)[-1]], flush=True)
R['files'] = out
R['total_rkey_hits'] = sum(v['rkey_hits'] for v in out.values()); R['total_skey_hits'] = sum(v['skey_hits'] for v in out.values())
os.makedirs('out', exist_ok=True)
json.dump(R, open('out/r2_splits.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in R.items() if k != 'files'}, indent=1))
