#!/usr/bin/env python3
"""C4: best-state arm comparison (best recipe vs ours) re-derived from per-problem eval rows.

tb72 counts: own recount (n_ok > 0 and >= 1 stored proof) from
  best arms   ~/work/best-state/artifacts/bs/eval/{Fz,T1}_best{6,12}_s*__tb72.jsonl (batch 2048)
  ours arms   audit/raw/textbook72/.../eval/{Fz,T1}_SN{6,12}_s*.jsonl         (batch 4096, inherited)
  replication trajectory(-cap6) s*_{pend,r8}__tb72_x0.jsonl (same best recipe, 3 fresh training runs)
dev metric: ~/work/best-state/artifacts/bs/eval/*__dev.jsonl (all arms read in best-state).
Ladder compute: sum of round_<r>.json 'secs' (clean ladder only; OOM-aborted attempts not included).
Writes audit/out/c4_arms.tsv
"""
import glob, itertools, json, math, os
import numpy as np
from scipy import stats

H = os.path.expanduser('~')
AUD = f'{H}/work/claim-audit/audit'
BS = f'{H}/work/best-state/artifacts/bs'
TB = f'{AUD}/raw/textbook72/artifacts/textbook72/eval'


def count(path):
    n = 0
    for l in open(path):
        r = json.loads(l)
        n += (r.get('n_ok', 0) > 0 and len(r.get('proofs') or []) > 0)
    return n


def mdd(sd, n1, n2, alpha=0.05, power=0.8):
    df = n1 + n2 - 2
    return (stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df)) * sd * math.sqrt(1 / n1 + 1 / n2)


def perm_p(a, b):
    """exact one-sided p for mean(a) - mean(b) >= observed."""
    allv = list(a) + list(b)
    obs = np.mean(a) - np.mean(b)
    hits = tot = 0
    for idx in itertools.combinations(range(len(allv)), len(a)):
        x = [allv[i] for i in idx]
        y = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1
        hits += (np.mean(x) - np.mean(y) >= obs - 1e-9)
    return hits / tot


def compare(name, a, b, out):
    a, b = np.array(a, float), np.array(b, float)
    sp = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    w = stats.ttest_ind(a, b, equal_var=False)
    m = mdd(sp, len(a), len(b))
    row = (name, '/'.join(str(int(x)) for x in a), '/'.join(str(int(x)) for x in b),
           round(a.mean() - b.mean(), 1), round(sp, 2), round(m, 1), round(w.pvalue, 4), round(perm_p(a, b), 3),
           int(a.min() > b.max()))
    out.append(row)
    print('\t'.join(map(str, row)))


