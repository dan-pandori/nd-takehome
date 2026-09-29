# Reviewer: Lean re-check of every counted proof the smoke run stored (ND rendering -> nd2lean.translate -> lean, own harness).
import json, sys, os, re, subprocess, tempfile, glob
sys.path.insert(0, os.path.expanduser('~/review/results-registry'))
from nd2lean import translate
LEAN = os.path.expanduser('~/.elan/bin/lean')
A = os.path.expanduser('~/review/results-registry/artifacts/rr/')
items = []
for l in open(A + 'heldout_greedy.jsonl'):
    d = json.loads(l)
    for p in d['proofs']: items.append(('smoke_s0 heldout', d['prompt'], p))
for fn in sorted(glob.glob(A + 'ei_*/found*.jsonl')):
    for l in open(fn):
        d = json.loads(l); items.append((fn.split('rr/')[1], d['prompt'], d['proof']))
def one(src, k):
    src = re.sub(r'theorem (\S+)', f'theorem t{k}', src, count=1)
    fn = tempfile.mktemp(suffix='.lean'); open(fn, 'w').write(src)
    p = subprocess.run([LEAN, fn], capture_output=True, text=True); os.remove(fn)
    return p.returncode == 0 and 'error' not in p.stdout + p.stderr and 'sorry' not in src
ok = 0; res = {}
for k, (tag, pr, pf) in enumerate(items):
    t = translate(pr, pf)
    src = t[0] if isinstance(t, tuple) else t
    good = bool(src) and one(src, k)
    res.setdefault(tag, [0, 0]); res[tag][0] += good; res[tag][1] += 1
    if k == 0: print(src)
print(res)
# negative control: corrupt a proof (swap conclusion formula) must be rejected
tag, pr, pf = items[0]
t = translate(pr, pf); src = t[0] if isinstance(t, tuple) else t
bad = src.replace('Or.inr', 'Or.inl', 1) if 'Or.inr' in src else src.replace('Or.inl', 'Or.inr', 1)
print('negative control accepted?', one(bad, 999), '(must be False)')
