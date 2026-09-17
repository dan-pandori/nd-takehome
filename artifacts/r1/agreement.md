# run1-lean step 1 — nd_verify vs Lean 4 agreement (generated 2026-09-17T23:29:44Z; nd2lean.py at 43442ed)

## Verifier-accepted proofs (all pools): nd_verify accepts ⇒ Lean accepts

| file | n | nd ok | lean ok | both ok | nd ok, lean no | nd no, lean ok | untranslatable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `artifacts/r1/agree_train.jsonl` | 154990 | 154990 | 154990 | 154990 | 0 | 0 | 0 |
| `artifacts/r1/agree_heldout.jsonl` | 5000 | 5000 | 5000 | 5000 | 0 | 0 | 0 |
| `artifacts/r1/agree_val36.jsonl` | 36 | 36 | 36 | 36 | 0 | 0 | 0 |
| `artifacts/r1/agree_transfer_gen.jsonl` | 1638 | 1638 | 1638 | 1638 | 0 | 0 | 0 |
| `artifacts/r1/agree_rl_targets_gen.jsonl` | 3000 | 3000 | 3000 | 3000 | 0 | 0 | 0 |
| `artifacts/r1/agree_minlen_transfer.jsonl` | 1573 | 1573 | 1573 | 1573 | 0 | 0 | 0 |
| `artifacts/r1/agree_minlen_val36.jsonl` | 20 | 20 | 20 | 20 | 0 | 0 | 0 |
| `artifacts/r1/agree_novelty_phase1.jsonl` | 12761 | 12761 | 12761 | 12761 | 0 | 0 | 0 |
| `artifacts/r1/agree_depth3_f0_a1_s0.jsonl` | 1147 | 1147 | 1147 | 1147 | 0 | 0 | 0 |
| `artifacts/r1/agree_depth3_f0_a1_s1.jsonl` | 1208 | 1208 | 1208 | 1208 | 0 | 0 | 0 |
| `artifacts/r1/agree_reductio_f0_s0_t2.jsonl` | 91 | 91 | 91 | 91 | 0 | 0 | 0 |

## Single-edit mutations (one citation / rule name / formula token / depth bar / ref swap per proof): nd_verify rejects ⇒ Lean rejects

Final translator (box-cite end checked; NEGI ascribed ¬A):

| file | n | nd ok | lean ok | both ok | nd ok, lean no | nd no, lean ok | untranslatable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `artifacts/r1/agree_mut_heldout_v2.jsonl` | 2000 | 1 | 1 | 1 | 0 | 0 | 1008 |
| `artifacts/r1/agree_mut_rl_targets_v2.jsonl` | 2000 | 6 | 6 | 6 | 0 | 0 | 1115 |

First translator (before 23:07; kept for the record — the 61 / 121 Lean-accepted rejects were 54 / 117 box cites with the wrong end line and 7 / 4 NEGI-for-IMPI):

| file | n | nd ok | lean ok | both ok | nd ok, lean no | nd no, lean ok | untranslatable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `artifacts/r1/agree_mut_heldout.jsonl` | 2000 | 1 | 62 | 1 | 0 | 61 | 788 |
| `artifacts/r1/agree_mut_rl_targets.jsonl` | 2000 | 6 | 127 | 6 | 0 | 121 | 693 |

'untranslatable' = the mutated proof has a structure Lean has no counterpart for (bad depth, wrong ref count, box cite not a closed box / wrong end, PR beyond premises); counted as rejected by both.

## Handcrafted divergences (artifacts/r1/agree_handcrafted.jsonl)

Lean unfolds `¬A` to `A → False` definitionally, so any rule that ND ties to the *name* of the connective is accepted by Lean when the two spellings are swapped; ND's premise-order / PR-placement / line-numbering rules have no Lean counterpart either.

| case | nd_verify | Lean |
|---|---|---|
| NEGE with (A > F) in place of (~A) | reject (rule check failed: NEGE (line 3)) | accept |
| IMPE with (~A) in place of (A > F) | reject (rule check failed: IMPE (line 3)) | accept |
| IMPI box ending in F used to derive (~A) | reject (rule check failed: IMPI (line 4)) | accept |
| NEGI box used to derive (A > F) | reject (rule check failed: NEGI (line 4)) | accept |
| DN on ( ~ ( P > F ) ) | reject (rule check failed: DN (line 2)) | accept |
| R across (~A) / (A > F) | reject (rule check failed: R (line 2)) | accept |
| PR lines in the wrong order | reject (premise block does not match declared premises) | reject |
| a PR line after a non-PR line | reject (PR misplaced at line 3) | accept |
| line indices not starting consecutively (N1, N3) | reject (line index mismatch at position 2) | accept |
| proof ends inside a box (control: both reject) | reject (proof ends inside a subproof) | reject |
