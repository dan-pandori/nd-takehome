#!/usr/bin/env bash
# The whole ckpt-avg pod pipeline, resumable (every step skips finished work).  Log artifacts/ca/logs/.
#   setsid nohup bash pod/ca/pipeline.sh > artifacts/ca/logs/pipeline.out 2>&1 < /dev/null &
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PATH=$HOME/.elan/bin:$PATH
L=artifacts/ca/logs; mkdir -p $L artifacts/ca/ev artifacts/ca/ev_r ckpts/sd ckpts/ca
ts() { date -u +%FT%TZ; }
echo "setup $(ts)"
{
  [ -x ~/.elan/bin/lean ] || curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.0
  ~/.elan/bin/lean --version; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  python3 -c "import torch; print('torch', torch.__version__, torch.cuda.get_device_name(0))"
  command -v hf || pip install -q -U 'huggingface_hub[cli]' 2>&1 | tail -2
  LEAN_GATE_WORKERS=6 LEAN_GATE_LOG=artifacts/ca/gate_selftest.jsonl python3 pod/lf/gate_selftest.py
} > $L/setup.log 2>&1
echo "download $(ts)"
hf buckets sync hf://buckets/dan-pandori/nd-rl/stage1-dynamics/ckpts/sd ckpts/sd > $L/download.log 2>&1
ls ckpts/sd/*.pt | wc -l >> $L/download.log
echo "average $(ts)"
python3 ca_average.py > $L/average.log 2>&1 || { echo AVG_FAILED; exit 1; }
echo "valloss $(ts)"
python3 ca_plan.py all_ckpts | sed 's#^#ckpts/sd/#; s#$#.pt#' > artifacts/ca/sd_ckpts.txt
python3 ca_valloss.py --ckpts $(cat artifacts/ca/sd_ckpts.txt) 'ckpts/ca/*.pt' --out artifacts/ca/valloss_A.jsonl > $L/valloss.log 2>&1 &
# greedy half-B evaluation, 3 concurrent chains; every sd checkpoint the plan uses + every average
( cat artifacts/ca/sd_ckpts.txt; ls ckpts/ca/*.pt ) > artifacts/ca/eval_list.txt
split -n l/3 -d artifacts/ca/eval_list.txt artifacts/ca/eval_part.
echo "eval $(ts)"
for p in 00 01 02; do
  CUDA_MEM_FRACTION=0.28 LEAN_GATE_WORKERS=8 python3 sd_eval.py --ckpts $(cat artifacts/ca/eval_part.$p) \
    --in data/ca/heldout_B.jsonl --outdir artifacts/ca/ev --batch 2500 --max_new 400 --texts --skip_done \
    > $L/eval_$p.log 2>&1 &
done
wait
echo "arm R texts $(ts)"
# the stage1-dynamics review's open gap: arm R's counted proofs with their literal text, on the FULL
# held-out file at stage1-dynamics' own settings (batch 512, max_new 400), so the counts are comparable
CUDA_MEM_FRACTION=0.5 LEAN_GATE_WORKERS=16 python3 sd_eval.py --ckpts 'ckpts/sd/r6*.pt' 'ckpts/sd/r24*.pt' \
  --in data/p2/heldout.jsonl --outdir artifacts/ca/ev_r --batch 512 --max_new 400 --texts --skip_done > $L/eval_r.log 2>&1
echo "PIPELINE_DONE $(ts)"
touch artifacts/ca/pipeline.done
