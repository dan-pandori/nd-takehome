#!/usr/bin/env bash
# bringup1.sh <p> <q> <full> <job> [<job> ...] (pod side): the Part-1 spectra pod. Light setup (huggingface_hub
# 0.36.2 + hf_xet for the Hub, a venv /opt/hfv with huggingface_hub 1.32.0 for the bucket), GPU gate, lora_main /
# lora_ctrl from olmo-ifladder's bucket path with their sha256 checked against artifacts/MANIFEST.jsonl's records,
# the engine self-test, then olmo_lowrank/spectra.py for each job in order. Run detached (setsid nohup ... &).
P=$1; Q=$2; FULL=$3; shift 3
cd /workspace/nd-takehome; A=artifacts/olmo_lowrank; mkdir -p $A/logs $A/meta $A/spectra /models/spec /workspace/lora
L=$A/logs/bringup1.log; log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
log START p=$P q=$Q full=$FULL jobs="$*"
{ date -u; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; nvidia-smi -q | grep -A4 -i "Remapped Rows"
  echo "cpu.max $(cat /sys/fs/cgroup/cpu.max 2>/dev/null)"; nproc; free -g | head -2; df -h / /workspace | tail -2; } > $A/meta/pod_env1_$(hostname).txt 2>&1
pip install --break-system-packages -q "huggingface_hub[hf_xet]==0.36.2" "hf-xet==1.8.0" safetensors > $A/logs/setup1.log 2>&1
python3 -m venv /opt/hfv >> $A/logs/setup1.log 2>&1 && /opt/hfv/bin/pip install -q "huggingface_hub[cli,hf_xet]==1.32.0" >> $A/logs/setup1.log 2>&1
python -c "import torch; x = torch.randn(8192, 8192, device='cuda'); print('GPU_TEST', bool((x @ x).sum().item() == (x @ x).sum().item()), torch.cuda.get_device_name(0), torch.__version__)" >> $L 2>&1
grep -q "GPU_TEST True" $L || { log GPU_BAD; exit 1; }
for n in main ctrl; do
  mkdir -p /workspace/lora/$n
  for f in adapter_config.json adapter_model.safetensors; do
    /opt/hfv/bin/hf buckets cp hf://buckets/dan-pandori/nd-rl/olmo-ifladder/artifacts/olmo_ifladder/lora/$n/$f /workspace/lora/$n/$f >> $A/logs/setup1.log 2>&1
  done
done
sha256sum /workspace/lora/*/adapter_model.safetensors > $A/meta/lora_sha256.txt
if grep -q "^9921a7602ea16e9845efb1ec868f6568e3e5a18d08c7fc6c151db826ca0596d9 .*main" $A/meta/lora_sha256.txt && \
   grep -q "^4cf06004bb580bf60e10e32fd1026bd9698902830c3b19b5f13f98cfd744133d .*ctrl" $A/meta/lora_sha256.txt; then log LORA_SHA_OK
else log LORA_SHA_FAIL; exit 1; fi
OMP_NUM_THREADS=8 python olmo_lowrank/spectra.py --selftest > $A/logs/spectra_selftest.log 2>&1
grep -q "SELFTEST PASS" $A/logs/spectra_selftest.log && log SELFTEST_PASS || { log SELFTEST_FAIL; exit 1; }
for J in "$@"; do
  log JOB_START $J
  OMP_NUM_THREADS=8 python -u olmo_lowrank/spectra.py --job $J --p $P --q $Q --full $FULL --subset-mod ${SUBSET_MOD:-1} > $A/logs/spectra_$J.log 2>&1
  log JOB_END $J rc=$?
done
log END
