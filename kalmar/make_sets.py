#!/usr/bin/env python3
"""Evaluation sets for run kalmar-pretrain (VPS, no GPU).  Every output record carries its sl Kalmár proof.

  python3 kalmar/make_sets.py --out data/kalmar [--seed 0]

  tf1200_kal_sl.jsonl     teacher-forced / free-generation set: 1,200 theorems of data/p2/heldout.jsonl (150 one-atom,
                          350 each with 2 / 3 / 4 atoms), none in K12's premise-order-invariant classes
  val300_kal_sl.jsonl     the first 300 of tf1200 (training-time validation loss only; selects nothing)
  g1_premises.jsonl       G1: 200 p2/heldout theorems with 2-3 premises (disjoint from tf1200 and K12) plus random
                          distractor premises over their own atoms -> 100 with 4 premises, 100 with 5
  g2_large.jsonl          G2: generated valid sequents, total size (nodes, ¬ counted) in [40,49] / [50,59] / [60,79],
                          80 per bin, <= 3 premises, <= 4 atoms, none in K12's classes
  g3_classical.jsonl      G3: the 106 strict sigma-covered held-out classical theorems of create-or-elicit
                          (data/coe/sigma_heldout_strict.txt, records from data/ladder/transfer.jsonl)
  <set>_kal_sl.jsonl      the sl Kalmár proof of every theorem of the standard read sets (holdout250, rr600, ge17,
                          long2, the release files, textbook72) -- algorithm lengths for the breakdowns
  sets_report.json        counts, atom / premise mixes, algorithm proof lengths, size bins, filters applied

Constraints on generated theorems: the algorithm's proof has <= 1,000 actions and its largest canonical name is <= 32
(the sampler's name base is <= 32 and lean_seq has 64 name tokens).
"""
import argparse, collections, itertools, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kalmar
from nd2lean import parse_prompt
from lean_tok import fnd
from state_env import decompose

ATOMS = ('P', 'Q', 'R', 'S')
PERMS = list(itertools.permutations(ATOMS))


def rename(f, m):
    if f[0] == 'atom':
        return ('atom', m[f[1]])
    if f[0] == 'bot':
        return f
    return (f[0],) + tuple(rename(g, m) for g in f[1:])


def pkey(prem, goal):
    """premise-order-invariant renaming-class key: min over the 24 atom bijections of (sorted premises, goal)."""
    best = None
    for p in PERMS:
        m = dict(zip(ATOMS, p))
        k = (tuple(sorted(fnd(rename(x, m)) for x in prem)), fnd(rename(goal, m)))
        if best is None or k < best:
            best = k
    return best


def size(f):
    return 1 if f[0] in ('atom', 'bot') else 1 + sum(size(g) for g in f[1:])


