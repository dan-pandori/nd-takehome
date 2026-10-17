# Reader notes: OUR side (Dan's models) for the cross-person RL comparison

Written 2026-10-17 by a read-only assistant for the independent reviewer. I read every number below myself from nd-rl
`origin/dan` with `git show`, `git ls-tree` and `git grep` (line numbers from `cat -n` / `grep -n`). Citation form:
`KEY:Lnn` = `origin/dan:<path>:Lnn`, with KEY expanded in §1. Quotes are exact fragments of the cited line(s).

**Not read (independence rules):** anything under `/home/dan/work/peer-rl-review`, `/home/dan/nd-takehome`,
`/home/dan/review/peer-rl-review/peer_rl_review` or `/home/dan/runs/`; any git ref or path containing
`peer-rl-review` / `peer_rl_review`; nd-rl `docs/project_strategy/2026-10-17*`.

**Not in nd-rl:** the fork files `NOISE_FLOOR.md` and `numbers.md` (`git ls-tree -r origin/dan` lists no
`NOISE_FLOOR*`). Numbers whose only nd-rl source is a model card are marked **card only**.

---

## 1. Inventory of documents read

| key | `origin/dan:` path | used for |
|---|---|---|
| SEO | `docs/models/state_env_october.md` | model card (anchor) |
| R16 | `docs/models/state_env_october_r16.md` | model card (anchor) |
| BS | `experiment-summaries/2026-09-30-best-state-robbies-recipe-wins-after-rl-level-frozen-at-cap12/README.md` | introduced best-cap12 (= `state_env_october`, best-state seeds); 3.2 M vs 9.56 M |
| TJ | `experiment-summaries/2026-10-01-trajectory-eventual-proof-worst-step-climbs-in-pretraining-and-rl/README.md` | trajectory seeds of best-cap12; groups A/B/C |
| TJ6 | `experiment-summaries/2026-10-02-trajectory-cap6-eventual-proof-worst-step-climbs-mainly-in-rl/README.md` | best-cap6, trajectory seeds |
| RC | `experiment-summaries/2026-10-03-rl-continue-cap12-group-c-rises-on-3-of-3-seeds-saturation-falsified-target-burst-is-one-seeds-excluded-middle/README.md` | r9–r16 (= `state_env_october_r16`) |
| RC6 | `experiment-summaries/2026-10-03-rl-continue-cap6-group-c-rises-on-3-of-3-seeds-saturation-falsified-cap-6-still-below-cap-12/README.md` | best-cap6 r9–r16 |
| GT | `experiment-summaries/2026-10-03-guided-tts-logical-redraws-beat-plain-on-long-theorems-structural-redraws-do-not/README.md` | plain vs guided; Charles's release |
| GB | `experiment-summaries/2026-10-02-grpo-best-grpo-default-trades-theorems-with-ei-pass4-level-overall/README.md` | GRPO vs EI (9.56 M, state) |
| GS | `experiment-summaries/2026-09-30-grpo-state-code-phase-grpo-in-the-state-env/README.md` | GRPO code phase (no result) |
| R2R4 | `experiment-summaries/2026-09-18-round2-run4-grpo-vs-ei/README.md` | older GRPO vs EI (3.2 M, token format) |
| R4GR | `experiment-summaries/2026-09-28-run4-grpo-review-grpo-ignites-from-zero/README.md` | older GRPO replication, reviewed |
| CM | `experiment-summaries/2026-10-02-compute-match-matched-ladder-gpu-time-does-not-close-gap/README.md` | compute-match |
| MA | `experiment-summaries/2026-10-02-mcts-a-puct-value-search-gate-fails-on-group-c/README.md` | MCTS-a |
| MB | `experiment-summaries/2026-10-03-mcts-b-not-run-mcts-a-gate-failed/README.md` | MCTS-b |
| CD | `experiment-summaries/2026-10-05-capability-defs-compute-matched-budget-shrinks-equal-k-creations-rl-still-ahead-lem-teachable/README.md` | capability-defs |
| COE | `experiment-summaries/2026-10-12-create-or-elicit-sigma-knockout-not-acquired-in-16-ei-rounds-needs-exposure-1pct-dose-restores/README.md` | create-or-elicit |
| COEP | `experiment-summaries/2026-10-13-create-or-elicit-paper-draft-and-blog-no-headline-number-wrong-c4-drops-knockout-s1-elicitation-reading/README.md` | paper-writing run |
| PC | `experiment-summaries/2026-10-14-paper-clean-clean-paper-and-blog-equivalent-to-reviewed-copy-12-of-13-possible-errors-fixed/README.md` | paper-clean (head only) |
| P-ABS, P-MEAS, P-LIM, P-CHK | `docs/papers/create-or-elicit/sections/{00_abstract,04_measurement,08_limitations,11_checks}.tex` | paper: abstract, measurement §, limitations, check C3 (I grepped all sections for textbook72 / holdout250 / dev / Robbie / Charles / Leon) |
| SE | `experiment-summaries/2026-09-28-state-env-state-lifts-below-the-wall/README.md` | 3.2 M SN-v2 / S / SH, C0 |
| SC12 | `experiment-summaries/2026-09-29-state-cap12-state-and-cap12-proofs-compound-on-long-pool/README.md` | 3.2 M SN-cap12; K12 whole-proof T1 |
| TB72 | `experiment-summaries/2026-09-30-textbook72-sn-cap12-t1-solves-37-of-72/README.md` | textbook72 reads of the 3.2 M SN models |
| RFC | `experiment-summaries/2026-10-02-rl-from-ckpt-early-start-ladders-reach-end-arm-from-step-5000/README.md` | pend / r8 x1 table; replay-only control; MDD |
| CA | `experiment-summaries/2026-10-02-claim-audit-headline-counts-reproduce-three-claims-weaker-than-stated/README.md` | claim-audit summary |
| CAD | `docs/project_strategy/2026-10-03-claim-audit.md` | claim-audit ledger (reading copy) |
| ATL, ATLH, MAP, ATLX | `experiment-summaries/2026-10-02-evidence-atlas-map-of-95-experiments-whole-proof-rescore/{ATLAS.md, data/headline_table.csv, MAP.md, data/experiment_map.csv}` | evidence atlas |
| NF | `experiment-summaries/2026-09-25-noise-floor-measurement-floor/README.md` | noise-floor run (C0 configuration only) |
| LJ | `experiment-summaries/2026-09-27-lean-judge-lean-alone-decides/README.md` | the 2026-09-27 judge switch |
| STATE | `docs/STATE.md` (L145–L173) | headline index, cross-check |
| P23 | `docs/proposals/2026-10-03-rl-on-textbook-release.md` | Charles's release; Charles's own score of our model |
| WIR | `docs/project_strategy/2026-10-08-week-in-review.md` (L95–L96) | Charles-release headline |

**Searched for and not found:**
- a "Charles149" set (`git grep` for `charles149`, `of 149`, `/149` over `docs/` and `experiment-summaries/`: no hits);
- a textbook72-level pass@1 for any of our models. Only group-level pass@1 exists (A/B/C over the 322; §3.2).

---

## 2. Model roster (our models)

All are trained from scratch. "Lean alone" = the post-2026-09-27 judge: LJ:L31–L33 "the 2026-09-27 update ... "Lean
alone is the reward and the checker for every new run"". All 9.56 M runs below are dated 2026-09-30 or later.

