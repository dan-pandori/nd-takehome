#!/usr/bin/env python3
"""create-or-elicit: assemble the knockout pretraining set K12- (σ removed, refilled to 155,000).

sigma (σ) = double negation (DN) applied to a negation-introduction (NEGI) line.  The knockout drops every K12 record
whose WRITTEN or PRUNED proof has a DN line citing a DERIVED double negation (`patterns.derived_dn`, σ+): this contains
every σ record (`patterns.reductio`, 16,703) and 258 records whose DN cites an IMPE / ORE / BOTE / DN / ANDE line (indirect
routes, e.g. an Or-elimination whose branches each build ¬¬G).  DN stays where it cites a premise (PR) or a hypothesis
(AS); NEGI stays everywhere.  The "lemma route" (an IMPI box that applies DN to its ¬¬X hypothesis, used by IMPE on a
NEGI-built ¬¬X) occurs in 0 K12 records and is asserted absent from the refill.

Refill, per pruned length L, exactly the number removed from that length, uniformly at random (seeded) from the records
of K12's OWN source pools that K12 did not use:
  * L <= 6: data/p2/train_depth3_f0_a1.jsonl (lean-format's a1 set; K12's short bins are a uniform subsample of it);
  * L >= 7: data/kh/pool_long_kh.jsonl (kh_gen.py; K12's long bins are a uniform draw from its eligible records).
Every refill record passes K12's filters (kh_assemble.py): same pruned length, box depth <= 2 in the pruned and the
written form, not in K12's exclusion pools, long bins not in the a1 set's classes; plus: σ+-free in both forms, not the
renaming class of ANY K12 record (kept or removed), and not in ANY evaluation pool of this run (every non-training
.jsonl under data/, targets/ and data/eval_only/textbook72/) under canon_key AND a premise-order-invariant key
(lexicographic minimum over the 24 atom bijections of (sorted premises, conclusion)).
Lean checks of the refill records run on a pod (coe_lean_check.py), not here.

  python3 coe/coe_assemble.py --k12 data/coe/src/train_k12.jsonl.gz --a1 data/coe/src/train_depth3_f0_a1.jsonl \
      --pool data/coe/src/pool_long_kh.jsonl --out data/coe/train_k12ko.jsonl.gz --seed 0
"""
import argparse, collections, glob, gzip, hashlib, itertools, json, os, random, sys, time
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)
from gen import canon_key, ATOMS
from patterns import parse, prune_lines, derived_dn
from coe.coe_sigma import flags, _origin

KH_EXCLUDE = ['data/p2/heldout.jsonl', 'data/p2/targets_depth3.jsonl', 'data/p2/transfer_depth3.jsonl',
              'data/p2/targets_reductio_req.jsonl', 'data/p2/transfer_reductio_req.jsonl',
              'data/r3_1/depth3_req.jsonl', 'data/r3_1/depth3_req_transfer.jsonl',
              'data/ladder/rl_targets.jsonl', 'data/ladder/transfer.jsonl', 'targets/validation_36.jsonl',
              'data/dsc/targets_depth3_sub250.jsonl']


def opener(fn):
    return gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)


def thm_of(r):
    if 'thm' in r:
        return r['thm'].strip()
    p = r['prompt'].strip()
    assert p.startswith('THM ') and p.endswith(' PRF'), p
    body = ' ' + p[4:-4] + ' '
    prem, concl = body.split(' SEQ ')
    return (prem.strip() + ' |- ' + concl.strip()).strip()


_PERMS = list(itertools.permutations(ATOMS))


def canon2(thm):
    """premise-order-invariant renaming class: min over atom bijections of (sorted premises, conclusion)."""
    lhs, rhs = thm.split('|-')
    prems = [p.strip() for p in lhs.split(' , ') if p.strip()]
    concl = rhs.strip()
    best = None
    for perm in _PERMS:
        m = dict(zip(ATOMS, perm))
        ren = lambda s: ' '.join(m.get(t, t) for t in s.split())
        cand = (tuple(sorted(ren(p) for p in prems)), ren(concl))
        if best is None or cand < best:
            best = cand
    return ' , '.join(best[0]) + ' |- ' + best[1]


def written_depth(proof):
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


