# STATUS

Updated: 2026-09-15 03:42 UTC

## Plan
1. 03:25–04:30  gen.py (forward random generator with lazy premises + goal completion for ORE branches, dependency pruning, verify every proof), tokenizer.py (two modes: `rel` relative refs, `abs` absolute refs with random start offset), model.py (4L d256 RoPE decoder), train.py, sample.py (batched KV-cache sampling), prove.py. Unit tests vs verifier.
2. 04:30–06:00  Stage 1 on pod: 100k+ cap-6 proofs, held-out split by renaming class, train both tokenizer modes, pick by held-out greedy AND by frozen-model pass@k on 7–9 line transfer theorems (the length-generalisation question is the point). Eval by length with Wilson CIs.
3. 06:00–09:30  Stage 2 expert iteration (k=32–64, T=0.8) with frozen control, per-round stats + plots.
4. 09:30–13:00  Stage 2b (second seed or relabelling arm), validation-36 analysis, figures.
5. 13:00–14:30  Test set once (create artifacts/TEST_RUN_DONE first), writeup.md, numbers.md, log.md, README reproduction section.
6. 15:00        Final pull, commit, push. DONE.

## Done
- Read README.md, spec.md, verifier, validation set, pod check (A40, torch 2.8+cu128).
- gen.py (0 verifier rejects), tokenizer.py (rel/abs, round-trip 0 mismatches), model.py (3,210,240 params), train.py, sample.py (KV cache), eval_set.py, prune.py, expert_iter.py, plots.py, prove.py.
- data/: train 154,990 (31k per length 2-6), heldout 5,000 (1k per length), rl_targets 3,000 (300 per length 7-16), transfer 1,600. Disjoint by atom-renaming class; validation-36 classes removed (10 hits in cap-6 raw, 5 in long raw). Committed + pushed (train.jsonl.gz).

## Running on pod
- train.py stage1 rel + abs (6000 steps, bs128); background waiters run stage1_eval.sh on each when saved.

## Next step
- compare rel vs abs on held-out greedy AND transfer pass@16; pick mode; launch expert_iter RL arm + frozen control concurrently.
