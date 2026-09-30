# Contributing: tests, outputs, configs

## Running the tests

    sh ci/run_ci.sh                  # everything CI runs, ~1 min on one CPU core
    PY=/path/to/venv/bin/python sh ci/run_ci.sh

Needs Lean 4 at `~/.elan/bin/lean` (v4.34.1 in CI) and, for the smoke tests, `torch` (CPU is enough), `numpy`,
`tqdm`, `pytest`: `pip install -r ci/requirements-ci.txt`. Each test is also a plain script
(`python3 tests/test_roundtrip_judge.py`). Every step runs offline (`ND_OFFLINE=1`: no bucket uploads).

| step | file |
|---|---|
| size guard: no tracked file > 5 MB, no `.jsonl`/`.jsonl.gz`/`.pt` under `artifacts/` (also the pre-commit hook) | `ci/check_sizes.sh` |
| `artifacts/MANIFEST.jsonl` well-formed and disjoint from git; fetch checks sha256, is idempotent, re-fetches a corrupted copy | `tests/test_manifest.py` |
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

Small files are tracked; bulk files are not (run `repo-hygiene-2`, 2026-09-29). **Bulk** = `.jsonl`, `.jsonl.gz`,
`.pt`, or anything over 5 MB. Every bulk file that is not in git has a row in `artifacts/MANIFEST.jsonl`
(`path`, bucket `uri`, `bytes`, `sha256`, producing `run`) and a copy in the public bucket
`hf://buckets/dan-pandori/nd-rl/`, checked by sha256.

- **Fetch** a moved file to its own repo path, so scripts keep their paths (stdlib only, no token, idempotent):

      python3 fetch_artifacts.py artifacts/nf/                  # a run's prefix
      python3 fetch_artifacts.py ckpts/final.pt data/r1/prompts.jsonl
      python3 fetch_artifacts.py --list artifacts/r5/           # what is there, what is not

- **Publish** a run's bulk files (credential scan, upload to `<run-id>/<path>`, sha256 re-check of the bucket copy,
  manifest row, `git rm --cached`), then commit `artifacts/MANIFEST.jsonl` with the run's small files:

      python3 publish_artifacts.py <run-id> artifacts/<dir> [ckpts/<dir> ...]

  `.gitignore` already ignores the bulk kinds under `artifacts/` and `*.pt`; the 5 MB rule for other kinds is enforced
  by `ci/check_sizes.sh`, as a pre-commit hook (`sh ci/install_hooks.sh`, once per clone) and in CI.
- `ckpts/`: uploaded on save by `model.save_ckpt` (`ND_RUN_ID` must be set; `REGISTRY.md`). The take-home's
  `ckpts/stage1_abs.pt` and `ckpts/final.pt` are manifest rows: `python3 fetch_artifacts.py ckpts/`.
- `data/` is tracked except its 7 files over 5 MB (manifest rows; `python3 fetch_artifacts.py data/`).
- Instead of fetching, old content can be read from git history: every manifest row names `git_commit` and
  `git_blob` (`git show <git_commit>:<path>`). New run worktrees are sparse checkouts (`newrun`): other runs'
  `artifacts/<dir>/` are left out; add one with `git sparse-checkout add /artifacts/<dir>/`, then fetch its bulk files.
- `ARTIFACTS_INDEX.tsv` is run `repo-hygiene`'s index of the 5,997 files it untracked (xet hashes); the manifest
  supersedes it for fetching.

## Configs

Right after argparse, call `record.save_config(vars(args), out)`: it writes `<out>.args.json` (or
`<outdir>/args.json` when `out` ends in `/`) with the resolved arguments plus a `_meta` key (script, argv, run id, git
SHA, host, UTC), and every registry row the process writes names that file. No config framework: the argparse flags
are the config.

## Compute

The same `save_config` call records the process's compute (AGENT_POLICY 2026-09-29): at exit it writes registry rows
`gpu_seconds` (wall-clock × GPUs; `labels.gpu` names the card, `labels.device = cpu` on CPU), and the counters the
sampler, trainers and Lean judge fill in — `gen_tokens`, `attempts`, `actions`, `train_steps`, `train_tokens`,
`lean_checks` (texts actually sent to Lean, not cache hits; `labels.lean_s` its process-seconds). An RL driver marks its
rounds with `record.phase('sample', round=r)` and wraps a training subprocess in `with record.child('finetune', round=r):`,
so each round's sampling, fine-tune and judging are separate rows and nothing is counted twice. A new script needs no
more than `save_config`; code that does work outside the instrumented libraries adds `record.count(gen_tokens=…)` etc.
`python3 registry_merge.py --compute --q run_id=<run>` gives the per-arm table. Details, and what each metric does not
count: `REGISTRY.md` § Compute rows.

## Merging a branch that still tracks bulk files

A branch made before 2026-09-29 may still add bulk files under `artifacts/`. At merge time, on the branch:
`python3 publish_artifacts.py <run-id> artifacts/<dir>` (uploads, adds manifest rows, untracks), commit, then merge.
The manifest merges with git's union driver (`.gitattributes`). CI's size guard fails on any bulk file left tracked.
