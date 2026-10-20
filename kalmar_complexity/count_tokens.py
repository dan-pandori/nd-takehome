#!/usr/bin/env python3
"""Exact token counts of the training pairs, as state_train builds them (run kalmar-complexity, for B1).

  python3 kalmar_complexity/count_tokens.py data/kh/train_k12.jsonl artifacts/kc/tokens_k12.json
  python3 kalmar_complexity/count_tokens.py data/kalmar/train_kal_sl.jsonl.gz artifacts/kc/tokens_kal_sl.json

Each record -> `state_env.decompose(prompt, proof, canon=True)` (mode `lean_staten`, as `state_train._pairs`).  A pair is
(state tokens, action tokens + <eos>); the loss is on the action tokens and <eos> (`state_train_best.make_batch`), so
the loss tokens of a pair = len(action) + 1.  Totals, and per step tag when the record carries `tags`.
"""
import collections, gzip, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_env import decompose


def main(fn, out):
    op = gzip.open if fn.endswith('.gz') else open
    t0 = time.time()
    n_rec = n_skip = n_pairs = s_state = s_loss = 0
    per = collections.defaultdict(lambda: [0, 0])          # tag -> [pairs, loss tokens]
    with op(fn, 'rt') as fh:
        for line in fh:
            r = json.loads(line)
            n_rec += 1
            try:
                steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
            except Exception:
                n_skip += 1
                continue
            tags = r.get('tags')
            if isinstance(tags, str):
                tags = json.loads(tags.replace("'", '"'))
            for j, (st, act, hs) in enumerate(steps):
                n_pairs += 1
                s_state += len(st)
                s_loss += len(act) + 1
                if tags:
                    p = per[tags[j]]
                    p[0] += 1
                    p[1] += len(act) + 1
            if n_rec % 10000 == 0:
                print(n_rec, n_pairs, f'{time.time() - t0:.0f}s', flush=True)
    res = {'file': fn, 'records': n_rec, 'skipped': n_skip, 'pairs': n_pairs, 'state_tokens': s_state,
           'loss_tokens': s_loss, 'pair_tokens': s_state + s_loss, 'per_tag': dict(per), 'secs': time.time() - t0}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'per_tag'})


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
