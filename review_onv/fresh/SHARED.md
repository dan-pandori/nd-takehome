# Reviewer fresh-search agents (run olmo-novelty, role reviewer) — shared instructions

You are a search agent working for the REVIEWER of run `olmo-novelty`. That run positioned a set of our experimental
findings (C1–C8 below) against the literature and labelled each as novel / extends / replicates / contradicted. Your
job is an INDEPENDENT, FRESH literature search for the closest prior work to the claims assigned to you, so the
reviewer can later test the run's novelty labels. Stay blind to the run's own write-up.

## Independence rules (important)

- Do NOT open, list or grep: `/home/dan/work/olmo-novelty/olmo_novelty/` or `/home/dan/review/olmo-novelty/olmo_novelty/`
  (the run's REVIEW, notes, ledgers, screened table), `~/onv_sources/`, `~/onv_work/`, any `log.md`, `numbers.md`,
  `run_olmo_novelty.md`, `STATUS.md`, or any file under `~/runs/`. Do not read other agents' files in
  `/home/dan/review/olmo-novelty/scratch_onv/fresh/` except this SHARED.md.
- You MAY read the project's earlier literature reviews for orientation (they predate the run):
  `/home/dan/nd-rl/docs/literature/*/REVIEW.md` (grep, do not read whole), and `/home/dan/nd-rl/references.bib`
  (read-only). Never edit anything in `/home/dan/nd-rl/`.
- Do not contact anyone. No pods. Do not commit or push anything.

## Our claims (from the reviewed summaries of our Olmo runs)

Models: `dpo` = allenai/Olmo-3-32B-Think-DPO (32B; pretrained base → Think SFT → DPO; the RL start);
`s0100`/`s0750`/`s2300` = allenai/Olmo-3.1-32B-Think at RL steps 100/750/2,300 (Dolci-Think-RL: maths, code, IF,
chat; public intermediate RL checkpoints). C1 uses Olmo 3 7B base vs Olmo-3.1-7B-RL-Zero-Math (steps 500/2,800).

- C1 (7B RL-Zero-Math, AIME 2024–2026, 83 problems): RL ≈ 1.5–3.2e-3 of pretraining compute. Graded by RL's own
  checker. pass@1 0.09 → 0.42; under RL's verifier the base is credited on all 17 RL-only AIME solves within 383
  samples (typically ≈ 70); 10 of 17 base resolutions sound by hand, 6 right through a flawed step, 1 a guess. Nothing
  lost: reverse 0 at k ≤ 512 (contrasts with Yue et al.'s narrowing at large k).
- C2 (32B Think, AIME 2025–26, 59 problems): DPO start vs the RL run (≈ 3e-3 – 2e-2 of pretraining FLOPs). pass@1
  0.716 → 0.746, pass@8 ≈ 0.86 both; one inconclusive reach candidate; nothing lost. RL barely moves maths.
- C3 (same RL run, IFBench, 218 prompts after contamination exclusion): pass@1 0.290 → 0.683 (strict). 49 prompts
  (strict checker) and 42–43 (by blinded model readers) that the DPO start never solves in 256 samples while the RL
  checkpoint is confirmed on fresh draws: an RL-only share ≈ 20 % of prompts, against Yue et al.'s ≤ 1 % on maths;
  many binding constraint types absent from RL's IF training data; almost no narrowing (2 reverse prompts). Under the
  format-tolerant `loose` grade, reach is 24 prompts.
- C4 (gaming): about a third (36 %) of the RL model's first-checked strict successes on IFBench are gamed (letter of
  the instruction kept, substance dropped: vacuous passes, keyword stuffing); on ~11 prompts RL's apparent advantage
  is entirely gaming; so checker-only pass@k overstates reach.
- C5: IFEval reach (6 of 150 prompts) may be brevity (RL passes with 5–15× shorter answers); OMEGA maths reach
  appears only at RL's 32,768-token cap (the DPO start is cut off on 255 of 256 tries).
- C6 (failure modes): the DPO model's failures on the 49 IFBench reach prompts are "substantive" in 93 % of a blind
  reading (70 % attempted but far off).
- C7 (methods): symmetric confirmation (same rule for reach and reverse candidates; fresh draws confirm the RL side);
  a blinded hand/model-reader gate; a final-answer-only grade beside the RL grader; guessing at large k on integer
  answers (AIME 0–999); a compute axis along a lab's PUBLIC intermediate RL checkpoint trajectory (Olmo 3.1 Think 32B
  publishes ~46 intermediate RL checkpoints); the standard "not reached at K", not "created".