def lemma_route(lines):
    by = {ln['idx']: ln for ln in lines}
    for ln in lines:
        if ln['rule'] == 'IMPE' and len(ln['refs']) == 2:
            imp, arg = _origin(by, ln['refs'][0]), _origin(by, ln['refs'][1])
            if imp is None or arg is None:
                continue
            if arg['rule'] == 'NEGI' and arg['formula'][0] == 'not' and arg['formula'][1][0] == 'not' and imp['rule'] == 'IMPI':
                a_idx, last = imp['refs'][0], imp['refs'][1]
                for x in lines:
                    if a_idx <= x['idx'] <= last and x['rule'] == 'DN' and x['refs']:
                        o = _origin(by, x['refs'][0])
                        if o is not None and o['idx'] == a_idx:
                            return True
    return False


def knock(proof):
    """-> (drop?, info) ; drop if σ+ (DN of a derived double negation) in the written or pruned form."""
    fl = flags(proof)
    if fl is None:
        return None, None
    drop = any(fl[f]['dn_derived'] or fl[f]['sigma_strict'] or fl[f]['sigma_chain'] for f in ('w', 'p'))
    return drop, fl


def eval_pool_files():
    fs = set(KH_EXCLUDE)
    for pat in ('data/**/*.jsonl', 'targets/*.jsonl'):
        for fn in glob.glob(os.path.join(ROOT, pat), recursive=True):
            rel = os.path.relpath(fn, ROOT)
            base = os.path.basename(rel)
            if base.startswith('train') or rel.startswith('data/coe/') or 'pool' in base or base.startswith('raw_'):
                continue
            fs.add(rel)
    return sorted(fs)


def exclusion_keys(files):
    k1, k2, per, missing = set(), set(), {}, []
    for fn in files:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            missing.append(fn)
            continue
        n = 0
        for l in opener(p):
            if not l.strip():
                continue
            try:
                r = json.loads(l)
                t = thm_of(r)
            except Exception:
                continue
            if '|-' not in t:
                continue
            k1.add(canon_key(t)); k2.add(canon2(t)); n += 1
        per[fn] = n
    return k1, k2, per, missing


