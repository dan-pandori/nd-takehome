#!/usr/bin/env bash
# Compact status: ladder steps per pod, failures, reader done counts.
for p in gb-p0 gb-p1 gb-p2 gb-p3 gb-p4 gb-p5; do
  podrun $p "cd /workspace/nd-takehome; for f in artifacts/gb/gb_*/steps.jsonl; do n=\$(basename \$(dirname \$f)); echo -n \"\${n#gb_}:\$(wc -l < \$f) \"; done; grep -l -E 'Traceback|Error' artifacts/gb/logs/gb_*.log 2>/dev/null | tr '\n' ' '; ls artifacts/gb/ | grep -E 'pair\.(done|fail)'; echo" 2>&1 | sed "s/^/$p /" | head -c 300; echo
done | grep .
for p in gb-r0 gb-r1; do podrun $p "cd /workspace/nd-takehome; echo $p reads done \$(ls artifacts/gb/eval/.done_* 2>/dev/null | wc -l) failed \$(grep -c 'READ FAILED' artifacts/gb/logs/reader.log); grep -E 'Traceback' artifacts/gb/logs/reader.log | head -n 2"; done
