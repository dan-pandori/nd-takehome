#!/usr/bin/env bash
# claim-audit re-sampling: fresh sampling seeds, no early stopping.
#  R1: SN base s0 (state-env stage1_SN_s0.pt) on the 29 support-curves survivors, T 0.8, k 10,000 each.
#      On file (support-state H s0): 26 / 29 reached at T 0.8 within the first 10,000 attempts (seed 1, stop_at 5).
#  R2: support-curves EI s0 (la_T1_sc_s0_r8.pt, whole-proof lean_seq) on the 29, T 0.8, k 2,000 each.
cd /workspace/nd-takehome
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True LEAN_GATE_WORKERS=32 ND_SAMPLE_PATH=fast
mkdir -p artifacts/ca/dump ckpts/se ckpts/ladder
{
[ -x ~/.elan/bin/lean ] || curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0
~/.elan/bin/lean --version; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
pip -q install --break-system-packages -U 'huggingface_hub[cli]' 2>&1 | tail -1
hf buckets cp hf://buckets/dan-pandori/nd-rl/state-env/ckpts/se/stage1_SN_s0.pt ckpts/se/stage1_SN_s0.pt
hf buckets cp hf://buckets/dan-pandori/nd-rl/support-curves/ckpts/ladder/la_T1_sc_s0_r8.pt ckpts/ladder/la_T1_sc_s0_r8.pt
md5sum ckpts/se/*.pt ckpts/ladder/*.pt
python3 -c "
import json; S=set(open('data/sc/falsifier_survivors.txt').read().split())
R=[l for l in open('data/sc/theorems.jsonl') if json.loads(l)['name'] in S]; open('artifacts/ca/surv.jsonl','w').writelines(R); print('surv rows',len(R))"
echo SETUP_DONE $(date -u +%FT%TZ)
} > artifacts/ca/setup.log 2>&1
(LEAN_GATE_DUMP=artifacts/ca/dump/R1.jsonl python3 ss_support.py --ckpt ckpts/se/stage1_SN_s0.pt --model base --stage CA \
  --names data/sc/falsifier_survivors.txt --k 10000 --stop_at 10000 --temperature 0.8 --seed 9001 --model_seed 0 \
  --batch 4096 --out artifacts/ca/R1_SNbase_s0_T08 > artifacts/ca/R1.log 2>&1; echo "EXIT $? $(date -u +%FT%TZ)" >> artifacts/ca/R1.log) &
(LEAN_GATE_DUMP=artifacts/ca/dump/R2.jsonl python3 support.py --ckpt ckpts/ladder/la_T1_sc_s0_r8.pt --model ei --stage CA \
  --in artifacts/ca/surv.jsonl --k 2000 --stop_at 2000 --temperature 0.8 --seed 9002 \
  --batch 2048 --out artifacts/ca/R2_EI_s0_T08 > artifacts/ca/R2.log 2>&1; echo "EXIT $? $(date -u +%FT%TZ)" >> artifacts/ca/R2.log) &
wait; echo ALL_DONE $(date -u +%FT%TZ) > artifacts/ca/ALL_DONE
