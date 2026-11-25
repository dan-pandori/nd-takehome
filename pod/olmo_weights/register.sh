#!/usr/bin/env bash
# register.sh <name> <pod_id> <created_utc> <gpu>: wait (up to 25 min) until a pod made outside podnew reports a direct
# ssh address, then register it as podnew2.sh does (~/.config/nd-rl/pods/<name>, a line in ~/pods.log, the HF token).
# Used for a pod whose image pull outlasted podnew2.sh's 12-minute wait (2026-11-25, olmo-weights stage 0).
. ~/.config/nd-rl/env; export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
N=$1; ID=$2; T0=$3; GPU=$4; REG=~/.config/nd-rl/pods/$N; [ -f "$REG" ] && { echo "pod $N already registered"; exit 1; }
end=$((SECONDS + 1500)); IP=""; PORT=""
while [ $SECONDS -lt $end ]; do
  INFO=$(runpodctl ssh info "$ID" 2>&1)
  IP=$(printf '%s' "$INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ip') or '')" 2>/dev/null)
  PORT=$(printf '%s' "$INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('port') or '')" 2>/dev/null)
  [ -n "$IP" ] && [ -n "$PORT" ] && break
  sleep 20
done
[ -n "$IP" ] && [ -n "$PORT" ] || { echo "register $N: no ssh address for $ID after 25 min: $(printf '%s' "$INFO" | tr '\n' ' ' | cut -c1-300)"; exit 1; }
RATE=$(python3 /home/dan/work/olmo-weights/pod/olmo_ifcurve/rp2.py get "$ID" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cost') or '')")
printf "POD_ID=%q\nPOD_IP=%q\nPOD_PORT=%q\nRUN=%q\nCREATED=%q\nGPU=%q\nRATE=%q\n" "$ID" "$IP" "$PORT" "${ND_RUN_ID:-unknown}" "$T0" "$GPU" "$RATE" > "$REG"
echo "$T0 $N $ID ${ND_RUN_ID:-unknown}" >> ~/pods.log
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=10 -p $PORT root@$IP"
end=$((SECONDS + 600))
until $S true 2>/dev/null; do [ $SECONDS -ge $end ] && { echo "register $N: ssh never accepted the key"; exit 1; }; sleep 10; done
podtoken "$N" > /dev/null 2>&1 || true
$S "mkdir -p /workspace/nd-takehome"
echo "pod $N ready: $ID $IP:$PORT (gpu $GPU, \$$RATE/h)"
