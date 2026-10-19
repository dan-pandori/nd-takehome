# D: RL compute relative to pretraining at frontier labs, 2024 to 2026 (brief Q3)

Screening agent D, 2026-10-19. Ledger: `D_frontier.tsv` (109 rows, 109/109 quotes verified). Grades: A primary lab
statement (A-informal = named employee/executive, marked in the ledger's location column), B paper/report, C independent
estimate with a stated method, D press/rumour/no method. DeepSeek and MiniMax reports are out of scope here (another
agent); they enter only as the secondary 3.75 % figure that Meta's ScaleRL paper quotes.

**Definitions.** *R* = RL-stage compute / pretraining compute for one model's final runs (FLOP unless stated).
Statements come in three currencies, and they are easy to confuse: (i) relative RL scale-ups ("10x o1"), which give no
*R* without the earlier model's share and base size; (ii) GPU-time or USD; (iii) **fleet shares** (share of a lab's
compute, including experiments), which are not *R*. RL GPU-time is dominated by rollout inference. In Reflection's Beam,
3.9 to 5.4 inference GPUs ran per trainer GPU, so GPU-time *R* and update-FLOP *R* can differ by about 5x.

## 1. Dated statements

"My arithmetic" marks numbers I derived; everything else is stated in the source.

| Date | Lab / source | Model | Statement (short) | Implication for RL/pretraining | Grade | claim_id |
|---|---|---|---|---|---|---|
| 2024-09-04 | Lambert (Interconnects) | lab-wide | compute allocation "pretraining — 60%, post-training — 25%, data — 10%, other — 5%" | fleet post/pre about 0.4 (my arithmetic); a research allocation, not *R* | D | D-lambert24-alloc |
| 2024-09-12 | OpenAI | o1 | performance improves with more RL train-time compute; RL constraints differ from pretraining | no figure; the chart has no axis values | A | D-oai-o1-rlscaling, D-oai-o1-constraints |
| 2025-01 | Anthropic (Amodei, A-informal) | all labs | RL-stage spend "small for all players"; "$1M instead of $0.1M"; labs scaling to "hundreds of millions and billions"; Claude 3.5 Sonnet "a few $10M's" | if the illustrative numbers are paired, reading "a few $10M's" as $20M to $50M: *R* about 0.2 to 5 % (my arithmetic, not his) | A | D-ant-amodei-rlsmall, -scaleup, -sonnet |
| 2025-01-15 | Lambert (interview) | o1 / frontier | guess: RL "10 or 20 percent of the compute budget"; o1 post-training "something like 40 percent" | budget shares, not *R* | D | D-lambert25-rl, D-lambert25-o1 |
| 2025-01-31 | Epoch (Erdil) | DeepSeek-R1 (o1-class analogue) | RL about 6.1e23 FLOP vs V3 pretraining about 3e24 | *R* about 0.2. DeepSeek's own GPU-hours give 3.75 % (next rows): a 5x disagreement | C | D-epoch-r1-rlflop, D-epoch-r1-ptflop, D-epoch-howfar-r1share |
| 2025-02-19 | xAI | Grok 3 (Think) | 10x the compute of previous SOTA; RL "at an unprecedented scale" | no RL figure | A | D-xai-grok3-10x, D-xai-grok3-rl |
| 2025-04-16 | OpenAI | o3 | "an additional order of magnitude in both training compute and inference-time reasoning" via RL | RL(o3) about 10x RL(o1). Gives *R* only with o1's *R* (undisclosed) and an equal-size base (assumed) | A | D-oai-o3-10x |
| 2025-05-09 | Epoch (You) | o1, o3 | o3 = 10x o1 (livestream chart, normalised axis); o1 and o3 RL "still below" the largest runs; Nemotron Ultra RL <1 % of pretraining; RL converges with the frontier "by 2026" | o3 RL below 1e26; trend forecast | C | D-epoch-howfar-* |
| 2025-05-09 | OpenAI (Dan Roberts, A-informal) | future o-series | "same size cake ... crush it with a giant reinforcement learning cherry" | intent: *R* well above 1; no figure | A | D-oai-roberts-cherry |
| 2025-05-22 | Anthropic (Sholto Douglas, A-informal) | o3; academic RL | o3 a "10X compute multiplier over o1"; RL spend small but "everyone ... scaling up RL"; academic RL not "anywhere comparable" to base compute | relative only; academic *R* far below 1 | A | D-ant-sholto-* |
| 2025-06-08 | SemiAnalysis | industry | RL "still in the tens of thousands of GPU domain"; "RL uses less FLOPs than pre-training" | *R* < 1 (no method) | D | D-sa-rl25-* |
| 2025-07 (arXiv 2507.06261) | Google | Gemini 2.5 | "increased the training compute allocated to RL" | relative increase, no figure | B | D-gdm-gemini25-rl |
| 2025-07-09 | xAI | Grok 4 | RL "at pretraining scale" on a 200k-GPU cluster; "over an order of magnitude more compute than had been used previously" | about 1 in words; launch slide shows RL bar about equal to the pretraining bar (seen only in Ord's reproduction) | A (slide D) | D-xai-grok4-ptscale, -10x, -slide |
| 2025-08-07 | OpenAI | GPT-5 | launch post states only "trained on Microsoft Azure AI supercomputers" | not disclosed | A | D-oai-gpt5-nofigure |
| 2025-09-11 | Epoch | GPT-4o, o1-high | pre-reasoning era: pretraining "90-99%" of training compute; o1-high RL "likely less than 10%" of GPT-4o pretraining | *R* below 0.1 for o1 | C | D-epoch-3iss-pre, -o1 |
| 2025-09-26 | Epoch (Ho) | GPT-4.5, GPT-5 | until about Sept 2024, "100x more pre-training than post-training"; GPT-4.5 about $200M pretraining vs $2M post-training; post-training soon "akin to tripling the entire compute budget" | about 0.01 before reasoning models | C | D-epoch-gpt5why-* |
| 2025-10 (arXiv 2510.13786) | Meta (ScaleRL) | R1-Zero, o3, Grok 4 | R1-Zero RL "3.75% of its pre-training compute"; more than 10x RL from o1 to o3, similar from Grok 3 to 4 | 0.0375 (GPU-hours, open model) | B | D-meta-scalerl-* |
| 2025-10-10 | Epoch | o-series 2024 | o-series post-training modelled as 1 % to 30 % of base-model compute (10th to 90th percentile); $4.5B of OpenAI's $5B 2024 R&D compute not in final runs | 0.01 to 0.3 | C | D-epoch-oai24-* |
| 2025-10-13 | Epoch | GPT-5 | early 2025 RL "maybe 1-10% of pre-training"; GPT-5 RL assumed 10 to 200 %; median total 5e25 with about 3e25 pretraining (database: about 6e25) | 0.1 to 2; medians imply about 0.7 (my arithmetic) | C | D-epoch-gpt5notes-*, D-epochdb-gpt5 |
| Epoch database (fetched 2026-10-19) | Epoch | Grok 4 | RL between Epoch's o3 estimate (10 %) and the 100 % implied by the launch slide; total about 5e26; 246M H100-hours | 0.1 to 1 (geometric mean about 0.3, my arithmetic); implies Grok 3 RL about 1 to 10 % | C | D-epochdb-grok4-*, D-epoch-grok4res |
| 2025-10-03 | Ord | first reasoning models | RL could be scaled "10 or 100" times "before even doubling" total compute | about 1 to 12 % initially (my arithmetic) | D | D-ord-infer-10or100 |
| 2025-10-20 | Ord | o1 to GPT-5 | first round about 1.01x base; o3 RL "much less" than about 1e25 pretraining ("widely believed"); GPT-5 fits a further 10x RL over o3; OpenAI, Google and Anthropic not at parity "but probably not far off" | about 0.01, then below 1, then near 1 | C/D | D-ord-rlscale-* |
| 2025-11-17 | xAI | Grok 4.1 | same large-scale RL infrastructure as Grok 4 | none | A | D-xai-grok41-infra |
| 2025-11-19 | Google (Vinyals, via aggregator) | Gemini 3 | pretraining "delivered a drastic jump" | pretraining also scaled; *R* unknown | D | D-gdm-vinyals-pretrain |
| 2025-11-25 | Sutskever (SSI; hearsay) | other labs | "based on what people say on Twitter, they spend more compute on RL than on pre-training" | above 1 (hearsay) | D | D-ilya-rl-gt-pt |
| undated | Qwen (OpenRouter description) | Qwen3-Max-Thinking | "significantly scaling ... reinforcement learning compute" | none | D | D-qwen-max-thinking |
| 2026-02-09 | Cursor | Composer 1.5 | RL scaled "20x further on the same pretrained model"; post-training compute "surpasses" base-model pretraining | above 1 (not a frontier lab; base pretrained elsewhere) | A | D-cursor-c15-ratio |
| 2026-02-13 | Anthropic (Amodei, A-informal) | — | "same scaling in RL that we saw for pre-training"; pretraining "continuing to give us gains" | both stages still scaling; no ratio | A | D-ant-amodei26-* |
| 2026-06-16 | Lambert | — | compute split "the hardest decision to get out of labs" | not disclosed | D | D-lambert26-opacity |
| 2026-08-18 | OpenAI | next generation | two-week RL pause; "largest planned frontier RL run remains on hold" | its frontier run is an RL run; no ratio | A | D-oai-pause-* |
| 2026-09-13 | SemiAnalysis | Anthropic + OpenAI fleet | pretraining share "shrunk significantly"; chart sourced to their "Tokenomics Model" | fleet, qualitative | D | D-sa-hbm-share |
| 2026-10-06 | Reflection | Beam (501B/23B) | RL on 10.5K GB300 for 4 weeks; pretraining under 4 weeks on 6,144 GB300; RL inference:training GPUs 3.9:1 to 5.4:1 | GPU-time *R* above 1.7; trainer-side GPU-time 0.27 to 0.35 of pretraining's upper bound (my arithmetic) | A | D-refl-beam-* |
| 2026-10-11 | Startup Fortune | — | "Epoch AI data shows post-training compute overtook pretraining in early 2026" | attribution unverified: no Epoch source found; matches the SemiAnalysis chart | D | D-sf-epoch-claim |
| 2026-10-18 | officechai (SemiAnalysis chart) | Anthropic + OpenAI fleet | pretraining 67 % (1Q24), 32 % (4Q25), 23 % (1Q26), 7 % (4Q26E); post-training/RL 5 %, 36 %, 42 %, 55 % | fleet post/pre about 0.07, 1.1, 1.8, 8 (my arithmetic) | D | D-oc-sa-* |

**Strongest "RL is tiny":** Amodei: RL spend "small for all players", about $1M vs tens of millions for pretraining (A-informal,
Jan 2025). Epoch: about 100x more pretraining than post-training before Sept 2024 (C). Ord: total training about 1.01x the
base model (D). Open models: R1-Zero 3.75 % (B), Nemotron Ultra <1 % (C).

**Strongest "RL at or above pretraining":** xAI's Grok 4 RL "at pretraining scale" (A, Jul 2025). Cursor's post-training
above base pretraining (A, Feb 2026; not frontier). Reflection's RL GPU-time at least 1.7x pretraining (A, Oct 2026; not
frontier). OpenAI's 2026 frontier run is an RL run (A, qualitative). SemiAnalysis fleet split of 42 % vs 23 % in 1Q26 (D).
Sutskever's hearsay (D).

