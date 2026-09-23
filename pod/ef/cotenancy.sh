#!/usr/bin/env bash
# Run efficiency, step 6: round time at N concurrent sampling jobs on one GPU.
# Usage: bash pod/ef/cotenancy.sh <n> <tagprefix> [extra bench args]
cd /workspace/nd-takehome
N=$1; TAG=$2; shift 2
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PATH=$HOME/.elan/bin:$PATH
export CUDA_MEM_FRACTION=$(python3 -c "print(round(0.90/$N,3))")
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 LEAN_CHECK_WORKERS=$((192/N)) LEAN_CHECK_CHUNK=300
mkdir -p artifacts/ef/logs
T0=$(date +%s.%N)
for i in $(seq 1 $N); do
  LEAN_GATE_LOG=artifacts/ef/gate_${TAG}_n${N}_$i.jsonl \
  python3 bench_sampler.py --tag ${TAG}_n${N}_$i --seed $((100*i)) "$@" > artifacts/ef/logs/${TAG}_n${N}_$i.log 2>&1 &
done
wait
T1=$(date +%s.%N)
python3 - "$TAG" "$N" "$T0" "$T1" <<'PY'
import json, sys, glob
tag, n, t0, t1 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
rs = [json.load(open(f)) for f in sorted(glob.glob(f'artifacts/ef/{tag}_n{n}_*.json'))]
tot = sum(r['n_samples'] for r in rs)
rec = {'tag': tag, 'n_jobs': n, 'wall_s': round(t1 - t0, 2), 'samples_total': tot,
       'samples_per_s_aggregate': round(tot / (t1 - t0), 1),
       'per_job_sample_wall_s': [r['sample_wall_s'] for r in rs],
       'per_job_samples_per_s': [r['samples_per_s'] for r in rs],
       'per_job_end_to_end_s': [r.get('end_to_end_s') for r in rs],
       'per_job_peak_alloc_gb': [r['peak_alloc_gb'] for r in rs],
       'accepted_total': sum(r.get('accepted_samples', 0) for r in rs)}
json.dump(rec, open(f'artifacts/ef/cotenancy_{tag}_n{n}.json', 'w'), indent=1)
print(json.dumps(rec))
PY
