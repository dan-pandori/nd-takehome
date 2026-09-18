#!/usr/bin/env python3
"""Expert iteration (rejection-sampling fine-tuning) against the verifier, with a frozen control.

  python expert_iter.py --init ckpts/stage1.pt --name ei_s0 --rounds 6 --k 32 --temperature 0.8 --seed 0
  python expert_iter.py --init ckpts/stage1.pt --name frozen_s0 --rounds 6 --k 32 --temperature 0.8 --seed 0 --no_train

Each round r:
  1. sample k proofs per RL target (T), verify, keep verifier-accepted proofs of the prompted sequent
     (distinct, accumulated across rounds);
  2. sample k proofs per TRANSFER theorem (never trained on), verify, record only;
  3. greedy pass@1 on transfer and on the Stage-1 held-out set (in-distribution tracking);
  4. unless --no_train: fine-tune the current model on all accumulated target proofs (each theorem's
     proofs capped at --max_per_thm) mixed with --retain random Stage-1 training records; save ckpt.
Stats per round -> artifacts/<name>/round_<r>.json ; accepted proofs -> artifacts/<name>/found_<r>.jsonl.
With --no_train, round r of the control has seen exactly the same r*k attempts per theorem as the RL arm.
--select longest: train on each theorem's longest dependency-pruned proofs (arm "EI-long").
--relabel: also keep by-product proofs (valid proof of a *different* conclusion from the same premises)
  as extra training data, if their theorem class is not in any evaluation pool and the proof has >= 7 lines.
--exclude_pattern <depth3|reductio|...> (round3-run1 'drift' arms): every found proof is still recorded in
  found_<r>.jsonl, but a proof whose dependency-pruned form has the pattern (patterns.classify) is never put
  into the training mix; the number of excluded proofs / theorems is logged per round.
  python expert_iter.py --test_exclude   # verifier-checked test of the exclusion filter
"""
import argparse, json, os, sys, random, collections, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from prune import pruned_length
from gen import canon_key
from patterns import classify, PATTERNS


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def relabel(prompt, proof):
    """If proof is a valid proof of some other conclusion from the same premises, return (new_prompt, thm)."""
    toks = proof.split()
    if 'QED' not in toks:
        return None
    # last line formula: between the last 'N<i>' line start and ':'... find last ';' before QED, then the line
    body = toks[:toks.index('QED')]
    # split into lines
    lines, cur = [], []
    for t in body:
        cur.append(t)
        if t == ';':
            lines.append(cur); cur = []
    if not lines or cur:
        return None
    last = lines[-1]
    if last[1] == '|':
        return None
    try:
        form = ' '.join(last[1:last.index(':')])
    except ValueError:
        return None
    pre = prompt.split(' SEQ ')[0]
    newp = f'{pre} SEQ {form} PRF'
    ok, reason, nl = verify_text(newp + ' ' + proof)
    if not ok:
        return None
    prem = pre[len('THM '):].strip()
    return newp, f'{prem} |- {form}', nl


def has_pattern(proof, pattern):
    """True iff the dependency-pruned proof has `pattern` (unparsable -> False)."""
    cl = classify(proof)
    return bool(cl and cl.get(pattern))


