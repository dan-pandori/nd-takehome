"""Recount 4 — base rates at pass@2,000 per arm x seed x pool.

Every distinct stored proof is re-verified with nd_verify and re-classified with
my own predicates; 'solved' and 'solved with a pattern proof' are re-decided from
those, not read from the executor's fields.
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text

POOLS = {
    'd3sub': ('data/dsc/targets_depth3_sub250.jsonl', 'depth3'),
    'd3req': ('data/r3_1/depth3_req.jsonl', 'depth3'),
    'redreq': ('data/p2/targets_reductio_req.jsonl', 'derived_dn'),
}
res = {}
ndbad = []
for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
    for s in [0, 1]:
        for pool, (pp, pat) in POOLS.items():
            f = 'artifacts/dsc/cov_%s_s%d_%s.s0.jsonl' % (arm, s, pool)
            if not os.path.exists(f):
                print('MISSING', f); continue
            n = 0; solved = 0; solved_pat = 0
            tried = 0; hits = 0; hits_pat = 0
            distinct_pat_ge8 = set(); distinct_pat = 0; distinct_ok = 0
            strat_n = collections.Counter(); strat_s = collections.Counter(); strat_sp = collections.Counter()
            schema_n = collections.Counter(); schema_s = collections.Counter()
            bad = 0
            for r in rv.load(f):
                n += 1
                tried += r['n_tried']
                st = r.get('min_lines_ub'); strat_n[st] += 1
                sc = r.get('schema'); schema_n[sc] += 1
                any_ok = False; any_pat = False
                for pf in r['proofs']:
                    v, why, _ = verify_text(r['prompt'] + ' ' + pf['proof'])
                    if not v:
                        bad += 1
                        ndbad.append({'file': f, 'name': r['name'], 'why': why, 'proof': pf['proof']})
                        continue
                    distinct_ok += 1
                    any_ok = True
                    hits += pf['count']
                    lines = rv.try_parse(pf['proof'])
                    pl = rv.prune(lines)
                    ispat = {'depth3': rv.is_depth3, 'derived_dn': rv.is_derived_dn}[pat](pl)
                    if ispat:
                        any_pat = True
                        distinct_pat += 1
                        hits_pat += pf['count']
                        if len(pl) >= 8:
                            distinct_pat_ge8.add(rv.norm(pf['proof']))
                if any_ok:
                    solved += 1; strat_s[st] += 1
                    schema_s[sc] += 1
                if any_pat:
                    solved_pat += 1; strat_sp[st] += 1
            res['%s_s%d_%s' % (arm, s, pool)] = {
                'pool': pp, 'pattern': pat, 'n_targets': n, 'n_tried_total': tried,
                'solved': solved, 'rate_solved': round(solved / n, 5),
                'solved_with_pattern': solved_pat, 'rate_solved_with_pattern': round(solved_pat / n, 5),
                'per_sample_rate': round(hits / tried, 8) if tried else 0,
                'per_sample_rate_pattern': round(hits_pat / tried, 8) if tried else 0,
                'distinct_accepted': distinct_ok, 'distinct_pattern': distinct_pat,
                'distinct_pattern_ge8_pruned': len(distinct_pat_ge8),
                'nd_verify_rejects_among_stored': bad,
                'by_stratum': {str(k): {'n': strat_n[k], 'solved': strat_s[k], 'solved_pat': strat_sp[k]} for k in sorted(strat_n, key=lambda x: (x is None, x))},
                'by_schema_solved': {str(k): [schema_s[k], schema_n[k]] for k in sorted(schema_n, key=str)} if pool == 'redreq' else None,
            }
            print('%s_s%d_%s' % (arm, s, pool), res['%s_s%d_%s' % (arm, s, pool)]['solved'],
                  res['%s_s%d_%s' % (arm, s, pool)]['solved_with_pattern'], 'ndbad', bad, flush=True)
json.dump(res, open('recount/out_coverage.json', 'w'), indent=1)
json.dump(ndbad[:50], open('recount/out_coverage_ndbad.json', 'w'), indent=1)
