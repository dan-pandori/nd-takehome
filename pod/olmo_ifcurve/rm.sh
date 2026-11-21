#!/usr/bin/env bash
# rm.sh <pod>: podrm, and if it fails (REST outage: `runpodctl pod remove` cannot resolve rest.runpod.io) the same
# bookkeeping with the GraphQL-based `runpodctl remove pod`, verified with `runpodctl get pod`.
N=$1; F=~/.config/nd-rl/pods/$N
podrm "$N" && exit 0
[ -f "$F" ] || exit 0
. "$F"
timeout 60 runpodctl remove pod "$POD_ID" > /dev/null 2>&1
if timeout 60 runpodctl get pod 2>/dev/null | grep -q "$POD_ID"; then echo "rm.sh $N: GraphQL delete failed too; registry kept"; exit 1; fi
H=$(awk -v a="$(date -u +%s)" -v b="$(date -u -d "$CREATED" +%s)" 'BEGIN{printf "%.4f",(a-b)/3600}')
echo "$(date -u +%FT%TZ) ${RUN:-olmo-ifcurve} $N $H $(awk -v h="$H" -v r="${RATE:-5.29}" 'BEGIN{printf "%.2f",h*r}') ${GPU:-}" >> ~/podhours.log
rm -f "$F"; echo "removed $N ($POD_ID) over GraphQL (${H}h)"
