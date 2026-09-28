#!/usr/bin/env python3
"""support-followups: re-check every accepted LITERAL sampled text of this run in Lean, one proof per Lean process
(LEAN_GATE_CHUNK=1), and scan it for vacuity tokens.  support.py's judge checked nd2lean's rendering of the decoded
proof; this checks the text the model actually wrote.  Writes artifacts/sf/recheck.json.
  LEAN_GATE_CHUNK=1 python3 sf_recheck.py [glob ...]"""
import glob, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer
from lean_gate import lean_check

BAD = ('sorry', 'admit', 'simp', 'decide', 'exact?', 'native_decide', 'omega', 'tauto', 'aesop', 'axiom')
pats = sys.argv[1:] or ['artifacts/sf/a_*.s0.jsonl', 'artifacts/sf/b_*.s0.jsonl', 'artifacts/sf/c1_*.jsonl', 'artifacts/sf/c2_*.s0.jsonl']
tok = LeanTokenizer('lean_seq')
prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/sc/theorems.jsonl') if l.strip()}
items, meta = [], []
for pat in pats:
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            r = json.loads(l)
            for p in r['proofs']:
                items.append((tok.statement(prompts[r['name']]), p['lean_text']))
                meta.append((os.path.basename(f), r['name'], r['ckpt_md5'][:8]))
ok, wall, _ = lean_check(items)
bad = [m for (s, t), m in zip(items, meta) if any(b in t.split() for b in BAD)]
rej = [m for o, m in zip(ok, meta) if not o]
res = {'n': len(items), 'accepted': sum(ok), 'rejected': rej, 'vacuity_token_hits': bad, 'files': pats, 'wall_s': round(wall, 1)}
json.dump(res, open('artifacts/sf/recheck.json', 'w'), indent=1)
print(f"{res['n']} literal texts, Lean accepts {res['accepted']}, rejects {len(rej)}, vacuity tokens {len(bad)} ({wall:.0f} s)")
