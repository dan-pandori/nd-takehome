#!/usr/bin/env bash
# Literal-text Lean re-check (lean_check, free-form path) of every long-pool prompt a model solved, + 300 rejected texts
# as a negative control.  Usage: bash pod/sc12/recheck.sh <label, e.g. T1_SN12_s0>
source pod/sc12/env.sh; L=$1; mkdir -p artifacts/sc12/recheck
python3 sc12_recheck.py --dumps artifacts/sc12/dump/rr_${L}__rr600.jsonl artifacts/sc12/dump/rr_${L}__ge17.jsonl --out artifacts/sc12/recheck/$L.jsonl
python3 lean_check.py --texts artifacts/sc12/recheck/$L.jsonl --out artifacts/sc12/recheck/${L}_lean.jsonl --workers 32 > artifacts/sc12/recheck/${L}_lean.log 2>&1
