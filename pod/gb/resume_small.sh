#!/usr/bin/env bash
# resume.sh at decode batch 1,024 and lp_batch 128 (after an OOM in the update).  Usage: bash pod/gb/resume_small.sh <adv> <seed> <R>
B=1024 LP=128 bash pod/gb/resume.sh "$@"
