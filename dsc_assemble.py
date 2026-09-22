#!/usr/bin/env python3
"""ds-composition: assemble the composition arms' pretraining sets from the UNCHANGED generator's pools, streaming
(the VPS has 4 GB of RAM, so the pool is never loaded whole), then the shape table, the overlap table and the render check.

  python3 dsc_assemble.py assemble --arm a1|a2|a3|a4 [--seed 0] [--size 155000] [--outdir data/dsc]
  python3 dsc_assemble.py shape   --set <train.jsonl[.gz]> --tag c0        # shape + overlap + render check of an existing set (the control)

Pools: data/p2/pool_cap6_recon.jsonl (723,534 renaming classes of 2-6-line proofs; the a1 control's pool), the ORE top-up
shards data/dsc/raw_ore.w*.jsonl (same generator, output filter `rule:ORE`, A2 only) and data/p2/pool_cap8.jsonl (7-8-line
records for the cap-8 yardstick A3 only). Exclusions (renaming class `key`): the p2 held-out set, every target / transfer pool
of this run, the ladder pools and validation-36. Depth-3 proofs are excluded in the pruned form (`pat.depth3`) and in the
written form (max box depth of the written proof >= 3). Every written record is re-verified with nd_verify and its cap
asserted; the shape table, overlap table and render check are written to data/dsc/.
"""
import argparse, json, os, sys, glob, gzip, random, collections, itertools, statistics, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from nd_verify.verify import parse_proof_tokens, parse_formula, ParseError
from gen import canon_key
from patterns import classify

POOL6 = 'data/p2/pool_cap6_recon.jsonl'
POOL8 = 'data/p2/pool_cap8.jsonl'
ORE_SHARDS = 'data/dsc/raw_ore*.w*.jsonl'
EXCLUDE = ['data/p2/heldout.jsonl', 'data/p2/targets_depth3.jsonl', 'data/p2/transfer_depth3.jsonl',
           'data/p2/targets_reductio_req.jsonl', 'data/p2/transfer_reductio_req.jsonl',
           'data/r3_1/depth3_req.jsonl', 'data/r3_1/depth3_req_transfer.jsonl',
           'data/ladder/rl_targets.jsonl', 'data/ladder/transfer.jsonl', 'targets/validation_36.jsonl']
RULES = ['AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']
ATOMS = ['P', 'Q', 'R', 'S']
SIZE = 155000
# per-length shares of the full cap-6 pool (measured 2026-09-22 on all 723,534 classes; see data/dsc/README.md)
SHARES = {'a1': None, 'a2': {L: 0.2 for L in range(2, 7)}, 'a3': {L: 1 / 7 for L in range(2, 9)},
          'a4': {2: 0.0, 3: 0.05, 4: 0.15, 5: 0.30, 6: 0.50}}
QUOTA_A2 = {'ORE': 0.10, 'ANDE': 0.08, 'BOTE': 0.05}     # ANDE = ANDE1 or ANDE2
# Natural per-length rates of the other two patterns, drawn exactly as the control's assembler draws them (make_coverage_sets.assemble_set
# NATURAL table: the take-home's class-deduplicated raw cap-6 pool, 32,000 per length); 7-8 (A3 only): pool_cap8.jsonl's own per-length rates
# (class-deduplicated, uncapped = the follow-up's "natural cap-8 rates"; measured 2026-09-22 07:12 on all 2,435,041 records).
NATURAL = {2: {'reductio': 0, 'derived_ore': 0}, 3: {'reductio': 0, 'derived_ore': 0}, 4: {'reductio': 0, 'derived_ore': 0},
           5: {'reductio': 5549 / 32000, 'derived_ore': 28 / 32000}, 6: {'reductio': 5338 / 32000, 'derived_ore': 63 / 32000},
           7: {'reductio': 12752 / 220502, 'derived_ore': 7570 / 220502}, 8: {'reductio': 13135 / 253870, 'derived_ore': 34511 / 253870}}


def opn(fn, mode='rt'):
    return gzip.open(fn, mode) if fn.endswith('.gz') else open(fn, mode)


def written_depth(proof):
    """max box depth of the WRITTEN proof (number of '|' after the line index)."""
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
    for fn in EXCLUDE:
        for l in opn(fn):
            if not l.strip():
                continue
            r = json.loads(l)
            ks.add(r['key'] if 'key' in r else canon_key(r['thm'].strip()))
    return ks


