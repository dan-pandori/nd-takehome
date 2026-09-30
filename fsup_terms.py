#!/usr/bin/env python3
"""frontier-supply: proof length of the read-out solves in lines AND elaborated Lean term size (AGENT_POLICY).
For every read-out file artifacts/fsup/rr/<label>__{lp2,rr}.jsonl: the shortest accepted proof (written lines) of each
solved theorem, re-checked alone by `lean_check` (which also returns the term size).  Also re-checks the kept supply
targets' shortest proofs (supply_found_8).  -> artifacts/fsup/terms.json; per-arm medians on stdout.

  python3 fsup_terms.py [--workers 2]
"""
import argparse, collections, glob, json, os, statistics
import nd2lean
from lean_check import check


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=2); a = ap.parse_args()
    items = []     # (label, file kind, name, L_true_lb, written, prompt, proof)
    for fn in sorted(glob.glob('artifacts/fsup/rr/*__*.jsonl')):
        lab, kind = os.path.basename(fn)[:-6].split('__')
        for l in open(fn):
            r = json.loads(l)
            if not r['solved']:
                continue
            i = min(range(len(r['proofs'])), key=lambda j: r['written_lens'][j] or 999)
            items.append((lab, kind, r['name'], r.get('L_true_lb'), r['written_lens'][i], r['prompt'], r['proofs'][i]))
    for fn in sorted(glob.glob('artifacts/fsup/la_S_s*/supply_found_8.jsonl')):
        lab = fn.split('/')[2]; best = {}
        for l in open(fn):
            x = json.loads(l)
            if x['name'] not in best or (x['written'] or 999) < (best[x['name']]['written'] or 999):
                best[x['name']] = x
        for x in best.values():
            items.append((lab, 'supply_' + x['source'], x['name'], x['ub'], x['written'], x['prompt'], x['proof']))
    srcs, keep, bad_tr = [], [], 0
    for it in items:
        try:
            srcs.append(nd2lean.translate(it[5], it[6], require_all_pr=False)); keep.append(it)
        except Exception:
            bad_tr += 1
    res, wall, _ = check(srcs, workers=a.workers)
    by = collections.defaultdict(list); rej = collections.Counter()
    for it, r in zip(keep, res):
        if r['ok'] and r['size'] is not None:
            by[(it[0], it[1])].append((it[4], r['size']))
        else:
            rej[(it[0], it[1])] += 1
    out = {'n_items': len(items), 'translate_failed': bad_tr, 'lean_rejected': {f'{k[0]}__{k[1]}': v for k, v in rej.items()},
           'lean_wall_s': wall, 'per_file': {}}
    for (lab, kind), v in sorted(by.items()):
        ln = [x for x, _ in v]; sz = [y for _, y in v]
        out['per_file'][f'{lab}__{kind}'] = {'n': len(v), 'lines_median': statistics.median(ln), 'lines_max': max(ln),
                                             'term_median': statistics.median(sz), 'term_max': max(sz)}
        print(f'{lab:14s} {kind:10s} n {len(v):4d} lines med {statistics.median(ln):5.1f} max {max(ln):3d}  term med {statistics.median(sz):6.1f} max {max(sz)}')
    print('translate failed', bad_tr, 'lean rejected', sum(rej.values()), f'lean wall {wall:.0f}s')
    json.dump(out, open('artifacts/fsup/terms.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
