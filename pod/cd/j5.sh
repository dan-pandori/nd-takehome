#!/usr/bin/env bash
# J5 (pre-registered in log.md before launch): missing plain draws, trajectory's read settings (k 256, T 0.8,
# max_steps 96, max_action 512, batch 2,048): cap-12 r16 on tb72 + h250 at sample seed 0 (x0; rl-continue read only
# x1), and cap-6 r16 on all of holdout250 at seed 1 (rl-continue-cap6 read only its C subset).  Resumable.
. pod/cd/env.sh
rd() {  # ckpt out in seed lenfield
  [ -s $2.json ] && { echo "skip $2"; return; }
  echo "$(date -u +%FT%TZ) start $2"
  ND_ARM=j5_read python3 state_eval.py --ckpt $1 --in $3 --out $2.jsonl --summary $2.json --k 256 --temperature 0.8 --seed $4 \
    --batch 2048 --max_action 512 --max_steps 96 --lenfield $5
  echo "$(date -u +%FT%TZ) end $2 rc=$?"
}
mkdir -p artifacts/cd/j5
for s in 0 1 2; do
  rd $CK/s${s}_r16.pt artifacts/cd/j5/s${s}_r16__tb72_x0 data/bs/textbook72.jsonl 0 reference_lines
  rd $CK/s${s}_r16.pt artifacts/cd/j5/s${s}_r16__h250_x0 data/bs/holdout250.jsonl 0 n_lines
  rd $CK/c6_s${s}_r16.pt artifacts/cd/j5/c6_s${s}_r16__h250_x1 data/bs/holdout250.jsonl 1 n_lines
done
