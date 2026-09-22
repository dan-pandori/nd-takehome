# Run lean-only — Lean as the only checker; term size beside lines; free-form terms vs the `have` fragment (proposal 9)

**Phase 1 done as specified. Phase 2: free-form terms are worse in distribution (E1, E2 wrong in both seeds), not better on the depth-3 base rate (E4 wrong), reach the same ladder `L*` (11 / 11 lines, 8 / 8 term size) from a weaker base, and show nothing the fragment lacks (E10). The fragment stays; one fragment seed reached line-`L*` 12.** Numbers: `numbers.md` § lean-only.

![results](figures/lean_only.png)

**Phase 1.** `lean_check.py`: elaborates without error, axioms ⊆ {propext, choice, Quot.sound}, every constant of the elaborated term on the And/Or/Not/False/Iff + `byContradiction` allowlist; `term_size` = inference nodes. 33 / 33 hand-written cases; **253,397 / 253,397** pool proofs agree with `nd_verify`; 0 / 4,012 corrupted proofs accepted; the 460 lean-format texts split 206 / 254 exactly by kind; 82 proofs / process-s. Pools relabelled with `ts_minlen` (Spearman with `L_true` 0.60, not ≥ 0.8). One bug caught before any sampler ran: Lean's parse-error recovery closes a truncated `( fun a => ( fun b => Or.inl` and accepts it — any error on the theorem's lines now rejects.

**Phase 2** (two Stage-1 seeds per format; reward = `lean_check`; s0 / s1):

| prediction | fragment | free-form | verdict |
|---|---|---|---|
| E1 held-out greedy (free ≥ frag + 0.03) | 0.938 / 0.953 | 0.918 / 0.906 | **wrong**, 2–5 pp worse |
| E2 transfer pass@16 (free ≥ 0.60) | 0.600 / 0.647 | 0.446 / 0.427 | **wrong**, 15–22 pp worse |
| E3 tokens per proof, held-out / ladder | 81 / 198 | 6.6 / 20.3 | 0.1×; misses "≤ 20" by 0.3 |
| E4 depth-3 base rate, pass@2,000 (free ≥ frag + 0.05) | 0.283 / 0.373 | 0.331 / 0.226 | **wrong**, inside seed spread |
| E6 depth-3 EI acquisition r8 (frozen) | 0.466 / 0.478 (0.214 / 0.338) | 0.473 / 0.508 (0.276 / 0.146) | mixed: +0.25 / +0.14 vs +0.20 / +0.36 |
| E7 ladder `L*` lines (11 / 11) | 11 / **12** (22 theorems ≥ 11, 6 at 12) | 11 / 11 (16 ≥ 11) | fragment reaches 12 |
| E8 `L*` term size (free ≥ frag) | 8 / 9 | 8 / 8 | **wrong** in seed 1 |
| E9 frozen `L*` lines (10 / 10) | 10 / 10 | 10 / 9 | free-form 9 once |
| E10 new pattern from f = 0 | – | none (depth4 0.02–0.03 both) | held |
| E11–E13 record; converter; solo round | 45,396 / 45,396 re-accepted; its text proofs are ND-formality texts | 2 of the 151 text proofs in the analysed pools still undenoted after a binder-name fix; 42 vs 160 s | held |

**Reading.** Without `have` lines the model has no per-step formula to condition on: the fragment is a chain of thought, the term is the answer. The free-form base is weaker everywhere (ladder frozen 157 / 108 solved vs 286 / 386), yet EI takes it to `L*` 11 / 11 and 953 / 936 transfer theorems (fragment 895 / 1,069): RL amplifies a weaker base by more, and nothing new appears. Term size orders the arms as lines do, more coarsely.

**Caveats.** ≈ 12.3 pod-hours; 4 h of 36. Five Stage-1 checkpoints were lost with their pods and retrained with the same seeds for the bucket; EI checkpoints not kept. `ts_minlen` is an upper bound. This run's fragment beats proposal 8's (0.938 / 0.953 vs 0.936; pass@16 0.600 / 0.647 vs 0.571): renderer fix, reward, seed — not separated.
