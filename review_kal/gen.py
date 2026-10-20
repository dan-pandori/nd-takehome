#!/usr/bin/env python3
"""E5 recount: the generalisation sets' construction (G1 / G2 / G3) re-checked with own code, and the pre-registered
"generalises" rule applied to my own numbers (out/free.json, out/solve.json).

Rule (pre-registration): KAL-D's rate >= 0.7 x its in-distribution rate at the same atom count (greedy success on the
TF set, here weighted by the set's own atom mix) AND above the control's pass@32 by more than the MDD -> generalises;
< 0.3 x -> does not; between -> partially.  KAL-D's "rate" is read as its greedy success (the rule's comparator).

  python3 review_kal/gen.py -> out/gen.json, stdout
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
D = os.path.join(kc.ROOT, 'data')
res = {}

# ---- construction checks
k12 = list(kc.rows(os.path.join(D, 'kh', 'train_k12.jsonl')))
k12_keys = set()
k12_sizes = []
for r in k12:
    p, g = kc.sequent(r)
    k12_keys.add(kc.key_inv(p, g))
    k12_sizes.append(sum(kc.size(kc.parse(x)) for x in p + [g]))
k12_sizes.sort()
k12_fsizes = [kc.size(kc.parse(x)) for r in k12 for x in sum(map(lambda t: [*t[0], t[1]], [kc.sequent(r)]), [])]
k12_fdepth = max(kc.fdepth(kc.parse(x)) for r in k12 for x in sum(map(lambda t: [*t[0], t[1]], [kc.sequent(r)]), []))
res['k12_total_size'] = {'p99': k12_sizes[int(0.99 * len(k12_sizes))], 'max': k12_sizes[-1], 'per_formula_max': max(k12_fsizes),
                         'per_formula_depth_max': k12_fdepth, 'n': len(k12), 'max_prem': max(len(kc.sequent(r)[0]) for r in k12)}
print('K12', res['k12_total_size'], flush=True)

held = {r['name']: r for r in kc.rows(os.path.join(D, 'p2', 'heldout.jsonl'))}
c = collections.Counter()
for r in kc.rows(os.path.join(D, 'kalmar', 'g1_premises.jsonl')):
    p, g = kc.sequent(r)
    o = held[r['orig']]
    po, go = kc.sequent(o)
    c[f'n_prem={len(p)}'] += 1
    c['valid'] += kc.valid([kc.parse(x) for x in p], kc.parse(g))
    c['goal_same'] += g == go
    rest = list(p)
    sub = True
    for x in po:
        if x in rest:
            rest.remove(x)
        else:
            sub = False
    c['orig_premises_kept'] += sub
    c['orig_2or3_prem'] += len(po) in (2, 3)
    oat = set(kc.atoms_in([kc.parse(x) for x in po + [go]]))
    c['distractors_own_atoms'] += all(set(kc.atoms_in([kc.parse(x)])) <= oat for x in rest)
    c['not_in_k12'] += kc.key_inv(p, g) not in k12_keys
res['g1_checks'] = dict(c)
print('G1', dict(c), flush=True)

c = collections.Counter(); g2bin = {}
for r in kc.rows(os.path.join(D, 'kalmar', 'g2_large.jsonl')):
    p, g = kc.sequent(r)
    fs = [kc.parse(x) for x in p + [g]]
    tot = sum(kc.size(f) for f in fs)
    b = '40-49' if 40 <= tot <= 49 else '50-59' if 50 <= tot <= 59 else '60-79' if 60 <= tot <= 79 else 'out'
    g2bin[r['name']] = b
    c[f'bin={b}'] += 1
    c['bin_matches_stored'] += b == r['bin'] and tot == r['total_size']
    c['valid'] += kc.valid(fs[:-1], fs[-1])
    c['le3_prem'] += len(p) <= 3
    c['not_in_k12'] += kc.key_inv(p, g) not in k12_keys
    c['above_k12_p99'] += tot > res['k12_total_size']['p99']
    c['above_k12_max'] += tot > res['k12_total_size']['max']
res['g2_checks'] = dict(c)
print('G2', dict(c), flush=True)

names = [l.strip() for l in open(os.path.join(D, 'coe', 'sigma_heldout_strict.txt')) if l.strip()]
g3 = list(kc.rows(os.path.join(D, 'kalmar', 'g3_classical.jsonl')))
res['g3_checks'] = {'n_file': len(names), 'n_set': len(g3), 'same_names': sorted(names) == sorted(r['name'] for r in g3),
                    'not_in_k12': sum(kc.key_inv(*kc.sequent(r)) not in k12_keys for r in g3)}
print('G3', res['g3_checks'], flush=True)

# ---- verdicts
F = json.load(open(os.path.join(OUT, 'free.json')))
S = json.load(open(os.path.join(OUT, 'solve.json')))
atoms_of = {}
for fn in ('g1_premises.jsonl', 'g2_large.jsonl', 'g3_classical.jsonl', 'hand_proved_14_kal_sl.jsonl', 'ge17_kal_sl.jsonl', 'long2_kal_sl.jsonl'):
    for r in kc.rows(os.path.join(D, 'kalmar', fn)):
        atoms_of[(fn, r['name'])] = kc.kalmar(r['prompt'])['n_atoms']


def in_dist(model, mix):
    """greedy success on tf1200 at the set's atom mix"""
    by = F[f'{model}__tf1200_greedy']['by']
    tot = sum(mix.values())
    return sum(n * by[f'atoms={a}']['valid'] / by[f'atoms={a}']['n'] for a, n in mix.items() if f'atoms={a}' in by) / tot


