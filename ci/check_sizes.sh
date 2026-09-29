#!/bin/sh
# Size guard (run repo-hygiene-2): fail if the index holds a file over 5 MB, or a bulk kind (.jsonl, .jsonl.gz, .pt)
# under artifacts/ other than artifacts/MANIFEST.jsonl. Bulk files go to the bucket with publish_artifacts.py.
# Checks the index, so the same script serves the pre-commit hook (staged state) and CI (a fresh checkout = HEAD).
#   sh ci/check_sizes.sh          # exit 1 and list the offenders
cd "$(git rev-parse --show-toplevel)" || exit 2
LIMIT=5242880
bad=$(git ls-files -s | awk -F'\t' '{split($1, m, " "); if (m[1] != "160000") print m[2] " " $2}' \
  | git cat-file --batch-check='%(objectsize) %(rest)' \
  | awk -v L=$LIMIT '{sz = $1; p = substr($0, length($1) + 2);
         if (sz > L) print "over 5 MB (" sz " bytes): " p;
         else if (p ~ /^artifacts\// && p != "artifacts/MANIFEST.jsonl" && p ~ /\.(jsonl|jsonl\.gz|pt)$/) print "bulk kind under artifacts/: " p}')
if [ -n "$bad" ]; then
  echo "FAIL size guard: $(echo "$bad" | wc -l) file(s) must not be tracked (CONTRIBUTING.md: publish_artifacts.py):"
  echo "$bad" | head -20
  exit 1
fi
echo "size guard ok: no tracked file over 5 MB, no bulk kind under artifacts/"
