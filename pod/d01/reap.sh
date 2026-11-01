#!/usr/bin/env bash
# Pull one pod's results into THIS worktree without touching create-or-elicit's tracked files (its artifacts/coe/logs/prune.log
# and la_ko_s1/args.json share names with this run's), then, with --rm, check the bucket holds the pod's checkpoints and delete
# the pod.  Pod logs go to artifacts/coe-dose01/pod_logs/<pod>/; knockout s1 brings back only rounds 25-32 and args_r25-32.json.
# Never pulls found_*, mix_*, dump/ (they are in the bucket).  Usage: pod/d01/reap.sh <pod> [--rm]
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F" 2>/dev/null
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
R="root@$POD_IP:/workspace/nd-takehome"; W=/home/dan/work/coe-dose01
rs() { rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "$@"; }
mkdir -p $W/artifacts/coe/rounds $W/artifacts/coe/eval $W/artifacts/coe/ladder $W/artifacts/coe-dose01/pod_logs/$N
ok=1
rs $R/artifacts/coe/rounds/ $W/artifacts/coe/rounds/ || ok=0
rs --include='*dose01*' --include='r32_ko_s1_*' --exclude='*' $R/artifacts/coe/eval/ $W/artifacts/coe/eval/ || ok=0
rs $R/artifacts/coe/logs/ $W/artifacts/coe-dose01/pod_logs/$N/ || ok=0
rs --exclude='diag/' $R/artifacts/coe-dose01/ $W/artifacts/coe-dose01/ || ok=0
rs $R/artifacts/coe-dose01/diag/ $W/artifacts/coe-dose01/diag/ 2>/dev/null
for d in $(ssh $SSHO -p $POD_PORT root@$POD_IP "ls /workspace/nd-takehome/artifacts/coe/ladder/"); do
  case $d in
    la_dose01_s*) rs --exclude='found_*' --exclude='mix_*' --exclude='relabelled_*' $R/artifacts/coe/ladder/$d $W/artifacts/coe/ladder/ || ok=0;;
    la_ko_s1) rs --include='la_ko_s1/' --include='round_2[5-9].json' --include='round_3[0-2].json' --include='args_r25-32.json' \
                 --exclude='*' $R/artifacts/coe/ladder/$d $W/artifacts/coe/ladder/ || ok=0;;
  esac
done
git -C $W status --short -- artifacts/coe | grep -v '^??' && { echo "REAP $N: a tracked file changed — inspect before anything else"; ok=0; }
echo "reap $N: pulled ok=$ok $(date -u +%FT%TZ)"
if [ "$2" = --rm ] && [ $ok = 1 ]; then
  n=$(timeout 300 hf buckets list hf://buckets/dan-pandori/nd-rl/coe-dose01/ckpts/coe/ladder --json 2>/dev/null | grep -o '"path"' | wc -l)
  echo "bucket coe-dose01/ckpts/coe/ladder: $n checkpoints"
  podrm $N
fi
