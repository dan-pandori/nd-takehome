# Evidence atlas (2026-10-02) and our creation tests: notes for peer-rl-review

Written 2026-10-17 by a read-only research subagent. Everything was read from `~/nd-rl` at `origin/dan` using only
`git show`, `git grep` and `git ls-tree`. No checkout, fetch or write was made in `~/nd-rl`.

**Citation convention.** `ALIAS/file:Lnn` expands to `origin/dan:<path>:Lnn`. Line numbers are the line numbers of
`git show origin/dan:<path> | cat -n`. For CSVs, L1 is the header (no CSV here has multi-line fields: 95 rows + header
= 96 lines in `experiment_map.csv`). Numbers are quoted as written. **derived** marks anything I computed.

**Five things to know first.**
1. The atlas's harmonised table puts every family on the same three pools: textbook72 at k 256, dev1108 at k 64 and
   holdout250 at k 256, all at T 0.8. It rates **every fork ↔ Robbie comparison only "partly" apples to apples**, and
   Leon's and Charles's textbook numbers **"no"** (EA/ATLAS.md:L229-240).
2. "best 9.56M" rows (51.7/72 etc.) are **our port** of Robbie's recipe to the proof-state format, not Robbie's runs
   (EA/ATLAS.md:L40). Robbie's own best cell is 32/30/32 † (EA/ATLAS.md:L146).
3. The whole-proof re-score: proof state beats whole proof in 8/8 dev/holdout cells at the same 3.2M recipe
   (EA/README.md:L74-79). Our whole-proof C0 T1 beats Robbie's naive whole-proof EI cells a fortiori (EA/README.md:L80-83).
