#!/usr/bin/env python3
"""frontier-supply: new EI targets just past the frontier (proposal 16 item 1).

Each round the supply arm of `state_ladder_ei.py` builds candidate theorems from the current model's own attempts and
keeps those it solves rarely (32 attempts, p-hat in (0, 1/4], STP 2502.00212v4 sec. 3.2).  Nothing here writes
proofs: a candidate is only a statement, and it becomes a training target only through proofs the model found and
Lean accepted.  Two sources:

  (a) mutations of theorems solved this round, with an upper bound `ub` on proof length built from the shortest
      written proof `w` (ND lines) of each parent:
        chain       T1: G1 |- C1, T2: G2 |- C2, a premise A of T2 with s(A) = C1 for an atom substitution s
                    -> G1 + s(G2 - A) |- s(C2)                                                   ub w1 + w2 - 1
        conj        G1 + r(G2) |- C1 & r(C2)   (r: a random atom renaming of T2)               ub w1 + w2 + 1
        contrapose  G, A |- C -> G, ~C |- ~A                                                   ub w + 3
        hyp         G, A |- C -> G |- A > C                                                    ub w + 1
        case        G, A |- C -> G, A v B, B > C |- C  (B a fresh small formula)               ub w + 4
      kept only with ub in the round's window [base+1, base+4];
  (b) the focused open goal, under every hypothesis in scope, where a failed attempt ended in the environment
      (`state_sample.env_generate(..., fail_states=...)` records the state before the failing action).

A candidate record looks like an `rl_targets` record: name, thm, key, prompt, n_lines (= ub; 0 when unknown), source,
op.  `leak_key` is the renaming class with premise order ignored; the ladder drops any candidate whose `leak_key`
matches an evaluation pool.
"""
import itertools, random
from gen import fstr, canon_key, ATOMS

MAX_PREM = 8
MAX_TOKENS = 300


def thm_of(prem, concl):
    return ' , '.join(fstr(p) for p in prem) + (' ' if prem else '') + '|- ' + fstr(concl)


def prompt_of(prem, concl):
    return (f"THM {' , '.join(fstr(p) for p in prem)} SEQ {fstr(concl)} PRF" if prem else f'THM SEQ {fstr(concl)} PRF')


def leak_key(prem, concl):
    """renaming class with premise order ignored (exact canonical form): the least string, over the 24 atom
    renamings, of the renamed premises sorted, then the conclusion.  Duplicate premises count once."""
    best = None
    for perm in itertools.permutations(ATOMS):
        s = {a: ('atom', b) for a, b in zip(ATOMS, perm)}
        k = ' , '.join(sorted({fstr(subst(p, s)) for p in prem})) + ' |- ' + fstr(subst(concl, s))
        if best is None or k < best:
            best = k
    return best


def leak_key_thm(thm):
    from nd_verify.verify import parse_formula
    lhs, rhs = thm.split('|-')
    prem = []
    toks = lhs.split()
    i = 0
    while i < len(toks):
        f, i = parse_formula(toks, i)
        prem.append(f)
        if i < len(toks) and toks[i] == ',':
            i += 1
    concl, _ = parse_formula(rhs.split(), 0)
    return leak_key(prem, concl)


def atoms_of(f, out=None):
    out = set() if out is None else out
    if f[0] == 'atom':
        out.add(f[1])
    elif f[0] == 'not':
        atoms_of(f[1], out)
    elif f[0] in ('and', 'or', 'imp'):
        atoms_of(f[1], out); atoms_of(f[2], out)
    return out


def subst(f, s):
    if f[0] == 'atom':
        return s.get(f[1], f)
    if f[0] == 'bot':
        return f
    if f[0] == 'not':
        return ('not', subst(f[1], s))
    return (f[0], subst(f[1], s), subst(f[2], s))


def match(pat, f, s):
    """one-way matching: extend substitution s (atom -> formula) so that subst(pat, s) == f; None if impossible."""
    if pat[0] == 'atom':
        a = pat[1]
        if a in s:
            return s if s[a] == f else None
        s = dict(s); s[a] = f
        return s
    if pat[0] != f[0]:
        return None
    if pat[0] == 'bot':
        return s
    if pat[0] == 'not':
        return match(pat[1], f[1], s)
    s = match(pat[1], f[1], s)
    return None if s is None else match(pat[2], f[2], s)


def ntoks(prem, concl):
    return len(prompt_of(prem, concl).split())


def dedupe(prem):
    out = []
    for p in prem:
        if p not in out:
            out.append(p)
    return out


def ok_shape(prem, concl):
    return len(prem) <= MAX_PREM and concl not in prem and ntoks(prem, concl) <= MAX_TOKENS


def rand_small(rng):
    a = ('atom', rng.choice(ATOMS))
    r = rng.random()
    if r < 0.5:
        return a
    if r < 0.75:
        return ('not', a)
    return (rng.choice(['and', 'or', 'imp']), a, ('atom', rng.choice(ATOMS)))


def rand_rename(rng):
    p = ATOMS[:]; rng.shuffle(p)
    return {a: ('atom', b) for a, b in zip(ATOMS, p)}


