# olmo_answeronly/ — run olmo-answeronly (proposal 45)

Given the RL model's (`s2300`) own genuine thinking, is the DPO start's (`dpo`) failure only how it writes the answer?
olmo-transplant's stored traces re-inserted by token ids with one registered change each (A1 instruction, A2 60-word
hint, A3 closing line in the thinking, A4 ≤ 5-token answer prefill), both writers, 8 answers per trace; optional arm with
olmo-ifladder's `lora_main`. Pre-registration `../preregistration/olmo-answeronly.md`; write-up
`../run_olmo_answeronly.md`; numbers `../numbers.md` § olmo-answeronly; plain summary `plain_summary.md`; log
`../log.md` § olmo-answeronly.

## Pipeline

| step | script | output |
|---|---|---|
| registered wordings and ids | `wordings.py`; ids from `tok_enc.py` (torch-free ASCII BPE encoder; re-checked by the pod's HF tokenizer) | – |
| requests (VPS) | `build_requests.py reach|calib` (asserts prefix = stored ids + exactly the change); `build_lora_requests.py` | `artifacts/olmo_answeronly/requests/*.jsonl.gz`, `lora_traces.csv` |
| sampling (pod) | `sample_prefix.py` (olmo-transplant's + user_suffix, answer prefill, `--lora`) via `../pod/olmo_answeronly/job.sh` (queue `worker.sh`) | `samples/<job>.jsonl.gz`, `meta/<job>.json`, `meta/<job>_boundary.txt` |
| grading (pod) | `../olmo_transplant/grade_rows.py` (unchanged) | `graded/<job>.jsonl` |
| hand gate | `select_reads.py r1|r2`, `handcheck.py prep / batch / table`, reader prompt `handcheck_prompt.md`, dated readings `handcheck_rules.md` | `artifacts/olmo_answeronly/hand/run/` (items, key, labels, adjudicate.csv), `handcheck.csv` |
| analysis | `analyze.py --jobs R_dpo,R_s2300,C_dpo,C_s2300,L1_lora,L2_dpo,L3_lora`, `mechanism.py`, `figures.py`, `numbers_section.py` | `results.csv`, `summary.md/.json`, `mechanism.md`, `../figures/olmo_answeronly.png` |
| compute | `compute_rows.py` | `compute.md`, `../artifacts/olmo-answeronly/registry/` |

Jobs (seed): `R_dpo` 8201, `R_s2300` 8202 (reach, A1–A4), `C_dpo` 8211, `C_s2300` 8212 (calibration), `L1_lora` 8221,
`L2_dpo` 8222, `L3_lora` 8223. Inputs (`artifacts/olmo_answeronly/inputs/`, not tracked): olmo-ifomega's
`{F,C1,C2}_s2300_ifb.jsonl.gz`, olmo-transplant's `tp_{R,C}_{dpo,s2300}` samples / grades, olmo-ifladder's
`Leval_main`; fetch from their bucket paths (`../artifacts/MANIFEST.jsonl`).

## For the reviewer

- **Inserted prefix = stored ids + the registered change:** each request row has `src` (job|pid|chunk|i), `prefix`
  (base64 int32), `user_suffix`, `answer_prefill_k`; `build_requests.py` asserts it. Sample rows carry `input_sha256`
  of (prompt ids + prefix); the meta stores every user-turn variant's ids (`prompt_ids_variants`) and `a3_ids_hf`.
- **Template boundary:** `meta/<job>_boundary.txt` (decoded prompt tail of 40 tokens, prefix head, input tail).
- **A4 text** = decode(prefill + generated); `gen_text` is the generated part; `prefill_ids` recorded per row.
- **Readers** see the original user turn (A1 / A2 additions hidden to keep the condition blind).
