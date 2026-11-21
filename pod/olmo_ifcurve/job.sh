#!/usr/bin/env bash
# job.sh <job> <name> <rev> <pids-file> <seed> <chunk> [sampler flags ...]: fetch, sample, grade (run olmo-ifcurve).
# olmo-ifladder's pod/olmo_ifladder/job.sh with this run's artifact dir; the sampler is olmo_ifladder/sample.py, unchanged,
# on olmo_ifomega/problems.jsonl (no hints); repo: dpo -> allenai/Olmo-3-32B-Think-DPO, else allenai/Olmo-3.1-32B-Think.
# <pids-file> lists pid:n (per-pid draw counts, request order = file order; --order given).
# env: META (meta path; default meta/<job>.json), TP (default 1), GPU (index for the nvidia-smi log, default 0),
#      RMMODEL=1 (delete /workspace/models/<name> after grading, to free the volume).
J=$1; NAME=$2; V=$3; P=$4; S=$5; CH=$6; shift 6
cd /workspace/nd-takehome; A=artifacts/olmo_ifcurve; TP=${TP:-1}; G=${GPU:-0}; mkdir -p $A/samples $A/graded $A/meta $A/logs
R=allenai/Olmo-3.1-32B-Think; [ "$NAME" = "dpo" ] && R=allenai/Olmo-3-32B-Think-DPO
M=${META:-$A/meta/$J.json}
bash pod/olmo_ifomega/fetch.sh "$R" "$V" "$NAME" || { echo "FETCH_FAIL $(date -u +%FT%TZ)"; exit 1; }
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi -i $G --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' ')"; done ) >> $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) name=$NAME rev=$V sha=$(cat /workspace/models/$NAME/.sha) tp=$TP gpu=$G cvd=$CUDA_VISIBLE_DEVICES pids=$P seed=$S meta=$M extra=[$*]"
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_ifladder/sample.py --model /workspace/models/$NAME --tokenizer /workspace/models/tok \
  --name "$NAME" --rev "$V" --problems olmo_ifomega/problems.jsonl --pids @$P --n 0 --chunk $CH --seed $S --job $J --tp $TP \
  --order given --out $A/samples/$J.jsonl.gz --meta $M "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo_ifomega/grade.py $A/samples/$J.jsonl.gz olmo_ifomega/problems.jsonl $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $M.done
[ "$RMMODEL" = "1" ] && [ $rc -eq 0 ] && rm -rf /workspace/models/$NAME /workspace/models/$NAME.lock && echo "MODEL_REMOVED $NAME"
exit $rc
