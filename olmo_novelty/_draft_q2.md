### ProRL's correlation on our data

`olmo_novelty/correlation.py` (pre-registered, 664aaa93), olmo-ifomega's fixed phase: `dpo` 16 draws per prompt,
each RL checkpoint 8, strict grade. x = `dpo` pass@1 on half of its draws; gain = RL pass@1 minus `dpo` pass@1 on the
other half (the split stops the gain sharing x's noise).

| unit (n) | model | Spearman ρ [95 %] | same draws | random-pairing null |
|---|---|---|---|---|
| IFBench prompt (218), pass@1 — **P1** | `s2300` | **−0.50 [−0.60, −0.40]** | −0.54 | −0.66 |
| IFBench prompt, pass@8 | `s2300` | −0.67 [−0.76, −0.57] | −0.77 | −0.71 |
| IFBench constraint type (47), pass@8 — ProRL's unit | `s2300` | −0.80 [−0.90, −0.62] | −0.88 | – |
| IFBench prompt, pass@1 | `s0750` / `s0100` | −0.25 / +0.01 | −0.27 / −0.03 | −0.62 / −0.63 |
| IFEval prompt (150), pass@1 | `s2300` | −0.65 [−0.78, −0.50] | −0.79 | −0.75 |

Observed: the pattern is there. `s2300`'s mean pass@1 gain is 0.54 where `dpo`'s half-sample rate is 0 and 0.00
where it exceeds 0.75; 69 % of the total gain (59.6 of 85.8 prompt-units) sits on the 107 prompts where `dpo` has 0
of 16, 34 % on the 49 strict-reach prompts. Six of seven pre-registered expectations hold; the per-type ρ is slightly
stronger than predicted (−0.80 against ≥ −0.80).

Our interpretation: the pattern does not separate creation from sharpening. Shuffling RL's per-prompt rates across
prompts, so that RL's success is unrelated to the start's, gives a *more* negative ρ (−0.66) than observed, because a
gain defined as a difference of bounded rates falls as the start rises whatever RL does. The observed ρ is weaker
than that null because RL's rate rises with the start's (ρ = +0.50). ProRL reports its correlation without a
coefficient, a test or such a null [EX-6]. What carries our creation claim is the reach count under symmetric
confirmation and a hand gate, not this correlation.
