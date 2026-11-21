#!/usr/bin/env bash
# podnew2.sh <name>: podnew over RunPod REST v2 (pod/olmo_ifcurve/rp2.py; v1 was retired 2026-11-15 and the host's
# runpodctl 2.14.0 still uses it). Registers the pod as podnew does (~/.config/nd-rl/pods/<name>: POD_ID POD_IP POD_PORT
# RUN CREATED GPU RATE; a line in ~/pods.log), so podrun / podpush / podpull / podbudget work unchanged.
# env: POD_GPU (NVIDIA H200), POD_COUNT (1), POD_CLOUD (COMMUNITY), POD_VOLUME (200), POD_DISK (60), POD_MINCUDA (12.8),
# ND_RUN_ID. Any failure after the create deletes the pod and verifies it (GET -> 404 / TERMINATED); a pod that cannot
# be verified gone is logged ORPHAN in ~/pods.log and printed.
. ~/.config/nd-rl/env; export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
N=$1; REG=~/.config/nd-rl/pods/$N; [ -f "$REG" ] && { echo "pod $N already registered"; exit 1; }
RP="python3 /home/dan/work/olmo-ifcurve/pod/olmo_ifcurve/rp2.py"
LK=~/runs/olmo-ifcurve/creating_$N; touch $LK; trap 'rm -f $LK' EXIT   # orphans.sh skips a name being created
GPU=${POD_GPU:-NVIDIA H200}; T0=$(date -u +%FT%TZ)
OUT=$($RP create "$N" --gpu "$GPU" --count "${POD_COUNT:-1}" --cloud "${POD_CLOUD:-COMMUNITY}" --disk "${POD_DISK:-60}" \
      --volume "${POD_VOLUME:-200}" --min-cuda "${POD_MINCUDA:-12.8}" 2>&1)
ID=$(printf '%s' "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id') or '')" 2>/dev/null)
[ -n "$ID" ] || { echo "podnew2 $N: create failed: $(printf '%s' "$OUT" | tr '\n' ' ' | cut -c1-300)"; exit 1; }
gone() { $RP get "$1" 2>/dev/null | grep -qE '"http": 404|"status": "TERMINATED"'; }
undo() {
  for i in 1 2 3 4 5; do
    $RP delete "$ID" > /dev/null 2>&1
    gone "$ID" && { echo "$(date -u +%FT%TZ) $N $ID ${ND_RUN_ID:-unknown} UNDONE" >> ~/pods.log; echo "podnew2 $N: removed $ID"; return 0; }
    sleep 15
  done
  echo "$(date -u +%FT%TZ) $N $ID ${ND_RUN_ID:-unknown} ORPHAN" >> ~/pods.log; echo "podnew2 $N: COULD NOT DELETE $ID"; return 1
}
end=$((SECONDS + 720)); ST=-; HOST=-; PORT=-; RATE=-
while [ $SECONDS -lt $end ]; do
  read -r ST HOST PORT RATE <<< "$($RP get "$ID" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status') or '-', d.get('host') or '-', d.get('port') or '-', d.get('cost') or '-')" 2>/dev/null)"
  [ "$ST" = "RUNNING" ] && [ "$HOST" != "-" ] && [ "$PORT" != "-" ] && break
  case "$ST" in EXITED|ERROR|TERMINATED) break ;; esac
  sleep 10
done
if [ "$ST" != "RUNNING" ] || [ "$HOST" = "-" ] || [ "$PORT" = "-" ]; then echo "podnew2 $N: $ID not running with a direct ssh port ($ST $HOST:$PORT)"; undo; exit 1; fi
printf "POD_ID=%q\nPOD_IP=%q\nPOD_PORT=%q\nRUN=%q\nCREATED=%q\nGPU=%q\nRATE=%q\n" "$ID" "$HOST" "$PORT" "${ND_RUN_ID:-unknown}" "$T0" "$GPU" "$RATE" > "$REG"
echo "$(date -u +%FT%TZ) $N $ID ${ND_RUN_ID:-unknown}" >> ~/pods.log
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=10 -p $PORT root@$HOST"
end=$((SECONDS + 600))
until $S true 2>/dev/null; do
  [ $SECONDS -ge $end ] && { echo "podnew2 $N: ssh never accepted the key ($ID); removing it"; bash /home/dan/work/olmo-ifcurve/pod/olmo_ifcurve/podrm2.sh "$N"; exit 1; }
  sleep 10
done
podtoken "$N" > /dev/null 2>&1 || true
$S "mkdir -p /workspace/nd-takehome"
echo "pod $N ready: $ID $HOST:$PORT (gpu $GPU, \$$RATE/h)"
