#!/usr/bin/env python3
"""Free generation against Kalmár's construction (run kalmar-pretrain, read-outs E2 / E3 and G1's supplied-premise read).

  python3 kalmar/kal_free.py --ckpt <ckpt> --in data/kalmar/tf1200_kal_sl.jsonl --k 1 --temperature 0 \
      --out artifacts/kalmar/free/<model>__tf1200_greedy.json [--supply_pr] [--max_steps 1024] [--batch 1024]

The environment loop of `state_sample.env_generate` (same worklist, same per-attempt name base, same noise keys,
same end rules), plus a record of every action the environment applied (`Env._eff`, i.e. with the names it
assigned).  `--supply_pr`: before the model acts, the environment applies the algorithm's premise lines
(`have n : F := h<k> ;`), so the model never has to write a premise token it was not trained on (G1, read (b)).

Every finished attempt's literal text goes to Lean (`lean_gate.gate`).  Each attempt is compared with the algorithm's
trajectory (the record's sl proof, names shifted by the attempt's base):
  follow      the attempt's actions equal the algorithm's, all the way (it is then the algorithm's proof)
  dev_step    index of the first action that differs (the state there is on the algorithm's trajectory)
  dev_tag     the algorithm's step type at that index (kalmar.TAGS); dev_depth, dev_decile
  valid       Lean accepted the finished proof; for a deviating valid attempt, its action count against the
              algorithm's (shorter = a shortcut)
Output: per-attempt rows (name, base, end, n_actions, follow, dev_*, valid, text if Lean-accepted) and a summary by
atom count, by deviation step type, depth and decile.
"""
import argparse, collections, gzip, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import record
from model import load_ckpt
from sample import generate_ids_fast
from state_env import Env, is_name
from state_sample import NAME_BASE_MAX, prompt_ids
from tf_agree import states_of, shift, masked


