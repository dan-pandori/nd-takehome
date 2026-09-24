"""Recount 3 — held-out greedy accuracy per arm x seed, re-verified with nd_verify.

Independent of the executor's summary json: every 'solved' is re-decided by
running nd_verify on the stored proof text against the stored prompt.
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text

HO = {r['name']: r for r in rv.load('data/p2/heldout.jsonl')}
# my own pattern classification of the generator proof of each held-out theorem
gp = {}
for n, r in HO.items():
    c = rv.classify(r['proof'])
    gp[n] = c

res = {}
for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
    for s in [0, 1]:
        p = 'artifacts/dsc/heldout_%s_s%d.jsonl' % (arm, s)
        if not os.path.exists(p):
            print('MISSING', p); continue
        n = solved = 0
        bylen = collections.Counter(); bylen_ok = collections.Counter()
        bypat = collections.Counter(); bypat_ok = collections.Counter()
        mismatch = 0
        wl = collections.Counter()
        tsz_ok = 0; tsz_gen = 0
        for r in rv.load(p):
            nm = r['name']; g = HO[nm]
            n += 1
            L = g['n_lines']
            c = gp[nm]
            anypat = c['depth3'] or c['reductio'] or c['derived_ore']
            bylen[L] += 1; bypat[anypat] += 1
            ok = False
            if r.get('proofs'):
                for pf in r['proofs']:
                    v, why, _ = verify_text(g['prompt'] + ' ' + pf)
                    if v:
                        ok = True
                        mine = rv.try_parse(pf)
                        wl[len(mine)] += 1
                        tsz_ok += rv.term_size(mine)
                        tsz_gen += rv.term_size(rv.try_parse(g['proof']))
                        break
            if ok != bool(r['solved']):
                mismatch += 1
            if ok:
                solved += 1; bylen_ok[L] += 1; bypat_ok[anypat] += 1
        res['%s_s%d' % (arm, s)] = {
            'n': n, 'solved': solved, 'rate': round(solved / n, 5),
            'verdict_mismatch_vs_file': mismatch,
            'by_len': {str(k): {'n': bylen[k], 'solved': bylen_ok[k], 'rate': round(bylen_ok[k] / bylen[k], 5)} for k in sorted(bylen)},
            'by_pattern': {('pat' if k else 'nopat'): {'n': bypat[k], 'solved': bypat_ok[k], 'rate': round(bypat_ok[k] / bypat[k], 5)} for k in bypat},
            'written_len_hist_of_solved': dict(sorted(wl.items())),
            'mean_term_size_solved': round(tsz_ok / max(solved, 1), 3),
            'mean_term_size_gen_of_solved': round(tsz_gen / max(solved, 1), 3),
        }
        print('%s_s%d' % (arm, s), res['%s_s%d' % (arm, s)]['rate'], 'mismatch', mismatch, flush=True)

# per-length x pattern breakdown (the 6-line bin is the interesting one)
res['_heldout_pool'] = {
    'n': len(HO),
    'by_len': dict(sorted(collections.Counter(r['n_lines'] for r in HO.values()).items())),
    'pattern_by_len': {},
}
for L in sorted({r['n_lines'] for r in HO.values()}):
    ns = [n for n, r in HO.items() if r['n_lines'] == L]
    res['_heldout_pool']['pattern_by_len'][str(L)] = {
        'n': len(ns),
        'pat': sum(1 for n in ns if gp[n]['depth3'] or gp[n]['reductio'] or gp[n]['derived_ore']),
        'depth3': sum(1 for n in ns if gp[n]['depth3']),
        'reductio': sum(1 for n in ns if gp[n]['reductio']),
        'derived_ore': sum(1 for n in ns if gp[n]['derived_ore']),
    }
json.dump(res, open('recount/out_heldout.json', 'w'), indent=1)
print(json.dumps(res['_heldout_pool'], indent=1))
