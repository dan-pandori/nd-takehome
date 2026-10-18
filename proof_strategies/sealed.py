#!/usr/bin/env python3
"""Guard: no example printed by this run may be in a renaming class of textbook72 (sealed: scoring only, never printed).

Three keys, a theorem is sealed if any matches a textbook72 theorem:
  1. gen.canon_key of the theorem string (nd-rl PR #26 make_golden.py's --sealed method; premise-order sensitive);
  2. a premise-order-invariant key: the minimum over the 24 renamings of P Q R S of (sorted premises, conclusion);
  3. the same key of the curried normal form (leading antecedents of the conclusion moved into the premises; Charles's
     overlap rule: A ⊢ B and ⊢ A → B are one problem).
Matches are counted, never printed.  Self-test: positive controls (every textbook72 theorem and a renamed, premise-
reversed, curried variant of each must be caught) and a count on K12.

  python3 proof_strategies/sealed.py --selftest
"""
import gzip, itertools, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from gen import canon_key, fstr                 # noqa: E402
from minlen import parse_thm                    # noqa: E402

SEALED = os.path.join(HERE, '..', 'data', 'bs', 'textbook72.jsonl')


def rename(f, m):
    if f[0] == 'atom':
        return ('atom', m[f[1]])
    return (f[0],) + tuple(rename(g, m) if isinstance(g, tuple) else g for g in f[1:])


def inv_key(prem, concl):
    best = None
    for perm in itertools.permutations('PQRS'):
        m = dict(zip('PQRS', perm))
        k = (tuple(sorted(fstr(rename(p, m)) for p in prem)), fstr(rename(concl, m)))
        if best is None or k < best:
            best = k
    return best


def curry(prem, concl):
    prem = list(prem)
    while concl[0] == 'imp':
        prem.append(concl[1])
        concl = concl[2]
    return prem, concl


def thm_string(prompt):
    body = prompt[len('THM '):-len(' PRF')] if prompt.startswith('THM ') else prompt
    prem, concl = body.split('SEQ')
    return (prem.strip() + ' |- ' + concl.strip()).strip()


class Sealed:
    def __init__(self, path=SEALED):
        self.canon, self.inv = set(), set()
        for line in open(path):
            p = json.loads(line)['prompt']
            prem, concl = parse_thm(p)
            self.canon.add(canon_key(thm_string(p)))
            self.inv.add(inv_key(prem, concl))
            self.inv.add(inv_key(*curry(prem, concl)))
        self.n = sum(1 for _ in open(path))

    def hit(self, prompt):
        prem, concl = parse_thm(prompt)
        return (canon_key(thm_string(prompt)) in self.canon or inv_key(prem, concl) in self.inv
                or inv_key(*curry(prem, concl)) in self.inv)


def selftest():
    S = Sealed()
    rows = [json.loads(l)['prompt'] for l in open(SEALED)]
    own = sum(S.hit(p) for p in rows)
    rng = random.Random(0)
    caught = 0
    for p in rows:                       # a renamed, premise-reversed, curried variant of each sealed theorem
        prem, concl = parse_thm(p)
        perm = list('PQRS'); rng.shuffle(perm); m = dict(zip('PQRS', perm))
        prem2 = [rename(x, m) for x in reversed(prem)]
        concl2 = rename(concl, m)
        if prem2:                        # move the last premise into the conclusion (uncurry one step)
            concl2 = ('imp', prem2[-1], concl2); prem2 = prem2[:-1]
        variant = 'THM ' + ' , '.join(fstr(x) for x in prem2) + (' ' if prem2 else '') + 'SEQ ' + fstr(concl2) + ' PRF'
        caught += S.hit(variant)
    k12 = sum(S.hit(json.loads(l)['prompt']) for l in gzip.open(os.path.join(HERE, '..', 'data', 'ps', 'in', 'train_k12.jsonl.gz'), 'rt'))
    out = {'sealed_theorems': S.n, 'own_caught': own, 'variants_caught': caught, 'k12_records_in_sealed_classes': k12}
    print(json.dumps(out))
    assert own == S.n and caught == S.n, out
    return out


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        json.dump(selftest(), open(os.path.join(HERE, '..', 'artifacts', 'ps', 'sealed_selftest.json'), 'w'))
