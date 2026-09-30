#!/usr/bin/env bash
# Wait for this pod's running Stage-1 chain (stage1.sh) to finish, then run seed.sh (which skips finished steps).
# Usage: bash pod/bs/relaunch.sh <cap> <seed>
source pod/bs/env.sh
while pgrep -f 'pod/bs/stage1.s[h]' >/dev/null; do sleep 20; done
bash pod/bs/seed.sh $1 $2
