#!/usr/bin/env python3
"""Independent re-check of the EI proofs behind the falsifier survivors.

`lean` exits 0 on a file whose only problem is `sorry` or `exact?` (it reports them as warnings/info), and a
proof checked in a BATCH shares a file with others, so a mis-attributed error line could in principle pass one
through.  This re-checks every distinct accepted EI proof on the survivor theorems **one per Lean process**,
and scans the literal sampled text for tokens that would make the check vacuous.  Both must pass.

  python3 sc_recheck.py data/sc/falsifier_survivors.txt
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_gate import check_sources
from lean_tok import LeanTokenizer
import nd2lean

BAD = re.compile(r'\b(sorry|admit|exact\?|apply\?|decide|native_decide|simp|omega|aesop|tauto|trivial|norm_num)\b')

want = set(open(sys.argv[1]).read().split())
cells = json.load(open('artifacts/sc/summary.json'))
prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/sc/theorems.jsonl')}
tk = LeanTokenizer('lean_seq')

items = []
for c in cells:
    if c['model'] != 'ei' or c['name'] not in want:
        continue
    for p in c['proofs']:
        items.append((c['name'], c['temperature'], p['proof'], p['lean_text'], p['n_lines'], p['term_size']))
print(f'{len(items)} distinct accepted EI proofs over {len({i[0] for i in items})} survivor theorems')

flag = [i for i in items if BAD.search(i[3] or '')]
print(f'literal texts containing a vacuity token {BAD.pattern}: {len(flag)}')

# one Lean process per proof, on the LITERAL sampled text against the theorem's own statement
bad = []
for j, (name, T, nd, tx, nl, ts) in enumerate(items):
    ok, _, _ = check_sources([tk.statement(prompts[name]) + '\n' + tx] if False else
                             [nd2lean.translate(prompts[name], nd, require_all_pr=False)])
    if not ok[0]:
        bad.append((name, T, nd[:80]))
    if j % 50 == 0:
        print(f'  {j}/{len(items)} rechecked, {len(bad)} failures', flush=True)
print(f'RE-CHECK: {len(items) - len(bad)} / {len(items)} accepted one-proof-per-Lean-process; failures {len(bad)}')
for b in bad[:10]:
    print('  FAIL', b)
lens = sorted(i[4] for i in items); tss = sorted(i[5] for i in items)
print(f'proof length lines: min {lens[0]} median {lens[len(lens)//2]} max {lens[-1]}')
print(f'proof term size:    min {tss[0]} median {tss[len(tss)//2]} max {tss[-1]}')
