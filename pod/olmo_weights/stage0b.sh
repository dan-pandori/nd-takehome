#!/usr/bin/env bash
# Stage 0b: the engine with the GPU cache, downloading to the container disk, on multi-member chains (steady state).
cd /workspace/nd-takehome; A=artifacts/olmo_weights; S=$A/stage0; mkdir -p $S
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0
J=olmo_weights/manifest/jobs_stage0b.json
date -u +"%FT%TZ stage0b 7B chain"
python olmo_weights/engine.py --job s0b_7b --jobs $J --out $S/gpu --work /root/dl --device cuda --inflight 6 --disk-cap-gb 36 2>&1 | tail -3
date -u +"%FT%TZ stage0b 32B chain"
python olmo_weights/engine.py --job s0b_32b --jobs $J --out $S/gpu --work /root/dl --device cuda --inflight 6 --disk-cap-gb 36 2>&1 | tail -3
date -u +"%FT%TZ stage0b done"; df -h /root | tail -1
touch $S/DONE_b