| name | params | interface | format / net | Stage-1 data + cap | RL algorithm + compute | judge | where defined |
|---|---|---|---|---|---|---|---|
| **`state_env_october`**, best-state seeds (internal: best-cap12, best12). `best-state/ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt` | **9,560,832** (+1.88 M MTP head, training only, not saved) | proof state, one step at a time, env-assigned names (`lean_staten`, SN-v2) | `ALiBiGPT` 6 × 384, Peri-LN, 4 ALiBi + 4 NoPE heads; Muon + AdamW, MTP 0.3 (Robbie's incumbent 186) | **K12**: 155,000 synthetic ND proofs, flat 2–12 lines (cap 12). 1,200 s on one A40 (23,951–24,123 steps; 1,283–1,292 A40-s) | **T1 EI**: 8 rounds × k 32, T 0.8, 4,495 `rl_targets`, K12 replay, 600 fine-tune steps per round (4,800). Ladder **25,876 / 30,524 / 28,952 A40-s**; 1,794 k clean attempts (1,793,960 gate samples per clean ladder); 393–419 M gen tokens; 1.28–1.30 M Lean checks | Lean 4 core alone (post 09-27) | SEO:L16–L21 ("**9,560,832 parameters**"; "**K12**: 155,000 synthetic ND proofs, flat lengths 2–12 lines"; "T1 expert iteration: 8 rounds, k 32, T 0.8, 4,495 `rl_targets`, K12 replay, 600 fine-tune steps per round"; "Lean 4 core alone"); SEO:L26; BS:L50–L51, L60–L61; BS:L82 ("25,876 / 30,524 / 28,952"); BS:L128 ("1,793,960 gate samples per clean ladder") |
| **`state_env_october`**, trajectory seeds ("three fresh seeds of the same recipe"). `trajectory/ckpts/tj/ladder/la_T1_best12_s{0,1,2}_r8.pt` | 9,560,832 | same | same | K12; 1,200 s on an A40 (24,077 / 24,345 / 24,328 steps; 1,350 A40-s each); held-out greedy 0.921 / 0.936 / 0.962 | Same T1 protocol, ladders on **RTX A6000**: **22,350 / 24,467 / 27,021 A6000-s**; attempts 1,794 / 1,794 / 2,011 k (s2 includes an OOM'd round; s2 resumed at batch 1,024); train tokens 754 / 783 / 751 M; Lean checks 1,299 / 1,313 / 1,417 k | Lean alone | SEO:L27–L28; TJ:L48–L58 ("on RTX A6000s, giving **r1–r8**"); TJ:L94–L95 ("22,350 / 24,467 / 27,021") |
| **`state_env_october_r16`** = trajectory seeds + 8 more rounds. `rl-continue/ckpts/rc/ladder/la_T1_best12_s{0,1,2}_r16.pt` (r12 also saved) | 9,560,832 | same | same | same as trajectory seeds | r1–r8 as above (A6000) + **r9–r16 on A40**: same T1 settings (k 32, T 0.8, 600 steps/round at lr 3e-4, replay 20,000 K12 records); **33,248 / 32,830 / 31,457 A40-s** (reviewer's sums; the card quotes the executor's 31,471–33,261); 1,793,960 attempts and 4,800 train steps per seed; 905.5 / 904.9 / 883.3 M train tokens | Lean alone ("No comparison crosses the 2026-09-27 change") | R16:L8–L10, L17, L25; R16:L57–L58 ("31,471–33,261 A40 GPU-seconds per seed"); RC:L36–L39; RC:L54–L56; RC:L179–L185 ("33,248"; "32,830"; "31,457") |
| **Stage-1 best12** ("pend", "Fz", "r0"): `best-state/ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt` and **a different training with the same file name** `trajectory/ckpts/tj/stage1_best12_s{0,1,2}_b1200.pt` (md5 2bf801fd / eaff7f4d / abca9c63) | 9,560,832 | same | same | K12, 1,200 s A40 | none | n/a | SEO:L28–L29; GB:L36–L37 |
| **GRPO arms** (grpo-best): `grpo-best/ckpts/gb/gb_<arm>_s<S>_r<k>.pt`, arms `default` (A = R − group mean), `unlikely` (β_rank 0.25), `passk` (k 4), `distinct` (bonus 0.5; optional, stopped at r4) | 9,560,832 | same | same | trajectory's Stage-1 pend (row above) | GRPO: G 8, 256 theorems per update, **561 updates** (1,792,168 attempts vs EI's 1,793,960), AdamW lr 3e-5 constant, no KL, no replay, T 0.8, caps 256 / 48. RTX A6000, two ladders per card (pass@4 s2 on A40): 24,571–29,360 GPU-s (co-tenant wall-clock) = 1.00–1.13× EI; train tokens 0.17–0.37× EI | Lean alone (reward and eval via `lean_judge.judge_many`) | GB:L43–L48 ("**561 updates** (equal sampled attempts to EI: 1,792,168 against 1,793,960)"); GB:L49; GB:L195–L203 |
| **best-cap6** (Robbie's recipe on cap-6 data, proof state). best-state: `la_T1_best6_s{0,1,2}_r8.pt`; trajectory-cap6: `la_T1_best6_s{0,1,2}_r8.pt` (fresh seeds); rl-continue-cap6: `la_T1_best6_s{0,1,2}_r{9..16}.pt` | 9,560,832 | same | same | cap-6 control set `train_depth3_f0_a1` (155,000; cap 6), 1,200 s A40 | T1 8 rounds × k 32. best-state ladders 20,057 / 16,881 / 17,885 A40-s; trajectory-cap6 ladders 17,990 / 17,730 / 16,763 A40-s, 1,794 k attempts each; r9–r16: 33,464 / 25,666 / 26,517 A40-s (includes r16 reads) | Lean alone | BS:L50, L81; TJ6:L57–L65, L100–L101; RC6:L32–L36, L164–L168 |
| **SN-v2 cap 6** ("ours", 3.2 M): `state-env/ckpts/se/ladder/la_T1_SN_s{0,1}_r8.pt`, frozen `stage1_SN_s{0,1}.pt` | **3,216,384** | proof state (`lean_staten`) | GPT 4 layers, d 256, 8 heads, AdamW | cap-6 set (155,000), 6,000 steps × 128 proofs; Stage-1 782 / 565 s (RTX 3090 / RTX PRO 4000) | T1 8 rounds × k 32, T 0.8 (1,150,720 RL-target attempts per ladder); 8,297 / 8,761 GPU-s (3090 / PRO 4000) | Lean alone | SE:L32–L38, L42, L45–L47; BS:L52, L83 |
| **SN-cap12** ("ours", 3.2 M): `state-cap12/ckpts/sc12/ladder/la_T1_SN12_s{0-3}_r8.pt`, frozen `stage1_SN12_s{0-3}.pt` | 3,216,384 | proof state | same | K12 (155,000, cap 12), 6,000 steps × 128; Stage-1 1,852 / 1,835 s (3090), 2,244 / 2,250 s (A40) | T1 8 rounds × k 32, T 0.8, replay K12; 12,672 / 12,992 (3090), 16,623 / 16,042 (A40) GPU-s; 1,799 k attempts | Lean alone | SC12:L32–L37; BS:L53, L84 |
| **cm12** (compute-match): `la_T1_cm12k64_s{0,1,2}_r8.pt` | 3,216,384 | proof state | same | SN-cap12 Stage-1 s0–s2 (inherited) | T1 8 rounds at **k 64**: 27,485 / 29,226 / 30,675 A40-s = **1.02×** best12's 28,451; 3,529,640 attempts each (**1.82×**) | Lean alone | CM:L49–L52, L120–L125 |
| **Whole-proof 3.2 M** (`lean_seq`): C0 cap 6 frozen `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}`, T1 `ds-generator/.../la_T1_c0_s{0,1}_r8`; K12 cap 12 frozen `cap-horizon/ckpts/kh/stage1_k12_s{0,1}`, T1 `state-cap12/.../la_T1_K12_s{0,1}_r8` | **3,214,336** | whole proof | GPT 4 × 256 | C0: cap-6 set; K12: K12 | T1 8 rounds (K12: `ladder_ei.py`, replay K12, `max_new` 512; pods `sc-k0` / `sc-k1` A40 1.31 h / 1.30 h) | **C0 ladder trained under Lean ∧ `nd_verify` (2026-09-24, pre-switch)**; K12 T1 Lean alone; all atlas reads Lean alone | ATL:L190–L194; SC12:L38–L41, L58–L59; SE:L40–L42 |
| **create-or-elicit arms**: full s0–s2 (= trajectory seeds, r9–r16 = `rl-continue`), **full s3–s5** (new), knockout s0–s5 (K12⁻), dose1 s0–s2 (K12^1%). `create-or-elicit/ckpts/coe/ladder/la_{full,ko,dose1}_s{S}_r{R}.pt` | 9,560,832 | proof state | same | K12 / K12⁻ (σ⁺ records removed, refilled) / K12^1%, 155,000 each, 1,200 s A40 | T1 **16 rounds**, k 32, T 0.8, 600 steps/round, 20,000 replay from the arm's own set; per new ladder (A40, batch 1,024): total ≈ 54,105 (ko) / 55,841 (full) / 56,390 (dose1) GPU-s; 2,301,440 target attempts; 9,600 fine-tune steps | Lean alone | COE:L61–L75, L141–L156 |
| RL-free controls: replay-only `c<S>_pend_r8` (rl-from-ckpt `rc_best12_s<S>_<start>`); J7 compute-matched continuation of pend (capability-defs) | 9,560,832 | proof state | same | from pend | replay-only: 8 rounds × 600 steps on K12 replay alone (≈ 3,170 A6000-s at pend). J7: 28,054 / 31,462 / 33,535 steps in 18,308 / 20,494 / 21,824 A40-s | Lean alone | RFC:L72–L77, L113–L114; CD:L51–L52, L291–L293 |
| 3.2 M **S** / **SH** (`lean_state`, `lean_stateh`) | 3,216,384 | proof state (own names / with history) | GPT 4 × 256 | cap-6 set | T1 8 rounds × k 32 | Lean alone | SE:L35–L38 (no textbook72 read anywhere) |
| Older 3.2 M **token-format** GRPO / EI (round2-run4; run4-grpo replication) | 3,210,240 (run4-grpo) | whole proof | ND token format (`--mode abs`) | `train_depth3_f0_*` (cap 6, 0 depth-3 proofs) | GRPO G 8 / 32, 256,000 samples = EI's 8 × 32 × 1,000 | **`nd_verify`** (pre-switch) | R2R4:L39–L56; R4GR:L39–L47 |

---

## 3. Headline numbers (our side)

Common read protocol unless a row says otherwise: `state_eval.py`, solved = ≥ 1 Lean-accepted attempt of k, T 0.8,
`max_action` 512, `max_steps` 96 (BS:L66 "`state_eval.py` k 256, T 0.8, seed 0, `max_action` 512, `max_steps` 96").
Sets: **textbook72** = dev58 + train14, eval-only (BS:L66; TB72:L38–L41). **dev metric** = "the 1,108 `transfer.jsonl`
records with `int(sha1(key), 16)` even, k 64, solved count (all `L_true` ≥ 7)" (BS:L69–L70). **holdout250** = Robbie's
`passk.py` pool, k 256 (BS:L70). **Q** = rr600 generator theorems at `L_true` 13–16, /380 (BS:L71). "x0 / x1" = sample
seeds 0 / 1.

### 3.1 `state_env_october`, best-state seeds, T1 r8 (the card's headline block)

| value + metric | set (n) | k | n samples / draw | T | plain / guided | judge | seeds s0 / s1 / s2 | reviewed? | citation: quote |
|---|---|---|---|---|---|---|---|---|---|
| solved, mean 51.67 | textbook72 (72) | 256 | 256, seed 0, batch 2,048 | 0.8 | plain | Lean | **52 / 51 / 52** | yes: "all reproduced file for file by the reviewer" (BS:L90) | BS:L94 "**52 / 51 / 52**"; SEO:L34 "textbook72 at pass@256: **52 / 51 / 52** of 72" |
| solved at 2× caps (`max_action` 1,024, `max_steps` 192) | textbook72 | 256 | diagnostic re-read | 0.8 | plain | Lean | s1 51 → 53, s2 52 → 53 | yes | BS:L171–L173 "T1 best12 s1 textbook72 51 → 53, T1 best12 s2 52 → 53" |
| solved | dev1108 (1,108) | 64 | 64 | 0.8 | plain | Lean | 1,058 / 1,050 / 1,055 | yes | BS:L95; SEO:L35 "1,058 / 1,050 / 1,055 of 1,108" |
| solved | holdout250 (250) | 256 | 256 | 0.8 | plain | Lean | 239 / 237 / 237 | yes | BS:L96; SEO:L36 |
| solved | Q (380) | 256 | 256, `lpool_reread.py` | 0.8 | plain | Lean | 377 / 375 / 376 | yes | BS:L97; SEO:L37 "377 / 375 / 376 of 380" |
| solved | `transfer_long2` (21, lengths ≥ 17) | 256 | 256 | 0.8 | plain | Lean | 21 / 21 / 20 | yes | BS:L98; SEO:L38 |
| greedy accuracy | p2 held-out (5,000) | 1 | 1 | 0 | greedy | Lean | .992 / .990 / .993 | yes | BS:L99 |
| `rl_targets` solved cumulatively at r8 | 4,495 | ladder (k 32 per round) | 8 rounds | 0.8 | ladder | Lean | 4,375 / 4,378 / 4,392 | yes (reviewer recount) | BS:L134–L136 "best12 4,375 / 4,378 / 4,392 of 4,495" |

### 3.2 `state_env_october`, trajectory seeds, T1 r8

| value + metric | set (n) | k | n samples / draw | T | plain / guided | judge | seeds s0 / s1 / s2 | reviewed? | citation: quote |
|---|---|---|---|---|---|---|---|---|---|
| solved | textbook72 (72) | 256 | x0, batch 2,048 | 0.8 | plain | Lean | 48 / 49 / 54 | yes | TJ:L108 "48 / 49 / 54" |
| solved | textbook72 | 256 | x1, batch 2,048 | 0.8 | plain | Lean | **48 / 48 / 53** | yes ("r8 values are `trajectory`'s files") | RC:L46, L147–L149; R16:L33; RFC:L138; GT:L103 "Plain on textbook72 is 48 / 48 / 53 (cap 12)" |
| solved | textbook72 | 256 | sample seed 2, batch 2,048 | 0.8 | plain | Lean | 49 / 50 / 55 | yes | MA:L81 "49 / 50 / 55" |
| solved | textbook72 | 256 | sample seed 1, ≤ 10 redraws per attempt | 0.8 | **guided-logical** | Lean | **54 / 52 / 57** | **card only**; the per-seed totals over all 259 reproduce GT's reviewed logical counts | SEO:L43 "48 / 48 / 53 \| **54 / 52 / 57**"; GT:L102 |
| logical − plain at matched sampled tokens, 64 plain-equivalent attempts: IQM **+5.4 pp** | textbook72 | 64 (matched) | from the 256 reads | 0.8 | guided vs plain | Lean | IQM only | yes | GT:L92–L93 "textbook72 +5.4 / +4.8"; SEO:L49–L50 |
| logical − plain, matched tokens, k 64: IQM **+9.1 pp** (k 256: IQM +10.0) | "long" = release rows with `min_lines` > 10 (90) | 64 | plain at k 64: 36.8 / 28.7 / 40.2 % | 0.8 | guided vs plain | Lean | +10.0 / +9.9 / +5.2 pp | yes | GT:L43; GT:L80 "36.8 / 28.7 / 40.2 \| +10.0 / +9.9 / +5.2, IQM **+9.1**" |
| solved, plain → guided (256 attempts each; not compute-matched) | Charles's `candidate_v0` (87) / `candidate_v1` (72) / `batch3` (14) / `hand_proved_14` (14) | 256 | sample seed 1 | 0.8 | plain → guided | Lean | v0 67 / 65 / 71 → 75 / 71 / 75; v1 52 / 51 / 55 → 59 / 57 / 56; batch3 11 / 8 / 9 → 12 / 10 / 11; hand 0 → 0 | **card only** (sums match GT's reviewed totals) | SEO:L44–L47; WIR:L95–L96 "proves 71–75 of the 87 in `candidate_v0` and 56–59 of the 72 in `candidate_v1`" |
| solved@256, plain / structural / logical | all 259 (textbook72 + 187 release) | 256 | sample seed 1, batch 2,048 | 0.8 | 3 arms | Lean | s0 178 / 185 / 200; s1 172 / 176 / 190; s2 188 / 193 / 199 | yes | GT:L102 "c12 178/185/200, 172/176/190, 188/193/199" |
| solved | holdout250 | 256 | x0 / x1 / seed 2 | 0.8 | plain | Lean | x0 238 / 237 / 239; x1 240 / 236 / 237; seed 2 239 / 236 / 239 | yes | TJ:L109; RC:L147–L149; MA:L83 |
| solved | textbook72 + holdout250 (322) | 256 | x1 | 0.8 | plain / guided | Lean | plain 288 / 284 / 290; guided 293 / 289 / 297 | yes | GB:L117 "288 / 284 / 290"; CD:L236 "293 (288) / 289 (284) / 297 (290)" |
| solved, **mean 1,053** (per seed not given) | dev1108 | 64 | 64, seed 0 | 0.8 | plain | Lean | — | yes | GB:L56; GB:L123–L124 "means 1,026 / 1,027 against EI's 1,053" |
| solved | rr600 rows with `L_true_lb` 13–16 (400; includes textbook rows) | **64** | x0, batch 512 | 0.8 | plain | Lean | 377 / 362 / 367 | yes | RC:L47–L48; RC:L147–L149 |
| solved | rrQ100 (100 of rr600 L13–16) | 256 | seed 2 | 0.8 | plain | Lean | 96 / 93 / 92 | yes | MA:L85 |
| solved | `transfer_long2` (21) | 256 | x0 batch 512 / seed 2 | 0.8 | plain | Lean | 21 / 20 / 20 (RC); 21 / 19 / 19 (MA) | yes | RC:L147–L149; MA:L87 |
| group C (per seed: x0-unsolved at pend and r8; 36 / 35 / 28) solved; mean pass@256 | group C | 256 | x1 / seed 2 | 0.8 | plain | Lean | x1 solved 3 / 1 / 1, pass@256 .083 / .029 / .036; seed 2 solved 4 / 2 / 4 | yes | RC:L49–L50, L107–L108; GB:L96; MA:L79 |
| pass@1 / pass@256, groups A / B / C (pooled over seeds) | A 232–236, B 51–60, C 28–36 per seed | unbiased estimator | n = 256, x1 | 0.8 | plain | Lean | pass@1 .85 / .56 / 0; pass@256 .99 / .96 / .05 | yes ("reproduced by the reviewer to 0.1 nat / 0.001") | TJ:L71; TJ:L123; TJ:L131–L132 |
| `rl_targets` cumulative at r8 | 4,495 | ladder | | 0.8 | ladder | Lean | 4,383 / 4,365 / 4,407 | yes | TJ:L58; R16:L35 |
| greedy accuracy at r8 | 5,000 | 1 | | 0 | greedy | Lean | 0.98–0.99 (range for every arm) | yes | GB:L141 |

### 3.3 `state_env_october_r16` (trajectory seeds; plain only, x1 for textbook72 / holdout250)

| value + metric | set (n) | k | n samples / draw | T | plain / guided | judge | seeds s0 / s1 / s2 | reviewed? | citation: quote |
|---|---|---|---|---|---|---|---|---|---|
| solved r8 / r12 / **r16** | textbook72 | 256 | x1, batch 2,048 | 0.8 | plain | Lean | 48 / 51 / **51**; 48 / 52 / **57**; 53 / 58 / **56** | yes: "reviewed, stands" | RC:L147–L149; R16:L33 "**51 / 57 / 56**"; R16:L46 "(reviewed, stands)" |
| solved r8 / r12 / r16 | holdout250 | 256 | x1 (s2 r16 retried at batch 1,024) | 0.8 | plain | Lean | 240 / 239 / 240; 236 / 241 / 246; 237 / 239 / 239 | yes | RC:L51–L53, L147–L149; R16:L34 |
| solved r8 → r16 | rr600 L13–16 (400) | 64 | x0, batch 512 | 0.8 | plain | Lean | 377 → 382; 362 → 370; 367 → 376 | yes | RC:L147–L149; R16:L36 |
| solved r8 → r16 | `transfer_long2` (21) | 256 | x0, batch 512 | 0.8 | plain | Lean | 21 → 21; 20 → 21; 20 → 20 | yes | RC:L147–L149; R16:L37 |
| group C solved r8 → r12 → r16; mean pass@256; r16 pass@8 / pass@1 | 36 / 35 / 28 | 256 | x1 | 0.8 | plain | Lean | solved 3→5→6, 1→8→17, 1→5→4; pass@256 r16 .167 / .486 / .143; pass@8 .081 / .257 / .081; pass@1 .035 / .144 / .044 | yes | RC:L107–L110; R16:L38 |
| `rl_targets` cumulative (new r9–r16) | 4,495 | ladder | | 0.8 | ladder | Lean | 4,403 (+20) / 4,433 (+68) / 4,429 (+22) | yes | RC:L81–L82 |
| solved, plain x1 (guided) | 322 | 256 | x1 / guided | 0.8 | plain (guided) | Lean | 291 (295) / 303 (303) / 295 (303) | yes | CD:L236 "295 (291) / 303 (303) / 303 (295)" |
| solved@256 (mean pass@1) | lem39 (39 held-out A ∨ ¬A) | 256 | | 0.8 | plain | Lean | 0 / **36 (0.70)** / 13 (0.13) | yes | CD:L254 |
| strict σ-covered held-out members solved | 106 | 256 | x0 / x1 / guided | 0.8 | plain / guided | Lean | x0 42 / 75 / 77; x1 43 / 73 / 77; guided 44 / 75 / 80 | yes | COE:L205–L207 |

### 3.4 Stage-1 best12 only ("pretraining only", pend, Fz, r0)

| value + metric | set (n) | k | draw | T | judge | seeds s0 / s1 / s2 | reviewed? | citation: quote |
|---|---|---|---|---|---|---|---|---|
| best-state Fz: solved | textbook72 / dev1108 / holdout250 / Q / long2; greedy | 256 / 64 / 256 / 256 / 256; 1 | seed 0 | 0.8 (greedy T 0) | Lean | tb72 32 / 27 / 27; dev 782 / 767 / 741; h250 184 / 195 / 182; Q 271 / 237 / 216; long2 10 / 5 / 4; greedy .926 / .951 / .903 | yes | BS:L94–L99 |
| trajectory pend: solved | textbook72 | 256 | x0 b2,048 / x1 b2,048 / seed 2 / x0 b512 | 0.8 | Lean | 32 / 32 / 38; **34 / 33 / 36**; 32 / 32 / 36; 34 / 30 / 34 | yes | TJ:L108; R16:L33 ("34 / 33 / 36"); RFC:L138; MA:L82; P-CHK:L41–L42 "prove 34, 30 and 34 ... against 32, 32 and 38" |
| trajectory pend: solved | holdout250 | 256 | x0 / x1 / seed 2 | 0.8 | Lean | 200 / 204 / 196; 196 / 205 / 200; 199 / 207 / 204 | yes | TJ:L109; R16:L34; MA:L84 |
| trajectory pend: solved | 322 | 256 | plain x1 (guided) | 0.8 | Lean | 230 (260) / 238 (266) / 236 (270) | yes | CD:L236 "260 (230) / 266 (238) / 270 (236)" |
| trajectory pend: solved | rrQ100 / long2 | 256 | seed 2 | 0.8 | Lean | 59 / 65 / 60; 8 / 5 / 4 | yes | MA:L86, L88 |
| trajectory pend: greedy accuracy | 5,000 | 1 | | 0 | Lean | 0.921 / 0.936 / 0.962 | yes | TJ:L52 |
| `rl_targets` = the pretrained model's own pass@32 (round 1's sample) | 4,495 | 32 | | 0.8 | Lean | 3,676 / 3,705 / 3,741 | **card only** | R16:L35, L41–L42 |

