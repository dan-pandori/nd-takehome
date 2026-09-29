# Contributing: tests, outputs, configs

## Running the tests

    sh ci/run_ci.sh                  # everything CI runs, ~1 min on one CPU core
    PY=/path/to/venv/bin/python sh ci/run_ci.sh

Needs Lean 4 at `~/.elan/bin/lean` (v4.34.1 in CI) and, for the smoke tests, `torch` (CPU is enough), `numpy`,
`tqdm`, `pytest`: `pip install -r ci/requirements-ci.txt`. Each test is also a plain script
(`python3 tests/test_roundtrip_judge.py`). Every step runs offline (`ND_OFFLINE=1`: no bucket uploads).

| step | file |
|---|---|
| nothing tracked under `artifacts/` | `ci/run_ci.sh` |
| token-format and `lean_seq` render ↔ parse round-trips; Lean judge on 150 gold proofs, the canonical `Not.elim` example, 450 negatives | `tests/test_roundtrip_judge.py`, fixture `tests/fixtures/proofs150.jsonl` |
| free-form Lean allowlist (`lean_check`, 39 cases incl. `Not.elim`, `sorry`, `simp`, library lemmas) | `lean_check.py --selftest` |
| no `nd_verify` on any judging path | `tests/test_lean_only_judge.py` |
| lean-prefilter soundness | `tests/test_lean_prefilter.py` |
| state-env round-trip, replay, Lean vs renderer | `tests/test_state_env.py` |
| relabel marker; results registry | `tests/test_relabel_marker.py`, `tests/test_registry.py` |
| every script with `--out`/`--outdir` records its config | `tests/test_configs.py` |
| 50 CPU training steps; sampler → `lean_seq` decode → Lean gate on a memorised toy model | `tests/test_smoke_train_sample.py` |

CI (GitHub Actions, `ci/ci.yml` → `.github/workflows/ci.yml`) runs the same script on pushes to `dan` and `ci-*`
and on pull requests. Installing the workflow needs a token with the `workflow` scope: `sh ci/install_workflow.sh`.
Test fixtures live in `tests/fixtures/`, never in `artifacts/`.

## Where outputs go

- `artifacts/<run>/` is **not tracked** (since run `repo-hygiene`, 2026-09-29). Write a run's outputs there and
  upload them to `hf://buckets/dan-pandori/nd-rl/<run>/artifacts/` as you go (`hf buckets sync`). `numbers.md` names
  the bucket path of every source file; reviewers pull from the bucket.
- `ckpts/`: uploaded on save by `model.save_ckpt` (`ND_RUN_ID` must be set; `REGISTRY.md`).
- `data/` stays tracked (≈ 230 MB). Large generated pools go to the bucket, not git.
- The 5,992 files that were tracked under `artifacts/` until `3bfdec15` are listed in `ARTIFACTS_INDEX.tsv`; each is at
  `hf://buckets/dan-pandori/nd-rl/repo-hygiene/git_tip/<path>` (verified by size and xet hash), and in git history:
  `git show 3bfdec15:<path>`.

## Configs

Right after argparse, call `record.save_config(vars(args), out)`: it writes `<out>.args.json` (or
`<outdir>/args.json` when `out` ends in `/`) with the resolved arguments plus a `_meta` key (script, argv, run id, git
SHA, host, UTC), and every registry row the process writes names that file. No config framework: the argparse flags
are the config.

## Merging a branch that still tracks artifacts

Branches made before 2026-09-29 track files under `artifacts/`. Merging one into `dan` re-adds any artifact file it
created (and conflicts, modify/delete, on any it changed). Before the merge, on the branch: upload its
`artifacts/<run>/` to the bucket, then `git rm -r --cached artifacts/`, then commit. CI's first step fails if
anything under `artifacts/` is tracked.
