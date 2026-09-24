#!/usr/bin/env python3
"""cap-horizon: the long pool (pruned lengths 7-14) from the CONTROL's generator settings.

  python3 kh_gen.py gen --workers 2 --tries 12000000 --out data/kh/raw_long
  python3 kh_gen.py merge --glob 'data/kh/raw_long.w*.jsonl' --out data/kh/pool_long_kh.jsonl

Generator: gen.sample_one short mode (NOT --long), Gen(max_prem=3, max_depth=3) -- the take-home
generator's own knobs, probabilities untouched.  The only filter is on the output: pruned length in
[7, 14].  There is a per-LENGTH storage cap (to bound disk); there is deliberately NO per-pattern cap
(`make_coverage_sets.py gen`'s --cap_np/--cap_pat), because those caps are what pattern-enriched the
pool that produced ds-composition's 07:10 confound.  Within a length bin the stored records are the
first N encountered, an unbiased sample of that length's natural distribution.

Every record is re-verified with nd_verify at generation time (assert n_lines == pruned length).
Depth-3 is NOT excluded here; exclusion (pruned `pat.depth3` OR written box depth >= 3) and the
renaming-class exclusions happen at assembly, so the pool's own depth-3 rate stays measurable.
"""
import argparse, collections, glob, json, os, random, sys, time, multiprocessing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from gen import Gen, sample_one, canon_key, Fail

LO, HI = 7, 14
CAPS = {7: 45000, 8: 45000, 9: 30000, 10: 30000, 11: 30000, 12: 30000, 13: 30000, 14: 30000}


def worker(args):
    seed, tries, out = args
    rng = random.Random(seed)
    g = Gen(rng, max_prem=3, max_depth=3)
    seen = set()
    per_len = collections.Counter()
    raw_len = collections.Counter()
    stats = collections.Counter()
    t0 = time.time()
    with open(out, 'w') as fo:
        for _ in range(tries):
            stats['tries'] += 1
            try:
                r = sample_one(g, rng, False)
            except (Fail, RecursionError):
                stats['fail'] += 1
                continue
            L = r['n_lines']
            raw_len[L] += 1
            if L < LO or L > HI:
                stats['len_out'] += 1
                continue
            if per_len[L] >= CAPS[L]:
                stats['len_full'] += 1
                continue
            key = canon_key(r['thm'])
            if key in seen:
                stats['dup_class'] += 1
                continue
            ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
            if not ok:
                stats['VERIFIER_REJECT'] += 1
                print('REJECT', reason, file=sys.stderr)
                continue
            assert nl == L, (nl, L)
            seen.add(key)
            r['key'] = key
            fo.write(json.dumps(r) + '\n')
            per_len[L] += 1
            if sum(per_len.values()) % 25000 == 0:
                print(f'{out}: {sum(per_len.values())} stored {time.time()-t0:.0f}s {dict(per_len)}', flush=True)
            if all(per_len[L2] >= CAPS[L2] for L2 in range(LO, HI + 1)):
                stats['all_full'] = 1
                break
    return {'out': out, 'seed': seed, 'secs': round(time.time() - t0, 1), 'stats': dict(stats),
            'per_len': {str(k): per_len[k] for k in sorted(per_len)},
            'raw_len_all': {str(k): raw_len[k] for k in sorted(raw_len)}}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('gen')
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--tries', type=int, default=12000000, help='tries PER worker')
    p.add_argument('--seed0', type=int, default=31000)
    p.add_argument('--out', default='data/kh/raw_long')
    m = sub.add_parser('merge')
    m.add_argument('--glob', default='data/kh/raw_long.w*.jsonl')
    m.add_argument('--out', default='data/kh/pool_long_kh.jsonl')
    a = ap.parse_args()
    if a.cmd == 'gen':
        os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
        jobs = [(a.seed0 + i, a.tries, f'{a.out}.w{i}.jsonl') for i in range(a.workers)]
        with multiprocessing.get_context('fork').Pool(a.workers) as pool:
            reps = pool.map(worker, jobs)
        rep = {'generator': 'gen.sample_one short mode, Gen(max_prem=3, max_depth=3), probabilities untouched',
               'filter': f'pruned length in [{LO},{HI}]; per-length storage caps {CAPS}; no per-pattern cap',
               'workers': reps}
        json.dump(rep, open(f'{a.out}_genreport.json', 'w'), indent=1)
        tot = collections.Counter()
        for r in reps:
            for k, v in r['per_len'].items():
                tot[int(k)] += v
        print('TOTAL (pre-merge, per worker dedup only):', dict(sorted(tot.items())))
    else:
        seen = set()
        per_len = collections.Counter()
        dup = 0
        with open(a.out, 'w') as fo:
            for fn in sorted(glob.glob(a.glob)):
                for l in open(fn):
                    r = json.loads(l)
                    if r['key'] in seen:
                        dup += 1
                        continue
                    seen.add(r['key'])
                    per_len[r['n_lines']] += 1
                    fo.write(l)
        rep = {'out': a.out, 'n': len(seen), 'cross_worker_dup_classes': dup,
               'per_len': {str(k): per_len[k] for k in sorted(per_len)}}
        json.dump(rep, open(a.out.replace('.jsonl', '_mergereport.json'), 'w'), indent=1)
        print(json.dumps(rep))


if __name__ == '__main__':
    main()
