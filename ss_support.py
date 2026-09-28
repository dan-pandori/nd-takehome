#!/usr/bin/env python3
"""support-state: `support.py`'s per-theorem large-k protocol for a STATE-conditioned checkpoint (run `state-env`),
sampled in the environment (`state_sample.env_generate`; for a `lean_staten` checkpoint that is `Env(canon=True,
assign=True)`: the environment names what a step introduces).

  python3 ss_support.py --ckpt ckpts/se/stage1_SN_s0.pt --model base --stage s1 \
      --in data/sc/theorems.jsonl --k 10000 --stop_at 50 --temperature 0.8 --seed 0 --batch 4096 \
      --out artifacts/ss/s1_base_T08_s0 --shard 0/1

Judging: every attempt the environment finishes is assembled into its literal `lean_seq` text and Lean checks that
text (`lean_gate.gate`; Lean alone decides, `nd_verify` judges nothing).  Set $LEAN_GATE_DUMP to keep every distinct
checked (prompt, literal text, ND, verdict).  Distinct proofs are counted after start-index normalisation of the
ND string (`normalize.norm`), as in support.py.

Stopping rule (checked after each env_generate call; a call is batch x 1, 2, 4, ... up to --max_chunk), record format and resumability are support.py's, so `sc_analysis.py`-style code reads both.  Extra
fields: n_leanrej (the environment finished, Lean rejected), n_trunc_action / n_step_cap (length-cap hits: the
policy's truncation line), env_end (how attempts ended).
"""
import argparse, json, os, sys, time, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from state_sample import env_generate
from normalize import norm
from lean_judge import n_lines
from support import proof_term_size, md5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--model', required=True, help='label: base | ei')
    ap.add_argument('--stage', default='s1')
    ap.add_argument('--in', dest='inp', default='data/sc/theorems.jsonl')
    ap.add_argument('--names', default=None, help='file of theorem names, one per line: restrict to these')
    ap.add_argument('--out', required=True, help='prefix; writes <out>.s<shard>.jsonl')
    ap.add_argument('--k', type=int, default=10000)
    ap.add_argument('--stop_at', type=int, default=50)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0, help='SAMPLING seed; must differ between two runs that are pooled')
    ap.add_argument('--model_seed', type=int, default=None, help='Stage-1 seed of --ckpt (record label); defaults to --seed')
    ap.add_argument('--batch', type=int, default=4096)
    ap.add_argument('--max_chunk', type=int, default=8, help='attempts per env_generate call grow 1x, 2x, 4x ... up '
                    'to this many x batch: the worklist keeps the decode batch full, and easy theorems still stop early')
    ap.add_argument('--max_action', type=int, default=256)
    ap.add_argument('--max_steps', type=int, default=48)
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--fail_keep', type=int, default=3)
    a = ap.parse_args()
    if a.model_seed is None:
        a.model_seed = a.seed
    si, sn = map(int, a.shard.split('/'))
    dev = 'cuda'
    ck_md5 = md5(a.ckpt)
    model, tok, _ = load_ckpt(a.ckpt, dev)
    assert getattr(tok, 'mode', '').startswith('lean_state'), 'ss_support.py expects a state-conditioned checkpoint'
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
    print(f'[{a.out} s{si}/{sn}] {len(recs)} theorems, {len(done)} done, {len(todo)} to do; model={a.model} '
          f'ckpt={os.path.basename(a.ckpt)} md5={ck_md5[:8]} mode={tok.mode} k={a.k} stop_at={a.stop_at} '
          f'T={a.temperature} batch={a.batch} max_action={a.max_action} max_steps={a.max_steps} seed={a.seed}', flush=True)
    rng = random.Random(a.seed * 7717 + si)
    t_start = time.time()
    tot_tried = 0
    with open(out_fn, 'a') as fo:
        for ti, r in enumerate(todo):
            t0 = time.time()
            counts = collections.Counter()      # normalised accepted ND -> count
            first_idx, first_text = {}, {}
            n = n_parse = n_rej = n_ok = 0
            fail_parse, n_parse_seen, fail_rej = [], 0, []
            st = {}
            calls = 0
            while n < a.k and not (a.stop_at and n_ok >= a.stop_at):
                b = min(a.batch * min(a.max_chunk, 2 ** calls), a.k - n)
                calls += 1
                tx = []
                outs = env_generate(model, tok, [r['prompt']] * b, greedy=False, temperature=a.temperature,
                                    max_action=a.max_action, max_steps=a.max_steps, batch=a.batch,
                                    seed=a.seed * 1000003 + n, stats=st, gate=True, texts_out=tx)
                for j, (nd, t) in enumerate(zip(outs, tx)):
                    if nd.startswith('LEANPARSE'):
                        n_parse += 1; n_parse_seen += 1
                        if len(fail_parse) < a.fail_keep:
                            fail_parse.append(nd)
                        elif rng.random() < a.fail_keep / n_parse_seen:
                            fail_parse[rng.randrange(a.fail_keep)] = nd
                        continue
                    if nd.startswith('LEANREJ'):
                        n_rej += 1
                        if len(fail_rej) < a.fail_keep:
                            fail_rej.append(t)
                        continue
                    s = norm(nd)
                    if s not in counts:
                        first_idx[s] = n + j + 1
                        first_text[s] = t
                    counts[s] += 1
                    n_ok += 1
                n += b
            acc = sorted(counts, key=lambda s: first_idx[s])
            ee = st.get('env_end', {})
            rec = {'name': r['name'], 'L_true': r['L_true'], 'schema': r.get('schema'), 'source': r.get('source'),
                   'model': a.model, 'ckpt': a.ckpt, 'ckpt_md5': ck_md5, 'tok_mode': tok.mode,
                   'temperature': a.temperature, 'seed': a.model_seed, 'sampling_seed': a.seed, 'stage': a.stage,
                   'k_requested': a.k, 'stop_at': a.stop_at, 'batch': a.batch, 'max_chunk': a.max_chunk, 'max_action': a.max_action,
                   'max_steps': a.max_steps, 'n_tried': n, 'n_ok': n_ok, 'n_distinct_ok': len(acc),
                   'n_parse_fail': n_parse, 'n_leanrej': n_rej,
                   'n_trunc_action': int(ee.get('truncated', 0)), 'n_step_cap': int(ee.get('step_cap', 0)),
                   'env_end': dict(ee), 'env_steps_mean': (sum(k * v for k, v in st.get('env_steps', {}).items()) /
                                                           max(1, sum(st.get('env_steps', {}).values()))),
                   'first_hit': (first_idx[acc[0]] if acc else None),
                   'stopped_early': bool(a.stop_at and n_ok >= a.stop_at and n < a.k),
                   'wall_s': round(time.time() - t0, 2), 'env_wall_s': round(st.get('env_wall_s', 0.0), 2),
                   'peak_alloc_gb': round(torch.cuda.max_memory_allocated() / 2 ** 30, 2),
                   'proofs': [{'proof': s, 'count': counts[s], 'first': first_idx[s], 'n_lines': n_lines(s),
                               'term_size': proof_term_size(s), 'lean_text': first_text[s]} for s in acc],
                   'fail_parse_sample': fail_parse, 'fail_leanrej_sample': fail_rej}
            assert sum(p['count'] for p in rec['proofs']) == n_ok
            fo.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fo.flush()
            tot_tried += n
            el = time.time() - t_start
            print(f'  [{ti+1}/{len(todo)}] {r["name"]} L{r["L_true"]} n={n} ok={n_ok} distinct_ok={len(acc)} '
                  f'rej={n_rej} parse={n_parse} | {tot_tried/el:.0f} att/s | {el/60:.1f} min, {tot_tried} att, '
                  f'peak {rec["peak_alloc_gb"]} GB', flush=True)
    el = time.time() - t_start
    print(f'DONE {out_fn}: {len(todo)} theorems, {tot_tried} attempts in {el/60:.1f} min = '
          f'{tot_tried/max(el,1e-9):.0f} att/s', flush=True)


if __name__ == '__main__':
    main()
