#!/usr/bin/env bash
# Acceptance table from the pulled files: ~/runs/podjob/tests/{T*.txt,local/,*.bucket.txt} and ~/podjob.log
cd "${1:-$(dirname "$0")}"; L=local/artifacts   # the podjob.log grep needs ~/podjob.log (excerpt: podjob.log.excerpt)
printf "%-4s %-22s %-5s %-6s %-26s %s\n" test name exit gone_s "reference" bucket_files
for t in T1 T2 T3 T4 T5; do
  n=$(awk '/^test/{print $4}' $t.txt); ex=$(awk '/^podjob exit/{print $3}' $t.txt); ab=$(awk '/^absent/{print $NF}' $t.txt)
  case $t in T3|T5) ref=$(awk '/^kill/{print $NF}' $t.txt); rn="signal";;
    *) ref=$(cat $L/podjob/$n/job*.rc 2>/dev/null | awk '{print $2}' | sort -n | tail -1); rn="last job end (pod clock)";; esac
  nb=$(grep -c "podjob/artifacts/pjtest/$t/" $t.bucket.txt 2>/dev/null)
  printf "%-4s %-22s %-5s %-6s %-26s %s\n" $t $n "$ex" $((ab-ref)) "$rn" "$nb"
done
echo "--- T4 (pack 3): host, start, end per job; one pod?"
for f in $L/pjtest/T4/{a,b,c}.txt; do tr '\n' ' ' < $f; echo; done
awk '/T4/ && /READY/' ~/podjob.log | cut -c1-80
echo "--- T4 job wall (first start -> last end, pod clock): $(( $(cat $L/pjtest/T4/*.txt | sed -n 's/^end=//p' | sort -n | tail -1) - $(cat $L/pjtest/T4/*.txt | sed -n 's/.*start=//p' | sort -n | head -1) )) s"
echo "--- podhours.log"; grep pj-podjob ~/podhours.log