### 3.5 best-cap6 (9.56 M, Robbie's recipe on cap-6 data, proof state)

| value + metric | set (n) | k | draw | T | judge | seeds s0 / s1 / s2 | reviewed? | citation |
|---|---|---|---|---|---|---|---|---|
| best-state T1 r8 solved | tb72 / dev / h250 / Q / long2 | 256 / 64 / 256 / 256 / 256 | seed 0 | 0.8 | Lean | 39 / 40 / 33; 1,002 / 986 / 1,002; 226 / 229 / 227; 350 / 346 / 339; 18 / 18 / 17 | yes | BS:L94–L98 |
| best-state Fz solved | same | same | seed 0 | 0.8 | Lean | 19 / 18 / 20; 569 / 466 / 506; 149 / 125 / 122; 8 / 4 / 7; 0 / 0 / 0 | yes | BS:L94–L98 |
| trajectory-cap6 r8 (r0) solved | textbook72; holdout250 | 256 | x0 | 0.8 | Lean | tb72 43 / 41 / 38 (r0 17 / 14 / 15); h250 225 / 228 / 224 (r0 152 / 124 / 125) | yes | TJ6:L118–L119 |
| r8 → r16 solved | textbook72 | 256 | x1 | 0.8 | Lean | 43 → 45; 43 → 41; 39 → 40 | yes | RC6:L106; GT:L103 ("43 / 43 / 39 (cap 6)") |
| group C (52 / 52 / 60) pass@256 r8 → r16 | group C | 256 | x1 | 0.8 | Lean | .077 → .192; .038 → .154; .050 → .183 | yes | RC6:L102 |
| logical − plain on long, k 64, IQM +8.3 pp | long (90) | 64 | | 0.8 | Lean | +7.4 / +8.1 / +10.3 | yes | GT:L81 |

