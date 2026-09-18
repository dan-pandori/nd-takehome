#!/usr/bin/env python3
"""ladder-A pools: transfer and RL-target pools labelled with the true (restricted-space) minimal proof length.

  python make_ladder_pools.py --long data/ladder/pool_long.jsonl --long_minlen data/ladder/pool_long_minlen.jsonl \
      --textbook data/ladder/raw_textbook.jsonl --textbook_minlen data/ladder/raw_textbook_minlen.jsonl --outdir data/ladder

Inputs: a merged strict-long generator pool (make_coverage_sets.py gen --long / merge), a textbook schemata pool
(textbook_pool.py), and their minlen.py labels (bound 14; a record's `min_lines_ub` is L_true when not None).
Keeps theorems with 7 <= L_true <= 14, excludes every renaming class in Stage-1 train / held-out, the take-home's
rl_targets / transfer, and validation-36; splits into transfer / rl_targets (class-disjoint) with the same
per-(source, L_true) stratification; <= --per_schema textbook instances per schema per pool; L_true 7 and 8 capped
per pool (--cap78) so the frontier bins are not drowned; everything else -> reserve. Writes POOLS.md.
"""
import argparse, json, os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key


def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--long', required=True); ap.add_argument('--long_minlen', required=True)
    ap.add_argument('--textbook', required=True); ap.add_argument('--textbook_minlen', required=True)
    ap.add_argument('--outdir', default='data/ladder')
    ap.add_argument('--exclude', nargs='*', default=['data/train.jsonl', 'data/heldout.jsonl', 'data/rl_targets.jsonl', 'data/transfer.jsonl'])
    ap.add_argument('--n_transfer', type=int, default=100000); ap.add_argument('--n_targets', type=int, default=100000)
    ap.add_argument('--per_schema', type=int, default=40); ap.add_argument('--cap78', type=int, default=300)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    excl = {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    n_val = len(excl)
    for fn in a.exclude:
        for l in open(fn):
            if l.strip():
                excl.add(json.loads(l)['key'])
    st = collections.Counter()
    cands, seen = [], set()
    for src, fn, fnl in (('gen', a.long, a.long_minlen), ('textbook', a.textbook, a.textbook_minlen)):
        recs = {r['name']: r for r in rd(fn)}
        labels = rd(fnl)
        st[f'{src}_n'] = len(labels)
        for x in labels:
            r = recs[x['name']]
            key = r.get('key') or canon_key(r['thm'])
            L = x['min_lines_ub']
            if L is None:
                st[f'{src}_unresolved'] += 1
                st[f'{src}_timeout'] += bool(x.get('timeout'))
                continue
            st[f'{src}_L{L}'] += 1
            if L < 7 or L > 14:
                st[f'{src}_out_of_range'] += 1; continue
            if key in excl:
                st[f'{src}_excluded_class'] += 1; continue
            if key in seen:
                st[f'{src}_dup_class'] += 1; continue
            seen.add(key)
            rec = {'thm': r['thm'], 'key': key, 'prompt': r['prompt'], 'n_lines': L, 'L_true': L, 'minlen_bound': x['bound'],
                   'source': src, 'schema': r.get('schema'), 'gen_lines': r.get('n_lines') if src == 'gen' else None,
                   'n_prem': r.get('n_prem'), 'rules': r.get('rules')}
            if src == 'gen':
                rec['gen_proof'] = r['proof']       # generating proof: an upper bound, never trained on; T5 reads its shapes
            cands.append(rec)
    # stratified split
    strata = collections.defaultdict(list)
    for r in cands:
        strata[(r['source'], r['schema'] or 'gen', r['L_true'])].append(r)
    transfer, targets, reserve = [], [], []
    schema_count = {'transfer': collections.Counter(), 'targets': collections.Counter()}
    bin_count = {'transfer': collections.Counter(), 'targets': collections.Counter()}
    for k in sorted(strata, key=lambda k: (k[0] != 'textbook', k)):      # textbook strata first (per-schema cap), generator fills the rest
        rs = strata[k]; rng.shuffle(rs)
        for i, r in enumerate(rs):
            pool = 'transfer' if i % 2 == 0 else 'targets'
            if r['source'] == 'textbook' and schema_count[pool][r['schema']] >= a.per_schema:
                reserve.append(r); continue
            if r['L_true'] in (7, 8) and bin_count[pool][r['L_true']] >= a.cap78:
                reserve.append(r); continue
            (transfer if pool == 'transfer' else targets).append(r)
            schema_count[pool][r['schema']] += 1; bin_count[pool][r['L_true']] += 1
    rng.shuffle(transfer); rng.shuffle(targets)
    if len(transfer) > a.n_transfer:
        reserve += transfer[a.n_transfer:]; transfer = transfer[:a.n_transfer]
    if len(targets) > a.n_targets:
        reserve += targets[a.n_targets:]; targets = targets[:a.n_targets]
    keys = [set(r['key'] for r in p) for p in (transfer, targets, reserve)]
    assert not (keys[0] & keys[1]) and not (keys[0] & keys[2]) and not (keys[1] & keys[2])
    assert not (keys[0] | keys[1] | keys[2]) & excl
    os.makedirs(a.outdir, exist_ok=True)
    summ = {'stats': dict(st), 'excluded_classes': len(excl), 'val36_classes': n_val, 'candidates': len(cands)}
    for name, pool in (('transfer', transfer), ('rl_targets', targets), ('reserve', reserve)):
        with open(f'{a.outdir}/{name}.jsonl', 'w') as f:
            for i, r in enumerate(pool):
                f.write(json.dumps({'name': f'la_{name}_{i}', **r}) + '\n')
        summ[name] = {'n': len(pool), 'by_L_true': dict(sorted(collections.Counter(r['L_true'] for r in pool).items())),
                      'by_source': dict(collections.Counter(r['source'] for r in pool)),
                      'by_schema': dict(sorted(collections.Counter(r['schema'] for r in pool if r['schema']).items())),
                      'by_L_true_source': {f'{s}_{L}': c for (s, L), c in sorted(collections.Counter((r['source'], r['L_true']) for r in pool).items())}}
    json.dump(summ, open(f'{a.outdir}/pools_summary.json', 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
