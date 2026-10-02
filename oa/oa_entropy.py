#!/usr/bin/env python3
"""organism-analysis Q3: policy entropy of stored checkpoints (forward passes only; no training).

  python3 oa/oa_entropy.py --ckpts ckpts.txt --targets targets_s0.jsonl --prompts data/ladder/rl_targets.jsonl \
      --out artifacts/oa/entropy/c12_s0 [--n_prompts 1024 --attempts 4 --batch 2048]

Per checkpoint (`label path` lines) it writes `<out>/<label>.json`:
  * `tf`: teacher-forced entropy on fixed target proofs (tj_score's targets: reference + eventual), at name base 0,
    per step: mean token entropy of softmax(logits / T) over the step's scored tokens (the tokens tj_score scores:
    the action tokens + <eos>, minus the names the environment assigns), T in (1.0, 0.8), and the entropy at the first
    scored token.  Also the per-step log p at base 0 (T 1.0) as a cross-check against tj_score's raw_b0.
  * `onpol`: on-policy rollouts in the environment (state_sample.env_generate's loop, unchanged except that it keeps
    every (prompt ids, generated ids) pair): `attempts` x `n_prompts` fixed RL targets at T 0.8 (the ladder's), then
    one teacher-forced pass over every generated action to get the entropy of softmax(logits / T) at every generated
    token (all generated tokens incl. <eos>; truncated actions included up to max_action).  Reported: mean token
    entropy (T 1.0, T 0.8), mean per-action entropy, the Lean-accepted rate, ends, truncation rate, peak memory.
"""
import argparse, collections, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
import torch.nn.functional as F
import record
from model import load_ckpt
from sample import generate_ids_fast
from state_env import Env
from state_sample import prompt_ids, NAME_BASE_MAX
import tj_score

TEMPS = (1.0, 0.8)
TOK_BUDGET = 1 << 18


@torch.no_grad()
def entropies(model, seqs, dev):
    """seqs: list of (prompt ids, target ids, skip positions) -> list of {T: [entropy per target token]}, lp1 [log p T1]."""
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i][0]) + len(seqs[i][1]))
    out = [None] * len(seqs)
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and (j - i + 1) * (len(seqs[order[j]][0]) + len(seqs[order[j]][1])) <= TOK_BUDGET:
            j += 1
        j = max(j, i + 1)
        ch = [order[q] for q in range(i, j)]
        L = max(len(seqs[c][0]) + len(seqs[c][1]) for c in ch)
        x = torch.zeros((len(ch), L), dtype=torch.long)
        for r, c in enumerate(ch):
            p, q, _ = seqs[c]
            x[r, :len(p) + len(q)] = torch.tensor(list(p) + list(q))
        x = x.to(dev)
        logits = model(x[:, :-1]).float()
        res = {}
        for T in TEMPS:
            lsm = F.log_softmax(logits / T, -1)
            res[T] = (-(lsm.exp() * lsm).sum(-1)).cpu()
            if T == 1.0:
                lp1 = lsm.gather(-1, x[:, 1:, None]).squeeze(-1).cpu()
        for r, c in enumerate(ch):
            p, q, skip = seqs[c]
            sl = slice(len(p) - 1, len(p) + len(q) - 1)
            keep = [k for k in range(len(q)) if k not in skip]
            out[c] = {T: res[T][r, sl][keep].tolist() for T in TEMPS}
            out[c]['lp1'] = lp1[r, sl][keep].tolist()
        i = j
    return out


