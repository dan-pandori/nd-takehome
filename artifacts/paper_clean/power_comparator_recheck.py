#!/usr/bin/env python3
"""paper-clean item 12: offline Lean re-check of the power-sampling comparators' stored accepted proofs.

The plain comparator (coe/power_sample.py run_plain) counts an attempt iff lean_gate accepts it, and from 2026-10-12 it
stores the accepted ND proofs ('accepted', with multiplicity).  This re-checks every stored proof the way
coe/coe_recheck.py re-checked the experiment's stored proofs: nd2lean + Lean 4 core via lean_judge.judge_many, with a
goal-negated control (conclusion G -> ( ~ G )) that must reject every proof.  Lists which comparator files store no text.

  LEAN=~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean LEAN_GATE_WORKERS=2 \
    python3 artifacts/paper_clean/power_comparator_recheck.py > artifacts/paper_clean/power_comparator_recheck.json
"""
import ast, glob, json, os, sys
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'coe'))
import lean_judge
from coe_recheck import negate

out = {'files': {}, 'lean': os.environ.get('LEAN', '~/.elan/bin/lean (default)')}
pairs, tags = [], []
for f in sorted(glob.glob('artifacts/coe/power/p2*_plainT*.json')):
    if f.endswith('.args.json'):
        continue
    d = json.load(open(f))
    prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open(d['in'])}
    rows = d['rows'] if 'rows' in d else [r for k in d if isinstance(d[k], list) for r in d[k] if isinstance(r, dict)]
    solved = [r for r in rows if str(r.get('solved')) == 'True']
    stored = [r for r in solved if r.get('accepted') not in (None, '', '{}')]
    nproofs = 0
    for r in stored:
        acc = r['accepted'] if isinstance(r['accepted'], dict) else ast.literal_eval(r['accepted'])
        for nd in acc:
            pairs.append((prompts[r['name']], nd)); tags.append((os.path.basename(f), r['name'])); nproofs += 1
    out['files'][os.path.basename(f)] = {'ckpt': d.get('ckpt'), 'theorems': len(rows), 'solved': len(solved),
                                          'solved_with_stored_proofs': len(stored), 'distinct_stored_proofs': nproofs}
res = lean_judge.judge_many(pairs)
neg = lean_judge.judge_many([(negate(p), nd) for p, nd in pairs])
per = {}
for (f, name), r, n in zip(tags, res, neg):
    e = per.setdefault(f, {'proofs': 0, 'lean_accepted': 0, 'negated_rejected': 0, 'theorems_with_an_accepted_proof': set()})
    e['proofs'] += 1; e['lean_accepted'] += bool(r[0]); e['negated_rejected'] += (not n[0])
    if r[0]:
        e['theorems_with_an_accepted_proof'].add(name)
for f, e in per.items():
    e['theorems_with_an_accepted_proof'] = len(e['theorems_with_an_accepted_proof'])
    out['files'][f]['recheck'] = e
out['rejections'] = [(t, r[1][:200]) for t, r in zip(tags, res) if not r[0]]
print(json.dumps(out, indent=1))
