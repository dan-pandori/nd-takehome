#!/usr/bin/env python3
"""Large-k sampling of a Lean-format checkpoint with the run's acceptance rule (ds-composition, readiness 1):
a sample counts iff nd_verify accepts the denoted ND proof AND Lean accepts the literal sampled text.

  python3 coverage_lean.py --ckpt ckpts/dsc/stage1_a1_s0.pt --in data/p2/targets_depth3.jsonl --k 2000 --temperature 0.8 --seed 0 \
      --out artifacts/dsc/cov_a1_s0_depth3 --batch 1024 --procs 4

Same bookkeeping as coverage.py (one record per theorem; every distinct verified success stored with its hit count, pattern
labels and first sample index; start-index normalisation is the identity for Lean decodes, which always number from N1), plus:
  * the literal Lean texts: per distinct ND proof, every distinct literal text that produced it is checked by Lean
    (lean_gate.lean_check, the in-loop gate's checker); the record stores the accepted text(s) (`texts_ok`), the rejected ones
    (`texts_rej`) and the per-text hit counts, so `count` (= samples counted) is re-derivable: count = sum of hits of accepted texts;
  * per-theorem 2 x 2 agreement (`gate`: distinct texts nd-ok/lean-ok, nd-ok/lean-rej, nd-rej/lean-ok (never checked here, see below), and
    parse failures), and the sample-level counts `n_ok_nd` (nd_verify accepts) vs `n_ok` (both accept).
nd_verify runs first on each distinct ND proof; Lean is asked only about the texts of nd_verify-accepted proofs (the protocol's
"nd_verify first, Lean on the distinct nd_verify-accepted proofs"); texts of nd_verify-rejected proofs are not sent to Lean.
Failures are not stored. Resumable: theorems already present in the output file are skipped.
"""
import argparse, json, os, sys, time, collections, multiprocessing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from sample import generate_ids, generate_ids_fast
from nd_verify import verify_text
from prune import pruned_length
from normalize import norm
from patterns import classify, PATTERNS
from lean_gate import lean_check

BUDGETS = (32, 128, 512, 1000, 2000, 10000)
PATS = list(PATTERNS) + ['derived_ore_strict', 'derived_dn']


