"""C2(a): survivors reached within the first 10,000 T0.8 attempts (first_hit), per state arm/seed; WP base s0 = 0 by construction."""
import json, collections
R = '/home/dan/work/claim-audit/audit/raw/'
surv = set(open(R + 'support-curves/data/sc/falsifier_survivors.txt').read().split())
for lab, f in [('SN s0', 'support-state/H_base_T08_s0.s0.jsonl'), ('SN s1', 'support-state/H_base_T08_s1.s0.jsonl'),
               ('S s0', 'state-readouts/H_S_T08_s0.s0.jsonl'), ('S s1', 'state-readouts/H_S_T08_s1.s0.jsonl'),
               ('SH s0', 'state-readouts/H_SH_T08_s0.s0.jsonl'), ('SH s1', 'state-readouts/H_SH_T08_s1.s0.jsonl')]:
    fh = {}; nrows = collections.Counter()
    for l in open(R + f):
        r = json.loads(l); nrows[r['name']] += 1
        if r['name'] in surv and r.get('first_hit') is not None: fh[r['name']] = min(fh.get(r['name'], 1e18), r['first_hit'])
    multi = sum(v > 1 for v in nrows.values())
    print(lab, 'reached <=10k:', sum(v <= 10000 for v in fh.values()), ' <=40k:', sum(v <= 40000 for v in fh.values()), ' rows>1 per thm (resumed; first_hit then per-row):', multi)
