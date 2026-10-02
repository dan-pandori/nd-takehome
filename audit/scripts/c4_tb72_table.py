#!/usr/bin/env python3
"""C4: every textbook72 read-out across textbook72 / best-state / trajectory / trajectory-cap6.

Own recount from per-problem eval rows (solved := n_ok > 0 and >= 1 stored proof; cross-checked
against the row's 'solved' flag).  Also: pool identity per file (hash of sorted (name, prompt)),
same-checkpoint double reads (trajectory x0 vs x1 sample seeds, textbook72 a512 vs a1024) tested
against the binomial redraw spread implied by the per-problem accept rates.

Writes audit/out/c4_tb72_table.tsv and audit/out/c4_tb72_pairs.tsv.
"""
import glob, hashlib, json, math, os, re, sys

HOME = os.path.expanduser('~')
AUD = f'{HOME}/work/claim-audit/audit'
SRC = {
    'textbook72': (f'{AUD}/raw/textbook72/artifacts/textbook72/eval/*.jsonl', 'bucket textbook72/artifacts/textbook72/eval'),
    'textbook72-diag': (f'{AUD}/raw/textbook72/artifacts/textbook72/diag/*.jsonl', 'bucket textbook72/artifacts/textbook72/diag'),
    'best-state': (f'{HOME}/work/best-state/artifacts/bs/eval/*__tb72.jsonl', 'best-state bucket artifacts/bs/eval (pulled copy ~/work/best-state)'),
    'trajectory': (f'{HOME}/work/trajectory/artifacts/tj/eval/*__tb72_x*.jsonl', 'trajectory bucket artifacts/tj/eval (pulled copy)'),
    'trajectory-cap6': (f'{HOME}/work/trajectory-cap6/artifacts/tj6/eval/*__tb72_x*.jsonl', 'trajectory-cap6 bucket artifacts/tj6/eval (pulled copy)'),
}


def pool_hash(rows):
    s = '\n'.join(sorted(f"{r['name']}\t{r['prompt']}" for r in rows))
    return hashlib.md5(s.encode()).hexdigest()[:10]


def ref_hashes():
    out = {}
    rows = [json.loads(l) for l in open(f'{HOME}/work/claim-audit/data/bs/textbook72.jsonl')]
    out['data/bs/textbook72.jsonl'] = pool_hash(rows)
    rows = []
    for f in ('textbook_dev.jsonl', 'textbook_train.jsonl'):
        rows += [json.loads(l) for l in open(f'{HOME}/work/claim-audit/data/eval_only/textbook72/{f}')]
    out['eval_only dev+train'] = pool_hash(rows)
    return out


def load(path):
    rows = [json.loads(l) for l in open(path)]
    solved = {}
    nok = {}
    flag_mismatch = 0
    tried = 0
    for r in rows:
        s = (r.get('n_ok', 0) > 0) and len(r.get('proofs') or []) > 0
        if bool(r.get('solved')) != s:
            flag_mismatch += 1
        solved[r['name']] = s
        nok[r['name']] = (r.get('n_ok', 0), r.get('n_tried', 0))
        tried += r.get('n_tried', 0)
    return rows, solved, nok, flag_mismatch, tried


def redraw_sd(nok):
    """sd of the solved count implied by per-problem accept rate q (pass@n Bernoulli)."""
    v = 0.0
    for ok, n in nok.values():
        if n == 0:
            continue
        q = ok / n
        p = 1 - (1 - q) ** n
        v += p * (1 - p)
    return math.sqrt(v)


def main():
    md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]
    refs = ref_hashes()
    print('reference pool hashes:', refs)
    table = []
    by = {}
    for run, (pat, src) in SRC.items():
        for p in sorted(glob.glob(pat)):
            rows, solved, nok, mm, tried = load(p)
            lab = os.path.basename(p).replace('.jsonl', '')
            n_sol = sum(solved.values())
            ph = pool_hash(rows)
            table.append((run, lab, len(rows), tried, n_sol, ph, mm, md5(p)))
            by[(run, lab)] = (solved, nok)
    with open(f'{AUD}/out/c4_tb72_table.tsv', 'w') as f:
        f.write('run\tread\tn_problems\tattempts\tsolved\tpool_hash\tflag_mismatch\tfile_md5\n')
        for t in table:
            f.write('\t'.join(map(str, t)) + '\n')
    # print compact: non-trajectory rows fully, trajectory only pend/r8
    for t in table:
        if t[0].startswith('trajectory') and not re.search(r'_(pend|r8)__', t[1]):
            continue
        print('\t'.join(map(str, t)))
    pools = {t[5] for t in table}
    print('distinct pool hashes over', len(table), 'reads:', pools, 'n_problems:', {t[2] for t in table},
          'flag mismatches:', sum(t[6] for t in table))

    # same-checkpoint double reads
    pairs = []
    for (run, lab), (s0, n0) in by.items():
        if run.startswith('trajectory') and lab.endswith('_x0'):
            o = (run, lab[:-1] + '1')
            if o in by:
                pairs.append((run, lab[:-3], by[(run, lab)], by[o]))
    a = by.get(('textbook72', 'T1_SN12_s0'))
    b = by.get(('textbook72-diag', 'T1_SN12_s0_a1024'))
    if a and b:
        pairs.append(('textbook72', 'T1_SN12_s0 a512 vs a1024 (same seed 0)', a, b))
    out = []
    for run, lab, (sa, na), (sb, nb) in pairs:
        ca, cb = sum(sa.values()), sum(sb.values())
        flips = sum(sa[k] != sb[k] for k in sa)
        # pooled per-problem accept rate over both reads -> pass@n Bernoulli var, x2 for a difference
        pooled = {k: (na[k][0] + nb[k][0], na[k][1] + nb[k][1]) for k in na}
        v = 0.0
        for k, (ok, n) in pooled.items():
            q = ok / n if n else 0
            pp = 1 - (1 - q) ** na[k][1]
            v += pp * (1 - pp)
        sd = math.sqrt(2 * v)
        z = (ca - cb) / sd if sd > 0 else float('nan')
        out.append((run, lab, ca, cb, ca - cb, flips, round(sd, 2), round(z, 2)))
    with open(f'{AUD}/out/c4_tb72_pairs.tsv', 'w') as f:
        f.write('run\tckpt\tsolved_a\tsolved_b\tdiff\tflips\tredraw_sd_diff\tz\n')
        for t in out:
            f.write('\t'.join(map(str, t)) + '\n')
    zs = [t[7] for t in out if not math.isnan(t[7])]
    print(f'\nsame-checkpoint double reads: {len(out)}; |z|>1.96: {sum(abs(z) > 1.96 for z in zs)}; '
          f'|z|>2.58: {sum(abs(z) > 2.58 for z in zs)}; max|diff| {max(abs(t[4]) for t in out)}; '
          f'mean flips {sum(t[5] for t in out) / len(out):.2f}; sd(z) {math.sqrt(sum(z * z for z in zs) / len(zs)):.2f}')
    for t in out:
        if re.search(r'_(pend|r8)$', t[1]) or 'a1024' in t[1] or abs(t[7]) > 1.96:
            print('\t'.join(map(str, t)))


if __name__ == '__main__':
    main()
