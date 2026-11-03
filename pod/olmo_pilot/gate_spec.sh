#!/usr/bin/env bash
# Speculative-decoding gate (pre-registration Part B): base, AIME 2023 pilot, 8 x 30, n-gram prompt lookup (4 drafts).
cd /workspace/nd-takehome
SAMPLE_EXTRA="--spec_ngram 4" bash pod/olmo_pilot/job.sh g_spec_base base allenai/Olmo-3-1025-7B main 8 @olmo_pilot/pilot_pids.txt 1003 0 8
echo "GATE_DONE $(date -u +%FT%TZ)"
