#!/usr/bin/env bash
# One status line per pod: current job, finished samples, vLLM throughput / resident / waiting.
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
for p in "$@"; do
  podrun $p 'L=$(ls -t artifacts/olmo_pilot/logs/q_*.log 2>/dev/null | head -1); J=$(basename "$L" .log); T=$(grep -E "Avg generation throughput" $L | tail -1 | sed -E "s/.*INFO [0-9-]+ ([0-9:]+).*generation throughput: ([0-9.]+) tokens\/s, Running: ([0-9]+) reqs, Waiting: ([0-9]+) reqs.*/\1 gen=\2 run=\3 wait=\4/"); S=$(grep -hE "^\[" $L | tail -1 | sed -E "s/.*samples=([0-9]+) gen_tok=([0-9]+).*length_cut=([0-9]+)/done=\1 tok=\2 cut=\3/"); D=$(ls artifacts/olmo_pilot/meta/ | grep -c "\.done$"); echo "'$p' $J | $T | $S | done_markers=$D"' 2>&1 | tail -1
done
