#!/usr/bin/env bash
# ds-rendering helpers (worktree ~/work/ds-rendering). Usage:
#   bash pod/dsr/sync.sh <pod>                  push code + data + the two control Stage-1 ckpts
#   bash pod/dsr/sync.sh <pod> pull <relpath>   pull a path from the pod into the worktree (into its parent dir)
#   bash pod/dsr/sync.sh <pod> push <relpath>
#   bash pod/dsr/sync.sh <pod> pullall          pull artifacts/dsr/
#   bash pod/dsr/sync.sh <pod> pullckpt         pull ckpts/dsr/ and ckpts/ladder/
. ~/.config/nd-rl/env; N=$1; shift; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
W=/home/dan/work/ds-rendering
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"
case "${1:-code}" in
  pull) mkdir -p "$W/$(dirname "$2")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/$2" "$W/$(dirname "$2")/" ;;
  push) ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/$(dirname "$2")"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/$2" "$R/$2" ;;
  # pullall writes into artifacts/dsr/<pod>/ so two pods can never overwrite each other's files (upload-staging trap)
  pullall) mkdir -p "$W/artifacts/dsr/$N"; exec rsync -rlptz --no-o --no-g --exclude 'mix_*.jsonl' -e "ssh $SSHO -p $POD_PORT" "$R/artifacts/dsr/" "$W/artifacts/dsr/$N/" ;;
  pullckpt) mkdir -p "$W/ckpts/dsr"; exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$R/ckpts/dsr/" "$W/ckpts/dsr/" ;;
  code)
    rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ --exclude .venv -e "ssh $SSHO -p $POD_PORT" "$W/" "$R/"
    ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "mkdir -p /workspace/nd-takehome/{data/ladder,data/p2,data/r3_1,ckpts/ladder,ckpts/dsr,artifacts/dsr/logs,targets}"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/targets/" "$R/targets/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/ckpts/dsr/stage1_a1_seq_s0.pt" "$W/ckpts/dsr/stage1_a1_seq_s1.pt" "$R/ckpts/dsr/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/transfer.jsonl" "$R/data/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/ladder/rl_targets.jsonl" "$W/data/ladder/transfer.jsonl" "$R/data/ladder/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/r3_1/depth3_req.jsonl" "$W/data/r3_1/depth3_req_transfer.jsonl" "$R/data/r3_1/"
    rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$W/data/p2/heldout.jsonl" "$W/data/p2/targets_depth3.jsonl" "$W/data/p2/transfer_depth3.jsonl" "$W/data/p2/targets_reductio_req.jsonl" "$W/data/p2/train_depth3_f0_a1.jsonl" "$R/data/p2/"
    ;;
esac
