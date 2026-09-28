#!/usr/bin/env bash
# Run jobs sequentially: each line of the queue file is "<jobname> <command...>".  Usage: bash pod/sf/queue.sh <queuefile>
# (Each job's LEAN_GATE_DUMP / log / .done marker as bg.sh.)  The queue file is copied first, so editing it later is safe.
cd /workspace/nd-takehome; Q=$(mktemp); cp "$1" $Q
while read -r J CMD; do
  [ -z "$J" ] && continue; [ -f artifacts/sf2/$J.done ] && continue
  ( source pod/sf/env.sh; export LEAN_GATE_DUMP=artifacts/sf2/dumps/$J.jsonl LEAN_GATE_LOG=artifacts/sf2/logs/$J.gate.jsonl
    bash -c "$CMD" < /dev/null > artifacts/sf2/logs/$J.log 2>&1 && touch artifacts/sf2/$J.done || touch artifacts/sf2/$J.fail )
done < $Q
