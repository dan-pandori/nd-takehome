#!/usr/bin/env python3
"""Large-k sampling of one checkpoint with success-only logging (Phase 1.3 / Phase 2 base reachability).

  python coverage.py --ckpt ckpts/stage1_abs.pt --in data/transfer.jsonl --k 10000 --temperature 0.8 \
      --out artifacts/cov_base_transfer_k1e4 --shard 0/3 --batch 4096 --seed 0

For every theorem: samples k proofs (T), decodes, START-INDEX-NORMALISES each proof (normalize.norm),
verifies each DISTINCT normalised string once (the verifier accepts any start index, so validity is
invariant under renumbering), and writes ONE record per theorem to <out>.s<shard>.jsonl:
  {name, thm, prompt, gen_lines, n_tried, n_ok, n_distinct_ok, first_hit (1-based sample index of the
   first verified sample, or null), solved_within: {32:.., 128:.., 512:.., 1000:.., 10000:.., 100000:..}
   (first_hit <= B, an exact pass@B draw), written_hist, pruned_hist,
   proofs: [{proof (normalised), count, written, pruned}]  -- verified successes only}
Failures are not stored. Resumable: theorems already present in the output file are skipped.
Samples are i.i.d. per theorem, so first_hit <= B is one Bernoulli draw of pass@B and n_ok/n_tried estimates the per-sample rate.
"""
import argparse, json, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from sample import generate_ids
from nd_verify import verify_text
from prune import pruned_length
from normalize import norm

BUDGETS = (32, 128, 512, 1000, 10000, 100000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True, help='output prefix; writes <out>.s<shard>.jsonl')
    ap.add_argument('--k', type=int, default=10000)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--batch', type=int, default=4096)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--shard', default='0/1', help='i/n: process theorems i, i+n, i+2n, ...')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--lenfield', default='n_lines')
    a = ap.parse_args()
    si, sn = map(int, a.shard.split('/'))
    dev = 'cuda'
    model, tok, _ = load_ckpt(a.ckpt, dev)
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
    t_start = time.time()
    n_done = 0
    with open(out_fn, 'a') as fo:
        for r in recs:
            name = r.get('name', r.get('thm'))
            if name in done:
                continue
            t0 = time.time()
            pid = tok.encode_prompt(r['prompt'])
            counts = collections.Counter()      # normalised proof string -> count
            first_idx = {}                      # normalised proof string -> first 1-based sample index
            n = 0
            while n < a.k:
                b = min(a.batch, a.k - n)
                with torch.autocast('cuda', dtype=torch.bfloat16):
                    outs = generate_ids(model, tok, [pid] * b, greedy=False, temperature=a.temperature, max_new=a.max_new, gen=gen)
                for j, o in enumerate(outs):
                    s = norm(tok.decode(o))
                    counts[s] += 1
                    if s not in first_idx:
                        first_idx[s] = n + j + 1
                n += b
            # verify distinct strings once
            ok_proofs = []
            for s, c in counts.items():
                ok, reason, nl = verify_text(r['prompt'] + ' ' + s)
                if ok:
                    ok_proofs.append({'proof': s, 'count': c, 'written': nl, 'pruned': pruned_length(r['prompt'], s), 'first': first_idx[s]})
            n_ok = sum(p['count'] for p in ok_proofs)
            # pass@B from sample order: we know the first index of each distinct success and its total count, but not
            # the position of every repeat; hits_within counts distinct successes whose first occurrence is within B,
            # and solved_within = first_hit <= B (exact).
            first_hit = min((p['first'] for p in ok_proofs), default=None)
            wh, ph = collections.Counter(), collections.Counter()
            for p in ok_proofs:
                wh[p['written']] += 1; ph[p['pruned']] += 1
            ok_proofs.sort(key=lambda p: -p['count'])
            rec = {'name': name, 'thm': r.get('thm'), 'prompt': r['prompt'], 'gen_lines': r.get(a.lenfield),
                   'n_tried': n, 'n_ok': n_ok, 'n_distinct_ok': len(ok_proofs), 'n_distinct_all': len(counts),
                   'first_hit': first_hit, 'solved_within': {str(B): bool(first_hit is not None and first_hit <= B) for B in BUDGETS},
                   'written_hist': dict(sorted(wh.items())), 'pruned_hist': dict(sorted(ph.items())), 'proofs': ok_proofs}
            fo.write(json.dumps(rec) + '\n'); fo.flush()
            torch.cuda.empty_cache()
            n_done += 1
            el = time.time() - t_start
            print(f'{name}: n_ok {n_ok}/{n} distinct_ok {len(ok_proofs)} first_hit {first_hit} written_hist {rec["written_hist"]} '
                  f'({time.time()-t0:.0f}s; {n_done} done, {el/n_done:.0f}s/thm, ETA {(len(recs)-len(done)-n_done)*el/n_done/60:.0f} min)', flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
