#!/usr/bin/env python3
"""Shared test protocol for run kalmar-complexity: sample K12 theorems and compute the reference outputs.

  from kalmar_complexity.common import sample_prompts, ref_sl, ref_pb, ref_tt, sl_steps

- `sample_prompts(n, seed)`: n distinct K12 prompts (`data/kh/train_k12.jsonl`, 155,000; md5 800b5486...), drawn with
  random.Random(seed).sample over record indices.  The run's test sample is seed 20261020; a reviewer uses any other.
- `ref_sl(prompt)` / `ref_pb(prompt)`: `kalmar.kalmar.build(prompt, 'sl' | 'pb')` -> dict (proof = ND body text, tags =
  step type per state-env action, ...).  This is kalmar-pretrain's builder, unmodified.
- `ref_tt(prompt)`: `tt_prover.solve(prompt)`, the Lean source text (nd-rl `dan:code/tools/tt_prover.py`, copied
  verbatim to `kalmar_complexity/ref/tt_prover.py`).
- `sl_steps(prompt)`: the (state tokens, action tokens, step tag, box depth) the algorithm visits in the state
  environment (`state_env.decompose`, canonical names, base 0) -- what kalmar-pretrain's models were trained on.
"""
import json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar'))
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity', 'ref'))
K12 = os.path.join(ROOT, 'data', 'kh', 'train_k12.jsonl')
TEST_SEED = 20261020


def k12_prompts():
    with open(K12) as fh:
        return [json.loads(l)['prompt'] for l in fh]


def sample_prompts(n=1000, seed=TEST_SEED):
    ps = k12_prompts()
    return [ps[i] for i in sorted(random.Random(seed).sample(range(len(ps)), n))]


def ref_sl(prompt):
    import kalmar
    return kalmar.build(prompt, 'sl')


def ref_pb(prompt):
    import kalmar
    return kalmar.build(prompt, 'pb')


def ref_tt(prompt):
    import tt_prover
    return tt_prover.solve(prompt)


def sl_steps(prompt):
    from state_env import decompose, split_actions, Env
    r = ref_sl(prompt)
    steps, toks, env = decompose(prompt, r['proof'], canon=True)
    e = Env(prompt, canon=True)
    out = []
    for (st, a, _h), tag in zip(steps, r['tags']):
        out.append((st, a, tag, len(e.frames) - 1))
        ok, why = e.apply(a)
        assert ok, why
    assert len(out) == len(r['tags'])
    return out


if __name__ == '__main__':
    ps = sample_prompts(3)
    for p in ps:
        print(p)
        st = sl_steps(p)
        print(len(st), 'states; first:')
        for s, a, t, d in st[:3]:
            print('  STATE', ' '.join(s))
            print('  ACTION', ' '.join(a), '|', t, d)
        print('  tt:', ref_tt(p)[:200])
