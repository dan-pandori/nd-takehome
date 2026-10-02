#!/usr/bin/env bash
# The CI test of grpo_state on the tiny ALiBiGPT, on a pod with CUDA hidden.  Usage: bash pod/gb/cputest.sh [steps] [temp]
source pod/gb/env.sh
export CUDA_VISIBLE_DEVICES= ND_OFFLINE=1 ND_REGISTRY_SYNC=0 ND_GRPO_TEST_ARCH=best
python3 tests/test_grpo_state.py
