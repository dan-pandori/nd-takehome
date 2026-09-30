#!/usr/bin/env bash
# run a resumable job up to 5 times (CUDA OOM under co-tenancy); usage: retry.sh <cmd...>
for i in 1 2 3 4 5; do "$@" && exit 0; echo "retry.sh: attempt $i failed, retrying in 60 s"; sleep 60; done; exit 1