def md5(fn):
    h = hashlib.md5()
    with open(fn, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--k12', required=True)
    ap.add_argument('--a1', required=True)
    ap.add_argument('--pool', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    rng = random.Random(a.seed)
    files = eval_pool_files()
    ex1, ex2, ex_per, ex_missing = exclusion_keys(files)
    print(f'exclusion: {len(files)} files ({len(ex_missing)} missing: {ex_missing}), {len(ex1)} canon_key, {len(ex2)} canon2 classes', flush=True)

    # ---- K12: keep / remove ----------------------------------------------------
    kept, removed_by_len = [], collections.Counter()
    k12_k1, k12_k2 = set(), set()
    k12_len = collections.Counter()
    removed_kind = collections.Counter()
    for l in opener(a.k12):
        r = json.loads(l)
        t = thm_of(r)
        k12_k1.add(r.get('key') or canon_key(t)); k12_k2.add(canon2(t))
        L = r['n_lines']; k12_len[L] += 1
        drop, fl = knock(r['proof'])
        assert drop is not None, 'K12 record does not parse'
        if drop:
            removed_by_len[L] += 1
            removed_kind['sigma_strict' if (fl['w']['sigma_strict'] or fl['p']['sigma_strict']) else 'dn_derived_only'] += 1
        else:
            kept.append(l if l.endswith('\n') else l + '\n')
    print(f'K12 {sum(k12_len.values())} records; removed {sum(removed_by_len.values())} {dict(removed_kind)}; per length {dict(sorted(removed_by_len.items()))}', flush=True)

    # ---- candidates --------------------------------------------------------------
    a1_keys = set()
    cand_k2 = set()      # premise-order-invariant classes already taken by an eligible candidate (first in file order wins)
    scan = collections.defaultdict(collections.Counter)
    cands = collections.defaultdict(list)

    def consider(r, src, L):
        t = thm_of(r)
        k1 = r.get('key') or canon_key(t)
        sc = scan[src]
        sc['in_range'] += 1
        if k1 in k12_k1 or canon2(t) in k12_k2:
            sc['k12_class'] += 1; return
        if k1 in ex1 or canon2(t) in ex2:
            sc['eval_class'] += 1; return
        if src == 'pool' and k1 in a1_keys:
            sc['a1_class'] += 1; return
        lines = parse(r['proof'])
        if lines is None:
            sc['parse_fail'] += 1; return
        pl = prune_lines(lines)
        if len(pl) != L and src == 'a1':
            sc['pruned_len_mismatch'] += 1; return
        if max((x['depth'] for x in pl), default=0) >= 3 or written_depth(r['proof']) >= 3:
            sc['depth3'] += 1; return
        drop, fl = knock(r['proof'])
        if drop:
            sc['sigma_plus'] += 1; return
        if lemma_route(lines):
            sc['lemma_route'] += 1; return
        k2 = canon2(t)
        if k2 in cand_k2:
            sc['dup_canon2_in_pools'] += 1; return
        cand_k2.add(k2)
        sc['eligible'] += 1
        cands[L].append(r)

    a1_rows = []
    for l in opener(a.a1):
        r = json.loads(l)
        a1_keys.add(r.get('key') or canon_key(thm_of(r)))
        if removed_by_len.get(r['n_lines']) and r['n_lines'] <= 6:
            a1_rows.append(r)
    for r in a1_rows:
        consider(r, 'a1', r['n_lines'])
    del a1_rows
    for l in opener(a.pool):
        r = json.loads(l)
        L = r['n_lines']
        if L >= 7 and removed_by_len.get(L):
            consider(r, 'pool', L)
    print('scan', {k: dict(v) for k, v in scan.items()}, flush=True)
    print('eligible per length', {L: len(v) for L, v in sorted(cands.items())}, flush=True)

    # ---- draw ----------------------------------------------------------------------
    refill = []
    for L in sorted(removed_by_len):
        need = removed_by_len[L]
        pool_L = cands[L]
        assert len(pool_L) >= need, f'length {L}: need {need}, eligible {len(pool_L)}'
        idx = sorted(rng.sample(range(len(pool_L)), need))
        for i in idx:
            refill.append(pool_L[i])
    seen1, seen2 = set(), set()
    out_lines = list(kept)
    for r in refill:
        t = thm_of(r)
        k1, k2 = r.get('key') or canon_key(t), canon2(t)
        assert k1 not in seen1 and k2 not in seen2, 'duplicate class inside the refill'
        seen1.add(k1); seen2.add(k2)
        rr = dict(r); rr['coe_refill'] = True
        out_lines.append(json.dumps(rr) + '\n')
    rng.shuffle(out_lines)

    # ---- checks -----------------------------------------------------------------------
    per_len = collections.Counter(); keys1 = set(); keys2 = set(); texts = set()
    n_refill = 0
    for l in out_lines:
        r = json.loads(l)
        t = thm_of(r)
        L = r['n_lines']; per_len[L] += 1
        k1, k2 = r.get('key') or canon_key(t), canon2(t)
        assert k1 not in keys1, 'duplicate renaming class'
        keys1.add(k1); keys2.add(k2)
        txt = r['prompt'] + ' ' + r['proof']
        assert txt not in texts, 'duplicate text'; texts.add(txt)
        drop, fl = knock(r['proof'])
        assert drop is False, 'sigma+ leaked'
        assert written_depth(r['proof']) < 3
        if r.get('coe_refill'):
            n_refill += 1
            assert k1 not in ex1 and k2 not in ex2, 'refill in an evaluation pool'
            assert k1 not in k12_k1 and k2 not in k12_k2, 'refill in a K12 class'
            assert not lemma_route(parse(r['proof']))
    assert per_len == k12_len, (dict(per_len), dict(k12_len))
    assert len(out_lines) == sum(k12_len.values())
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with gzip.open(a.out, 'wt') as f:
        f.writelines(out_lines)
    k12_in_eval2 = len(k12_k2 & ex2)
    rep = {'out': a.out, 'md5_out_uncompressed_lines': hashlib.md5(''.join(out_lines).encode()).hexdigest(),
           'seed': a.seed, 'records': len(out_lines), 'kept_from_k12': len(kept), 'refill': n_refill,
           'removed_per_length': {str(k): v for k, v in sorted(removed_by_len.items())}, 'removed_kind': dict(removed_kind),
           'per_length': {str(k): v for k, v in sorted(per_len.items())},
           'eligible_per_length': {str(L): len(v) for L, v in sorted(cands.items())},
           'scan': {k: dict(v) for k, v in scan.items()},
           'inputs': {'k12': a.k12, 'a1': a.a1, 'pool': a.pool},
           'input_md5': {'k12': md5(a.k12), 'a1': md5(a.a1), 'pool': md5(a.pool)},
           'exclusion_files': ex_per, 'exclusion_missing': ex_missing,
           'exclusion_classes': {'canon_key': len(ex1), 'canon2': len(ex2)},
           'k12_classes_in_eval_pools_canon2': k12_in_eval2,
           'distinct_classes_canon_key': len(keys1), 'distinct_classes_canon2': len(keys2),
           'secs': round(time.time() - t0, 1)}
    json.dump(rep, open(a.out.replace('.jsonl.gz', '') + '_assemble_report.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k not in ('exclusion_files', 'scan')}, indent=1))


if __name__ == '__main__':
    main()
