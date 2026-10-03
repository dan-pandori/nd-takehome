#!/usr/bin/env bash
# One pod's queue for guided-tts: model seed S at cap 12 and cap 6.  plain (dumps steps) -> checker gate on this
# pod's dumps -> logical (only if the gate passed) -> structural.  Resumable: a job whose summary exists is skipped.
. pod/gt/env.sh
S=$1
run() {  # model arm [extra]
  local M=$1 A=$2; shift 2; local O=artifacts/gt/eval/${M}_s${S}_${A}
  [ -s $O.json ] && { echo "skip $O"; return; }
  echo "$(date -u +%FT%TZ) start $O"
  python3 guided_eval.py --ckpt ckpts/gt/la_T1_${M}_s${S}_r8.pt --arm $A --k 256 --seed 1 --batch 2048 --sets $SETS --out $O "$@" > artifacts/gt/logs/${M}_s${S}_${A}.log 2>&1
  echo "$(date -u +%FT%TZ) end $O rc=$?"
}
run best12 plain --dump
run best6 plain --dump
V=artifacts/gt/validate_s${S}.json
[ -s $V ] || python3 step_check_validate.py --out $V artifacts/gt/eval/best12_s${S}_plain.steps.jsonl.gz artifacts/gt/eval/best6_s${S}_plain.steps.jsonl.gz > artifacts/gt/logs/validate_s${S}.log 2>&1
if python3 -c "import json,sys; sys.exit(0 if json.load(open('$V'))['gate_passed'] else 1)"; then
  run best12 logical; run best6 logical
else
  echo "GATE FAILED s$S"; touch artifacts/gt/gate_failed_s${S}
fi
run best12 structural; run best6 structural
echo "$(date -u +%FT%TZ) QUEUE_DONE s$S"
