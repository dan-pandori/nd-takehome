#!/usr/bin/env bash
# textbook72 references the bound-14 search left unlabelled: one minlen.py per theorem (bound 22), 60 min wall each.
source pod/tj/env.sh
one() { f=$1; timeout 3600 python3 minlen.py --in $f --out ${f%.jsonl}.out.jsonl --bound 22 --time 3500 --procs 1 > ${f%.jsonl}.log 2>&1; echo "$f exit $?"; }
export -f one
ls data/tj/ml22/in_*.jsonl | xargs -P 15 -I{} bash -c 'one {}'
cat data/tj/ml22/in_*.out.jsonl > data/tj/tb72_minlen22.jsonl 2>/dev/null; wc -l data/tj/tb72_minlen22.jsonl
