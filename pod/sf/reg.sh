#!/usr/bin/env bash
# Register a pod created with runpodctl directly (podnew fails silently when the class is out of stock). Usage: reg.sh <name> <id> <gpu>
. ~/.config/nd-rl/env; export PATH="$HOME/.local/bin:$PATH"; N=$1; ID=$2; G=$3
for i in $(seq 1 40); do INFO=$(runpodctl ssh info "$ID" 2>/dev/null); IP=$(printf "%s" "$INFO" | jq -r .ip 2>/dev/null); PORT=$(printf "%s" "$INFO" | jq -r .port 2>/dev/null); [ -n "$IP" ] && [ "$IP" != null ] && break; sleep 10; done
printf "POD_ID=%q\nPOD_IP=%q\nPOD_PORT=%q\nRUN=%q\nCREATED=%q\nGPU=%q\n" "$ID" "$IP" "$PORT" support-followups "$(date -u +%FT%TZ)" "$G" > ~/.config/nd-rl/pods/$N
echo "$(date -u +%FT%TZ) $N $ID support-followups" >> ~/pods.log
S="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ConnectTimeout=10 -p $PORT root@$IP"
for i in $(seq 1 40); do $S true 2>/dev/null && break; sleep 10; done; podtoken $N >/dev/null 2>&1
$S "mkdir -p /workspace/nd-takehome; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; nproc; python3 -c 'import torch;print(torch.cuda.is_available())'"