### 3.6 3.2 M models ("ours" in best-state's language)

| model | value + metric | set (n) | k / draw | judge | per seed | reviewed? | citation |
|---|---|---|---|---|---|---|---|
| SN-cap12 T1 r8 (s0–s3) | solved; IQM 37.5 [36, 38] | textbook72 | k 256, seed 0, **batch 4,096** | Lean | **37 / 38 / 36 / 38** | yes: "all 12 per-checkpoint rows reproduce exactly" (TB72:L77); claim-audit "solid" (CA:L69) | TB72:L53–L54, L83–L86, L100 |
| SN-cap12 T1 r8 (s0–s2) | solved, re-read | textbook72 | k 256, seed 0, batch 2,048 | Lean | 36 / 40 / 36 | yes | CM:L83 "36 / 40 / 36 → 37.33 (re-read)" |
| SN-cap12 frozen (s0–s3) | solved; IQM 27.5 | textbook72 | k 256, batch 4,096 | Lean | 26 / 29 / 32 / 26 | yes | TB72:L87–L90, L101 |
| SN-cap12 | RL gain T1 − frozen, paired: mean +9.0 (sd 3.56, t 5.06, df 3, p ≈ 0.015) | textbook72 | | Lean | +11 / +9 / +4 / +12 | yes | TB72:L105–L107 |
| SN-cap12 T1 / frozen | solved | dev1108 (k 64); holdout250 (k 256) | seed 0 | Lean | T1 dev 927 / 972 / 961 / 940, h250 217 / 221 / 223 / 219; frozen dev 745 / 782 / 804 / 781, h250 183 / 188 / 198 / 185 | yes | BS:L95–L96 |
| SN-cap12 T1 | Q (380) | Q | k 256; `max_steps` 48 / re-read at 96 | Lean | 233 / 295 / 320 / 317; re-read 227 / 293 / 317 | yes | SC12:L72; CM:L86 |
| SN-v2 cap 6 T1 / frozen (s0–s1) | solved | tb72 / dev / h250 / Q | as above | Lean | T1 22 / 16; 746 / 663; 169 / 151; 102 / 28. Frozen 16 / 14; 405 / 329; 103 / 83; 3 / 0 | yes | BS:L94–L97; TB72:L91–L94 |
| cm12 T1 r8 (k 64 ladder) | solved | tb72 / dev / h250 / Q / long2; greedy | best-state settings | Lean | 36 / 36 / 36; 934 / 995 / 972; 220 / 224 / 225; 232 / 295 / 320; 11 / 11 / 15; .9642 / .9768 / .9758 | yes ("Lean-recounted by the reviewer") | CM:L78–L89 |
| whole-proof C0 cap 6 (frozen / T1) | solved | tb72 / dev / h250 | k 256 / 64 / 256, seed 0, batch 2,048, `max_new` 512 | Lean (read) | frozen 12 / 11; 54 / 36; 15 / 8. T1 15 / 13; 417 / 465; 104 / 102 | yes (atlas reviewed copy) | ATLH:L26–L31; ATL:L139–L140, L194 |
| whole-proof K12 cap 12 (frozen / T1) | solved | tb72 / dev / h250 | same | Lean | frozen 21 / 21; 415 / 384; 115 / 104. T1 25 / 22; 797 / 771; 181 / 177 | yes | ATLH:L32–L37; ATL:L141–L142 |
| whole-proof K12 T1 | Q (380) | k 256 | Lean | 79 / 72 | yes | SC12:L74 |