def _verify_one(args):
    prompt, s = args
    ok, reason, nl = verify_text(prompt + ' ' + s)
    if not ok:
        return None
    cl = classify(s) or {}
    return {'written': nl, 'pruned': pruned_length(prompt, s), 'pat': {p: bool(cl.get(p)) for p in PATS}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True, help='output prefix; writes <out>.s<shard>.jsonl')
    ap.add_argument('--k', type=int, default=2000)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--lenfield', default='n_lines')
    ap.add_argument('--procs', type=int, default=1)
    a = ap.parse_args()
    pool = multiprocessing.get_context('fork').Pool(a.procs) if a.procs > 1 else None
    si, sn = map(int, a.shard.split('/'))
    dev = 'cuda'
    model, tok, _ = load_ckpt(a.ckpt, dev)
    assert hasattr(tok, 'statement'), 'coverage_lean.py is for Lean-format checkpoints'
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    recs = [r for i, r in enumerate(recs) if i % sn == si]
    if a.limit:
        recs = recs[:a.limit]
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    out_fn = f'{a.out}.s{si}.jsonl'
    done = set()
    if os.path.exists(out_fn):
        for l in open(out_fn):
            if l.strip():
                done.add(json.loads(l)['name'])
    print(f'shard {si}/{sn}: {len(recs)} theorems, {len(done)} already done; k={a.k} T={a.temperature} batch={a.batch}', flush=True)
    gen = torch.Generator(device=dev)
    gen.manual_seed(a.seed * 100003 + si * 7919)
    # ds-composition 2026-09-23: the fast decode path (run efficiency) is used unless ND_SAMPLE_PATH=base.  Its noise is
    # keyed by (chunk seed, step, slot), so each batch gets its own seed from the same base as the base path's generator.
    fast = os.environ.get('ND_SAMPLE_PATH', 'fast') == 'fast'
    chunk_seed = a.seed * 100003 + si * 7919
    t_start = time.time(); n_done = 0
    G = collections.Counter()
    with open(out_fn, 'a') as fo:
        for r in recs:
            name = r.get('name', r.get('thm'))
            if name in done:
                continue
            t0 = time.time()
            pid = tok.encode_prompt(r['prompt'])
            counts = collections.Counter()            # normalised ND proof -> samples
            texts = collections.defaultdict(collections.Counter)   # normalised ND proof -> literal text -> samples
            first_idx = {}                            # (nd proof, text) -> first 1-based sample index
            n_parse = 0
            n = 0
            while n < a.k:
                b = min(a.batch, a.k - n)
                with torch.autocast('cuda', dtype=torch.bfloat16):
                    if fast:
                        outs = generate_ids_fast(model, tok, [pid] * b, greedy=False, temperature=a.temperature,
                                                 max_new=a.max_new, seed=chunk_seed, early='eos', compact=True)
                        chunk_seed += 1
                    else:
                        outs = generate_ids(model, tok, [pid] * b, greedy=False, temperature=a.temperature, max_new=a.max_new, gen=gen)
                for j, o in enumerate(outs):
                    nd = tok.decode(o); tx = tok.last_text
                    if nd.startswith('LEANPARSE'):
                        n_parse += 1; counts['LEANPARSE'] += 1
                        continue
                    s = norm(nd)
                    counts[s] += 1; texts[s][tx] += 1
                    first_idx.setdefault((s, tx), n + j + 1)
                n += b
            strs = [s for s in counts if s != 'LEANPARSE']
            jobs = [(r['prompt'], s) for s in strs]
            res = pool.map(_verify_one, jobs, chunksize=32) if pool else [_verify_one(j) for j in jobs]
            nd_ok = {s: x for s, x in zip(strs, res) if x}
            # Lean on every distinct literal text of every nd_verify-accepted proof
            items = [(s, tx) for s in nd_ok for tx in texts[s]]
            lean_ok, wall, cpu = lean_check([(tok.statement(r['prompt']), tx) for s, tx in items])
            lok = {it: ok for it, ok in zip(items, lean_ok)}
            ok_proofs = []
            for s, x in nd_ok.items():
                t_ok = {tx: c for tx, c in texts[s].items() if lok[(s, tx)]}
                t_rej = {tx: c for tx, c in texts[s].items() if not lok[(s, tx)]}
                G['nd_ok_lean_ok_texts'] += len(t_ok); G['nd_ok_lean_rej_texts'] += len(t_rej)
                if not t_ok:
                    continue
                ok_proofs.append({'proof': s, 'count': sum(t_ok.values()), 'count_nd_only': sum(t_rej.values()), 'written': x['written'], 'pruned': x['pruned'],
                                  'first': min(first_idx[(s, tx)] for tx in t_ok), 'pat': x['pat'],
                                  'texts_ok': [{'text': tx, 'count': c} for tx, c in sorted(t_ok.items(), key=lambda y: -y[1])],
                                  'texts_rej': [{'text': tx, 'count': c} for tx, c in sorted(t_rej.items(), key=lambda y: -y[1])]})
            n_ok = sum(p['count'] for p in ok_proofs)
            n_ok_nd = sum(counts[s] for s in nd_ok)
            first_hit = min((p['first'] for p in ok_proofs), default=None)
            wh, ph = collections.Counter(), collections.Counter()
            for p in ok_proofs:
                wh[p['written']] += 1; ph[p['pruned']] += 1
            ok_proofs.sort(key=lambda p: -p['count'])
            hits_by_pattern = {p: sum(x['count'] for x in ok_proofs if x['pat'][p]) for p in PATS}
            distinct_by_pattern = {p: sum(1 for x in ok_proofs if x['pat'][p]) for p in PATS}
            G['samples'] += n; G['parse_fail'] += n_parse; G['nd_ok_samples'] += n_ok_nd; G['both_ok_samples'] += n_ok; G['lean_wall_s'] += wall; G['lean_proc_s'] += cpu
            rec = {'name': name, 'thm': r.get('thm'), 'prompt': r['prompt'], 'gen_lines': r.get(a.lenfield), 'min_lines_ub': r.get('min_lines_ub'), 'schema': r.get('schema'),
                   'n_tried': n, 'n_parse_fail': n_parse, 'n_ok_nd': n_ok_nd, 'n_ok': n_ok, 'n_distinct_ok': len(ok_proofs), 'n_distinct_nd_ok': len(nd_ok), 'n_distinct_all': len(strs),
                   'first_hit': first_hit, 'solved_within': {str(B): bool(first_hit is not None and first_hit <= B) for B in BUDGETS},
                   'written_hist': dict(sorted(wh.items())), 'pruned_hist': dict(sorted(ph.items())),
                   'hits_by_pattern': hits_by_pattern, 'distinct_by_pattern': distinct_by_pattern,
                   'gate': {'distinct_texts_checked': len(items), 'nd_ok_lean_ok': sum(lean_ok), 'nd_ok_lean_rej': len(items) - sum(lean_ok), 'lean_wall_s': wall, 'lean_proc_s': cpu},
                   'proofs': ok_proofs}
            fo.write(json.dumps(rec) + '\n'); fo.flush()
            torch.cuda.empty_cache()
            n_done += 1
            el = time.time() - t_start
            print(f'{name}: n_ok {n_ok}/{n} (nd-only {n_ok_nd - n_ok}, parse-fail {n_parse}) distinct_ok {len(ok_proofs)} first_hit {first_hit} written_hist {rec["written_hist"]} '
                  f'lean {wall:.0f}s ({time.time()-t0:.0f}s; {n_done} done, {el/n_done:.0f}s/thm, ETA {(len(recs)-len(done)-n_done)*el/n_done/60:.0f} min)', flush=True)
    json.dump(dict(G), open(f'{a.out}.s{si}.gate.json', 'w'), indent=1)
    print('DONE', dict(G), flush=True)


if __name__ == '__main__':
    main()
