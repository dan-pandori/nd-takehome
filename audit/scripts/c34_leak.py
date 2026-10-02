#!/usr/bin/env python3
"""C3/C4 leakage: renaming class invariant to atom renaming (P,Q,R,S; F = falsum is NOT an atom)
AND premise order (premises as a sorted multiset), computed as the min over all 24 atom permutations.

Training sets: K12 (cap-12 Stage-1, SN-cap12 / K12 / best12), cap-6 control set (SN-v2 / best6 / C0),
rl_targets (every T1 ladder's targets). Eval pools: rr600 (+Q subset), ge17, long2 (new 21), long2 calib,
textbook72, dev1108 (transfer.jsonl, sha1(key) even). Also reports how many hits the repo's order-sensitive
`key` field would have found.
Writes audit/out/c34_leak.tsv (one line per eval theorem that hits a training class).
"""
import hashlib, itertools, json, os, re

H = os.path.expanduser('~')
D = f'{H}/work/best-state/data'
AUD = f'{H}/work/claim-audit/audit'
ATOMS = ('P', 'Q', 'R', 'S')
PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]
TOK = re.compile(r'\S+')


def parse(row):
    p = row['prompt'].strip()
    assert p.startswith('THM') and p.endswith('PRF'), p
    body = ' ' + p[3:-3].strip() + ' '
    prem, concl = body.split(' SEQ ')
    prems = [x.strip() for x in prem.split(' , ')] if prem.strip() else []
    return prems, concl.strip()


def canon(row):
    prems, concl = parse(row)
    best = None
    for m in PERMS:
        f = lambda s: ' '.join(m.get(t, t) for t in s.split())
        k = ' , '.join(sorted(f(x) for x in prems)) + ' |- ' + f(concl)
        if best is None or k < best:
            best = k
    return best


def ordkey(row):
    """order-sensitive renaming key (first-occurrence renaming, premise order kept) ~ repo's `key`."""
    prems, concl = parse(row)
    s = ' , '.join(prems) + ' |- ' + concl
    m = {}
    out = []
    for t in s.split():
        if t in ATOMS:
            if t not in m:
                m[t] = ATOMS[len(m)]
            out.append(m[t])
        else:
            out.append(t)
    return ' '.join(out)


def stream(path):
    with open(path) as f:
        for l in f:
            yield json.loads(l)


def main():
    train = {
        'K12': f'{D}/kh/train_k12.jsonl',
        'cap6': f'{D}/p2/train_depth3_f0_a1.jsonl',
        'rl_targets': f'{D}/ladder/rl_targets.jsonl',
    }
    md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()[:12]
    tk = {}
    to = {}
    for name, p in train.items():
        s, so = set(), set()
        for r in stream(p):
            s.add(canon(r))
            so.add(ordkey(r))
        tk[name], to[name] = s, so
        print(f'train {name}: {len(s)} classes ({p}, md5 {md5(p)})')
    tb = [json.loads(l) for l in open(f'{D}/bs/textbook72.jsonl')]
    dev = [r for r in stream(f'{D}/ladder/transfer.jsonl') if int(hashlib.sha1(r['key'].encode()).hexdigest(), 16) % 2 == 0]
    rr = list(stream(f'{D}/ladder/transfer_long_rr600.jsonl'))
    pools = {
        'rr600': rr,
        'rr600_Q(gen13-16)': [r for r in rr if r['source'] == 'gen' and 13 <= r['L_true'] <= 16],
        'ge17': list(stream(f'{D}/ladder/transfer_long_ge17.jsonl')),
        'long2_new21': list(stream(f'{D}/ladder/transfer_long2.jsonl')),
        'long2_calib70': list(stream(f'{D}/ladder/transfer_long2_calib.jsonl')),
        'textbook72': tb,
        'dev1108': dev,
    }
    rows = []
    print('\npool\tn\t' + '\t'.join(f'{t}(canon/ordkey)' for t in train))
    for pn, pr in pools.items():
        cells = []
        for t in train:
            hc = [r for r in pr if canon(r) in tk[t]]
            ho = [r for r in pr if ordkey(r) in to[t]]
            cells.append(f'{len(hc)}/{len(ho)}')
            for r in hc:
                rows.append((pn, t, r['name'], r.get('L_true', r.get('reference_lines', '')), r['prompt']))
        print(f'{pn}\t{len(pr)}\t' + '\t'.join(cells))
    with open(f'{AUD}/out/c34_leak.tsv', 'w') as f:
        f.write('pool\ttrain\tname\tL\tprompt\n')
        for r in rows:
            f.write('\t'.join(map(str, r)) + '\n')
    # pairwise eval-pool overlap (rr600 vs ge17 vs long2) for completeness
    ck = {pn: {canon(r) for r in pr} for pn, pr in pools.items()}
    print('\nrr600 ∩ ge17', len(ck['rr600'] & ck['ge17']), '| rr600 ∩ long2_new21', len(ck['rr600'] & ck['long2_new21']),
          '| ge17 ∩ long2_new21', len(ck['ge17'] & ck['long2_new21']), '| ge17 == calib70', ck['ge17'] == ck['long2_calib70'])
    # within-pool duplicates by class
    for pn, pr in pools.items():
        print(f'{pn}: {len(pr)} rows, {len(ck[pn])} distinct classes')


if __name__ == '__main__':
    main()