def depth(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + max(depth(g) for g in f[1:])


def prompt_of(prem, goal):
    return 'THM ' + ' , '.join(fnd(p) for p in prem) + (' ' if prem else '') + 'SEQ ' + fnd(goal) + ' PRF'


def kal(prompt):
    """-> dict of the sl proof's numbers (or None if the builder / decomposition fails)."""
    b = kalmar.build(prompt, 'sl')
    if b is None:
        return None
    steps, toks, env = decompose(prompt, b['proof'], canon=True)
    assert len(steps) == b['n_actions']
    return {'kal_proof': b['proof'], 'kal_lines': b['n_lines'], 'kal_actions': b['n_actions'], 'n_atoms': b['n_atoms'],
            'kal_max_state': max(len(s) for s, a, h in steps), 'kal_max_name':
                max((int(t[1:]) for t in toks if t[:1] == 'n' and t[1:].isdigit()), default=0),
            'kal_pair_tokens': sum(len(s) + len(a) + 1 for s, a, h in steps), 'kal_tags': b['tags']}


def ok_limits(k):
    return k is not None and k['kal_actions'] <= 1000 and k['kal_max_name'] <= 32


# ---- random formulas (G1 distractors, G2) ----
def rand_formula(rng, atoms, n):
    """a uniformly-shaped random formula with exactly n nodes over `atoms` (¬ ∧ ∨ → equally likely where they fit)."""
    if n == 1:
        return ('atom', rng.choice(atoms))
    if n == 2:
        return ('not', ('atom', rng.choice(atoms)))
    op = rng.choice(['not', 'and', 'or', 'imp'])
    if op == 'not':
        return ('not', rand_formula(rng, atoms, n - 1))
    k = rng.randint(1, n - 2)
    return (op, rand_formula(rng, atoms, k), rand_formula(rng, atoms, n - 1 - k))


def mask(f):
    """truth table over the 16 valuations of P, Q, R, S as a 16-bit int."""
    if f[0] == 'atom':
        i = ATOMS.index(f[1])
        return sum(1 << v for v in range(16) if (v >> i) & 1)
    if f[0] == 'bot':
        return 0
    if f[0] == 'not':
        return 0xFFFF & ~mask(f[1])
    a, b = mask(f[1]), mask(f[2])
    return a & b if f[0] == 'and' else a | b if f[0] == 'or' else 0xFFFF & (~a | b)


def summ(xs):
    xs = sorted(xs)
    return {'n': len(xs), 'mean': round(sum(xs) / len(xs), 1), 'p50': xs[len(xs) // 2], 'max': xs[-1]} if xs else {}


def write(fn, rows):
    with open(fn, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/kalmar')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--k12', default='data/kh/train_k12.jsonl')
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    rep = {'seed': a.seed}

    k12keys = set()
    for l in open(a.k12):
        p, g = parse_prompt(json.loads(l)['prompt'])
        k12keys.add(pkey(p, g))
    rep['k12_classes'] = len(k12keys)
    print('K12 classes', len(k12keys), flush=True)

    # ---- tf1200 / val300 ----
    held = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
    by = collections.defaultdict(list)
    n_k12 = 0
    for r in held:
        p, g = parse_prompt(r['prompt'])
        r['_key'] = pkey(p, g)
        if r['_key'] in k12keys:
            n_k12 += 1
            continue
        by[len(kalmar.atoms_of(p + [g]))].append(r)
    rep['p2_heldout_in_k12_classes'] = n_k12
    want = {1: 150, 2: 350, 3: 350, 4: 350}
    tf, used = [], set()
    for na in (1, 2, 3, 4):
        pool = list(by[na])
        rng.shuffle(pool)
        tf += pool[:want[na]]
    rng.shuffle(tf)
    rows = []
    for r in tf:
        k = kal(r['prompt'])
        assert k is not None
        used.add(r['name'])
        rows.append({'name': r['name'], 'key': r['key'], 'prompt': r['prompt'], 'n_lines': r['n_lines'], 'n_prem': r['n_prem'],
                     'proof': k['kal_proof'], **{x: y for x, y in k.items() if x != 'kal_proof'}})
    write(f'{a.out}/tf1200_kal_sl.jsonl', rows)
    write(f'{a.out}/val300_kal_sl.jsonl', rows[:300])
    rep['tf1200'] = {'atoms': dict(collections.Counter(r['n_atoms'] for r in rows)),
                     'kal_actions': summ([r['kal_actions'] for r in rows]),
                     'kal_max_state': summ([r['kal_max_state'] for r in rows])}
    print('tf1200', rep['tf1200'], flush=True)

    # ---- G1: 4-5 premises ----
    psize = [s for s in range(3, 10)]
    cand = [r for na in (2, 3, 4) for r in by[na] if r['name'] not in used and r['n_prem'] in (2, 3)]
    rng.shuffle(cand)
    g1 = []
    for target in (4, 5):
        got = 0
        for r in cand:
            if got >= 100:
                break
            if r.get('_g1'):
                continue
            p, g = parse_prompt(r['prompt'])
            at = kalmar.atoms_of(p + [g])
            prem = list(p)
            tries = 0
            while len(prem) < target and tries < 50:
                tries += 1
                d = rand_formula(rng, at, rng.choice(psize))
                if d in prem or d == g:
                    continue
                prem.insert(rng.randint(0, len(prem)), d)
            if len(prem) < target:
                continue
            pr = prompt_of(prem, g)
            k = kal(pr)
            if not ok_limits(k):
                continue
            r['_g1'] = True
            got += 1
            g1.append({'name': f'g1_{target}p_{got:03d}', 'orig': r['name'], 'prompt': pr, 'n_prem': target,
                       'proof': k['kal_proof'], **{x: y for x, y in k.items() if x != 'kal_proof'}})
    write(f'{a.out}/g1_premises.jsonl', g1)
    rep['g1'] = {'n': len(g1), 'n_prem': dict(collections.Counter(r['n_prem'] for r in g1)),
                 'atoms': dict(collections.Counter(r['n_atoms'] for r in g1)),
                 'kal_actions': summ([r['kal_actions'] for r in g1]), 'kal_max_state': summ([r['kal_max_state'] for r in g1])}
    print('g1', rep['g1'], flush=True)

    # ---- G2: larger formulas ----
    bins = [(40, 49), (50, 59), (60, 79)]
    g2, seen = [], set()
    stats = collections.Counter()
    for lo, hi in bins:
        got = 0
        while got < 80:
            stats['tries'] += 1
            na = rng.choice([2, 3, 4, 4])
            at = list(ATOMS[:na]) if rng.random() < 0.5 else rng.sample(ATOMS, na)
            npr = rng.choice([1, 2, 3])
            tot = rng.randint(lo, hi)
            # split the total size over premises and goal (each >= 3 nodes)
            cuts = sorted(rng.sample(range(3, tot - 2), npr)) if tot - 5 >= npr else None
            if cuts is None:
                continue
            sizes = [b - c for b, c in zip(cuts + [tot], [0] + cuts)]
            if min(sizes) < 3:
                stats['bad_split'] += 1
                continue
            prem = [rand_formula(rng, at, s) for s in sizes[:-1]]
            m = 0xFFFF
            for p in prem:
                m &= mask(p)
            g = None
            for _ in range(400):
                cand_g = rand_formula(rng, at, sizes[-1])
                if m & ~mask(cand_g) & 0xFFFF == 0:
                    g = cand_g
                    break
            if g is None:
                stats['no_valid_goal'] += 1
                continue
            if g in prem or len(set(map(fnd, prem))) < len(prem):
                stats['trivial'] += 1
                continue
            if kalmar.atoms_of(prem + [g]) != sorted(set(at), key=ATOMS.index):
                stats['atoms_dropped'] += 1
                continue
            key = pkey(prem, g)
            if key in k12keys or key in seen:
                stats['dup'] += 1
                continue
            pr = prompt_of(prem, g)
            k = kal(pr)
            if not ok_limits(k):
                stats['over_limits'] += 1
                continue
            seen.add(key)
            got += 1
            g2.append({'name': f'g2_{lo}_{got:03d}', 'prompt': pr, 'bin': f'{lo}-{hi}', 'total_size': tot,
                       'max_size': max(size(f) for f in prem + [g]), 'max_depth': max(depth(f) for f in prem + [g]),
                       'n_prem': npr, 'consistent': m != 0, 'proof': k['kal_proof'],
                       **{x: y for x, y in k.items() if x != 'kal_proof'}})
    write(f'{a.out}/g2_large.jsonl', g2)
    rep['g2'] = {'n': len(g2), 'gen_stats': dict(stats)}
    for lo, hi in bins:
        rs = [r for r in g2 if r['bin'] == f'{lo}-{hi}']
        rep['g2'][f'{lo}-{hi}'] = {'atoms': dict(collections.Counter(r['n_atoms'] for r in rs)),
                                   'n_prem': dict(collections.Counter(r['n_prem'] for r in rs)),
                                   'inconsistent': sum(not r['consistent'] for r in rs),
                                   'max_depth': summ([r['max_depth'] for r in rs]),
                                   'kal_actions': summ([r['kal_actions'] for r in rs]),
                                   'kal_max_state': summ([r['kal_max_state'] for r in rs])}
    print('g2', json.dumps(rep['g2'])[:1500], flush=True)

    # ---- G3: classical (create-or-elicit strict sigma-covered held-out) ----
    names = [l.strip() for l in open('data/coe/sigma_heldout_strict.txt') if l.strip()]
    tr = {}
    for l in open('data/ladder/transfer.jsonl'):
        r = json.loads(l)
        tr[r['name']] = r
    g3 = []
    for nm in names:
        r = tr[nm]
        k = kal(r['prompt'])
        assert k is not None
        g3.append({'name': nm, 'prompt': r['prompt'], 'schema': r.get('schema'), 'L_true': r.get('L_true'),
                   'proof': k['kal_proof'], **{x: y for x, y in k.items() if x != 'kal_proof'}})
    write(f'{a.out}/g3_classical.jsonl', g3)
    rep['g3'] = {'n': len(g3), 'schema': dict(collections.Counter(r['schema'] for r in g3)),
                 'atoms': dict(collections.Counter(r['n_atoms'] for r in g3)),
                 'in_k12_classes': sum(pkey(*parse_prompt(r['prompt'])) in k12keys for r in g3),
                 'kal_actions': summ([r['kal_actions'] for r in g3])}
    print('g3', rep['g3'], flush=True)

    # ---- algorithm proofs of the standard read sets ----
    std = {'holdout250': 'data/bs/holdout250.jsonl', 'rr600': 'data/ladder/transfer_long_rr600.jsonl',
           'ge17': 'data/ladder/transfer_long_ge17.jsonl', 'long2': 'data/ladder/transfer_long2.jsonl',
           'candidate_v0': 'data/gt/candidate_v0.jsonl', 'candidate_v1': 'data/gt/candidate_v1.jsonl',
           'batch3': 'data/gt/batch3.jsonl', 'hand_proved_14': 'data/gt/hand_proved_14.jsonl',
           'textbook72': 'data/bs/textbook72.jsonl'}
    rep['std'] = {}
    for nm, fn in std.items():
        rows = []
        for l in open(fn):
            r = json.loads(l)
            k = kal(r['prompt'])
            assert k is not None, (nm, r.get('name'))
            p, g = parse_prompt(r['prompt'])
            if nm == 'textbook72':    # scoring only: no theorem, no proof, no tags in any file this run writes
                rows.append({'name': r.get('name'), 'n_prem': len(p),
                             **{x: k[x] for x in ('kal_lines', 'kal_actions', 'n_atoms', 'kal_max_state', 'kal_max_name',
                                                  'kal_pair_tokens')}})
                continue
            rows.append({'name': r.get('name'), 'prompt': r['prompt'], 'n_prem': len(p), 'proof': k['kal_proof'],
                         **{x: y for x, y in k.items() if x not in ('kal_proof',)},
                         **{x: r[x] for x in ('L_true', 'min_lines') if x in r}})
        write(f'{a.out}/{nm}_kal_sl.jsonl', rows)
        rep['std'][nm] = {'n': len(rows), 'atoms': dict(collections.Counter(r['n_atoms'] for r in rows)),
                          'n_prem': dict(collections.Counter(r['n_prem'] for r in rows)),
                          'kal_actions': summ([r['kal_actions'] for r in rows]),
                          'kal_max_state': summ([r['kal_max_state'] for r in rows]),
                          'kal_max_name': max(r['kal_max_name'] for r in rows)}
    print('std', json.dumps(rep['std'])[:2000], flush=True)
    json.dump(rep, open(f'{a.out}/sets_report.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
