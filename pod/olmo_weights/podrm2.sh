#!/usr/bin/env bash
# podrm2.sh <name>: podrm over RunPod REST v2: delete, verify (GET -> 404 / TERMINATED), then podrm's bookkeeping
# (~/podhours.log: run name hours dollars gpu) and the registry file removed. A delete that cannot be verified keeps the
# registry and exits 1.
N=$1; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; RATE=""; . "$F"
RP="python3 /home/dan/work/olmo-weights/pod/olmo_ifcurve/rp2.py"; gone=0
for i in 1 2 3 4 5; do
  $RP delete "$POD_ID" > /dev/null 2>&1
  $RP get "$POD_ID" 2>/dev/null | grep -qE '"http": 404|"status": "TERMINATED"' && { gone=1; break; }
  sleep 15
done
[ $gone = 1 ] || { echo "podrm2 $N: delete of $POD_ID not verified; registry kept"; exit 1; }
H=$(awk -v a="$(date -u +%s)" -v b="$(date -u -d "$CREATED" +%s)" 'BEGIN{printf "%.4f",(a-b)/3600}')
D=$(awk -v h="$H" -v r="${RATE:-5.29}" 'BEGIN{printf "%.2f",h*r}')
echo "$(date -u +%FT%TZ) ${RUN:-unknown} $N $H $D ${GPU:-}" >> ~/podhours.log
rm -f "$F"; echo "removed $N ($POD_ID) (${H}h, \$$D)"
