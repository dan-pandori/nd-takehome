#!/usr/bin/env python3
"""cap-horizon: assemble the cap arms' pretraining sets.

  python3 kh_assemble.py --arm k8add|k10|k12|k14 [--seed 0] [--outdir data/kh]

Short bins (lengths 2-6) come from K6's OWN training set (data/p2/train_depth3_f0_a1.jsonl, the
ds-composition control C0 = lean-format's a1 set, 31,000 per length):
  * k8add  : all 155,000 records, byte-identical lines, in their original order;
  * k10/k12/k14 : a uniform per-bin subsample (seeded), so every arm's short bins are a SUBSET of
    the control's exact records and "short proofs removed" is pure subsetting -- no re-draw noise
    anywhere below the cap.
Long bins (lengths >= 7) come from data/kh/pool_long_kh.jsonl (kh_gen.py; the control's generator
settings, output filter only).  Eligible = not in any evaluation pool's renaming class, not in the
control set's renaming classes, and NOT depth-3 in the pruned form (patterns.classify) or in the
written form (max box depth >= 3) -- the same exclusion every arm of proposal 10 used.  Within a
length bin the draw is uniform at random, which reproduces the pool's natural pattern rates (the
pool has no per-pattern generation cap).

Every emitted record is re-verified with nd_verify, its cap asserted and its lean_seq round trip
checked.  Writes <outdir>/train_<arm>.jsonl.gz, assemble_report_<arm>.json and shape_<arm>.json.
"""
import argparse, collections, gzip, json, os, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from gen import canon_key
from patterns import classify
from kh_size import term_size
from tokenizer import make_tokenizer

C0 = 'data/p2/train_depth3_f0_a1.jsonl'
POOL = 'data/kh/pool_long_kh.jsonl'
EXCLUDE = ['data/p2/heldout.jsonl', 'data/p2/targets_depth3.jsonl', 'data/p2/transfer_depth3.jsonl',
           'data/p2/targets_reductio_req.jsonl', 'data/p2/transfer_reductio_req.jsonl',
           'data/r3_1/depth3_req.jsonl', 'data/r3_1/depth3_req_transfer.jsonl',
           'data/ladder/rl_targets.jsonl', 'data/ladder/transfer.jsonl', 'targets/validation_36.jsonl',
           'data/dsc/targets_depth3_sub250.jsonl']
RULES = ['AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']

# per-length target counts; K8add is the only arm whose SET SIZE differs (217,000)
def counts(arm):
    if arm == 'k8add':
        return {L: 31000 for L in range(2, 9)}, 8, 217000
    hi = {'k10': 10, 'k12': 12, 'k14': 14}[arm]
    lens = list(range(2, hi + 1))
    base, rem = divmod(155000, len(lens))
    c = {L: base + (1 if i < rem else 0) for i, L in enumerate(lens)}
    assert sum(c.values()) == 155000
    return c, hi, 155000


def written_depth(proof):
    """max box depth of the WRITTEN proof (number of '|' after the line index) -- dsc_assemble.py's definition."""
    best = 0
    for seg in proof.split(' ; '):
        t = seg.split()
        if not t or not t[0].startswith('N'):
            continue
        d = 0
        for x in t[1:]:
            if x == '|':
                d += 1
            else:
                break
        best = max(best, d)
    return best


def exclusion_keys():
    ks = set()
    per = {}
    for fn in EXCLUDE:
        n0 = len(ks)
        for l in open(fn):
            if not l.strip():
                continue
            r = json.loads(l)
            ks.add(r['key'] if 'key' in r else canon_key(r['thm'].strip()))
        per[os.path.basename(fn)] = len(ks) - n0
    return ks, per


