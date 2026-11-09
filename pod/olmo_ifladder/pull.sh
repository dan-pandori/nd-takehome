#!/usr/bin/env bash
# pull.sh <pod> <job> [<job> ...]: VPS-side; pull a job's samples, grades, meta and logs into the worktree; print row counts.
N=$1; shift; export POD_LOCAL_ROOT=/home/dan/work/olmo-ifladder; W=$POD_LOCAL_ROOT; A=artifacts/olmo_ifladder
mkdir -p $W/$A/samples $W/$A/graded $W/$A/meta $W/$A/logs
for J in "$@"; do
  for f in samples/$J.jsonl.gz graded/$J.jsonl meta/$J.json meta/$J.done logs/q_$J.log logs/${J}_smi.log; do
    podpull $N $A/$f > /dev/null 2>&1
  done
  ns=$(python3 -c "import gzip
n=0
try:
    for l in gzip.open('$W/$A/samples/$J.jsonl.gz','rt'): n+=1
except Exception: pass
print(n)")
  ng=$(wc -l < $W/$A/graded/$J.jsonl 2>/dev/null || echo 0)
  echo "$J samples=$ns graded=$ng done=$([ -f $W/$A/meta/$J.done ] && echo yes || echo no)"
done
