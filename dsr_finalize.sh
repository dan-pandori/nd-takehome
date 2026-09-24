#!/usr/bin/env bash
# One command that turns whatever the pods have produced into this run's deliverables.
# Written so that a short or interrupted session can still land the run:
#   bash dsr_finalize.sh            # pull, re-derive every number, regenerate numbers.md + figures, commit, upload
# Idempotent. Does NOT write run_ds_rendering.md (that needs judgement) and does NOT delete pods.
set -u
cd /home/dan/work/ds-rendering

echo "== 1. pull every pod that still exists"
bash pod/dsr/pull.sh

echo "== 2. re-derive every number from the pulled raw files"
python3 dsr_analysis.py || exit 1

echo "== 3. regenerate the numbers.md section (replacing any previous one) and the figures"
python3 - <<'PY'
import subprocess, re
new = subprocess.run(['python3', 'dsr_numbers.py'], capture_output=True, text=True, check=True).stdout
cur = open('numbers.md').read()
mark = '\n# ds-rendering (proposal 10)'
i = cur.find(mark)
cur = cur[:i] if i >= 0 else cur.rstrip() + '\n'
open('numbers.md', 'w').write(cur.rstrip() + '\n' + new)
print('numbers.md § ds-rendering rewritten (%d lines)' % new.count('\n'))
PY
python3 dsr_figures.py || exit 1

echo "== 4. commit"
git add -A
git -c user.name='agent:claude' -c user.email='noreply@anthropic.com' commit -q -m "ds-rendering: regenerate numbers.md and figures from the current artefacts

Edited-by: agent:claude
Agent-role: executor
Run-id: ds-rendering
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" 2>/dev/null && git push -q origin dan_ds-rendering && echo pushed || echo "nothing to commit"

# The pods CANNOT upload: hf is absent from the RunPod image (log.md 2026-09-23 23:45). The host does it, and
# dsr_upload.sh keeps the per-pod layout instead of flattening every pod's artefacts into one directory.
echo "== 5. upload from the host"
bash dsr_upload.sh 2>&1 | grep -E '^==|FAILED'
hf buckets sync data/r3_1 hf://buckets/dan-pandori/nd-rl/ds-rendering/data/r3_1 2>&1 | tail -1

echo "== done"; date -u +%FT%TZ; podbudget ds-rendering
