#!/usr/bin/env python3
"""Canonical examples: per strategy the shortest clean K12 instance and one typical K12 instance (random, seeded, at the
median pruned length of the proofs whose primary label is the strategy), plus the shortest K12 instance of each kind of
proof by contradiction.  Every example passes the textbook72 guard (sealed.py) and its Lean rendering (lean_render.py)
is accepted by lean_check.  Where K12 has no clean instance the example comes from the Lean-checked shortest proofs of
the pools' textbook-schema instances (source given).  Glosses are hand-written in example_glosses.json.

  python3 proof_strategies/examples.py      # -> artifacts/ps/examples.json, proof_strategies/EXAMPLES.md
"""
import gzip, json, os, random, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from patterns import parse, prune_lines, lines_to_text      # noqa: E402
from strategies import get_proof, STRATS, NAME              # noqa: E402
from lean_render import render                              # noqa: E402
from sealed import Sealed                                   # noqa: E402

BASIC = {'direct', 'and_intro', 'or_intro'}
CLEAN = {   # (label row) -> bool: a clean instance of the strategy as the PRIMARY label
    'direct': lambda a: a['pri'] == 'direct' and a['box_free'] and set(a['u']) <= {'direct'},
    'and_intro': lambda a: a['pri'] == 'and_intro' and set(a['u']) <= BASIC,
    'cond_proof': lambda a: a['pri'] == 'cond_proof' and 'cond_proof.working' in a['psub'] and 'cond_proof.vacuous' not in a['sub'] and set(a['u']) <= BASIC | {'cond_proof'},
    'or_intro': lambda a: a['pri'] == 'or_intro' and set(a['u']) <= BASIC,
    'cases': lambda a: a['pri'] == 'cases' and 'cases.genuine' in a['psub'] and 'cases.trivial_merge' not in a['sub'] and 'cases.redundant' not in a['sub'] and set(a['u']) <= BASIC | {'cases'},
    'disj_syll': lambda a: a['pri'] == 'disj_syll' and set(a['u']) <= BASIC | {'cases', 'disj_syll', 'ex_falso'} and 'ex_falso.inconsistent_premises' not in a['sub']
                           and 'cases.genuine' in a['psub'] and not {'cases.redundant', 'cases.or_intro_decoration'} & set(a['sub']),
    'neg_intro': lambda a: a['pri'] == 'neg_intro' and 'neg_intro.working' in a['psub'] and 'neg_intro.mt' not in a['psub'] and 'neg_intro.immediate' not in a['psub'] and set(a['u']) <= BASIC | {'neg_intro'},
    'mod_tollens': lambda a: a['pri'] == 'mod_tollens' and 'mod_tollens.strict' in a['psub'] and 'mod_tollens.contraposition' not in a['psub'],
    'ex_falso': lambda a: a['pri'] == 'ex_falso' and set(a['u']) <= {'ex_falso', 'direct'},
    'contradiction': lambda a: 'contradiction.free' in a['sub'] and 'contradiction.working' in a['sub'] and 'contradiction.template' not in a['sub'],
    'dne': lambda a: a['pri'] == 'dne' and 'dne.on_premise' in a['psub'],
    'lem': lambda a: 'lem' in a['u'] and not {'cases.redundant', 'cond_proof.vacuous', 'contradiction.template'} & set(a['sub']),
    'lemma_reuse': lambda a: 'lemma_reuse' in a['u'] and 'lemma_reuse.multi_step' in a['sub'] and not set(a['u']) & {'contradiction', 'dne', 'ex_falso'} and 'cases.redundant' not in a['sub'] and 'cond_proof.vacuous' not in a['sub'],
}
TYPICAL = lambda s, a: ('lemma_reuse' in a['u']) if s == 'lemma_reuse' else a['pri'] == s
KINDS = ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free')


def readable(s):
    """a shortest-clean candidate must read like a textbook instance: no ⊥ in the theorem, no line citing the same line
    twice (X ∧ X, X ∨ X), no one-line box (A → A), no reiteration."""
    if ' F ' in s['prompt'].replace('(', ' ').replace(')', ' '):
        return False
    toks = s['prompt'].split()
    for k in range(len(toks) - 2):     # no X op X with identical atomic sides in the theorem
        if toks[k] in 'PQRS' and toks[k + 1] in ('&', 'v', '>') and toks[k + 2] == toks[k]:
            return False
    for ln in parse(get_proof(s)):
        if ln['rule'] == 'AS' and ln['formula'] == ('bot',):
            return False
        if ln['rule'] == 'R' or (len(ln['refs']) >= 2 and len(set(ln['refs'][:2])) < 2 and ln['rule'] in ('ANDI', 'NEGE')):
            return False
        if ln['rule'] in ('IMPI', 'NEGI') and ln['refs'][0] == ln['refs'][1]:
            return False
        if ln['rule'] == 'ORE' and (ln['refs'][1] == ln['refs'][2] and ln['refs'][3] == ln['refs'][4]):
            return False
    return True


def seq_size(prompt):
    return sum(1 for t in prompt.split() if t not in ('(', ')', ',', 'THM', 'SEQ', 'PRF'))


def load(lab, src):
    L = [json.loads(l) for l in gzip.open(lab, 'rt')]
    op = (lambda f: gzip.open(f, 'rt')) if src.endswith('.gz') else open
    S = [json.loads(l) for l in op(src)]
    return [(a, s) for a, s in zip(L, S) if not a.get('parse_fail')]