def counts_from_shares(shares, size):
    lens = sorted(shares)
    c = {L: int(round(shares[L] * size)) for L in lens}
    diff = size - sum(c.values())
    for L in sorted(lens, key=lambda L: -shares[L]):   # fix rounding on the largest bins
        if diff == 0:
            break
        step = 1 if diff > 0 else -1
        c[L] += step; diff -= step
    return c


def scan(fn, excl, seen, lens, src_id, full_hist=None):
    """Stream one pool file. Returns list of (src_id, offset, n_lines, ORE, ANDE, BOTE, reductio, derived_ore) of eligible records and a stats Counter."""
    idx = []; st = collections.Counter()
    with open(fn, 'rb') as f:
        off = 0
        for raw in f:
            L0 = len(raw)
            r = json.loads(raw)
            st['read'] += 1
            if full_hist is not None:
                full_hist[r['n_lines']] += 1
            if r['n_lines'] in lens:
                if r['key'] in excl:
                    st['excluded_class'] += 1
                elif r['key'] in seen:
                    st['dup_class'] += 1
                elif r['pat'].get('depth3') or written_depth(r['proof']) >= 3:
                    st['depth3'] += 1; st[f"depth3_{'pruned' if r['pat'].get('depth3') else 'written_only'}"] += 1
                else:
                    seen.add(r['key'])
                    ru = set(r['rules'])
                    idx.append((src_id, off, r['n_lines'], 'ORE' in ru, bool(ru & {'ANDE1', 'ANDE2'}), 'BOTE' in ru, bool(r['pat'].get('reductio')), bool(r['pat'].get('derived_ore'))))
                    st['eligible'] += 1; st[f'eligible_len{r["n_lines"]}'] += 1
            off += L0
    return idx, st


def select(idx, counts, rng, quota=None):
    """idx: eligible records; counts: L -> n. quota: rule -> n proofs (A2). Returns the selected list."""
    by = collections.defaultdict(list)
    for x in idx:
        by[x[2]].append(x)
    for L in by:
        rng.shuffle(by[L])
    picked = {L: [] for L in counts}
    pset = set()
    report = {}
    if quota:
        flag = {'ORE': 3, 'ANDE': 4, 'BOTE': 5}
        for rule in ('ORE', 'ANDE', 'BOTE'):
            have = sum(1 for L in picked for x in picked[L] if x[flag[rule]])
            need = quota[rule] - have
            avail = {L: [x for x in by[L] if x[flag[rule]] and x not in pset] for L in counts}
            room = {L: counts[L] - len(picked[L]) for L in counts}
            tot = sum(min(len(avail[L]), room[L]) for L in counts)
            if need > tot:
                raise SystemExit(f'quota {rule}: need {need} more, only {tot} available within the length quotas')
            alloc = {L: int(round(need * len(avail[L]) / max(1, sum(len(v) for v in avail.values())))) for L in counts}
            for L in counts:
                alloc[L] = min(alloc[L], len(avail[L]), room[L])
            d = need - sum(alloc.values())
            for L in sorted(counts, key=lambda L: -len(avail[L])):
                while d > 0 and alloc[L] < min(len(avail[L]), room[L]):
                    alloc[L] += 1; d -= 1
                while d < 0 and alloc[L] > 0:
                    alloc[L] -= 1; d += 1
            for L in counts:
                take = avail[L][:alloc[L]]
                picked[L] += take; pset.update(take)
            report[rule] = {'quota': quota[rule], 'already': have, 'added': need, 'by_len': alloc, 'avail_by_len': {L: len(v) for L, v in avail.items()}}
    report['pattern_fill'] = {}
    for L in counts:
        rest = counts[L] - len(picked[L])
        target = {p: int(round(counts[L] * NATURAL[L][p])) for p in ('reductio', 'derived_ore')}
        have = {'reductio': sum(1 for x in picked[L] if x[6]), 'derived_ore': sum(1 for x in picked[L] if x[7])}
        need = {p: max(0, target[p] - have[p]) for p in target}
        cands = collections.defaultdict(list)
        for x in by[L]:
            if x not in pset:
                cands[(x[6], x[7])].append(x)
        def take(k, n):
            got = cands[k][:n]; del cands[k][:n]; return got
        fill = []
        n_both = min(need['reductio'], need['derived_ore'], len(cands[(True, True)]))
        fill += take((True, True), n_both); need['reductio'] -= n_both; need['derived_ore'] -= n_both
        fill += take((True, False), min(need['reductio'], len(cands[(True, False)])))
        fill += take((False, True), min(need['derived_ore'], len(cands[(False, True)])))
        fill = fill[:rest]
        fill += take((False, False), rest - len(fill))
        short = rest - len(fill)
        if short > 0:      # not enough pattern-free proofs: top up from whatever is left (reported)
            for k in ((True, False), (False, True), (True, True)):
                fill += take(k, rest - len(fill))
        if len(fill) < rest:
            raise SystemExit(f'length {L}: need {rest} more records, only {len(fill)} eligible')
        picked[L] += fill; pset.update(fill)
        report['pattern_fill'][L] = {'n': counts[L], 'target': target, 'from_quota_picks': have, 'achieved': {'reductio': sum(1 for x in picked[L] if x[6]), 'derived_ore': sum(1 for x in picked[L] if x[7])},
                                     'pattern_free_shortfall': max(0, short)}
    out = [x for L in counts for x in picked[L]]
    rng.shuffle(out)
    return out, report


