"""K12 extras: v0 direct reading (root NEGE not direct), P1/P2 pattern proxies, sigma flags. Reviewer labels only."""
import gzip, json, collections
O = '/home/dan/review/proof-strategies/review_ps/out'
c = collections.Counter()
for l in gzip.open(f'{O}/labels_k12.jsonl.gz', 'rt'):
    a = json.loads(l)
    s = set(a['sub']); u = set(a['uses'])
    c['n'] += 1
    c['direct_mp_or_ande'] += ('direct.mp' in s or 'direct.ande' in s)
    c['direct_only_neg_elim_root'] += ('direct' in u and not ('direct.mp' in s or 'direct.ande' in s))
    c['no_uses_if_root_nege_not_direct'] += (u <= {'direct'} and 'direct.mp' not in s and 'direct.ande' not in s)
    c['ore_on_hyp_or_derived'] += ('cases.on_hypothesis' in s or 'cases.on_derived' in s)
    c['ore_on_derived'] += ('cases.on_derived' in s)
    c['ore_on_derived_not_trivial_merge'] += ('cases.on_derived' in s and 'cases.trivial_merge' not in s)
    c['sigma'] += bool(a.get('sigma')); c['sigma_strict'] += bool(a.get('sigma_strict')); c['sigma_plus'] += bool(a.get('sigma_plus'))
    c['nested'] += ('cases.nested' in s)
    c['v0_mt'] += ('mod_tollens' in a['v0']); c['v0_ds'] += ('disj_syll' in a['v0']); c['v0_lem'] += ('lem' in a['v0'])
    c['contradiction_sigma_sub'] += ('contradiction.sigma' in s)
print(dict(c))
json.dump(dict(c), open('/home/dan/review/proof-strategies/phase2/scripts/tab_k12extra.out.json', 'w'), indent=1)
