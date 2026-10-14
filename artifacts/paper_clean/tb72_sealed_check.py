#!/usr/bin/env python3
"""paper-clean task 3: is any theorem printed in the paper, the blog or paper/lean/ in a sealed textbook72 renaming class?

Method of nd-rl `dan_shared_proof_state` code/tests/fixtures/proof_state/make_golden.py --sealed: the class of a theorem
is gen.canon_key("premises |- goal") (atoms relabelled by first appearance; premise-order SENSITIVE).  We add a
premise-order-INVARIANT key (the minimum canon_key over all premise orders), because gen.canon_key misses
premise-swapped twins.  Schema letters A, B, G are mapped to atoms first (any injective map gives the same class).
Positive control: the pre-clean negated-conditional schema must hit textbook_b98931f2 under both keys.

  python3 artifacts/paper_clean/tb72_sealed_check.py  > artifacts/paper_clean/tb72_sealed_check.txt
"""
import itertools, json, os, sys
sys.path.insert(0, os.getcwd())
from gen import canon_key

def thm_of(prompt):                       # make_golden.thm_of
    t = prompt.split(); i = t.index('SEQ')
    return ' '.join(t[1:i]) + ' |- ' + ' '.join(t[i + 1:-1])

def split_top(s):                         # split premises at depth-0 commas
    out, depth, cur = [], 0, []
    for tok in s.split():
        if tok == ',' and depth == 0:
            out.append(' '.join(cur)); cur = []; continue
        depth += tok == '('; depth -= tok == ')'; cur.append(tok)
    if cur: out.append(' '.join(cur))
    return out

def keys(thm):
    prem, goal = thm.split('|-')
    prems = split_top(prem.strip()) if prem.strip() else []
    k_ord = canon_key(thm.strip())
    k_inv = min(canon_key(' , '.join(p) + (' ' if p else '') + '|- ' + goal.strip()) for p in itertools.permutations(prems))
    return k_ord, k_inv

def schema(s):                            # schema letters -> atoms (A->P, B->Q, G->R)
    return ' '.join({'A': 'P', 'B': 'Q', 'G': 'R'}.get(t, t) for t in s.split())

PRINTED = [  # (where, theorem in generator syntax: ~ not, > implies, & and, v or)
    ('paper §2 (03_setup) family list: converse contraposition schema', schema('( ( ~ B ) > ( ~ A ) ) |- ( A > B )')),
    ('paper §2 (03_setup) family list: Peirce sequent schema', schema('( ( A > B ) > A ) |- A')),
    ('paper §2 (03_setup) family list: De Morgan schema', schema('( ~ ( A & B ) ) |- ( ( ~ A ) v ( ~ B ) )')),
    ('paper Table 1 lemma route: the formula ¬¬G → G read as a theorem', schema('|- ( ( ~ ( ~ G ) ) > G )')),
    ('paper Fig. 1 listing + caption (03_setup), App. listing (b), blog text + Lean block, lean/blog_example.lean '
     '(la_transfer_916)', '( ( ~ S ) > ( ~ P ) ) , P |- ( R > S )'),
    ('paper App. listing (a) (la_transfer_1246)', '( ( ~ S ) > ( ~ ( ( S & R ) v R ) ) ) |- ( ( ( S & R ) v R ) > S )'),
    ('lean/blog_example_negctl.lean (goal-negated control, unprovable)', '( ( ~ S ) > ( ~ P ) ) , P |- ( ~ ( R > S ) )'),
    ('blog: excluded middle "P or not P"', '|- ( P v ( ~ P ) )'),
]
CONTROL = ('reading copy §2 (removed in the clean copy): negated-conditional schema', schema('( ~ ( A > B ) ) |- ( A & ( ~ B ) )'))

tb = [json.loads(l) for l in open('data/bs/textbook72.jsonl')]
ORD, INV = {}, {}
for r in tb:
    ko, ki = keys(thm_of(r['prompt']))
    ORD.setdefault(ko, []).append(r['name']); INV.setdefault(ki, []).append(r['name'])
print(f'textbook72: {len(tb)} problems, {len(ORD)} order-sensitive classes, {len(INV)} premise-order-invariant classes')
hits = 0
for where, thm in [CONTROL] + PRINTED:
    ko, ki = keys(thm)
    a, b = ORD.get(ko, []), INV.get(ki, [])
    hits += bool(a or b) and (where, thm) != CONTROL
    print(f"{'HIT ' if (a or b) else 'ok  '} {thm:70s} order-sensitive {a or '-'}  order-invariant {b or '-'}  | {where}")
print(f'printed theorems in a textbook72 class (excluding the removed control): {hits}')