def contradictory(prompt):
    """premises jointly unsatisfiable (classical truth tables over the atoms present)?"""
    toks = prompt.split()
    prem_toks = toks[1:toks.index('SEQ')]
    if not prem_toks:
        return False
    prems = []; i = 0
    while i < len(prem_toks):
        if prem_toks[i] == ',':
            i += 1; continue
        f, i = parse_formula(prem_toks, i); prems.append(f)

    def ev(f, v):
        k = f[0]
        if k == 'atom': return v[f[1]]
        if k == 'bot': return False
        if k == 'not': return not ev(f[1], v)
        a, b = ev(f[1], v), ev(f[2], v)
        return a and b if k == 'and' else (a or b if k == 'or' else (not a) or b)
    for bits in itertools.product([False, True], repeat=4):
        v = dict(zip(ATOMS, bits))
        if all(ev(p, v) for p in prems):
            return False
    return True


def boxes_inside_ore(proof):
    try:
        lines = parse_proof_tokens(proof.split())
    except ParseError:
        return 0
    depth = {ln['idx']: ln['depth'] for ln in lines}
    n = 0
    for ln in lines:
        if ln['rule'] == 'ORE' and len(ln['refs']) == 5:
            _, a1, e1, a2, e2 = ln['refs']
            if any(depth[i] >= ln['depth'] + 2 for i in depth if a1 <= i <= e1 or a2 <= i <= e2):
                n += 1
    return n


def insensitive_key(thm):
    """renaming class with premise order ignored: min over the 24 atom permutations of the sorted-premise sequent."""
    lhs, rhs = thm.split('|-')
    prems = [p.strip() for p in lhs.split(' , ') if p.strip()]
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        ps = sorted(' '.join(m.get(t, t) for t in p.split()) for p in prems)
        c = ' , '.join(ps) + ' |- ' + ' '.join(m.get(t, t) for t in rhs.split())
        if best is None or c < best:
            best = c
    return best