4. Our creation tests: at equal k, RL "creates" 51–60 theorems per seed. With RL's compute given to the base as
   attempts, 14–22 remain (4–5 that no seed's base ever solved). RL stays ahead at set level (CD:L117-127). The σ
   knockout gives 0/6 vs 6/6 seeds, p = 0.00024, "largely present before RL" (PAPER/sections/00_abstract.tex:L6-8).
5. Almost every other-member row in the atlas is **unreviewed** (U), with numbers copied from their branches. The
   claim-audit audited **only our claims**. The atlas did not count its own "mixed checkers / k" expectation
   (EA/README.md:L109-110).

---

## 1. Files read

| alias | origin/dan path | how read |
|---|---|---|
| EA | `experiment-summaries/2026-10-02-evidence-atlas-map-of-95-experiments-whole-proof-rescore/` | `README.md` (132 lines) and `ATLAS.md` (284) in full; `MAP.md` (153): header plus every Robbie/Leon/Charles/Dmitry/chainik1125 row and the Dmitry-era imports; `data/headline_table.csv`, `protocol_differences.csv`, `create_vs_elicit.csv`, `truncation_check.csv`, `compute_rescore.csv` in full; `data/experiment_map.csv` parsed for owner, review status and protocol fields. Figures (PNG) not viewed |
| CD | `experiment-summaries/2026-10-05-capability-defs-compute-matched-budget-shrinks-equal-k-creations-rl-still-ahead-lem-teachable/README.md` | in full (452 lines) |
| COE | `experiment-summaries/2026-10-12-create-or-elicit-sigma-knockout-not-acquired-in-16-ei-rounds-needs-exposure-1pct-dose-restores/README.md` | in full (691) |
| COEP | `experiment-summaries/2026-10-13-create-or-elicit-paper-draft-and-blog-no-headline-number-wrong-c4-drops-knockout-s1-elicitation-reading/README.md` | in full (543) |
| PC | `experiment-summaries/2026-10-14-paper-clean-clean-paper-and-blog-equivalent-to-reviewed-copy-12-of-13-possible-errors-fixed/README.md` | L1-90 in full, rest skimmed by heading (312) |
| PAPER | `docs/papers/create-or-elicit/` | `README.md` in full (116); `sections/00_abstract.tex` in full; `blog.md` L1-118 and L140-195; `next_steps.md` structure plus items 1 and 10 |
| CA | `experiment-summaries/2026-10-02-claim-audit-headline-counts-reproduce-three-claims-weaker-than-stated/README.md` | in full (102) |
| CAR | `docs/project_strategy/2026-10-03-claim-audit.md` (claim-audit reading copy) | rating table L28-40 |
| STATE | `docs/STATE.md` | grep for the mentee names and for thinking / GRPO v2 / retry / TTRL / selection / distract; read L145, 147, 155, 161, 167, 169, 173 in full |
| GT | `experiment-summaries/2026-10-03-guided-tts-logical-redraws-beat-plain-on-long-theorems-structural-redraws-do-not/README.md` | L42-43, L74-92, L130-142 (method evidence) |
| NF | `experiment-summaries/2026-09-25-noise-floor-measurement-floor/README.md` | L1-12, L96-122 (method evidence) |
| CM | `experiment-summaries/2026-10-02-compute-match-matched-ladder-gpu-time-does-not-close-gap/README.md` | grep: L68, L93, L99-101 |
| BS | `experiment-summaries/2026-09-30-best-state-robbies-recipe-wins-after-rl-level-frozen-at-cap12/README.md` | grep: L106, L113, L132 |

**Not found:** `docs/WHERE_THINGS_ARE.md` does not exist on `origin/dan` (`git show` returns "path … does not exist in
'origin/dan'"). The atlas cites it on nd-rl `main` (EA/MAP.md:L153).

**STATE.md and other mentees after 2026-09-25.** The only mentee mentions in STATE.md are:
- Dmitry, about a 2026-09-17 idea (STATE:L27);
- Robbie, inside our own entries: textbook72 (L145), best-state (L147), compute-match (L155), evidence-atlas (L161)
  and grpo-best (L167).

There are no hits for Leon or Charles. The keywords thinking, GRPO v2, TTRL and distract do not appear. "retry"
appears only at L52, about our own r3-run4b schedule retry. "selection" appears only about our own runs (L16, 87, 107,
139, 149, 153, 165). In the atlas the only one of these
topics is Robbie's TTRL (EA/MAP.md:L84-85; EA/data/create_vs_elicit.csv:L12; EA/data/protocol_differences.csv:L9).
**So none of the mentees' newer topics (thinking, GRPO v2, retry, distractors) is covered on origin/dan.**

---

## 2. The atlas's harmonised tables, comparability verdicts and the whole-proof re-score

### 2.1 Scope and how it was built

- **Status.** Completed and reviewed 2026-10-02; nothing quarantined. "The deliverable is a **map for Dan**, not a
  test of a hypothesis". Its one new measurement is the pre-registered whole-proof re-score (EA/README.md:L8-12).
- **Size.** 95 experiments: "81 by Dan's agents and the earlier Codex sprints … and 14 by other members (Robbie, Leon,
  Charles, Dmitry, read-only from their nd-rl branches)" (EA/ATLAS.md:L15-16). This conflicts with the CSV; see §7.
- **Recomputation.** Shared-pool numbers were recomputed from per-theorem files (EA/README.md:L30-34):
  - 243 fork read-outs;
  - Robbie's factorial `passk.csv`;
  - the long-pool per-stratum files (878 rows).

  There were "0 disagreements with the summaries". Every other number is marked `copied`.
- **Robbie's dev values are copied.** "Robbie's dev values are copied from his tables; holdout250 is recomputed from
  his `passk.csv`" (EA/ATLAS.md:L126-127).
- **Labels** (EA/ATLAS.md:L35-41):
  - "Lean" = Lean alone (from 2026-09-27); † = Lean ∧ `nd_verify`; ‡ = `nd_verify` alone;
  - "state" = `lean_staten`; "whole proof" = `lean_seq`;
  - **"best" = Robbie's 9.56M recipe ported to the state format (`best-state`)**, a fork (Dan) run;
  - "ours" = the 3.2M 4 × 256 recipe.

  All models are from scratch. Training sets are the cap-6 control set (depth3 f0 a1, 155k) or K12 (155k) unless
  stated (EA/ATLAS.md:L43).
- **Shared pools.** All textbook72 files across members are byte-identical (Robbie's, Dmitry's, Charles's, the
  fork's; md5 `b7397660…`). Robbie's dev1108 and holdout250 are the fork's sets. Every read on these pools is T 0.8,
  with k 256 for textbook72 and holdout250 and k 64 for dev (EA/ATLAS.md:L49-52).
- **Checker effect.** Lean vs Lean ∧ `nd_verify` "changes counts by ≤ 0.02 % (lean-judge) to a few theorems
  (state-env), so it is a labelled difference, not a blocker" (EA/ATLAS.md:L53-54). The measured Lean-only excess is
  0.021 %, and C0 counts move "+2 / +1 (T1), +7 / +2 (frozen)" (EA/ATLAS.md:L236).
- **The forward-citation bug.** The fork's `nd_verify` still has it (EA/ATLAS.md:L36-37). 14 of 23 create-vs-elicit
  rows were judged by `nd_verify` alone, and none of the 14 has been scanned for it (EA/ATLAS.md:L89-90).

### 2.2 Harmonised shared-pool table

Source: EA/ATLAS.md:L129-149, with per-seed values also in EA/data/headline_table.csv:L2-63. Each cell is per seed →
mean.

| # | family (whose run) | model / format | training data | RL | judge | seeds | textbook72 /72 (k 256) | dev1108 /1108 (k 64) | holdout250 /250 (k 256) | src |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ours state cap 6, frozen (Dan) | 3.2M 4×256, `lean_staten` (SN-v2) | cap-6 155k | — | Lean | 2 | 16 / 14 → 15.0 | 405 / 329 → 367 | 103 / 83 → 93 | L131 |
| 2 | ours state cap 6, T1 (Dan) | same | same | T1 ladder (r8) | Lean | 2 | 22 / 16 → 19.0 | 746 / 663 → 704.5 | 169 / 151 → 160 | L132 |
| 3 | ours state cap 12, frozen (Dan) | 3.2M `lean_staten` (SN-cap12) | K12 155k | — | Lean | 4 | 26 / 29 / 32 / 26 → 28.2 | 745 / 782 / 804 / 781 → 778 | 183 / 188 / 198 / 185 → 188.5 | L133 |
| 4 | ours state cap 12, T1 (Dan) | same | same | T1 ladder | Lean | 4 | 37 / 38 / 36 / 38 → 37.2 | 927 / 972 / 961 / 940 → 950 | 217 / 221 / 223 / 219 → 220 | L134 |
| 5 | best 9.56M state cap 6, frozen (Dan's port of Robbie's recipe) | 9.56M `lean_staten` | cap-6 | — | Lean | 3 | 19 / 18 / 20 → 19.0 | 569 / 466 / 506 → 513.7 | 149 / 125 / 122 → 132 | L135 |
| 6 | best cap 6, T1 (Dan) | same | same | T1 ladder | Lean | 3 | 39 / 40 / 33 → 37.3 | 1002 / 986 / 1002 → 996.7 | 226 / 229 / 227 → 227.3 | L136 |
| 7 | best cap 12, frozen (Dan) | same | K12 | — | Lean | 3 | 32 / 27 / 27 → 28.7 | 782 / 767 / 741 → 763.3 | 184 / 195 / 182 → 187 | L137 |
| 8 | best cap 12, T1 (Dan) | same | K12 | T1 ladder | Lean | 3 | 52 / 51 / 52 → 51.7 | 1058 / 1050 / 1055 → 1054.3 | 239 / 237 / 237 → 237.7 | L138 |
| 9 | ours whole proof cap 6, frozen (re-score, Dan) | 3,214,336 params, `lean_seq` | C0 cap-6 | — | Lean | 2 | 12 / 11 → 11.5 | 54 / 36 → 45 | 15 / 8 → 11.5 | L139 |
| 10 | ours whole proof cap 6, T1 (re-score) | same | same | T1 ladder | Lean | 2 | 15 / 13 → 14.0 | 417 / 465 → 441 | 104 / 102 → 103 | L140 |
| 11 | ours whole proof cap 12, frozen (re-score) | same | K12 | — | Lean | 2 | 21 / 21 → 21.0 | 415 / 384 → 399.5 | 115 / 104 → 109.5 | L141 |
| 12 | ours whole proof cap 12, T1 (re-score) | same | K12 | T1 ladder | Lean | 2 | 25 / 22 → 23.5 | 797 / 771 → 784 | 181 / 177 → 179 | L142 |
| 13 | **Robbie** naive pretrain, Lean, plain EI | naive "012" 4×256 (size not recorded), `lean_seq` whole proof | cap-6 155k | harness EI, 2,400 s pipeline | † | 3 | 8 / 6 / 10 → 8.0 | 209 / 195 / 174 → 192.7 | 45 / 42 / 37 → 41.3 | L143 |
| 14 | **Robbie** naive, Lean, Leon RL + guided | same | same | Leon RL + verifier-guided sampling ("rl-leon-c005") | † | 3 | 12 / 10 / 9 → 10.3 | 434 / 420 / 387 → 413.7 | 107 / 102 / 99 → 102.7 | L144 |
| 15 | **Robbie** best 9.56M, Lean, plain EI | "186" 6×384 9.56M, `lean_seq` | cap-6 | harness EI | † | 3 | 19 / 21 / 20 → 20.0 | 694 / 677 / 674 → 681.7 | 155 / 161 / 147 → 154.3 | L145 |
| 16 | **Robbie** best 9.56M, Lean, Leon RL + guided | same | cap-6 | Leon RL + guided | † | 3 | 32 / 30 / 32 → 31.3 | 916 / 895 / 901 → 904 | 210 / 200 / 205 → 205 | L146 |
| 17 | **Robbie** recipe 198, state SN, plain EI | ~9.56M `lean_staten` | cap-6 155k | harness EI 4 rounds | Lean | 3 | — | 852 / 824 / 798 → 824.7 | — | L147 |
| 18 | **Robbie** recipe 198, whole proof C0, plain EI | ~9.56M `lean_seq` | cap-6 | harness EI 4 rounds | Lean | 3 | — | 669 / 692 / 216 → 525.7 | — | L148 |
| 19 | **Robbie** naive / best, token, EI / Leon (4 cells) | abs token format | cap-6 | EI / Leon RL + guided | ‡ | 3 each | 9.0 / 12.0 / 17.0 / 25.0 | 142 / 444 / 457 / 782 | 35 / 108 / 121 / 177 | L149 |

Where each protocol detail comes from:
- **Fork state reads:** `max_steps` 96, `max_action` 512, batch 4,096 (EA/ATLAS.md:L71-72, L152-154;
  EA/README.md:L77-78).
- **Whole-proof re-score reads:** `max_new` 512, batch 2,048, sample seed 0 (EA/ATLAS.md:L194).
- **Robbie's factorial** (EA/data/protocol_differences.csv:L8; EA/data/experiment_map.csv:L55):
  - "2,400 s single-GPU budget per pipeline; only after-RL reads in git (passk.csv)";
  - naive "4x256 (size not stated; fork 3.2M class)", best 9.56M;
  - "dev1108 pass@64 T0.8; holdout250 & textbook72 256 samples T0.8 (unbiased pass@k); 3 seeds";
  - data: cap-6 155k (fork 51604b3).
- **Robbie's state recipes:** "dev1108 pass@64 T0.8, harness EI 4 rounds; 3 seeds" (EA/data/experiment_map.csv:L36).
- **textbook72 is not held out for Robbie's factorial.** "Robbie's factorial cells were RL-trained on 14 of the 72
  textbook72 theorems (`split = train` in `passk.csv`), so these counts are not held-out on those 14"
  (EA/ATLAS.md:L61-63).
- **No frozen reads.** "Robbie's factorial has no frozen reads in git" (EA/ATLAS.md:L121-122).
- **Token cells (row 19).** The CSV means are 142.33 / 443.67 / 456.67 / 782.33 (dev) and 35.0 / 108.33 / 120.67 /
  177.33 (holdout250) (EA/data/headline_table.csv:L52-63).

The atlas's reading notes (EA/ATLAS.md:L151-161):
- Fork rows within one pool are apples to apples except for the decode cap.
- "Re-reading one checkpoint at another batch flips 6–11 of 70 textbook72 problems (sampling re-draw). The
  best-state MDDs for textbook72 are 9.3 (cap 6) and 6.5 (cap 12) at these seed counts, so differences under ≈ 7
  problems are inside the floor."
- Against Robbie's lean cells, "the checker differs († vs Lean; near-equivalent) and so does training: his pipelines
  run for 2,400 s, ours for the T1 ladder."
- "The cleanest fork ↔ Robbie overlap is dev1108 for recipe 198 state SN vs best-cap6 state: same checker and
  interface. Even there, the RL differs (plain EI in his harness vs our T1 ladder)."
  - *derived:* best-cap6 T1 996.7 − Robbie 198-SN plain EI 824.7 = **+172.0 dev**. Our best-cap6 frozen is 513.7.
    The atlas does not state this difference.

The atlas's headline numbers on the table (EA/ATLAS.md:L46-90):
- **Top textbook72 family.** It is best-9.56M state cap 12 after T1: round-8 reads 51–53 in best-state and 48–54 in
  `trajectory`'s re-run, with a **maximum of 57** (`trajectory` `la_T1_best12_s2_r6`, seed 2, round 6)
  (EA/ATLAS.md:L55-59).
  - Cap-12 counts include one `train_k12` theorem (disjunctive syllogism with its premises swapped), ≤ 1 per count
    (EA/ATLAS.md:L58-59; EA/README.md:L106-108).
  - "No Robbie factorial cell exceeds 32" (EA/README.md:L99).
- **Robbie's best cell vs our best-state.** Robbie's best factorial cell solves 32/30/32 †; best-state cap 6 solves
  39/40/33. "That gap mixes interface and RL algorithm, and the runs are not compute-matched" (EA/ATLAS.md:L60-65).
- **Interface** is "the largest single factor we can now isolate" (EA/ATLAS.md:L66-73); see §2.5.
- **Recipe and size.** "Pretraining recipe and size (9.56M vs 3.2M) matter more after RL than before" (EA/ATLAS.md:L74-78):
  - frozen best − ours on textbook72: +4.0 (cap 6), +0.5 (cap 12), inside the MDD;
  - after T1: +18 and +14;
  - "Robbie's factorial finds the same ordering in whole-proof format: pretraining +408 dev, RL +268, format +92.
    These are main effects, unreviewed."
- **Length extension.** "RL's clearest effect is length extension from a reachable base" (EA/ATLAS.md:L79-82):
  - on rr600 13–16-line theorems, best-9.56M cap 6 goes 2 % → 87 % after T1 (3 seeds);
  - ours state cap 6 goes 0 % → 16 %; ours whole proof cap 6 goes 0 % → 1 %;
  - cap-12 pretraining alone gives 49 % (state) and 10 % (whole proof).

### 2.3 Comparability verdicts

Source: EA/ATLAS.md:L225-240 (verbatim apart from formatting).

| comparison | apples to apples? | why |
|---|---|---|
| fork families on textbook72 / dev / holdout250 | **yes**, with a decode-cap note | Lean, T 0.8, same k and pool; state `max_steps` 96 vs whole-proof `max_new` 512 |
| fork state vs Robbie factorial lean cells | **partly** | same pools, k, T; † vs Lean; interface, RL and compute differ |
| fork whole proof (this run) vs Robbie naive lean cells | **partly** | same format, pools, k, T; † vs Lean; T1 ladder vs 2,400 s EI; his model size not recorded; on textbook72 his cells RL-trained on 14 / 72 |
| Robbie autoresearch dev scores across eras | **no** | token-era ‡ vs Lean-era †; ±10 seed noise at the start (000 vs 001) |
| Leon textbook dev58 / Charles textbook72 vs fork textbook72 | **no** | k 32–4,096; T 1.0 (Charles); `strict_verify` / nd_v2; 3.2M token models |
| any number before vs after 2026-09-27 | **yes, if labelled** | measured Lean-only excess 0.021 %; C0 counts +2 / +1 (T1), +7 / +2 (frozen) |
| `nd_verify`-only counts (token era) vs Lean | **not checked** | the fork's `nd_verify` accepts forward box citations (Leon's fix); never scanned outside run4-grpo-review (13,317 / 13,317 Lean-confirmed) |
| L\* on transfer2285 vs rr600 / long2 | **no** | transfer2285 censored at 14; rr600 + ge17 censors cap-12 state at ≥ 17 |
| long-pool reads at `max_steps` 48 vs 96 | **counts yes, lengths no** | rr600 totals move −10 to +5; longest proof capped near 48 lines |
| same checkpoint, batch 2,048 vs 4,096 | **re-draw** | 6–11 of 70 textbook72 problems flip; quote `NOISE_FLOOR.md` |

Further caveats from the README (EA/README.md:L117-120):
- Fork ↔ Robbie textbook72 comparisons are only **partly** apples to apples. His cells trained on 14 / 72, use a
  different checker, have an unrecorded model size, and ran a 2,400 s pipeline against our T1 ladder.
- "The inherited headline numbers (rr600 2 % → 87 %, support survivors 28 / 29, depth-3 13–28 %, Robbie's main
  effects, '6–11 of 70 flips') were not re-derived here."

Open questions with cross-person content (EA/ATLAS.md:L249-271):
- Q2: "How much of Robbie's best-cell vs best-cap6-state gap (31 vs 37 textbook72, 904 vs 997 dev) is interface, and
  how much is RL?" A best-recipe whole-proof model under our T1 ladder, or our state model under Leon's RL, would
  separate them.
