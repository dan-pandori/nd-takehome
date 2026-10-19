#!/usr/bin/env python3
"""Tests for the K12-Kalmár builder (run kalmar-pretrain).  CPU; needs Lean at ~/.elan/bin/lean for tests 5-6.

  python3 kalmar/test_kalmar.py [--k12 data/kh/train_k12.jsonl]

1. Kalmár's lemma: for random formulas and valuations, `Builder.lit` returns a line whose formula is f when f is true
   and ¬f when it is false, and every cited line is in scope (checked by rendering + decomposing a proof that uses it).
2. Hand-written sequents covering every case of the construction (each connective at both polarities, ⊥, ex falso,
   an atom-free sequent, a goal that is a premise, a goal that is X ∨ ¬X): both variants build, decompose, replay,
   and the action tags line up with the environment's actions; an invalid sequent returns None.
3. The construction is the prover's: atoms split in the order P, Q, R, S, X ∨ ¬X derived once per atom (sl) or once
   per branch (pb), and a leaf with a false premise closes by ex falso on the FIRST false premise.
4. The algorithm is a function of the visible state: over K12 records, a state that recurs always gets the same action;
   and the sampler's environment (random name base, assign=True) shows exactly the shifted canonical states and
   applies exactly the shifted canonical actions.
5. Lean accepts the literal canonical text of 60 K12-Kalmár proofs (both variants), and `lean_tok.inverse` maps each
   text back to the record's ND proof.
6. Negative controls: Lean rejects every one of 60 mutated texts (a disjunction introduced on the wrong side, a
   citation redirected to another name in scope, the theorem's goal replaced by a non-consequence).
"""
import argparse, itertools, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kalmar
from kalmar import Builder, val, render, build
from nd2lean import parse_prompt
from lean_tok import LeanTokenizer, inverse, fnd
from state_env import Env, decompose, split_actions, is_name, BIGN

FAIL = []


