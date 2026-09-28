#!/usr/bin/env bash
# Before `podrm <pod>`: list every file the pod holds under artifacts/, ckpts/ and data/ that is NOT already
# in this worktree.  Written after deleting sc2 having checked only artifacts/sc/*.jsonl and thereby losing
# ckpts/ladder/la_T1_sc_s1_r*.pt.  Prints nothing and exits 0 when it is safe to delete.
set -u
P=$1
WT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
miss=0
for d in artifacts ckpts data; do
  for f in $(podrun "$P" "find $d -type f 2>/dev/null" 2>/dev/null); do
    [ -e "$WT/$f" ] || { echo "MISSING LOCALLY: $f"; miss=$((miss+1)); }
  done
done
[ "$miss" = 0 ] && echo "$P: everything pulled, safe to podrm" || echo "$P: $miss file(s) NOT pulled -- do not podrm"
exit $miss
