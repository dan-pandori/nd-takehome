#!/usr/bin/env bash
# fetch.sh <repo> <revision> <dirname> [file ...]: download a checkpoint (or the named files) to /workspace/models/<dirname>.
R=$1; V=$2; D=/workspace/models/$3; shift 3
[ -f "$D/.complete" ] && exit 0
mkdir -p "$D"; exec 9> "$D.lock"; flock 9   # one download per directory (prefetch and job may race)
[ -f "$D/.complete" ] && exit 0
t0=$(date +%s)
if [ $# -gt 0 ]; then hf download "$R" "$@" --revision "$V" --local-dir "$D" > /dev/null || exit 1
else hf download "$R" --revision "$V" --local-dir "$D" --exclude "*.png" > /dev/null || exit 1; fi
python -c "from huggingface_hub import HfApi; print(HfApi().model_info('$R', revision='$V').sha)" > "$D/.sha"
echo "fetched $R@$V ($(cat $D/.sha)) in $(( $(date +%s) - t0 )) s, $(du -sh $D | cut -f1)"; touch "$D/.complete"
