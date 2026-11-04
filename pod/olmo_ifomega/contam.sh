#!/usr/bin/env bash
# contam.sh: n-gram scan of the evaluation prompts against the Think DPO and SFT data (CPU side job at nice 19 on a
# sampling pod; the RL prompts are scanned on the VPS). Pinned revisions; each corpus deleted after its scan.
cd /workspace/nd-takehome; A=artifacts/olmo_ifomega/contam; mkdir -p $A; DATA=${DATA:-/root/data}; mkdir -p $DATA
Q=$(awk '{if ($1=="max") print 0; else print int($1/$2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); NP=$(nproc)
PROCS=${PROCS:-$([ -n "$Q" ] && [ "$Q" -gt 0 ] && [ "$Q" -lt "$NP" ] && echo $((Q > 2 ? Q - 2 : 1)) || echo 6)}; [ $PROCS -gt 12 ] && PROCS=12
echo "CONTAM_START $(date -u +%FT%TZ) nproc=$NP quota=$Q procs=$PROCS"
for spec in "dpo allenai/Dolci-Think-DPO-32B 0898aac9657c0fa79b02c0e91627b370bed2a127" "sft allenai/Dolci-Think-SFT-32B 7668c638cc84100951973b456069a1a462d6d915"; do
  set -- $spec; t0=$(date +%s)
  hf download $2 --repo-type dataset --revision $3 --local-dir $DATA/$1 > /dev/null || { echo "DOWNLOAD_FAIL $2"; continue; }
  echo "$2 $3" >> $A/dataset_revisions.txt
  echo "downloaded $2 in $(( $(date +%s) - t0 )) s ($(du -sh $DATA/$1 | cut -f1))"
  t1=$(date +%s); PROCS=$PROCS nice -n 19 python olmo_ifomega/contam.py scan olmo_ifomega/problems.jsonl $1 $A/scan_$1.jsonl olmo_ifomega/contam_template_df20.json $(find $DATA/$1 -name '*.parquet' | sort) > $A/scan_$1.log 2>&1
  echo "scanned $1 in $(( $(date +%s) - t1 )) s: $(tail -n 1 $A/scan_$1.log)"
  rm -rf $DATA/$1
done
echo "CONTAM_DONE $(date -u +%FT%TZ)"
