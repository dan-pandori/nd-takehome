#!/usr/bin/env bash
# one bucket path -> download to /tmp, summarise, delete (disk footprint: one file per worker)
p="$1"; out=/home/dan/review/lit-measures/rv/m3/$(echo "$p" | tr / _).json
[ -s "$out" ] && exit 0
t=/tmp/rvm3/$(echo "$p" | tr / _)
timeout 900 hf buckets cp "hf://buckets/dan-pandori/nd-rl/$p" "$t" >/dev/null 2>&1 || { echo "FETCH_FAIL $p"; rm -f "$t"; exit 0; }
python3 /home/dan/review/lit-measures/rv/m3_one.py "$t" "$out" || echo "SUM_FAIL $p"
rm -f "$t"