def test_exclude():
    """Verifier-checked test of the --exclude_pattern filter: pattern proofs are dropped from a training mix, the rest kept."""
    cases = [  # (prompt, proof, {pattern: should be EXCLUDED under --exclude_pattern pattern})
        ('THM SEQ ( P > ( Q > ( R > R ) ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | | R : AS ; N4 | | ( R > R ) : IMPI N3 N3 ; N5 | ( Q > ( R > R ) ) : IMPI N2 N4 ; N6 ( P > ( Q > ( R > R ) ) ) : IMPI N1 N5 ; QED',
         {'depth3': True, 'reductio': False}),
        ('THM SEQ ( P > ( Q > P ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | P : R N1 ; N4 | ( Q > P ) : IMPI N2 N3 ; N5 ( P > ( Q > P ) ) : IMPI N1 N4 ; QED',
         {'depth3': False, 'reductio': False}),
        # depth-3 box that is padding: pruned form is depth 2 -> NOT excluded
        ('THM SEQ ( P > ( Q > P ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | | R : AS ; N4 | | ( R > R ) : IMPI N3 N3 ; N5 | | P : R N1 ; N6 | ( Q > P ) : IMPI N2 N5 ; N7 ( P > ( Q > P ) ) : IMPI N1 N6 ; QED',
         {'depth3': False, 'reductio': False}),
        ('THM ( ~ ( ~ P ) ) SEQ P PRF',
         'N1 ( ~ ( ~ P ) ) : PR ; N2 | ( ~ P ) : AS ; N3 | F : NEGE N2 N1 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; N5 P : DN N4 ; QED',
         {'depth3': False, 'reductio': True}),
        ('THM ( ~ ( ~ P ) ) SEQ P PRF', 'N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; QED', {'depth3': False, 'reductio': False}),
        ('THM ( P > Q ) , ( ~ Q ) SEQ ( ~ P ) PRF',
         'N1 ( P > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | P : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ P ) : NEGI N3 N5 ; QED',
         {'depth3': False, 'reductio': False}),
    ]
    bad = 0
    for prompt, proof, exp in cases:
        ok, reason, nl = verify_text(prompt + ' ' + proof)
        assert ok, (reason, prompt, proof)
        for pat, want in exp.items():
            got = has_pattern(proof, pat)
            bad += got != want
            print(('ok   ' if got == want else 'FAIL ') + f'exclude_pattern={pat}: excluded={got} {prompt[:50]}')
    # the mix-building rule itself: a found list with 3 proofs (2 pattern) under max_per_thm=4 keeps exactly the 1 non-pattern one
    fs = [{'proof': cases[0][1]}, {'proof': cases[1][1]}, {'proof': cases[0][1] + ' '}]
    kept = [x for x in fs if not has_pattern(x['proof'], 'depth3')]
    bad += len(kept) != 1 or kept[0]['proof'] != cases[1][1]
    print(('ok   ' if len(kept) == 1 else 'FAIL ') + f'mix rule keeps {len(kept)} of {len(fs)} (expected 1)')
    print('EXCLUDE_PATTERN TESTS', 'PASS' if not bad else f'FAIL ({bad})')
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    if '--test_exclude' in sys.argv:
        sys.exit(0 if test_exclude() else 1)
    global torch, load_ckpt, generate, judge, summarize
    import torch
    from eval_set import judge, summarize
    from model import load_ckpt
    from sample import generate
    ap.add_argument('--init', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--targets', default='data/rl_targets.jsonl')
    ap.add_argument('--transfer', default='data/transfer.jsonl')
    ap.add_argument('--heldout', default='data/heldout.jsonl')
    ap.add_argument('--train', default='data/train.jsonl')
    ap.add_argument('--rounds', type=int, default=6)
    ap.add_argument('--k', type=int, default=32)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--no_train', action='store_true')
    ap.add_argument('--ft_steps', type=int, default=600)
    ap.add_argument('--ft_lr', type=float, default=3e-4)
    ap.add_argument('--retain', type=int, default=20000)
    ap.add_argument('--max_per_thm', type=int, default=4)
    ap.add_argument('--rl_weight', type=int, default=4, help='repeat RL proofs this many times in the mix')
    ap.add_argument('--relabel', action='store_true')
    ap.add_argument('--select', default='random', choices=['random', 'longest'], help='which <=max_per_thm proofs of a theorem to train on: random, or longest dependency-pruned length')
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--start_round', type=int, default=1)
    ap.add_argument('--extra_train', default=None, help='Phase 3 precursor injection: jsonl of verified <=6-line generator proofs added to the retained slice every round')
    ap.add_argument('--extra_weight', type=int, default=1, help='repeat each extra_train record this many times per round')
    ap.add_argument('--exclude_pattern', default=None, choices=list(PATTERNS) + ['derived_ore_strict'], help='drift arms: never train on a found proof whose pruned form has this pattern (still recorded in found_<r>.jsonl)')
    ap.add_argument('--resume_found', default=None, help='artifacts dir of a previous run of the same arm; loads found_<start_round-1>.jsonl and found_transfer_<start_round-1>.jsonl')
    a = ap.parse_args()
    out = f'artifacts/{a.name}'
    os.makedirs(out, exist_ok=True)
    os.makedirs('ckpts', exist_ok=True)
    json.dump(vars(a), open(f'{out}/args.json', 'w'), indent=1)
    dev = 'cuda'
    targets, transfer, heldout = read(a.targets), read(a.transfer), read(a.heldout)
    eval_keys = {r['key'] for r in transfer} | {r['key'] for r in heldout} | {r['key'] for r in targets}
    eval_keys |= {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    train_recs = read(a.train)
    extra_recs = read(a.extra_train) if a.extra_train else []
    for x in extra_recs:
        assert x['n_lines'] <= 6, x
    rng = random.Random(a.seed)
    ckpt = a.init
    found = collections.defaultdict(list)     # target name -> list of {proof, written, pruned, round}
    found_t = collections.defaultdict(list)
    relabelled = {}                           # thm -> record
    if a.resume_found:
        r0 = a.start_round - 1
        for l in open(f'{a.resume_found}/found_{r0}.jsonl'):
            x = json.loads(l); found[x['name']].append({'proof': x['proof'], 'written': x['written'], 'pruned': x['pruned'], 'round': x['round']})
        for l in open(f'{a.resume_found}/found_transfer_{r0}.jsonl'):
            x = json.loads(l); found_t[x['name']].append({'proof': x['proof'], 'written': x['written'], 'pruned': x['pruned'], 'round': x['round']})
        print(f'resumed {sum(len(v) for v in found.values())} target proofs, {sum(len(v) for v in found_t.values())} transfer proofs', flush=True)
    for r in range(a.start_round, a.start_round + a.rounds):
        t0 = time.time()
        model, tok, _ = load_ckpt(ckpt, dev)
        seed = a.seed * 1000 + r
        stats = {'round': r, 'ckpt': ckpt, 'k': a.k, 'temperature': a.temperature, 'seed': seed}
        # 1. RL targets
        prompts = [t['prompt'] for t in targets for _ in range(a.k)]
        flat = generate(model, tok, prompts, greedy=False, temperature=a.temperature, batch=a.batch, seed=seed)
        outs = [flat[i * a.k:(i + 1) * a.k] for i in range(len(targets))]
        rows = judge(targets, outs, 'n_lines')
        new_this = 0
        for t, row in zip(targets, rows):
            have = {x['proof'] for x in found[t['name']]}
            for p, wl, pl in zip(row['proofs'], row['written_lens'], row['pruned_lens']):
                if p not in have:
                    found[t['name']].append({'proof': p, 'written': wl, 'pruned': pl, 'round': r}); new_this += 1
        stats['targets_round'] = summarize(rows, 'n_lines', f'[{a.name} r{r}] targets (this round, pass@{a.k})')
        # cumulative view over all attempts so far
        cum_rows = []
        for t in targets:
            fs = found[t['name']]
            cum_rows.append({'n_lines': t['n_lines'], 'solved': bool(fs), 'written_lens': [x['written'] for x in fs],
                             'pruned_lens': [x['pruned'] for x in fs], 'reasons': []})
        stats['targets_cum'] = summarize(cum_rows, 'n_lines', f'[{a.name} r{r}] targets (cumulative {r*a.k} attempts)')
        stats['new_proofs_this_round'] = new_this
        # sample-level acceptance rate
        stats['target_sample_acc'] = sum(x['n_ok'] for x in rows) / sum(x['n_tried'] for x in rows)
        # relabelling by-products
        if a.relabel:
            nrl = 0
            for t, ps in zip(targets, outs):
                for p in ps:
                    rl = relabel(t['prompt'], p)
                    if rl is None:
                        continue
                    newp, thm, nl = rl
                    key = canon_key(thm)
                    if nl < 7 or key in eval_keys or thm in relabelled:
                        continue
                    relabelled[thm] = {'prompt': newp, 'proof': p, 'n_lines': nl, 'thm': thm, 'round': r}
                    nrl += 1
            stats['relabelled_new'] = nrl; stats['relabelled_total'] = len(relabelled)
        # 2. transfer, sampled
        prompts = [t['prompt'] for t in transfer for _ in range(a.k)]
        flat = generate(model, tok, prompts, greedy=False, temperature=a.temperature, batch=a.batch, seed=seed + 500)
        outs_t = [flat[i * a.k:(i + 1) * a.k] for i in range(len(transfer))]
        rows_t = judge(transfer, outs_t, 'n_lines')
        stats['transfer_round'] = summarize(rows_t, 'n_lines', f'[{a.name} r{r}] transfer (this round, pass@{a.k})')
        stats['transfer_sample_acc'] = sum(x['n_ok'] for x in rows_t) / sum(x['n_tried'] for x in rows_t)
        # cumulative transfer (union of attempts so far)
        for t, row in zip(transfer, rows_t):
            have = {x['proof'] for x in found_t[t['name']]}
            for p, wl, pl in zip(row['proofs'], row['written_lens'], row['pruned_lens']):
                if p not in have:
                    found_t[t['name']].append({'proof': p, 'written': wl, 'pruned': pl, 'round': r})
        cum_t = [{'n_lines': t['n_lines'], 'solved': bool(found_t[t['name']]), 'written_lens': [x['written'] for x in found_t[t['name']]],
                  'pruned_lens': [x['pruned'] for x in found_t[t['name']]], 'reasons': []} for t in transfer]
        stats['transfer_cum'] = summarize(cum_t, 'n_lines', f'[{a.name} r{r}] transfer (cumulative {r*a.k} attempts)')
        # 3. greedy
        g = generate(model, tok, [t['prompt'] for t in transfer], greedy=True, batch=a.batch)
        stats['transfer_greedy'] = summarize(judge(transfer, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] transfer greedy')
        g = generate(model, tok, [t['prompt'] for t in heldout], greedy=True, batch=a.batch)
        stats['heldout_greedy'] = summarize(judge(heldout, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] heldout greedy')
        with open(f'{out}/found_{r}.jsonl', 'w') as f:
            for t in targets:
                for x in found[t['name']]:
                    f.write(json.dumps({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'gen_lines': t['n_lines'], **x}) + '\n')
        with open(f'{out}/found_transfer_{r}.jsonl', 'w') as f:
            for t in transfer:
                for x in found_t[t['name']]:
                    f.write(json.dumps({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'gen_lines': t['n_lines'], **x}) + '\n')
        # 4. train
        del model
        torch.cuda.empty_cache()
        if not a.no_train:
            mix = f'{out}/mix_{r}.jsonl'
            n_rl = 0
            n_excl = n_excl_thm = 0
            with open(mix, 'w') as f:
                for t in targets:
                    fs = found[t['name']]
                    rng.shuffle(fs)
                    if a.exclude_pattern:
                        keep = [x for x in fs if not has_pattern(x['proof'], a.exclude_pattern)]
                        n_excl += len(fs) - len(keep)
                        n_excl_thm += len(keep) < len(fs)
                        fs = keep
                    if a.select == 'longest':
                        fs = sorted(fs, key=lambda x: -x['pruned'])
                    for x in fs[:a.max_per_thm]:
                        for _ in range(a.rl_weight):
                            f.write(json.dumps({'prompt': t['prompt'], 'proof': x['proof'], 'n_lines': x['written']}) + '\n'); n_rl += 1
                for x in relabelled.values():
                    for _ in range(a.rl_weight):
                        f.write(json.dumps({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']}) + '\n'); n_rl += 1
                for x in rng.sample(train_recs, min(a.retain, len(train_recs))):
                    f.write(json.dumps({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']}) + '\n')
                for x in extra_recs:
                    for _ in range(a.extra_weight):
                        f.write(json.dumps({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']}) + '\n')
            stats['mix_extra_records'] = len(extra_recs) * a.extra_weight
            stats['mix_rl_records'] = n_rl
            if a.exclude_pattern:
                stats['excluded_pattern'] = a.exclude_pattern
                stats['excluded_pattern_proofs'] = n_excl          # cumulative found proofs dropped from this round's mix
                stats['excluded_pattern_theorems'] = n_excl_thm    # targets with >= 1 dropped proof
                print(f'[{a.name} r{r}] exclude_pattern={a.exclude_pattern}: dropped {n_excl} proofs of {n_excl_thm} theorems from the mix', flush=True)
            if n_rl == 0:
                print('no accepted proofs: skipping training this round', flush=True)
            else:
                new_ckpt = f'ckpts/{a.name}_r{r}.pt'
                cmd = ['python3', 'train.py', '--data', mix, '--init', ckpt, '--steps', str(a.ft_steps), '--lr', str(a.ft_lr),
                       '--min_lr', str(a.ft_lr / 10), '--warmup', '50', '--cap', '0', '--out', new_ckpt, '--seed', str(seed), '--log_every', '200']
                print(' '.join(cmd), flush=True)
                subprocess.run(cmd, check=True)
                ckpt = new_ckpt
        stats['secs'] = time.time() - t0
        json.dump(stats, open(f'{out}/round_{r}.json', 'w'), indent=1)
        print(f'=== round {r} done in {stats["secs"]:.0f}s; new proofs {new_this}; cum targets solved {stats["targets_cum"]["solved"]}', flush=True)


if __name__ == '__main__':
    main()
