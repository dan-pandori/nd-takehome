#!/usr/bin/env bash
# ds-composition pod helpers (worktree ~/work/ds-composition; ~/bin helpers address ~/nd-takehome, so this wrapper rsyncs the worktree).
#   bash pod/dsc/w.sh <pod> sync                 push code (no data/artifacts/ckpts) + targets + pools + control ckpts
#   bash pod/dsc/w.sh <pod> push <relpath>       push a worktree path (into its parent dir on the pod)
#   bash pod/dsc/w.sh <pod> pull <relpath>       pull a pod path into the worktree (into its parent dir)
#   bash pod/dsc/w.sh <pod> sh '<cmd>'           run a command in /workspace/nd-takehome
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/ds-composition
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
RS() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
case "${1:-sync}" in
  pull) mkdir -p "$W/$(dirname "$2")"; RS "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; RS "$W/$2" "$R/$(dirname "$2")/" ;;
  sh) shift; ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && $*" ;;
  sync)
    RS --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv --exclude figures/ "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/ladder,data/p2,data/r3_1,data/dsc,ckpts/lf,ckpts/dsc,ckpts/ladder,artifacts/dsc/logs,targets}"
    RS "$W/targets/validation_36.jsonl" "$R/targets/"
    RS "$W/data/ladder/rl_targets.jsonl" "$W/data/ladder/transfer.jsonl" "$R/data/ladder/"
    RS "$W/data/p2/heldout.jsonl" "$W/data/p2/targets_depth3.jsonl" "$W/data/p2/transfer_depth3.jsonl" "$W/data/p2/targets_reductio_req.jsonl" "$W/data/p2/transfer_reductio_req.jsonl" "$R/data/p2/"
    RS "$W/data/r3_1/depth3_req.jsonl" "$W/data/r3_1/depth3_req_transfer.jsonl" "$R/data/r3_1/"
    RS "$W/data/dsc/targets_depth3_sub250.jsonl" "$R/data/dsc/"
    RS "$W/ckpts/lf/stage1_a1_seq_s0.pt" "$W/ckpts/lf/stage1_a1_seq_s1.pt" "$R/ckpts/lf/"
    ;;
esac
