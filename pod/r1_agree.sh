#!/usr/bin/env bash
# Agreement sweep on the VPS: nd_verify vs Lean on every pool. Outputs artifacts/r1/agree_<name>.jsonl
cd /home/dan/work/run1-lean; export PATH=$HOME/.elan/bin:$PATH
P=${PROCS:-2}
run() { n=$1; shift; echo "$(date -u +%T) start $n"; python3 nd2lean.py --check "$@" --out artifacts/r1/agree_$n.jsonl --procs $P --batch 100 2>&1 | tail -1; }
run heldout data/heldout.jsonl
run transfer_gen data/transfer.jsonl --field gen_proof
run rl_targets_gen data/rl_targets.jsonl --field gen_proof
run novelty_phase1 artifacts/novelty_phase1_proofs.jsonl
run depth3_f0_a1_s0 artifacts/p2/novelty_depth3_f0_a1_s0_proofs.jsonl
run depth3_f0_a1_s1 artifacts/p2/novelty_depth3_f0_a1_s1_proofs.jsonl
run reductio_f0_s0_t2 artifacts/p2/novelty_reductio_f0_s0_t2_proofs.jsonl
run minlen_transfer artifacts/minlen_transfer.jsonl
echo "$(date -u +%T) start mutations"
python3 nd2lean.py --mutate data/heldout.jsonl --n 2000 --seed 0 --out artifacts/r1/agree_mut_heldout.jsonl --procs $P --batch 50 2>&1 | tail -1
python3 nd2lean.py --mutate data/rl_targets.jsonl --n 2000 --seed 1 --out artifacts/r1/agree_mut_rl_targets.jsonl --procs $P --batch 50 2>&1 | tail -1
run train data/train.jsonl.gz
echo "$(date -u +%T) SWEEP DONE"