### 3.7 Experiment-level outcomes (create vs elicit, search, compute)

| outcome | numbers | reviewed? | citation: quote |
|---|---|---|---|
| **best-state**: best − ours after the same T1 ladder (rliable IQM) | textbook72 cap 6 T1 **+18.3** (MDD 9.3), cap 12 T1 **+14.2** (MDD 6.5); frozen +4.0 / +1.2; dev +146.7 / +292.2 / −18.2 / +103.8 (MDD 88 / 61) | yes ("counts and the headline comparison stand") | BS:L104–L107; BS:L112–L114; BS:L8–L9 |
| best-state compute caveat | "each best ladder used about 2× our GPU-seconds"; same class (A40) **1.6–1.9×** | yes | BS:L128–L133 |
| **compute-match**: best12 − cm12 at 1.02× ladder A40-s | textbook72 **+15.67** [15, 16]; dev **+87.3** [60.3, 119.3]; cm12 − SN12 paired textbook72 −1.33 (0 / −4 / 0), dev +13.7 (+7 / +23 / +11) | yes ("every number reproduces; the falsifier is not met") | CM:L93–L95; CM:L9–L10 |
| compute-match reviewer wording | "giving our ladder best12's GPU time, as twice the samples per round, does not close the gap" | yes | CM:L13–L15 |
| **MCTS-a**: PUCT + value vs k 256 sampling on group C at r8, matched wall clock | value 2 / 2 / 3 vs sample 4 / 2 / 4, Δ = −2 / 0 / −1, **GATE FAIL**; 10× read value 9 / 5 / 7 vs sample 10 / 7 / 5; pend rrQ100 value − sample +19 / +10 / +14 | yes | MA:L79; MA:L90; MA:L96–L97; MA:L101 |
| **MCTS-b** | not run (gate failed) | yes | MB:L41–L47 |
| **capability-defs** (r8, x0, of 322) | equal-k "created" 54 / 51 / 60 → compute-matched at K_eval-set **22 / 21 / 14** → net of replay-only 20 / 14 / 8 → never solved by any seed's base 4 / 5 / 5; Δ_cov +21 / +16 / +12 (r16 +24 / +32 / +14); RL-free controls replay-only 239 / 244 / 249, J7 220 / 215 / 219 vs r8 286 / 286 / 293 | yes ("central measurement ... stand") | CD:L117–L125; CD:L11–L12 |
| capability-defs certification and LEM | 7 of 9 (theorem, seed) pairs certified; LEM "teachable, not latent" (A4 36 / 33 / 36 of 39) | yes | CD:L170; CD:L256; CD:L261–L263 |
| capability-defs budget caveat | "K_eval-set mixes GPU classes" (A6000 ladder seconds ÷ A40 per-attempt cost) | yes (reviewer's addition) | CD:L70–L71 |
| **create-or-elicit** primary (pre-registered) | 6 / 6 full vs 0 / 6 knockout seeds with ≥ 1 family at the bar at r16, Boschloo **p = 0.00024**, "needs exposure" | yes ("stand") | COE:L221–L223; COE:L12–L13 |
| create-or-elicit RL-phase (exploratory) | families acquired during RL: full 5 / 6 vs knockout 0 / 6, **p = 0.0032** | yes (p corrected from 0.0020) | COE:L241–L242 |
| create-or-elicit strict members at r16 | full 42 / 75 / 77 / 65 / 23 / 33 vs knockout 0 / 2 / 1 / 0 / 0 / 2 (MW p = 0.0011); dose1 58 / 39 / 30 (3 / 3 vs 0 / 6, p = 0.0033, exploratory) | yes | COE:L232–L233; COE:L262–L266 |
| create-or-elicit restated budgets (old full s0–s2 at r8) | compute-matched set 34 / 33 / 33 (K_att) … 22 / 21 / 14 (published K) … 21 / 20 / 14 (K_adapt); 21 / 20 / 14 are compute-matched at all five allocations | yes | COE:L419–L428 |
| **paper** abstract | "0/6 against 6/6 full-exposure seeds, a pre-registered contrast ($p=0.00024$)"; "5/6 against 0/6 ... ($p=0.0032$; not pre-registered)"; "51--60 theorems look RL-created at equal sample counts and 14--34 at RL's compute as base attempts (14--21 under all five allocations)" | review run: "No headline number is wrong" (COEP:L13–L14) | P-ABS:L6–L14 |
| paper on GRPO | "from full-exposure bases, plain GRPO proved fewer theorems than EI, which alone replayed pretraining data" | review run | P-LIM:L19–L21 |

### 3.8 Our models scored by others, as recorded on our side

| value | protocol | reviewed? | citation: quote |
|---|---|---|---|
| Charles's own score of our **best-state r8**: candidate_v0 ≈ 75 / 104; candidate_v1 ≈ 50 / 80; batch3 10–12 / 21; hand-proved 0 / 14 | **k 32, T 1.0, `nd_verify`** ("his protocol"); older release with 104 / 80 / 21 problems | no (proposal text, "about") | P23:L30–L34 "at k 32, T 1.0, with `nd_verify` (his protocol)" |
| Robbie's combined model (context in our summaries): textbook72 32 / 30 / 32, dev 904 | his whole-proof `lean_seq` pipeline, Lean ∧ `nd_verify` | read from his `passk.csv` by our reviewer (TB72) | BS:L148–L150; TB72:L125; SEO:L51–L52; ATLH:L47–L48 |

---

## 4. GRPO vs EI on our side

### 4.1 grpo-best (2026-10-02; 9.56 M best-cap12, proof state, Lean alone; same base checkpoints; equal sampled attempts)

Setup: EI = `trajectory`'s T1 ladder (inherited; replays 20,000 K12 records per round, "which favours EI on retention");
GRPO = G 8, 561 updates, 1,792,168 attempts vs EI's 1,793,960, no KL, no replay (GB:L38–L48). Groups are defined on
EI's x0 draw: A / B / C = 232 / 54 / 36, 236 / 51 / 35, 234 / 60 / 28 (GB:L58–L63). Pre-registered MDD from EI's
between-seed sd: 3.5 for C solved, 9.3 for all-322 solved (GB:L65).

| arm | group C solved at r8 (k 256, x1) s0 / s1 / s2 (IQM) | Δ vs EI | all 322 solved at r8 (x1) | arm-only vs EI-only (pooled), sign test | dev1108 mean (k 64) | citation |
|---|---|---|---|---|---|---|
| EI r8 | 3 / 1 / 1 (1.67) | — | 288 / 284 / 290 | — | 1,053 | GB:L96, L117, L123–L124 |
| GRPO-default r8 | 2 / 9 / 3 (4.67) | +3.0, inside the MDD | 278 / 278 / 279 | 15 vs **38**, p **0.0022**, favours EI | 1,026 | GB:L97, L118, L123–L124 |
| GRPO-unlikely r8 | 3 / 8 / 4 (5.00) | +3.3, inside the MDD | 277 / 277 / 279 | 15 vs **44**, p **0.0002**, favours EI | 1,027 | GB:L98, L119, L123–L124 |
| GRPO-pass@4 r8 | **6 / 19 / 3** (9.33 [3, 19]) | +7.7, outside the MDD | 286 / 301 / 285 | 33 vs 20, p 0.098, not resolved (s1 20 vs 4; s2 4 vs 10) | 1,058 | GB:L99, L120, L125 |
| GRPO-distinct r4 (partial arm) | 2 / 2 / 3 (2.33) vs EI r4 3 / 1 / 3 | — | — | — | — | GB:L100 |

Per k (sample seed 1, IQM over seeds; pass@1 = mean n_ok / 256, pass@256 = fraction solved) (GB:L127–L133):

| group | EI r8 | default r8 | unlikely r8 | pass@4 r8 | distinct r4 |
|---|---|---|---|---|---|
| A pass@1 / pass@256 | .851 / .994 | .893 / .979 | .892 / .980 | .830 / .996 | .806 / .980 |
| B pass@1 / pass@256 | .564 / .964 | .542 / .811 | .547 / .788 | .460 / .881 | .331 / .710 |
| C pass@1 / pass@256 | .000 / .049 | .057 / .140 | .050 / .152 | .091 / **.272** | .004 / .073 |

Other per-arm facts:
- **Robustness to the draw:** on x0 the C′ means are EI 2.0, default 5.7, unlikely 4.7, pass@4 10.7 (GB:L108). C solved on
  either draw pooled, 17 / 16 / 33 vs EI's 5, is biased ("EI's sample seed 0 cannot solve a C theorem by construction");
  on x1 alone the totals are 14 / 15 / 28 vs 5 (GB:L109–L110).
- **Why the pass@4 excess is weak:** "the MDD assumed EI's sd (1.15), while pass@4's own sd is 8.5"; "a Welch t-test on
  the seeds gives t ≈ 1.55"; "the bootstrap interval [3, 19] touches EI's maximum" (GB:L102–L106).
- **Retention:** held-out greedy at r8 is 0.98–0.99 for every arm, EI included (GB:L141). Targets solved at r8: default
  4,323–4,344, pass@4 4,371–4,411 (GB:L153), against EI's 4,383 / 4,365 / 4,407 (TJ:L58).
- **Compute:** GRPO used 1.00–1.13× EI's GPU-seconds and 0.17–0.37× its train tokens; GPU-seconds are co-tenant
  wall-clock, two ladders per card (GB:L192–L203). "Compute is not matched" (GB:L240–L241).
- **Pre-registered story condition not met:** "an arm beats EI on C beyond the MDD *and* on the sign test at p < 0.05 |
  **not met**" (GB:L218).
- **The summary's conclusion:** "plain GRPO does not reach more theorems than EI. It reaches different ones, while EI
  keeps more overall (EI also replays K12)"; pass@4 "is the only candidate for "RL reaching theorems EI could not". At
  n = 3, with one outlier seed, that is not resolved" (GB:L220–L223). Reviewer: "GRPO reaches theorems that EI does not" is
  **not supported as worded** as an unqualified headline for all three arms (GB:L10–L11). Reviewed: "Every
  pre-registered count reproduces on the reviewer's independent code" (GB:L8–L9).

### 4.2 grpo-state (2026-09-30; 3.2 M SN-cap12 Stage-1 s0)

Code phase only: "no claim about GRPO is made, and the smoke numbers below are measurements of the code (≤ 8 updates),
not results" (GS:L9–L11).

### 4.3 Older GRPO vs EI (3.2 M, ND token format, cap 6 depth-3 f = 0, judged by `nd_verify`, before 2026-09-27)

- **round2-run4** (2026-09-18, reviewed). Equal budget, 256,000 samples per arm, six Stage-1 draws, 1,000 targets.
  Per draw, solved ratio G8 / EI 1.17–1.34 and G32 / EI 1.11–1.25 (R2R4:L124–L131). Depth-3 acquisition means: "G = 8
  0.474 (0.447–0.505), G = 32 0.426 (0.395–0.467), EI 0.351 (0.335–0.364)" (R2R4:L134–L135). Cost: held-out greedy
  "0.34–0.67 vs 0.90–0.95" (R2R4:L208–L212). Reviewer: the draws are rare-prior, not zero-prior (R2R4:L216–L224).
- **run4-grpo-review** (2026-09-28, review of a salvaged replication; checkpoints lost). GRPO "ignites in **40 of 40 arms
  with surviving data**", "**12 of 12 on the zero-rate draws**"; paired EI "ignites in **6 of 8** arms on s22–s25, or **7
  of 10**", and "in **1 of 3** arms" on the zero-rate draws (R4GR:L97–L108). Counts are "`nd_verify`-counted,
  Lean-confirmed" (R4GR:L46–L52).
- The atlas's one-line reading of these: "GRPO > EI on depth 3 (token)" (ATL:L100).

---

## 5. Noise-floor / MDD statements that apply to textbook72 counts

`NOISE_FLOOR.md` (fork) has no textbook72 row. CAD:L121–L122: "`NOISE_FLOOR.md` has no row for the state models,
textbook72 or long pools, so the MDDs here come from observed seed spread." The noise-floor run itself measured only
the 3.2 M C0 `lean_seq` cap-6 configuration (NF:L52–L58; floor table NF:L104–L114), with no textbook72 quantity.

| statement | design | applies to | citation: quote |
|---|---|---|---|
| textbook72 MDD **9.3 (cap 6) / 6.5 (cap 12)** | pre-registered; pooled per-seed SDs, two-sample t, 80 % power; 3 vs 2 (cap 6), 3 vs 4 (cap 12) | best vs ours, T1 and frozen | BS:L101–L102 "pre-registered MDD from pooled per-seed SDs, two-sample t, 80 % power"; BS:L106 "9.3 / 6.5" |
| interaction MDD ≈ 12 | pre-registered | cap-12 advantage best vs ours | BS:L125–L126 "inside the interaction MDD (≈ 12)" |
| cap-12 MDD 6.5 reused; **≈ 6.9 at 3 vs 3** (reviewer) | n = 3 per arm | best12 vs cm12 vs SN12 | CM:L68–L69 "The pre-registered MDDs are 6.5 (textbook72) and 61 (dev) ... The reviewer computes ≈ 6.9 and 65 at 3 vs 3" |
| paired RL-gain MDD **≈ 8** pre-registered; **≈ 7.4** at the observed sd, n = 4 paired | SN-cap12 T1 − frozen | 3.2 M SN-cap12 | TB72:L105–L107 "The pre-registered MDD was ≈ 8; at the observed sd the n = 4 paired MDD is ≈ 7.4" |
| MDD at n = 3 **≈ 7** textbook72 (≈ 5 holdout250) | n = 3, early-start ladders vs end arm | best-cap12 trajectory seeds | RFC:L149 "The MDD at n = 3 is ≈ 7 textbook72 and ≈ 5 holdout250" |
| **MDD ≈ 7.8** tb72 | n = 3, claim C6 | rl-from-ckpt "level" | CA:L72 "(MDD ≈ 7.8 tb72)" |
| frozen cap 12 "level" **+0.4, MDD 7.7** | observed spread | best vs ours frozen, cap 12 | CAD:L35 "(+0.4, MDD 7.7)" |
| T1 margins pass "even at the larger observed-sd MDDs" | observed sd | best vs ours T1 | CAD:L116–L117 |
| "differences under ≈ 7 problems are inside the floor"; "Re-reading one checkpoint at another batch flips 6–11 of 70 textbook72 problems (sampling re-draw)" | atlas reading rule | all fork textbook72 rows | ATL:L155–L157; ATL:L240 "6–11 of 70 textbook72 problems flip"; ATL:L270–L271 |
| same checkpoint, x0 vs x1: "≤ 4 problems apart; 7 / 133 at \|z\| > 1.96 (6.6 expected); sd(z) 1.11" | 66 checkpoints × 2 draws | trajectory checkpoints | CAD:L55 |
| best-state vs trajectory (independent trainings of the same recipe): "+1.3 and −3.3; inside the spread" | fresh trainings | best12 / best6 T1 means | CAD:L56 |
| pend re-read at batch 512 within the pre-registered ±4 (34 / 30 / 34 vs 32 / 32 / 38) | same checkpoint, new batch | trajectory pend | P-CHK:L41–L43 "All three are within the pre-registered $\pm4$, seed 2 at its edge" |
| all-322 solved MDD **9.3**; group C MDD **3.5** | EI between-seed sd, n = 3 | grpo-best | GB:L65 |
| group C per-seed MDD ≈ 6–7 | at ≈ 0.1 solves per theorem | mcts-a | MA:L94; MA:L169–L170 |
| guided-tts per-seed band ≈ 4–5 pp; the executor's MDD ≈ 2.7 pp "was not independently derived" | long (90), pp not counts | guided-tts | GT:L88–L89 |
| no MDD at all for capability-defs | — | capability-defs | CD:L416 "the pre-registration states no minimum detectable difference" |

Worked spread for one checkpoint (trajectory pend s2, textbook72): 38 (x0, b2,048), 36 (x1), 36 (seed 2), 34 (x0,
b512): range 4 (TJ:L108; R16:L33; MA:L82; P-CHK:L42).

---

## 6. Inconsistencies (same model and protocol, or same label, with different values)

1. **One name, two trainings.** `state_env_october` covers best-state's seeds and trajectory's fresh seeds of the same
   recipe (SEO:L26–L28). The card's headline block uses best-state seeds (textbook72 52 / 51 / 52, SEO:L33–L34). Its
   guided table uses trajectory seeds (plain 48 / 48 / 53, SEO:L39–L43). Its "97.1–98.0 % solved by r8" (SEO:L56) matches
   trajectory's 4,365–4,407 / 4,495, not best-state's 4,375–4,392 (TJ:L58; BS:L135–L136). The two ladders also ran on
   different GPUs (A40 vs RTX A6000; BS:L77; TJ:L57). textbook72 at r8 on file: 52 / 51 / 52 (best-state, seed 0), 48 / 49
   / 54 (trajectory x0), 48 / 48 / 53 (x1), 49 / 50 / 55 (seed 2). CAD:L56 calls the best-state ↔ trajectory gap "+1.3
   ... inside the spread".
2. **Identical file names in two buckets.** `la_T1_best12_s{0,1,2}_r8.pt` and `stage1_best12_s{0,1,2}_b1200.pt` exist under
   both `best-state/ckpts/bs/` and `trajectory/ckpts/tj/` and are different models (SEO:L26–L29; GB:L36–L37). R16:L20–L21
   warns "Compare against `trajectory`'s round 8, not `best-state`'s."
3. **"Long pool L_true 13–16" is two different measurements.**
   - SEO:L37: "377 / 375 / 376 of 380" = best-state seeds, Q (generator theorems only), k 256, seed 0, batch 2,048
     (BS:L71, L97).
   - R16:L36: "pass@64 (of 400)", r8 = 377 / 362 / 367 = trajectory seeds, rr600 rows with `L_true_lb` 13–16 including
     textbook rows, k 64, x0, batch 512 (RC:L47–L53).
   - The shared "377" for s0 is a coincidence. RC:L52 says k 64 is "not comparable with `best-state`'s k 256".
4. **Same quantity, different estimator (IQM vs mean).** best − ours frozen at cap 12 on textbook72:
   - **+1.2** (best-state, IQM: 28.67 − 27.5; BS:L106);
   - **+0.5** (atlas, means 28.7 − 28.2; ATL:L75, L133, L137);
   - **+0.4** (claim-audit ledger; CAD:L35).
   T1 at cap 12: **+14.2** (BS:L106) and **+14.17 (IQM)** (CA:L68) against **+14.4** (CAD:L35; the mean difference
   51.67 − 37.25). The claim-audit summary and its own ledger thus disagree, 14.17 vs 14.4. The dev cap-12 T1 margin is
   +103.8 stated vs **+104.3** on the claim-audit's recount (CA:L57–L58).
5. **holdout250 and long2 at r8 differ by seed set and draw.** holdout250: 239 / 237 / 237 (best-state; SEO:L36) vs 240 /
   236 / 237 (trajectory x1; R16:L34) vs 238 / 237 / 239 (x0; TJ:L109) vs 239 / 236 / 239 (seed 2; MA:L83). Lengths ≥ 17:
   21 / 21 / 20 (best-state; SEO:L38) vs 21 / 20 / 20 (trajectory x0, batch 512; R16:L37) vs 21 / 19 / 19 (seed 2; MA:L87).
6. **Pretraining-only textbook72 for the trajectory seeds** has four reads on file: 32 / 32 / 38 (x0, TJ:L108), 34 / 33 / 36
   (x1, R16:L33), 32 / 32 / 36 (seed 2, MA:L82) and 34 / 30 / 34 (x0 at batch 512, P-CHK:L41–L42). best-state's own Fz
   seeds read 32 / 27 / 27 (BS:L94). The r16 card's "pretraining only" column is the x1 draw. Its `rl_targets` entry
   (3,676 / 3,705 / 3,741) is **card only**.
7. **SN-cap12 T1 textbook72**: 37 / 38 / 36 (s0–s2) at batch 4,096 (TB72:L83–L85) vs 36 / 40 / 36 when compute-match
   re-read them at batch 2,048 (CM:L83). best-state and the atlas use 37 / 38 / 36 / 38 (BS:L94; ATLH:L11). SN-cap12 Q:
   233 / 295 / 320 at `max_steps` 48 (SC12:L72) vs 227 / 293 / 317 at 96 (CM:L86). long2: 8 / 15 / 17 (BS:L98) vs 9 / 14
   / 18 (CM:L88).
8. **Atlas "maximum of 57" is superseded.** ATL:L55–L57 and STATE:L161: "The best textbook72 number on file is 57
   (best-cap12, `trajectory` seed 2 round 6)". Later plain reads include **58** (trajectory s2 r12, x1; RC:L149
   "53 / 58 / 56") and 57 (s1 r16; RC:L148). 57 also appears guided at r8 s2 (SEO:L43) and for PUCT + value at r8 s2
   (MA:L81).
