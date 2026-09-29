"""long-pool review, part 1: the pool.  Own label derivation from the raw staged minlen files, bins, sources, timeouts,
contradictory premises, label-proof Lean re-check (own translator), own term size.  Writes out/r1_pool.json."""
import json, collections, itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv import parse, prompt_parts
from rlean import translate, check, my_size, Bad

W = os.path.expanduser('~/review/long-pool')
LP = W + '/data/lp'
os.makedirs('out', exist_ok=True)
J = lambda f: [json.loads(l) for l in open(f) if l.strip()]
pool = J(W + '/data/ladder/transfer_long.jsonl')
ge17 = J(W + '/data/ladder/transfer_long_ge17.jsonl')
rr600 = J(W + '/data/ladder/transfer_long_rr600.jsonl')
R = {}

# ---- own labels from raw stage files
lab = {}          # (chunk, prompt) -> ('L', L, proof) | ('unk', stage) | ('ge17',)
tout = collections.Counter(); entered = collections.Counter()
for c in ['g1', 'g2', 'g3', 'g4', 'tb']:
    src = J(f'{LP}/{c}.jsonl'); entered[(c, 'gen')] = len(src)
    reached = {r['prompt'] for r in src}
    for b in (10, 12, 14, 16):
        rows = J(f'{LP}/{c}_ml{b}.jsonl')
        entered[(c, b)] = len(rows)
        nxt = set()
        for r in rows:
            p = r['prompt']
            assert p in reached, (c, b)
            if r.get('timeout') or r.get('error'):
                lab[(c, p)] = ('unk', b); tout[(c, b)] += 1
            elif r['min_lines_ub'] is not None:
                lab[(c, p)] = ('L', r['min_lines_ub'], r['proof'], b)
            elif b == 16:
                lab[(c, p)] = ('ge17',)
            else:
                nxt.add(p)
        # every no-proof-no-timeout record must be the next stage's input, and nothing else
        if b < 16:
            nin = {json.loads(l)['prompt'] for l in open(f'{LP}/{c}_ml{b + 2}.jsonl')}
            assert nin == nxt, (c, b, len(nin), len(nxt), len(nin - nxt), len(nxt - nin))
        reached = nxt
R['entered'] = {f'{c}|{b}': n for (c, b), n in entered.items()}
R['timeouts'] = {f'{c}|{b}': n for (c, b), n in tout.items()}
st = collections.Counter()
for b in (10, 12, 14, 16):
    st[f'bound{b}_in'] = sum(entered[(c, b)] for c in ['g1', 'g2', 'g3', 'g4', 'tb'])
    st[f'bound{b}_to'] = sum(tout[(c, b)] for c in ['g1', 'g2', 'g3', 'g4', 'tb'])
R['timeouts_by_stage'] = dict(st)
avail = collections.Counter()
for (c, p), v in lab.items():
    src = 'tb' if c == 'tb' else 'gen'
    if v[0] == 'L' and v[1] >= 11:
        avail[(v[1], src)] += 1
    elif v[0] == 'ge17':
        avail[('ge17', src)] += 1
R['labelled_ge11_before_dedup_excl'] = {f'{k[0]}|{k[1]}': n for k, n in sorted(avail.items(), key=str)}

# ---- pool records vs own labels
mism = []
for r in pool + ge17:
    v = lab.get((r['chunk'], r['prompt']))
    if r in ge17 or r['L_true'] is None:
        if v != ('ge17',):
            mism.append((r['name'], 'ge17', v))
        continue
    if v is None or v[0] != 'L' or v[1] != r['L_true'] or v[2] != r['minlen_proof']:
        mism.append((r['name'], r['L_true'], v and v[:2]))
    L = parse(r['minlen_proof'])
    if len(L) != r['L_true']:
        mism.append((r['name'], 'nlines', len(L)))
R['label_mismatches'] = mism[:20]; R['n_label_mismatch'] = len(mism)

