#!/usr/bin/env python3
"""Reviewer: term size (my Lean elaboration, recheck.json) and ND lines / env actions, by group, eventual vs reference;
plus B6&A12 cap-6 vs cap-12 eventual proofs; compared with the executor's term_size field."""
import json, os, statistics as st, collections
R = os.path.expanduser('~/review/trajectory-cap6'); rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
rc = {k.split('|', 1)[1]: v for k, v in json.load(open(f'{R}/rv6/recheck.json'))['target_size'].items()};  # keyed by proof text (recheck dedups on (prompt, proof))
G = json.load(open(f'{R}/rv6/recount.json'))['groups']
sets = json.load(open(f'{R}/rv6/analysis.json'))['sets']
pool = lambda n: 'tb72' if n.startswith('textbook_') else 'h250'
mism = 0; nn = 0
for s in (0, 1, 2):
    meta = {r['tid']: r for r in rd(f'{R}/artifacts/tj6/score/s{s}/targets.jsonl')}
    rows = collections.defaultdict(list)
    for t in rd(f'{R}/artifacts/tj6/targets/targets_s{s}.jsonl'):
        sz = rc.get(t['proof']); m = meta[t['tid']]
        if m.get('term_size') is not None: nn += 1; mism += sz != m['term_size']
        g = G[str(s)][f'{pool(t["name"])}:{t["name"]}']
        rows[(t['kind'], g)].append((sz, t['proof'].count(' ; '), m['n_steps']))
    print(f's{s}: ' + '  '.join(f'{k}/{g} n{len(v)} size {st.median(x[0] for x in v)} lines {st.median(x[1] for x in v)} acts {st.median(x[2] for x in v)}' for (k, g), v in sorted(rows.items())))
print(f'my term size == executor term_size: {nn - mism}/{nn}')
cr = {r['tid']: r for r in rd(f'{R}/data/tj6/cross.jsonl')}
for lab in ('B6&A12', 'A6&A12'):
    a, b = lab.split('&'); keys = set(sets[a]) & set(sets[b])
    for kind in ('ev6', 'ev12'):
        v = [(rc[r['proof']], r['proof'].count(' ; ')) for t, r in cr.items() if t.startswith(kind) and f'{r["pool"]}:{r["name"]}' in keys]
        print(f'{lab} {kind}: n {len(v)} median term size {st.median(x[0] for x in v)} ND lines {st.median(x[1] for x in v)}')
