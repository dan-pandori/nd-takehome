#!/usr/bin/env python3
"""Minimal on-policy GRPO against the verifier (run 4), on the existing model / sampler.

  python grpo.py --init ckpts/r4/stage1_depth3_f0_a1_s20.pt --name r4/grpo_g8_depth3_f0_a1_s20 \
      --targets data/p2/targets_depth3.jsonl --transfer data/p2/transfer_depth3.jsonl --heldout data/p2/heldout.jsonl \
      --group 8 --batch 800 --updates_per_round 40 --rounds 8 --lr 1e-4 --temperature 0.8 --seed 20

Per update: --batch samples = (--batch / --group) prompts x --group samples each, drawn from the CURRENT weights
(strictly on-policy); reward 1 iff nd_verify accepts the sample as a proof of the prompted sequent, else 0
(unterminated samples get 0); advantage = reward - group mean (no std normalisation; a zero-variance group
contributes exactly zero gradient); loss = -(1 / (N_samples * max_new)) * sum_i A_i * sum_t log pi_T(a_t)
with pi_T = softmax(logits / T) (the sampling distribution), fixed divisor N_samples * max_new; AdamW, constant lr,
weight decay 0, grad-norm clip 1.0; one optimizer step per batch; no KL, no PPO clip (ratio == 1 on-policy).

A "round" = --updates_per_round updates. With --batch 800 and 40 updates per round, a round is 32,000 target
samples = 32 per target, so round r of this script has seen exactly the attempts that round r of expert_iter.py
(k = 32) has seen. At each round boundary the script writes the same files as expert_iter.py so that
phase2_metrics.arm_metrics() applies unchanged:
  artifacts/<name>/round_<r>.json          summaries (targets this round / cumulative, transfer pass@k, greedy)
  artifacts/<name>/found_<r>.jsonl         every distinct verified TARGET proof from the TRAINING samples, with the
                                           round of its first appearance (one record per (target, raw proof))
  artifacts/<name>/found_transfer_<r>.jsonl  same for the evaluation-only transfer samples (k per theorem per round)
  ckpts/<name>_r<r>.pt
and per update a line in artifacts/<name>/updates.jsonl: groups, groups with reward variance, all-zero / all-one
groups, verified-sample rate, samples / groups / new targets with a depth-3 proof (patterns.classify on the pruned,
start-index-normalised model proof), cumulative solved targets and depth-3 targets, mean response length,
fraction unterminated, loss, grad norm, seconds.
"""
import argparse, json, os, sys, random, collections, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn.functional as F
from model import load_ckpt, save_ckpt
from sample import generate_ids, generate
from nd_verify import verify_text
from prune import pruned_length
from eval_set import judge, summarize
from normalize import norm
from patterns import classify


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def sample_groups(model, tok, prompts, G, temperature, max_new, sample_batch, gen):
    """prompts: list of P prompt strings -> list of P lists of G (response_ids, proof_text)."""
    ids = [tok.encode_prompt(p) for p in prompts]
    flat_ids = [ids[i] for i in range(len(prompts)) for _ in range(G)]
    order = sorted(range(len(flat_ids)), key=lambda i: len(flat_ids[i]))
    res = [None] * len(flat_ids)
    dev = next(model.parameters()).device
    for s in range(0, len(order), sample_batch):
        chunk = order[s:s + sample_batch]
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            outs = generate_ids(model, tok, [flat_ids[i] for i in chunk], greedy=False, temperature=temperature, max_new=max_new, gen=gen)
        for i, o in zip(chunk, outs):
            if tok.eos in o:
                o = o[:o.index(tok.eos) + 1]
            res[i] = (o, tok.decode(o))
        del outs
    return [[(flat_ids[i * G + j], *res[i * G + j]) for j in range(G)] for i in range(len(prompts))]