9. **Stale card statements.**
   - R16:L53: "It has no guided read-out yet". capability-defs later read r16 guided: 295 / 303 / 303 of 322 (CD:L236).
   - SEO:L56 and SEO:L67–L69 still say `rl-continue` is "checking" / "(running)"; it completed 2026-10-04 (RC:L8).
   - SEO:L58: "about 30 of the 322 (`trajectory`'s group C)" are "not reached by anything". Group C is defined on the x0
     draw only (TJ:L67–L70). Other reads do reach some of it: EI r8 itself on x1 3 / 1 / 1 (GB:L96), seed 2 4 / 2 / 4
     (MA:L79), r16 6 / 17 / 4 (RC:L107) and GRPO-pass@4 6 / 19 / 3 (GB:L99).
10. **Guided numbers per set exist only in the card.** SEO:L43–L47's per-set plain / guided counts (textbook72 and
    Charles's four sets) are not in any summary. GT gives only per-seed totals over 259 (GT:L102). Those totals equal
    the card's column sums: plain 178 / 172 / 188, logical 200 / 190 / 199. GT's plain textbook72 at x1 (48 / 48 / 53,
    GT:L103) is identical per seed to trajectory's x1 files (RC:L46–L49). GT does not say whether this is the same draw
    replayed or an independent one; CAD:L61–L64 warns that same-checkpoint, same-seed reads are deterministic replays.
