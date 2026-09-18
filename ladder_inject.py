#!/usr/bin/env python3
"""T5 precursor injection set: <= 6-line verified generator proofs whose shape matches what the UNSOLVED RL targets need.

Shapes are read from the unsolved targets only (a training pool; no evaluation pool is read):
  * generator targets: the patterns of their generating proofs (patterns.py: derived_ore, reductio, depth3;
    patterns2.py: depth4, impe_chain4, nested_ore, impi_ore, negi_ande_hyp) -> cap-6 pool proofs with the same pattern,
    drawn in proportion to how many unsolved targets need each pattern;
  * textbook targets: their schema name -> cap-6 pool theorems that match a precursor sub-step template of that schema
    (precursors.py TEMPLATES).
Every injected record is re-verified and asserted <= 6 lines; classes in `eval_keys` are excluded.
"""
import json, collections, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from patterns import classify
from patterns2 import classify2
from precursors import classify_thm, TEMPLATES

PATS = ('derived_ore', 'reductio', 'depth3', 'depth4', 'impe_chain4', 'nested_ore', 'impi_ore', 'negi_ande_hyp')
SCHEMA_ALIAS = {'dn_intro': 'dn_forms', 'dn_elim': 'dn_forms', 'triple_negation': 'dn_forms'}


def shapes_of(proof):
    c = classify(proof); c2 = classify2(proof)
    return {p for p in PATS if (c.get(p) if p in c else c2.get(p))}


def build_injection(targets, found, pool_fn, eval_keys, n_total, rng, per_schema_cap=150):
    unsolved = [t for t in targets if not found.get(t['name'])]
    need = collections.Counter(); need_schema = collections.Counter()
    for t in unsolved:
        if t.get('source') == 'gen' and t.get('gen_proof'):
            for p in shapes_of(t['gen_proof']):
                need[p] += 1
        elif t.get('schema'):
            need_schema[SCHEMA_ALIAS.get(t['schema'], t['schema'])] += 1
    log = {'unsolved': len(unsolved), 'need_patterns': dict(need), 'need_schemas': dict(need_schema)}
    by_pat = collections.defaultdict(list); by_schema = collections.defaultdict(list)
    n_pool = n_excl = 0
    for l in open(pool_fn):
        r = json.loads(l); n_pool += 1
        if r['n_lines'] > 6 or r['key'] in eval_keys:
            n_excl += 1; continue
        for p in shapes_of(r['proof']):
            if p in need:
                by_pat[p].append(r)
        if need_schema:
            for s, _, _ in classify_thm(r['prompt']):
                if s in need_schema:
                    by_schema[s].append(r)
    log['pool'] = n_pool; log['pool_excluded'] = n_excl
    log['available'] = {p: len(v) for p, v in by_pat.items()}; log['available_schema'] = {s: len(v) for s, v in by_schema.items()}
    chosen, seen = [], set()
    # schemata first (their sub-steps are few), capped per schema
    for s, rs in by_schema.items():
        rng.shuffle(rs); rs.sort(key=lambda r: -r['n_lines'])     # prefer the longer sub-steps
        for r in rs[:per_schema_cap]:
            if r['key'] not in seen:
                seen.add(r['key']); chosen.append((r, f'schema:{s}'))
    # patterns in proportion to need
    budget = max(0, n_total - len(chosen))
    tot = sum(need[p] for p in by_pat) or 1
    for p, rs in by_pat.items():
        rng.shuffle(rs)
        q = int(round(budget * need[p] / tot))
        got = 0
        for r in rs:
            if got >= q:
                break
            if r['key'] in seen:
                continue
            seen.add(r['key']); chosen.append((r, f'pattern:{p}')); got += 1
    out = []
    for r, why in chosen:
        ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
        assert ok and nl == r['n_lines'] <= 6, (reason, r)
        out.append({'prompt': r['prompt'], 'proof': r['proof'], 'n_lines': nl, 'thm': r['thm'], 'key': r['key'], 'why': why})
    log['chosen'] = dict(collections.Counter(x['why'] for x in out)); log['n'] = len(out)
    log['by_len'] = dict(sorted(collections.Counter(x['n_lines'] for x in out).items()))
    return out, log


if __name__ == '__main__':
    import argparse, random
    ap = argparse.ArgumentParser(); ap.add_argument('--targets', required=True); ap.add_argument('--found', default=None); ap.add_argument('--pool', required=True); ap.add_argument('--n', type=int, default=3000)
    a = ap.parse_args()
    targets = [json.loads(l) for l in open(a.targets)]
    found = collections.defaultdict(list)
    if a.found:
        for l in open(a.found):
            x = json.loads(l); found[x['name']].append(x)
    out, log = build_injection(targets, found, a.pool, set(), a.n, random.Random(0))
    print(json.dumps(log, indent=1))
