#!/usr/bin/env bash
# reader_task.sh <batch>: print the full reader-subagent prompt for one batch (reader prompt + item list + output path).
B=$1; R=/home/dan/work/olmo-ifcurve; H=$R/artifacts/olmo_ifcurve/hand
cat $R/olmo_ifcurve/handcheck_prompt_if.md
echo
echo "Item files (read each one in full):"
sed "s|^|$H/items/|; s|$|.md|" $H/batches/$B.txt | grep -v '^$' | grep -v "items/.md"
echo
echo "Output path: $H/labels/$B.json"
echo
echo "Write the JSON list to the output path (python is fine). Then reply with ONE line only, e.g. \"DONE $B: 40 items, 31 genuine, 9 gamed\" — do not repeat the JSON in your reply unless writing the file failed."
