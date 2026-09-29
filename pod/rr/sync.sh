#!/usr/bin/env bash
# Push this worktree's code to a pod (podsync is hardwired to ~/nd-takehome), with .git_sha so registry rows carry the
# commit.  Pull: sync.sh <pod> pull <relpath>.   Usage: sync.sh <pod> [push | pull <relpath>]
. ~/.config/nd-rl/env; N=$1; F=~/.config/nd-rl/pods/$N; . "$F"; L=$HOME/work/results-registry
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
if [ "${2:-push}" = pull ]; then
  mkdir -p "$L/$(dirname "$3")"
  exec rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/$3" "$L/$(dirname "$3")/"
fi
git -C "$L" rev-parse HEAD > "$L/.git_sha"
[ -z "$(git -C "$L" status --porcelain -uno -- '*.py')" ] || echo "WARNING: uncommitted .py changes; .git_sha is HEAD"
rsync -rlptz --no-o --no-g --exclude .git --exclude data/ --exclude artifacts/ --exclude ckpts/ --exclude __pycache__ \
  -e "ssh $SSHO -p $POD_PORT" "$L/" "root@$POD_IP:/workspace/nd-takehome/"