def policy_loss(model, seqs, plens, advs, temperature, divisor, micro, dev):
    """seqs: list of full token lists (prompt + response); plens: prompt lengths; advs: per-sequence advantages.
    Accumulates gradients of  -(1/divisor) * sum_i A_i * sum_t log pi_T(a_t)  over micro-batches. Returns (loss, tokens)."""
    total = 0.0
    n_tok = 0
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    for s in range(0, len(order), micro):
        idx = order[s:s + micro]
        if all(advs[i] == 0.0 for i in idx):
            continue                     # zero advantage everywhere: exactly zero gradient, skip the pass
        T = max(len(seqs[i]) for i in idx)
        x = torch.full((len(idx), T), 0, dtype=torch.long)
        m = torch.zeros((len(idx), T), dtype=torch.bool)
        a = torch.zeros((len(idx),), dtype=torch.float32)
        for r, i in enumerate(idx):
            x[r, :len(seqs[i])] = torch.tensor(seqs[i])
            m[r, plens[i]:len(seqs[i])] = True        # response tokens (targets at positions plens..len-1)
            a[r] = advs[i]
        x, m, a = x.to(dev), m.to(dev), a.to(dev)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            logits = model(x[:, :-1])
        logp = F.log_softmax(logits.float() / temperature, -1)
        tgt = x[:, 1:]
        mk = m[:, 1:]
        lp = logp.gather(-1, tgt[..., None]).squeeze(-1) * mk
        seq_lp = lp.sum(1)                                   # sum_t log pi(a_t) per sequence
        loss = -(a * seq_lp).sum() / divisor
        loss.backward()
        total += loss.item()
        n_tok += int(mk.sum().item())
    return total, n_tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--init', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--targets', default='data/p2/targets_depth3.jsonl')
    ap.add_argument('--transfer', default='data/p2/transfer_depth3.jsonl')
    ap.add_argument('--heldout', default='data/p2/heldout.jsonl')
    ap.add_argument('--group', type=int, default=8)
    ap.add_argument('--batch', type=int, default=800, help='samples per update (= groups x group size)')
    ap.add_argument('--updates_per_round', type=int, default=40)
    ap.add_argument('--rounds', type=int, default=8)
    ap.add_argument('--lr', type=float, default=1e-4)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--k_eval', type=int, default=32, help='transfer samples per theorem per round (evaluation only)')
    ap.add_argument('--sample_batch', type=int, default=800)
    ap.add_argument('--micro', type=int, default=200, help='sequences per backward micro-batch (one optimizer step per update regardless)')
    ap.add_argument('--eval_batch', type=int, default=768)
    ap.add_argument('--pattern', default='depth3')
    ap.add_argument('--clip', type=float, default=1.0)
    ap.add_argument('--std_norm', action='store_true', help='(not used in the pre-registered arms) divide advantages by the group std')
    ap.add_argument('--no_step_on_zero', action='store_true', help='(not used in the pre-registered arms) skip the optimizer step when no group has variance')
    a = ap.parse_args()
    assert a.batch % a.group == 0
    out = f'artifacts/{a.name}'
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.dirname(f'ckpts/{a.name}'), exist_ok=True)
    json.dump(vars(a), open(f'{out}/args.json', 'w'), indent=1)
    dev = torch.device('cuda')
    targets, transfer, heldout = read(a.targets), read(a.transfer), read(a.heldout)
    model, tok, _ = load_ckpt(a.init, dev)
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, 0.95), weight_decay=0.0)
    rng = random.Random(a.seed)
    gen = torch.Generator(device=dev)
    P = a.batch // a.group                       # prompts (groups) per update
    found = collections.defaultdict(list)        # target name -> [{proof, written, pruned, round}]
    found_t = collections.defaultdict(list)
    cls_cache = {}
    pat_targets = set()
    solved_targets = set()
    upd = 0
    ulog = open(f'{out}/updates.jsonl', 'w')
    divisor = float(a.batch * a.max_new)
    t_start = time.time()
    by_name = {t['name']: t for t in targets}
    for r in range(1, a.rounds + 1):
        t_round = time.time()
        # prompt schedule for this round: whole shuffles of the target list, concatenated
        n_groups_round = a.updates_per_round * P
        sched = []
        while len(sched) < n_groups_round:
            perm = list(range(len(targets))); rng.shuffle(perm); sched += perm
        sched = sched[:n_groups_round]
        round_rows = {t['name']: {'n_ok': 0, 'n_tried': 0, 'wl': [], 'pl': [], 'solved': False} for t in targets}
        rstats = collections.Counter()
        new_this = 0
        for u in range(a.updates_per_round):
            t0 = time.time()
            upd += 1
            gidx = sched[u * P:(u + 1) * P]
            batch_t = [targets[i] for i in gidx]
            gen.manual_seed(a.seed * 1000003 + upd)
            model.eval()
            groups = sample_groups(model, tok, [t['prompt'] for t in batch_t], a.group, a.temperature, a.max_new, a.sample_batch, gen)
            model.train()
            t_sample = time.time() - t0
            # rewards
            rows = judge(batch_t, [[g[2] for g in grp] for grp in groups], 'n_lines')
            seqs, plens, advs = [], [], []
            n_var = n_zero = n_one = 0
            n_ok = 0; n_pat_samples = 0; n_pat_groups = 0; n_unterm = 0; resp_len = 0
            for t, grp, row in zip(batch_t, groups, rows):
                good = set(row['proofs'])
                rew = [1.0 if g[2] in good else 0.0 for g in grp]
                sm = sum(rew)
                if sm == 0:
                    n_zero += 1
                elif sm == a.group:
                    n_one += 1
                else:
                    n_var += 1
                mean = sm / a.group
                std = math.sqrt(sum((x - mean) ** 2 for x in rew) / a.group) if a.std_norm else 1.0
                pat_here = False
                for g, rw in zip(grp, rew):
                    pid, rid, ptxt = g
                    seqs.append(pid + rid); plens.append(len(pid))
                    advs.append((rw - mean) / (std if std > 0 else 1.0))
                    resp_len += len(rid)
                    if tok.eos not in rid:
                        n_unterm += 1
                    if rw:
                        n_ok += 1
                        pn = norm(ptxt)
                        if pn not in cls_cache:
                            cls_cache[pn] = classify(pn)
                        cl = cls_cache[pn]
                        if cl and cl[a.pattern]:
                            n_pat_samples += 1; pat_here = True
                            pat_targets.add(t['name'])
                n_pat_groups += pat_here
                # bookkeeping in expert_iter's format (distinct by raw proof string; round = first appearance)
                have = {x['proof'] for x in found[t['name']]}
                for p, wl, pl in zip(row['proofs'], row['written_lens'], row['pruned_lens']):
                    if p not in have:
                        found[t['name']].append({'proof': p, 'written': wl, 'pruned': pl, 'round': r}); new_this += 1; have.add(p)
                rr = round_rows[t['name']]
                rr['n_ok'] += row['n_ok']; rr['n_tried'] += row['n_tried']
                if row['solved']:
                    rr['solved'] = True; solved_targets.add(t['name'])
                    rr['wl'] += row['written_lens']; rr['pl'] += row['pruned_lens']
            t_verify = time.time() - t0 - t_sample
            # update
            opt.zero_grad(set_to_none=True)
            loss, n_tok = policy_loss(model, seqs, plens, advs, a.temperature, divisor, a.micro, dev)
            gn = float(torch.nn.utils.clip_grad_norm_(model.parameters(), a.clip))
            if not (a.no_step_on_zero and n_var == 0):
                opt.step()
            opt.zero_grad(set_to_none=True)
            rec = {'update': upd, 'round': r, 'groups': P, 'group_size': a.group, 'var_groups': n_var, 'zero_groups': n_zero, 'one_groups': n_one,
                   'var_frac': n_var / P, 'sample_acc': n_ok / a.batch, 'n_ok': n_ok,
                   'pattern_samples': n_pat_samples, 'pattern_groups': n_pat_groups,
                   'cum_solved_targets': len(solved_targets), 'cum_pattern_targets': len(pat_targets),
                   'mean_resp_len': resp_len / a.batch, 'frac_unterminated': n_unterm / a.batch,
                   'loss': loss, 'grad_norm': gn, 'resp_tokens': n_tok, 'lr': a.lr,
                   'secs': time.time() - t0, 'secs_sample': t_sample, 'secs_verify': t_verify}
            ulog.write(json.dumps(rec) + '\n'); ulog.flush()
            for k in ('var_groups', 'zero_groups', 'one_groups', 'n_ok', 'pattern_samples', 'pattern_groups'):
                rstats[k] += rec[k]
            if upd % 10 == 0 or upd == 1:
                print(f'[{a.name}] upd {upd} r{r}: var {n_var}/{P} acc {n_ok/a.batch:.4f} pat_samples {n_pat_samples} cum_solved {len(solved_targets)} cum_pat {len(pat_targets)} '
                      f'len {resp_len/a.batch:.1f} unterm {n_unterm} loss {loss:.3e} gn {gn:.3f} {time.time()-t0:.1f}s', flush=True)
        # ---- round boundary: EI-format artefacts ----
        model.eval()
        seed = a.seed * 1000 + r
        stats = {'round': r, 'ckpt': a.init, 'k': a.updates_per_round * a.batch // len(targets), 'temperature': a.temperature, 'seed': seed,
                 'algorithm': 'grpo', 'group': a.group, 'lr': a.lr, 'updates': upd, 'samples': upd * a.batch,
                 'round_var_groups': rstats['var_groups'], 'round_groups': n_groups_round, 'round_var_frac': rstats['var_groups'] / n_groups_round,
                 'round_pattern_samples': rstats['pattern_samples'], 'round_pattern_groups': rstats['pattern_groups']}
        tr_rows = [{'n_lines': t['n_lines'], 'solved': round_rows[t['name']]['solved'], 'written_lens': round_rows[t['name']]['wl'],
                    'pruned_lens': round_rows[t['name']]['pl'], 'reasons': []} for t in targets]
        stats['targets_round'] = summarize(tr_rows, 'n_lines', f'[{a.name} r{r}] targets (this round, training samples)')
        cum_rows = [{'n_lines': t['n_lines'], 'solved': bool(found[t['name']]), 'written_lens': [x['written'] for x in found[t['name']]],
                     'pruned_lens': [x['pruned'] for x in found[t['name']]], 'reasons': []} for t in targets]
        stats['targets_cum'] = summarize(cum_rows, 'n_lines', f'[{a.name} r{r}] targets (cumulative {upd * a.batch} samples)')
        stats['new_proofs_this_round'] = new_this
        stats['target_sample_acc'] = sum(v['n_ok'] for v in round_rows.values()) / max(1, sum(v['n_tried'] for v in round_rows.values()))
        # transfer, sampled (evaluation only, never trained on)
        prompts = [t['prompt'] for t in transfer for _ in range(a.k_eval)]
        flat = generate(model, tok, prompts, greedy=False, temperature=a.temperature, batch=a.eval_batch, seed=seed + 500)
        outs_t = [flat[i * a.k_eval:(i + 1) * a.k_eval] for i in range(len(transfer))]
        rows_t = judge(transfer, outs_t, 'n_lines')
        stats['transfer_round'] = summarize(rows_t, 'n_lines', f'[{a.name} r{r}] transfer (this round, pass@{a.k_eval})')
        stats['transfer_sample_acc'] = sum(x['n_ok'] for x in rows_t) / sum(x['n_tried'] for x in rows_t)
        for t, row in zip(transfer, rows_t):
            have = {x['proof'] for x in found_t[t['name']]}
            for p, wl, pl in zip(row['proofs'], row['written_lens'], row['pruned_lens']):
                if p not in have:
                    found_t[t['name']].append({'proof': p, 'written': wl, 'pruned': pl, 'round': r})
        cum_t = [{'n_lines': t['n_lines'], 'solved': bool(found_t[t['name']]), 'written_lens': [x['written'] for x in found_t[t['name']]],
                  'pruned_lens': [x['pruned'] for x in found_t[t['name']]], 'reasons': []} for t in transfer]
        stats['transfer_cum'] = summarize(cum_t, 'n_lines', f'[{a.name} r{r}] transfer (cumulative {r*a.k_eval} attempts)')
        g = generate(model, tok, [t['prompt'] for t in transfer], greedy=True, batch=a.eval_batch)
        stats['transfer_greedy'] = summarize(judge(transfer, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] transfer greedy')
        g = generate(model, tok, [t['prompt'] for t in heldout], greedy=True, batch=a.eval_batch)
        stats['heldout_greedy'] = summarize(judge(heldout, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] heldout greedy')
        with open(f'{out}/found_{r}.jsonl', 'w') as f:
            for t in targets:
                for x in found[t['name']]:
                    f.write(json.dumps({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'gen_lines': t['n_lines'], **x}) + '\n')
        with open(f'{out}/found_transfer_{r}.jsonl', 'w') as f:
            for t in transfer:
                for x in found_t[t['name']]:
                    f.write(json.dumps({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'gen_lines': t['n_lines'], **x}) + '\n')
        ck = f'ckpts/{a.name}_r{r}.pt'
        save_ckpt(ck, model, tok.mode, extra={'args': vars(a), 'round': r, 'updates': upd})
        stats['ckpt_out'] = ck
        stats['secs'] = time.time() - t_round
        stats['secs_total'] = time.time() - t_start
        json.dump(stats, open(f'{out}/round_{r}.json', 'w'), indent=1)
        print(f'=== [{a.name}] round {r} done in {stats["secs"]:.0f}s; updates {upd}; var frac {stats["round_var_frac"]:.3f}; new proofs {new_this}; '
              f'cum solved {stats["targets_cum"]["solved"]}; cum {a.pattern} targets {len(pat_targets)}; heldout {stats["heldout_greedy"]["rate"]:.3f}', flush=True)
        model.train()
    ulog.close()


if __name__ == '__main__':
    main()
