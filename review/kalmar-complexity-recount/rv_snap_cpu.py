#!/usr/bin/env python3
"""CPU re-score of a kalmar-pretrain checkpoint on the first K tf1200 records (canonical names, base 0), compared state
by state with the per-state code the pod wrote into artifacts/kc/b1_snap.json (B1-snap).

  ~/.venv-torch/bin/python rv_snap_cpu.py --ckpt stage1_kalD_s0.pt --records 40

Own scoring loop: the state tokens and the action tokens + <eos> are concatenated; the code of a pair is the sum over
the action + <eos> positions of -log softmax(logits)[next token] (fp32 on CPU).  Also reports greedy exactness per state
(every action token and <eos> is the argmax given the correct prefix).
"""
import argparse, json, os, sys, time, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS)
import torch, torch.nn.functional as F
torch.set_num_threads(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', default='stage1_kalD_s0.pt')
    ap.add_argument('--records', type=int, default=40)
    a = ap.parse_args()
    from model import load_ckpt
    from state_env import decompose
    model, tok, extra = load_ckpt(os.path.join(WS, 'ckpts/kc_src', a.ckpt), 'cpu')
    model.eval()
    snap = json.load(open(os.path.join(WS, 'artifacts/kc/b1_snap.json')))['models'][f'ckpts/kc_src/{a.ckpt}']
    ref = snap['per_state_nats']
    t0 = time.time()
    mine, tags = [], []
    exact = []
    recs = [json.loads(l) for l in open(os.path.join(WS, 'data/kalmar/tf1200_kal_sl.jsonl'))][:a.records]
    for r in recs:
        kt = r['kal_tags']; kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        for (st, act, h), tg in zip(steps, kt):
            s_ids = tok.encode_toks(st)
            a_ids = tok.encode_toks(act) + [tok.eos]
            x = torch.tensor([s_ids + a_ids])
            with torch.no_grad():
                h_, _ = model.features(x[:, :-1])
                lg = model.head(model.ln_f(h_)).float()[0]
            tgt = x[0, 1:]
            lp = F.log_softmax(lg, -1)
            pos = range(len(s_ids) - 1, len(s_ids) + len(a_ids) - 1)
            code = -sum(float(lp[p, tgt[p]]) for p in pos)
            ex = all(int(lg[p].argmax()) == int(tgt[p]) for p in pos)
            mine.append(code); tags.append(tg); exact.append(ex)
    n = len(mine)
    diffs = [abs(m - r_) for m, r_ in zip(mine, ref[:n])]
    rel = sum(mine) / sum(ref[:n]) - 1
    out = {'ckpt': a.ckpt, 'records': a.records, 'states': n, 'sum_mine_nats': sum(mine), 'sum_pod_nats': sum(ref[:n]),
           'rel_diff_total': rel, 'max_abs_diff': max(diffs), 'median_abs_diff': sorted(diffs)[n // 2],
           'states_absdiff_gt_0.05': sum(d > 0.05 for d in diffs), 'greedy_exact_rate': sum(exact) / n,
           'secs': time.time() - t0}
    json.dump(out, open(os.path.join(HERE, 'out', f'snap_cpu_{a.ckpt[:-3]}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
