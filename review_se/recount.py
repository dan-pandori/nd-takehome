#!/usr/bin/env python3
"""Reviewer recount for run state-env (independent of se_analysis.py / state_ladder_ei.py bookkeeping).
Run from a copy of the run repo: python3 review_se/recount.py > review_se/recount.json"""
import json, glob, os, re, collections, itertools, sys

def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]

# ---------- canonical form of a sequent: min over the 24 bijections of {P,Q,R,S}; F is falsum ----------
ATOMS = 'PQRS'
PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]
def split_thm(thm):
    lhs, rhs = thm.split('|-')
    prem = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    return [p for p in prem if p], rhs.strip()
def canon(thm):
    prem, c = split_thm(thm)
    best = None
    for m in PERMS:
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = (tuple(sorted(f(p) for p in prem)), f(c))
        if best is None or k < best: best = k
    return best
def canon_set(prem_multiset=True):
    pass

# ---------- my own start-index normaliser for ND proofs ----------
def mynorm(proof):
    m = {}
    out = []
    for t in proof.split():
        if re.fullmatch(r'N\d+', t):
            if t not in m: m[t] = f'N{len(m)+1}'
            out.append(m[t])
        else:
            out.append(t)
    return ' '.join(out)

def nlines(proof):
    return sum(1 for s in proof.split(' ; ') if re.match(r'\s*N\d+', s))

transfer = rd('data/ladder/transfer.jsonl'); targets = rd('data/ladder/rl_targets.jsonl')
heldout = rd('data/p2/heldout.jsonl')
Lt = {r['name']: r['n_lines'] for r in transfer}
src = {r['name']: (r['source'], r['schema']) for r in transfer}
Ltg = {r['name']: r['n_lines'] for r in targets}

def lstar(solved_L, need=5):
    return max([L for L in range(2, 30) if sum(1 for x in solved_L if x >= L) >= need], default=0)

out = {'ladders': {}, 'heldout': {}}
for d in sorted(glob.glob('artifacts/se/la_*')):
    name = os.path.basename(d); rows = {}
    prev = None
    for r in range(1, 9):
        fn = f'{d}/found_transfer_{r}.jsonl'
        if not os.path.exists(fn): continue
        F = rd(fn)
        by = collections.defaultdict(set)
        raw_dupes = 0
        for x in F:
            assert x['name'] in Lt, x['name']
            assert x['thm'] == next(t for t in [None] if True) or True
            k = mynorm(x['proof'])
            if k in by[x['name']]: raw_dupes += 1
            by[x['name']].add(k)
        solved = set(by)
        if prev is not None:
            lost = prev - solved
        else:
            lost = set()
        sl = [Lt[n] for n in solved]
        ge = {L: sum(1 for x in sl if x >= L) for L in range(7, 15)}
        tb = [n for n in solved if src[n][0] == 'textbook']
        # targets cumulative
        Ft = rd(f'{d}/found_{r}.jsonl') if os.path.exists(f'{d}/found_{r}.jsonl') else []
        tsol = {x['name'] for x in Ft}
        rows[r] = {'transfer_solved': len(solved), 'lstar': lstar(sl), 'ge': ge, 'ge13_names': sorted((n, Lt[n]) for n in solved if Lt[n] >= 13),
                   'textbook_solved': len(tb), 'textbook_schemata': len({src[n][1] for n in tb}),
                   'distinct_norm_proofs': sum(len(v) for v in by.values()), 'rows': len(F), 'dupes_after_mynorm': raw_dupes,
                   'lost_vs_prev': len(lost),
                   'by_L': {L: sum(1 for x in sl if x == L) for L in range(7, 15)},
                   'targets_solved': len(tsol), 'targets_lstar': lstar([Ltg[n] for n in tsol]),
                   'written_max': max((x['written'] for x in F), default=0),
                   'written_recount_mismatch': sum(1 for x in F if nlines(x['proof']) != x['written'])}
        # round-json reported (for comparison only)
        rj = f'{d}/round_{r}.json'
        if os.path.exists(rj):
            J = json.load(open(rj))
            rows[r]['reported'] = {'solved': J['transfer_cum']['solved'], 'lstar': J['transfer_cum']['lstar'],
                                   'targets_solved': J['targets_cum']['solved'],
                                   'heldout_greedy': J['heldout_greedy']['rate'], 'transfer_greedy': J['transfer_greedy']['solved']}
            e = J.get('env', {})
            ee = e.get('env_end', {}); tot = sum(ee.values()) or 1
            st = e.get('env_steps', {}); ns = sum(st.values()) or 1
            dh = e.get('action_declen_hist', {}); nd = sum(dh.values()) or 1
            rows[r]['env'] = {'end': ee, 'syntax_frac': ee.get('syntax', 0) / tot, 'trunc_attempt_frac': ee.get('truncated', 0) / tot,
                              'mean_steps': sum(int(k) * v for k, v in st.items()) / ns,
                              'declen_ge256_frac': sum(v for k, v in dh.items() if int(k) >= 256) / nd,
                              'declen_max': max((int(k) for k in dh), default=None),
                              'peak_alloc_gb': e.get('peak_alloc_gb'), 'fail_reason': e.get('env_fail_reason'),
                              'step_cap_frac': ee.get('step_cap', 0) / tot,
                              'names_defined': e.get('names_defined'), 'names_renamed': e.get('names_renamed')}
        prev = solved
    # equal attempts: tried totals from alloc
    al = sorted(glob.glob(f'{d}/alloc_*.json'), key=lambda s: int(re.findall(r'(\d+)\.json', s)[0]))
    if al:
        A = json.load(open(al[-1]))
        rows['tried_total_targets'] = sum(A['tried'].values()); rows['alloc_last'] = os.path.basename(al[-1])
    out['ladders'][name] = rows

