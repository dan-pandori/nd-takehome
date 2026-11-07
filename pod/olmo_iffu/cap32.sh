#!/usr/bin/env bash
# cap32.sh (pod): deviation 4 of olmo-iffu. While T4_s0750 samples, every 30 s add to its stop file each prompt with
# >= 16 rows (its first chunk done, so its second chunk is its last): T4's cap becomes 32 fresh draws per prompt
# (48 for the few prompts whose third chunk was already in flight when this started).
cd /workspace/nd-takehome
while pgrep -f 'olmo_iffu/[s]ample.py.*T4_s0750' > /dev/null; do
  python3 - <<'PY'
import collections, gzip, json
n = collections.Counter()
try:
    with gzip.open('artifacts/olmo_iffu/samples/T4_s0750.jsonl.gz', 'rt') as f:
        for l in f:
            try:
                n[json.loads(l)['pid']] += 1
            except Exception:
                break
except Exception:
    pass
stop = set(open('olmo_iffu/plan/T4_s0750.stop').read().split())
new = [p for p, c in n.items() if c >= 16 and p not in stop]
if new:
    with open('olmo_iffu/plan/T4_s0750.stop', 'a') as g:
        g.write(' '.join(new) + '\n')
    print(len(new), 'added', flush=True)
PY
  sleep 30
done
echo "CAP32_DONE $(date -u +%FT%TZ)"
