#!/usr/bin/env python3
"""Draw the blind spot-check sample: per strategy 12 random positives, 4 random negatives and 4 borderline proofs
(K12; textbook-schema search proofs where K12 has too few positives).  Writes the blind files (no labels) for the
checkers and a key file with our labels.  textbook72 and Charles's release are never sampled.

  python3 proof_strategies/validation_sample.py      # -> data/ps/validation/spot_{a,b,c}.jsonl, data/ps/validation/spot_key.jsonl
"""
import gzip, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from patterns import parse, prune_lines, lines_to_text      # noqa: E402
from strategies import get_proof, STRATS                    # noqa: E402

# borderline filters: (description, predicate on a label row)
BORDER = {
    'direct': ('root ¬E, or box-free without →E / ∧E', lambda a: 'direct.neg_elim_root' in a['sub'] or (a['box_free'] and 'direct' not in a['u'])),
    'and_intro': ('∧I not at the root', lambda a: 'and_intro' in a['u'] and a['pri'] != 'and_intro'),
    'cond_proof': ('vacuous →I', lambda a: 'cond_proof.vacuous' in a['sub']),
    'or_intro': ('∨I feeding a ∨E', lambda a: 'or_intro.feeds_ore' in a['sub']),
    'cases': ('redundant or trivial-merge split', lambda a: 'cases.redundant' in a['sub'] or 'cases.trivial_merge' in a['sub']),
    'disj_syll': ('∨E with an ex falso branch not refuted by its case', lambda a: 'cases' in a['u'] and 'ex_falso' in a['u'] and 'disj_syll' not in a['u']),
    'neg_intro': ('¬I consumed by DN (a reductio) or vacuous ¬I', lambda a: ('contradiction' in a['u'] and 'neg_intro' not in a['u']) or 'neg_intro.vacuous' in a['sub']),
    'mod_tollens': ('¬I with another route (∧E, ∨I, conditional assumption, chain)', lambda a: any(s in a['sub'] for s in ('neg_intro.and_elim', 'neg_intro.or_weaken', 'neg_intro.imp_hyp', 'mod_tollens.chain', 'mod_tollens.neg_side'))),
    'ex_falso': ('ex falso from inconsistent premises inside a case', lambda a: 'ex_falso.inconsistent_premises' in a['sub'] and 'cases' in a['u']),
    'contradiction': ('template reductio or DN on a premise', lambda a: 'contradiction.template' in a['sub'] or 'dne.on_premise' in a['sub']),
    'dne': ('DN on an assumption or on a supplied derived ¬¬', lambda a: 'dne.on_hypothesis' in a['sub'] or 'dne.on_derived' in a['sub']),
    'lem': ('a derived X ∨ ¬X without DN, or LEM with cases', lambda a: 'lem' in a['u'] or 'cases.on_lem' in a['sub']),
    'lemma_reuse': ('a premise or assumption cited twice', lambda a: 'lemma_reuse' not in a['u'] and a['Lp'] >= 6),
}


def load_labels(fn):
    return [json.loads(l) for l in gzip.open(fn, 'rt')]


def main():
    rng = random.Random(20261018)
    k12_lab = load_labels('artifacts/ps/labels/k12.jsonl.gz')
    tb_lab = load_labels('artifacts/ps/labels/tb_schema_search.jsonl.gz')
    k12_src = [json.loads(l) for l in gzip.open('data/ps/in/train_k12.jsonl.gz', 'rt')]
    tb_src = [json.loads(l) for l in open('data/ps/search/tb_schema.checked.jsonl')]
    pool = [('k12', a, k12_src[a['i']]) for a in k12_lab if a['Lp'] <= 14] + \
           [('tb_schema', a, tb_src[a['i']]) for a in tb_lab if not a.get('parse_fail') and a['Lp'] <= 16]
    items, used = [], set()

    def take(cands, k, role, target):
        cands = [c for c in cands if (c[0], c[1]['i']) not in used]
        for c in rng.sample(cands, min(k, len(cands))):
            used.add((c[0], c[1]['i']))
            items.append((target, role, c))

    for s in STRATS:
        pos = [c for c in pool if s in c[1]['u'] and c[0] == 'k12']
        if len(pos) < 200:      # rare in K12: half from the textbook-schema search proofs
            take(pos, 6, 'positive', s)
            take([c for c in pool if s in c[1]['u'] and c[0] == 'tb_schema'], 6, 'positive', s)
        else:
            take(pos, 12, 'positive', s)
        take([c for c in pool if s not in c[1]['u'] and c[0] == 'k12'], 4, 'negative', s)
        take([c for c in pool if BORDER[s][1](c[1])], 4, 'borderline', s)
    rng.shuffle(items)
    os.makedirs('data/ps/validation', exist_ok=True); os.makedirs('artifacts/ps/validation', exist_ok=True)
    groups = {'a': STRATS[0:5], 'b': STRATS[5:9], 'c': STRATS[9:13]}
    key = open('data/ps/validation/spot_key.jsonl', 'w')
    for g, strs in groups.items():
        with open(f'data/ps/validation/spot_{g}.jsonl', 'w') as f:
            n = 0
            for target, role, (src, a, r) in items:
                if target not in strs:
                    continue
                n += 1
                sid = f'{g}{n:03d}'
                text = lines_to_text(prune_lines(parse(get_proof(r)))).replace(' QED', '')
                f.write(json.dumps({'id': sid, 'target': target, 'prompt': r['prompt'],
                                    'proof_lines': [x.strip().rstrip(';').strip() for x in text.split(' ; ')]}) + '\n')
                key.write(json.dumps({'id': sid, 'target': target, 'role': role, 'src': src, 'i': a['i'], 'border': BORDER[target][0] if role == 'borderline' else None,
                                      'uses_target': target in a['u'], 'primary': a['pri'], 'sub': a['sub']}) + '\n')
            print(g, n)
    key.close()


if __name__ == '__main__':
    main()