- Q3: whether `nd_verify`-only accepts use forward box citations, including Robbie's token cells.
- Q4: "No frozen read anywhere exceeds k 256 on textbook72".
- Q5: "There is no noise floor for T1 ladders, state models, long pools or the support counts."
- Q7: "Robbie's pipelines are budgeted in wall-clock (2,400 s); ours in attempts. No cross-member comparison is
  compute-matched."
- Q8: "Most fork families have 2–4 seeds and Robbie's 3."

### 2.4 Protocol eras

Source: EA/data/protocol_differences.csv:L2-11, "re-quoted" in the reviewed copy (EA/ATLAS.md:L9-11). These are the
rows relevant to other people.

| era (CSV line) | checker / judge | pools | k | T | seeds | notes (verbatim) |
|---|---|---|---|---|---|---|
| Sept imports (L3), incl. Dmitry's cap-comparison, 09-08..10 | strict replay ND verifier (`strict_verify`) | textbook58-dev, validation-36, synthetic | 16 | not stated (cap-comparison) | 1 | "Dmitry's cap-comparison: caps 6/10/12, dev58, 1 seed" |
| Lean ∧ nd_verify (fork) (L5), 09-18..26 | Lean 4.34 ∧ nd_verify | transfer2285, held-out, ds pools | 256 (frozen) / in-loop 8x32 (T1) | 0.8 / 1.0 | 2 | "lean-judge: Lean-only excess 0.021 %…" |
| Lean alone (fork) (L6), 09-27..10-02 | lean_judge | textbook72, dev1108, holdout250, rr600, ge17_70, long2, sc383, transfer2285 | 64 (dev) / 256 / up to 10^7 (support) | 0.8 (reads) / 1.0 (some support) | 2-4 (3.2M) / 3 (9.56M) | batch 2048 vs 4096 flips 6-11 of 70 textbook72 problems |
| Robbie autoresearch (L7), 09-21..26 | nd_verify (token) / Lean gate + nd_verify (lean) | dev1108 (sha1-even half of transfer.jsonl), holdout1177, textbook72 | 64 (dev) / 256 (textbook) | 0.8 | 3 per kept config | "dev metric = theorems with ≥ 1 accepted proof in 64 samples; ≥ 7-line filter vacuous" |
| Robbie factorial / combined (L8), 09-28..30 | Lean gate + nd_verify (lean cells) / nd_verify (abs cells) | dev1108, holdout250, textbook72 | 64 / 256 | 0.8 | 3 | "2,400 s single-GPU budget per pipeline; only after-RL reads in git (passk.csv)" |
| Robbie state recipes / TTRL (L9), 09-30..10-01 | Lean alone (state); TTRL rows as harness | dev1108 | 64 | 0.8 (reads) / 1.0 (TTRL training) | 3 | "TTRL trains on the dev statements themselves: not comparable with held-out reads" |
| Leon (L10), 09-2x | nd_verify (runs) / nd_v2 (fixed, ndbench) / strict_verify | textbook dev58, sealed length 12-14 pool (1,931), dev 1,610 | 32-4096 | 0.8 | 1-3 | "0 forward citations in 876,479 of his accepted proofs" |
| Charles (L11), 09-2x | strict_verify | textbook72 (all 72), new textbook194 | 32-64 | 1.0 | 1 | "'new capability' = frozen 0/32 and trained ≥ 0.5 (a k = 32 threshold, not a support test)" |

### 2.5 The whole-proof re-score (Addendum 1)

**Why.** "No fork whole-proof model had been scored on textbook72, dev1108 or holdout250. That left every fork ↔ Robbie
row unmatched on format, and the interface effect unmeasured on these pools" (EA/ATLAS.md:L187-188).

**What was rescored** (EA/README.md:L35-45; EA/ATLAS.md:L190-195):
- **Checkpoints.** Eight existing ones, "all **3,214,336 params (4 × 256), `lean_seq` whole proof, from scratch, Lean
  alone** (`eval_set.py` → `lean_judge`; `nd_verify` unmodified and unused)":
  - C0 cap 6 (cap-6 control set, depth3 f0 a1, 155k): frozen `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt`, T1
    `ds-generator/ckpts/ladder/la_T1_c0_s{0,1}_r8.pt`;
  - K12 cap 12 (`data/kh/train_k12.jsonl`, 155k): frozen `cap-horizon/ckpts/kh/stage1_k12_s{0,1}.pt`, T1
    `state-cap12/ckpts/ladder/la_T1_K12_s{0,1}_r8.pt`.
- **Reads.** textbook72 at k 256, dev1108 at k 64, holdout250 at k 256; T 0.8, sample seed 0, batch 2,048,
  `max_new` 512.
  - The pre-registration said batch 4,096, which ran out of memory with two jobs per card. Batch 2,048 is the same in
    every arm.
  - Two jobs per RTX 3090; peak 8.0–8.4 GB per job.
- **Pre-registration.** Pre-registered in Addendum 1 (`b4f08b79`, 17:23:40Z), before the first pod (17:24:44Z)
  (EA/README.md:L22-24).

**Result: solved counts per seed (s0, s1), Lean alone** (EA/README.md:L64-69):

| model | textbook72 /72 | dev1108 /1108 | holdout250 /250 |
|---|---|---|---|
| C0 cap 6 frozen | 12, 11 | 54, 36 | 15, 8 |
| C0 cap 6 T1 | 15, 13 | 417, 465 | 104, 102 |
| K12 cap 12 frozen | 21, 21 | 415, 384 | 115, 104 |
| K12 cap 12 T1 | 25, 22 | 797, 771 | 181, 177 |

**Verdicts:**
- **(i) Proof state vs whole proof** at the same 3.2M recipe, cap and stage: "Whole proof is below state **in all 8
  dev1108 / holdout250 cells, by 41–322 theorems** (holdout250 +81.5, +57, +79, +41)" (EA/README.md:L74-79).
  - "**On textbook72, only the cap-12 T1 cell (+13.75) is outside the ≈ 7 floor** the addendum set. Cap-12 frozen
    (+7.25) is at the edge. The two cap-6 cells (+3.5, +5) point the same way but are not differences."
  - Caveats: whole proof has 2 seeds and state 2–4; the state reads used batch 4,096 and `max_steps` 96 /
    `max_action` 512. "Statement (i) holds as a direction."
  - *derived* dev gaps (state mean − whole-proof mean, from EA/ATLAS.md:L131-142): cap 6 frozen +322, cap 6 T1
    +263.5, **cap 12 frozen +378.5**, cap 12 T1 +166. The stated upper bound of 322 does not cover the cap-12 frozen
    gap (see §7).
  - "The cap-6 whole-proof base barely solves dev theorems (7–14 lines) at all: 54 / 36 of 1,108, vs 405 / 329 for
    state" (EA/ATLAS.md:L73).
- **(ii) Our C0 T1 vs Robbie's `lean-naive-ei`:** "15, 13 vs 8, 6, 10 on textbook72, and 104, 102 vs 45, 42, 37 on
  holdout250. It **holds**" (EA/README.md:L80-83).
  - "Robbie's cells are Lean gate ∧ `nd_verify`, and on textbook72 they were RL-trained on 14 of the 72 theorems.
    Both differences favour his cells, so the direction stands a fortiori. His model size is not recorded."
  - Not compute-matched: "his pipeline is 2,400 s; ours is a full T1 ladder" (EA/ATLAS.md:L201-203).
- **Expected ranges:** "6 of 12 cells are in range in both seeds". The frozen bases fell far below on long theorems:
  C0 frozen holdout250 15 / 8 against an expected 30–90 (EA/README.md:L84-86).
- **(iii) Truncation: missed.** 11 of 24 reads had > 0.1 % of samples at `max_new` 512 (max 0.258 %). Re-read at
  1,024, all 11 gave the **identical solved set**, so the cap does not bias the counts (EA/README.md:L87-89).
  `only_512` = `only_1024` = 0 in all 11 rows (EA/data/truncation_check.csv:L2-12).
- **Re-draw spread** (batch 4,096 vs 2,048 on the same checkpoint, 11 pairs): −5 to +7 on dev, −2 to +3 on
  holdout250, −4 to 0 on textbook72 (EA/README.md:L90-91).
- **Reviewer's checks.** All 24 reads recounted identical. 4,356 proofs Lean re-checked with the reviewer's own
  headers and harness: 0 rejected. Negative controls (goal set to `False`; a different theorem): 0 / 1,200 accepted
  (EA/README.md:L71-73).