11. **Charles's sets have two versions.**
    - guided-tts and the card use the 2026-10-02 release: `candidate_v0` 87, `candidate_v1` 72, `batch3` 14,
      `hand_proved_14` 14 (GT:L42; P23:L16–L24).
    - Charles's own score of our best-state r8 is "about 75 / 104", "about 50 / 80" and "10–12 / 21", at k 32, T 1.0,
      `nd_verify` (P23:L30–L34).
    - The atlas lists an earlier release (2026-09-30) with `candidate_v0` (104) and `candidate_v1` (80) (ATLX:L74 "New
      textbook ND problem sets candidate_v0 (104), candidate_v1 (80), unsolved (10)").
    So denominators, k, T and checker all differ between "our" and "Charles's" numbers on the "same" sets.
12. **The paper vs capability-defs on the J7 continuation control.**
    - P-MEAS:L74–L75: "about 75--78\% of the ladder's GPU time. It proves 220/215/219, gaining 12--19 theorems and losing
      30--42".
    - CD:L292–L295: "82 / 84 / 81 % of the r8 ladders' GPU-seconds, which are **RTX A6000** seconds"; "gains 19 / 19 / 16
      ... and loses 31 / 40 / 31".
    - The share difference is presumably the A6000 → A40 conversion. The paper's P-MEAS:L9 says "the 75--78\% share ...
      were not recounted", and P-MEAS:L13–L14 gives "a measured A6000/A40 ratio of 0.932".
    - The gain / loss ranges also differ (12–19 / 30–42 vs 16–19 / 31–40), and the paper does not state their basis. Not
      resolved here.
13. **capability-defs' headline "14–22" depends on a mixed-GPU-class budget.** CD:L67–L71 flags it. COE:L419–L428 restates
    same-class budgets: 28 / 26 / 24 at uniform same-class K_eval-set, against 22 / 21 / 14 as published. The paper
    abstract uses "14--34 ... (14--21 under all five allocations)" (P-ABS:L13–L14). These are consistent, but a single
    "created" count needs its allocation named.
14. **The "textbook" label is not always textbook72.** state-env's "textbook / 760" is 760 generated schema instances
    (SE:L73; TB72:L13). state-cap12's "textbook solved (of **73**)" counts textbook theorems inside rr600 (SC12:L94,
    L100–L102). Neither is textbook72.
15. **Same MDD number, different quantities.** grpo-best's MDD 9.3 is for all 322 solved (GB:L65); best-state's 9.3 is the
    cap-6 textbook72 MDD (BS:L106).
16. **Judge and date caveats inside the 3.2 M whole-proof rows.** The C0 T1 ladder was trained under Lean ∧ `nd_verify`
    on 2026-09-24 and only re-read under Lean alone (SC12:L41; SE:L41–L44). The atlas labels these rows Lean (ATLH:L29–L31).
17. **Robbie-recipe naming.** Our port is "Robbie's autoresearch incumbent 186" (SEO:L16), the same 186 recipe as the
    factorial's "best" cell (MAP:L82 "{012 naive 4x256, 186 best 6x384}"). The atlas's "cleanest fork ↔ Robbie overlap"
    is his recipe **198** state SN (dev 852 / 824 / 798; ATLH:L50; ATL:L160), a different recipe. Also, Robbie's
    factorial cells "were RL-trained on 14 of the 72 textbook72 theorems" (ATL:L61–L62); the card's comparison line
    (SEO:L51–L52) does not say so.
