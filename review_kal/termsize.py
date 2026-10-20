#!/usr/bin/env python3
"""Term size (lean_check inference nodes, the project's definition) of a seeded sample of K12-Kalmár proofs and of the K12
proofs of the same theorems, measured by running the project's `lean_check.check` on canonical texts built here (header
from the prompt; body = the state env's canonical tokens with `.elim` / `.1` / `.2` re-joined), against the stored
`term_size` field (the executor's per-rule formula).  Also a length (lines, tokens) cross-check.

  python3 review_kal/termsize.py [--n 150] -> out/termsize.json
"""
import argparse, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
from state_env import decompose
import lean_check

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=150)
a = ap.parse_args()
SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}


def fm(s):
    return ' '.join(SYM.get(t, t) for t in s.split())


def source(prompt, proof):
    steps, toks, env = decompose(prompt, proof, canon=True)
    body = re.sub(r' \.(elim|1|2)\b', r'.\1', ' '.join(toks))
    p, g = kc.split_prompt(prompt)
    hs = ''.join(f' (h{i + 1} : {fm(x)})' for i, x in enumerate(p))
    return f'theorem t (P Q R S : Prop){hs} : {fm(g)} := by {body}', len(toks)


pick = set(random.Random(11).sample(range(155000), a.n))
recs = [json.loads(l) for i, l in enumerate(kc.opener(os.path.join(kc.ROOT, 'data', 'kalmar', 'train_kal_sl.jsonl.gz'))) if i in pick]
srcs, srck, lt = [], [], []
for r in recs:
    s, n = source(r['prompt'], r['proof']); srcs.append(s); lt.append((n, r['lean_tokens']))
    s2, n2 = source(r['prompt'], r['k12_proof']); srck.append(s2)
res_k, w1, c1 = lean_check.check(srcs, workers=1, chunk=50)
res_12, w2, c2 = lean_check.check(srck, workers=1, chunk=50)
ok = sum(x['ok'] for x in res_k)
match = sum(x['ok'] and x['size'] == r['term_size'] for x, r in zip(res_k, recs))
out = {'n': len(recs), 'kal_ok': ok, 'kal_size_equals_stored': match, 'kal_tokens_equal_stored': sum(n == m for n, m in lt),
       'kal_size_mean_lean_check': sum(x['size'] for x in res_k if x['ok']) / max(1, ok),
       'kal_size_mean_stored': sum(r['term_size'] for r in recs) / len(recs),
       'k12_ok': sum(x['ok'] for x in res_12), 'k12_size_mean_lean_check': sum(x['size'] for x in res_12 if x['ok']) / max(1, sum(x['ok'] for x in res_12)),
       'k12_size_max': max(x['size'] for x in res_12 if x['ok']), 'reasons_bad': [x['reason'] for x in res_k + res_12 if not x['ok']][:5],
       'mismatch_examples': [(x['size'], r['term_size']) for x, r in zip(res_k, recs) if x['ok'] and x['size'] != r['term_size']][:10],
       'lean_s': round(c1 + c2, 1)}
print(json.dumps(out))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'termsize.json'), 'w'), indent=1)
