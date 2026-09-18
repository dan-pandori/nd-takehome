#!/usr/bin/env bash
# round3-run4a: rebuild the cap-6 pool from reachable generator sets and assemble the f = 0 reductio set (assembler seed 41).
set -e
cd /workspace/nd-takehome
python3 r3_4a_pool.py --sets data/p2/train_depth3_f0_a1.jsonl data/r2/train_r2_struct.jsonl data/r2/train_r2_impi_ore_f0.jsonl data/r2/train_r2_negi_ande_hyp_f0.jsonl data/r2/train_r2_ori_ore_f0.jsonl --out data/r3_4a/pool_cap6_r4a.jsonl
python3 make_coverage_sets.py assemble --pool data/r3_4a/pool_cap6_r4a.jsonl --outdir data/r3_4a --patterns reductio --freqs 0 \
  --heldout_file data/p2/heldout.jsonl --suffix _b1 --seed 41 \
  --exclude data/p2/targets_reductio_req.jsonl data/p2/transfer_reductio_req.jsonl data/p2/targets_reductio.jsonl data/p2/transfer_reductio.jsonl \
            data/p2/targets_reductio2.jsonl data/p2/transfer_reductio2.jsonl data/r3_2/targets_reductio_req6.jsonl
touch data/r3_4a/build_set.done
