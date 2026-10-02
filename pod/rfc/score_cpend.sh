#!/usr/bin/env bash
# Reference proofs under the pend replay-only controls' r8 (x_ctrl for the end arm).  Usage: bash pod/rfc/score_cpend.sh <seed>
source pod/rfc/env.sh
S=$1; C=rc_best12_s${S}_pend; fetch rl-from-ckpt/ckpts/rfc/control/${C}_r8.pt ckpts/rfc/control/${C}_r8.pt
echo "s${S}_pend_c8 ckpts/rfc/control/${C}_r8.pt" > artifacts/rfc/score/ckpts_cpend_s$S.txt
md5sum ckpts/rfc/control/${C}_r8.pt > artifacts/rfc/score/ckpts_cpend_s$S.md5
python3 tj_score.py --targets data/rfc/ref_targets.jsonl --ckpts artifacts/rfc/score/ckpts_cpend_s$S.txt --out artifacts/rfc/score/cpend_s$S || exit 1
up artifacts/rfc
echo "=== score cpend s$S done $(date -u +%FT%TZ)"
