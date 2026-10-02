#!/usr/bin/env python3
"""mcts_value_train.py -- train the value head on frozen-trunk features and report its calibration (run `mcts-a`).

Train on the states of the non-held-out theorems of one or more `mcts_value_data.py` files; report on the held-out
theorems' states (a tenth of rl_targets + generator theorems, chosen by name hash -- no evaluation pool is involved):
  * solvable: Brier score, AUC (state solvable at all vs never), and a 10-bin reliability table of predicted
    sigmoid(s) against the observed success fraction, weighted by attempts;
  * steps-to-go: on states with a success, MAE and Spearman of predicted d against the observed mean, and the table
    of mean predicted d per observed steps-to-go;
  * the search value v = sigmoid(s) * gamma^d against the observed gamma-discounted success (mean over attempts of
    success * gamma^steps-to-go).

  python mcts_value_train.py --data vdata_s0_r8.pt --out ckpts/mcts/value_s0_r8.pt --report artifacts/mcts/value_s0_r8.json
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn.functional as F
import value_head


def auc(scores, labels):
    o = sorted(zip(scores, labels))
    pos = sum(labels); neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return float('nan')
    r = 0.0; seen_neg = 0
    i = 0
    while i < len(o):
        j = i
        while j < len(o) and o[j][0] == o[i][0]:
            j += 1
        p = sum(l for _, l in o[i:j]); q = (j - i) - p
        r += p * (seen_neg + q / 2)
        seen_neg += q
        i = j
    return r / (pos * neg)


def spearman(a, b):
    def rk(x):
        o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
        for k, i in enumerate(o):
            r[i] = k
        return r
    ra, rb = rk(a), rk(b)
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = math.sqrt(sum((x - ma) ** 2 for x in ra)); vb = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return cov / (va * vb) if va and vb else float('nan')


def load(paths):
    D = [torch.load(p) for p in paths]
    out = {}
    for k in ('feats', 'n', 'succ', 'stg', 'depth'):
        out[k] = torch.cat([d[k] for d in D])
    out['held'] = torch.cat([d['heldout_thm'][d['ti']] for d in D])
    return out


def evaluate(head, X, n, succ, stg, gamma):
    with torch.no_grad():
        s, d = head(X)
    p = torch.sigmoid(s)
    frac = succ / n
    w = n
    brier = float(((p - frac) ** 2 * w).sum() / w.sum())
    a = auc(p.tolist(), (succ > 0).long().tolist())
    rel = []
    for b in range(10):
        m = (p >= b / 10) & (p < (b + 1) / 10 if b < 9 else p <= 1.0)
        if m.sum() > 0:
            rel.append(dict(bin=f'{b / 10:.1f}-{(b + 1) / 10:.1f}', states=int(m.sum()), attempts=int(w[m].sum()),
                            pred=round(float((p[m] * w[m]).sum() / w[m].sum()), 4),
                            obs=round(float((frac[m] * w[m]).sum() / w[m].sum()), 4)))
    pos = succ > 0
    mstg = stg[pos] / succ[pos]
    dp = d[pos]
    mae = float((dp - mstg).abs().mean()) if pos.any() else float('nan')
    sp = spearman(dp.tolist(), mstg.tolist()) if pos.any() else float('nan')
    by = {}
    for t in sorted(set(mstg.round().long().tolist())):
        m = mstg.round().long() == t
        by[int(t)] = dict(states=int(m.sum()), pred_mean=round(float(dp[m].mean()), 3))
    v = p * gamma ** d.clamp(min=0)
    return dict(states=len(n), attempts=int(n.sum()), solvable_states=int(pos.sum()), brier=round(brier, 5),
                brier_const=round(float((((frac * w).sum() / w.sum() - frac) ** 2 * w).sum() / w.sum()), 5),
                auc_solvable=round(a, 4), reliability=rel, stg_mae=round(mae, 3), stg_spearman=round(sp, 4),
                stg_by_observed=by, v_mean=round(float(v.mean()), 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--epochs', type=int, default=30)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--batch', type=int, default=4096)
    ap.add_argument('--gamma', type=float, default=0.95)
    ap.add_argument('--hidden', type=int, default=512)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    D = load(a.data)
    X = D['feats'].float().to(dev)
    n, succ, stg = D['n'].to(dev), D['succ'].to(dev), D['stg'].to(dev)
    tr = (~D['held']).nonzero().squeeze(1).to(dev)
    te = D['held'].nonzero().squeeze(1).to(dev)
    head = value_head.ValueHead(X.shape[1], a.hidden, a.gamma).to(dev)
    opt = torch.optim.AdamW(head.parameters(), lr=a.lr, weight_decay=0.01)
    steps = a.epochs * math.ceil(len(tr) / a.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=steps, pct_start=0.1)
    hist = []
    for ep in range(a.epochs):
        perm = tr[torch.randperm(len(tr), device=dev)]
        tot = 0.0
        for i in range(0, len(perm), a.batch):
            b = perm[i:i + a.batch]
            s, d = head(X[b])
            frac = succ[b] / n[b]
            w = n[b].clamp(max=16)        # attempts through the state, capped so roots do not dominate
            l1 = (F.binary_cross_entropy_with_logits(s, frac, reduction='none') * w).sum() / w.sum()
            pos = succ[b] > 0
            l2 = F.smooth_l1_loss(d[pos], stg[b][pos] / succ[b][pos]) if pos.any() else d.sum() * 0
            loss = l1 + 0.5 * l2
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
            tot += float(loss) * len(b)
        hist.append(round(tot / len(tr), 5))
    head.eval()
    rep = dict(data=a.data, train_states=len(tr), heldout_states=len(te), loss_by_epoch=hist,
               heldout=evaluate(head, X[te], n[te], succ[te], stg[te], a.gamma),
               train=evaluate(head, X[tr[:len(te) * 3]], n[tr[:len(te) * 3]], succ[tr[:len(te) * 3]],
                              stg[tr[:len(te) * 3]], a.gamma),
               args=vars(a))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    os.makedirs(os.path.dirname(a.report) or '.', exist_ok=True)
    value_head.save(a.out, head.cpu(), extra=dict(report=a.report))
    json.dump(rep, open(a.report, 'w'), indent=1)
    h = rep['heldout']
    print(json.dumps(dict(brier=h['brier'], brier_const=h['brier_const'], auc=h['auc_solvable'], stg_mae=h['stg_mae'],
                          stg_spearman=h['stg_spearman'])))


if __name__ == '__main__':
    main()
