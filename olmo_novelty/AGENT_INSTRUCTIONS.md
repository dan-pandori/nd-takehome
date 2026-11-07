# Instructions shared by every olmo-novelty research agent

You are one of five research agents for run `olmo-novelty` (executor: agent:claude). The project (SPAR) asks to what
extent RL against a verifier produces genuinely new capability rather than eliciting rare-but-known behaviour. Your
job: position our Olmo results against the literature for one topic, with every cited claim verified in the source
text.

## Read first (briefly; extend, don't redo)

- Our claims: `/home/dan/work/olmo-novelty/olmo_novelty/claims_C1-C8.md` (read it in full).
- Earlier reviews (nd-rl): `/home/dan/nd-rl/docs/literature/2026-09-29-lit-review/REVIEW.md`,
  `.../2026-10-02-lit-review-2/REVIEW.md` (+ `notes/`), `.../2026-10-04-capabilities/REVIEW.md`,
  `.../2026-10-19-rl-compute-share/REVIEW.md` and its `compute_table.csv` (RL / pretraining compute per paper: columns
  `ratio_low`, `ratio_high`, `gpu_hour_ratio`, `verdict`). Use `grep` for what concerns your topic; do not read them
  whole. arXiv ids already screened there are in `~/onv_work/prior_ids.txt` ("prior").

## Sources

- Fetch each source's text into `~/onv_sources/<PREFIX>_<arxivid>v<N>.txt` (record the version), e.g.
  `curl -sL -m 120 https://arxiv.org/pdf/<id>v<N> -o /tmp/<PREFIX>_<id>.pdf && pdftotext /tmp/<PREFIX>_<id>.pdf
  ~/onv_sources/<PREFIX>_<id>v<N>.txt && rm /tmp/<PREFIX>_<id>.pdf`. Blogs/READMEs: `curl` the page and strip tags
  with a short python script, or use `https://r.jina.ai/<url>` for a text rendering. Files already in `~/onv_sources/`
  without a prefix are shared, read-only copies: use them, never overwrite or edit any source file.
- The VPS has 2 CPUs and 4 GB and is shared: **one download at a time**, and before each download check
  `pgrep -c -f 'curl|pdftotext|wget'`; if it is ≥ 3, wait (`python3 -c "import time; time.sleep(20)"`) and retry.
  Never run more than one process in parallel yourself.
- Discovery: `WebSearch` (mode "standard"; "extended" for hard, recent or niche searches), arXiv listings, and the
  Semantic Scholar API (`curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations?fields=title,externalIds,publicationDate&limit=500"`;
  it rate-limits with HTTP 429: wait 30–60 s and retry a few times, then fall back to web search). `WebFetch` is for
  discovery only: its output is a model's summary, never a quotable source.
- The source texts are copyrighted: they stay in `~/onv_sources/`, never in the repository or the public bucket.

## Outputs (write only these files; PREFIX is given in your task)

1. **Ledger** `/home/dan/work/olmo-novelty/olmo_novelty/ledger/<PREFIX>.tsv`, tab-separated, header exactly
   `claim_id	source_id	source_file	location	quote	supports	used_for`. `claim_id` = `<PREFIX>-<n>`;
   `source_file` = the file name inside `~/onv_sources/`; `location` = section / figure / table / page; `quote` =
   verbatim from the text file, ≤ 25 words, no tabs or newlines; `supports` = one sentence stating what the paper
   says (its claim, not our interpretation); `used_for` = tags such as `C3;Q2`. Then run
   `python3 /home/dan/work/olmo-novelty/olmo_novelty/verify_ledger.py --neg <your ledger>` and fix or drop rows until
   every quote is found and the negative controls report 0. Never edit a source file to make a quote match.
2. **Notes**, one per paper read in depth, `/home/dan/work/olmo-novelty/olmo_novelty/notes/<firstauthor><year>-<short>.md`,
   in the format of `/home/dan/nd-rl/docs/literature/TEMPLATE.md` (front matter `written_on: 2026-11-07`,
   `written_by: "agent:claude"`, `papers:` citekeys; sections Learnings / Evidence and limitations / Connections and
   questions). Add a **Setup card** table: model size and start (pretrained base, distilled, SFT + DPO, instruct);
   RL share of pretraining (rl-compute-share's numbers if its table has the paper, say so; otherwise "not computed");
   RL steps; domain(s); the largest k; grading (answer match, checker, LLM judge, hand); controls (symmetric budgets,
   format tolerance, guessing, contamination: yes / no / partly, each with a ledger id). In Learnings, keep three
   things apart and label them: what the paper **observed**, how the **paper interprets** it, and **our
   interpretation**. Every factual statement about a paper cites a ledger id in brackets, e.g. `[PR-3]`; anything not
   verified is marked UNVERIFIED. ≤ 700 words per note. In Connections, give a relation label for each of our claims
   it bears on: replicates / extends / contradicts / unrelated, with the reason.
3. **Screened rows** `/home/dan/work/olmo-novelty/olmo_novelty/screen/<PREFIX>.tsv`, header exactly
   `id	version	title	first_author	date	prior	depth	topic	bears_on	relevance	one_line`; `prior` = yes if the
   arXiv id is in `~/onv_work/prior_ids.txt`; `depth` = title / abstract / skim / in-depth / full; `topic` = Q1–Q6;
   `bears_on` = C1–C8; `relevance` 0–3; `one_line` ≤ 30 words: what it measures and why it matters (or not).
4. **Relations** `/home/dan/work/olmo-novelty/olmo_novelty/screen/<PREFIX>_relations.tsv`, header exactly
   `claim	source_id	relation	reason	ledger_ids`, one row per (our claim, paper) pair that matters.

Citekeys: reuse keys from `/home/dan/nd-rl/references.bib` where the paper is there (`yueDoesReinforcementLearning2025`,
`liuProRLProlongedReinforcement2025`, `guoDeepSeekR1IncentivizesReasoning2025`, `allenaiOLMo3RLZero2025`, …);
otherwise propose one in the same style (`firstauthorTitleWordsYear`).

## Rules

- Do not contact anyone. Do not edit `references.bib` or run `code/tools/literature.py`. Do not commit or push (the
  executor does). No pods.
- Quotes ≤ 25 words. A number you report from a figure you cannot read in the text is UNVERIFIED (say "figure only").
- If two papers disagree, record both; do not adjudicate beyond what the texts support.
- **Final reply** to the executor (≤ 350 words): the headline findings with ledger ids; counts (screened, in depth,
  ledger rows verified, negative controls); what you could not verify; and the single most important point for
  our novelty labels.