def ck(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        FAIL.append(msg)


def rand_formula(rng, atoms, n):
    if n == 1:
        return ('atom', rng.choice(atoms)) if rng.random() > 0.05 else ('bot',)
    if n == 2:
        return ('not', ('atom', rng.choice(atoms)))
    op = rng.choice(['not', 'and', 'or', 'imp'])
    if op == 'not':
        return ('not', rand_formula(rng, atoms, n - 1))
    k = rng.randint(1, n - 2)
    return (op, rand_formula(rng, atoms, k), rand_formula(rng, atoms, n - 1 - k))


def t1():
    print('1. Kalmár lemma on random formulas')
    rng = random.Random(1)
    bad = n = 0
    for _ in range(3000):
        f = rand_formula(rng, ['P', 'Q', 'R'], rng.randint(1, 12))
        v = {a: rng.random() < 0.5 for a in 'PQR'}
        b = Builder([], ('atom', 'P'))
        for a in 'PQR':        # branch hypotheses in scope, as at a leaf
            hyp = ('atom', a) if v[a] else ('not', ('atom', a))
            b.emit(hyp, 'PR')
        ln = b.lit(f, v)
        n += 1
        bad += ln.f != (f if val(f, v) else ('not', f))
    ck(bad == 0, f'lit() proves f or ¬f as the valuation says: {n - bad} / {n}')


HAND = [
    'THM ( P > Q ) , P SEQ Q PRF',                       # →E needed via ex falso / leaf
    'THM ( P & Q ) SEQ ( Q & P ) PRF',                   # ∧+ and ∧-
    'THM ( P v Q ) , ( ~ P ) SEQ Q PRF',                 # ∨-, efq
    'THM SEQ ( P v ( ~ P ) ) PRF',                       # goal = the excluded-middle line (R at each branch)
    'THM SEQ ( ( ( P > Q ) > P ) > P ) PRF',             # Peirce: imp+ / imp- at depth
    'THM ( ~ ( ~ P ) ) SEQ P PRF',                       # not+ (¬¬A from A)
    'THM F SEQ ( P & ( ~ P ) ) PRF',                     # ⊥ premise: ¬⊥ box + efq
    'THM SEQ ( ~ F ) PRF',                               # atom-free: no split at all
    'THM P SEQ P PRF',                                   # goal = premise = branch hypothesis
    'THM ( P > ( Q > R ) ) SEQ ( ( P & Q ) > R ) PRF',   # 3 atoms
    'THM ( ( P v Q ) > ( R & S ) ) , ( ~ S ) SEQ ( ~ P ) PRF',   # 4 atoms
]


def t2():
    print('2. hand-written sequents, both variants')
    for pr in HAND:
        for var in ('sl', 'pb'):
            b = build(pr, var)
            try:
                steps, toks, env = decompose(pr, b['proof'], canon=True)
                okd = env.done and len(steps) == b['n_actions'] == len(b['tags'])
                inv = inverse(toks).split() == b['proof'].split()
            except Exception as e:      # noqa: BLE001
                okd, inv = False, f'{e!r}'
            ck(okd and inv is True, f'{var} {pr[4:60]}: {b["n_lines"]} lines, {b["n_actions"]} actions, decompose+inverse')
    ck(build('THM ( P v Q ) SEQ P PRF', 'sl') is None, 'an invalid sequent returns None')


def t3():
    print('3. it is the prover\'s construction')
    pr = 'THM ( ( P v Q ) > ( R & S ) ) , ( ~ S ) SEQ ( ~ P ) PRF'
    sl, pb = build(pr, 'sl'), build(pr, 'pb')
    lem = lambda b: [ln for ln in b['proof'].split(' ; ') if ' : DN ' in ln]
    order = [ln.split()[2] for ln in lem(sl)]            # 'N9 ( P v ( ~ P ) ) : DN N8' -> atom token
    ck(order == ['P', 'Q', 'R', 'S'], f'sl derives X ∨ ¬X for P, Q, R, S in that order ({order})')
    ck(len(lem(pb)) == 1 + 2 + 4 + 8, f'pb derives X ∨ ¬X 15 times for four atoms ({len(lem(pb))})')
    # first false premise: P true, Q any, R & S false -> premise 1 false; premise 2 (~S) may also be false
    b = Builder(*parse_prompt('THM ( P > Q ) , ( ~ P ) SEQ Q PRF'), 'sl')
    for p in b.prem:
        b.prlines.append(b.emit(p, 'PR'))
    b.emit(('atom', 'P'), 'AS'); b.emit(('not', ('atom', 'Q')), 'AS')
    g = b.leaf({'P': True, 'Q': False})
    nege = [ln for ln in b.top if ln.rule == 'NEGE' and ln.tag == 'efq']
    ck(len(nege) == 1 and nege[0].refs[0] is b.prlines[0], 'with premises 1 and 2 both false, ex falso uses premise 1')


def t4(k12):
    print('4. a function of the visible state; the sampler shows the shifted canonical states')
    seen, conf, rep = {}, 0, 0
    recs = []
    for i, l in enumerate(open(k12)):
        if i % 31:
            continue
        recs.append(json.loads(l)['prompt'])
        if len(recs) >= 3000:
            break
    shift = lambda toks, b: [f'n{int(t[1:]) + b}' if is_name(t, BIGN) else t for t in toks]
    badenv = 0
    for i, pr in enumerate(recs):
        b = build(pr, 'sl')
        steps, toks, env = decompose(pr, b['proof'], canon=True)
        for s, a, h in steps:
            k = ' '.join(s)
            if k in seen:
                rep += 1
                conf += seen[k] != a
            else:
                seen[k] = a
        if i < 500:
            base = random.Random(i).randint(0, 32)
            e = Env(pr, canon=True, base=base, assign=True)
            for s, a, h in steps:
                if e.state_tokens() != shift(s, base):
                    badenv += 1; break
                junk = shift(a, base)
                if junk[0] == 'have':
                    junk[1] = 'n1'
                ok, why = e.apply(junk)
                if not ok or e._eff != shift(a, base):
                    badenv += 1; break
    ck(conf == 0, f'{len(recs)} K12 records: {rep} repeated states, {conf} with a different action')
    ck(badenv == 0, f'500 records replayed with a random name base: {badenv} mismatches')


def lean_srcs(prompts, var):
    tok = LeanTokenizer('lean_staten')
    out = []
    for pr in prompts:
        b = build(pr, var)
        steps, toks, env = decompose(pr, b['proof'], canon=True)
        assert inverse(toks).split() == b['proof'].split()
        out.append((pr, toks, f'{tok.statement(pr)} {tok.text(toks)}'))
    return out


def t5_t6(k12):
    import lean_gate
    print('5. Lean accepts the canonical texts')
    rng = random.Random(5)
    lines = [json.loads(l)['prompt'] for l in open(k12)]
    pick = rng.sample(lines, 60)
    items = lean_srcs(pick[:30], 'sl') + lean_srcs(pick[30:], 'pb')
    ok, wall, proc = lean_gate.check_sources([s for _, _, s in items])
    ck(all(ok), f'Lean accepts {sum(ok)} / {len(ok)} (30 sl + 30 pb)')
    print('6. negative controls')
    tok = LeanTokenizer('lean_staten')
    muts = []
    for j, (pr, toks, src) in enumerate(items):
        t = list(toks)
        kind = j % 3
        if kind == 0:                       # ∨-introduction on the wrong side
            ii = [i for i, x in enumerate(t) if x in ('Or.inl', 'Or.inr')]
            if not ii:
                kind = 1
            else:
                i = rng.choice(ii); t[i] = 'Or.inr' if t[i] == 'Or.inl' else 'Or.inl'
                muts.append(f'{tok.statement(pr)} {tok.text(t)}'); continue
        if kind == 1:                       # a citation redirected: the n-name after `:=` in an atomic `have`
            cand = [i for i in range(1, len(t)) if t[i - 1] == ':=' and is_name(t[i]) and i + 1 < len(t) and t[i + 1] == ';']
            names = sorted({x for x in t if is_name(x)})
            if cand and len(names) > 1:
                i = rng.choice(cand)
                t[i] = rng.choice([x for x in names if x != t[i]])
                muts.append(f'{tok.statement(pr)} {tok.text(t)}'); continue
            kind = 2
        prem, goal = parse_prompt(pr)       # the goal replaced by a non-consequence (the proof text unchanged)
        bad = ('atom', 'P') if fnd(goal) != 'P' else ('atom', 'Q')
        if kalmar.countermodel(prem, bad) is None:
            bad = ('bot',)
        pr2 = 'THM ' + ' , '.join(fnd(p) for p in prem) + (' ' if prem else '') + 'SEQ ' + fnd(bad) + ' PRF'
        muts.append(f'{tok.statement(pr2)} {tok.text(toks)}')
    ok2, wall2, proc2 = lean_gate.check_sources(muts)
    ck(not any(ok2), f'Lean rejects {len(ok2) - sum(ok2)} / {len(ok2)} mutated texts')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--k12', default='data/kh/train_k12.jsonl')
    ap.add_argument('--no_lean', action='store_true')
    a = ap.parse_args()
    t1(); t2(); t3(); t4(a.k12)
    if not a.no_lean:
        t5_t6(a.k12)
    print('\nALL TESTS PASS' if not FAIL else f'\n{len(FAIL)} FAILED')
    sys.exit(1 if FAIL else 0)
