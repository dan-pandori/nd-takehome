#!/usr/bin/env python3
"""What the model writes when its greedy action differs from Kalmár's (teacher-forced states; run kalmar-pretrain).

  python3 kalmar/error_classes.py artifacts/kalmar/tf/errors_kalD_s2__tf1200.errors.jsonl.gz [--examples 2]

Input: `kalmar/tf_agree.py --dump_errors` rows (state, algorithm action, model action, step type).  Classes, first
match wins:
  truncated       the model's action never ended (no <eos> in 512 tokens)
  malformed       the declared formula does not parse, or the action is outside the action grammar
  close-timing    one action is `exact`, the other a `have` (closing a box too early / too late)
  exact-citation  both `exact`, different name
  same-formula    both `have` with the same declared formula, different justification (another valid route or a
                  wrong citation)
  polarity        the model declares ¬F where the algorithm declares F, or F where it declares ¬F (a truth-value
                  error at a leaf)
  other-subformula the model declares a formula that occurs in the state (a hypothesis, the goal, or a subformula of
                  one): the right material, the wrong place in the recursion
  corrupted       the declared formula occurs nowhere in the state (a copying / substitution error)
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_env import parse_ftoks
from lean_tok import ParseFail, ftoks


def subformulas(f, acc):
    acc.add(tuple(ftoks(f)))
    if f[0] not in ('atom', 'bot'):
        for g in f[1:]:
            subformulas(g, acc)


def declared(act):
    """`have n : F := ...` -> (F tuple, rest tokens) or raises ParseFail."""
    if len(act) < 4 or act[0] != 'have' or act[2] != ':':
        raise ParseFail('head')
    f, used = parse_ftoks(act, 3)
    if 3 + used >= len(act) or act[3 + used] != ':=':
        raise ParseFail('assign')
    return f, act[3 + used + 1:]


def state_formulas(state):
    """every hypothesis formula and the goal of a state token list, with their subformulas (as token tuples)."""
    acc = set()
    toks = state
    i = 0
    while i < len(toks):
        if toks[i] == ':' or toks[i] == '⊢':
            try:
                f, used = parse_ftoks(toks, i + 1)
                subformulas(f, acc)
                i += 1 + used
                continue
            except ParseFail:
                pass
        i += 1
    return acc


def classify(r):
    A, M = r['algorithm'].split(), r['model'].split()
    if M and M[-1] == '…':
        return 'truncated'
    if (A[0] == 'exact') != (M[:1] == ['exact']):
        if M[:1] not in (['exact'], ['have']):
            return 'malformed'
        return 'close-timing'
    if A[0] == 'exact':
        return 'exact-citation'
    try:
        fm, _ = declared(M)
    except (ParseFail, IndexError):
        return 'malformed'
    fa, _ = declared(A)
    if fm == fa:
        return 'same-formula'
    if fm == ('not', fa) or fa == ('not', fm):
        return 'polarity'
    if tuple(ftoks(fm)) in state_formulas(r['state'].split()):
        return 'other-subformula'
    return 'corrupted'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('errors')
    ap.add_argument('--examples', type=int, default=0)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    op = gzip.open if a.errors.endswith('.gz') else open
    rows = [json.loads(l) for l in op(a.errors, 'rt')]
    tot = collections.Counter(); by = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
    for r in rows:
        c = classify(r)
        tg = r['tag'].split(':')[0] if r['tag'].startswith('close:') else r['tag']
        tot[c] += 1; by[tg][c] += 1
        if len(ex[c]) < a.examples:
            ex[c].append(r)
    n = sum(tot.values())
    print(f'{a.errors}: {n} disagreements')
    print('  ' + ', '.join(f'{k} {v} ({100 * v / n:.1f} %)' for k, v in tot.most_common()))
    for tg in sorted(by, key=lambda t: -sum(by[t].values())):
        m = sum(by[tg].values())
        print(f'  {tg:14s} {m:5d}: ' + ', '.join(f'{k} {100 * v / m:.0f} %' for k, v in by[tg].most_common(4)))
    for c, xs in ex.items():
        for r in xs:
            print(f'--- {c} [{r["tag"]}]\n  algo : {r["algorithm"][:200]}\n  model: {r["model"][:200]}')
    if a.out:
        json.dump({'n': n, 'classes': dict(tot), 'by_tag': {k: dict(v) for k, v in by.items()}}, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
