#!/usr/bin/env bash
# stage0.sh (pod side, after setup.sh with FETCH="dpo s2300"): olmo-lowrank stage 0 on one H200, then the Part-2
# adapters. Steps, each logged with its UTC time in artifacts/olmo_lowrank/stage0/stage0.log:
#  1 wait for the dpo / s2300 downloads (setup.sh logs FETCH_SECONDS) and sha256-check every shard against the manifest
#  2 SVD time and accuracy (olmo_lowrank/stage0_svd.py) -> stage0/svd_timing.json
#  3 SVD of D = s2300 - dpo on the 448 matrices: exact if svd_timing projects <= 3600 s, else randomized at the chosen
#    (p, q); adapters T1..T256, C16, Z8 written and verified (adapters.py) -> /workspace/lowrank/{factors,adapters}
#  4 zero-delta check: plain dpo vs dpo + Z8 through the LoRA path (zero_check.py)
#  5 T256 on plan/S0.pids (12 reach x 16 + 12 others x 4) through the LoRA path at max_lora_rank 256 -> the first rows
#    of job T256 (meta/T256_stage0.json)
cd /workspace/nd-takehome; A=artifacts/olmo_lowrank; S=$A/stage0; W=/workspace/lowrank; mkdir -p $S $A/logs $W
L=$S/stage0.log; log() { echo "$(date -u +%FT%TZ) $*" | tee -a $L; }
export OMP_NUM_THREADS=8
log STAGE0_START
until [ -f /workspace/models/dpo/.complete ] && [ -f /workspace/models/s2300/.complete ]; do sleep 15; done
log DOWNLOADS_DONE $(grep -h FETCH_SECONDS $A/logs/fetch_dpo.log $A/logs/fetch_s2300.log | tr '\n' ' ')
python olmo_lowrank/shacheck.py /workspace/models/dpo 32B/dpo /workspace/models/s2300 32B/rl/2300 > $S/sha_check.txt 2>&1
log SHA $(grep -h SHA_ $S/sha_check.txt | tr '\n' ' ')
grep -q SHA_FAIL $S/sha_check.txt && { log STAGE0_ABORT sha; exit 1; }
python olmo_lowrank/stage0_svd.py --dpo /workspace/models/dpo --rl /workspace/models/s2300 --out $S/svd_timing.json > $A/logs/stage0_svd.log 2>&1
log SVD_TIMING $(grep CHOICE $A/logs/stage0_svd.log)
read METHOD P Q <<< "$(python -c "
import json; r = json.load(open('$S/svd_timing.json')); c = r.get('choice') or {'p': 256, 'q': 16}
print('exact' if r['proj_t_svd_fp32_full_s_per_change'] <= 3600 else 'rsvd', c['p'], c['q'])")"
log ADAPTER_SVD_METHOD $METHOD p=$P q=$Q
python olmo_lowrank/adapters.py svd --dpo /workspace/models/dpo --rl /workspace/models/s2300 --out $W --method $METHOD --p $P --q $Q > $A/logs/adapters_svd.log 2>&1
log ADAPTER_SVD_DONE $(tail -n 1 $A/logs/adapters_svd.log)
python olmo_lowrank/adapters.py write --out $W > $A/logs/adapters_write.log 2>&1
python olmo_lowrank/adapters.py verify --out $W --dpo /workspace/models/dpo --rl /workspace/models/s2300 > $A/logs/adapters_verify.log 2>&1
log ADAPTERS $(tail -n 1 $A/logs/adapters_verify.log)
cp $W/adapters/verify.json $S/adapters_verify.json; cp $W/factors/norms.csv $S/N2300_norms.csv
for z in plain lora; do
  X=""; [ $z = lora ] && X="--lora $W/adapters/Z8 --lora_rank 8"
  VLLM_ATTENTION_BACKEND=FLASH_ATTN python olmo_lowrank/zero_check.py run --model /workspace/models/dpo --tokenizer /workspace/models/tok \
    --problems olmo_ifomega/problems.jsonl --out $S/zero_$z.json $X > $A/logs/zero_$z.log 2>&1
done
python olmo_lowrank/zero_check.py diff $S/zero_plain.json $S/zero_lora.json > $S/zero_diff.json 2>&1
log ZERO_CHECK $(cat $S/zero_diff.json)
META=$A/meta/T256_stage0.json bash pod/olmo_lowrank/job.sh T256 dpo main olmo_lowrank/plan/S0.pids 62026 8 \
  --lora $W/adapters/T256 --lora_name T256 --lora_rank 256 > $A/logs/q_T256_stage0.log 2>&1
log T256_STAGE0 rc=$? $(grep -h -E 'JOB_DONE|kv_cache|Error|error' $A/logs/q_T256_stage0.log | tail -n 3 | tr '\n' ' ')
log STAGE0_DONE
