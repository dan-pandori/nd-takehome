#!/usr/bin/env bash
# one-screen status of this pod's round3-run4a jobs
cd /workspace/nd-takehome/artifacts/r3_4a
echo "== $(hostname) $(date -u +%T) gpu $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader) disk $(df -h /workspace | tail -1 | awk '{print $5}')"
echo "done: $(ls *.done 2>/dev/null | sed 's/.done//' | tr '\n' ' ')"
[ -f queue_failed.txt ] && echo "FAILED: $(tr '\n' ' ' < queue_failed.txt)"
[ -f queue_retries.txt ] && echo "retries: $(wc -l < queue_retries.txt) last: $(tail -n 1 queue_retries.txt)"
for f in train_*.log; do [ -f stage1_${f#train_}.done ] 2>/dev/null; t=${f#train_}; t=${t%.log}; [ -f stage1_$t.done ] || echo "train $t: $(tail -n 1 $f | cut -c1-80)"; done
for f in cov_*_pre.log cov_*_b10k.log; do [ -f $f ] || continue; t=${f#cov_}; t=${t%.log}; n=$(grep -c 'n_ok [1-9]' $f); echo "cov $t: hit-targets $n; $(tail -n 1 $f | grep -o '([0-9]*s; .*' | cut -c1-60)$(tail -n 1 $f | grep -o DONE)"; done
for d in ei_* frozen_*; do [ -d $d ] || continue; r=$(ls $d/round_*.json 2>/dev/null | wc -l); [ $r -gt 0 ] && python3 - $d $r <<'P'
import json,sys
d,r=sys.argv[1],int(sys.argv[2])
print(d, 'rounds', r, 'cum solved by round:', [json.load(open(f'{d}/round_{i}.json'))['targets_cum']['solved'] for i in range(1,r+1)], 'heldout', round(json.load(open(f'{d}/round_{r}.json'))['heldout_greedy']['rate'],3))
P
done
