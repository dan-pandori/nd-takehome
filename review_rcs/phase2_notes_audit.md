# Phase 2 sub-audit: the 11 other notes, screened.md, to_add_to_zotero.md

**Scope.** Notes zeng, yu, guo, liu, hu, khatri, matsutani, wu, minimax, rastogi and teamolmo. They were written 17:57–18:08, before both claim checks and before the final table (19:55). The audit was read-only.

**Method.**
- **(c) Quotations.** Every double-quoted string was checked: 118 in all, including the short ones `check_quotes.py` skips ("2.8M", "~40T", "2500 steps", …). Matching used the verifier's normalisation without its space-stripped fallback.
- **(a) Numbers.** Every step count, batch, group, length, GPU-hour figure, token total and verdict label was compared with table lines 2–5, 7, 17–21, 25–29 and 42.
- **(b) Sources.** Claims were checked against the ledger quote, and against the source text wherever the wording goes beyond it.

## Non-OK rows

| # | note | claim (short) | note's value | final table / source value | verdict | evidence |
|---|---|---|---|---|---|---|
| 1 | liu L43 | ProRL is "the largest open run in this set with a large-k test" | v1, ≈ 16k H100-h | Ring-Zero is in the set (1T MoE, 63B active, 320 H200, 3,600 steps; pass@1024 to step 2,000). ProRL v2 (≤ 2.1 × 10⁻², 3,000 steps) is larger than v1 and was re-tested by Leash. REVIEW BL2 names v2 and AceReason-7B as the top tested runs | OVERCLAIM | C-RING-base, -hardware, -kmax; table L19, L40; REVIEW L41 |
| 2 | liu L43 | "Independent evaluation at k ≥ 4096 still finds net narrowing" | k ≥ 4,096 | Holds for maths only (k 4,096/8,192). The pooled 36/163 and 48/175 cited at L34 include non-maths tasks at k 1,024/2,048. REVIEW was fixed to "k 1,024–16,384" (L166; `_claimcheck.md` #23); table L18 `verdict_how` still says "4,096-16,384" | UNCLEAR | C-LEASH-kmax, -prorlv1_math |
| 3 | liu L36; matsutani L47 | RL Squeezes finds fewer *correct* trajectories after RL from SFT checkpoints (ProRL, AceReason) | fewer correct paths | Paper: RL cuts *incorrect* trajectories "whether starting from Base or SFT" (L79). For SFT+RL: "SFT expands correct trajectories while subsequent RL compresses incorrect trajectories" (L179). The correct-path sentence (L177) is generic. AceReason-14B shows "minimal changes in path count compared to the SFT model" (L1239) | UNSUPPORTED | 2509.21128v2.txt; C-RLSQ-verdict_both, -ace14b_caveat |
| 4 | matsutani L48 | "narrowing persists at the largest open RL scales tested" | — | The squeeze is of incorrect paths. Llama-3.1-8B and AceReason-1.1-7B expand correct paths. Larger tested runs exist (row 1) | OVERCLAIM | C-RLSQ-llama_expands, -ace11_amc |
| 5 | liu L26 | On code and boxnet: "extended training sustains and amplifies performance gains consistently across all values of k" | all k, code + boxnet | The sentence is about boxnet only (L281–283). Code gets "continued improvements", with no k (L272). REVIEW fixed the same conflation (`_claimcheck.md` #46) | OVERCLAIM | C-PRORL-sustained, -boxnet |
| 6 | liu L22 | v2 ran "at 512 prompts per step per BroRL's baseline row" | 512 | BroRL's "Baseline 16 512 3000" row sits beside the N = 16 / 512 continuation rows. JustRL Table 4 (fetched) gives ProRL-V2 a batch of 256 and "+1,000" steps that "continue from ProRL-V1". Table L19's high bound (2.1 × 10⁻²) assumes 512 throughout and says continuation "is not stated in the fetched text" | UNCLEAR | C-BRORL-baseline_row; 2512.16649v1.txt L218–228 |
| 7 | matsutani L40 | "Cluster counts are threshold-dependent (App. C.5)" | dependent | App. C.5: BLEU and varied thresholds "yielded identical results" | OVERCLAIM (mis-cite) | 2509.21128v2.txt L1281 |
| 8 | minimax L39–40 | Text-01 phases "sum to 11.4T"; base ≈ 19.3T (own arithmetic) | 11.4T; 19.3T (= table D) | "the remaining 3.2T tokens" can also mean the last 3.2T of the 7.2T. That gives 8.2T, D ≈ 16.1T and the M1 ratio × 1.2 | UNCLEAR | 2501.08313v1.txt L606 |
| 9 | headers of liu, hu, matsutani, wu, khatri, minimax | "latest" / "only version" | — | No abs page saved, and the fetch URLs pin the version | UNCLEAR (minor) | `~/rcs_sources/*.abs.*` |

## OK rows per note

| zeng | yu | guo | liu | hu | khatri | matsutani | wu | minimax | rastogi | teamolmo |
|---|---|---|---|---|---|---|---|---|---|---|
| 22 | 21 | 22 | 18 | 20 | 24 | 18 | 19 | 17 | 18 | 21 |

That is 220 OK claims in total.
- **No stale numbers.** Every number a table row uses matches the final table, and every verdict label matches the row's `verdict`.
- **Quotations and ids.** All 118 quotations are verbatim, each substantive one in the source the note cites. All 56 cited ledger-id occurrences resolve.
- **Figure axes.** SimpleRL's Fig. 1 length-axis ranges match the ledger but cannot be assigned to panels unambiguously from the PDF text.

## The reviewer's two issues

1. **JustRL token budget.** No note covers JustRL. screened.md #36 gives steps, batch and length but no token figure, so the issue does not recur. JustRL's Table 4 is also the source behind row 6.
2. **The 11.8× create/elicit gap.** No note states or uses it.

## screened.md (recounted by script)

- 96 rows, numbered 1–96, 11 cells each.
- 52 rows carry a versioned arXiv id; 44 are web.
- First question: 15 Q1, 42 Q2, 34 Q3, 5 Q4, sorted in that order.
- In depth: 12 "full" rows + 12 "full*" rows (the frontier note) = 13 notes.
- The claims column sums to 1,016, against 1,206 ledger rows.

Every header count is correct.

## to_add_to_zotero.md

- **Count.** 47 arXiv ids + 43 URLs = 90 = 96 − 6 sources already in `~/nd-rl/references.bib`. All six excluded keys are present; none of the 47 ids is.
- **Match with screened.md.** The ids and their order are identical. Versions are dropped, as in earlier runs and `literature.py add arxiv:<id>`.
- **Markers and fields.** All 19 "(also listed by …)" markers were found in the named earlier list. Entries use the earlier runs' fields (id; or URL — title, author, proposed key).
- **Notes.** They follow TEMPLATE.md; their proposed keys are labelled and absent from the bib.
- **Minor.** Ord's essay is listed under the index URL `tobyord.com/writing`.
- **Caveat.** The local bib was last committed 2026-09-17; I did not check the remote.

## Summary
1. Quotations are 118/118 verbatim and every ledger id resolves. No note number is stale against the final table.
2. The ProRL note holds 5 of the 9 problems: a "largest run" claim contradicted by Ring-Zero and v2; a k range that holds only for maths; a boxnet quote extended to code; a misread RL Squeezes finding; and a disputed v2 batch that feeds table L19.
3. The RL Squeezes note says long RL loses *correct* trajectories and that narrowing persists at the largest scales. The text supports only the loss of incorrect trajectories.
4. Neither reviewer issue recurs in the notes. JustRL's Table 4 also undercuts table L19's ProRL v2 assumptions, and table L18 keeps the k range that REVIEW corrected.
5. screened.md and to_add_to_zotero.md check out; the only flaw is one weak Zotero URL (Ord).
