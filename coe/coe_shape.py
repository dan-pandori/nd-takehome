#!/usr/bin/env python3
"""create-or-elicit: what else the σ knockout shifts -- K12 vs K12- shape table.

Per set: records per length, rule shares (fraction of records using each ND rule), DN-cited-rule counts, σ / σ+ counts,
premise-count histogram, written box depth, term size (formula nodes over the pruned proof, kh_size's definition),
share of records whose theorem is classical-only (G4ip, intuit.py; computed on a seeded 20,000-record sample).

  python3 coe/coe_shape.py --sets data/coe/src/train_k12.jsonl.gz data/coe/train_k12ko.jsonl.gz --out artifacts/coe/shape_k12_vs_ko.json
"""
import argparse, collections, gzip, json, os, random, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from patterns import parse, prune_lines
from coe.coe_sigma import flags
from coe.coe_assemble import written_depth
from intuit import intuit_provable

RULES = ['PR', 'AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']


def fnodes(f):
    if f[0] in ('atom', 'bot'):
        return 1
    if f[0] == 'not':
        return 1 + fnodes(f[1])
    return 1 + fnodes(f[1]) + fnodes(f[2])


def shape(fn, sample_n=20000, seed=0):
    op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
    n = 0
    per_len, rule_rec, rule_lines = collections.Counter(), collections.Counter(), collections.Counter()
    nprem, wdepth, cited = collections.Counter(), collections.Counter(), collections.Counter()
    sig = collections.Counter()
    ts, ts_len = [], collections.defaultdict(list)
    lines_total = 0
    prompts = []
    for l in op:
        r = json.loads(l)
        n += 1
        L = r['n_lines']; per_len[L] += 1
        lines = parse(r['proof'])
        kept = prune_lines(lines)
        t = sum(fnodes(x['formula']) for x in kept)
        ts.append(t); ts_len[L].append(t)
        used = set()
        for x in lines:
            rule_lines[x['rule']] += 1; used.add(x['rule'])
        lines_total += len(lines)
        for u in used:
            rule_rec[u] += 1
        fl = flags(r['proof'])
        for c in fl['w']['dn_cited']:
            cited[c] += 1
        if fl['w']['sigma_strict'] or fl['p']['sigma_strict']:
            sig['sigma'] += 1
        if fl['w']['dn_derived'] or fl['p']['dn_derived']:
            sig['sigma_plus'] += 1
        if fl['w']['dn_any']:
            sig['dn_any'] += 1
        np_ = r.get('n_prem')
        if np_ is None:
            body = ' ' + r['prompt'].strip()[4:-4] + ' '
            np_ = len([p for p in body.split(' SEQ ')[0].split(' , ') if p.strip()])
        nprem[np_] += 1
        wdepth[written_depth(r['proof'])] += 1
        prompts.append(r['prompt'])
    rng = random.Random(seed)
    samp = rng.sample(prompts, min(sample_n, len(prompts)))
    co = sum(1 for p in samp if not intuit_provable(p))
    return {'file': fn, 'records': n,
            'per_length': {str(k): v for k, v in sorted(per_len.items())},
            'rule_share_records': {k: round(rule_rec[k] / n, 5) for k in RULES},
            'rule_share_lines': {k: round(rule_lines[k] / lines_total, 5) for k in RULES},
            'dn_cited_rule': dict(cited), 'sigma_counts': dict(sig),
            'n_prem': {str(k): v for k, v in sorted(nprem.items())},
            'written_box_depth': {str(k): v for k, v in sorted(wdepth.items())},
            'term_size': {'mean': round(statistics.mean(ts), 3), 'median': statistics.median(ts), 'max': max(ts)},
            'term_size_by_length': {str(L): round(statistics.mean(v), 2) for L, v in sorted(ts_len.items())},
            'classical_only_share_sample': {'n': len(samp), 'classical_only': co, 'share': round(co / len(samp), 5)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    res = [shape(fn) for fn in a.sets]
    json.dump(res, open(a.out, 'w'), indent=1)
    names = [os.path.basename(x['file']) for x in res]
    print('| quantity | ' + ' | '.join(names) + ' |')
    print('|---|' + '---|' * len(res))
    print('| records | ' + ' | '.join(str(x['records']) for x in res) + ' |')
    for k in ('sigma', 'sigma_plus', 'dn_any'):
        print(f'| records with {k} | ' + ' | '.join(str(x['sigma_counts'].get(k, 0)) for x in res) + ' |')
    for k in RULES:
        print(f'| share of records using {k} | ' + ' | '.join(f"{x['rule_share_records'][k]:.4f}" for x in res) + ' |')
    print('| mean term size | ' + ' | '.join(str(x['term_size']['mean']) for x in res) + ' |')
    print('| premises 0/1/2/3 | ' + ' | '.join('/'.join(str(x['n_prem'].get(str(i), 0)) for i in range(4)) for x in res) + ' |')
    print('| written box depth 0/1/2 | ' + ' | '.join('/'.join(str(x['written_box_depth'].get(str(i), 0)) for i in range(3)) for x in res) + ' |')
    print('| classical-only theorems (20k sample) | ' + ' | '.join(str(x['classical_only_share_sample']['share']) for x in res) + ' |')
    print('| DN cites (written) | ' + ' | '.join(json.dumps(x['dn_cited_rule']) for x in res) + ' |')


if __name__ == '__main__':
    main()
