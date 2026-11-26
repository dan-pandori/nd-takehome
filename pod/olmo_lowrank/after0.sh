#!/usr/bin/env bash
# after0.sh (pod side, the stage-0 pod): wait for stage0.sh to finish, rerun the zero-delta check with the
# batch-composition noise reference (zero_check.py: batched and one-sequence-per-batch log-probs, plain and Z8),
# then start the queue worker (queue/lr-a/q0.txt: the rest of T256, then T64).
cd /workspace/nd-takehome; A=artifacts/olmo_lowrank; S=$A/stage0; W=/workspace/lowrank
until grep -q STAGE0_DONE $S/stage0.log; do sleep 20; done
for z in plain lora; do
  X=""; [ $z = lora ] && X="--lora $W/adapters/Z8 --lora_rank 8"
  VLLM_ATTENTION_BACKEND=FLASH_ATTN python olmo_lowrank/zero_check.py run --model /workspace/models/dpo --tokenizer /workspace/models/tok \
    --problems olmo_ifomega/problems.jsonl --out $S/zero2_$z.json $X > $A/logs/zero2_$z.log 2>&1
done
{ echo "plain_vs_lora $(python olmo_lowrank/zero_check.py diff $S/zero2_plain.json $S/zero2_lora.json)"
  echo "plain_batched_vs_single $(python olmo_lowrank/zero_check.py diff $S/zero2_plain.json $S/zero2_plain.json --single)"
  echo "lora_batched_vs_single $(python olmo_lowrank/zero_check.py diff $S/zero2_lora.json $S/zero2_lora.json --single)"
  echo "run1_vs_run2_plain $(python olmo_lowrank/zero_check.py diff $S/zero_plain.json $S/zero2_plain.json)"; } > $S/zero2_diff.txt 2>&1
echo "$(date -u +%FT%TZ) ZERO_CHECK2 done" >> $S/stage0.log
mkdir -p $A/queue; cp $A/queue/lr-a/q0.txt $A/queue/q0.txt
bash pod/olmo_lowrank/start.sh >> $A/logs/after0.log 2>&1
