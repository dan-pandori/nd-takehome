#!/bin/sh
R=~/review/rl-from-ckpt; P=~/venv-cpu/bin/python; cd $R/review_rfc
$P score.py ck/rc_best12_s0_p1600_r8.pt $R/artifacts/rfc/targets/targets_s0_p1600.jsonl @rv/pick_p1600.txt rv/myscore_c8_s0_p1600.jsonl
$P score.py ck/rc_best12_s0_pend_r8.pt $R/artifacts/rfc/targets/targets_s0_p1600.jsonl @rv/pick_pend.txt rv/myscore_c8_s0_pend.jsonl
echo SCORE_DONE
