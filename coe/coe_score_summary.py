#!/usr/bin/env python3
"""create-or-elicit: E2's second estimate -- teacher-forced log p (cd_score, one name base) of the full arm's known proofs of
the strict sigma-covered members under each knockout base and trajectory's full pend s0.  One base gives log pi(y | b0);
log pi(y) >= that - ln 33 (the sampler draws the name base from 33), so every number below is a valid LOWER bound after
subtracting ln 33 (reported both ways).  Per member: best known proof (max) and the known-proof sum (logsumexp).

  python3 coe/coe_score_summary.py --dir artifacts/coe/score/known_b1 --out artifacts/coe/score/summary.json
"""
import argparse, collections, gzip, json, math, os, statistics


def lse(xs):
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--T', default='T0.8')
    a = ap.parse_args()
    tg = {}
    for l in gzip.open(os.path.join(a.dir, 'targets.jsonl.gz'), 'rt'):
        t = json.loads(l); tg[t['tid']] = t
    src = {}
    for l in gzip.open('data/coe/known_targets.jsonl.gz', 'rt'):
        x = json.loads(l); src[x['tid']] = x
    LN33 = math.log(33)
    res = {}
    for fn in sorted(os.listdir(a.dir)):
        if not fn.endswith('.jsonl.gz') or fn.startswith('targets'):
            continue
        ck = fn[:-len('.jsonl.gz')]
        per = collections.defaultdict(list)
        worst = collections.defaultdict(list)
        for l in gzip.open(os.path.join(a.dir, fn), 'rt'):
            r = json.loads(l)
            x = src[r['tid']]
            per[(x['group'], x['name'])].append((r[a.T]['total'], r[a.T]['w1'], r[a.T]['w1_kind']))
        out = {}
        for grp in ('heldout', 'trained'):
            best, sums, w1b, kinds = [], [], [], collections.Counter()
            for (g, n), v in per.items():
                if g != grp:
                    continue
                bt = max(v, key=lambda z: z[0])
                best.append(bt[0]); w1b.append(bt[1]); kinds[bt[2]] += 1
                sums.append(lse([z[0] for z in v]))
            out[grp] = {'members': len(best), 'best_median': statistics.median(best), 'best_max': max(best),
                        'best_p90': sorted(best)[int(0.9 * len(best))], 'sum_median': statistics.median(sums), 'sum_max': max(sums),
                        'worst_step_median_at_best': statistics.median(w1b), 'worst_step_kind_at_best': dict(kinds.most_common(4)),
                        'per_member_best': {n: round(max(z[0] for z in v), 3) for (g, n), v in per.items() if g == grp}}
        res[ck] = out
    json.dump({'T': a.T, 'note': 'one name base: subtract ln 33 = 3.50 for a valid lower bound on log pi', 'ckpts': res},
              open(a.out, 'w'), indent=1)
    print(f'teacher-forced log p at {a.T}, one name base (lower bound: subtract ln 33 = {LN33:.2f})')
    print('| checkpoint | held-out members | best known proof: median / max | known-proof sum: median / max | worst step at the best proof (median, kind) | trained: best median / max |')
    print('|---|---|---|---|---|---|')
    for ck, o in res.items():
        h, t = o['heldout'], o['trained']
        print(f"| {ck} | {h['members']} | {h['best_median']:.1f} / {h['best_max']:.1f} | {h['sum_median']:.1f} / {h['sum_max']:.1f} | "
              f"{h['worst_step_median_at_best']:.1f} {h['worst_step_kind_at_best']} | {t['best_median']:.1f} / {t['best_max']:.1f} |")


if __name__ == '__main__':
    main()
