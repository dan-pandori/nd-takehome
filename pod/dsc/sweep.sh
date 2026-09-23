#!/usr/bin/env bash
# VPS side: one compact line per pod — running jobs, ladder rounds done (T1s0 frs0 T1s1 frs1), coverage targets done,
# failures, GPU%, and the run's pod-hours.  Usage: bash pod/dsc/sweep.sh
cd /home/dan/work/ds-composition
for a in c0 a1 a2 a3 a4; do
  echo -n "$a "
  bash pod/dsc/w.sh dsc-$a sh "echo -n \"j\$(pgrep -fc 'pod/dsc/job[.]sh') la:\"; for j in laT1_${a}_s0 lafr_${a}_s0 laT1_${a}_s1 lafr_${a}_s1; do echo -n \"\$(grep -c 'round .* done' artifacts/dsc/logs/\$j.log 2>/dev/null),\"; done; echo -n ' cov:'; for f in artifacts/dsc/cov_${a}_s*.s0.jsonl; do [ -e \"\$f\" ] && echo -n \"\$(basename \$f .s0.jsonl|sed s/cov_${a}_//)=\$(wc -l < \$f) \"; done; echo -n '| done:'; ls artifacts/dsc/*.done 2>/dev/null|wc -l; echo -n ' fail:'; ls artifacts/dsc/*.failed 2>/dev/null|xargs -n1 basename 2>/dev/null|tr '\n' ' '; nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader" 2>/dev/null | grep -v "command not found" | tr '\n' ' '
  echo
done
podbudget ds-composition 2>/dev/null | tail -1