for fn in sorted(glob.glob('artifacts/se/heldout_*.jsonl')):
    R = rd(fn)
    assert len(R) == 5000
    byL = collections.defaultdict(lambda: [0, 0])
    reasons = collections.Counter()
    for r in R:
        ok = bool(r['proofs'])
        byL[r['n_lines']][0] += ok; byL[r['n_lines']][1] += 1
        for x in r['reasons']: reasons[x.split()[0] if x else x] += 1
        if not ok and r['fail_example']:
            reasons['FE:' + ' '.join(r['fail_example'].split()[:2])] += 1
    names = [r['name'] for r in R]
    assert names == [h['name'] for h in heldout]
    out['heldout'][os.path.basename(fn)] = {'solved': sum(v[0] for v in byL.values()), 'rate': sum(v[0] for v in byL.values()) / 5000,
                                            'by_L': {L: v[0] / v[1] for L, v in sorted(byL.items())},
                                            'fail_examples': dict(collections.Counter(' '.join(r['fail_example'].split()[:2]) for r in R if not r['proofs'] and r['fail_example']).most_common(8))}

# ---------- splits: renaming-class disjointness ----------
train = rd('data/p2/train_depth3_f0_a1.jsonl')
ctr = {canon(r['thm']) for r in train}
pools = {'heldout': heldout, 'transfer': transfer, 'rl_targets': targets}
sp = {}
for k, P in pools.items():
    sp[f'train_vs_{k}'] = sum(1 for r in P if canon(r['thm']) in ctr)
ct = {canon(r['thm']) for r in transfer}
sp['rl_targets_vs_transfer'] = sum(1 for r in targets if canon(r['thm']) in ct)
sp['heldout_vs_transfer'] = sum(1 for r in heldout if canon(r['thm']) in ct)
sp['n'] = {k: len(v) for k, v in pools.items()} | {'train': len(train)}
# the validation_36 and test files
for f in ['targets/validation_36.jsonl']:
    if os.path.exists(f):
        V = rd(f); sp['train_vs_val36'] = sum(1 for r in V if canon(r['thm'].strip()) in ctr)
out['splits'] = sp
json.dump(out, sys.stdout, indent=1, default=str)
