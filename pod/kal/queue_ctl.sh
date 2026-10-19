#!/usr/bin/env bash
# kal-5: every read-out of the three frozen control models, in turn.
cd /workspace/nd-takehome
for s in 0 1 2; do bash pod/kal/eval_model.sh ctl_s$s ckpts/ctl/stage1_best12_s${s}_b1200.pt ctl 1024; done
