#!/usr/bin/env python3
"""long-pool: assemble data/ladder/transfer_long.jsonl from the staged minlen labels (pod/lpool/label.sh) and check
renaming-class disjointness against every training / evaluation set on file.

  python3 lpool_assemble.py --chunks g1 g2 g3 g4 tb --excl_manifest artifacts/lpool/excl_manifest.txt --out data/ladder/transfer_long.jsonl

Label of a record = the first stage (bounds 10, 12, 14, 16) whose search returned a proof; a timeout at any stage it
reached = label unknown (excluded, counted); no proof at bound 16 and no timeout = `L_true >= 17` (lower bound only,
written to transfer_long_ge17.jsonl, not binned).  A label L is final: every smaller total was searched to exhaustion
(iterative deepening, restricted formula space as in POOLS.md).
Renaming class = gen.canon_key over the prompt tokens (atoms relabelled by first appearance, premise order kept).
Assembly (seed 0): per bin 11..16, generator theorems up to --cap_gen, textbook up to --cap_tb per schema.
Writes a summary json (counts, timeouts per stage and bin, disjointness table) next to --out.
"""
import argparse, json, os, sys, gzip, random, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key

STAGES = (10, 12, 14, 16)
BINS = range(11, 17)


def pkey(prompt):
    return canon_key(prompt.replace('THM ', '', 1).replace(' PRF', '').strip())


def opener(fn):
    return gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chunks', nargs='+', required=True); ap.add_argument('--dir', default='data/lp')
    ap.add_argument('--excl_manifest', required=True, help='text file: one exclusion jsonl(.gz) path per line')
    ap.add_argument('--out', required=True); ap.add_argument('--cap_gen', type=int, default=300)
    ap.add_argument('--cap_tb', type=int, default=40); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    recs, stats = {}, collections.Counter()
    tout = collections.Counter()          # (stage bound, chunk) -> timeouts
    for c in a.chunks:
        src = {}
        for l in open(f'{a.dir}/{c}.jsonl'):
            r = json.loads(l); src[r['name']] = r
        stats[f'{c}:generated'] = len(src)
        lab = {}                          # name -> (L or None, bound, proof) ; missing = never reached
        unknown = set()
        for b in STAGES:
            fn = f'{a.dir}/{c}_ml{b}.jsonl'
            if not os.path.exists(fn):
                continue
            for l in open(fn):
                r = json.loads(l)
                if r['name'] in lab or r['name'] in unknown:
                    continue
                if r.get('timeout') or r.get('error'):
                    unknown.add(r['name']); tout[(b, c)] += 1
                elif r['min_lines_ub'] is not None:
                    lab[r['name']] = (r['min_lines_ub'], b, r['proof'], r.get('secs'))
                elif b == 16:
                    lab[r['name']] = (None, 16, None, r.get('secs'))    # >= 17
        for name, (L, b, proof, secs) in lab.items():
            if L is not None and L < 11:
                continue
            s = src[name]
            tb = c == 'tb'
            out = {'name': f'lp_{name}', 'thm': s['thm'], 'key': pkey(s['prompt']), 'prompt': s['prompt'],
                   'n_lines': L, 'L_true': L, 'L_true_lb': 17 if L is None else L, 'minlen_bound': b,
                   'source': 'textbook' if tb else 'gen', 'schema': s.get('schema'), 'gen_lines': None if tb else s['n_lines'],
                   'n_prem': s.get('n_prem'), 'rules': None if tb else s.get('rules'), 'gen_proof': None if tb else s['proof'],
                   'minlen_proof': proof, 'minlen_secs': secs, 'chunk': c}
            k = out['key']
            if k in recs:
                stats['dup_class_across_chunks'] += 1; continue
            recs[k] = out
        stats[f'{c}:unknown'] = len(unknown)
    print('labelled >= 11 candidates', len(recs), file=sys.stderr)
    # disjointness: which candidate classes occur in any exclusion file
    keys = set(recs)
    hit_by = collections.defaultdict(set)
    files = [l.strip() for l in open(a.excl_manifest) if l.strip() and not l.startswith('#')]
    nfile = {}
    for fn in files:
        n = 0
        with opener(fn) as f:
            for l in f:
                i = l.find('"prompt": "')
                if i < 0:
                    continue
                j = l.find('"', i + 11)
                k = pkey(l[i + 11:j]); n += 1
                if k in keys:
                    hit_by[fn].add(k)
        nfile[fn] = n
        print(f'{fn}: {n} records, {len(hit_by[fn])} candidate classes hit', file=sys.stderr)
    excluded = set().union(*hit_by.values()) if hit_by else set()
    for c in ('targets/validation_36.jsonl',):
        for l in open(c):
            k = canon_key(json.loads(l)['thm'].strip())
            if k in keys:
                excluded.add(k); hit_by[c].add(k)
    rng = random.Random(a.seed)
    pool, ge17 = [], []
    avail = collections.defaultdict(list)
    for k in sorted(recs):
        r = recs[k]
        if k in excluded:
            continue
        if r['L_true'] is None:
            ge17.append(r); continue
        avail[(r['L_true'], r['source'], r['schema'])].append(r)
    table = {}
    for L in BINS:
        g = avail.get((L, 'gen', None), [])
        rng.shuffle(g); take = g[:a.cap_gen]
        tbs = sorted(s for (LL, src, s) in avail if LL == L and src == 'textbook')
        ttake = []
        for s in tbs:
            t = avail[(L, 'textbook', s)]; rng.shuffle(t); ttake += t[:a.cap_tb]
        pool += take + ttake
        table[L] = {'gen_available': len(g), 'gen_taken': len(take), 'textbook_taken': len(ttake),
                    'textbook_by_schema': {s: min(len(avail[(L, 'textbook', s)]), a.cap_tb) for s in tbs}}
    rng.shuffle(pool)
    for i, r in enumerate(pool):
        r['name'] = f'lp_transfer_{i}'
    assert len({r['key'] for r in pool}) == len(pool)
    assert not ({r['key'] for r in pool} & excluded)
    with open(a.out, 'w') as f:
        for r in pool:
            f.write(json.dumps(r) + '\n')
    with open(a.out.replace('.jsonl', '_ge17.jsonl'), 'w') as f:
        for r in ge17:
            f.write(json.dumps(r) + '\n')
    lab_all = collections.Counter((r['L_true'] if r['L_true'] is not None else '>=17', r['source']) for r in recs.values())
    summ = {'n': len(pool), 'bins': table, 'ge17_lower_bound_only': len(ge17), 'stats': dict(stats),
            'labelled_candidates_by_bin_source': {f'{L}|{s}': n for (L, s), n in sorted(lab_all.items(), key=str)},
            'timeouts_by_stage_chunk': {f'bound{b}|{c}': n for (b, c), n in sorted(tout.items())},
            'disjointness': {fn: {'records': nfile.get(fn), 'candidate_classes_hit': len(hit_by[fn])} for fn in files + ['targets/validation_36.jsonl']},
            'excluded_total': len(excluded), 'seed': a.seed, 'cap_gen': a.cap_gen, 'cap_tb': a.cap_tb}
    json.dump(summ, open(a.out.replace('.jsonl', '_summary.json'), 'w'), indent=1)
    print(json.dumps({k: summ[k] for k in ('n', 'bins', 'ge17_lower_bound_only', 'excluded_total')}, indent=1))


if __name__ == '__main__':
    main()
