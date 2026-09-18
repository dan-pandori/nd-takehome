#!/usr/bin/env bash
# Local: final pull of one pod's artifacts (+ named checkpoints), check that every remote artifact file exists locally with the same size, then delete the pod.
# Usage: bash pod/r3_4b/finish_pod.sh <pod> [ckpt relpaths...]
P=$1; shift; cd /home/dan/work/round3-run4b
timeout 60 podrun $P "pgrep -af 'python3 (coverage|expert_iter|train|eval_set)' | grep -v pgrep | head -n 3" | grep -q python3 && { echo "$P still has jobs running: not deleting"; exit 1; }
bash pod/r3_4b/wpod.sh pull $P artifacts/r3_4b/ > /dev/null 2>&1
for c in "$@"; do bash pod/r3_4b/wpod.sh pull $P $c; done
timeout 120 podrun $P "find artifacts/r3_4b -type f ! -name 'mix_*.jsonl' -printf '%p %s\n' | sort" > /tmp/$P.remote
MISSING=0; while read -r f s; do [ -f "$f" ] && [ "$(stat -c %s "$f")" = "$s" ] || { echo "MISSING/DIFFERENT: $f"; MISSING=$((MISSING+1)); }; done < /tmp/$P.remote
echo "$P: $(wc -l < /tmp/$P.remote) remote artifact files, $MISSING missing or different locally"
[ $MISSING = 0 ] && podrm $P
