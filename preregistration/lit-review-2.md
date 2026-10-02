# Pre-registration: lit-review-2 (executor, 2026-10-02)

Written before any new paper was fetched or screened. Only the earlier review (`lit-review`, 58 papers),
proposal 20 and the `trajectory` / `trajectory-cap6` / `rl-from-ckpt` summaries have been read.

## Question

The SPAR question: how far does RL against a verifier create new capability rather than elicit rare-but-known
behaviour, and what limits it. Three sub-questions from the run brief:
1. Create vs elicit, 2025–2026: current evidence and measurement standard; which designs separate the two
   convincingly; where `trajectory` and `rl-from-ckpt` fall short.
2. Exploration: which methods demonstrably produce behaviour outside the base model's support, and whether each
   needs a pretrained prior.
3. Model-organism domains with exact control of pretraining coverage and an RL phase.

## Design

- Extend `lit-review` (do not re-screen its 58 papers; papers it screened are cited from its notes).
- Screen 25–40 **new** papers, preferring 2025–2026; read 8–12 in depth (notes in TEMPLATE format).
- Every cited claim is fetched into `~/lr_sources/` (arXiv HTML, else PDF text) with `lit_review_2/fetch.py` and
  grepped; the review gives id + version + location. Unverified claims are marked.
- Screening is split across ≤ 3 sub-agents by question (each keeps ≤ 1 process at a time on the VPS; ≤ 4 in all),
  each returning a claim ledger; I re-check a sample of ≥ 25 claims myself with `lit_review_2/quote.py`.
- No pods. No Lean checks (nothing is counted on a model).

## Expected results (falsifiable)

1. **Q1.** No 2025–2026 study on a pretrained LLM shows RL solving problems its base fails at a base budget of
   k ≥ 1,024 *and* checks that the new solutions are not low-probability base samples (per-token or per-step
   likelihood under the base). Falsified by one such paper.
2. **Q1.** ProRL-type "beyond the base" results rest on tasks where the base is weak by format or instruction
   following (base pass@k ≈ 0 at moderate k), not on a likelihood test of the new solutions.
3. **Q1.** The designs that separate creation from elicitation best use controlled pretraining (synthetic data with
   known coverage); ≥ 2 such 2025–2026 papers exist beyond the two already screened (Interplay, Echo Chamber).
4. **Q2.** The only methods with direct out-of-support evidence are tabula-rasa self-play search (AlphaZero / MuZero
   family) and Go-Explore / count-based methods in environments without a pretrained prior; no LLM-RL exploration
   bonus paper measures support of its new solutions under the base at k ≥ 1,024.
5. **Q3.** ≤ 4 of the brief's model-organism families have published work with both exact pretraining coverage
   control and an RL phase; our ND setting is at least as controlled as the best of them.
6. ≥ 90 % of the claims I re-check verify verbatim at the stated location.
7. At least one claim in our own documents (brief, proposal 20, earlier review) is found mis-stated or needs a
   qualification.

## Budget and stop rule

- Pods: none ($0.50 / 1 h registered as a guard only).
- Claude time heavy, as authorised. Stop when the deliverables are written and the re-check is done, or at 40 new
  papers screened, whichever comes first.
