#!/usr/bin/env bash
# VPS side: compact progress line per pod: failed markers, finished coverage jobs, latest ladder round per arm, GPU memory.
for arm in ${@:-c0 a1 a2 a3 a4}; do
  echo "== $arm $(date -u +%H:%M) $(bash /home/dan/work/ds-composition/pod/dsc/w.sh dsc-$arm sh "ls artifacts/dsc/*.failed 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/.failed/ FAILED/' | tr '\n' ' '; echo -n 'cov done: '; ls artifacts/dsc/cov_*.done 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/cov_${arm}_//;s/.done//' | tr '\n' ' '; echo -n '| running: '; ps -eo args | grep '^python3 coverage_lean.py' | grep -o 'cov_[a-z0-9_]*$' | sort -u | sed 's/cov_${arm}_//' | tr '\n' ' '; echo -n '| ladder: '; for a in la_T1_${arm}_s0 la_T1_${arm}_s1 la_frozen_${arm}_s0 la_frozen_${arm}_s1; do r=\$(ls artifacts/dsc/\$a/round_*.json 2>/dev/null | wc -l); echo -n \"\$r \"; done; nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr '\n' ' '" 2>&1 | grep -v "^Warning")"
done
