#!/bin/sh
# The CI test suite (run repo-hygiene): the same steps .github/workflows/ci.yml runs, runnable locally.
#   PY=/path/to/python sh ci/run_ci.sh        # needs torch (CPU), numpy, pytest, tqdm, and Lean at ~/.elan/bin/lean
# Every step is CPU-only, offline (ND_OFFLINE=1: no bucket uploads) and writes only under a temp dir or ignored paths.
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python3}
export ND_OFFLINE=1 ND_REGISTRY_SYNC=0 PYTHONDONTWRITEBYTECODE=1
TMP=$(mktemp -d); export ND_REGISTRY_DIR=$TMP/registry
T0=$(date +%s)
step() { name=$1; shift; t=$(date +%s); echo "::group::$name"; "$@"; echo "::endgroup::"; echo "ok  $name ($(( $(date +%s) - t ))s)"; }

step "size guard: no tracked file > 5 MB, no bulk kind under artifacts/ (ci/check_sizes.sh)" sh ci/check_sizes.sh
step "artifacts/MANIFEST.jsonl well-formed; no manifest path tracked" $PY tests/test_manifest.py
step "tokenizer + lean_seq round-trips, Lean judge on a fixed sample" $PY tests/test_roundtrip_judge.py
step "lean_check selftest (free-form Lean allowlist: Not.elim and negatives)" $PY lean_check.py --selftest
step "Lean-only judge (no nd_verify on any judging path)" $PY tests/test_lean_only_judge.py
step "lean-prefilter soundness" $PY tests/test_lean_prefilter.py
step "state-env round-trip and replay" $PY tests/test_state_env.py
step "relabel marker" $PY -m pytest -q tests/test_relabel_marker.py
step "results registry" $PY tests/test_registry.py
step "every script with --out/--outdir records its config (record.save_config)" $PY tests/test_configs.py
step "50-step CPU training + sampler smoke" $PY tests/test_smoke_train_sample.py
rm -rf "$TMP"
echo "CI PASS ($(( $(date +%s) - T0 ))s)"
