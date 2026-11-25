#!/usr/bin/env bash
# bringup.sh <name> <container_disk_gb> <jobs,comma,list> <inflight> <disk_cap_gb> [lora]: VPS-side. Create an A40
# pod (podnew2.sh, REST v2), push the code (and the LoRA adapters, sha256-checked on the pod), run setup.sh (installs,
# engine self-test), then launch run_jobs.sh detached. Prints BRINGUP_OK <name> or BRINGUP_FAIL <name> <why>.
N=$1; DISK=$2; JOBS=$3; INF=$4; CAP=$5; LORA=${6:-}; W=/home/dan/work/olmo-weights; cd $W
ND_RUN_ID=olmo-weights POD_GPU="NVIDIA A40" POD_CLOUD=SECURE POD_VOLUME=20 POD_DISK=$DISK POD_MINCUDA=12.8 \
  bash pod/olmo_weights/podnew2.sh $N || { echo "BRINGUP_FAIL $N create"; exit 1; }
bash pod/olmo_weights/push.sh $N
if [ -n "$LORA" ]; then
  POD_LOCAL_ROOT=/home/dan/runs/olmo-weights podpush $N lora > /dev/null 2>&1 || { echo "BRINGUP_FAIL $N lora push"; exit 1; }
  timeout 120 podrun $N "sha256sum lora/main/adapter_model.safetensors lora/ctrl/adapter_model.safetensors" > /home/dan/runs/olmo-weights/lora_sha_$N.txt 2>&1
  grep -q 9921a7602ea16e9845efb1ec868f6568e3e5a18d08c7fc6c151db826ca0596d9 /home/dan/runs/olmo-weights/lora_sha_$N.txt && \
  grep -q 4cf06004bb580bf60e10e32fd1026bd9698902830c3b19b5f13f98cfd744133d /home/dan/runs/olmo-weights/lora_sha_$N.txt || \
    { echo "BRINGUP_FAIL $N lora sha256"; exit 1; }
fi
timeout 900 podrun $N "bash pod/olmo_weights/setup.sh > /workspace/setup.log 2>&1; grep -c 'SELFTEST PASS' /workspace/setup.log" > /home/dan/runs/olmo-weights/setup_$N.txt 2>&1
[ "$(tail -1 /home/dan/runs/olmo-weights/setup_$N.txt)" = "3" ] || { echo "BRINGUP_FAIL $N selftest: $(tail -2 /home/dan/runs/olmo-weights/setup_$N.txt | tr '\n' ' ')"; exit 1; }
timeout 20 podrun $N "setsid nohup bash pod/olmo_weights/run_jobs.sh $JOBS $INF $CAP > /workspace/run_jobs.log 2>&1 < /dev/null & disown; sleep 1; echo launched" > /dev/null 2>&1
sleep 5
timeout 30 podrun $N "pgrep -f 'run_jobs.s[h]' | head -1" 2>/dev/null | grep -q '[0-9]' && echo "BRINGUP_OK $N $(date -u +%T) jobs $JOBS" || echo "BRINGUP_FAIL $N launch"
