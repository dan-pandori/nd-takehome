# kalmar_complexity — how many bits is Kalmár's construction? (run `kalmar-complexity`, proposal 31)

Everything here is reproducible from the repository plus the two training sets (`data/kh/train_k12.jsonl` from
`hf://buckets/dan-pandori/nd-rl/cap-horizon/data/kh/train_k12.jsonl.gz`, md5 800b5486…; `data/kalmar/train_kal_sl.jsonl.gz`
from `…/kalmar-pretrain/data/kalmar/`, gz md5 c91dbc6f…) and kalmar-pretrain's checkpoints in its bucket.

## Test protocol (`common.py`)
`sample_prompts(n, seed)`: n K12 theorems by `random.Random(seed).sample` over record indices; the run's sample is
seed 20261020, n = 1,000. References: `kalmar.build(prompt, 'sl' | 'pb')` (kalmar-pretrain's builder, unmodified),
`ref/tt_prover.py` (nd-rl `dan:code/tools/tt_prover.py` @ bcad22ff, verbatim), and `sl_steps(prompt)` = the
(state, action) pairs the models were trained on (`state_env.decompose`, canonical names).

## Programs (`programs/`) — each with its checker and a test against the builder

| dir | what | test (any seed: `--seed S --n N`) |
|---|---|---|
| `policy/` | `policy.py`: the explicit per-step policy (state → action); frames from the gaps that pending `have`s leave in the canonical names | `test_policy.py`: every state of 1,000 theorems (109,072) and 5,000 fresh (546,991) exact |
| `python/` | hand-golfed Python: `ksl_alg.py` (K-sl algorithm), `ksl_nd.py` / `ksl_seq.py` (renderers: ND text, canonical `lean_seq`), `parse.py`, `ktt_alg.py` + `ktt_lean.py` (tt_prover's construction), `kpol.py` (golfed per-step policy), `calib/` (copy, reverse, parity, sort, addition, eval, taut); `measure.py` (sizes) | `test_python.py`, `test_kpol.py`, `test_calib.py` |
| `dtree/` | `features.py` (21 generic state features + template labels), `build_rows.py`, `fit_tree.py` (smallest exact tree found, beam search) | rows of 4,000 theorems fitted; fresh 2,000 (217,968 states) and all tf1200 states (137,984) exact |
| `blc/` | binary lambda calculus / binary combinatory logic programs, toolchain and evaluator (agent-written; see its README) | `test_blc.py` |
| `rasp/` | RASP-L interpreter, the per-step policy as a RASP-L program, calibration programs (agent-written; see its README) | `test_rasp.py` |

## Measures and analyses

| file | what |
|---|---|
| `measures.csv` | one row per algorithm × measure (units, language, method, source file); built by `build_measures.py` |
| `count_tokens.py` | exact loss-token counts of both training sets (B1's N) |
| `b1_preq.py` | B1: first-epoch prequential code and absorbed bits (EDL) from kalmar-pretrain's logged curves |
| `b1_snap.py`, `b1_snap_types.py` | B1-snap: per-step-type code of 24 kalmar-pretrain checkpoints on tf1200; per-type breakdown (approximation) |
| `b2_preq.py`, `b2_per_type.py` | B2: block-wise prequential code (S / M / L, Kalmár / K12 / eval) and its per-type breakdown |
| `q4_states.py`, `q4_join.py`, `q4_tree_paths.py`, `q4_analysis.py` | Q4: per-state demand measures on tf1200, joined with kalmar-pretrain's verdicts; Spearman across step types and state-level logistic regression |
| `literature.md`, `lit_notes/` | Q5: 25 sources, 8 read in depth (agent-written; claims marked UNVERIFIED where not checked) |

Outputs are in `artifacts/kc/` (pod logs in `artifacts/kc/logs/`); the write-up is `run_kalmar_complexity.md`,
`numbers.md` § kalmar-complexity and the plain summary `run_kalmar_complexity_plain.md`.
