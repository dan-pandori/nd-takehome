# olmo_ifladder — code and results of run olmo-ifladder

How much of RL's instruction-following reach (Olmo 3.1 Think 32B `step_2300` succeeds, its DPO start does not in 256
draws) can the DPO start get without RL: by a ladder of prompt interventions (rungs 1–4), or by a LoRA fine-tune on 16
genuine RL trajectories against a control LoRA on 16 of `dpo`'s own? Write-up `../run_olmo_ifladder.md`; numbers
`../numbers.md` § olmo-ifladder; pre-registration `../preregistration/olmo-ifladder.md` (design and binding
expectations before any pod; deviations at the end); log `../log.md` § olmo-ifladder; plain summary
`plain_summary.md`. Bulk files (every sample's text and token ids, every grade, both adapters) are in
`hf://buckets/dan-pandori/nd-rl/olmo-ifladder/artifacts/olmo_ifladder/` and listed in `../artifacts/MANIFEST.jsonl`
(`python3 fetch_artifacts.py artifacts/olmo_ifladder/`). Merged weights were not kept (unused after the merge check;
deleted on the pod, which is gone).

Models: `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`); `s2300` = `allenai/Olmo-3.1-32B-Think` `main`
(`97ade57a` = `step_2300`); `lora_main` / `lora_ctrl` = `dpo` + this run's r 16 LoRA adapters
(`../artifacts/olmo_ifladder/lora/main`, `../artifacts/olmo_ifladder/lora/ctrl`), evaluated through vLLM's LoRA path. Decoding as olmo-iffu
(`olmo_thinker` template, T 1, top-p 1, 32,768 response tokens, vLLM 0.11.0, bf16, one H200, TP 1).

