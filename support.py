#!/usr/bin/env python3
"""support-curves: per-theorem success probability of one checkpoint at large k, with early stopping.

  python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s0.pt --model base --stage s1 \
      --in data/sc/theorems.jsonl --k 4000 --stop_at 50 --temperature 0.8 --seed 0 \
      --batch 2048 --out artifacts/sc/s1_base_T08_s0 --shard 0/2 --procs 3

Why not `coverage.py`: coverage.py samples a FIXED k per theorem and judges once at the end, so a theorem with
p = 0.5 burns all k samples.  This run needs 8-10 M samples, so it stops a theorem once it has `stop_at`
successes; that needs the Lean verdicts DURING the loop, batched per sampling batch.  Judging is otherwise
identical to coverage.py's: start-index-normalise (`normalize.norm`), then one `lean_judge.judge_many` over the
distinct normalised strings (Lean alone decides, Dan 2026-09-27; `nd_verify` judges nothing).

Sampling is i.i.d. per theorem, so (n_tried, n_ok) at a fixed temperature from two runs with different --seed
ADD: stage 2 is an independent continuation of stage 1 and the analysis sums them.

Stopping rule (state it with every p-hat): a theorem stops at the first batch boundary at which n_ok >=
stop_at, or at k.  n is therefore a stopping time and p-hat = n_ok / n_tried carries an O(1/n_ok) bias; at
stop_at = 50 that is ~2 %, far inside the 4+ decades the scatter spans.  Theorems that never reach stop_at
have fixed n = k and an exactly unbiased p-hat.

Writes ONE record per theorem to <out>.s<shard>.jsonl (failures are NOT stored in bulk -- this run draws
~10 M samples and VPS1 has ~8 GB free; `fail_sample` keeps a uniform reservoir of `--fail_keep` failing
literal texts per theorem):
  {name, L_true, schema, model, ckpt, ckpt_md5, temperature, seed, stage, k_requested, stop_at,
   n_tried, n_ok, n_distinct_ok, n_distinct_strings, n_parse_fail, first_hit (1-based, or null),
   stopped_early, gen_s, lean_s, wall_s,
   proofs: [{proof (normalised), count, first, n_lines, term_size, lean_text}],   <- EVERY distinct accepted proof
   fail_sample: [literal text, ...]}
Resumable: theorem names already in the output file are skipped.
"""
import argparse, json, os, sys, time, hashlib, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from sample import generate_ids_fast
from lean_judge import judge_many
from normalize import norm
import re


def _formula_size(f):
    """nodes of one formula's syntax tree: connectives + atoms."""
    return sum(1 for t in f.split() if t in ('~', '&', 'v', '>', 'F') or re.fullmatch(r'[A-Z]', t))


_LINE = re.compile(r'N\d+\s+((?:\|\s*)*)(.*?):')


