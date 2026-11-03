#!/usr/bin/env bash
# CPU side job: n-gram scan of the midtraining math/reasoning subsets (streams shards; deletes each after scanning).
cd /workspace/nd-takehome; A=artifacts/olmo_pilot; mkdir -p $A/contam /workspace/midscan
nice -n 10 python -u olmo_pilot/midscan.py olmo_pilot/problems.jsonl $A/contam/midscan.jsonl ${1:-6}
python olmo_pilot/contam.py merge $A/contam/midscan.csv $A/contam/midscan.jsonl.*
