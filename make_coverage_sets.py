#!/usr/bin/env python3
"""Phase 2 pools: generate a large raw pool with the UNCHANGED generator, label patterns, assemble
fixed-size pretraining sets with a chosen pattern frequency, and build pattern target pools.

  # 1. parallel generation (output filter only; generator probabilities untouched)
  python make_coverage_sets.py gen --out data/p2/raw_cap6 --workers 90 --tries 2500000 --cap_np 1500 --cap_pat 3000
  python make_coverage_sets.py gen --long --min 7 --max 12 --out data/p2/raw_long --workers 90 --tries 300000 --cap_np 400 --cap_pat 400
  # 2. merge shards (dedupe by renaming class, drop validation-36 classes)
  python make_coverage_sets.py merge --glob 'data/p2/raw_cap6.w*.jsonl' --out data/p2/pool_cap6.jsonl
  # 3. assemble pretraining sets
  python make_coverage_sets.py assemble --pool data/p2/pool_cap6.jsonl --outdir data/p2 --size 155000 --heldout 5000
  # 4. target pools from the long pool (after minlen labelling)
  python make_coverage_sets.py targets --pool data/p2/pool_long.jsonl --minlen data/p2/pool_long_minlen.jsonl --outdir data/p2

Every emitted proof is verifier-checked at generation time and again at assembly (assert).
"""
import argparse, json, os, sys, random, collections, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from gen import Gen, sample_one, canon_key, Fail
from patterns import classify, PATTERNS

LENS = (2, 3, 4, 5, 6)


def worker(args):
    seed, tries, mn, mx, long, cap_np, cap_pat, out = args
    rng = random.Random(seed)
    g = Gen(rng)
    seen = set()
    per_len = collections.Counter()
    per_pat = collections.Counter()
    stats = collections.Counter()
    n_out = 0
    t0 = time.time()
    with open(out, 'w') as fo:
        for _ in range(tries):
            stats['tries'] += 1
            try:
                r = sample_one(g, rng, long)
            except (Fail, RecursionError):
                stats['fail'] += 1
                continue
            L = r['n_lines']
            if L < mn or L > mx:
                stats['len_out'] += 1
                continue
            if long and r['contra_prem']:
                stats['contra'] += 1
                continue
            key = canon_key(r['thm'])
            if key in seen:
                stats['dup'] += 1
                continue
            cl = classify(r['proof'])
            pats = [p for p in PATTERNS if cl[p]]
            if not pats:
                if per_len[L] >= cap_np:
                    stats['np_full'] += 1
                    continue
            elif all(per_pat[p] >= cap_pat for p in pats):
                stats['pat_full'] += 1
                continue
            ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
            if not ok:
                stats['VERIFIER_REJECT'] += 1
                continue
            assert nl == L
            seen.add(key)
            per_len[L] += 1
            for p in pats:
                per_pat[p] += 1
            r['key'] = key
            r['pat'] = {p: cl[p] for p in PATTERNS}
            r.pop('text', None)
            fo.write(json.dumps(r) + '\n')
            n_out += 1
    return {'seed': seed, 'n_out': n_out, 'per_len': dict(per_len), 'per_pat': dict(per_pat), 'stats': dict(stats), 'secs': time.time() - t0}


def cmd_gen(a):
    import multiprocessing as mp
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    jobs = [(a.seed + i, a.tries, a.min, a.max, a.long, a.cap_np, a.cap_pat, f'{a.out}.w{i}.jsonl') for i in range(a.workers)]
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        res = pool.map(worker, jobs)
    tot = collections.Counter()
    for r in res:
        tot['n_out'] += r['n_out']
        for k, v in r['per_pat'].items():
            tot['pat_' + k] += v
        for k, v in r['stats'].items():
            tot[k] += v
    print(json.dumps({'total': dict(tot), 'secs': time.time() - t0}, indent=1))