def shape(records):
    """shape table of a list of (n_lines, prompt, proof, key)."""
    s = collections.Counter()
    per_len = collections.Counter()
    pats = collections.Counter()
    ts_all, ts_by_len = [], collections.defaultdict(list)
    nprem = collections.Counter()
    wdepth = collections.Counter()
    pat_by_len = collections.defaultdict(collections.Counter)
    for L, prompt, proof, key in records:
        per_len[L] += 1
        cl = classify(proof) or {}
        for p in ('reductio', 'derived_ore', 'derived_ore_strict', 'depth3', 'derived_dn'):
            if cl.get(p):
                pats[p] += 1
                pat_by_len[L][p] += 1
        for ru in RULES:
            if f' {ru} ' in f' {proof} ' or f' {ru};' in proof or proof.rstrip().endswith(' ' + ru):
                pass
        toks = set(proof.split())
        for ru in RULES:
            if ru in toks:
                s['rule_' + ru] += 1
        t = term_size(proof)
        if t:
            ts_all.append(t[1])
            ts_by_len[L].append(t[1])
        nprem[len([x for x in prompt.split(' , ') if x.strip()]) if prompt.strip() and '|-' not in prompt.split()[0] else 0] += 0
        wdepth[written_depth(proof)] += 1
    n = len(records)
    return {'records': n,
            'per_length': {str(k): per_len[k] for k in sorted(per_len)},
            'written_box_depth': {str(k): wdepth[k] for k in sorted(wdepth)},
            'patterns': {k: v for k, v in sorted(pats.items())},
            'pattern_share_by_length': {str(L): {p: round(pat_by_len[L][p] / per_len[L], 6) for p in ('reductio', 'derived_ore', 'derived_ore_strict')} for L in sorted(per_len)},
            'rule_share': {k[5:]: round(v / n, 6) for k, v in sorted(s.items()) if k.startswith('rule_')},
            'mean_term_size': round(statistics.mean(ts_all), 3),
            'median_term_size': statistics.median(ts_all),
            'max_term_size': max(ts_all),
            'term_size_by_length': {str(L): {'mean': round(statistics.mean(v), 2), 'median': statistics.median(v), 'max': max(v)} for L, v in sorted(ts_by_len.items())}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True, choices=['k8add', 'k10', 'k12', 'k14'])
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--outdir', default='data/kh')
    a = ap.parse_args()
    t0 = time.time()
    want, cap, size = counts(a.arm)
    tok = make_tokenizer('lean_seq')
    excl, excl_per = exclusion_keys()
    print(f'{a.arm}: cap {cap}, size {size}, exclusion classes {len(excl)}', flush=True)

    # ---- short bins: the control's own records --------------------------------
    short_lines = collections.defaultdict(list)     # L -> [raw json line]
    c0_keys = set()
    for l in open(C0):
        r = json.loads(l)
        L = r['n_lines']
        c0_keys.add(r['key'] if 'key' in r else canon_key(r['thm']))
        if L in want:
            short_lines[L].append(l)
    c0_per_len = {str(L): len(v) for L, v in sorted(short_lines.items())}
    print('control set per-length available:', c0_per_len, flush=True)

    rng = random.Random(a.seed)
    out_lines, chosen = [], []
    short_note = {}
    for L in sorted(short_lines):
        avail = short_lines[L]
        if len(avail) == want[L]:
            take = avail                       # k8add: byte-identical, original order
            short_note[str(L)] = 'all (byte-identical)'
        else:
            idx = sorted(rng.sample(range(len(avail)), want[L]))
            take = [avail[i] for i in idx]
            short_note[str(L)] = f'uniform subsample {want[L]}/{len(avail)} (seed {a.seed})'
        out_lines += take

    # ---- long bins: the new pool ---------------------------------------------
    long_want = {L: want[L] for L in want if L >= 7}
    scan = collections.Counter()
    elig = collections.defaultdict(list)
    if long_want:
        for l in open(POOL):
            r = json.loads(l)
            L = r['n_lines']
            scan['read'] += 1
            if L not in long_want:
                continue
            scan['in_range'] += 1
            k = r['key']
            if k in excl:
                scan['excluded_class_evalpool'] += 1
                continue
            if k in c0_keys:
                scan['excluded_class_controlset'] += 1
                continue
            cl = classify(r['proof'])
            if cl is None:
                scan['parse_fail'] += 1
                continue
            if cl['depth3'] or written_depth(r['proof']) >= 3:
                scan['depth3'] += 1
                continue
            scan['eligible'] += 1
            elig[L].append(r)
    avail_long = {str(L): len(elig[L]) for L in sorted(long_want)}
    print('long bins eligible:', avail_long, flush=True)

    # fill; if a bin is short, disclose and fill the deficit proportionally from the bins that did fill
    fill_disclosure = {}
    deficit = 0
    got = {}
    for L in sorted(long_want):
        n = min(len(elig[L]), long_want[L])
        got[L] = n
        if n < long_want[L]:
            deficit += long_want[L] - n
            fill_disclosure[str(L)] = {'wanted': long_want[L], 'achieved': n, 'shortfall': long_want[L] - n}
    if deficit:
        donors = [L for L in sorted(long_want) if len(elig[L]) > got[L]]
        spare = {L: len(elig[L]) - got[L] for L in donors}
        tot = sum(spare.values())
        assert tot >= deficit, f'cannot fill deficit {deficit} from spare {tot}'
        add = {L: int(deficit * spare[L] / tot) for L in donors}
        i = 0
        while sum(add.values()) < deficit:
            add[donors[i % len(donors)]] += 1
            i += 1
        for L, k in add.items():
            got[L] += k
            fill_disclosure.setdefault('proportional_fill', {})[str(L)] = k
    for L in sorted(long_want):
        pool_L = elig[L]
        idx = sorted(rng.sample(range(len(pool_L)), got[L]))
        for i in idx:
            r = pool_L[i]
            out_lines.append(json.dumps(r) + '\n')

    # ---- checks ---------------------------------------------------------------
    rng.shuffle(out_lines)
    keys, texts = set(), set()
    per_len = collections.Counter()
    recs = []
    for l in out_lines:
        r = json.loads(l)
        L = r['n_lines']
        assert L <= cap, f'record exceeds cap {cap}: {L}'
        ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
        assert ok and nl == L, (reason, nl, L)
        ids = tok.encode_proof(r['proof'])
        assert tok.decode(ids) == r['proof'], 'lean_seq round trip'
        k = r['key'] if 'key' in r else canon_key(r['thm'])
        assert k not in keys, 'duplicate renaming class'
        assert k not in excl, 'record in an evaluation pool'
        keys.add(k)
        assert r['prompt'] + ' ' + r['proof'] not in texts, 'duplicate rendered text'
        texts.add(r['prompt'] + ' ' + r['proof'])
        cl = classify(r['proof'])
        assert not cl['depth3'] and written_depth(r['proof']) < 3, 'depth-3 leaked'
        per_len[L] += 1
        recs.append((L, r['prompt'], r['proof'], k))
    assert len(out_lines) == size, (len(out_lines), size)
    assert all(per_len[L] == want[L] for L in want), (dict(per_len), want)

    os.makedirs(a.outdir, exist_ok=True)
    fn = f'{a.outdir}/train_{a.arm}.jsonl.gz'
    with gzip.open(fn, 'wt') as f:
        f.writelines(out_lines)
    sh = shape(recs)
    json.dump(sh, open(f'{a.outdir}/shape_{a.arm}.json', 'w'), indent=1)
    rep = {'arm': a.arm, 'cap': cap, 'size': size, 'seed': a.seed, 'out': fn,
           'per_length_wanted': {str(k): v for k, v in sorted(want.items())},
           'per_length_achieved': {str(k): per_len[k] for k in sorted(per_len)},
           'short_bins_source': {'file': C0, 'available': c0_per_len, 'how': short_note},
           'long_bins_source': {'file': POOL, 'eligible': avail_long, 'scan': dict(scan)},
           'fill_disclosure': fill_disclosure or 'none: every long bin filled from its own length',
           'distinct_renaming_classes': len(keys), 'distinct_rendered_texts': len(texts),
           'exclusion_classes': len(excl), 'exclusion_per_file': excl_per,
           'overlap_with_eval_pools': 0, 'records_over_cap': 0, 'depth3_records': 0,
           'secs': round(time.time() - t0, 1)}
    json.dump(rep, open(f'{a.outdir}/assemble_report_{a.arm}.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k not in ('exclusion_per_file',)}, indent=1))


if __name__ == '__main__':
    main()
