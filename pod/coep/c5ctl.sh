#!/usr/bin/env bash
# C5 harness control (not pre-registered): after C5, the same checker on 400 in-loop-accepted texts of the same dump,
# with their own theorem (expect all accepted) and with another row's theorem (expect all rejected).
source pod/coep/env.sh
export LEAN_BIN=$HOME/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean
until [ -e artifacts/coe_paper/LANE_E_DONE ]; do sleep 20; done
python3 paper/scripts/c5_control.py data/coe_paper/dump_ko_s1.jsonl.gz artifacts/coe_paper/c5/control_ko_s1.json \
  > artifacts/coe_paper/logs/c5_control.log 2>&1 || echo "C5 CONTROL FAILED"
up artifacts/coe_paper/c5
echo "=== C5 control done $(date -u +%FT%TZ)"; touch artifacts/coe_paper/C5CTL_DONE
