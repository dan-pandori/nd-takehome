#!/usr/bin/env bash
# Secondary (not pre-registered): re-read state-cap12's SN-cap12 T1 checkpoints (the "up to 4 random proofs" selection,
# per-round evals, no step filter) at this run's read-out settings, to compare with arm A (shortest-proof selection).
# Usage: bash pod/sx/t1reads.sh <seed> [<seed> ...]   (runs after this pod's pair.sh finished)
source pod/sx/env.sh
while pgrep -f 'pair.s[h]' > /dev/null; do sleep 30; done
for S in "$@"; do
  CK=ckpts/sx/T1/la_T1_SN12_s${S}_r8.pt
  [ -s $CK ] || hf buckets cp hf://buckets/dan-pandori/nd-rl/state-cap12/ckpts/sc12/ladder/la_T1_SN12_s${S}_r8.pt $CK
  bash pod/sx/reread.sh $CK T1_s$S &
done
wait
up artifacts/sx
echo "=== t1reads done $(date -u +%FT%TZ)"
