#!/usr/bin/env bash
# Phase 1 (style-edl), CPU: S_short's minlen search on all of tf1200 (bound 14, 120 s per theorem).
. pod/sedl/env.sh
P=${1:-4}
pod/sedl/job.sh minlen python3 style_edl/search_short.py --in data/kalmar/tf1200_kal_sl.jsonl --out data/style_edl/short/tf1200_minlen14.jsonl --bound 14 --time 120 --procs $P
up data/style_edl/short
echo "QUEUE DONE $(date -u +%FT%TZ)"