def shape_and_overlap(fn, tag, outdir, cap):
    from lean_tok import LeanTokenizer
    tk = LeanTokenizer('lean_seq')
    st = collections.Counter(); L = collections.Counter(); D = collections.Counter(); NP = collections.Counter()
    R = collections.Counter(); ntok_p, ntok_q = [], []
    keys, ikeys = [], []
    recs_for_render = []
    rng = random.Random(0)
    n = 0
    for l in opn(fn):
        if not l.strip():
            continue
        r = json.loads(l); n += 1
        ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
        assert ok and nl == r['n_lines'] <= cap, (reason, nl, r['name'])
        L[nl] += 1
        wd = written_depth(r['proof']); D[wd] += 1
        cl = classify(r['proof']); clw = classify(r['proof'], pruned=False)
        assert not cl['depth3'] and not clw['depth3'] and wd < 3, r['name']
        st['derived_ore_pruned'] += cl['derived_ore']; st['reductio_pruned'] += cl['reductio']
        st['derived_ore_written'] += clw['derived_ore']; st['reductio_written'] += clw['reductio']
        for ru in set(r['rules']):
            R[ru] += 1
        st['ande_any'] += bool(set(r['rules']) & {'ANDE1', 'ANDE2'})
        NP[r['n_prem']] += 1
        st['contradictory_premises'] += contradictory(r['prompt'])
        st['boxes_inside_ore_proofs'] += boxes_inside_ore(r['proof']) > 0
        st['trivial_prem_is_concl'] += r['thm'].split('|-')[1].strip() in [p.strip() for p in r['thm'].split('|-')[0].split(' , ')]
        ids = tk.encode_proof(r['proof']); ntok_q.append(len(ids)); ntok_p.append(len(tk.encode_prompt(r['prompt'])))
        keys.append(r['key']); ikeys.append(insensitive_key(r['thm'].strip()))
        if (n % 50 == 0 or n <= 3000) and len(recs_for_render) < 3000:
            recs_for_render.append(r)
    shape = {'set': fn, 'n': n, 'len_hist': dict(sorted(L.items())), 'len_share': {k: v / n for k, v in sorted(L.items())},
             'written_box_depth_hist': dict(sorted(D.items())), 'rule_share': {ru: R[ru] / n for ru in RULES}, 'rule_count': {ru: R[ru] for ru in RULES},
             'ande_any_share': st['ande_any'] / n, 'n_prem_hist': dict(sorted(NP.items())), 'contradictory_premise_share': st['contradictory_premises'] / n,
             'boxes_inside_ore_proofs': st['boxes_inside_ore_proofs'], 'trivial_prem_is_concl_share': st['trivial_prem_is_concl'] / n,
             'pattern_counts': {k: st[k] for k in ('derived_ore_pruned', 'reductio_pruned', 'derived_ore_written', 'reductio_written')}, 'depth3_count': 0,
             'tokens_lean_seq': {'prompt_mean': statistics.mean(ntok_p), 'proof_mean': statistics.mean(ntok_q), 'total_mean': statistics.mean(ntok_p) + statistics.mean(ntok_q),
                                 'proof_max': max(ntok_q), 'total_max': max(a + b for a, b in zip(ntok_p, ntok_q))}}
    # overlap with every pool, order-sensitive (key) and premise-order-insensitive
    kset, ikset = set(keys), set(ikeys)
    assert len(kset) == n, 'duplicate classes inside the set'
    ov = {}
    for pf in EXCLUDE:
        pk, pik = set(), set()
        for l in opn(pf):
            if not l.strip():
                continue
            r = json.loads(l)
            pk.add(r['key'] if 'key' in r else canon_key(r['thm'].strip())); pik.add(insensitive_key(r['thm'].strip()))
        ov[pf] = {'pool_n': len(pk), 'order_sensitive': len(pk & kset), 'premise_order_insensitive': len(pik & ikset)}
    shape['overlap'] = ov
    # render check: 3,000 records render -> inverse -> identical ND proof; Lean accepts 1,000 literal texts; 300 theorem-swapped negatives rejected
    from lean_gate import lean_check
    rr = recs_for_render[:3000]
    n_id = 0; texts = []
    for r in rr:
        ids = tk.encode_proof(r['proof']); ids = tk.shift_abs(ids, rng)
        nd = tk.decode(ids); n_id += nd == r['proof']; texts.append(tk.last_text)
    pos = [(tk.statement(r['prompt']), t) for r, t in zip(rr[:1000], texts[:1000])]
    neg = [(tk.statement(rr[(k + 7) % len(rr)]['prompt']), texts[k]) for k in range(min(300, len(rr)))]
    ok_pos, w1, c1 = lean_check(pos); ok_neg, w2, c2 = lean_check(neg)
    shape['render_check'] = {'rendered': len(rr), 'inverse_identical': n_id, 'lean_positive_n': len(pos), 'lean_positive_accepted': sum(ok_pos),
                             'lean_negative_n': len(neg), 'lean_negative_rejected': sum(1 for o in ok_neg if not o), 'lean_wall_s': w1 + w2}
    os.makedirs(outdir, exist_ok=True)
    json.dump(shape, open(f'{outdir}/shape_{tag}.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in shape.items() if k not in ('overlap',)}, indent=None)[:3000])
    print('overlap', json.dumps(ov))
    return shape


def cmd_assemble(a):
    t0 = time.time()
    rng = random.Random(a.seed)
    excl = exclusion_keys()
    print(f'{len(excl)} excluded classes from {len(EXCLUDE)} files', flush=True)
    lens6 = set(range(2, 7))
    seen = set(); full_hist = collections.Counter(); stats = {}
    sources = [POOL6]
    idx, st = scan(POOL6, excl, seen, lens6, 0, full_hist); stats[POOL6] = dict(st)
    print(POOL6, dict(st), flush=True)
    if a.arm == 'a2':
        for k, fn in enumerate(sorted(glob.glob(ORE_SHARDS))):
            sources.append(fn)
            i2, s2 = scan(fn, excl, seen, lens6, len(sources) - 1); idx += i2; stats[fn] = dict(s2)
            print(fn, dict(s2), flush=True)
    if a.arm == 'a3':
        sources.append(POOL8)
        i8, s8 = scan(POOL8, excl, seen, {7, 8}, len(sources) - 1); idx += i8; stats[POOL8] = dict(s8)
        print(POOL8, dict(s8), flush=True)
    tot = sum(full_hist.values())
    shares = SHARES[a.arm] or {L: full_hist[L] / tot for L in sorted(lens6)}
    counts = counts_from_shares(shares, a.size)
    cap = 8 if a.arm == 'a3' else 6
    quota = {k: int(round(v * a.size)) for k, v in QUOTA_A2.items()} if a.arm == 'a2' else None
    print('target counts', counts, 'quota', quota, flush=True)
    sel, qrep = select(idx, counts, rng, quota)
    assert len(sel) == a.size
    os.makedirs(a.outdir, exist_ok=True)
    fn = f'{a.outdir}/train_{a.arm}.jsonl.gz'
    fhs = [open(s, 'rb') for s in sources]
    with gzip.open(fn, 'wt') as fo:
        for i, (src, off, L, *_ ) in enumerate(sel):
            fhs[src].seek(off); r = json.loads(fhs[src].readline())
            ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
            assert ok and nl == r['n_lines'] == L <= cap, (reason, r)
            assert not r['pat'].get('depth3') and written_depth(r['proof']) < 3
            rec = {'name': f'train_{a.arm}_{i}', 'thm': r['thm'], 'key': r['key'], 'prompt': r['prompt'], 'proof': r['proof'],
                   'text': r['prompt'] + ' ' + r['proof'], 'n_lines': r['n_lines'], 'rules': r['rules'], 'n_prem': r['n_prem'],
                   'pat': {p: bool(r['pat'].get(p)) for p in ('derived_ore', 'reductio', 'depth3')}, 'src': os.path.basename(sources[src])}
            fo.write(json.dumps(rec) + '\n')
    rep = {'arm': a.arm, 'seed': a.seed, 'size': a.size, 'cap': cap, 'sources': sources, 'scan_stats': stats, 'full_pool_len_hist': dict(sorted(full_hist.items())),
           'shares_used': shares, 'counts': counts, 'quota': quota, 'quota_report': {k: v for k, v in qrep.items() if k != 'pattern_fill'}, 'pattern_fill': qrep.get('pattern_fill'), 'natural_rates': NATURAL, 'n_excluded_classes': len(excl), 'secs': time.time() - t0}
    json.dump(rep, open(f'{a.outdir}/assemble_report_{a.arm}.json', 'w'), indent=1)
    print('written', fn, f'{time.time() - t0:.0f}s', json.dumps(qrep.get('pattern_fill')), flush=True)
    if not a.no_shape:
        shape_and_overlap(fn, a.arm, a.outdir, cap)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('assemble'); s.add_argument('--arm', required=True, choices=['a1', 'a2', 'a3', 'a4']); s.add_argument('--seed', type=int, default=0)
    s.add_argument('--size', type=int, default=SIZE); s.add_argument('--outdir', default='data/dsc'); s.add_argument('--no_shape', action='store_true')
    h = sub.add_parser('shape'); h.add_argument('--set', required=True); h.add_argument('--tag', required=True); h.add_argument('--outdir', default='data/dsc'); h.add_argument('--cap', type=int, default=6)
    a = ap.parse_args()
    if a.cmd == 'assemble':
        cmd_assemble(a)
    else:
        shape_and_overlap(a.set, a.tag, a.outdir, a.cap)


if __name__ == '__main__':
    main()