- **Cost** (EA/README.md:L48-51):
  - 1.08 pod-hours, $0.54 (`podbudget`'s $0.50/h fallback rate, not a verified billed rate);
  - per arm 491–574 GPU-s, 306,688 attempts, 45.2 / 50.3 / 56.8 / 62.3 M generated tokens, 0 training steps;
  - GPU-s are shared-card wall time.
- **Term size** (reviewer's sample): median 8–11; max 11 / 23 / 35 / 44 for C0 frozen / C0 T1 / K12 frozen / K12 T1
  (EA/README.md:L92).

**Reviewer's next steps** (EA/README.md:L123-128):
- (a) a paired 4+-seed textbook72 interface read;
- (b) "Fork vs Robbie on the 58 `textbook_dev` theorems only, for a held-out comparison";
- (c) frozen best-cap12 pass@4,096 on textbook72.

### 2.6 The create-vs-elicit table

Source: EA/ATLAS.md:L163-183; full rows in EA/data/create_vs_elicit.csv:L2-12.

- **Rubric** (EA/ATLAS.md:L165-168):
  - strong = beyond the MDD on ≥ 3 seeds, base reach measured to ≥ 10⁴ attempts, pre-registered, reviewed, Lean;
  - moderate = one or two of these missing;
  - weak = post hoc, n = 1, or inside the floor.
- **No line reaches "strong for creation"** (EA/ATLAS.md:L83-88). Of 11 lines, none is above "moderate"
  (EA/README.md:L100-102).
- **The only row with another mentee's result** is "expert quality" (search-expert; frontier-supply; robbie-ttrl-*).
  - Its key numbers include "Robbie TTRL at 5x: targets-only EI 1,088 vs TTRL 1,079 vs sample-more 1,020 of 1,108
    dev".
  - Direction "unclear", strength "weak"; caveat "Robbie's dev metric at T 0.8, Lean and nd_verify"
    (EA/data/create_vs_elicit.csv:L12).
  - *derived:* no Leon, Charles or Dmitry result is rated in this table.

---

## 3. What the atlas says about each mentee (up to 2026-10-02)

Review column codes (EA/MAP.md:L3): R = reviewed, R! = reviewed with result-changing findings, U = unreviewed. The
atlas says "Other members' results are described neutrally with sources. This is a map of evidence, not an assessment
of anyone" (EA/ATLAS.md:L24). Headlines are "copied from the source and carry its caveats" (EA/MAP.md:L3).

### 3.1 Robbie

Robbie owns 15 map rows (derived from EA/data/experiment_map.csv). Every result row is U.

| date | row | protocol | headline (as copied) | src |
|---|---|---|---|---|
| 09-22 | autoresearch pre-Lean 000–011 | token, ≤10M, ‡; dev1108; "600 s total / 240 s pretrain / 2 EI rounds / k=32, mostly 1 seed" | "000 baseline 56 dev; 001 67 (same config, different RNG: ~+-10 noise); best kept 011 = 119" | EA/MAP.md:L59; experiment_map.csv:L37 |
| 09-22 | autoresearch token era | token, ≤10M, ‡; "dev1108 pass@64 T0.8, 3 seeds; 1200 s / 300 s pretrain / 4 EI rounds x1500x32" | "012 baseline 148 (139/141/163); best kept 081 polar-express 404" | EA/MAP.md:L60; csv:L38 |
| 09-22 | pretrain POC run0 | 3.2M token, ‡, single seed | "frozen 4/1108 dev-transfer solved -> 38/1108 after 2 EI rounds; L* 0 -> 8; plumbing check" | EA/MAP.md:L61; csv:L39 |
| 09-24 | autoresearch Lean era | 9.56M `lean_seq`, †; "2400 s total / 300 s pretrain / 4 EI rounds x1500x32" | "153 = 687 (676/700/685), holdout1177 733 (732/737/729); 186 = 680; 198 = 681; 207 simplification 635" | EA/MAP.md:L62; csv:L40 |
| 09-26 | pretrain ablations / correlations | ≤10M, †, 3-seed means | "dev vs holdout r=0.99 (Lean era, n=100); dev vs textbook r=0.76 (Lean, n=99); val loss vs dev r=+0.21 (Lean); best textbook run 150 = 21.7/72, incumbent 153 = 18.7/72" | EA/MAP.md:L113; csv:L71 |
| 09-28 | combined pipeline c001–c005 | 9.56M `lean_seq`, †; dev1108 pass@64 T0.8, 3 seeds, A40 | "c001 687.3 -> c002 (Leon EI) 804.3 -> c004 (guided sampling) 905.0 (over budget) -> c005 904.3 (915/893/905) within 2,400 s" | EA/MAP.md:L81; csv:L54 |
| 09-29 | factorial 0929 (8 cells) | see §2.2 rows 13–16, 19 | "dev naive 142.3 -> best 904.0; main effects pre +408, rl +268, tok +92; textbook72 pass@256 12.5% -> 43.5% (best cell 32/30/32 of 72); holdout250 pass@1 43.8% (best-ei) vs 30.1% (best-leon), pass@64 58.9% vs 79.1%" | EA/MAP.md:L82; csv:L55 |
| 09-29 | test-time scaling c005 | frozen c005 s0–s2, 9.56M, †; "holdout1177 (114 >10 lines), k up to 64 (bigk 1,024), T0.8, 3 seeds; textbook72 k up to 256" | "plain 31.2% pass@1 / 80.8% pass@64; resample 57.4% / 85.6%; SMC N=64 84.4%; beam/best-first no better than plain at matched tokens; value head 69% pairwise, no gain; textbook72 c005 plain 41.7% / resample 50.5% at k=256" | EA/MAP.md:L101; csv:L64 |
| 09-30 | TTRL dev64 | c005, †; "64 dev theorems failed by c005 at 64 plain samples; guided sampler T1.0; 8 rounds; matched samples ~2,400/target" | "s0: TTRL 48/64 vs sample-more 31/64 vs unrelated-variants 28/64; s1: TTRL 41 vs 31" | EA/MAP.md:L84; csv:L57 |
| 10-01 | TTRL at scale | c005 s0–s2, †; "dev1108 (baseline 915/893/905), guided sampler T1.0, 3 seeds x 3 arms, read at 1x-5x compute" | "at 5x (3-seed mean): targets-only EI 1,088, TTRL 1,079, sample more 1,020 of 1,108; at 1x EI 1,069 vs TTRL 929" | EA/MAP.md:L85; csv:L58 |
| 09-30 | state recipes 0930 | ~9.56M, `lean_seq` / `lean_staten`, **Lean alone**; dev1108 pass@64 T0.8, harness EI 4 rounds; 3 seeds | "SN beats C0 on every recipe by 111-178 (medians); 198: C0 669/692/216 vs SN 852/824/798; SH below SN by 84-118" | EA/MAP.md:L53; csv:L36 |
| 09-30 | bigger model / longer pretrain | recipe 198 at 9.6M/300 s, 9.6M/1200 s, 38M/1200 s; †; 3 seeds | "dev means 681 / 420 / 440 (bimodal: 702/294/265, 710/300/311); textbook 18.3 / 18.7 / 18.0 of 72" | EA/MAP.md:L67; csv:L45 |
| (code) | r1-cot scratchpad (owner `chainik1125`), autoresearch infra, shared-code port, WHERE_THINGS_ARE index | — | no numbers ("code only…", "tooling commits only", "code port only", "Index doc… run 198 score 681") | EA/MAP.md:L48, L133, L145, L153 |

The atlas on Robbie's work:
- **Comparability.** Fork state vs his factorial lean cells: "partly". Fork whole proof vs his naive lean cells:
  "partly". His autoresearch dev scores across eras: "no" (EA/ATLAS.md:L232-234).
- **TTRL is not held out.** TTRL "trains on the dev statements themselves: not comparable with held-out reads"
  (EA/data/protocol_differences.csv:L9).
- **RL-algorithm summary:** "GRPO > EI on depth 3 (token); Leon's recipe + guided sampling (+268 dev); TTRL ≈
  targets-only EI" (EA/ATLAS.md:L100).
- **Pretraining-recipe summary:** "Robbie's autoresearch (dev 56 → 687), bigger model bimodal; best-state recipe wins
  after RL" (EA/ATLAS.md:L99).
- **Format summary:** "Robbie: format pays only with good pretraining" (EA/ATLAS.md:L98).
- **The interface result has an independent, unreviewed counterpart in his own runs.** His state recipes have SN above
  C0 on every recipe by 111–178 (medians) under Lean alone (EA/MAP.md:L53). The C0 whole-proof seed at 216 (vs
  669/692) is one of the bimodal collapses (EA/data/headline_table.csv:L51).
- **Our port of his recipe.** The best-state run (ours, reviewed): "After the same T1 ladder best beats ours beyond
  MDD: textbook72 cap12 T1 52/51/52 vs 37/38/36/38 (+14.2, MDD 6.5), cap6 T1 39/40/33 vs 22/16 (+18.3, MDD 9.3);
  frozen at cap 12 level (textbook72 +1.2, dev -18); best ladders used 1.6-1.9x A40-seconds" (EA/MAP.md:L66).
  compute-match then gave our ladder 1.02× best12's A40-seconds and the gap stayed: +15.7 textbook72, +87.3 dev
  (CM:L99-101; STATE:L155).
- **Textbook72 under his checker.** In our textbook72 run, his combined model scores "32/30/32 under Lean and
  nd_verify (descriptive only)" (EA/MAP.md:L28). STATE: "Robbie's pretrained combined model scores 30–32 under his
  checker (descriptive: different model, format, checker; our counts are unchanged under it)" (STATE:L145).

### 3.2 Leon

Leon owns 9 map rows (derived from EA/data/experiment_map.csv). All are 3.2M token models except the Dan-models
benchmark plan.

| date | row | protocol | headline (as copied) | review | src |
|---|---|---|---|---|---|
| 09-23 | rl-hillclimb-ab | Robbie's `share_pretrain_4l_seed0` + agent-written rl.py; ‡; "dev 1,610 (L7-9) pass@32 T0.8; … 2 sampling seeds; 600 s RL per experiment; 1 training seed per recipe" | "Dev pass@32 solved: GEAR 401, orchestration 339 (incumbent 324), seed recipe 238, pretrained 7 of 1,610; textbook58 5-7 solved for every RL checkpoint vs 7/9 pretrained, 0 of 43 with reference >= 7 lines; dev pass@1 12.5-14.5% (ranking reverses vs pass@32)" | U | EA/MAP.md:L78; csv:L51 |
| 09-24 | rl-hillclimb-run2 | ‡; "sealed L12-14 1,931 at k=64/256, textbook58 k=256 T0.8 plain sampling; line-verified sampling used in training only" | "Champion 2 proves 707 of 1,931 sealed L12-14 theorems at pass@256 (570/127/10 at L12/13/14; pretrained and run-1 best 0) and 10 of 58 textbook (first 7- and 8-line textbook solves, 3 of 43); sealed L12-14 pass@1 12.4%, textbook pass@1 5.2% vs 4.1% pretrained" | U | EA/MAP.md:L79; csv:L52 |
| 09-25 | length-generalisation | ‡; "test L6-18 up to 300 per length, 32 samples T0.8, unbiased pass@k; 3 seeds (101-103) per RL arm; **equal metered budget 3.9e15 FLOPs**" | "pass@1 one line past each arm's RL maximum is 2.8-4.3%, two lines past <= 0.3%, nothing at L14-18; arm C 12.7% at L11 vs 0% pretrain; joined conjunctions solved at 15-21% of the part product" | U | EA/MAP.md:L23; csv:L16 |
| 09-25 | repr-goals-length | ‡; 32 samples T0.8; 3 seeds | "No representation moves the wall: pass@1 <= 2.2% at L13 and 0.0% at L14-18 for every variant; nope = abs (9.6% at L12), pos-line 4.2%, goal notes 2.2% vs 0.6% at L13" | U | EA/MAP.md:L52; csv:L35 |
| 09-26 | midtrain-long-glued | ‡; 32 samples T0.8; **one seed** | "After RL, long mid-training is no better past L11 and worse on natural L12-14 (2.9% vs 5.3% pass@1); in distribution L6-11 49.7% long vs 46.7% base" | U | EA/MAP.md:L63; csv:L41 |
| 09-30 | ndbench | mixed checkers; "textbook_dev58 pass@k up to k=4096 T0.8; 12 suites; single checkpoint per model, one sampling seed; item bootstrap CIs" | "textbook_dev58 pass@1 / pass@4096: base 4.1% / 17.2%, rl 5.5% / 22.4%, armC 9.3% / 13.8%; ~40% of bootstrap resamples show a base/rl crossover; base assigns ~7.0 nats/line less than rl to neutral proofs of rl-only theorems" | **R** | EA/MAP.md:L117; csv:L75 |
| 10-01 | ndbench on Dan's models | Dan's best-state SN best6/best12, Stage-1 and T1, 3 seeds; Lean judge `lean_v2` | "Plan, adapters, Lean judge and dashboard code committed; no result numbers for Dan's models are committed on the branch (outputs on /scratch)" | — | EA/MAP.md:L120; csv:L78 |
| 10-01 | nd-verify fix | scan of 876,479 accepted proofs | "Unfixed box_citable lets a line discharge a later box that cites it, so circular proofs of non-theorems (e.g. /- P > Q) verify; fix adds `if e >= i: return False`; 0 of 876,479 Leon-run proofs used a forward citation" | U | EA/MAP.md:L146; csv:L94 |
| 09-26 | rl-dashboards | tool | "Tool and proposal note… no new experimental result" | — | EA/MAP.md:L136 |

The atlas on Leon's work:
- **Comparability.** "Leon textbook dev58 / Charles textbook72 vs fork textbook72: **no**" (k 32–4,096; `strict_verify` /
  nd_v2; 3.2M token models) (EA/ATLAS.md:L235).
- **His RL inside Robbie's factorial.** Leon's RL (GEAR) enters Robbie's factorial as "Leon RL + guided" (rl-leon-c005).
  That arm carries the "+268 dev" RL main effect, which is unreviewed (EA/ATLAS.md:L77-78, L100).
- **His verifier fix.** The fork's `nd_verify` still has the bug Leon fixed. Token-era `nd_verify`-only counts vs Lean
  are "not checked" (EA/ATLAS.md:L36-37, L237).
- *derived:* in ndbench, arm C is above base at pass@1 (9.3 % vs 4.1 %) and below base at pass@4096 (13.8 % vs
  17.2 %). That is a pass@k crossover on dev58 (one checkpoint, one sampling seed).

### 3.3 Charles

Charles owns 3 map rows (derived from EA/data/experiment_map.csv).

| date | row | protocol | headline (as copied) | review | src |
|---|---|---|---|---|---|
| 09-23 | exp-00 local check | `share_pretrain_4l_seed0` + 50 GRPO steps, 3.2M token; old ND checker; "textbook72 k=64 T1.0 seed 0; heldout greedy 1,000; rl_targets 200 pass@32 T1.0" | "Textbook72 10/72 (8 dev58, 2 train14) both frozen and after RL, 0/43 at reference >= 7; long-pool pass@32 14/200 vs 11/200; KL 0.0017" | R | EA/MAP.md:L134; csv:L82 |
| 09-27 | exp-00c lr-ei | Robbie `039_muon-adamw-finish-5pct_s1` + GRPO / EI; old ND; "eval 200 (160 L7, 40 L8) 32 samples T1.0; textbook72 32 samples T1.0; seed 0; ~12.3k samples per arm" | "L7 avg solve rate 0.122 frozen -> 0.39-0.43 GRPO, 0.545 EI; EI L8 0 -> 0.266; textbook72 avg 0.101 -> 0.084-0.119, long textbook 0-1 of 43 (same problem)" | R | EA/MAP.md:L80; csv:L53 |
| 09-30 | textbook problem release | data only; reference proofs via strict_verify; "Lean 4.34.1 accepts all 184" | "194 transcribed textbook problems (184 with search-found proofs; 85/69 at >= 7 lines), audited disjoint from textbook72 and RL pools by renaming class; no model evaluated on them" | — | EA/MAP.md:L116; csv:L74 |

The atlas on Charles's work:
- **His "new capability" definition** is "frozen 0/32 and trained ≥ 0.5 (a k = 32 threshold, not a support test)"
  (EA/data/protocol_differences.csv:L11).
- **Comparability.** His textbook72 numbers vs the fork's: "no" (T 1.0; strict_verify; 3.2M token)
  (EA/ATLAS.md:L235).
- **Later use of his release.** After the atlas, our guided-tts run used "Charles's release (187)" as its evaluation
  pool. **long** = the release rows with `min_lines` > 10 (90) (GT:L42-43).

### 3.4 Dmitry

Dmitry owns 1 map row (derived from EA/data/experiment_map.csv).
- **The textbook72 data.** "Adds the 72 textbook prompts; sha256 identical to the fork's data/eval_only/textbook72
  files (dev 1b04192d..., train e6a219e0...); third slice old_final (73) unrecoverable" (EA/MAP.md:L111). Its
  protocol notes: "data only (no numbers); textbook_train14 were RL training prompts in the cap-comparison sprint,
  dev58 its dev benchmark" (EA/data/experiment_map.csv:L69).
- **The cap-comparison sprint** appears as an import: "Dmitry's cap-comparison: caps 6/10/12, dev58, 1 seed", under
  `strict_verify` at k 16 (EA/data/protocol_differences.csv:L3).
  - The corresponding map row is owned by `dan-codex`: "best sampled 10/58 (Direct cap 12, from 8 after SFT); no
    model solves a textbook problem with reference above its own cap; long synthetic training success 0% (cap 6) ->
    91.5% (cap 12) without textbook transfer" (EA/MAP.md:L37).
  - It is also cited as "cap-comparison: 0/43 textbook targets beyond cap 6" (EA/data/create_vs_elicit.csv:L10).
- **An earlier idea.** STATE credits "cast ND into Lean and measure novelty by model scale (Dmitry's idea, with a
  Qwen3-Coder in-context v0)" (STATE:L27). That became r2-run1-scale-novelty (EA/MAP.md:L15).
- **No later results.** No Dmitry RL result after 2026-09-25 is in the atlas (derived from the map rows).

---

## 4. Our creation-vs-elicitation results

### 4.1 capability-defs (2026-10-05; reviewed)

**Status.** Completed and reviewed 2026-10-05; nothing quarantined (CD:L8-14).
- The reviewer recounted every pre-registered quantity blind. Lean accepted **3,710 / 3,710** counted proofs, and the
  negative controls behaved.
- "The central measurement, the known-proof estimate, the J9 certification and the recommendation **stand**."
- There were eleven corrections. Five claims are "not supported as written": Q16's "beta-binomial hit"; the read caps
  deciding `textbook_6997…`; `1077`/`1648` in two seeds' strictest sets; the "≈ 20 passes over K12" mechanism; "35 of
  120" padded proofs (it is 26).

**Protocol** (CD:L43-71):
- **Model.** best-cap12 = `best_model.ALiBiGPT` 6 × 384, **9,560,832 params**, `lean_staten`, from scratch on K12
  (155,000 records), Stage 1 for 1,200 s, seeds s0–s2.
  - r8 = 8 EI rounds (`trajectory`'s T1 ladder, run on **RTX A6000**); r16 = `rl-continue`'s.
  - best-cap6 = the same recipe on `train_depth3_f0_a1`.
  - The replay-only control is `rl-from-ckpt`'s `c<S>_pend_r8`: the same 8 fine-tune rounds on K12 replay, with no RL
    proofs.
- **Theorems.** textbook72 (scoring only) + holdout250 = **322**.
- **Reads.** Plain: T 0.8, `max_steps` 96, `max_action` 512, k 256 per draw, batch 2,048. Guided:
  `guided_eval.py --arm logical`. Checker: Lean alone.
- **Budget.** K_eval-set = ladder GPU-s / (322 × 3.6 ms per pend attempt) = **19,281 / 21,107 / 23,310** at r8.
  - "The ladder seconds are RTX A6000 seconds and 3.6 ms is an A40 cost, so K_eval-set mixes GPU classes" (the
    reviewer's point).
  - In ladder attempts it would be ≈ 5.6–6.2 × 10³ per theorem.
- **Cost.** 77.21 pod-hours, $37.84; 77.0 A40-hours of process-level GPU time; 24.4 M attempts; 4.43 B generated
  tokens (CD:L85-88).

**Central measurement** (r8, draw x0, of 322; s0 / s1 / s2) (CD:L117-125):

| quantity | s0 | s1 | s2 |
|---|---|---|---|
| equal-k "created" (pend 0/256, r8 ≥ 1/256) | 54 | 51 | 60 |
| … not within base reach at K_eval-set (compute-matched) | **22** | **21** | **14** |
| … net of the replay-only control | 20 | 14 | 8 |
| … never solved by any seed's base | **4** | **5** | **5** |
| set level: r8 solves at k 256 / base within reach at K_eval-set | 286 / 265 | 286 / 270 | 293 / 281 |
| Δ_cov (r16 in brackets) | **+21** (+24) | **+16** (+32) | **+12** (+14) |
| RL-free controls at k 256: replay-only r8 / J7 continuation | 239 / 220 | 244 / 215 | 249 / 219 |

Findings around the table:
- **Set level.** "At set level RL is ahead at matched compute on every seed, and neither RL-free control closes the
  gap" (CD:L127-128).
- **The budget dominates.** "The budget is the dominant free parameter." At 0.1 / 0.3 / 1 / 3 × K_eval-set the
  compute-matched set is 38 / 36 / 36 → 33 / 28 / 28 → 22 / 21 / 14 → 21 / 20 / 3 (CD:L129-130).
- **"Created at k" is a fact about n.** 512 or ≥ 768 base attempts instead of 256 remove **4–17** equal-k theorems
  (CD:L131-132).
- **Bracket verdicts.** For the r8-solved hard theorems (55 / 45 / 52), "certified created 3 / 2 / 2". The median
  estimated k-to-solve is 10^4.6 / 10^5.3 / 10^4.5, "right at K_eval-set" (CD:L133-139).
- **Known-proof estimate.** It recovers a median 0.98 / 0.94 / 0.93 of measured p on 30 calibration theorems per seed
  at T 0.8. It is "not a strict bound" (CD:L143-146).
- **J9 certification.** "7 of 9 (theorem, seed) pairs are certified relative to their own seed's base" (CD:L170-171).
  "Four pairs on three theorems survive every RL-free control" (CD:L173-177). They are held-out members of families
  RL trained on.
- **Definitions disagree.** Mean off-diagonal Jaccard over 12 definitions: 0.29 (r8 x0), 0.34 (r16 x1). Seed Jaccard
  is low (0.06–0.44): "each seed's RL 'creates' different theorems" (CD:L219-223).
- **Plain vs guided (J3).** Guided ≥ plain at **18 / 18** checkpoints. On holdout250, guided adds +18 to +22 for cap-12
  pend and −1 to +4 for RL (CD:L239-240).
  - Pend guided solves 27/54, 28/51, 36/60 of B, but rescues only 3 / 4 / 1 of the compute-matched 22 / 21 / 14
    (CD:L241-242).
  - Guided costs ≈ 1.8× the tokens and 2.2× the GPU time per attempt (CD:L243-244).
- **Excluded middle: "teachable, not latent"** (CD:L248-265).
  - lem39 pend is 0 / 0 / 0; r16 is 0 / 36 / 13.
  - Four LEM demonstrations install it in every base (36 / 33 / 36), even in a no-DN knockout base (35 / 37 / 37 with
    A16).
  - "What RL contributed there was finding an instance" (CD:L427-428).
- **IRT.** "At matched ability gain, EI creates no more DIF+ items than RL-free training." The matching is approximate
  (CD:L279-284).
- **J7 compute-matched continuation** (82 / 84 / 81 % of the ladders' GPU-s, across GPU classes) solves 220 / 215 /
  219, against pend's 232 / 236 / 234 and r8's 286 / 286 / 293: "a lateral move" (CD:L291-297).
- **J8.** The share of new solves certified elicited is "not monotone on any seed" in the RL start step
  (CD:L300-308).
- **J10.** Given 16,384 more attempts, pend finds 29 / 45 (0.64) of the long-pool pairs RL "creates" at equal k
  (CD:L310-311).

**Recommended standard** (REPORT §4; unchanged by the review) (CD:L208-217):
- **A.** Compute-matched reach with each theorem's k-to-solve interval. "Certified created only at UB95 < 0.05 / K,
  which takes ≈ 60 K zero-success attempts". Report net of both RL-free controls and of other seeds' bases.
- **B.** Capability vs propensity: plain pass@1 against the best per-theorem method within the budget (more samples,
  or guided redraws).
- **C.** Key-step family acquisition with a teachability test (base vs a knockout pretrained without the key step).
- **D.** IRT ability with an ability-matched placebo, as a diagnostic.

**Interpretation (executor's, left standing).** "On these models, equal-k 'creation' mostly measures how few base
attempts were made … Yet at set level RL is ahead at matched compute on every seed" (CD:L421-430).

**Limitations.** One architecture at two caps, 3 seeds; K_eval-set divides A6000 seconds by an A40 attempt cost; no
guided reads of the fine-tunes or J7; cut-offs exceed policy in several strata (CD:L434-439). There is also no MDD in
the pre-registration (CD:L416-417).

### 4.2 create-or-elicit (2026-10-12/13; reviewed)

**Status.** Completed and reviewed 2026-10-13; nothing quarantined. The pre-registered primary result and its verdict,
**"needs exposure"**, stand. There were ten rewordings (COE:L8-21). Three claims are **not supported as written**:
- that the families "need" σ in pretraining, beyond 16 rounds of this EI;
- "sharpening the base is not RL" as a general claim;
- "(18 / 17 / 8 survive all)".

The Boschloo transposition fixed three p-values: 0.0020 → **0.0032**, 0.30 → 0.39, 0.035 → 0.034 (COE:L20-21,
L590-601).

**Design and protocol:**
- **σ** = double negation (DN, `Classical.byContradiction`) applied to a NEGI line (COE:L27-31).
- **Knockout data.** K12⁻ removes the 16,961 σ⁺ records (10.94 %), refilled per length to 155,000 (COE:L77-87).
  K12^1% puts back 1,550 σ records (COE:L88-90).
- **Model.** `best_model.ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten`; Stage 1 1,200 s on an A40.
- **RL.** T1 EI for 16 rounds: k 32, T 0.8, 600 fine-tune steps per round, 4,495 `rl_targets`, and 20,000 replay
  records from the arm's own pretraining set (COE:L61-66).
- **Arms.** full s0–s5 (s0–s2 old, ladder r1–r8 on RTX A6000); knockout s0–s5; dose1 s0–s2 (COE:L68-73).
- **Reads.** Plain k 256, T 0.8, 96 steps, 512 tokens per action, batch 512; guided `--arm logical` (COE:L100-105).
- **Decision rule** (pre-registered; COE:L106-120):
  - a family is "acquired" when ≥ 50 % of its strict held-out members are solved;
  - "Created" needs ≥ 2/6 knockout seeds acquiring **and** a certificate;
  - power: "A 0 / 6 knockout outcome bounds the per-seed creation rate below 0.39".
- **Cost and matching.** 16 pods, 309.34 pod-hours, $182.50 (COE:L124). Arms are compute-matched on protocol: every
  knockout/full and dose1/full ratio is within 0.95–1.03 (COE:L155-156).

**Results:**
- **Primary.** 6 / 6 full vs 0 / 6 knockout seeds with ≥ 1 family at the bar at r16, Boschloo **p = 0.00024**. The
  same holds on x1, guided and the original 178-member sets (COE:L221-223).
- **Per family** (Holm over 6) (COE:L224-231):
  - contraposition_conv 6 vs 0 (Holm 0.0015) → "needs exposure";
  - negated_conditional, peirce and peirce_sequent 3 vs 0 (Holm 0.17) → undetermined;
  - excluded_middle 1 vs 0 (p 0.39) → undetermined;
  - De Morgan 0 vs 0 → "neither".
- **Members solved at r16.** full 42 / 75 / 77 / 65 / 23 / 33 (median 53.5) vs knockout 0 / 2 / 1 / 0 / 0 / 2
  (median 0.5); MW U = 36, p = 0.0011 (COE:L232-233). IQM difference **53.0 [31.0, 72.8]** (COE:L234-236).
- **The decision happens before RL.** contraposition_conv is already at the bar at pend on 5 / 6 full seeds (6 / 6
  guided), so "the primary indicator is decided before RL starts". The RL-only reading (exploratory): families
  acquired *during RL* full **5 / 6** vs knockout **0 / 6**, **p = 0.0032** (COE:L237-242).
- **Dose arm (exploratory).** r16 58 / 39 / 30; 3 / 3 vs 0 / 6, p = 0.0033 (COE:L261-266).
- **σ is rare in the knockout bases, not absent** (COE:L276-293). σ/σ⁺ appear in round 1 of every knockout ladder. Free
  positive reductio first appears at knockout s1 r9, s2 r12, s3 r15, s4 r15, s5 r2, and s0 never.
- **Certificates.** 2 of 6 knockout bases certified out of reach, and "no family is certified for any seed"
  (COE:L303-312).
- **General ability** (COE:L369-383):
  - knockout held-out greedy −6.88 pp, with +0.12 pp on non-σ theorems;
  - pass@256 at pend is lower also on intuitionistic theorems (textbook72 −4.0 / 53, holdout250 −4.3 / 225);
  - textbook72 at r16 is still −7.5.
- **Standard A on the 322.** Compute-matched created sets: full s3–s5 37 / 36 / 35, Δ_cov +37 / +36 / +32; knockout
  Δ_cov +29 / +31 / +35 / +37 / +26 / +21. These are not netted against RL-free controls (COE:L389-396).
- **Phase 0 budgets** (old full s0–s2 at r8). The compute-matched sets under five allocations run from K_att 34 / 33 /
  33 down to K_adapt 21 / 20 / 14 (COE:L419-425).
  - "21 / 20 / 14 are compute-matched at all five allocations, and 18 / 17 / 8 of them have no base success in ≥
    66,304 attempts" (COE:L427-428).
  - The A40 cost of pend is 7.22 / 8.04 / 6.36 ms per attempt, vs capability-defs' 3.6 ms (COE:L415-416).
- **Power sampling** (one MH sampler, α 1.5–4) solves 0 of RL's compute-matched new solves. It also fails a positive
  control (0 / 17 vs plain 6–13 / 17), so the null is sampler-specific (COE:L443-462).
- **Cut-offs.** "64 of 74 plain reads have more than 0.1 % of some stratum cut off". The guided strict counts agree
  with plain (COE:L545-555).
- **Limitations.** "One architecture (9.56 M, proof state) … One RL algorithm: T1 EI at k 32, T 0.8. A negative
  knockout result says 'this EI did not', not 'RL cannot'" (COE:L649-651). Excluded middle would need "≈ 12–15 seeds
  per arm for 80 % power" (COE:L655-656).

### 4.3 create-or-elicit-paper (2026-10-13/14; reviewed) and paper-clean (2026-10-14; reviewed)

**create-or-elicit-paper** was a writing run: a 34-page paper and a 2,499-word blog, plus five pre-registered pod
checks C1–C5 (COEP:L8-10).
- **Review.** Four sub-auditors checked **731 claims**. "No headline number is wrong anywhere". The review asked for
  17 paper rewordings (P1–P17) and 8 blog rewordings (B1–B8) (COEP:L12-19).
- **Not supported as written** (COEP:L21-28):
  - "every rejection was the pre-filter's" (P9);
  - "GRPO would first succeed on seeds 1, 2 and 5" (P11: by A5 base rates it is s1, then s4);
  - the PUCT half of a test-time claim (P16);
  - knockout s5 proving `2256` in every r16 draw (P6).
- **C4 drop rule fired.** Knockout s1's base was sampled 18,432 times per member with no early stopping. Only `1460`
  of `1246` / `1460` / `2256` is within reach, so the "elicitation, not creation" reading of knockout s1 is **dropped**.
  The base reaches 2 of the 5 theorems the ladder proves (COEP:L31-37, L251-272).
- **C5.** The pre-filter's false-reject check is 0 / 210,151 distinct rejected texts; 95 % bound 1.43 × 10⁻⁵ per
  distinct text (COEP:L38-40).
- **C1.** Doubled caps change each strict count by ≤ 1 and no family verdict. Cut-offs fall only 1.0–2.2×
  (COEP:L41-46).
- **C2.** The dose r16 redraw is 56 / 39 / 30 and guided 58 / 42 / 29 (COEP:L47-48).
- **C3.** The textbook72 full − knockout gap at pend over 6 vs 6 seeds is +5.83 (COEP:L49-50).
- **Descriptives** (COEP:L333-345):
  - hardware-matched (full s3–s5 on A40): acquired during RL 2 / 3 vs 0 / 6, **p = 0.034**; ≥ 1 family at r16 3 / 3 vs
    0 / 6, p = 0.0033;
  - RL-phase gains: full 24 / 69 / 55 / 42 / 8 / 15 vs knockout 0 / 2 / 1 / 0 / 0 / 2 (p = 0.0011);
  - Δ_cov means 35.0 vs 29.8, permutation p **0.095**.
- **A5 (post hoc).** 0.547 seeds expected with a strict success by r16, 3 observed, P(≥ 3) = 0.0060
  (COEP:L323-329).
- **Claim audit inside the run.** 382 rows with 70 discrepancies, plus a re-audit of 90 rows with 22 (COEP:L97-98).
  W3 ("≤ 15 discrepancies") missed (COEP:L185).
- **What the paper can claim** (librarian's interpretation; COEP:L480-484): "Within 16 rounds, this EI amplified a
  composition that pretraining had exposed but did not acquire the classical families without it … the RL-specific
  evidence is post hoc".

**paper-clean** ($0, no pod) produced clean drafts "equivalent to the marked reading copy" (PC:L8-33):
- 12 of the 13 possible errors were real and fixed;
- no printed theorem in a textbook72 class;
- blog 2,487 words;
- "Not supported: nothing".

It changed the rarity factor to 4.2× (DN) and 2.9× (NEGI) by record share (PC:L64-67).

### 4.4 The paper and blog as they stand (clean versions)

**Abstract** (PAPER/sections/00_abstract.tex:L1-15):
- the model is a "9.56M-parameter transformer prover trained from scratch on 155,000 synthetic propositional-logic
  proofs and judged only by Lean 4";
- "0/6 against 6/6 full-exposure seeds, a pre-registered contrast ($p=0.00024$) largely present before RL";
- "During RL, full-exposure seeds gained 8--69 held-out classical theorems and knockout seeds 0--2; 5/6 against 0/6
  acquired a new family ($p=0.0032$; not pre-registered)";
- "1% … restored acquisition (3/3 seeds; exploratory)";
- "five of six proved held-out theorems with σ … 1--7 times in 1.1--1.4M attempts";
- "In three earlier 8-round full-exposure runs, 51--60 theorems look RL-created at equal sample counts and 14--34 at
  RL's compute as base attempts (14--21 under all five allocations)".

**Blog** (PAPER/blog.md):
- **Epistemic status:** "one small model (9.6 million parameters), one kind of logic, one simple RL algorithm, six runs
  per main condition … I would not generalise this to large language models without more work" (L10-13).
- **GRPO caveat:** "a closely related study found the opposite with another RL algorithm (GRPO), so our result may be
  specific to ours" (L26).
- **Recommendation:** "report the result as a curve over the base's budget, include a control that gets RL's training
  without RL's proofs, and say which number of attempts 'never' means. Here, such a control … recovered 13% to 25% of
  RL's gain" (L156-158).
  - *derived from CD:L123-125:* (239−232)/(286−232) = 13.0 %, (244−236)/(286−236) = 16.0 %, (249−234)/(293−234) =
    25.4 %. Consistent.
- **Test-time compute:** guided redraws "halved the gap between base and RL model on one held-out set"; tree search
  "recovered 14% to 44% of what eight RL rounds add for the base"; "with guided redraws the base proves only 3, 4 and
  1 of the 22, 21 and 14 theorems still counted as created" (L162-169).
- **GRPO here:** "from full data, plain GRPO solved fewer theorems than our method …, and a coverage-rewarding variant
  about as many. GRPO from the knockout models has not been run" (L183-184).

**next_steps.md.** Item 1, the top priority, is "GRPO from the knockout bases, at matched samples — ≈ $40–60". Its
rationale (PAPER/next_steps.md:L27-44):
- "The title is scoped to EI because this is the decisive missing experiment";
- in the earlier 3.2M organism, GRPO acquired a depth-3 habit "(12/12 arms), where EI did so in 1/3".

Item 10 is an interface pilot (whole proof vs proof state from the same data), ≈ $25 (L116-118).

---

## 5. Claim-audit findings relevant to cross-person comparisons

**Scope and verdict.** claim-audit (2026-10-02, reviewed): "every headline count reproduces; three claims are weaker
than stated, none unsupported" (CA:L6-13). It audited **our** claims only: the week-in-review and STATE headlines since
2026-09-27 (CA:L15-17). The only other-mentee name in its rating table is Robbie, in C4a, which concerns our port of
his recipe (CAR:L35; derived from grep).

Ratings that bear on cross-person comparisons:
- **C4a "Robbie's recipe beats ours after RL"** holds with caveats (CA:L68).
  - "+18.33 cap 6, +14.17 cap 12 (IQM); replicates in fresh trainings (permutation p 1/28, 1/210); 3× parameters;
    best used ≈ 1.6–1.9× the GPU-seconds".
  - The reading copy adds (CAR:L35):
    - "+18.3 cap 6, +14.4 cap 12 … (+21.7, +13.1; permutation p 0.036, 0.005). But 'recipe' includes **3× the
      parameters**";
    - "extra *ladder* compute is ruled out at cap 12 only. Model size and architecture are not separated";
    - "'Level frozen at cap 12' is unresolved (+0.4, MDD 7.7)".
  - Suggested wording: "After the same ladder (equal attempts), Robbie's 9.6 M recipe solves 51–52 (cap 12) and 33–40
    (cap 6) of 72, against our 3.2 M model's 36–38 and 16–22; … model size is not separated from the recipe."
- **C4b textbook72 counts** are solid: per seed 37 / 38 / 36 / 38; one problem is a premise-order copy of a K12
  theorem; the dev set shares 1 class with K12 and 1 with `rl_targets` (CA:L69; CAR:L36). "Say 'per seed'. Footnote
  the 1/72 overlap."
- **C2a / C2b (interface)** (CA:L65-66; CAR:L32-33):
  - "proof-state base reaches 28 / 29" is solid as *reach*; at EI's "solves" bar (p̂ ≥ 0.01) it is only 21 / 14;
  - "the state, not the naming" is **weaker than stated**: "state is confounded with the step interface; naming null
    is n = 2 per arm".

  This matters for any recommendation that others adopt the proof-state interface. The gain is the state **and** the
  step interface together.
- **C7 "GPU nondeterminism ≈ half the seed spread"** is weaker than stated: variance ratio 0.543, F 95 % [0.23, 2.05];
  one cell, one pod (CA:L73). In SD terms it is 0.74, driven by 1–2 mode flips (CAR:L40).
- **Replays vs replications.** "Several 'agreements' are deterministic replays (same checkpoint and sampling seed,
  bit-identical) … They show pipeline reproducibility, not replication" (CA:L79-82).

Other audit-type caveats on cross-person numbers:
- **Unchecked expectation.** The atlas's expectation 3 ("1–5 headline comparisons in docs/STATE.md or the digests mix
  checkers or k without saying so") "was not reported against a count by the executor, and the reviewer did not
  recount it" (EA/README.md:L109-110).
- **Inherited numbers.** Robbie's main effects and "6–11 of 70 flips" were "not re-derived here" (EA/README.md:L119-120).
- **Map review scope.** The map was "reviewed for counts and traceability, not for its judgements" (EA/README.md:L94).
  The create-vs-elicit ratings "follow a stated rubric and are judgements, not measurements" (EA/README.md:L102).
- **Ledger spot check.** The create-or-elicit review spot-checked 18 inherited `claims_ledger.md` rows: every bold
  value was correct. One example: "L32's 'MDD 2.7' was not reviewed as stated" (COE:L610-613).

---

## 6. Methods we have that others might adopt, with evidence of value

For each: what it is, evidence (numbers + sources), and what the atlas records about the others' current practice.

### 6.1 Guided read-out (logical redraws at evaluation time; "capability vs propensity")

**What it is.** At test time, redraw a step that a per-step logical check rejects (without replacement, ≤ 10 per
attempt). Report it next to plain sampling as the "best per-theorem method within the budget" (definition B, CD:L213-214).

**Evidence:**
- **guided-tts** (reviewed): logical redraws beat plain on long textbook theorems in **6 / 6** models at matched
  sampled tokens: IQM **+9.1 pp** (cap 12) and **+8.3 pp** (cap 6) at k 64 (GT:L76-83; STATE:L173).
  - Models: best-cap12 / best-cap6 T1 r8, 9,560,832 params, Lean alone. Pool: "long" = 90 rows of Charles's release
    with > 10 lines (GT:L42-43).
  - The reviewer's intervals are [+5.9, +11.7] and [+5.8, +11.6]. The executor's MDD of ≈ 2.7 pp "was not
    independently derived" (GT:L85-89).
  - Structural-only redraws gain nothing (|Δ| ≤ 1.2 pp) (GT:L91).
  - Cost at equal attempts: 2.18× GPU-s and 1.78× tokens (cap 12); 2.34× and 2.68× (cap 6) (GT:L139, L142).
- **capability-defs J3:** guided ≥ plain at 18 / 18 checkpoints. Holdout250 +18 to +22 for cap-12 pend vs −1 to +4
  for RL: test-time compute helps the base more than the RL model (CD:L239-240). But guided pend rescues only
  3 / 4 / 1 of the compute-matched 22 / 21 / 14 (CD:L242).
- **create-or-elicit-paper:** "Guided knockout bases reach 1–3 strict members on 4 of 6 seeds at pend, where plain x0
  reaches none" (COEP:L341). Guided reads are what showed "rare, not absent".

**What others have.** Robbie already uses verifier-guided sampling:
- c004 "(guided sampling) 905.0 (over budget)" (EA/MAP.md:L81);
- the factorial's "Leon RL + guided" arm (EA/ATLAS.md:L144, L146);
- test-time "resample 57.4% / 85.6%" vs plain 31.2% / 80.8% on holdout1177 (EA/MAP.md:L101; pool from
  EA/data/experiment_map.csv:L64).

So the adoptable part is narrower: guided reads of the **frozen base** as a standing control for "RL created it"
claims. The atlas notes his factorial has **no frozen reads in git** (EA/ATLAS.md:L121-122).

### 6.2 Proof-state interface (`lean_staten`)

**Evidence:**
- **Atlas re-score** (same 3.2M recipe, cap and stage, Lean alone): state beats whole proof in **8 / 8 dev1108 /
  holdout250 cells**. holdout250 +81.5 / +57 / +79 / +41; on textbook72, cap-12 T1 +13.75 is beyond the floor
  (EA/README.md:L74-79).
  - The frozen cap-6 whole-proof base solves 54 / 36 of dev vs 405 / 329 for state (EA/ATLAS.md:L73).
  - The interface effect "is largest on frozen bases at long lengths" (EA/ATLAS.md:L265).
- **Robbie's own (unreviewed) state recipes:** "SN beats C0 on every recipe by 111-178 (medians)" under Lean alone
  (EA/MAP.md:L53).

**Caveats:**
- claim-audit C2b: the state is confounded with the step interface, and the naming null is n = 2 per arm (CA:L66).
- The textbook72 cap-6 cells are inside the floor (EA/README.md:L76-78).
- The atlas's open question 6 asks how much is naming vs action granularity (EA/ATLAS.md:L265-267).

**What others have.** Robbie has adopted proof-state recipes for dev1108 (EA/MAP.md:L53). Leon had planned to
benchmark Dan's best-state SN models, with no numbers committed by 2026-10-01 (EA/MAP.md:L120). Charles's and Leon's
numbers in the atlas are 3.2M token whole-proof models (EA/ATLAS.md:L235).

### 6.3 Budgeted creation tests (compute-matched reach, replay-only control, certificates, knockouts)

**What it is.**
- Give the frozen base RL's compute as attempts (K_eval-set), and report the created set as a curve over K.
- Net it against a replay-only control and the other seeds' bases.
- Certify "out of reach" only at UB95 < 0.05 / K (≈ 60 K zero-success attempts).
- Where possible, test acquisition with a pretraining knockout (CD:L208-217; COE:L106-120).

**Evidence:**
- **Equal-k creation shrinks.** 54 / 51 / 60 → **22 / 21 / 14** compute-matched → 20 / 14 / 8 net of replay → 4 / 5 / 5
  never solved by any base (CD:L117-122).
- **The threshold choice alone moves the count.** 512 or ≥ 768 base attempts instead of 256 remove 4–17 "created"
  theorems (CD:L131-132). The budget convention moves the set from 38 / 36 / 36 to 21 / 20 / 3 (CD:L129-130).
- **A control recovers part of RL's gain.** The replay-only control recovers 13–25 % of RL's set-level gain (blog
  L158; derived check in §4.4).
- **A pre-registered certificate check reversed a reviewed reading** (C4, COEP:L31-37).
- **The knockout design gives a decision rule with stated power** (0 / 6 bounds the creation rate < 0.39, COE:L119-120).

**What others have.**
- Charles's "new capability" is "frozen 0/32 and trained ≥ 0.5 (a k = 32 threshold, not a support test)"
  (EA/data/protocol_differences.csv:L11).
- Leon's run-2 headline is "707 of 1,931 sealed L12-14 … (pretrained and run-1 best 0)" at pass@256 (EA/MAP.md:L79).
  His own ndbench shows "~40% of bootstrap resamples show a base/rl crossover", with arm C below base at pass@4096
  (EA/MAP.md:L117).
- Robbie's factorial has only after-RL reads (EA/data/protocol_differences.csv:L8).
- On textbook72 "'RL solved X' never comes with base reachability on that pool" (EA/ATLAS.md:L261-262).

### 6.4 Noise floor / MDD and seed discipline

**Evidence:**
- **noise-floor** (2026-09-25, reviewed; 3.2M token era, `nd_verify`): frozen-ladder transfer solved has range 62–265
  (4.27×), MDD at n = 2 **±397** of 2,285. Held-out greedy has MDD ±16.3 pp (NF:L104-114). "Every frozen-ladder value
  proposal 10 ever reported sits inside the null range" (NF:L116-118).
- **Atlas.** textbook72 MDDs are 9.3 (cap 6) and 6.5 (cap 12). A same-checkpoint batch change flips 6–11 of 70
  textbook72 problems (EA/ATLAS.md:L155-157). "There is no noise floor for T1 ladders, state models, long pools or the
  support counts" (EA/ATLAS.md:L263-264).
- **compute-match** used pre-registered MDDs of 6.5 (textbook72) and 61 (dev) to call +15.7 / +87.3 (CM:L68, L99-101).

**What others have.**
- Robbie's own data show the floor matters:
  - "001 67 (same config, different RNG: ~+-10 noise)" vs 56 (EA/MAP.md:L59);
  - bimodal seeds "702/294/265, 710/300/311" (EA/MAP.md:L67);
  - recipe 198 C0 669 / 692 / **216** (EA/data/headline_table.csv:L51).
- Leon has single-seed results (midtrain "one seed", EA/data/experiment_map.csv:L41; hill-climb "1 training seed per
  recipe", L51).
- Charles uses seed 0 only (EA/data/experiment_map.csv:L53, L82).
- Leon does report item-bootstrap CIs in ndbench (EA/data/experiment_map.csv:L75).

### 6.5 Pre-registration (expectations, decision rules and drop rules committed before the first pod)

**Evidence:**
- **The atlas.** Addendum 1 was committed before the first pod (EA/README.md:L22-24). The expectations were scored
  honestly: 6 of 12 cells in range (EA/README.md:L84-86); expectation 2 was a "partial miss" (57, not ≈ 52)
  (EA/README.md:L96-99).
- **create-or-elicit.** The pre-registration came before the first pod. The one late change (Addendum 2) was
  disclosed, and the recount shows it did not decide the headline (COE:L43-50). The pre-registered Holm correction
  keeps three families at "undetermined" (COE:L224-231).
- **create-or-elicit-paper.** The pre-registered C4 drop rule fired and removed a reading the earlier review had
  endorsed (COEP:L31-37).
- **capability-defs.** The scorecard lists the misses (Q2, Q5, Q7, Q8a, J10, J8, Q16). The review caught that the run
  summary's own miss list "omits the partial misses and Q16" (CD:L332-350).

**What others have.** The atlas rubric needs pre-registration for "strong" (EA/ATLAS.md:L166). It records review
status for the other members (mostly U) but says nothing about pre-registration. So their pre-registration practice
is not recorded here (an absence of evidence, not evidence of absence).

### 6.6 Compute records (per-job registry rows; compute-matched comparisons)

**Evidence:**
- **Registry rows** hold `gpu_seconds`, `gen_tokens`, `attempts`, `lean_checks`, and `train_steps` / `train_tokens`
  for training jobs (CD:L85-87).
- **create-or-elicit matched its arms** within 0.95–1.03 on protocol (COE:L141-156).
- **Records exposed confounds:**
  - best-state's 1.6–1.9× ladder GPU-s (BS:L132) led to compute-match, which ruled out ladder compute at cap 12
    (+15.7 at 1.02×, CM:L99-101);
  - the reviewer found the A6000-vs-A40 mismatch in K_eval-set (CD:L70-71);
  - C4's measured 12.35 ms per attempt re-costed a proposal to ≈ $48 from $25–30 (COEP:L442-444).
- **Limits.** The claim-audit's registry had no `gen_tokens` or `lean_checks`, and its `gpu_seconds` double-count a
  shared card (CA:L44-47).

**What others have.**
- Robbie budgets in wall clock (2,400 s per pipeline); "No cross-member comparison is compute-matched"
  (EA/ATLAS.md:L268-269).
- Leon's length-generalisation used an "equal metered budget 3.9e15 FLOPs" (EA/data/experiment_map.csv:L16), so he
  already meters compute in at least one run.

### 6.7 Two more practices with direct cross-person relevance

- **Lean-alone judging with independent re-checks and negative controls.**
  - The re-score's reviewer: 4,356 proofs Lean-checked, 0 rejected, negative controls 0 / 1,200 accepted
    (EA/README.md:L71-73).
  - C5: 0 / 210,151 false rejects by the pre-filter (COEP:L38-40).
  - Others: Robbie's lean cells are † (near-equivalent). His token cells and the fork's token-era rows depend on an
    `nd_verify` with the forward-citation bug Leon fixed (EA/ATLAS.md:L36-37, L237). Charles uses strict_verify /
    old ND (EA/data/protocol_differences.csv:L11).
- **Split hygiene by renaming class** (both premise-order keys).
  - It found the textbook72 premise-swapped twin in K12 (≤ 1 per cap-12 count) (EA/README.md:L106-108).
  - The atlas flags Robbie's factorial as RL-trained on 14 of 72 textbook72 theorems (EA/ATLAS.md:L61-63).
  - Charles's release is audited disjoint from textbook72 and the RL pools (EA/MAP.md:L116).

---

## 7. Ambiguities

1. **Count of other-member experiments.** The atlas says 81 by Dan's agents and 14 by other members (EA/ATLAS.md:L15-16;
   EA/README.md:L95). Its own `experiment_map.csv` has 95 rows with owners dan-agents 57, dan-codex 9, robbie 15,
   leon 9, charles 3, chainik1125 1, dmitry 1 (derived: 66 vs 29). Excluding code / tool / data rows does not give 14
   either (derived: 21 rows have review status R or U). The reviewed README repeats 81 / 14.
2. **"41–322" range of the interface gaps** (EA/README.md:L74-75; STATE:L161). Recomputed from the atlas's own table
   means (EA/ATLAS.md:L133, L141), the cap-12 frozen dev gap is 778 − 399.5 = **+378.5** (derived). That is above 322.
   With s0/s1 only it would be 763.5 − 399.5 = +364 (derived). The 8/8 direction is unaffected; only the stated upper
   bound looks wrong. The other dev gaps (derived): +322, +263.5, +166.
3. **Frozen cap-12 best − ours on textbook72.** Three sources disagree:
   - atlas: "+0.5" (EA/ATLAS.md:L75; EA/README.md:L103);
   - claim-audit reading copy: "+0.4, MDD 7.7" (CAR:L35);
   - best-state / map row: "+1.2" (EA/MAP.md:L66; BS:L106).

   *derived:* by means 28.67 − 28.25 = 0.42; by IQM (ours 26/29/32/26 → 27.5) 28.67 − 27.5 = 1.17. The atlas's 0.5
   matches neither exactly.
4. **Cap-12 T1 recipe gap.** Four values appear:
   - atlas "+14" (EA/ATLAS.md:L76);
   - CA "+14.17 cap 12 (IQM)" (CA:L68);
   - CAR "+14.4" (CAR:L35);
   - map row "+14.2" (EA/MAP.md:L66).

   *derived:* 51.67 − 37.25 = 14.42 by means; 51.67 − 37.5 = 14.17 by IQM. So CAR and CA differ by mean vs IQM.
5. **"6–11 of 70 textbook72 problems flip"** (EA/ATLAS.md:L155, L240; EA/data/protocol_differences.csv:L6). textbook72
   has 72 problems. The number is inherited and was not re-derived (EA/README.md:L119-120).
6. **"7 of 201 textbook72 families have a k 256, Lean-alone row"** (EA/README.md:L99). The denominator (201
   "families") is not explained in the files I read.
7. **Robbie's naive model size** is "not recorded" / "size not stated; fork 3.2M class" (EA/README.md:L82-83;
   EA/data/experiment_map.csv:L55). Any per-parameter comparison with our 3.2M is assumption-laden.
8. **`robbie-r1-cot-scratchpad`** has owner `chainik1125` and model "small ND transformer (Dmitry take-home tree)"
   (EA/MAP.md:L48). It is unclear whose work it is. There are no numbers either way.
9. **Robbie's dev numbers.** They are copied from his tables, not recomputed (EA/ATLAS.md:L126-127). The README's
   recomputation line (EA/README.md:L32-33) names his factorial `passk.csv`. Per the Figure 4 caption, the holdout250
   values are what is recomputed from it; I did not open `passk.csv`. So "0 disagreements" does not cover his dev
   values.
10. **Pool of Robbie's test-time-scaling percentages.** The map row does not name it (EA/MAP.md:L101). The CSV
    protocol says holdout1177 (EA/data/experiment_map.csv:L64).
11. **P11 left in next_steps.** The paper review corrected the GRPO first-success order to "s1, then s4" (COEP:L391,
    L521). `next_steps.md` item 1 still says "(s1, s2 and s5)" with no *[review]* mark (PAPER/next_steps.md:L38-39;
    the review marks are only at L9-11, L173, L187).
12. **K_eval-set GPU classes.** capability-defs' K_eval-set divides A6000 ladder seconds by an A40 attempt cost
    (CD:L70-71). create-or-elicit restates the r8 sets with same-class costs: 28 / 26 / 24 uniform vs 22 / 21 / 14 as
    published (COE:L419-425). Any number quoted "at K_eval-set" should say which.
13. **The dropped knockout-s1 reading.** COE's Observation 5 and Interpretation still contain the knockout-s1
    "elicitation" reading, now marked dropped by C4 (COE:L357, L639). Quote COEP:L31-37, not COE:L355 or L635-638.
14. **WHERE_THINGS_ARE.md is absent on origin/dan.** Peer results after 2026-10-02 (thinking, GRPO v2, retry,
    distractors, selection) are not covered by any origin/dan file I read. The atlas stops at 2026-10-02 and STATE.md
    has no peer entries after 2026-09-25.
15. **"Reviewed" for other members' rows.** Charles's exp-00 / exp-00c and Leon's ndbench are marked R (EA/MAP.md:L80,
    L117, L134). The atlas does not say who reviewed them or under which protocol.