def greedy_rate(model, read, names=None):
    """greedy success of `model` on read `read` (optionally restricted to names); also the set's atom mix"""
    path = F[f'{model}__{read}_greedy']['in']
    fn = os.path.basename(path)
    rows = list(kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'free', f'{model}__{read}_greedy.rows.jsonl.gz')))
    if names is not None:
        rows = [r for r in rows if r['name'] in names]
    mix = collections.Counter(atoms_of[(fn, r['name'])] for r in rows)
    return sum(r['valid'] for r in rows) / len(rows), mix, len(rows)


def ctl_p32(seed, file, names=None, supplied=False):
    if supplied:
        rows = list(kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'free', f'ctl_s{seed}__g1_supplied_k32.rows.jsonl.gz')))
        per = collections.defaultdict(list)
        for r in rows:
            per[r['name']].append(r['valid'])
        return sum(any(v) for v in per.values()) / len(per)
    rows = [r for r in kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'eval', f'ctl_s{seed}_plain_k32.rows.jsonl.gz'))
            if r['file'] in file and (names is None or r['name'] in names)]
    return sum(r['n_ok'] > 0 for r in rows) / len(rows)


V = {}
tests = [('G1b', 'g1_supplied', None, 'g1', True), ('G3', 'g3_classical', None, ['g3_classical'], False),
         ('hand_proved_14', 'hand_proved_14', None, ['hand_proved_14'], False)]
for b in ('40-49', '50-59', '60-79'):
    tests.append((f'G2 {b}', 'g2_large', {n for n, x in g2bin.items() if x == b}, ['g2_large'], False))
for arm in ('kalD', 'kalC', 'kalDA'):
    for (lab, read, names, cfile, sup) in tests:
        for s in range(3):
            m = f'{arm}_s{s}'
            if f'{m}__{read}_greedy' not in F:
                continue
            rate, mix, n = greedy_rate(m, read, names)
            ind = in_dist(m, mix)
            cp = ctl_p32(s, cfile, names, sup)
            ratio = rate / ind if ind else None
            verdict = 'generalises' if ratio >= 0.7 and rate > cp else 'does not' if ratio < 0.3 else 'partially'
            V[f'{lab}|{m}'] = {'n': n, 'greedy': round(rate, 4), 'in_dist_same_atoms': round(ind, 4), 'ratio': round(ratio, 3),
                               'ctl_p32_same_seed': round(cp, 4), 'verdict': verdict}
    # >= 17: ge17 + long2 greedy reads pooled
    for s in range(3):
        m = f'{arm}_s{s}'
        if f'{m}__ge17_greedy' not in F:
            continue
        r1, mx1, n1 = greedy_rate(m, 'ge17'); r2, mx2, n2 = greedy_rate(m, 'long2')
        rate = (r1 * n1 + r2 * n2) / (n1 + n2); mix = mx1 + mx2
        ind = in_dist(m, mix)
        cp = (ctl_p32(s, ['transfer_long_ge17']) * n1 + ctl_p32(s, ['transfer_long2']) * n2) / (n1 + n2)
        ratio = rate / ind
        verdict = 'generalises' if ratio >= 0.7 and rate > cp else 'does not' if ratio < 0.3 else 'partially'
        V[f'ge17_91|{m}'] = {'n': n1 + n2, 'greedy': round(rate, 4), 'in_dist_same_atoms': round(ind, 4), 'ratio': round(ratio, 3),
                             'ctl_p32_same_seed': round(cp, 4), 'verdict': verdict}
res['verdicts'] = V
for k, v in V.items():
    print(f'{k:28s}', v)
json.dump(res, open(os.path.join(OUT, 'gen.json'), 'w'), indent=1)
