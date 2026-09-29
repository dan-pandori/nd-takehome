# Run repo-hygiene-2 — small files back, manifest, fetch/publish, size guard

No pods and no model. CI's smoke models (114 k params, `lean_seq`, from scratch on the 150-proof fixture) only show that code runs.

| expected (pre-registered) | outcome |
|---|---|
| 2,053 manifest rows, 0 sha256 mismatches, 0 lost | **2,053 rows** (+1 published by the demo), all re-hashed from full bucket downloads: 2,054 ok. Of the 6,006 files untracked by either run: 3,953 tracked again with the same blob, 2,053 in the manifest, **0 lost** (`rh2_acceptance.py`; a falsified check shows 1 lost) |
| fetch reproduces a run's numbers | the pre-registered `lean-prefilter` choice could not test it (its inputs were never in git): deviation. Instead, `noise-floor`'s `nf_analysis.py` gave output **byte-identical** to the tracked `summary.json` after the fetch (365 files, 24 s). Idempotent; a corrupted copy is re-fetched |
| fresh worktree 120–170 MB | **147.4 MB** |
| guard red on 6 MB | hook, `check_sizes.sh`, `run_ci.sh` and GitHub Actions all **red** |
| CI green on `dan` | Actions **green**: `ci-rh2-green`, then `dan` after the merge (run 36594025125); fresh `dan` worktree 148.1 MB |
| credential scan 0 hits | **0 hits**: 6,023 objects under `repo-hygiene/` and `repo-hygiene-2/` (4.33 GB) plus the 1 file `publish_artifacts.py` uploaded; 4 planted fakes and 1 real-value copy found |

Found on the way: `cf5924e2` did not narrow CI's guard, although its message says it did. `check_sizes.sh` replaces that guard.

**repo-hygiene quarantine:** (1) `TEST_RUN_DONE` is tracked (sha256 `aa174582…`, unchanged), and so are all other small files; (2) the CI guard is "> 5 MB or bulk kind"; (3) the rest of the amendment is done (see above); it is recorded in `log.md`; (4) re-review: this run's reviewer.

## Draft for `AGENT_POLICY.md` (Artifacts)

> Runs publish bulk files instead of committing them: `python3 publish_artifacts.py <run-id> artifacts/<dir> …` (bulk = `.jsonl`, `.jsonl.gz`, `.pt`, > 5 MB). Commit the small files and `artifacts/MANIFEST.jsonl`. A pre-commit hook and CI refuse any tracked file > 5 MB. At merge time, the librarian publishes any bulk file a run branch still adds.

Sources: `artifacts/repo-hygiene-2/`, `hf://buckets/dan-pandori/nd-rl/repo-hygiene-2/`.