@torch.no_grad()
def env_generate_rec(model, tok, prompts, greedy, temperature, max_action, max_steps, batch, seed, prefix=None,
                     stats=None):
    """state_sample.env_generate with the applied actions recorded.  prefix[i] (optional): actions the environment
    applies to attempt i before the model acts (names are re-assigned by the environment, as for the model's own).
    -> list of dicts (nd, text, acts, end, base, steps)."""
    dev = next(model.parameters()).device
    st = stats if stats is not None else {}
    res = [None] * len(prompts)
    live, nxt, wave = [], 0, 0
    record.count(attempts=len(prompts))

    def finish(i, e, end):
        nd = e.nd()
        res[i] = {'nd': nd, 'text': tok.text(e.text) if e.done and not nd.startswith('LEANPARSE') else None,
                  'acts': e._rec, 'end': end, 'base': e.base, 'steps': e.steps}
        st[end] = st.get(end, 0) + 1

    while nxt < len(prompts) or live:
        while len(live) < batch and nxt < len(prompts):
            base = random.Random(seed * 1000003 + nxt).randint(0, NAME_BASE_MAX)
            e = Env(prompts[nxt], canon=True, base=base, assign=True)
            e._rec = []
            bad = False
            for pa in (prefix[nxt] if prefix else []):
                ok, why = e.apply(pa)
                if not ok:
                    bad = True
                    break
                e._rec.append(list(e._eff))
            if bad:
                finish(nxt, e, 'prefix_failed'); nxt += 1; continue
            live.append((nxt, e)); nxt += 1
        if not live:
            break
        pids = [prompt_ids(tok, e) for _, e in live]
        record.count(actions=len(live))
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            outs = generate_ids_fast(model, tok, pids, goals=None, greedy=greedy, temperature=temperature,
                                     max_new=max_action, seed=seed * 100003 + wave, early='eos', compact=True,
                                     stats=st)
        wave += 1
        keep = []
        for (i, e), o in zip(live, outs):
            atoks, ended = tok.decode_action(o)
            if not ended:
                finish(i, e, 'truncated'); continue
            ok, why = e.apply(atoks)
            if not ok:
                e._rec.append(list(atoks))
                finish(i, e, 'syntax'); continue
            e._rec.append(list(e._eff))
            if e.done:
                finish(i, e, 'done'); continue
            if e.steps >= max_steps:
                finish(i, e, 'step_cap'); continue
            keep.append((i, e))
        live = keep
        del outs
    st['waves'] = wave
    if dev.type == 'cuda':
        st['peak_alloc_gb'] = torch.cuda.max_memory_allocated() / 2 ** 30
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--k', type=int, default=1)
    ap.add_argument('--temperature', type=float, default=0.0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--max_action', type=int, default=512)
    ap.add_argument('--max_steps', type=int, default=1024)
    ap.add_argument('--supply_pr', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    record.save_config(vars(a), a.out)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, extra = load_ckpt(a.ckpt, dev)
    model.eval()
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.limit:
        recs = recs[:a.limit]
    algo = []                    # per record: list of (action base 0, tag, depth)
    for r in recs:
        st = states_of(r['prompt'], r['proof'])
        tags = r.get('kal_tags') or r.get('tags')
        algo.append([(act, tg, d) for (s, act, d), tg in zip(st, tags)])
    prompts = [r['prompt'] for r in recs for _ in range(a.k)]
    prefix = None
    if a.supply_pr:
        prefix = []
        for ri, r in enumerate(recs):
            pr = [act for act, tg, d in algo[ri] if tg == 'pr']
            prefix += [pr] * a.k
    stats = {}
    t0 = time.time()
    res = env_generate_rec(model, tok, prompts, greedy=(a.temperature == 0), temperature=max(a.temperature, 1e-6),
                           max_action=a.max_action, max_steps=a.max_steps, batch=a.batch, seed=a.seed, prefix=prefix,
                           stats=stats)
    gen_s = time.time() - t0
    from lean_gate import gate
    nds = gate(tok, prompts, [x['nd'] for x in res], [x['text'] for x in res])
    lean_s = time.time() - t0 - gen_s
    rows = []
    for j, (x, nd) in enumerate(zip(res, nds)):
        ri = j // a.k
        al = algo[ri]
        b = x['base']
        valid = x['end'] == 'done' and not nd.startswith('LEAN')
        dev_step = None
        for t, act in enumerate(x['acts']):
            if t >= len(al) or masked(act) != masked(shift(al[t][0], b)):
                dev_step = t
                break
        if dev_step is None and len(x['acts']) < len(al):
            dev_step = len(x['acts'])            # ended early without a differing action (truncation / cap)
        follow = dev_step is None and x['end'] == 'done'
        row = {'name': recs[ri].get('name'), 'i': ri, 'base': b, 'end': x['end'], 'n_actions': len(x['acts']),
               'algo_actions': len(al), 'follow': follow, 'valid': valid, 'n_atoms': recs[ri].get('n_atoms')}
        if dev_step is not None and dev_step < len(al):
            row.update(dev_step=dev_step, dev_tag=al[dev_step][1], dev_depth=al[dev_step][2],
                       dev_decile=min(9, int(10 * dev_step / len(al))))
        if valid:
            row['text'] = x['text']
        rows.append(row)
    # summary
    by = collections.defaultdict(collections.Counter)
    for r in rows:
        for key in ('all', f'atoms={r["n_atoms"]}'):
            c = by[key]
            c['n'] += 1; c['valid'] += r['valid']; c['follow'] += r['follow']
            c['dev_valid'] += r['valid'] and not r['follow']
            c['dev_valid_shorter'] += r['valid'] and not r['follow'] and r['n_actions'] < r['algo_actions']
            c[f'end={r["end"]}'] += 1
    dev_by = collections.defaultdict(collections.Counter)
    for r in rows:
        if 'dev_tag' in r:
            dev_by['tag'][r['dev_tag']] += 1; dev_by['depth'][r['dev_depth']] += 1; dev_by['decile'][r['dev_decile']] += 1
    per_thm = collections.defaultdict(list)
    for r in rows:
        per_thm[r['i']].append(r['valid'])
    summ = {'ckpt': a.ckpt, 'in': a.inp, 'k': a.k, 'temperature': a.temperature, 'seed': a.seed, 'batch': a.batch,
            'max_action': a.max_action, 'max_steps': a.max_steps, 'supply_pr': a.supply_pr, 'n_theorems': len(recs),
            'n_attempts': len(rows), 'gen_s': round(gen_s, 1), 'lean_s': round(lean_s, 1),
            'solved_theorems': sum(any(v) for v in per_thm.values()),
            'by': {k: dict(v) for k, v in sorted(by.items())}, 'deviation': {k: dict(v) for k, v in dev_by.items()},
            'env': {k: v for k, v in stats.items() if not isinstance(v, (list, dict))}}
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(summ, open(a.out, 'w'), indent=1)
    with gzip.open(a.out.replace('.json', '') + '.rows.jsonl.gz', 'wt') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(json.dumps({k: summ[k] for k in ('n_attempts', 'solved_theorems', 'gen_s', 'lean_s')}))
    for k, v in sorted(by.items()):
        print(f'  {k:10s} n {v["n"]:6d}  valid {v["valid"] / v["n"]:.4f}  follow {v["follow"] / v["n"]:.4f}  '
              f'dev-valid {v["dev_valid"]}  shorter {v["dev_valid_shorter"]}')


if __name__ == '__main__':
    main()