## 2. Graded range for frontier *R* (RL FLOP / pretraining FLOP, flagship final runs)

| Period | Observed statements (grade) | My estimate: low to high (central) | Weakest link | Reasoning |
|---|---|---|---|---|
| 2024 (o1 era) | OpenAI: no figure (A). Amodei: RL spend small, about $0.1 to 1M (A-informal). Epoch: o-series 1 to 30 % (C), o1-high <10 % (C), post-training 1 % before Sept 2024 (C). Ord: about 1 % (D). Lambert: 10 to 40 % of budget (D, fleet) | 0.003 to 0.3 (0.01 to 0.1) | C | No lab states *R*. The A statements are relative or illustrative. Epoch's 80 % interval is the only stated method, and the open analogues (R1-Zero 3.75 %, Nemotron <1 %) sit inside it. The upper end is Epoch's 90th percentile. |
| H1 2025 | o3 about 10x o1 (A, relative). Grok 3 Think RL "unprecedented" (A). Epoch: early 2025 RL 1 to 10 % (C), o3 about 10 % (C). Ord: o3 RL much less than pretraining (D). SemiAnalysis: tens of thousands of GPUs (D) | 0.02 to 0.5 (about 0.1) | C | 10x on top of the 2024 range, on a similar-size base, gives 0.03 to 3. Epoch's and Ord's "o3 well below pretraining" caps it near 0.5. Epoch puts Grok 3's RL at about 1 to 10 %. |
| H2 2025 | Grok 4 RL "at pretraining scale" (A), slide about 1 (D via Ord), Epoch 0.1 to 1 (C). GPT-5: Epoch 0.1 to 2 (C), Ord about 10x o3 (C). Ord: big three "not far off" parity (D). Gemini 3 pretraining jump (D). Sutskever: above 1 (D). Fleet 4Q25 about 1.1 (D) | 0.1 to 2 (0.3 to 1) | D | xAI is the only lab putting RL on a par with pretraining, and the only graphic is a schematic slide. OpenAI's GPT-5 *R* is Epoch's assumption band. Google says pretraining also jumped, so *R* likely differs widely by lab. |
| 2026 | No frontier lab states *R*. OpenAI's flagship run is an RL run (A). Amodei: pretraining still gives gains (A-informal). Cursor above 1 (A, not frontier). Reflection GPU-time above 1.7 (A, not frontier). Fleet post/pre 1.8 (1Q26) to about 8 (4Q26E) (D). Epoch: RL could be the "majority" (C forecast) | 0.3 to 5 (1 to 2) | D | Fleet shares include experiments and rollout inference, so they overstate *R*. Reflection shows GPU-time *R* above 1 with trainer-side GPU-time near 0.3. New large pretrains (press-only, unverified here) would pull per-model *R* below 1. |

