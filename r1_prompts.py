#!/usr/bin/env python3
"""run1-lean step 2: theorem set, example draws, and the three surface-form prompts.

  python r1_prompts.py --out data/r1        # writes theorems.jsonl, examples.jsonl, prompts.jsonl, prompt_stats.json

Theorems: validation-36 (stratum = its `bin`) + 200 transfer theorems (20 per generating length 7-16, seed 0).
Examples: per draw, 10 train proofs (2 per length 2-6) + 10 rl_targets generator proofs (1 per length 7-16),
re-drawn until every one of the 13 non-PR/AS rules appears; 5 draws (seeds 0-4); ordered by length.
Class-disjointness (atom-renaming key) between examples and test theorems is asserted.
Forms: tokens (take-home format), lean (term-mode Lean 4; the model completes after ':='), english
(same lines, rule names spelled out, boxes as bars, Unicode connectives). Same theorems, same examples.
"""
import argparse, json, os, sys, random, gzip, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key
from nd_verify import verify_text
from nd_verify.verify import parse_proof_tokens
import nd2lean as L

RULES13 = ['R', 'ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'IMPI', 'ORI1', 'ORI2', 'ORE', 'NEGE', 'NEGI', 'BOTE', 'DN']

SYSTEM = ('You are an expert in classical propositional logic who writes formal natural-deduction proofs. '
          'Follow the format of the worked examples exactly. Output only the proof, with no explanation.')

CARD = {
 'tokens': """Format: Fitch-style natural deduction in a token format. Atoms P Q R S, falsum F; connectives ~ (not), & (and), v (or), > (implies); every compound formula is fully parenthesised, e.g. ( ~ P ), ( P & Q ). A theorem is written `THM <premises separated by ,> SEQ <conclusion> PRF` (zero premises: `THM SEQ <conclusion> PRF`). A proof is a sequence of lines
  N<i> <'|' repeated once per subproof depth> <formula> : <RULE> <cited lines> ;
ending with QED. Line indices are consecutive from N1. Rules: PR (premise; the premise lines come first, in order), AS (assumption; opens a subproof box one level deeper), R Nj (reiterate line j), ANDI Na Nb, ANDE1 Na (left conjunct), ANDE2 Na (right conjunct), IMPE Na Nb (Na is the implication ( B > G ), Nb is B), IMPI Ns Ne (the box from assumption line s to its last line e gives ( A > B )), ORI1 Na (gives ( A v X )), ORI2 Na (gives ( X v A )), ORE Nj Ns1 Ne1 Ns2 Ne2 (Nj is ( A v B ); two boxes assuming A and B, each ending in the goal), NEGE Na Nb (Na is A, Nb is ( ~ A ); gives F), NEGI Ns Ne (a box assuming A that ends in F gives ( ~ A )), BOTE Na (from F derive anything), DN Na (from ( ~ ( ~ A ) ) derive A). A line may cite only earlier lines whose boxes are still open; a box is cited by its first (AS) and last line once it is closed. The last line is at depth 0 and is the conclusion.""",
 'english': """Format: Fitch-style natural deduction. Atoms P Q R S, falsum ⊥; connectives ¬, ∧, ∨, →; every compound formula is fully parenthesised, e.g. (¬P), (P ∧ Q). A theorem is given as its premises and its goal. A proof is a numbered list of lines
  <i>. <'| ' repeated once per subproof depth><formula> : <rule and the cited lines>
ending with QED. Line numbers are consecutive from 1. Rules: premise (the premise lines come first, in order); assumption (opens a subproof box one level deeper); reiteration of j; conjunction introduction from a and b; conjunction elimination (left) from a; conjunction elimination (right) from a; implication elimination from a and b (a is the implication (B → G), b is B); implication introduction from subproof s-e (the box from assumption line s to its last line e gives (A → B)); disjunction introduction (left) from a (gives (A ∨ X)); disjunction introduction (right) from a (gives (X ∨ A)); disjunction elimination from j with subproofs s1-e1 and s2-e2 (j is (A ∨ B); two boxes assuming A and B, each ending in the goal); negation elimination from a and b (a is A, b is (¬A); gives ⊥); negation introduction from subproof s-e (a box assuming A that ends in ⊥ gives (¬A)); ex falso from a (from ⊥ derive anything); double negation elimination from a (from (¬(¬A)) derive A). A line may cite only earlier lines whose boxes are still open; a box is cited by its first (assumption) and last line once it is closed. The last line is at depth 0 and is the goal.""",
 'lean': """Format: Lean 4 term-mode proofs using only the core library (no Mathlib, no tactics, no `by`, no `sorry`). Atoms are the Prop variables P Q R S; premises are the hypotheses h1, h2, …; the theorem statement is given and the proof is a chain of
  have n<i> : <formula> := <term>
lines, ending with the name of the final fact. Building blocks: And.intro a b; a.1 and a.2 (conjunction elimination); Or.inl a and Or.inr a; Or.elim d f g (d : A ∨ B, f : A → G, g : B → G); application f a (modus ponens; also h a : False when h : ¬A); fun n : A => ( … ) for implication and negation introduction (a subproof under the assumption n : A, whose last line is its result); False.elim a (from False derive anything); Classical.not_not.mp a (from ¬¬A derive A). Every intermediate fact is named n<i>; subproofs are named b<i>."""
}


def load_jsonl(fn, limit=None):
    op = gzip.open if fn.endswith('.gz') else open
    out = []
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                out.append(json.loads(l))
                if limit and len(out) >= limit:
                    break
    return out


def rules_of(proof):
    return {ln['rule'] for ln in parse_proof_tokens(proof.split())}


def render_example(form, prompt, proof, k):
    if form == 'tokens':
        return f'### Example {k}\n{prompt}\n{proof}'
    if form == 'english':
        return f'### Example {k}\n{L.eng_sequent(prompt)}\n{L.to_english(prompt, proof)}'
    if form == 'lean':
        h, b = L.to_lean(prompt, proof, name=f'ex{k}')
        return f'### Example {k}\n```lean\n{h}\n{b.rstrip()}\n```'
    raise ValueError(form)


def render_target(form, prompt):
    if form == 'tokens':
        return f'Now prove the following theorem in the same format. Output only the proof lines and QED.\n{prompt}'
    if form == 'english':
        return f'Now prove the following theorem in the same format. Output only the numbered proof lines and QED.\n{L.eng_sequent(prompt)}'
    if form == 'lean':
        return (f'Now prove the following theorem in the same style. Output only the complete theorem with its proof term '
                f'(the statement is fixed; complete it after :=).\n```lean\n{L.lean_header(prompt, name="target")}\n```')
    raise ValueError(form)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/r1')
    ap.add_argument('--n_transfer_per_len', type=int, default=20)
    ap.add_argument('--draws', type=int, default=5)
    ap.add_argument('--n_examples', type=int, default=20)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(0)

    # ---- theorems
    val = load_jsonl('targets/validation_36.jsonl')
    thms = [{'name': v['name'], 'thm': v['thm'], 'prompt': v['prompt'], 'src': 'val36', 'stratum': 'val36 ' + v['bin'],
             'gen_lines': None, 'min_lines_ub': v.get('min_lines_ub'), 'key': canon_key(v['thm'].strip())} for v in val]
    tr = load_jsonl('data/transfer.jsonl')
    by_len = collections.defaultdict(list)
    for t in tr:
        by_len[t['n_lines']].append(t)
    for n in range(7, 17):
        pick = rng.sample(by_len[n], a.n_transfer_per_len)
        for t in pick:
            thms.append({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'src': 'transfer', 'stratum': f'L{n}',
                         'gen_lines': n, 'key': t['key'], 'gen_proof': t['gen_proof']})
    test_keys = {t['key'] for t in thms}
    assert len(test_keys) == len(thms), 'duplicate renaming class among test theorems'

    # ---- example pools
    train = load_jsonl('data/train.jsonl.gz')
    train_by_len = collections.defaultdict(list)
    for r in train:
        train_by_len[r['n_lines']].append(r)
    rlt = load_jsonl('data/rl_targets.jsonl')
    rlt_by_len = collections.defaultdict(list)
    for r in rlt:
        rlt_by_len[r['n_lines']].append(r)
    draws = []
    for d in range(a.draws):
        seed = d
        while True:
            rd = random.Random(1000 + seed)
            ex = []
            for n in range(2, 7):
                ex += rd.sample(train_by_len[n], 2)
            for n in range(7, 17):
                ex += rd.sample(rlt_by_len[n], 1)
            ex = [{'draw': d, 'name': r['name'], 'prompt': r['prompt'], 'proof': r.get('proof') or r['gen_proof'],
                   'n_lines': r['n_lines'], 'key': r['key']} for r in ex]
            cov = set().union(*(rules_of(e['proof']) for e in ex))
            missing = [r for r in RULES13 if r not in cov]
            if not missing and not ({e['key'] for e in ex} & test_keys):
                break
            seed += 100
        for e in ex:
            ok, reason, nl = verify_text(e['prompt'] + ' ' + e['proof'])
            assert ok and nl == e['n_lines'], (e['name'], reason)
        draws.append(ex)
        print(f'draw {d}: seed {seed}, lengths {[e["n_lines"] for e in ex]}')

    # ---- prompts
    prompts, stats = [], collections.Counter()
    for form in ('tokens', 'lean', 'english'):
        for d, ex in enumerate(draws):
            body = CARD[form] + '\n\nWorked examples:\n\n' + '\n\n'.join(render_example(form, e['prompt'], e['proof'], k + 1) for k, e in enumerate(ex))
            for t in thms:
                user = body + '\n\n' + render_target(form, t['prompt'])
                rec = {'id': f'{form}/d{d}/{t["name"]}', 'form': form, 'draw': d, 'name': t['name'], 'src': t['src'],
                       'stratum': t['stratum'], 'gen_lines': t['gen_lines'], 'nd_prompt': t['prompt'],
                       'lean_header': L.lean_header(t['prompt'], name='target'),
                       'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}]}
                prompts.append(rec)
                stats[form] += len(user)
    with open(f'{a.out}/theorems.jsonl', 'w') as f:
        for t in thms:
            f.write(json.dumps(t) + '\n')
    with open(f'{a.out}/examples.jsonl', 'w') as f:
        for ex in draws:
            for e in ex:
                f.write(json.dumps(e) + '\n')
    with open(f'{a.out}/prompts.jsonl', 'w') as f:
        for p in prompts:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    st = {'n_theorems': len(thms), 'strata': collections.Counter(t['stratum'] for t in thms), 'n_prompts': len(prompts),
          'mean_user_chars': {k: v / (len(thms) * a.draws) for k, v in stats.items()},
          'example_lengths': [[e['n_lines'] for e in ex] for ex in draws]}
    json.dump(st, open(f'{a.out}/prompt_stats.json', 'w'), indent=1)
    print(json.dumps(st, indent=1))
    # sanity: every example renders and round-trips in every form
    for ex in draws:
        for e in ex:
            h, b = L.to_lean(e['prompt'], e['proof'])
            back = L.english_to_tokens(L.to_english(e['prompt'], e['proof']))
            assert verify_text(e['prompt'] + ' ' + back)[0], e['name']
    print('round-trip ok')


if __name__ == '__main__':
    main()