| file | what |
|---|---|
| `interventions.py` | the exact rung wordings: the 60-word line, the check line, one procedure hint per constraint id (`HINTS`, written from `DESCRIPTIONS` alone), `DROP60`; sha256 prefix `e3c284741c25d84c` (pre-registered) |
| `select.py` → `prompts.csv`, `problems_r1cal.jsonl`, `problems_r2.jsonl`, `problems_r3.jsonl`, `cand_exemplar.csv`, `cand_train.csv`, `overlap.csv` | the 48 reach + 10 calibration prompts with olmo-iffu's rung-1 status; prompt files per rung (`prompt_sample` = prompt + appended lines; grading uses `prompt`); exemplar and training candidates; the base-request overlap check (8-gram constraint masking, longest common run) |
| `sources.py` → `train_manifest.csv` / `.jsonl`, `pids_lchk.txt`, `pids_leval.txt`, `problems_plain.jsonl`, `exemplars.csv`, `problems_r4.jsonl` | the LoRA training manifest (16 slots × {`s2300`, `dpo`} + 8 held-out prompts: source job, draw, sha256 of the text, tokens, label source) and the rung-4 exemplars (pid, draw, sha256 of the answer), both fixed before use |
| `lora.py` | LoRA training (`RECIPE`: r 16, α 32, dropout 0.05, q/k/v/o/gate/up/down × 64 layers, AdamW 1e-4, 4 warm-up steps then cosine to 10 %, batch 1, 4 epochs = 64 steps, seed 20261109, response-only loss), the NLL checks and the merge check; reports in `../artifacts/olmo_ifladder/meta/lora_{main,ctrl}.json` |
| `sample.py` | olmo-iffu's sampler + multi-turn prompts (`messages_sample`, rung 4), the prompt's sha256 per pid in the meta, `--lora` (vLLM `LoRARequest`) |
| `stage0.py` | the stage-0 measurement and cost projection (`../artifacts/olmo_ifladder/meta/stage0_projection.json`) |
| `order_r2.txt` | the request order of the rung-2 jobs (`R2_dpo`, `R2_s2300`; longest-first from stage 0) |
| `next_rung.py` → `order_r3.txt`, `order_r4.txt` | cut 2: rungs 3 and 4 only on prompts no earlier rung elicited (plus calibration) |
| `jobs.csv` | every sampling job: model, arm, rung, engine seed, problems file, draws per prompt, prompts, pod |
| `handcheck.py`, `handcheck_prompt_if.md` | the blinded kit (items named by random ids; key kept from readers) and the reader prompt |
| `handcheck_rule_addendum.md` | my confirming rules (with olmo-ifomega's 1–5 and olmo-iffu's 6), not given to readers: 7–9 written before any ladder item was read; 10–12 (one reading each for 206, 207, 268) added during the `s2300` sanity gate, after every `dpo` / LoRA cell was decided |
| `handcheck_src.csv` | this run's source gate (231 reads of stored trajectories before use as exemplars or training examples; kit `../artifacts/olmo_ifladder/hand_src/`); the other sources carry olmo-ifomega's labels (`label_src` in `train_manifest.csv` / `exemplars.csv`: 13 of 32 training trajectories, 23 of 116 exemplars) |
| `gate.py` | per-cell bookkeeping: strict successes in draw order, the mechanical rule-1 pre-screen, identity inheritance, reads still needed, deciding items for second reads; `../artifacts/olmo_ifladder/gate_status.csv` |
| `handcheck.csv` (`handcheck.py table artifacts/olmo_ifladder/hand olmo_ifladder/handcheck.csv`) | every hand-read ladder, LoRA and `s2300`-sanity response: item, job, prompt, draw, reader labels and evidence, my confirmation (`final_label`); items, key, batches and reader files in `../artifacts/olmo_ifladder/hand/` |
| `pids_sanity_r2.txt`, `pids_sanity_r3.txt`, `pids_sanity_r4.txt` | the `s2300` sanity cells that were hand-gated: the prompts no rung up to that one elicited (where a `dpo` failure decides a reading); 31 / 26 / 23 |
| `analyze.py` → `results.csv`, `classify.csv`, `summary.json` | one row per job × prompt (draws, strict, loose, cut, tokens, thinking tokens, answer words, gate state); one row per reach prompt (state per rung and LoRA, reading, flags, Fisher sensitivity); the counts |
| `lengths.py` → `lengths.csv` | thinking tokens and answer words without hints: `dpo` and `s2300` (olmo-ifomega's stored fixed-phase draws), both LoRAs |
| `figures.py` → `../figures/olmo_ifladder_ladder.png` | the per-prompt ladder figure (needs matplotlib) |
| `compute_rows.py` | registry compute rows per job and per LoRA training |

Pod scripts: `../pod/olmo_ifladder/` (pod-side `setup.sh`, `job.sh`, `start.sh` and the queue `worker.sh` reading
`../artifacts/olmo_ifladder/queue/q0.txt`; VPS-side `launch.sh`, `push.sh`, `pull.sh`, `poll_pod.sh`). Claim checks of the
write-up: `claim_check_numbers.md`, `claim_check_writeup.md` and the second pass `claim_check_second.md` (findings and
their resolution, before publication).

**Recompute** (repository root, after `python3 fetch_artifacts.py artifacts/olmo_ifladder/` and, for `lengths.py`,
`python3 fetch_artifacts.py artifacts/olmo_ifomega/samples/F_dpo_ifb.jsonl.gz artifacts/olmo_ifomega/samples/F_s2300_ifb.jsonl.gz
artifacts/olmo_ifomega/samples/F_dpo_ife.jsonl.gz artifacts/olmo_ifomega/samples/F_s2300_ife.jsonl.gz`):
`python3 olmo_ifladder/handcheck.py table artifacts/olmo_ifladder/hand olmo_ifladder/handcheck.csv && python3
olmo_ifladder/gate.py status R2_dpo R3_dpo R4_dpo Leval_main Leval_ctrl R2_s2300 R3_s2300 R4_s2300 && python3
olmo_ifladder/analyze.py && python3 olmo_ifladder/lengths.py && python3 olmo_ifladder/figures.py`. Re-grade a samples
file (the checkers need nltk / langdetect): `python3 olmo_ifomega/grade.py <samples.jsonl.gz> <problems.jsonl>
<out.jsonl>` with the job's problems file from `jobs.csv`.
