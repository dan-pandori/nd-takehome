#!/usr/bin/env bash
# status.sh [pod ...]: VPS-side one-line-per-pod summary: current job, finished samples, vLLM throughput / queue.
W=/home/dan/work/olmo-ifomega
for pod in ${@:-oif-a oif-b}; do
  bash $W/pod/olmo_ifomega/w.sh sh $pod 'L=artifacts/olmo_ifomega/logs; J=$(grep -o "RUNQ start [^ ]*" $L/runq_F*.log 2>/dev/null | tail -1 | cut -d" " -f3);
    S=$(grep -o "samples=[0-9]* gen_tok=[0-9]*" $L/q_$J.log 2>/dev/null | tail -1);
    T=$(grep "generation throughput" $L/q_$J.log 2>/dev/null | tail -1 | grep -o "generation throughput: [0-9.]*\|Running: [0-9]*\|Waiting: [0-9]*\|usage: [0-9.]*" | tr "\n" " ");
    D=$(ls artifacts/olmo_ifomega/meta/*.done 2>/dev/null | xargs -n1 basename 2>/dev/null | tr "\n" " ");
    echo "'$pod' $(date -u +%T) job=$J $S | $T| done: $D"' 2>/dev/null || echo "$pod unreachable"
done
