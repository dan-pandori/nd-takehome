#!/usr/bin/env bash
# contam.sh: n-gram scan of the evaluation problems against the Think RL, DPO and SFT data (CPU job, own pod).
cd /workspace/nd-takehome; A=artifacts/olmo32/contam; mkdir -p $A; DATA=${DATA:-/root/data}; mkdir -p $DATA
pip install --break-system-packages -q pyarrow "huggingface_hub[cli,hf_xet]" 2>&1 | grep -v -i "warning\|notice" | tail -2
Q=$(awk '{if ($1=="max") print 0; else print int($1/$2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); NP=$(nproc)
PROCS=${PROCS:-$([ -n "$Q" ] && [ "$Q" -gt 0 ] && [ "$Q" -lt "$NP" ] && echo $Q || echo $NP)}; [ $PROCS -gt 24 ] && PROCS=24
echo "CONTAM_START $(date -u +%FT%TZ) nproc=$NP quota=$Q procs=$PROCS"
for spec in "rl allenai/Dolci-Think-RL-32B" "dpo allenai/Dolci-Think-DPO-32B" "sft allenai/Dolci-Think-SFT-32B"; do
  set -- $spec; t0=$(date +%s)
  hf download $2 --repo-type dataset --local-dir $DATA/$1 > /dev/null || { echo "DOWNLOAD_FAIL $2"; continue; }
  python -c "from huggingface_hub import HfApi; print('$2', HfApi().dataset_info('$2').sha)" >> $A/dataset_revisions.txt
  echo "downloaded $2 in $(( $(date +%s) - t0 )) s ($(du -sh $DATA/$1 | cut -f1))"
  t1=$(date +%s); PROCS=$PROCS python olmo32/contam32.py scan olmo32/problems.jsonl $1 $A/scan_$1.jsonl $(ls $DATA/$1/data/*.parquet) > $A/scan_$1.log 2>&1
  echo "scanned $1 in $(( $(date +%s) - t1 )) s: $(tail -n 1 $A/scan_$1.log)"
  [ $1 = rl ] && python olmo32/contam32.py idf olmo32/problems.jsonl $A/idf_rl.jsonl $(ls $DATA/rl/data/*.parquet)
  rm -rf $DATA/$1   # free the container disk for the next corpus
done
python olmo32/contam32.py merge olmo32/problems.jsonl $A/contamination_think.csv $A/scan_*.jsonl
echo "CONTAM_DONE $(date -u +%FT%TZ)"
