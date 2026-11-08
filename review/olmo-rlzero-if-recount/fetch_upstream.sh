#!/bin/bash
# Reviewer fetch of pinned upstream sources (sequential; one process). Output: ~/review/rzi_rv/upstream/
set -u
U=~/review/rzi_rv/upstream
gh_get() { repo=$1; sha=$2; path=$3; dst=$U/$4/$path; [ -s "$dst" ] && return; mkdir -p "$(dirname "$dst")"; curl -sfL -o "$dst" "https://raw.githubusercontent.com/$repo/$sha/$path" || echo "FAIL $repo $sha $path"; }
OI_D=d928a7cd29c2610af04300f817494c8e6dba977d
OI_S=7e780f2fea1217fad80665a1b754bd8bec4afd8f
OI_R=e25a27b8ea388c6a8fba84b38a70fa21c5fff5d7
for p in open_instruct/ground_truth_utils.py open_instruct/dataset_transformation.py open_instruct/grpo_fast.py open_instruct/if_functions.py open_instruct/IFEvalG/instructions.py open_instruct/IFEvalG/instructions_registry.py open_instruct/IFEvalG/instructions_util.py open_instruct/vllm_utils3.py; do gh_get allenai/open-instruct $OI_D $p oi_d928a7c; done
for p in scripts/train/olmo3/7b_rlzero_instruction_following.sh scripts/train/olmo3/7b_rlzero_math.sh scripts/train/olmo3/README.md open_instruct/dataset_transformation.py open_instruct/grpo_fast.py open_instruct/ground_truth_utils.py; do gh_get allenai/open-instruct $OI_S $p oi_7e780f2; done
for p in scripts/train/olmo3/README.md scripts/train/olmo3/7b_rlzero_instruction_following.sh; do gh_get allenai/open-instruct $OI_R $p oi_e25a27b; done
IFB=cd189a9c2889526d8af901d2103fd3e1ffcea6df
for p in evaluation_lib.py run_eval.py ifbench/__init__.py ifbench/classic_instructions.py ifbench/instructions.py ifbench/instructions_registry.py ifbench/instructions_util.py ifbench/data/IFBench_test.jsonl data/IFBench_test.jsonl; do gh_get allenai/IFBench $IFB $p ifbench; done
GR=e6890f85757dd84e27ca6df2dd30651dafad28e0
for p in instruction_following_eval/evaluation_lib.py instruction_following_eval/instructions.py instruction_following_eval/instructions_registry.py instruction_following_eval/instructions_util.py; do gh_get google-research/google-research $GR $p ife; done
echo FETCH DONE
