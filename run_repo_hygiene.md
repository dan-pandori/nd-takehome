# Run repo-hygiene (proposal 15 §6)

CI smoke models (114 k parameters, `lean_seq`, from scratch on a 150-proof fixture) only show that code runs.

| expected (pre-registered) | outcome |
|---|---|
| 0 lost files | **0 lost**: 5,992 / 5,992 files verified in the bucket by size and xet hash (`repo-hygiene/git_tip/`); 20 / 20 random downloads match their git blob SHA; negative control flags 2 / 2 corrupted entries |
| 60–90 % of files already at their run path | **43 %** (2,557); 1,454 more had the same content elsewhere; **1,981 files (2.89 GB) were in no bucket path** and were uploaded first. (mostly take-home `p2`/`p3`). Expectation wrong |
| 4,159,751,936 bytes removed from the tip | yes; the tip is now 549 files, 236 MB |
| fresh non-sparse worktree 200–280 MB | **227 MB** (< 300 MB) |
| CI green on `dan`, red on a broken commit | green in a clean HOME + venv (fresh Lean 4.34.1, torch 2.8 CPU), 59 s; red on `ci-broken` (`78770822`, decode drops `.2`): 5 failures |
| CI on GitHub, < 10 min | **not shown — deviation.** The VPS token lacks the `workflow` scope; GitHub refuses the file. It ships as `ci/ci.yml`; `ci/install_workflow.sh` installs it (QUESTIONS.md) |
| configs universal | 4 scripts wrote `args.json` before; now all 60 with `--out`/`--outdir` call `record.save_config`; rows name the file; CI enforces it |

Sources: `artifacts/repo-hygiene/` (inventories, listings, CI logs),
`hf://buckets/dan-pandori/nd-rl/repo-hygiene/artifacts/repo-hygiene/`; `ARTIFACTS_INDEX.tsv`. No pods; $0.