@torch.no_grad()
def onpolicy(model, tok, prompts, temperature, max_action, max_steps, batch, seed, st):
    """state_sample.env_generate's worklist loop, keeping (prompt ids, generated ids) of every action."""
    dev = next(model.parameters()).device
    cnt = st.setdefault('env_end', collections.Counter())
    pairs, live, nxt, wave, done_ok = [], [], 0, 0, 0
    record.count(attempts=len(prompts))
    while nxt < len(prompts) or live:
        while len(live) < batch and nxt < len(prompts):
            base = random.Random(seed * 1000003 + nxt).randint(0, NAME_BASE_MAX)
            live.append((nxt, Env(prompts[nxt], canon=True, base=base, assign=True))); nxt += 1
        pids = [prompt_ids(tok, e) for _, e in live]
        record.count(actions=len(live))
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            outs = generate_ids_fast(model, tok, pids, goals=None, greedy=False, temperature=temperature,
                                     max_new=max_action, seed=seed * 100003 + wave, early='eos', compact=True, stats=st)
        wave += 1
        keep = []
        for (i, e), p, o in zip(live, pids, outs):
            o = [int(x) for x in o]
            if tok.eos in o:
                o = o[:o.index(tok.eos) + 1]
            o = [x for x in o if x != tok.pad]
            pairs.append((tuple(p), tuple(o), ()))
            atoks, ended = tok.decode_action(o)
            if not ended:
                cnt['truncated'] += 1; continue
            ok, why = e.apply(atoks)
            if not ok:
                cnt['syntax'] += 1; continue
            if e.done:
                cnt['done'] += 1; continue
            if e.steps >= max_steps:
                cnt['step_cap'] += 1; continue
            keep.append((i, e))
        live = keep
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', required=True)
    ap.add_argument('--targets', required=True, help="tj_score-style targets (tid, name, prompt, kind, proof)")
    ap.add_argument('--prompts', default='data/ladder/rl_targets.jsonl')
    ap.add_argument('--out', required=True)
    ap.add_argument('--n_prompts', type=int, default=1024)
    ap.add_argument('--attempts', type=int, default=4)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--max_action', type=int, default=256)
    ap.add_argument('--max_steps', type=int, default=48)
    ap.add_argument('--batch', type=int, default=2048)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    cks = [l.split() for l in open(a.ckpts) if l.strip()]
    _, tok, _ = load_ckpt(cks[0][1], 'cpu')
    assert tok.mode == 'lean_staten' and tok.canon and not tok.with_history
    targets = [json.loads(l) for l in open(a.targets) if l.strip()]
    meta, plan, _ = tj_score.build(targets, tok)
    tids = list(plan)
    tf_seqs = [k for t in tids for k in plan[t][0]]
    allp = [json.loads(l)['prompt'] for l in open(a.prompts) if l.strip()]
    sub = sorted(random.Random(a.seed).sample(range(len(allp)), min(a.n_prompts, len(allp))))
    prompts = [allp[i] for i in sub for _ in range(a.attempts)]
    print(f'{len(tids)} targets ({len(tf_seqs)} steps at base 0); {len(prompts)} on-policy attempts', flush=True)
    for label, path in cks:
        op = os.path.join(a.out, f'{label}.json')
        if os.path.exists(op):
            print(f'skip {label}', flush=True); continue
        t0 = time.time()
        model, _, _ = load_ckpt(path, dev)
        model.eval()
        o = {'label': label, 'path': path}
        with record.compute(phase='entropy_tf', arm=label):
            ent = entropies(model, tf_seqs, dev)
        o['tf'] = {}
        q = 0
        for t in tids:
            steps = []
            for _ in plan[t][0]:
                e = ent[q]; q += 1
                steps.append({'H1': round(sum(e[1.0]) / max(1, len(e[1.0])), 4),
                              'H08': round(sum(e[0.8]) / max(1, len(e[0.8])), 4),
                              'H1_first': round(e[1.0][0], 4) if e[1.0] else None,
                              'lp1': round(sum(e['lp1']), 4)})
            o['tf'][t] = steps
        t1 = time.time()
        st = {}
        if dev == 'cuda':
            torch.cuda.reset_peak_memory_stats()
        with record.compute(phase='entropy_onpolicy', arm=label) as c:
            pairs = onpolicy(model, tok, prompts, a.temperature, a.max_action, a.max_steps, a.batch, a.seed, st)
            ent = entropies(model, pairs, dev)
        ntok = sum(len(e[1.0]) for e in ent)
        o['onpol'] = {
            'n_attempts': len(prompts), 'n_actions': len(pairs), 'n_tokens': ntok,
            'H1_tok': sum(sum(e[1.0]) for e in ent) / ntok, 'H08_tok': sum(sum(e[0.8]) for e in ent) / ntok,
            'H1_act': sum(sum(e[1.0]) / max(1, len(e[1.0])) for e in ent) / len(ent),
            'H08_act': sum(sum(e[0.8]) / max(1, len(e[0.8])) for e in ent) / len(ent),
            'H1_first': sum(e[1.0][0] for e in ent if e[1.0]) / len(ent),
            'ends': dict(st.get('env_end', {})),
            'trunc_rate': st.get('env_end', {}).get('truncated', 0) / max(1, len(pairs)),
            'peak_alloc_gb': torch.cuda.max_memory_allocated() / 2 ** 30 if dev == 'cuda' else None,
            'secs_tf': round(t1 - t0, 1), 'secs_onpol': round(time.time() - t1, 1)}
        with open(op + '.tmp', 'w') as f:
            json.dump(o, f)
        os.replace(op + '.tmp', op)
        p = o['onpol']
        print(f"{label}: H1_tok {p['H1_tok']:.4f} H08_tok {p['H08_tok']:.4f} done {p['ends'].get('done', 0)}/{len(prompts)} "
              f"trunc {p['trunc_rate']:.4f} peak {p['peak_alloc_gb']} GB  tf {p['secs_tf']}s onpol {p['secs_onpol']}s", flush=True)
        del model
        if dev == 'cuda':
            torch.cuda.empty_cache()


if __name__ == '__main__':
    main()
