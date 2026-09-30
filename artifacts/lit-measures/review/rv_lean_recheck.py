#!/usr/bin/env python3
"""Reviewer Lean recheck: ND proof -> nd2lean.translate(require_all_pr=False) -> lean_check.check (Lean 4 core,
allowlist + axioms, term size).  Or, with --texts, literal lean_text through lean_check's --texts path.
Negative controls: each input is also checked with one corrupted variant (last cited line swapped) that must fail."""
import sys, json, random, collections
sys.path.insert(0, '/home/dan/review/lit-measures')
import nd2lean, lean_check
inp, outp = sys.argv[1], sys.argv[2]
recs = [json.loads(l) for l in open(inp)]
srcs = []; kinds = []
rng = random.Random(0)
def corrupt(nd):
    # change the conclusion formula of the last line to a different atom: must be rejected
    lines = nd.split(' ; ')
    i = len(lines) - 2
    toks = lines[i].split(); j = toks.index(':')
    atom = 'Q' if 'P' in toks[1:j] else 'P'
    k = 1
    while toks[k] == '|': k += 1
    lines[i] = ' '.join(toks[:k] + [f'( {atom} & ( ~ {atom} ) )'] + toks[j:])
    return ' ; '.join(lines)
bad = []
for r in recs:
    try:
        srcs.append(nd2lean.translate(r['prompt'], r['proof'], require_all_pr=False)); kinds.append('orig')
    except Exception as e:
        srcs.append(None); kinds.append(f'untranslatable {e}')
ctl_idx = rng.sample(range(len(recs)), min(200, len(recs)))
ctl = []
for i in ctl_idx:
    try: ctl.append(nd2lean.translate(recs[i]['prompt'], corrupt(recs[i]['proof']), require_all_pr=False))
    except Exception: ctl.append(None)
todo = [s for s in srcs if s] + [s for s in ctl if s]
res, wall, cpu = lean_check.check(todo)
it = iter(res)
out = []
for r, s, k in zip(recs, srcs, kinds):
    v = next(it) if s else {'ok': False, 'size': None, 'reason': k}
    out.append(dict(r, lean_ok=v['ok'], term_size=v.get('size'), lean_reason=v.get('reason')))
ctl_res = [next(it) if s else {'ok': False, 'reason': 'untranslatable'} for s in ctl]
with open(outp, 'w') as f:
    for o in out: f.write(json.dumps(o) + '\n')
by = collections.defaultdict(collections.Counter)
key = 'cell' if 'cell' in recs[0] else 'set'
for o in out: by[o.get(key)][o['lean_ok']] += 1
rej = [o for o in out if not o['lean_ok']]
print(f'checked {len(out)}: accepted {sum(o["lean_ok"] for o in out)}, rejected {len(rej)}; wall {wall:.0f}s')
print('per group min accepted:', min(c[True] for c in by.values()), 'groups', len(by))
for o in rej[:10]: print('  REJ', o.get(key), o['name'], o['lean_reason'][:200] if o['lean_reason'] else '')
print(f'negative controls: {sum(not c["ok"] for c in ctl_res)}/{len(ctl_res)} corrupted proofs rejected')
