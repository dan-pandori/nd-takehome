#!/usr/bin/env bash
# VPS side: poll every pod until all chains are done, a job fails, or MAXPOLL polls elapse.
# Sleeps on a pod (the VPS shell blocks foreground sleep), so it is safe to run in the background.
#   bash pod/sd/wait.sh <maxpolls> <pod>...
cd /home/dan/work/stage1-dynamics
MAX=$1; shift; PODS="$*"; SLEEPER=${PODS%% *}
for ((i=1; i<=MAX; i++)); do
  ALLDONE=1; FAIL=""; LINE=""
  for p in $PODS; do
    s=$(bash pod/sd/sync.sh $p sh 'ls artifacts/sd/*.failed 2>/dev/null | sed "s|.*/||;s|\.failed||" | tr "\n" ","; echo -n "|"; ls artifacts/sd/chain_*.done 2>/dev/null | wc -l; echo -n "|"; ls pod/sd/chains/*.sh 2>/dev/null | wc -l; echo -n "|"; for f in artifacts/sd/logs/*.log; do b=${f##*/}; b=${b%.log}; case $b in setup|smoke*|chain*|judge*) continue;; esac; [ -f artifacts/sd/$b.done ] && continue; [ -f artifacts/sd/$b.failed ] && continue; printf "%s:%s " $b "$(grep -oE "^step [0-9]+" $f | tail -1 | cut -d" " -f2)"; done' 2>/dev/null | tr -d '\n')
    IFS='|' read -r f nd nc rest <<< "$s"
    [ -n "$f" ] && FAIL="$FAIL $p:$f"
    [ "${nd:-0}" = "${nc:-1}" ] || ALLDONE=0
    LINE="$LINE  $p[$nd/$nc] $rest"
  done
  if [ -n "$FAIL" ]; then echo "FAILED$FAIL"; echo "$(date -u +%FT%TZ)$LINE"; exit 2; fi
  if [ "$ALLDONE" = 1 ]; then echo "ALL CHAINS DONE $(date -u +%FT%TZ)"; echo "$LINE"; exit 0; fi
  [ $i -lt $MAX ] && bash pod/sd/sync.sh $SLEEPER sh 'sleep 100' > /dev/null 2>&1
done
echo "$(date -u +%FT%TZ) still running:$LINE"
