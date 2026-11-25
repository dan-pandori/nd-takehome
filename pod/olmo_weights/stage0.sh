#!/usr/bin/env bash
# Stage 0 (one pod): hf_xet / hf_transfer throughput at 1-8 concurrent files, sha256 rate, and statistics time for one
# 7B pair (stage-1 1,000 -> 2,000) and one 32B pair (stage-1 0 -> 1,000) on GPU and CPU, plus a numpy cross-check.
cd /workspace/nd-takehome; A=artifacts/olmo_weights; S=$A/stage0; mkdir -p $S
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0
J=olmo_weights/manifest/jobs_stage0.json
date -u +"%FT%TZ stage0 start"
python olmo_weights/dl_bench.py --p 1 --files 7B/s1/1000:0 --mode xet
python olmo_weights/dl_bench.py --p 1 --files 7B/s1/1000:1 --mode transfer
python olmo_weights/dl_bench.py --p 2 --files 7B/s1/1000:2,7B/s1/2000:0 --mode xet
python olmo_weights/dl_bench.py --p 4 --files 7B/s1/2000:1,7B/s1/2000:2,32B/s1/0:0,32B/s1/0:1 --mode xet
echo "memory.max $(cat /sys/fs/cgroup/memory.max 2>/dev/null)"; df -h /dev/shm /root | tail -2
python olmo_weights/dl_bench.py --p 4 --files 32B/s1/0:10,32B/s1/0:11,32B/s1/0:12,32B/s1/0:13 --mode xet --work /root/dl_bench
python olmo_weights/dl_bench.py --p 8 --files 32B/s1/0:2,32B/s1/0:3,32B/s1/0:4,32B/s1/0:5,32B/s1/0:6,32B/s1/0:7,32B/s1/0:8,32B/s1/0:9 --mode xet
du -sh ~/.cache/huggingface/xet 2>/dev/null | sed 's/^/xet cache /'
date -u +"%FT%TZ engine 7B gpu"
python olmo_weights/engine.py --job s0_7b --jobs $J --out $S/gpu --work /workspace/dl --device cuda --inflight 6 --keep 1 --disk-cap-gb 100 2>&1 | tail -4
date -u +"%FT%TZ engine 7B cpu"
python olmo_weights/engine.py --job s0_7b --jobs $J --out $S/cpu --work /workspace/dl_cpu --device cpu --local-root /workspace/dl/s0_7b --verify 0 --disk-cap-gb 100 2>&1 | tail -2
python olmo_weights/realcheck.py --a /workspace/dl/s0_7b/7B_s1_1000 --b /workspace/dl/s0_7b/7B_s1_2000 --label-a 7B/s1/1000 --label-b 7B/s1/2000 --stats $S/gpu/s0_7b \
  --tensors model.embed_tokens.weight,model.layers.0.self_attn.q_proj.weight,model.layers.31.mlp.down_proj.weight,model.norm.weight,lm_head.weight
rm -rf /workspace/dl/s0_7b /workspace/dl_cpu
date -u +"%FT%TZ engine 32B gpu"
python olmo_weights/engine.py --job s0_32b --jobs $J --out $S/gpu --work /workspace/dl --device cuda --inflight 8 --keep 1 --disk-cap-gb 200 2>&1 | tail -4
date -u +"%FT%TZ engine 32B cpu (shards 0,1)"
python olmo_weights/engine.py --job s0_32b --jobs $J --out $S/cpu --work /workspace/dl_cpu --device cpu --local-root /workspace/dl/s0_32b --verify 0 --disk-cap-gb 200 --shards 0,1 2>&1 | tail -2
python olmo_weights/realcheck.py --a /workspace/dl/s0_32b/32B_s1_0 --b /workspace/dl/s0_32b/32B_s1_1000 --label-a 32B/s1/0 --label-b 32B/s1/1000 --stats $S/gpu/s0_32b \
  --tensors model.embed_tokens.weight,model.layers.0.self_attn.q_proj.weight,model.norm.weight
rm -rf /workspace/dl /workspace/dl_cpu
date -u +"%FT%TZ stage0 done"
touch $S/DONE