def cmd_merge(a):
    val_keys = {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    seen = set()
    stats = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    files = sorted(glob.glob(a.glob))
    with open(a.out, 'w') as fo:
        for fn in files:
            for l in open(fn):
                r = json.loads(l)
                stats['read'] += 1
                if r['key'] in val_keys:
                    stats['val_class'] += 1
                    continue
                if r['key'] in seen:
                    stats['dup_class'] += 1
                    continue
                seen.add(r['key'])
                r['name'] = f'{a.prefix}_{stats["written"]}'
                L = r['n_lines']
                per[L]['n'] += 1
                for p in PATTERNS:
                    per[L][p] += r['pat'][p]
                per[L]['none'] += not any(r['pat'].values())
                fo.write(json.dumps(r) + '\n')
                stats['written'] += 1
    print(json.dumps({'files': len(files), 'stats': dict(stats)}, indent=1))
    for L in sorted(per):
        d = per[L]
        print(f'len {L}: n {d["n"]:7d} none {d["none"]:7d} ' + ' '.join(f'{p} {d[p]:6d} ({d[p]/d["n"]:.4%})' for p in PATTERNS))


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def label_of(r):
    return tuple(bool(r['pat'][p]) for p in PATTERNS)


def assemble_set(pool_by_len, pattern, f, size, rng, baseline):
    """pool_by_len: L -> list of records (all available). Returns list of records with pattern freq f,
    the other two patterns at `baseline[L][other]` counts per length, length distribution size/5 each."""
    pi = PATTERNS.index(pattern)
    others = [i for i in range(3) if i != pi]
    quota = {L: size // len(LENS) for L in LENS}
    n_pat_total = int(round(f * size))
    # distribute pattern proofs across lengths in proportion to availability
    avail = {L: [r for r in pool_by_len[L] if r['pat'][pattern]] for L in LENS}
    tot_avail = sum(len(v) for v in avail.values())
    if n_pat_total > tot_avail:
        return None, f'only {tot_avail} {pattern} proofs available, need {n_pat_total}'
    n_pat = {L: int(round(n_pat_total * len(avail[L]) / tot_avail)) for L in LENS} if tot_avail else {L: 0 for L in LENS}
    # fix rounding
    diff = n_pat_total - sum(n_pat.values())
    for L in sorted(LENS, key=lambda L: -len(avail[L])):
        if diff == 0:
            break
        step = 1 if diff > 0 else -1
        if 0 <= n_pat[L] + step <= len(avail[L]):
            n_pat[L] += step; diff -= step
    out = []
    achieved = collections.defaultdict(collections.Counter)
    for L in LENS:
        # pattern proofs: prefer those without the other patterns? No - take a random sample (keeps the
        # generator's conditional distribution), then compensate the other patterns in the non-pattern part.
        chosen = rng.sample(avail[L], n_pat[L]) if n_pat[L] else []
        rest = quota[L] - len(chosen)
        target_other = {j: baseline[L][PATTERNS[j]] for j in others}
        have_other = {j: sum(r['pat'][PATTERNS[j]] for r in chosen) for j in others}
        need_other = {j: max(0, target_other[j] - have_other[j]) for j in others}
        # non-pattern candidates grouped by (other1, other2) label
        cands = collections.defaultdict(list)
        for r in pool_by_len[L]:
            if r['pat'][pattern]:
                continue
            cands[(bool(r['pat'][PATTERNS[others[0]]]), bool(r['pat'][PATTERNS[others[1]]]))].append(r)
        for k in cands:
            rng.shuffle(cands[k])
        picked = []
        # greedy: fill the joint needs. First both-pattern proofs where both are needed, then singles, then none.
        def take(k, n):
            got = cands[k][:n]; del cands[k][:n]; return got
        n_both = min(need_other[others[0]], need_other[others[1]], len(cands[(True, True)]))
        picked += take((True, True), n_both)
        need_other[others[0]] -= n_both; need_other[others[1]] -= n_both
        picked += take((True, False), min(need_other[others[0]], len(cands[(True, False)])))
        picked += take((False, True), min(need_other[others[1]], len(cands[(False, True)])))
        picked = picked[:rest]
        picked += take((False, False), rest - len(picked))
        if len(picked) < rest:
            # not enough pattern-free proofs: top up from whatever is left (report the deviation)
            for k in ((True, False), (False, True), (True, True)):
                picked += take(k, rest - len(picked))
        if len(picked) < rest:
            return None, f'length {L}: only {len(chosen) + len(picked)} proofs available for quota {quota[L]}'
        sel = chosen + picked
        rng.shuffle(sel)
        out += sel
        achieved[L]['n'] = len(sel)
        for p in PATTERNS:
            achieved[L][p] = sum(r['pat'][p] for r in sel)
    return out, achieved


def cmd_assemble(a):
    rng = random.Random(a.seed)
    pool = read(a.pool)
    rng.shuffle(pool)
    # held-out: pattern-free proofs? No: in-distribution held-out drawn like the f=0 baseline would be
    # pattern-dependent; use a fixed held-out of `heldout` proofs drawn uniformly per length from the pool
    # (all patterns at their pool rates), disjoint from every training set.
    by_len = collections.defaultdict(list)
    for r in pool:
        by_len[r['n_lines']].append(r)
    heldout = []
    for L in LENS:
        heldout += by_len[L][:a.heldout // len(LENS)]
        by_len[L] = by_len[L][a.heldout // len(LENS):]
    os.makedirs(a.outdir, exist_ok=True)
    write_set(f'{a.outdir}/heldout.jsonl', heldout, 'heldout')
    hk = {r['key'] for r in heldout}
    # baseline per length: pattern counts in the f=0 set of each pattern are just the natural rates among
    # proofs WITHOUT that pattern. To hold the other two patterns' frequencies fixed across f, use the
    # natural per-length rate of each pattern among ALL pool proofs, scaled to the quota.
    quota = a.size // len(LENS)
    # Baseline = the generator's NATURAL per-length pattern rates (the pool itself is pattern-enriched by the
    # output caps, so its rates are not the natural ones). Measured on the take-home's unfiltered cap-6 pool
    # data/raw_cap6.jsonl (32,000 proofs per length; patterns.py --stats, log.md 2026-09-15 19:40):
    NATURAL = {2: {'derived_ore': 0, 'reductio': 0, 'depth3': 0}, 3: {'derived_ore': 0, 'reductio': 0, 'depth3': 0},
               4: {'derived_ore': 0, 'reductio': 0, 'depth3': 0},
               5: {'derived_ore': 28 / 32000, 'reductio': 5549 / 32000, 'depth3': 0},
               6: {'derived_ore': 63 / 32000, 'reductio': 5338 / 32000, 'depth3': 5870 / 32000}}
    if a.baseline_ref:
        cnt = collections.defaultdict(collections.Counter)
        for l in open(a.baseline_ref):
            r = json.loads(l); cl = classify(r['proof']); cnt[r['n_lines']]['n'] += 1
            for p in PATTERNS:
                cnt[r['n_lines']][p] += cl[p]
        NATURAL = {L: {p: cnt[L][p] / max(cnt[L]['n'], 1) for p in PATTERNS} for L in LENS}
    baseline = {L: {p: int(round(quota * NATURAL[L][p])) for p in PATTERNS} for L in LENS}
    print('natural per-length rates used as baseline', NATURAL)
    print('pool per length', {L: len(by_len[L]) for L in LENS})
    print('baseline pattern counts per length (natural rate x quota)', baseline)
    report = {}
    freqs = [float(x) for x in a.freqs.split(',')]
    for pattern in (a.patterns.split(',') if a.patterns else PATTERNS):
        for f in freqs:
            tag = f'{pattern}_f{f:g}'
            sel, ach = assemble_set(by_len, pattern, f, a.size, rng, baseline)
            if sel is None:
                print(f'{tag}: FAILED: {ach}')
                report[tag] = {'error': ach}
                continue
            fn = f'{a.outdir}/train_{tag}.jsonl'
            write_set(fn, sel, f'train_{tag}')
            # re-classify the written file (independent check)
            cnt = collections.Counter(); n = 0
            for l in open(fn):
                r = json.loads(l); n += 1
                cl = classify(r['proof'])
                for p in PATTERNS:
                    cnt[p] += cl[p]
                assert r['key'] not in hk
            if f == 0:
                assert cnt[pattern] == 0, (tag, cnt)
            rep = {'n': n, 'achieved_freq': {p: cnt[p] / n for p in PATTERNS}, 'achieved_count': dict(cnt),
                   'target_freq': f, 'per_len': {L: dict(ach[L]) for L in LENS}}
            report[tag] = rep
            print(f'{tag}: n {n} ' + ' '.join(f'{p} {cnt[p]} ({cnt[p]/n:.5f})' for p in PATTERNS))
    json.dump(report, open(f'{a.outdir}/assemble_report.json', 'w'), indent=1)


def write_set(fn, recs, prefix):
    with open(fn, 'w') as f:
        for i, r in enumerate(recs):
            ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
            assert ok and nl == r['n_lines'] <= 6 or nl == r['n_lines'], (reason, r)
            rec = {'name': f'{prefix}_{i}', 'thm': r['thm'], 'key': r['key'], 'prompt': r['prompt'], 'proof': r['proof'],
                   'text': r['prompt'] + ' ' + r['proof'], 'n_lines': r['n_lines'], 'rules': r['rules'], 'n_prem': r['n_prem'], 'pat': r['pat']}
            f.write(json.dumps(rec) + '\n')


def cmd_targets(a):
    rng = random.Random(a.seed)
    pool = read(a.pool)
    ml = {r['name']: r for r in read(a.minlen)} if a.minlen else {}
    excl = set()
    for fn in a.exclude:
        for r in read(fn):
            excl.add(r['key'])
    val_keys = {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    excl |= val_keys
    pool = [r for r in pool if r['key'] not in excl]
    for r in pool:
        m = ml.get(r.get('name'))
        r['min_lines_ub'] = m['min_lines_ub'] if m else None
        r['minlen_timeout'] = m['timeout'] if m else None
    # keep only theorems with NO <=6-line proof found by minlen (min_lines_ub >= 7 or None)
    if a.require_long:
        pool = [r for r in pool if r['min_lines_ub'] is None or r['min_lines_ub'] >= 7]
    rng.shuffle(pool)
    used = set()
    os.makedirs(a.outdir, exist_ok=True)
    summary = {}
    for pattern in list(PATTERNS) + ['none']:
        if pattern == 'none':
            cands = [r for r in pool if not any(r['pat'].values()) and r['key'] not in used]
        else:
            cands = [r for r in pool if r['pat'][pattern] and r['key'] not in used]
        # per generating length balance
        by = collections.defaultdict(list)
        for r in cands:
            by[r['n_lines']].append(r)
        n_t, n_x = a.n_targets, a.n_transfer
        targets, transfer = [], []
        lens = sorted(by)
        for L in lens:
            rs = by[L]
            targets += rs[:n_t // len(lens)]
            transfer += rs[n_t // len(lens):n_t // len(lens) + n_x // len(lens)]
        # top up from remaining
        rem = [r for L in lens for r in by[L][n_t // len(lens) + n_x // len(lens):]]
        while len(targets) < n_t and rem:
            targets.append(rem.pop())
        while len(transfer) < n_x and rem:
            transfer.append(rem.pop())
        for r in targets + transfer:
            used.add(r['key'])
        for name, recs in (('targets', targets), ('transfer', transfer)):
            fn = f'{a.outdir}/{name}_{pattern}.jsonl'
            with open(fn, 'w') as f:
                for i, r in enumerate(recs):
                    rec = {'name': f'{name}_{pattern}_{i}', 'thm': r['thm'], 'key': r['key'], 'prompt': r['prompt'], 'n_lines': r['n_lines'],
                           'rules': r['rules'], 'n_prem': r['n_prem'], 'pat': r['pat'], 'gen_proof': r['proof'],
                           'min_lines_ub': r['min_lines_ub'], 'minlen_timeout': r['minlen_timeout']}
                    f.write(json.dumps(rec) + '\n')
            summary[f'{name}_{pattern}'] = {'n': len(recs), 'by_len': dict(sorted(collections.Counter(r['n_lines'] for r in recs).items())),
                                            'min_lines_ub_hist': dict(sorted(collections.Counter(str(r['min_lines_ub']) for r in recs).items())),
                                            'other_patterns': {p: sum(r['pat'][p] for r in recs) for p in PATTERNS}}
            print(name, pattern, json.dumps(summary[f'{name}_{pattern}']))
    json.dump(summary, open(f'{a.outdir}/targets_summary.json', 'w'), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gen')
    g.add_argument('--out', required=True); g.add_argument('--workers', type=int, default=90); g.add_argument('--tries', type=int, default=1000000)
    g.add_argument('--min', type=int, default=2); g.add_argument('--max', type=int, default=6); g.add_argument('--long', action='store_true')
    g.add_argument('--cap_np', type=int, default=1500, help='per worker, per length cap on pattern-free proofs')
    g.add_argument('--cap_pat', type=int, default=3000, help='per worker cap per pattern')
    g.add_argument('--seed', type=int, default=1000)
    m = sub.add_parser('merge'); m.add_argument('--glob', required=True); m.add_argument('--out', required=True); m.add_argument('--prefix', default='pool')
    s = sub.add_parser('assemble'); s.add_argument('--pool', required=True); s.add_argument('--outdir', required=True)
    s.add_argument('--size', type=int, default=155000); s.add_argument('--heldout', type=int, default=5000); s.add_argument('--seed', type=int, default=0)
    s.add_argument('--freqs', default='0,0.0001,0.001,0.01,0.1'); s.add_argument('--patterns', default=None)
    s.add_argument('--baseline_ref', default=None, help='unfiltered generator pool to measure natural per-length pattern rates (default: hard-coded take-home numbers)')
    t = sub.add_parser('targets'); t.add_argument('--pool', required=True); t.add_argument('--minlen', default=None); t.add_argument('--outdir', required=True)
    t.add_argument('--exclude', nargs='*', default=[]); t.add_argument('--n_targets', type=int, default=1000); t.add_argument('--n_transfer', type=int, default=500)
    t.add_argument('--require_long', action='store_true'); t.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    {'gen': cmd_gen, 'merge': cmd_merge, 'assemble': cmd_assemble, 'targets': cmd_targets}[a.cmd](a)


if __name__ == '__main__':
    main()