def proof_term_size(proof):
    """Proof term size = formula nodes summed over the proof's lines.  Byte-identical to
    `review_nf_ladder_cov.proof_term_size`, which the `noise-floor` reviewer used; inlined because that module reads
    files at import time.  Reported alongside line count because under Lean a proof may be shorter than the shortest
    ND proof and may omit premise re-statements, so lines alone are not the whole story (AGENT_POLICY)."""
    tot = 0
    for seg in proof.split(';'):
        seg = seg.strip()
        if not seg or seg == 'QED':
            continue
        m = _LINE.match(seg)
        if m:
            tot += _formula_size(m.group(2))
    return tot


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--model', required=True, help='label: base | ei')
    ap.add_argument('--stage', default='s1')
    ap.add_argument('--in', dest='inp', default='data/sc/theorems.jsonl')
    ap.add_argument('--names', default=None, help='file of theorem names, one per line: restrict to these')
    ap.add_argument('--out', required=True, help='prefix; writes <out>.s<shard>.jsonl')
    ap.add_argument('--k', type=int, default=4000)
    ap.add_argument('--stop_at', type=int, default=50, help='stop a theorem at the first batch boundary with >= this many successes (0 = never)')
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--batch', type=int, default=2048)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--fail_keep', type=int, default=3, help='failing literal texts kept per theorem (storage: this run draws ~10M samples)')
    ap.add_argument('--compact', default='1', choices=['0','1'], help="fast-path KV compaction; ds-generator saw it flip ~1 row in 128 vs the base path")
    ap.add_argument('--early', default='eos', choices=['eos', 'exact', 'goal'], help="fast-path stop rule; 'eos' is sample.generate's default and matches the base path")
    ap.add_argument('--procs', type=int, default=1, help='unused; kept so job lines match coverage.py')
    a = ap.parse_args()
    si, sn = map(int, a.shard.split('/'))
    dev = 'cuda'
    ck_md5 = md5(a.ckpt)
    model, tok, _ = load_ckpt(a.ckpt, dev)
    is_lean = hasattr(tok, 'statement')
    assert is_lean, 'support.py expects a lean_seq checkpoint'
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.names:
        keep = {l.strip() for l in open(a.names) if l.strip()}
        recs = [r for r in recs if r['name'] in keep]
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
    todo = [r for r in recs if r['name'] not in done]
    print(f'[{a.out} s{si}/{sn}] {len(recs)} theorems, {len(done)} done, {len(todo)} to do; '
          f'model={a.model} ckpt={os.path.basename(a.ckpt)} md5={ck_md5[:8]} k={a.k} stop_at={a.stop_at} '
          f'T={a.temperature} batch={a.batch} max_new={a.max_new} seed={a.seed}', flush=True)
    gen = torch.Generator(device=dev)
    gen.manual_seed(a.seed * 100003 + si * 7919 + 13)
    rng = random.Random(a.seed * 7717 + si)
    t_start = time.time()
    tot_tried = tot_gen = tot_lean = 0.0
    with open(out_fn, 'a') as fo:
        for ti, r in enumerate(todo):
            t0 = time.time()
            pid = tok.encode_prompt(r['prompt'])
            counts = collections.Counter()     # normalised accepted-or-not string -> count
            first_idx, first_text, verdict = {}, {}, {}
            n = n_parse = n_ok = 0
            gen_s = lean_s = 0.0
            fail_parse, n_parse_seen = [], 0     # uniform reservoir over grammar-reject literal texts
            while n < a.k and not (a.stop_at and n_ok >= a.stop_at):
                b = min(a.batch, a.k - n)
                tg = time.time()
                with torch.autocast('cuda', dtype=torch.bfloat16):
                    outs = generate_ids_fast(model, tok, [pid] * b, greedy=False, temperature=a.temperature,
                                             max_new=a.max_new, seed=a.seed * 1000003 + n, early=a.early,
                                             compact=(a.compact == '1'))
                fresh = []
                for j, o in enumerate(outs):
                    nd = tok.decode(o)
                    if nd.startswith('LEANPARSE'):
                        n_parse += 1; n_parse_seen += 1
                        if len(fail_parse) < a.fail_keep:
                            fail_parse.append(tok.last_text)
                        elif rng.random() < a.fail_keep / n_parse_seen:
                            fail_parse[rng.randrange(a.fail_keep)] = tok.last_text
                        continue
                    s = norm(nd)
                    if s not in counts:
                        first_idx[s] = n + j + 1
                        first_text[s] = tok.last_text
                        fresh.append(s)
                    counts[s] += 1
                del outs
                gen_s += time.time() - tg
                tl = time.time()
                if fresh:
                    for s, (ok, _, nl) in zip(fresh, judge_many([(r['prompt'], s) for s in fresh])):
                        verdict[s] = (bool(ok), nl)
                lean_s += time.time() - tl
                n += b
                n_ok = sum(c for s, c in counts.items() if verdict[s][0])
            acc = sorted((s for s in counts if verdict[s][0]), key=lambda s: first_idx[s])
            rej = sorted((s for s in counts if not verdict[s][0]), key=lambda s: -counts[s])
            rec = {'name': r['name'], 'L_true': r['L_true'], 'schema': r.get('schema'), 'source': r.get('source'),
                   'model': a.model, 'ckpt': a.ckpt, 'ckpt_md5': ck_md5, 'temperature': a.temperature,
                   'seed': a.seed, 'stage': a.stage, 'k_requested': a.k, 'stop_at': a.stop_at,
                   'n_tried': n, 'n_ok': n_ok, 'n_distinct_ok': len(acc), 'n_distinct_strings': len(counts),
                   'n_parse_fail': n_parse, 'early': a.early, 'compact': a.compact, 'first_hit': (first_idx[acc[0]] if acc else None),
                   'stopped_early': bool(a.stop_at and n_ok >= a.stop_at and n < a.k),
                   'gen_s': round(gen_s, 2), 'lean_s': round(lean_s, 2), 'wall_s': round(time.time() - t0, 2),
                   'proofs': [{'proof': s, 'count': counts[s], 'first': first_idx[s], 'n_lines': verdict[s][1],
                               'term_size': proof_term_size(s), 'lean_text': first_text[s]} for s in acc],
                   'fail_parse_sample': fail_parse,
                   'fail_leanrej_sample': [first_text[s] for s in list(rej)[:a.fail_keep]]}
            assert sum(p['count'] for p in rec['proofs']) == n_ok
            fo.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fo.flush()
            tot_tried += n; tot_gen += gen_s; tot_lean += lean_s
            el = time.time() - t_start
            if ti % 5 == 0 or ti == len(todo) - 1:
                print(f'  [{ti+1}/{len(todo)}] {r["name"]} L{r["L_true"]} n={n} ok={n_ok} distinct_ok={len(acc)} '
                      f'| {tot_tried/el:.0f} samp/s (gen {tot_gen/el:.0%}, lean {tot_lean/el:.0%}) '
                      f'| {el/60:.1f} min, {tot_tried:.0f} samples', flush=True)
    el = time.time() - t_start
    print(f'DONE {out_fn}: {len(todo)} theorems, {tot_tried:.0f} samples in {el/60:.1f} min = '
          f'{tot_tried/max(el,1e-9):.0f} samples/s = {tot_tried/max(el/3600,1e-9):.0f} samples/pod-hour-equiv '
          f'(gen {tot_gen/el:.0%}, lean {tot_lean/el:.0%})', flush=True)


if __name__ == '__main__':
    main()