def nd_lines(prompt, proof):
    return [x.strip().rstrip(';').strip() for x in lines_to_text(prune_lines(parse(proof))).replace(' QED', '').split(' ; ')]


def main():
    seal = Sealed()
    k12 = load('artifacts/ps/labels/k12.jsonl.gz', 'data/ps/in/train_k12.jsonl.gz')
    tb = load('artifacts/ps/labels/tb_schema_search.jsonl.gz', 'data/ps/search/tb_schema.checked.jsonl')
    rng = random.Random(20261018)
    skipped = 0
    out = []

    def first_unsealed(cands):
        nonlocal skipped
        for a, s in cands:
            if seal.hit(s['prompt']):
                skipped += 1
                continue
            return a, s
        return None

    for st in STRATS:
        key = lambda x: (x[0]['Lp'], seq_size(x[1]['prompt']), x[0]['ts'], len(x[0]['u']), x[0]['i'])
        pick, src = first_unsealed(sorted([x for x in k12 if CLEAN[st](x[0]) and readable(x[1])], key=key)) or (None, None), 'K12'
        if pick[0] is None:
            pick, src = first_unsealed(sorted([x for x in tb if CLEAN[st](x[0]) and readable(x[1])], key=key)) or (None, None), 'textbook-schema instance (search proof)'
        if pick[0] is not None:
            out.append({'strategy': st, 'role': 'shortest clean', 'source': src, 'index': pick[0]['i'], 'prompt': pick[1]['prompt'],
                        'proof': get_proof(pick[1]), 'labels': pick[0]})
        chosen = {e['index'] for e in out if e['strategy'] == st and e['source'] == 'K12'}
        grp = [x for x in k12 if TYPICAL(st, x[0]) and (x[0]['i'] not in chosen or len([y for y in k12 if TYPICAL(st, y[0])]) == 1)]
        if grp:
            med = statistics.median_low([x[0]['Lp'] for x in grp])
            cands = [x for x in grp if x[0]['Lp'] == med]
            rng.shuffle(cands)
            t = first_unsealed(cands)
            if t:
                out.append({'strategy': st, 'role': f'typical (pruned length {med}, the median)', 'source': 'K12', 'index': t[0]['i'],
                            'prompt': t[1]['prompt'], 'proof': get_proof(t[1]), 'labels': t[0]})
    for kd in KINDS:
        key = lambda x: (x[0]['Lp'], x[0]['ts'], x[0]['i'])
        key = lambda x: (x[0]['pri'] != 'contradiction' or f'contradiction.{kd}' not in x[0]['psub'], x[0]['Lp'], x[0]['ts'], x[0]['i'])
        cands = [x for x in k12 if f'contradiction.{kd}' in x[0]['sub'] and len([k for k in KINDS if f'contradiction.{k}' in x[0]['sub']]) == 1]
        t = first_unsealed(sorted([x for x in cands if readable(x[1])], key=key)) or first_unsealed(sorted(cands, key=key))
        if t:
            out.append({'strategy': 'contradiction', 'role': f'kind {kd} (shortest K12 proof with only this kind; primary if one exists)', 'source': 'K12', 'index': t[0]['i'],
                        'prompt': t[1]['prompt'], 'proof': get_proof(t[1]), 'labels': t[0]})
    # Lean: render every example and check it
    import lean_check
    srcs = [render(e['prompt'], e['proof']) for e in out]
    res, _, _ = lean_check.check(srcs)
    for e, x in zip(out, res):
        e['lean_ok'], e['term_size_lean'] = x['ok'], x.get('size')
        e['lean'] = render(e['prompt'], e['proof'], name='', kind='example')
        e['nd'] = nd_lines(e['prompt'], e['proof'])
        assert seal.hit(e['prompt']) is False
    json.dump({'examples': out, 'sealed_skipped': skipped, 'lean_ok': sum(e['lean_ok'] for e in out), 'n': len(out)},
              open('artifacts/ps/examples.json', 'w'), indent=1)
    print(json.dumps({'n': len(out), 'lean_ok': sum(e['lean_ok'] for e in out), 'sealed_skipped': skipped}))
    write_md(out)


def write_md(out):
    gl = json.load(open(os.path.join(HERE, 'example_glosses.json'))) if os.path.exists(os.path.join(HERE, 'example_glosses.json')) else {}
    md = ['# Canonical examples', '',
          'Generated by `proof_strategies/examples.py` (`artifacts/ps/examples.json`). Each example: the theorem, the pruned ND',
          'proof, a Lean 4 rendering accepted by `lean_check` (core Lean, allowlisted constants only), and a hand-written gloss.',
          'No example is in a textbook72 renaming class (`sealed.py`: order-sensitive, premise-order-invariant and curried keys).',
          'Line counts are pruned ND lines; term size is lean_check\'s inference-node count.', '']
    for st in STRATS:
        ex = [e for e in out if e['strategy'] == st]
        md += [f'## {STRATS.index(st) + 1}. {NAME[st]}', '']
        for e in ex:
            gid = f"{st}:{e['role'].split(' (')[0]}"
            md += [f"**{e['role']}** — {e['source']} record {e['index']}; {len(e['nd'])} lines, term size {e['term_size_lean']}; "
                   f"uses {', '.join(e['labels']['u']) or '–'}; primary {e['labels']['pri']}."
                   + (f" Gloss: {gl[gid]}" if gid in gl else ' Gloss: *(to write)*'), '',
                   '```', e['prompt'], *e['nd'], '```', '', '```lean', e['lean'], '```', '']
    open(os.path.join(HERE, 'EXAMPLES.md'), 'w').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
