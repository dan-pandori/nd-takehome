#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §6): the second implementer's 25 fixtures -- Lean (reviewer harness) and the reviewer's
classifier vs the fixtures' expected labels.  Fixture contents are never printed (3 are in textbook72 classes)."""
import json, sys
sys.path.insert(0, "/home/dan/review/proof-strategies/review_ps")
from nd import parse_prompt  # noqa: E402
from cls import classify  # noqa: E402
import lean  # noqa: E402
rows = [json.loads(l) for l in open("/home/dan/work/proof-strategies/artifacts/ps/validation/second_impl_fixtures_v1.2.jsonl")]
items, res = [], []
for n, r in enumerate(rows):
    proof = r['proof'].strip()
    if not proof.rstrip(' ;').endswith('QED'):
        proof = proof.rstrip(' ;') + ' ; QED'
    p, c = parse_prompt(r['prompt'])
    o = classify(p, c, proof)
    sub = {f"{s}.{t}" for (s, t) in o['sub']}
    norm = lambda x: x.replace('route_', '')  # noqa: E731
    pres_missing = [x for x in r['expect_sub_present'] if x not in sub and norm(x) not in sub]
    abs_present = [x for x in r['expect_sub_absent'] if x in sub or norm(x) in sub]
    ok = (set(o['uses']) == set(r['expect_u']) and not pres_missing and not abs_present and o['primary'] == r['expect_pri'])
    res.append({'n': n, 'labels_ok': ok, 'uses_eq': set(o['uses']) == set(r['expect_u']), 'pres_missing': pres_missing,
                'abs_present': abs_present, 'pri': (o['primary'], r['expect_pri'])})
    items.append((p, c, lean.render(p, c, proof)))
lk = lean.check(items)
for r, (ok, why) in zip(res, lk):
    r['lean_ok'] = ok
    r['lean_why'] = why
    print(json.dumps(r))
print('fixtures:', len(rows), '| Lean accepted:', sum(r['lean_ok'] for r in res), '| reviewer labels = expected:',
      sum(r['labels_ok'] for r in res))
