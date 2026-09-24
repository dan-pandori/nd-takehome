"""Reviewer recount 2: coverage pass@2000 files.  Everything re-derived from the raw
`proofs[]` entries: acceptance = nd_verify (re-run here) AND Lean (texts_ok non-empty),
distinct proofs deduped on the START-INDEX-NORMALISED proof string, lengths from the
reviewer's own pruner."""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib
from nd_verify import verify_text

ROOT = '/home/dan/review/cap-horizon'
POOLINFO = {}
for p, fn in [('redreq', 'data/p2/targets_reductio_req.jsonl'), ('d3req', 'data/r3_1/depth3_req.jsonl')]:
    POOLINFO[p] = {r['name']: r for r in rvlib.rd(f'{ROOT}/{fn}')}


def recount(fn, pool):
    rows = [json.loads(l) for l in open(fn)]
    info = POOLINFO[pool]
    solved = set()
    acc = []            # accepted distinct proofs
    nd_fail = []        # counted proofs nd_verify rejects here
    lean_rej_counted = 0
    per_target_n = {}
    names_seen = []
    for r in rows:
        names_seen.append(r['name'])
        seen = set()
        n_here = 0
        for p in r['proofs']:
            key = rvlib.norm_start(p['proof'])
            ok_lean = len(p.get('texts_ok', [])) > 0
            if p.get('texts_rej'):
                lean_rej_counted += 1
            ok_nd = verify_text(r['prompt'] + ' ' + p['proof'])[0]
            if not ok_nd:
                nd_fail.append((r['name'], p['proof']))
            if not (ok_lean and ok_nd):
                continue
            if key in seen:
                continue
            seen.add(key)
            n_here += 1
            acc.append({'name': r['name'], 'proof': p['proof'],
                        'pruned': rvlib.pruned_length(p['proof']),
                        'written': rvlib.written_length(p['proof']),
                        'term': rvlib.term_size(p['proof']),
                        'first': p.get('first'),
                        'stratum': info[r['name']].get('min_lines_ub')})
        per_target_n[r['name']] = n_here
        if n_here:
            solved.add(r['name'])
    ph = collections.Counter(a['pruned'] for a in acc)
    wh = collections.Counter(a['written'] for a in acc)
    strat = collections.Counter()
    strat_tot = collections.Counter()
    for r in rows:
        s = info[r['name']].get('min_lines_ub')
        strat_tot[s] += 1
        if r['name'] in solved:
            strat[s] += 1
    return {
        'file': os.path.relpath(fn, ROOT),
        'targets': len(rows),
        'solved': len(solved),
        'accepted_distinct_proofs': len(acc),
        'max_pruned': max([a['pruned'] for a in acc], default=0),
        'max_written': max([a['written'] for a in acc], default=0),
        'pruned_ge': {L: sum(c for k, c in ph.items() if k >= L) for L in (8, 10, 12)},
        'written_ge': {L: sum(c for k, c in wh.items() if k >= L) for L in (8, 10, 12)},
        'pruned_hist': dict(sorted(ph.items())),
        'written_hist': dict(sorted(wh.items())),
        'mean_term_size': round(sum(a['term'] for a in acc) / len(acc), 2) if acc else None,
        'max_term_size': max([a['term'] for a in acc], default=None),
        'by_stratum_solved': {str(k): [strat[k], strat_tot[k]] for k in sorted(strat_tot, key=lambda x: (x is None, x))},
        'counted_proofs_nd_verify_rejects': len(nd_fail),
        'counted_proofs_with_lean_rejected_texts': lean_rej_counted,
    }, acc


if __name__ == '__main__':
    out = {}
    allacc = {}
    files = sorted(glob.glob(f'{ROOT}/artifacts/kh/cov*_*.s0.jsonl')) + \
            sorted(glob.glob(f'{ROOT}/artifacts/dsc_inherited/cov_*.s0.jsonl'))
    for fn in files:
        b = os.path.basename(fn)[:-9]
        pool = 'redreq' if 'redreq' in b else 'd3req'
        res, acc = recount(fn, pool)
        out[b] = res
        allacc[b] = acc
        print(b, json.dumps({k: v for k, v in res.items() if k not in ('pruned_hist', 'written_hist')}))
        sys.stdout.flush()
    json.dump(out, open(f'{ROOT}/rv/out_cov.json', 'w'), indent=1)
    with open(f'{ROOT}/rv/out_cov_proofs.jsonl', 'w') as f:
        for b, acc in allacc.items():
            for a in acc:
                a['src'] = b
                f.write(json.dumps(a) + '\n')
