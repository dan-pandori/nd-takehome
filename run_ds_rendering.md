# ds-rendering — does the Lean rendering change what a from-scratch model learns?

**Question.** Proofs, model, schedule and pools fixed; only the *Lean rendering* varies. Does that change held-out
accuracy by length and RL readiness — and is the **"cap + 1" horizon a property of the text, or of the ND proof's
structure?**

**Setup.** Five renderings of the *same* 155,000 ND records (cap 6, no depth-3 proofs): **C0** `lean_seq` (control),
**R1** no premise re-statement, **R3** formula-free `have`s, **R2** `intro` boxes, **R4** bare-`fun` boxes
(addendum 1). 3.2M from-scratch models, 2 seeds full-plan, 6 through Stage-1. A sample counts only if **Lean 4.34
accepts the literal text and `nd_verify` the denoted ND proof** — 83,513 counted proofs, re-checked, zero
rejections.

## No rendering buys RL readiness — and the early metrics point the wrong way

| depth-3 solved | frozen dial | EI dial, 4 rounds | **ladder, 8 rounds** (/2,285) |
|---|---:|---:|---:|
| **C0** control | 0.324 | **0.657** | **963** |
| R4 bare-`fun` | 0.362 | 0.635 | 833 |
| **R2** `intro` | **0.406** | 0.615 | **729** |

At the base, untyped-binder arms beat the control. Expert iteration **compensates**: corr(frozen,
EI − frozen) = **−0.871**; the arms converge (sd 0.045 → 0.024). By the 8-round ladder **the control is above every
arm on both seeds**; R2 — best on Stage-1 depth-3 *and* the frozen dial — is **worst**, ×0.757.
**A rendering picked on a Stage-1 number would be picked exactly wrong.**

## The horizon is not text length

**R1 writes the shortest text (−21 %) and sits below the control everywhere** — 7-line pass@16 ×0.70/×0.78, every
premise count, frozen, EI and ladder. The pre-registered falsifier wanted a lower base rate **and** a larger
EI − frozen; R1's is *smaller* on both seeds. **The horizon belongs to the ND proof's structure.** In distribution,
the five span **2.28 pp**.

## Lean alone is not a sufficient checker

Over **16.3M** pairs they disagree **2,208 times, always Lean being too permissive** (`nd2lean.py`'s own `BOTE` = `.elim`,
resolving to `Not.elim`); Lean **never once** caught what `nd_verify` missed. The conjunction is load-bearing, and
**R3 is fooled ~9× as often as the control**.

## What I got wrong

That R2's box removes the seed lottery: a 24-model sweep put its sd at **0.310, second largest**. And that EI adds
a constant — true of two arms, false across five.

![lengths](figures/ds_rendering_lengths.png)
![readiness](figures/ds_rendering_readiness.png)
