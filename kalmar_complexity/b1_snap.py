#!/usr/bin/env python3
"""B1-snap: per-step-type teacher-forced code length of kalmar-pretrain checkpoints on tf1200 (run kalmar-complexity).

  python3 kalmar_complexity/b1_snap.py --ckpts a.pt,b.pt,... --out artifacts/kc/b1_snap.json [--per_state c.pt,...]

tf1200 = data/kalmar/tf1200_kal_sl.jsonl (1,200 held-out theorems with their Kalmár sl proofs and `kal_tags`; the
states of kalmar-pretrain's E1 read, 137,984).  Each proof -> `state_env.decompose(canon=True)` pairs, names at base 0
(in the training distribution: the trainer shifts names by s >= 0).  Code length of a pair = sum over its loss tokens
(action + <eos>) of -log p, in nats, bf16 autocast.  Output per checkpoint: total and per step tag (nats, loss tokens,
pairs).  `--per_state`: also the per-state code (nats) for those checkpoints, in record / state order.
"""
import argparse, collections, gzip, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity'))
import torch
from model import load_ckpt
from state_env import decompose
from b2_preq import code_pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', required=True)
    ap.add_argument('--data', default=os.path.join(ROOT, 'data/kalmar/tf1200_kal_sl.jsonl'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--per_state', default='')
    a = ap.parse_args()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    recs = [json.loads(l) for l in open(a.data)]
    pairs, tags = [], []
    for r in recs:
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        kt = r['kal_tags']
        kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
        assert len(kt) == len(steps)
        pairs.append([(st, act) for st, act, hs in steps])
        tags += kt
    out = {'data': a.data, 'records': len(recs), 'states': len(tags), 'models': {}}
    if os.path.exists(a.out):
        out = json.load(open(a.out))
    per_state = set(x for x in a.per_state.split(',') if x)
    for ck in [x for x in a.ckpts.split(',') if x]:
        if ck in out['models']:
            continue
        t0 = time.time()
        model, tok, extra = load_ckpt(ck, dev)
        enc = [[(bytes(tok.encode_toks(st)), bytes(tok.encode_toks(act) + [tok.eos])) for st, act in rec] for rec in pairs]
        res = code_pairs(model, enc, tags, dev, return_pairs=ck in per_state)
        tot, ntok, per = res[:3]
        cnt = collections.Counter(tags)
        row = {'nats': tot, 'loss_tokens': ntok, 'nats_per_token': tot / ntok,
               'per_tag': {t: {'nats': v[0], 'loss_tokens': v[1], 'pairs': cnt[t]} for t, v in per.items()},
               'steps': (extra or {}).get('steps'), 'secs': time.time() - t0}
        if ck in per_state:
            row['per_state_nats'] = [round(x, 5) for x in res[3]]
        out['models'][ck] = row
        print(f'{ck}: {tot / ntok:.5f} nats/token over {ntok:,} loss tokens, {time.time() - t0:.0f}s', flush=True)
        json.dump(out, open(a.out, 'w'))
        del model
    json.dump(out, open(a.out, 'w'))


if __name__ == '__main__':
    main()
