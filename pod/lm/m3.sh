#!/usr/bin/env bash
# lit-measures M3 on a pod: fetch the last-round found files + args.json of every M3 ladder (pod/lm/m3_files.txt,
# ~2.1 GB, 1.5 GB of it state-cap12) into /workspace/m3/<bucket path>, then run lm_m3.py (stdlib only, streams rows).
# Run from anywhere: bash /workspace/nd-takehome/pod/lm/m3.sh   (hf CLI installed and logged in via HF_TOKEN)
cd /workspace/nd-takehome; mkdir -p artifacts/lit-measures/m3 /workspace/m3
LOG=artifacts/lit-measures/m3/m3_$(hostname).log
{
  date; B=hf://buckets/dan-pandori/nd-rl
  grep -v '^$' pod/lm/m3_files.txt | xargs -P 8 -I{} sh -c \
    'mkdir -p "$(dirname /workspace/m3/{})" && { [ -s "/workspace/m3/{}" ] || hf buckets cp '"$B"'/{} /workspace/m3/{} >/dev/null 2>&1; } || echo "FETCH_FAIL {}"'
  echo "fetched $(find /workspace/m3 -type f | wc -l) of $(grep -c . pod/lm/m3_files.txt) files, $(du -sb /workspace/m3 | cut -f1) bytes"
  # zero-byte bucket files (round3-run4b req/frozen arms) are legitimately empty: fetch failures are the ones missing
  missing=0; while read -r p; do [ -e "/workspace/m3/$p" ] || { echo "MISSING $p"; missing=$((missing+1)); }; done < pod/lm/m3_files.txt
  echo "missing=$missing"; date
  python3 lm_m3.py --root /workspace/m3 --out artifacts/lit-measures/m3 && echo M3_DONE
  date
} > "$LOG" 2>&1
tail -5 "$LOG"