bins = collections.Counter(r['L_true'] for r in pool)
bysrc = collections.Counter((r['L_true'], r['source']) for r in pool)
bysch = collections.Counter((r['L_true'], r['schema']) for r in pool if r['source'] == 'textbook')
R['pool_n'] = len(pool); R['ge17_n'] = len(ge17); R['rr600_n'] = len(rr600)
R['bins'] = dict(sorted(bins.items()))
R['bins_source'] = {f'{L}|{s}': n for (L, s), n in sorted(bysrc.items())}
R['bins_schema'] = {f'{L}|{s}': n for (L, s), n in sorted(bysch.items())}
R['chunk_by_bin'] = {f'{L}|{c}': n for (L, c), n in sorted(collections.Counter((r['L_true'], r['chunk']) for r in pool).items())}
R['rr600_bins'] = dict(sorted(collections.Counter(r['L_true'] for r in rr600).items()))
pn = {r['name']: r for r in pool}
R['rr600_not_in_pool_or_changed'] = sum(1 for r in rr600 if pn.get(r['name'], {}).get('prompt') != r['prompt'])
R['rr600_bin_counts_by_source'] = {f'{L}|{s}': n for (L, s), n in sorted(collections.Counter((r['L_true'], r['source']) for r in rr600).items())}
R['ge17_by_chunk'] = dict(collections.Counter(r['chunk'] for r in ge17))
R['minlen_bound_vs_L'] = {f'{L}|{b}': n for (L, b), n in sorted(collections.Counter((r['L_true'], r['minlen_bound']) for r in pool).items())}
R['gen_lines_by_bin'] = {L: [min(r['gen_lines'] for r in pool if r['L_true'] == L and r['gen_lines']),
                             sorted(r['gen_lines'] for r in pool if r['L_true'] == L and r['gen_lines'])[len([1 for r in pool if r['L_true'] == L and r['gen_lines']]) // 2],
                             max(r['gen_lines'] for r in pool if r['L_true'] == L and r['gen_lines'])] for L in sorted(bins)}


# ---- contradictory (unsatisfiable) premises, by my own truth-table evaluator
def ev(fs, a):
    t = fs.split()

    def go(i):
        x = t[i]
        if x == '(':
            if t[i + 1] == '~':
                v, j = go(i + 2); return (not v), j + 1
            u, j = go(i + 1); op = t[j]; w, j = go(j + 1)
            return {'&': u and w, 'v': u or w, '>': (not u) or w}[op], j + 1
        if x == 'F':
            return False, i + 1
        return a[x], i + 1
    return go(0)[0]


def unsat_prem(prompt):
    prems, _ = prompt_parts(prompt)
    for vals in itertools.product([False, True], repeat=4):
        a = dict(zip('PQRS', vals))
        if all(ev(p, a) for p in prems):
            return False
    return bool(prems)


def valid(prompt):
    prems, c = prompt_parts(prompt)
    for vals in itertools.product([False, True], repeat=4):
        a = dict(zip('PQRS', vals))
        if all(ev(p, a) for p in prems) and not ev(c, a):
            return False
    return True


R['unsat_premises_by_bin'] = dict(collections.Counter(r['L_true'] for r in pool if unsat_prem(r['prompt'])))
R['unsat_premises_ge17'] = sum(unsat_prem(r['prompt']) for r in ge17)
R['not_valid_pool'] = sum(not valid(r['prompt']) for r in pool)
R['not_valid_ge17'] = sum(not valid(r['prompt']) for r in ge17)
R['n_prem_by_bin'] = {f'{L}|{k}': n for (L, k), n in sorted(collections.Counter((r['L_true'], len(prompt_parts(r['prompt'])[0])) for r in pool).items())}

# ---- Lean re-check of every label proof, own term size
srcs = []
for r in pool:
    try:
        srcs.append(translate(r['prompt'], r['minlen_proof']))
    except Bad as e:
        srcs.append(None)
res = check(srcs)
R['label_lean_ok'] = sum(ok for ok, _ in res)
R['label_lean_rej'] = [(pool[i]['name'], why) for i, (ok, why) in enumerate(res) if not ok][:30]
R['executor_label_lean_ok_field'] = dict(collections.Counter(r.get('label_lean_ok') for r in pool))
ms = [my_size(r['prompt'], r['minlen_proof']) for r in pool]
R['my_size_eq_theirs'] = sum(m == r['label_term_size'] for m, r in zip(ms, pool))
R['size_diff_hist'] = dict(collections.Counter(m - r['label_term_size'] for m, r in zip(ms, pool)))
R['size_by_bin'] = {}
for L in sorted(bins):
    xs = sorted(m for m, r in zip(ms, pool) if r['L_true'] == L)
    R['size_by_bin'][L] = {'min': xs[0], 'median': xs[len(xs) // 2], 'max': xs[-1], 'mean': round(sum(xs) / len(xs), 2)}
json.dump(R, open('out/r1_pool.json', 'w'), indent=1, default=str)
print(json.dumps(R, indent=1, default=str))