def mutate(solved, rng, n_try):
    """solved: list of dicts {prem, concl, w}.  Yields (prem, concl, ub, op) candidates (unfiltered)."""
    ops = ['chain', 'conj', 'contrapose', 'hyp', 'case']
    for _ in range(n_try):
        op = rng.choice(ops)
        t1 = rng.choice(solved)
        P1, C1, w1 = t1['prem'], t1['concl'], t1['w']
        if op == 'chain':
            t2 = rng.choice(solved)
            P2, C2, w2 = t2['prem'], t2['concl'], t2['w']
            idx = list(range(len(P2))); rng.shuffle(idx)
            for i in idx:
                s = match(P2[i], C1, {})
                if s is None:
                    continue
                free = atoms_of(C2)
                for p in P2:
                    atoms_of(p, free)
                for a in sorted(free):
                    if a not in s:
                        s[a] = ('atom', rng.choice(ATOMS))
                prem = dedupe(list(P1) + [subst(p, s) for j, p in enumerate(P2) if j != i])
                yield prem, subst(C2, s), w1 + w2 - 1, op
                break
        elif op == 'conj':
            t2 = rng.choice(solved)
            s = rand_rename(rng)
            prem = dedupe(list(P1) + [subst(p, s) for p in t2['prem']])
            yield prem, ('and', C1, subst(t2['concl'], s)), w1 + t2['w'] + 1, op
        elif op == 'contrapose':
            if not P1 or C1 == ('bot',):
                continue
            i = rng.randrange(len(P1))
            prem = dedupe([p for j, p in enumerate(P1) if j != i] + [('not', C1)])
            yield prem, ('not', P1[i]), w1 + 3, op
        elif op == 'hyp':
            if not P1:
                continue
            i = rng.randrange(len(P1))
            yield dedupe([p for j, p in enumerate(P1) if j != i]), ('imp', P1[i], C1), w1 + 1, op
        elif op == 'case':
            if not P1:
                continue
            i = rng.randrange(len(P1))
            b = rand_small(rng)
            prem = dedupe([p for j, p in enumerate(P1) if j != i] + [('or', P1[i], b), ('imp', b, C1)])
            yield prem, C1, w1 + 4, op


def make_candidates(solved, fails, n_want, window, block, leak, rng, round_, n_try=200000):
    """solved: [{prem, concl, w}]; fails: [{prem, concl, pri}] (pri 0 = from a target with p-hat <= 1/4 this round).
    block: set of leak keys never to produce (rl_targets, earlier candidates) -- updated in place with every
    candidate returned; leak: evaluation classes (dropped and counted, `leak_keys` in the log).  -> (candidates, log).  Half from (a), half from (b); each fills the other's shortfall."""
    lo, hi = window
    log = {'window': [lo, hi], 'a_tried': 0, 'a_in_window': 0, 'a_dup': 0, 'b_pool': len(fails), 'b_dup': 0,
           'b_shape': 0, 'a_ops': {}, 'a_leak': 0, 'b_leak': 0, 'leak_keys': []}
    a_out, b_out = [], []
    # (a)
    if solved:
        for prem, concl, ub, op in mutate(solved, rng, n_try):
            log['a_tried'] += 1
            if not (lo <= ub <= hi) or not ok_shape(prem, concl):
                continue
            log['a_in_window'] += 1
            k = leak_key(prem, concl)
            if k in leak:
                log['a_leak'] += 1; log['leak_keys'].append(k); continue
            if k in block:
                log['a_dup'] += 1; continue
            block.add(k)
            a_out.append({'prem': prem, 'concl': concl, 'n_lines': ub, 'source': 'a', 'op': op, 'leak_key': k})
            log['a_ops'][op] = log['a_ops'].get(op, 0) + 1
            if len(a_out) >= n_want:
                break
    # (b)
    fl = list(fails); rng.shuffle(fl); fl.sort(key=lambda x: x['pri'])
    for x in fl:
        if len(b_out) >= n_want:
            break
        prem = dedupe(x['prem'])
        if not ok_shape(prem, x['concl']):
            log['b_shape'] += 1; continue
        k = leak_key(prem, x['concl'])
        if k in leak:
            log['b_leak'] += 1; log['leak_keys'].append(k); continue
        if k in block:
            log['b_dup'] += 1; continue
        block.add(k)
        b_out.append({'prem': prem, 'concl': x['concl'], 'n_lines': 0, 'source': 'b', 'op': 'open_goal', 'leak_key': k,
                      'steps': x.get('steps')})
    half = n_want // 2
    na = min(len(a_out), max(half, n_want - len(b_out)))
    nb = min(len(b_out), n_want - na)
    cands = a_out[:na] + b_out[:nb]
    for i, c in enumerate(cands):
        c['thm'] = thm_of(c['prem'], c['concl'])
        c['key'] = canon_key(c['thm'])
        c['prompt'] = prompt_of(c['prem'], c['concl'])
        c['name'] = f"sup_r{round_}_{c['source']}_{i}"
    # unused candidates are released so a later round may make them again
    for c in a_out[na:] + b_out[nb:]:
        block.discard(c['leak_key'])
    log.update({'a_made': na, 'b_made': nb, 'made': len(cands)})
    return cands, log


def strip(c):
    """json-safe candidate record (formula trees dropped)."""
    return {k: v for k, v in c.items() if k not in ('prem', 'concl')}
