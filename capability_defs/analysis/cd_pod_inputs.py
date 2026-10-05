#!/usr/bin/env python3
"""capability-defs: build the pod jobs' input files (pure python; VPS).  Deterministic.

  python3 capability_defs/analysis/cd_pod_inputs.py

J2  data/cd/j2/s<S>_c<NN>.jsonl  : each seed's J2 theorems (artifacts/cd/j1/sets.json), 8 per chunk, read at k 16,384
    data/cd/j2/s<S>_cal.jsonl    : each seed's 30 calibration theorems, read at k 4,096
J3  data/cd/h250_gt.jsonl        : holdout250 with min_lines = n_lines (guided_eval's length field)
J4  data/cd/j4/lem_transfer40.jsonl : the 40 premise-free A v ~A instances of transfer (never trained on by any ladder;
                                   6 are holdout250 theorems), the evaluation set
    data/cd/j4/mix_{A0,A4,A16,C16}.jsonl : fine-tune mixes = demos x 4 (rl_weight, as the ladder) + the same 20,000 K12
                                   replay records (random.Random(0)); A0 = replay only; A4 / A16 = 4 / 16 excluded-middle
                                   demonstrations (s1's r16 found set on rl_targets, one shortest proof per theorem);
                                   C16 = 16 non-excluded-middle rl_targets proofs (s1's found set) matched on L_true
    data/cd/j4/demos.json        : which theorems and proofs went into each mix
"""
import collections, itertools, json, os, random, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wj(p, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')


def parts(prompt):
    m = re.match(r'THM\s*(.*?)\s*SEQ (.*) PRF', prompt)
    return m.group(1).strip(), m.group(2).strip()


def strip(s):
    t = s.split()
    while len(t) >= 2 and t[0] == '(' and t[-1] == ')':
        d, ok = 0, True
        for i, x in enumerate(t):
            d += (x == '(') - (x == ')')
            if d == 0 and i < len(t) - 1:
                ok = False
                break
        if not ok:
            break
        t = t[1:-1]
    return ' '.join(t)


def split_top(s, op):
    t, d = s.split(), 0
    for i, x in enumerate(t):
        d += (x == '(') - (x == ')')
        if x == op and d == 0:
            return ' '.join(t[:i]), ' '.join(t[i + 1:])
    return None


def is_lem(prompt):
    """premise-free A v ~A (A any formula)."""
    prem, concl = parts(prompt)
    if prem:
        return False
    sp = split_top(strip(concl), 'v')
    if not sp:
        return False
    a, b = strip(sp[0]), strip(sp[1])
    return b.startswith('~ ') and strip(b[2:]) == a


def canon(prompt):
    """renaming class: atom permutations (F is falsum, not an atom), premise order ignored."""
    prem, concl = parts(prompt)
    prems = [p.strip() for p in prem.split(',')] if prem else []
    best = None
    for perm in itertools.permutations('PQRS'):
        mp = dict(zip('PQRS', perm))
        f = lambda s: ' '.join(mp.get(x, x) for x in s.split())
        key = (tuple(sorted(f(p) for p in prems)), f(concl))
        best = key if best is None or key < best else best
    return best


def main():
    os.chdir(ROOT)
    pools = {**{r['name']: dict(r, n_lines=r.get('reference_lines')) for r in rj('data/bs/textbook72.jsonl')},
             **{r['name']: r for r in rj('data/bs/holdout250.jsonl')}}
    sets = json.load(open('artifacts/cd/j1/sets.json'))
    for s, d in sets.items():
        j2 = d['J2']
        for c in range(0, len(j2), 8):
            wj(f'data/cd/j2/s{s}_c{c // 8:02d}.jsonl', [pools[n] for n in j2[c:c + 8]])
        wj(f'data/cd/j2/s{s}_cal.jsonl', [pools[n] for n in d['CAL']])
        print(f's{s}: J2 {len(j2)} theorems in {(len(j2) + 7) // 8} chunks; CAL {len(d["CAL"])}')
    wj('data/cd/h250_gt.jsonl', [dict(r, min_lines=r['n_lines']) for r in rj('data/bs/holdout250.jsonl')])
    # J4
    tb_classes = {canon(r['prompt']) for r in rj('data/bs/textbook72.jsonl')}
    targets = {r['name']: r for r in rj('data/ladder/rl_targets.jsonl')}
    transfer = rj('data/ladder/transfer.jsonl')
    ev = [r for r in transfer if is_lem(r['prompt'])]
    assert len(ev) == 40 and not any(canon(r['prompt']) in tb_classes for r in ev)
    wj('data/cd/j4/lem_transfer40.jsonl', ev)
    lem = json.load(open('artifacts/cd/in/lem_found16.json'))['targets']['1']      # s1's r16 found set, LEM targets
    by = collections.defaultdict(list)
    for x in lem:
        by[x['name']].append(x)
    names = sorted(n for n in by if canon(targets[n]['prompt']) not in tb_classes)
    pick16 = random.Random(0).sample(names, 16)
    shortest = lambda xs: min(xs, key=lambda x: (x['written'] or 99, x['proof']))
    demo = {n: shortest(by[n]) for n in pick16}
    # control: s1's found_16 proofs of non-LEM rl_targets, L_true matched one-for-one (stream the big file once)
    want = collections.Counter(targets[n]['L_true'] for n in pick16)
    cand = collections.defaultdict(list)
    keep = {n for n, r in targets.items() if r.get('schema') != 'excluded_middle' and not is_lem(r['prompt'])
            and canon(r['prompt']) not in tb_classes and r['L_true'] in want}
    with open(os.path.expanduser('~/review/rc_data/s1/found_16.jsonl')) as f:
        for line in f:
            r = json.loads(line)
            if r['name'] in keep:
                cand[r['name']].append(r)
    rng = random.Random(1)
    ctrl = {}
    for L, k in sorted(want.items()):
        pool = sorted(n for n in cand if targets[n]['L_true'] == L)
        for n in rng.sample(pool, k):
            ctrl[n] = shortest(cand[n])
    k12 = rj(os.path.expanduser('~/work/best-state/data/kh/train_k12.jsonl'))
    replay = [{'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']} for x in random.Random(0).sample(k12, 20000)]
    arms = {'A0': {}, 'A4': {n: demo[n] for n in pick16[:4]}, 'A16': demo, 'C16': ctrl}
    for arm, dm in arms.items():
        rows = [{'prompt': targets[n]['prompt'], 'proof': x['proof'], 'n_lines': x['written']}
                for n, x in dm.items() for _ in range(4)] + replay
        wj(f'data/cd/j4/mix_{arm}.jsonl', rows)
        print(f'J4 {arm}: {len(dm)} demonstration theorems, {len(rows)} records')
    json.dump({arm: {n: {'prompt': targets[n]['prompt'], 'L_true': targets[n]['L_true'], 'proof': x['proof'],
                         'written': x['written'], 'round_found': x.get('round')} for n, x in dm.items()}
               for arm, dm in arms.items()}, open('data/cd/j4/demos.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
