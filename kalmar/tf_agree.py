#!/usr/bin/env python3
"""Teacher-forced agreement with Kalmár's construction (run kalmar-pretrain, read-out E1).

  python3 kalmar/tf_agree.py --ckpt ckpts/kalmar/stage1_kalD_s0.pt --in data/kalmar/tf1200_kal_sl.jsonl \
      --out artifacts/kalmar/tf/<model>__tf1200.json [--batch 1024] [--seed 0]

For every record (a theorem with its sl Kalmár proof, `kalmar/make_sets.py`) the proof is cut into the states the
algorithm visits (`state_env.decompose`, canonical names) and every name is shifted by a per-theorem base
b = random.Random(seed * 1000003 + i).randint(0, 32) -- the states the model sees when it follows the algorithm in
the sampler (`state_sample.NAME_BASE_MAX`).  At each state the model writes its **greedy** action (to <eos>, at most
--max_action tokens).  It agrees if that action equals the algorithm's after the names the environment assigns
(the `have` name and a box / Or.elim binder, `Env._assign_names`) are masked: the environment would apply exactly the
algorithm's step.

Output: overall agreement; by step type (kalmar.TAGS), box depth (frames open before the action), position decile,
atom count, and step type x atom count; the first-disagreement position per record; and, for the reviewer, one
agreement string per record ('1' / '0' per state, in order) with its base.
"""
import argparse, collections, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
from model import load_ckpt
from sample import generate_ids_fast
from state_env import Env, decompose, split_actions, is_name, BIGN

NAME_BASE_MAX = 32


def shift(toks, b):
    return [f'n{int(t[1:]) + b}' if is_name(t, BIGN) else t for t in toks]


def masked(act):
    """the action with the environment-assigned names replaced by '<def>' (Env._assign_names' positions)."""
    a = list(act)
    if len(a) < 2 or a[0] != 'have':
        return a
    a[1] = '<def>'
    if ':=' in a:
        i = a.index(':=') + 1
        j = i + 3 if i < len(a) and a[i] == '(' else i + 5 if i < len(a) and a[i] == 'Or.elim' else None
        if j is not None and j < len(a):
            a[j] = '<def>'
    return a


def states_of(prompt, proof):
    """-> list of (state tokens, action tokens, depth) along the algorithm's trajectory (canonical names, base 0)."""
    steps, toks, env = decompose(prompt, proof, canon=True)
    acts = split_actions(toks)
    e = Env(prompt, canon=True)
    depth = []
    for a in acts:
        depth.append(len(e.frames) - 1)
        ok, why = e.apply(a)
        assert ok, why
    return [(s, a, d) for (s, a, h), d in zip(steps, depth)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--max_action', type=int, default=512)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dump_errors', type=int, default=0, help='save up to N disagreeing states per step type '
                    '(state, algorithm action, model action) to <out>.errors.jsonl')
    a = ap.parse_args()
    import record
    record.save_config(vars(a), a.out)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, extra = load_ckpt(a.ckpt, dev)
    model.eval()
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.limit:
        recs = recs[:a.limit]
    items = []          # (record idx, step idx, prompt ids, algorithm action (shifted), tag, depth)
    bases = []
    for i, r in enumerate(recs):
        b = random.Random(a.seed * 1000003 + i).randint(0, NAME_BASE_MAX)
        bases.append(b)
        st = states_of(r['prompt'], r['proof'])
        tags = r.get('kal_tags') or r.get('tags')
        assert tags and len(tags) == len(st), (i, len(st), len(tags or []))
        for j, (s, act, d) in enumerate(st):
            items.append((i, j, tok.encode_toks(shift(s, b)), shift(act, b), tags[j], d))
    t0 = time.time()
    order = sorted(range(len(items)), key=lambda k: len(items[k][2]))
    agree = [None] * len(items)
    model_act = [None] * len(items)
    ntok = 0
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
        for s0 in range(0, len(order), a.batch):
            idx = order[s0:s0 + a.batch]
            outs = generate_ids_fast(model, tok, [items[k][2] for k in idx], goals=None, greedy=True,
                                     max_new=a.max_action, seed=0, early='eos', compact=True)
            for k, o in zip(idx, outs):
                atoks, ended = tok.decode_action(o)
                ntok += len(atoks) + 1
                agree[k] = bool(ended) and masked(atoks) == masked(items[k][3])
                if a.dump_errors and not agree[k]:
                    model_act[k] = (atoks if ended else atoks[:64] + ['…'])
    secs = time.time() - t0
    record.count(gen_tokens=ntok, actions=len(items))
    tot = collections.Counter(); hit = collections.Counter()
    per_rec = collections.defaultdict(list)
    for (i, j, _, _, tag, d), ok in zip(items, agree):
        r = recs[i]
        na = r.get('n_atoms')
        n = len(r.get('kal_tags') or r.get('tags'))
        dec = min(9, int(10 * j / n))
        tg = tag.split(':')[0] if tag.startswith('close:') else tag
        for key in ('all', f'tag={tag}', f'tagg={tg}', f'depth={d}', f'decile={dec}', f'atoms={na}', f'tag={tag}|atoms={na}'):
            tot[key] += 1; hit[key] += ok
        per_rec[i].append('1' if ok else '0')
    first = collections.Counter()
    rec_all = 0
    rows = []
    for i, r in enumerate(recs):
        sres = ''.join(per_rec[i])
        rows.append({'name': r.get('name'), 'base': bases[i], 'agree': sres})
        k = sres.find('0')
        if k < 0:
            rec_all += 1
        else:
            first[min(9, int(10 * k / len(sres)))] += 1
    out = {'ckpt': a.ckpt, 'in': a.inp, 'seed': a.seed, 'batch': a.batch, 'max_action': a.max_action,
           'n_records': len(recs), 'n_states': len(items), 'secs': round(secs, 1),
           'agreement': {k: {'n': tot[k], 'agree': hit[k], 'rate': hit[k] / tot[k]} for k in sorted(tot)},
           'records_all_agree': rec_all, 'first_disagreement_decile': dict(sorted(first.items())),
           'peak_alloc_gb': torch.cuda.max_memory_allocated() / 2 ** 30 if dev == 'cuda' else None,
           'rows': rows}
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'))
    if a.dump_errors:
        seen = collections.Counter()
        with open(a.out.replace('.json', '') + '.errors.jsonl', 'w') as f:
            for k, (i, j, ids, act, tg, d) in enumerate(items):
                if model_act[k] is None or seen[tg] >= a.dump_errors:
                    continue
                seen[tg] += 1
                f.write(json.dumps({'name': recs[i].get('name'), 'step': j, 'tag': tg, 'depth': d,
                                    'state': ' '.join(tok.itos[x] for x in ids), 'algorithm': ' '.join(act),
                                    'model': ' '.join(model_act[k])}) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('agreement', 'rows')}))
    print('overall', out['agreement']['all'])
    for k in sorted(tot):
        if k.startswith('tagg=') or k.startswith('atoms='):
            print(f'  {k:24s} {hit[k]:8d} / {tot[k]:8d} = {hit[k] / tot[k]:.4f}')


if __name__ == '__main__':
    main()
