"""Reviewer (compute-record): replay train.py's batch draw (random.Random(seed), refill when fewer than bs remain, the
name-shift draw per record) without torch, and sum the tokens of the records actually drawn."""
import json, random, sys, os
sys.path.insert(0, os.getcwd())
from tokenizer import make_tokenizer
def replay(fn, bs, steps, seed, mode='lean_seq', shift=True):
    tok = make_tokenizer(mode); tok.shift = shift
    data = [(tok.encode_prompt(r['prompt']), tok.encode_proof(r['proof'])) for r in map(json.loads, open(fn)) if r]
    rng = random.Random(seed); perm = []; tot = 0
    for step in range(steps):
        if len(perm) < bs:
            perm = list(range(len(data))); rng.shuffle(perm)
        idxs = [perm.pop() for _ in range(bs)]
        for i in idxs:
            p, q = data[i]; q2 = tok.shift_abs(q, rng); assert len(q2) == len(q); tot += len(p) + len(q2)
    return tot
print('CI train (fixture, bs 100, 3 steps, seed 0):', replay('tests/fixtures/proofs150.jsonl', 100, 3, 0), '(counter 39441)')
for seed in (0, 1, 2):
    print(f'pod legacy/fast-short 600 steps bs 500 seed {seed}:', replay('data/lj/train_retain.jsonl', 500, 600, seed), '(counter 37560900)')
