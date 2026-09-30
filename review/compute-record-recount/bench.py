"""Reviewer (compute-record): cost of train.py's per-step counter line at bs 500 on data/lj/train_retain (VPS CPU, no torch),
and the legacy A/B walls from the pod (same host, alternated)."""
import json, os, random, sys, time
sys.path.insert(0, os.getcwd())
os.environ.update(ND_OFFLINE='1', ND_REGISTRY_SYNC='0', ND_REGISTRY_DIR='/tmp/rvcr/reg')
import record
from tokenizer import make_tokenizer
tok = make_tokenizer('lean_seq')
data = [(tok.encode_prompt(r['prompt']), tok.encode_proof(r['proof'])) for r in map(json.loads, open('data/lj/train_retain.jsonl'))]
rng = random.Random(5); idx = [[rng.randrange(len(data)) for _ in range(500)] for _ in range(2000)]
c = record.compute(phase='bench').start()
t0 = time.perf_counter()
for idxs in idx:
    record.count(train_steps=1, train_tokens=sum(len(data[i][0]) + len(data[i][1]) for i in idxs))
us = (time.perf_counter() - t0) / len(idx) * 1e6
t0 = time.perf_counter()
for idxs in idx:
    [data[i] for i in idxs]
base = (time.perf_counter() - t0) / len(idx) * 1e6
c.n = dict.fromkeys(c.n, 0); record._blocks.remove(c)
print(f'counter line: {us:.1f} us/step (list-comprehension baseline {base:.1f} us)')
W = {json.loads(l)['job']: json.loads(l) for l in open(os.path.expanduser('~/review/compute-record/artifacts/compute-record/gpu/walls.jsonl'))}
w = {k: W[k]['t1'] - W[k]['t0'] for k in W if k.startswith('legacy')}
print({k: round(v, 2) for k, v in w.items()})
on = (w['legacy_on_1'] + w['legacy_on_2']) / 2; off = (w['legacy_off_1'] + w['legacy_off_2']) / 2
print(f'on - off = {on - off:.2f} s ({(on - off) / off * 100:.2f} % of wall); 600 steps x counter = {600 * us / 1e6:.3f} s')
