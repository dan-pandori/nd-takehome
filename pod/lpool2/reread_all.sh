#!/usr/bin/env bash
# long-pool-2 read-out: 12 checkpoints on the new pool (tag new) and the calibration file (tag cal), max_steps 96.
P="new:data/ladder/transfer_long2.jsonl cal:data/ladder/transfer_long2_calib.jsonl"
for s in 0 1 2 3; do LF=L_lb bash pod/lpool2/reread.sh ckpts/sc12/ladder/la_T1_SN12_s${s}_r8.pt T1_SN12_s$s $P; done
for s in 0 1 2 3; do LF=L_lb bash pod/lpool2/reread.sh ckpts/sc12/stage1_SN12_s$s.pt stage1_SN12_s$s $P; done
for s in 0 1; do LF=L_lb bash pod/lpool2/reread.sh ckpts/se/la_T1_SN_s${s}_r8.pt T1_SNv2_s$s $P; done
for s in 0 1; do WP=1 LF=L_lb bash pod/lpool2/reread.sh ckpts/ladder/la_T1_K12_s${s}_r8.pt T1_K12_s$s $P; done