- C8 (follow-up tests): with the full ≈ 65k context the DPO start finishes the long geometry samples and solves one of
  the 3 OMEGA reach prompts (token budget explains 1 of 3); the hint "Answer in at most 60 words." makes the DPO start
  succeed on 4 of 6 IFEval and 12 of 42 IFBench reach prompts (prompt-elicitable); 0 genuine successes in 1,024 DPO
  draws on 10 IFBench reach prompts (per-draw rate ≤ 2.9e-3), but 4 of those 10 are prompt-elicitable; the step-750
  checkpoint already solves 26 of 43 reach prompts.

## How to search

- Load the web tools first: call ToolSearch with query "select:WebSearch,WebFetch". Use WebSearch (mode "standard";
  "extended" for niche/recent/hard-to-find items). Search through November 2026 (today is 2026-11-07). Use arXiv
  listing/abs pages, Semantic Scholar (`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations?fields=title,externalIds,publicationDate&limit=500"`,
  HTTP 429 → wait 30–60 s, retry ≤ 3 times, then fall back to web search), Google Scholar-style queries, OpenReview,
  GitHub READMEs, lab blogs. Forward citations of Yue et al. (arXiv 2504.13837) and ProRL (2505.24864) are a good seed.
- WebFetch output is a model's summary — use it for discovery only, never as a quotable source.
- To quote a paper, fetch its text: `curl -sL -m 120 https://arxiv.org/pdf/<id> -o /tmp/<PREFIX>_<id>.pdf &&
  pdftotext /tmp/<PREFIX>_<id>.pdf /home/dan/onv_rev_sources/<PREFIX>_<id>.txt && rm /tmp/<PREFIX>_<id>.pdf`
  (HTML pages: curl + strip tags with python, or `https://r.jina.ai/<url>`). Before EACH download run
  `pgrep -c -f 'curl|pdftotext|wget'`; if the count is ≥ 3, wait (`python3 -c "import time; time.sleep(20)"`) and
  retry. One download at a time; never run processes in parallel (the machine has 2 CPUs / 4 GB and is shared; at most
  4 processes machine-wide). Never use a bare `sleep N` command (it is blocked); use the python sleep above. End every
  shell command so it exits 0 (append `; true`).
- Source texts are copyrighted: keep them only in `/home/dan/onv_rev_sources/` (never in a repository).
- Verify each quote you record with: `python3 - <<'EOF'` … a check that the whitespace-normalised quote occurs in the
  whitespace-normalised source text (lowercase, collapse runs of whitespace, join "-\n" hyphenation). Drop or fix a
  quote that is not found. Quotes ≤ 25 words, no tabs/newlines.

## Output

1. A TSV at `/home/dan/review/olmo-novelty/scratch_onv/fresh/<PREFIX>.tsv` with header exactly
   `claim	arxiv_id	title	first_author	date	source_file	location	quote	measures	relation	threat	reason`
   - one row per (our claim, paper) pair that matters; `date` = first arXiv version date (YYYY-MM-DD);
   - `measures` = one sentence: what the paper measured (model, start point, task, largest k, grading);
   - `relation` = replicates / extends / contradicts / unrelated (relative to OUR claim: replicates = same direction,
     comparable measurement; extends = same direction but different setting/axis/control; contradicts = opposite
     finding under a comparable measurement);
   - `threat` = 0–3: how much the paper undermines calling our claim "novel" (3 = it already reports the same
     measurement on the same kind of task and start model);
   - `quote` verbatim ≤ 25 words from `source_file` (found by your check), `location` = section/page/table.
2. Your FINAL REPLY (≤ 500 words, returned as text — the file write may be blocked, so put the essential rows in the
   reply too): for each assigned claim, the closest 1–4 prior works (arXiv id, title, date, what they measured, the
   relation, the threat score) and your one-line verdict on whether the claim is novel / extends / replicates; then
   the searches you ran (queries, roughly) and anything you could not verify.

Time budget: about 45 minutes of work. Prefer depth on the closest 3–6 papers over a long list.