**Trajectory (my reading).** *R* rose about one to two orders of magnitude: about 0.01 to 0.1 in 2024, about 0.1 in early
2025, about 0.3 to 1 by late 2025 (xAI at about 1), and probably about 1 to 2 in 2026. The fleet share of post-training
went from single digits to about 40 to 55 % (D). That is the strongest quantitative 2024 to 2026 series, but it comes
from an analyst model with no stated method.

**UNVERIFIED or not found.**
- OpenAI's Dec 2024 o3 livestream: no transcript found.
- Grok 4 livestream verbal claims: no transcript; the slide is seen only in Ord's reproduction, and Epoch cites an
  archive.is copy that was CAPTCHA-blocked.
- Press claims that GPT-5.1 to 5.4 shared one base and that GPT-5.5 is a new pretrain: OpenAI's GPT-5.5 post gives no
  compute split.
- Moonshot (Kimi): no RL-share statement found. Meta: only the secondary ScaleRL figure. Qwen: qualitative only, via a
  third-party host.
- officechai's 1Q24 "5%" for post-training does not appear as a label on its own chart image; numbers were taken from
  the text only.

**Proposed citekeys** (for the note): `openaiLearningReasonLLMs2024`, `openaiIntroducingO3O4mini2025`, `xaiGrok42025`,
`amodeiDeepSeekExportControls2025`, `epochHowFarCanReasoning2025`, `epochNotesGPT5Training2025`,
`epochWhyGPT5Used2025`, `epochMostOpenAIsCompute2025`, `ordHowWellDoes2025`, `khatriArtScalingReinforcement2025`,
`xieLongLiveShort2026`, `cursorIntroducingComposer152026`, `reflectionIntroducingBeam2026`.
