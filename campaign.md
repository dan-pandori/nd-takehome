# Does RL create capabilities, or elicit rare ones? — campaign answer

**Both, and the measurements say which is which.** Expert iteration against the verifier amplifies behaviour that
the pretrained model already assigns non-negligible probability to, *and* it composes one kind of pattern the
pretraining data never contained — a deeper nesting of an operation the model already performs — but it does not
invent rule sequences it has never seen, and it does not learn patterns the reward never requires.

- **Phase 1 (existing run).** Per theorem, three quarters of what RL solved is elicitation: the frozen Stage-1 model
  solves 57% of the transfer set at the same 512-sample budget and 66% at 10⁴. The remaining quarter (348 of 1,411
  RL-solved theorems) is unreachable by sampling at 10⁴, and every 9-line RL proof has base probability < 10⁻³⁰. The
  log-probability estimate is calibrated to 0.00 nats against 10⁴ real samples, so "unreachable" is measured, not
  guessed. The novelty is concentrated in one line: the opening of a third nested box.
- **Phase 2 (controlled coverage).** With **zero** depth-3 proofs in pretraining, RL still solves 27–34% of depth-3
  targets *with* depth-3 proofs, the same as at 10⁻³ or 10⁻¹ coverage; the frozen f = 0 control produces none, the
  base model finds none in 3·10⁶ samples, and every found proof sits below 10⁻⁵ under the base model. That is
  composition. Derived-ORE behaves as pure amplification: ~0 at f = 0 (a degenerate form the base already emits at
  ~10⁻⁴), 22% at f = 10⁻⁴ (16 proofs in 155k), flat after. Reductio never moves, at any f, because the targets do not
  require it.
- **Phase 3 (textbook curriculum).** Textbook targets lift only schemata with a foothold (contraposition,
  consequentia mirabilis, export); validation-36 `> 6` goes 0 → 1/24, or 2/24 with precursor injection, which buys
  the one theorem (export, p ≈ 10⁻⁸) that sampling cannot reach. De Morgan and distribution stay at 0.

**Rule of thumb from this data:** RL crosses zero pretraining coverage when the missing pattern is a structural
repetition of a learned move (one more box), not when it is a new rule sequence (reductio) or a shape whose short
instances do not exist (non-degenerate derived ORE). Budget at which the distinction holds: 512–10⁵ samples.

![phase 1](figures/phase1_reachability.png)
![phase 2](figures/phase2_acquisition.png)
![phase 3](figures/phase3_schemata.png)

Details: `phase1.md`, `phase2.md`, `phase3.md`; every number in `numbers.md`; chronology and judgment calls in `log.md`.
