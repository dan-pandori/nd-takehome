# Review: lit-review (reviewer, agent:claude, 2026-09-29)

Run brief: nd-rl `docs/proposals/literature/BRIEF_lit-review.md`. Pre-registration: `preregistration/lit-review.md`.
Deliverable under review: `lit_review/REVIEW.md`, `lit_review/notes/` (23), `lit_review/to_add_to_zotero.md`.

The brief says the reviewer "does not recount; there are no counts". Phase 1 therefore re-checks the
four things the brief names (claims, novelty, feasibility, ranking inputs) plus the hard constraints,
with code written for this review. Phase 1 used the phase-1 copy `~/review/lit-review`. It did not read
`run_lit_review.md`, `log.md` or `STATUS.md` prose.

## Recount (phase 1, written before reading the executor's write-ups)

### Method

- **Independent sources.** The executor's text cache `~/lr_sources/` was not used. The reviewer
  re-fetched every source it checks, at the version `REVIEW.md` cites, with its own fetcher
  (`review_lit_fetch.py`: arXiv HTML, falling back to PDF via pypdf). AlphaProof came from the Nature
  HTML. The files are in `~/rv_lit/src/` (not committed; re-fetchable). Claims were checked with
  `review_lit_quote.sh <id> <regex>`, a regex grep with context.
