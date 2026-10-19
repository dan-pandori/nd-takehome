# data/kalmar — K12-Kalmár and the read sets of run `kalmar-pretrain`

Bulk files (`*.jsonl`, `*.jsonl.gz`) are in `hf://buckets/dan-pandori/nd-rl/kalmar-pretrain/data/kalmar/`, not in git.
Every file below is rebuilt deterministically by the scripts named.

## K12-Kalmár (`train_kal_sl.jsonl`, 155,000 records)

- **What it is:** one Kalmár-construction proof per K12 record (`data/kh/train_k12.jsonl`, md5 800b5486…), same theorems,
  same order. The proofs are ND records in the project's format (spec.md), so `lean_tok` renders them as `lean_seq` and
  `state_env.decompose` cuts them into (state, action) pairs.
- **Builder:** `kalmar/kalmar.py` (`build(prompt, variant)`); dataset: `python3 kalmar/build.py --in
  data/kh/train_k12.jsonl --variant sl --out data/kalmar/train_kal_sl.jsonl --stats artifacts/kalmar/build_sl.json`
  (≈ 1,000 s on 2 cores). Tests: `python3 kalmar/test_kalmar.py` (needs Lean for parts 5–6).
- **md5:** jsonl 1e4cebf57c081cf89082f67dcef0a22b, gz c91dbc6fb2280372b2e9284d95aec7d5.
- **The construction** (nd-rl `dan:code/tools/tt_prover.py`):
  - Atoms are split in the order P, Q, R, S.
  - Variant **sl** (used): X ∨ ¬X is derived once per atom at the top level, 9 lines: a ¬I box giving
    ¬¬(X ∨ ¬X), then DN. The splits are nested ∨E on those lines.
  - In each branch, the first false premise closes the branch by ex falso. Otherwise the goal is proved by Kalmár's
    lemma: per connective and polarity, as the prover's `prove()`.
  - **Memo:** a formula already on a line in scope is cited, not re-derived.
  - Variant **pb** (the prover's layout: X ∨ ¬X re-derived in every branch) is built for statistics only.
- **Checks:**
  - Lean on the literal canonical `lean_seq` text: **155,000 / 155,000 accepted**, 0 structural failures, and every text
    parses back to exactly its record's ND proof (`kalmar/lean_check_kal.py` → `artifacts/kalmar/lean_check_train_sl.json`).
  - Every record decomposes and replays in the environment (0 failures).
  - The algorithm's action is a function of the visible state: 0 conflicts over 3.37 M states (every 5th record).
  - Builder tests: Lean 60 / 60, negative controls 60 / 60 rejected.

| per proof (155,000) | K12 (its own proofs) | K12-Kalmár sl | K12-Kalmár pb |
|---|---|---|---|
| ND lines, mean / p50 / p99 / max | 7.0 / 7 / 12 / 12 | 107.9 / 95 / 285 / 527 | 150.6 / 131 / 384 / 626 |
| state-env actions, mean / max | 8.0 / 13 | 108.9 / 528 | 151.6 / 627 |
| (state, action) pairs, total | 1,239,995 | 16,876,247 | 23,504,837 |
| pair tokens (Σ state + action + 1), mean / total | 775 / 120 M | 21,121 / 3.27 B | 28,334 / 4.39 B |
| ND box depth, mean / max | 1.1 / 2 | 4.2 / 6 | — |
| longest state per proof, mean / max (tokens) | 104.5 / 386 | 229.3 / 655 | — / 655 |
| longest action, max (tokens) | 219 | 219 | 219 |
| largest canonical name, mean / max | 5.8 / 12 | 18.8 / 31 | — / 31 |
| canonical `lean_seq` tokens, mean | 127 | 1,755 | 2,406 |
| term size (lean_check inference nodes), mean / max | 4.5 / 14 | 92.2 / 423 | 135.0 / 522 |

Longest (state, action) pair:
- K12: 367 + 25 tokens (record 124962).
- K12-Kalmár: 513 + 219 tokens, plus `<eos>` (record 93283).
- The trainer's padded length is 733.

Sources: `artifacts/kalmar/build_{sl,pb}.json`, `artifacts/kalmar/stats_k12_vs_kal.json`.

## Read sets (`kalmar/make_sets.py --out data/kalmar`, seed 0; report `sets_report.json`)

Each record carries the theorem's sl proof (`proof`, `kal_tags` = step type per action, `kal_actions`, `kal_max_state`,
`kal_max_name`).

| file | n | what | md5 |
|---|---|---|---|
| `tf1200_kal_sl.jsonl` | 1,200 | teacher-forced / free-generation set: `data/p2/heldout.jsonl`, 150 one-atom + 350 each 2 / 3 / 4 atoms, none in K12's premise-order-invariant classes (22 of p2/heldout are) | b99c3b8d… |
| `val300_kal_sl.jsonl` | 300 | its first 300 (training validation loss only) | 131888de… |
| `g1_premises.jsonl` | 200 | G1: p2/heldout theorems with 2–3 premises + random distractor premises over their atoms → 100 with 4, 100 with 5 premises | b6770721… |
| `g2_large.jsonl` | 240 | G2: generated valid sequents, total size (nodes, ¬ counted) 40–49 / 50–59 / 60–79, 80 each; ≤ 3 premises, ≤ 4 atoms; none in K12's classes | 273c80f8… |
| `g3_classical.jsonl` | 106 | G3: create-or-elicit's strict σ-covered held-out classical theorems (`data/coe/sigma_heldout_strict.txt`) | 95434a32… |
| `<set>_kal_sl.jsonl` | — | sl proofs of holdout250, rr600, ge17, long2 and Charles's release (textbook72: lengths only, no theorem) | — |
| `ei_targets1000.jsonl` / `ei_transfer200.jsonl` | 1,000 / 200 | the EI ladder's targets / transfer theorems (`rl_targets` seed 0, `transfer` seed 1) | 85f0936a… / e9910c29… |

Generated theorems were filtered so that:
- the algorithm's proof has ≤ 1,000 actions;
- the largest canonical name is ≤ n32 (the sampler's name base is ≤ 32, and `lean_seq` has 64 name tokens).

The algorithm's longest action is 305 tokens (G2) and ≤ 172 elsewhere. Its longest proof is 451 actions (G2), 425
(tf1200) and 420 (hand_proved_14).
