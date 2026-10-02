"""Summarise p2_necessity_textbook72.jsonl: requires_X = full search finds a proof <= bound and the X-free search fails
without timeout; 'costlier' = X-free proof exists but is longer; 'unknown' = full search fails or the X-free search times out."""
import json, collections
R = [json.loads(l) for l in open('radical_scoping/p2_necessity_textbook72.jsonl')]
print(f"n={len(R)} full_found={sum(r['full'] is not None for r in R)} full_timeout={sum(bool(r['full_timeout']) for r in R)} "
      f"errors={sum(bool(r.get(k)) for r in R for k in ('full_err','no_ore_err','no_dn_err'))}")
for t in ('no_ore', 'no_dn'):
    c = collections.Counter()
    for r in R:
        if r['full'] is None: c['unknown_full_fail'] += 1
        elif r[t] is None and r[t + '_timeout']: c['unknown_timeout'] += 1
        elif r[t] is None: c['requires'] += 1
        elif r[t] > r['full']: c['costlier'] += 1
        else: c['not_needed'] += 1
    print(t, dict(c))
both = sum(r['full'] is not None and r['no_ore'] is None and not r['no_ore_timeout'] and r['no_dn'] is None and not r['no_dn_timeout'] for r in R)
print('requires both ORE and DN:', both)
