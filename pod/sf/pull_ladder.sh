#!/usr/bin/env bash
# Pull one ladder directory without its fine-tune mixes (in the bucket).  Usage: pod/sf/pull_ladder.sh <pod> <la_name>
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
mkdir -p /home/dan/work/state-frontier/artifacts/sf2/$2
exec rsync -rlptz --no-o --no-g --exclude 'mix_*' --exclude 'found_[0-9]*' -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/sf2/$2/" "/home/dan/work/state-frontier/artifacts/sf2/$2/"
