#!/usr/bin/env bash
# job.sh <job> <name> <repo> <rev> <n> <pids|-> <seed> <chunk> <chunk0> [sampler flags ...]: fetch, sample, grade.
# env: PROBLEMS (default olmo32/problems.jsonl); TP (default: all GPUs of the pod).
J=$1; NAME=$2; R=$3; V=$4; N=$5; P=$6; S=$7; CH=$8; C0=$9; shift 9
cd /workspace/nd-takehome; A=artifacts/olmo32; PROBLEMS=${PROBLEMS:-olmo32/problems.jsonl}; TP=${TP:-$(nvidia-smi -L | wc -l)}
bash pod/olmo32/fetch.sh "$R" "$V" "$NAME" || { echo "FETCH_FAIL $(date -u +%FT%TZ)"; exit 1; }
PIDS=""; [ "$P" != "-" ] && PIDS="--pids $P"
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' ')"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) tp=$TP extra=[$*]"
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo32/sample.py --model /workspace/models/$NAME --tokenizer /workspace/models/tok \
  --name "$NAME" --rev "$V" --problems $PROBLEMS $PIDS --n $N --chunk $CH --chunk0 $C0 --seed $S --job $J --tp $TP \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo32/grade.py $A/samples/$J.jsonl.gz $PROBLEMS $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
