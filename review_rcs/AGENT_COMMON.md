# Instructions for reviewer extraction agents (review of run rl-compute-share, 2026-10-19)

You work for the **reviewer** of run `rl-compute-share`. The reviewer must stay independent of the executor, so:

**Never open, grep, list or read** any of these (they hold the executor's numbers and conclusions):
- anything under `/home/dan/work/rl-compute-share/rl_compute_share/` or `~/review/`
- `/home/dan/work/rl-compute-share/{log.md,numbers.md,STATUS.md,run_rl_compute_share.md}`
- `~/runs/`, `~/rcs_work/`, `~/nd-rl/docs/literature/2026-10-19*` (and any file whose name contains `rl-compute-share` / `rl_compute_share` other than your own output)
Do not grep the home directory recursively.

**You may read**: the fetched source texts in `~/rcs_sources/` (plain text from arXiv HTML/PDF, model cards, configs,
blogs; line 1 of each file is its URL) and your own fetches. If a source you need is missing or garbled there, fetch it
yourself into `~/rcs_review_sources/` with `curl -sL -m 60 -A 'Mozilla/5.0 (research)' <url> -o <file>` (PDF →
`pdftotext -layout in.pdf out.txt`; HTML → a quick python BeautifulSoup get_text). Write line 1 of the text file as
`source: <url>`. Search with the WebSearch tool if needed (load it with ToolSearch `select:WebSearch`); search results
are leads, never evidence.

**Write only** your two output files (named in your task) under `/home/dan/work/rl-compute-share/review_rcs/ledger/`.
Do not commit, push, or edit anything else. Do not contact anyone.

**VPS limits.** 4 GB RAM shared with other runs: one command at a time, no background or parallel processes. Read with
`grep -n` and `sed -n 'a,bp'` ranges, never whole long files.

**Never write a value from memory.** Every value has a ledger row with a verbatim quote copied from the fetched text
(copy the characters exactly as they appear in the file, ≤ 300 characters, no tabs or newlines inside the quote; if
the text wraps across lines, quote a single-line part). If a value is not reported, write the row with value
`not reported` and the quote of the closest relevant passage (or `-` if nothing).

**Ledger format** (`<prefix>.tsv`), tab-separated, header line exactly:
`row_id	run	field	value	source_file	location	quote`
- `row_id`: `<prefix>-<n>`; `run`: a short label of the RL-trained model or experiment (e.g. `DeepSeek-R1-Zero`);
- `field`: one of the field names below; `source_file`: path relative to `~/` (e.g. `rcs_sources/2503.14476v2.txt`);
- `location`: section / table / figure / page or line number.

**Fields for every RL run** (one RL-trained model or experimental arm; give the largest/main configuration and note
others): `base` (exact checkpoint), `params_total`, `params_active`, `pretrain_tokens` (D for the base, including
continued pretraining; cite the base model's own report/card, and record mid-training/continued-pretraining tokens as
`cpt_tokens`), `algorithm`, `train_prompts` (unique), `epochs`, `steps` (RL steps / iterations; per stage if staged),
`prompts_per_step` (rollout batch, prompts), `group_size` (responses per prompt), `updates_per_step` (mini-batches ×
PPO epochs, if stated), `max_response_len`, `mean_response_len` (if reported; say at which point of training and from
where, e.g. figure axis), `prompt_len` (if reported), `kl_ref` (yes/no), `critic` (yes/no), `overgen` (dynamic sampling /
filtering / over-generation factor), `gpu_type`, `gpu_hours` (or wall-clock × GPUs), `cost` (if a dollar figure is
given), `verdict` (the paper's own create-vs-elicit conclusion, if any: create / elicit / both / none), `verdict_method`
(metric, max k, benchmarks), `scale_vary` (does the paper vary RL steps/compute within the study and measure pass@k at
large k? range of steps and k, direction of the effect), `contamination` (base saw instruction / synthetic CoT /
distilled from an RL-trained model, etc.).

**Summary file** (`<prefix>_summary.md`, ≤ 900 words): one compact table per run with field → value (row_id), plus a
line per run separating what the source states from your interpretation, and a list of anything UNVERIFIED.

**Final answer to the reviewer**: ≤ 300 words — files written, rows, anything surprising or ambiguous (e.g. two
sources disagreeing, unclear whether a batch counts prompts or responses).
