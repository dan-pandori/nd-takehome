#!/usr/bin/env bash
# J9 (pre-registered in log.md before launch): certification sampling.  pend_S on the theorems in data/cd/j9/s<S>.jsonl
# (chosen on the VPS by capability_defs/analysis/cd_j9_select.py), chunks of k 131,072 (seed 7500 + chunk), up to 9
# chunks = 1,179,648 attempts per theorem on top of J2's 65,536; a theorem leaves the queue at its first success.
# Standard read caps (96 steps, 512 tokens per action), T 0.8, batch 2048.  Rows are compacted on the pod (failure
# reasons counted, not listed).  Resumable per chunk.
. pod/cd/env.sh
S=$1; IN=data/cd/j9/s${S}.jsonl; D=artifacts/cd/j9; mkdir -p $D
[ -s $IN ] || { echo "missing $IN"; exit 1; }
for C in 0 1 2 3 4 5 6 7 8; do
  O=$D/s${S}_k${C}
  [ -s $O.json ] && { echo "skip $O"; continue; }
  python3 - $IN $S > $D/s${S}_in${C}.jsonl <<'EOF'
import glob, json, sys
inp, S = sys.argv[1], sys.argv[2]
hit = set()
for p in glob.glob(f'artifacts/cd/j9/s{S}_k*.jsonl'):
    for l in open(p):
        r = json.loads(l)
        if r['n_ok'] > 0:
            hit.add(r['name'])
for l in open(inp):
    if json.loads(l)['name'] not in hit:
        sys.stdout.write(l)
EOF
  [ -s $D/s${S}_in${C}.jsonl ] || { echo "$(date -u +%FT%TZ) every theorem has a success; stop"; break; }
  echo "$(date -u +%FT%TZ) start s${S}_k${C} seed $((7500 + C)) theorems $(wc -l < $D/s${S}_in${C}.jsonl)"
  ND_ARM=j9_pend_s${S} python3 state_eval.py --ckpt $CK/s${S}_pend.pt --in $D/s${S}_in${C}.jsonl --out $O.full.jsonl \
    --summary $O.json --k 131072 --temperature 0.8 --seed $((7500 + C)) --batch 2048 --max_action 512 --max_steps 96 \
    --lenfield n_lines
  RC=$?
  python3 - $O.full.jsonl $O.jsonl <<'EOF'
import collections, json, sys
with open(sys.argv[2], 'w') as f:
    for l in open(sys.argv[1]):
        r = json.loads(l)
        r['reasons'] = dict(collections.Counter(r.get('reasons') or []).most_common(20))
        r.pop('written_lens', None); r.pop('pruned_lens', None)
        f.write(json.dumps(r) + '\n')
EOF
  [ -s $O.jsonl ] && rm -f $O.full.jsonl
  echo "$(date -u +%FT%TZ) end s${S}_k${C} rc=$RC"
done
echo "$(date -u +%FT%TZ) J9 s$S done"