- **Scale.** 29 source texts fetched: 27 arXiv papers at the cited version, 2506.02355v1 for the "either version" check, and AlphaProof. arXiv metadata came from the
  abs pages (the export API returned HTTP 429).

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72` equals `origin/main`'s. **Pass.** |
| `nd_verify` used as a judge | the run adds no checking code. `lit_review/fetch.py` and `quote.py` do not import it. **Pass.** |
| `artifacts/TEST_RUN_DONE` | absent at HEAD. It was already absent on `origin/dan`: repo-hygiene commit `e844a8ea` moved `artifacts/` to the bucket. It is still `1d5cf064` on `origin/main`. Not this run's change. **Pass.** |
| files touched | only `lit_review/`, `preregistration/lit-review.md`, `STATUS.md`, `log.md`, `run_lit_review.md`. No training or evaluation code changed. **Pass.** |
| `references.bib` untouched; `literature.py` not run | untouched in both repos. **Pass.** |
| pre-registration before screening | commit `dae83e61` at 03:22:31 UTC. The executor started at 03:20:04. The only paper text fetched before it was two fetch-helper smoke tests (2506.02355 and 1705.08439). The file's own "Written ≈ 03:35 UTC" is wrong: that is after the commit. **Pass**, with a cosmetic finding. |

No quarantine.

### Identifiers

- **All 55 arXiv ids in `REVIEW.md` and `to_add_to_zotero.md` resolve to the stated paper.** Title and first
  author match arXiv's abs-page metadata for each one.
- **Every cited version matches the latest arXiv version** (e.g. 2502.03438v3, 2506.02355v2, 2505.15201v5,
  2502.12272v6, 2409.15647v5).
- **Zotero list.** None of the 54 `arxiv:` lines in `to_add_to_zotero.md` is already in nd-rl's
  `references.bib`, matched by id or title. Minimo is the only screened paper already in the bib, and it is
  correctly excluded and cited by citekey.
- **Error in the brief, not in the run.** The brief says pass@k training, the entropy mechanism and Dr. GRPO
  are "in `references.bib`". They are not: the bib has only DAPO's verl recipe page (`tongDAPORecipe2025`).
  `to_add_to_zotero.md` lists all four papers. `REVIEW.md` names only the DAPO case.

### Claims behind the top five (all of them)

V = verified verbatim at the cited location in the reviewer's own fetch. V~ = verified as a paraphrase, or
verified with a nuance noted.

| # | claim | source, location | verdict |
|---|---|---|---|
| 1 | BFS score Σ log p / L^α, α ∈ [0,1] | 2502.03438v3 §2.2 Eq. (1) | V |
| 1 | 70.83 % ± 0.89 | 2502.03438v3 Table 1 | V |
| 1 | minimal proofs of all solved nodes 78.1 vs all proofs 40.6 (Equations) | 2205.11491v1 Table 4 | V |
| 1 | "Learning only from the minimal proofs always leads to improved performance" | 2205.11491v1 §7.2.1 | V |
| 1 | BF mean found length 1.66 vs critic-guided 4.44 | 2410.15700v2 §3.2 | V |
| 1 | ExIt's comparison is against REINFORCE (Hex) | 1705.08439v4 §6.1 heading | V |
| 1 | TS-LLM π_θ1 47.9 vs RFT-100 47.5 | 2309.17179v2 Table 4 | V (RFT-50 is 47.0) |
| 1 | truncate-and-resume | 2408.08152v1 §3.1 "Truncate… Resume…" | V |
| 2 | keep conjectures with P̂ ∈ (0, 1/4] | 2502.00212v4 §3.2 | V |
| 2 | 28.5 % vs "13.2 % achieved through expert iteration" | 2502.00212v4 abstract | V |
| 2 | "too difficult … is detrimental" | 2502.01612v2 §7.1 | V |
| 2 | `extract_goal` captures unsolved states | 2508.03613v1 §2.2 | V |
| 2 | Firoiu: fixed generator saturates | 2103.03798v2 §5: "close to 100 % on most synthetic domains, and so has little left to learn from the current Forward Proposer" | V~ (paraphrase is fair) |
| 3 | β_rank = 0.25; zero-advantage samples still skipped | 2506.02355v2 §4.1, Table 1 | V |
| 3 | 8,065 / 9,600 vs 7,860 (GRPO) vs 7,707 (static) | 2506.02355v2 Table 2 | V |
| 3 | "outperforms expert iteration" has no experiment behind it, in either version | 2506.02355 v1 and v2: the phrase is in the abstract and introduction only; no table or figure caption compares with EI | V (text-only check; figures not inspected) |
| 3 | rank bias | 2506.02355v2 Fig. 4 caption | V |
| 3 | Enigmata pass@1/pass@k 12.9/21.3 → 17.9/29.8 | 2508.10751v1 Table 1 (Qwen2.5-7B-Instruct) | V |
| 3 | Darling pass@128 +7.62 / 10.16 % | 2509.02534v1 §5 and Fig. 6 caption | V |
| 3 | no paper evaluates beyond k = 512 | largest pass@k in He 512, PKPO 16, Chen 8, Darling 128, NSR 256 | V (for the objective papers; Invisible Leash goes to 16,384, but it is a measurement paper) |
| 4 | Identities 91.3 % vs supervised "never exceeds 36 %" | 2205.11491v1 §7.1.3 | V |
| 4 | "programmatically created variants" | AlphaProof Methods (TTRL) | V |
| 4 | "More synthetic variants consistently improves the final prove rate" | AlphaProof ED Fig. 3b caption | V |
| 5 | reward −1 per tactic "to incentivize the discovery of the shortest proof"; value −T_steps | AlphaProof Methods | V~: T_steps is "the number of tactics in the longest branch of the proof required to resolve all subgoals", not total steps. A steps-to-go head for our AND-node-free linear proofs is the same thing; with `Or.elim` subgoals it is not. |
| 5 | proofsize buckets | 2202.01344v1 §4.3.2 | V |
| 5 | soft critic 78.1 / none 65.6 / hard 63.1 | 2205.11491v1 Table 5 | V |
| 5 | Minimo ≈ 8.45 M parameters | 2407.00695v2 App. A | V |

**Top-five claims: 27 checked, 27 verified (2 with a nuance). None misquoted, none not found.**

### Sample of other cited claims

The brief asks for ≥ 10. The reviewer checked 16.

| claim | source, location | verdict |
|---|---|---|
| RMaxTS 58.4 → 59.6 | 2408.08152v1 Table 3 (CoT, 4 × 6,400, RL column: single-pass 58.4, RMaxTS 59.6) | V |
| SFT 70.38 vs SFT + DPO 70.83 | 2502.03438v3 §3 | V |
| Goedel-V2: removing compiler feedback "significantly lowers performance" | 2508.03613v1 | V |
| SRR ≈ 0.93–0.99, NDR ≤ 0.04 | 2507.14843v4 §4.2 (overall figures; per-domain SRR goes down to 0.90) | V |
| (1 − p)^k ≤ ζ | 2507.14843v4 App. C | V |
| power sampling 8.84× tokens | 2510.14901v1 §5 | V |
| MATH500 0.748 (power) vs 0.785 (GRPO) | 2510.14901v1 Table 1 (Qwen2.5-Math-7B) | V |
| RL "amplifies a specific mode … while collapsing the others" | 2504.07912v2 conclusion | V |
| 0 % / 0.1 % exposure: no transfer; 1 % enhances it | 2512.07783v1 Observation 2 | V |
| variance across data orders at fixed initialisation | 2402.09371v1 §4.2 | V |
| outcome + tactic 59.2 vs outcome-only 57.9 (pass@64, ± 0.5, 7B) | 2606.20068v1: 59.2 is in the table; 57.9 follows from the text's "+2.5 vs +1.2 over baseline" | V. "2.6 σ" is 1.3 / 0.5; the σ of a difference is ≈ 0.7, so ≈ 1.8 σ. The conclusion is unaffected. |
| RFT on Level 3 "never surpasses 2.6 %" | 2509.25123v3 §4.2 | V |
| looping needs the step count in training | 2409.15647v5 §7: "requires the ground-truth number of steps in the training data" | V |
| pass@N gain requires lifting solutions with p₀ ≈ 1/N | 2506.02355v2 §3.4 | V~: this comes from a stylised calculation (Fig. 3 assumes a uniform (1 + ε) uplift), not a measurement. `REVIEW.md`'s "the pass@N gain comes from…" reads as empirical. |
| entropy law R = −a·e^H + b | 2505.22617v1 | V |
| Minimo propositional longest proofs 5 → 11 steps | 2407.00695v2 §5 | V |

**Other claims: 16 checked, 16 verified (2 with a nuance). Total 43 of 43, none misquoted, none not found.**

### Feasibility: code mappings on this branch (HEAD = `origin/dan` + the run's commits; no code changed)

| mapping in `REVIEW.md` | at that location | verdict |
|---|---|---|
| `ladder_ei.allocate`, `ladder_ei.py:60` | `def allocate(mode, …)` | real |
| `state_sample.env_generate`, `state_sample.py:34` | `def env_generate(…)` | real |
| `Env`, `state_env.py:172`; `decompose`, :512 | `class Env:`; `def decompose(prompt, nd_body, canon=False)` | real |
| `sample.generate_ids_fast`, `sample.py:131`, discards log-probs | returns `out.tolist()` (token ids only) | real, and the claim is true |
| `state_ladder_ei.generate`, :51 | a wrapper that calls `env_generate` | real |
| `gen.Gen`, `gen.py:66` | `class Gen:` | real |
| open goals at failure, `state_sample.py:73–79` | the per-wave failure branches (truncated, syntax, done, step cap) | real |
| `grpo.py:117`, `adv = R - R.mean(1)` | `adv = (R - R.mean(1, keepdim=True)).view(-1)` | real. `grpo.py` has no state-env path, so "whole-proof only" is true |
| `model.GPT.forward`, `model.py:103`; `load_ckpt`, :128, strict | `def forward(…)`; `load_state_dict(ck['state'])` (default strict=True) | real, and the claim is true |
| `fast_train.packed_logits`, `fast_train.py:225` | `def packed_logits(model, x, pos, bm)` | real |
| `--max_per_thm` in `ladder_ei.py` / `state_ladder_ei.py` | `ladder_ei.py:155` argument, :333 use; `state_ladder_ei.py` inherits it | real |
| NoPE "instead of RoPE" | `model.py:1` docstring and `rope_cache` | real |

**Every mapping names a real file, function and line.**

### Novelty (against the brief's "already does" list and nd-rl `experiment-summaries/` and proposals on `origin/dan`)

| # | shortlisted technique | done here? | already proposed? |
|---|---|---|---|
| 1 | search as the EI expert | No experiment summary runs search. | **Yes. nd-rl proposal 14 (`docs/proposals/2026-09-28-after-state-env.md`) item 1 already proposes it:** PUCT search with AND nodes plus a steps-to-go value head, against best-of-N at equal model calls, asking "does search move `L*` further than sampling". Proposal 13 (`state-conditioned-environment.md`) names it as the next step. `REVIEW.md` never cites proposal 14. Its added value is the design: best-first on log-prob first and value later, the apprentice evaluated *without* search (the ExIt question), minimal-proof training, and truncate-and-resume as a cheap baseline. |
| 2 | frontier target supply | Not done. Ladder-A **T5** injected 2,505 static cap-6 generator records at round 4: supply, but not frontier-conditioned. `REVIEW.md`'s "tried allocation but not supply" / "we have none" omits T5. The accurate claim is "no *model-conditioned* supply past `L*`". | No. |
| 3 | unlikeliness / pass@k / distinct-proof advantages | Not done. The word "unlikely" in two summaries is unrelated. | Not as a proposal found by the reviewer's grep. |
| 4 | transductive EI on textbook theorems plus variants | Not done. Textbook theorems are evaluation targets in `long-pool` and ladder-A, never EI targets. | No. |
| 5 | steps-to-go value token | Not done. | **Yes. Proposal 14 item 1 and proposal 13** both describe this value head, with AlphaProof's target. |
| 6 | least-likely proof selection | Not done. | Its comparator, the shortest-proof rule, is proposed in `2026-09-28-repo-and-method-improvements.md`, and `REVIEW.md` says so. |

No shortlisted technique is already *done*. Items 1 and 5 are already *proposed*, and `REVIEW.md` should
say so.

### Numbers the shortlist inherits (model labels)

| number | source | verdict |
|---|---|---|
| SN / S: 3,216,384 parameters | `state-env` summary | reproduces |
| C0: 3,214,336 parameters | `lean-format` summary | reproduces |
| frozen-ladder transfer `L*` sd 0.3536; MDD 2 at n = 2 | `NOISE_FLOOR.md` table row | reproduces |
| 1.794 × 0.354 = 0.63 at n = 6 | `NOISE_FLOOR.md` "At n = 6 per arm the constant falls to 1.794 · sd" | reproduces (arithmetic 0.635) |
| raw solve-count floors 167–257 % at n = 2 | `NOISE_FLOOR.md` (167, 235, 257 %) | reproduces |
| "the pairing removes the Stage-1 component, about 99 % of the variance" | `NOISE_FLOOR.md`: "≈ 99 % of the variance is the individual training run" | **Over-read.** The 99 % is run-to-run training variance. Two EI arms from one checkpoint are two further training runs, and their arm-level variance from a shared checkpoint is not measured anywhere. Pairing removes the Stage-1 draw, but not the component the floor calls dominant. |
| textbook solved 10 times in 73 × 14 reads; 282 textbook theorems in `transfer_long` | `long-pool` summary (Observations; pool table) | reproduces |
| ladder-A T2 / T4 did not move `L*` | ladder-A summary: every trained rung has transfer `L*` 10 on both seeds | reproduces. Model labelled correctly in `REVIEW.md` (token-format `stage1_abs.pt`, `nd_verify`-era) |

### Format and deliverable checks

- **Screened-paper table: 4 rows garbled.** 58 rows, as claimed. Rows 17 (LILO), 20 (SEC), 32 (Dr. GRPO) and
  37 (Cheng et al.) are broken by an unescaped `|` or a truncated cell. In each, the relevance, depth and
  claims-verified columns are shifted or missing (row 17's technique is cut off at "top-").
- **Word count.** `REVIEW.md` prose is 1,498 words, excluding tables and front matter; the limit is 1,500.
  Notes: 23, which is more than the brief's 8–12. All follow `TEMPLATE.md`'s headings. Citekeys are used
  only for bib papers (Minimo); the others give an arXiv URL and version.
- **Pre-registration timestamp.** The text says "≈ 03:35 UTC", the commit says 03:22. Cosmetic.

### Recount summary

- 43 of 43 checked claims verify against the reviewer's own fetch of the cited version: all 27 behind the
  top five, plus 16 others. Four carry a nuance: AlphaProof's T_steps is the longest branch; He et al.'s
  p₀ ≈ 1/N is analytic; Firoiu is a paraphrase; the Kim et al. σ arithmetic.
- 55 of 55 identifiers are correct. Every code mapping is real.
- Findings to carry into phase 2:
  - F1: #1 and #5 duplicate proposal 14 item 1 without citing it.
  - F2: "no supply" omits ladder-A T5.
  - F3: the "pairing removes ≈ 99 %" over-read.
  - F4: sign-count expectations. "≥ 5 of 6 pairs" has one-sided sign-test p = 7/64 ≈ 0.11, and only
    6 of 6 reaches p < 0.05. Policy asks for IQM with a stratified-bootstrap CI.
  - F5: the 4 garbled table rows.
  - F6: He §3.4 is worded as empirical.
  - F7: the pre-registration timestamp.