def main():
    tb = {}
    for cell in ('Fz_best6', 'T1_best6', 'Fz_best12', 'T1_best12'):
        tb[cell] = [count(f'{BS}/eval/{cell}_s{s}__tb72.jsonl') for s in range(3)]
    for cell, n in (('Fz_SN6', 2), ('T1_SN6', 2), ('Fz_SN12', 4), ('T1_SN12', 4)):
        tb[cell] = [count(f'{TB}/{cell}_s{s}.jsonl') for s in range(n)]
    tb['tj_pend_best12'] = [count(f'{H}/work/trajectory/artifacts/tj/eval/s{s}_pend__tb72_x0.jsonl') for s in range(3)]
    tb['tj_r8_best12'] = [count(f'{H}/work/trajectory/artifacts/tj/eval/s{s}_r8__tb72_x0.jsonl') for s in range(3)]
    tb['tj6_pend_best6'] = [count(f'{H}/work/trajectory-cap6/artifacts/tj6/eval/s{s}_pend__tb72_x0.jsonl') for s in range(3)]
    tb['tj6_r8_best6'] = [count(f'{H}/work/trajectory-cap6/artifacts/tj6/eval/s{s}_r8__tb72_x0.jsonl') for s in range(3)]
    dev = {}
    for cell in ('Fz_best6', 'T1_best6', 'Fz_best12', 'T1_best12'):
        dev[cell] = [count(f'{BS}/eval/{cell}_s{s}__dev.jsonl') for s in range(3)]
    for cell, n in (('Fz_SN6', 2), ('T1_SN6', 2), ('Fz_SN12', 4), ('T1_SN12', 4)):
        dev[cell] = [count(f'{BS}/eval/{cell}_s{s}__dev.jsonl') for s in range(n)]
    print('tb72 per seed:', tb)
    print('dev per seed :', dev)
    out = []
    print('\ncomparison\tbest\tours\tdiff\tpooled_sd\tMDD(t,80%)\tWelch_p\tperm_p_1sided\tfull_sep')
    for cap in ('6', '12'):
        for st in ('Fz', 'T1'):
            compare(f'tb72 {st} cap{cap}', tb[f'{st}_best{cap}'], tb[f'{st}_SN{cap}'], out)
            compare(f'dev {st} cap{cap}', dev[f'{st}_best{cap}'], dev[f'{st}_SN{cap}'], out)
    # replication: fresh best-recipe runs from trajectory / trajectory-cap6 against the same "ours"
    compare('tb72 T1 cap12 REPL(tj r8)', tb['tj_r8_best12'], tb['T1_SN12'], out)
    compare('tb72 T1 cap6 REPL(tj6 r8)', tb['tj6_r8_best6'], tb['T1_SN6'], out)
    compare('tb72 Fz cap12 REPL(tj pend)', tb['tj_pend_best12'], tb['Fz_SN12'], out)
    compare('tb72 T1 cap12 best6+repl', tb['T1_best12'] + tb['tj_r8_best12'], tb['T1_SN12'], out)
    compare('tb72 T1 cap6 best6+repl', tb['T1_best6'] + tb['tj6_r8_best6'], tb['T1_SN6'], out)
    # same recipe, independent training runs: best-state vs trajectory(-cap6)
    compare('tb72 T1 best12: bs vs tj (same recipe)', tb['T1_best12'], tb['tj_r8_best12'], out)
    compare('tb72 T1 best6: bs vs tj6 (same recipe)', tb['T1_best6'], tb['tj6_r8_best6'], out)
    compare('tb72 Fz best12: bs vs tj (same recipe)', tb['Fz_best12'], tb['tj_pend_best12'], out)
    # interaction (cap-12 advantage on best vs ours), T1 tb72, by seed-mean contrasts
    i = (np.mean(tb['T1_best12']) - np.mean(tb['T1_best6'])) - (np.mean(tb['T1_SN12']) - np.mean(tb['T1_SN6']))
    se = math.sqrt(sum(np.var(tb[c], ddof=1) / len(tb[c]) for c in ('T1_best12', 'T1_best6', 'T1_SN12', 'T1_SN6')))
    print(f'\ninteraction tb72 T1 (cap12 gain best - cap12 gain ours) = {i:.2f}, se {se:.2f}, z {i / se:.2f}')
    with open(f'{AUD}/out/c4_arms.tsv', 'w') as f:
        f.write('comparison\tbest\tours\tdiff\tpooled_sd\tMDD\twelch_p\tperm_p\tfull_sep\n')
        for r in out:
            f.write('\t'.join(map(str, r)) + '\n')

    # ladder compute
    print('\nladder secs (sum of 8 clean rounds):')
    lad = {}
    for s in range(3):
        for c in ('best6', 'best12'):
            lad[f'{c}_s{s}'] = sum(json.load(open(f'{BS}/la_T1_{c}_s{s}/round_{r}.json'))['secs'] for r in range(1, 9))
    for s in range(4):
        lad[f'SN12_s{s}'] = sum(json.load(open(f'{AUD}/raw/state-cap12/artifacts/sc12/la_T1_SN12_s{s}/round_{r}.json'))['secs'] for r in range(1, 9))
    for s in range(2):
        lad[f'SN6_s{s}'] = sum(json.load(open(f'{AUD}/raw/state-env/artifacts/se/la_T1_SN_s{s}/round_{r}.json'))['secs'] for r in range(1, 9))
    for k, v in lad.items():
        print(f'  {k}\t{v:,.0f}')
    a40_sn12 = [lad['SN12_s2'], lad['SN12_s3']]  # A40 per state-cap12 summary (sc-s2, sc-s3)
    b12 = [lad[f'best12_s{s}'] for s in range(3)]
    print(f'  best12 / SN12(A40 s2-s3) ratio range {min(b12) / max(a40_sn12):.2f}-{max(b12) / min(a40_sn12):.2f}')
    b6 = [lad[f'best6_s{s}'] for s in range(3)]
    sn6 = [lad['SN6_s0'], lad['SN6_s1']]
    print(f'  best6 / SN6 (mixed GPU classes) ratio range {min(b6) / max(sn6):.2f}-{max(b6) / min(sn6):.2f}')


if __name__ == '__main__':
    main()
