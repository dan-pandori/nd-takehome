#!/usr/bin/env python3
"""create-or-elicit Phase 3a: one extra EI-style fine-tune round from a knockout ladder's r16 checkpoint, with or without
a self-found free-sigma proof in the mix.  The mix is built exactly as state_ladder_ei.py builds a round's mix -- up to
--max_per_thm accepted proofs per target (shuffled), --rl_weight copies each, from the ladder's last found file, plus
--retain replay records from the arm's pretraining set -- and the 'seeded' arm adds the given proof(s) with the same
--rl_weight copies.  Then the same fine-tune command as a ladder round.

  python3 coe/coe_seeded_round.py --ladder artifacts/coe/ladder/la_ko_s0 --init ckpts/coe/ladder/la_ko_s0_r16.pt \
      --train data/coe/train_k12ko.jsonl --seed_proofs data/coe/phase3a_seed.jsonl --arm seeded --out ckpts/coe/p3a/ko_s0_seeded.pt
"""
import argparse, collections, glob, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ladder', required=True)
    ap.add_argument('--init', required=True)
    ap.add_argument('--train', required=True)
    ap.add_argument('--seed_proofs', default=None)
    ap.add_argument('--arm', required=True, choices=['seeded', 'control'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=17)
    ap.add_argument('--max_per_thm', type=int, default=4)
    ap.add_argument('--rl_weight', type=int, default=4)
    ap.add_argument('--retain', type=int, default=20000)
    ap.add_argument('--steps', type=int, default=600)
    a = ap.parse_args()
    fs = [f for f in glob.glob(os.path.join(a.ladder, 'found_*.jsonl')) if re.search(r'found_\d+\.jsonl$', f)]
    last = max(fs, key=lambda f: int(re.search(r'found_(\d+)\.jsonl$', f).group(1)))
    found = collections.defaultdict(list)
    for l in open(last):
        x = json.loads(l); found[x['name']].append(x)
    rng = random.Random(a.seed)              # the same RNG for both arms: identical target proofs and replay draw
    mix = []
    for name in sorted(found):
        xs = list(found[name]); rng.shuffle(xs)
        for x in xs[:a.max_per_thm]:
            for _ in range(a.rl_weight):
                mix.append({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['written']})
    train = [json.loads(l) for l in open(a.train)]
    for x in rng.sample(train, min(a.retain, len(train))):
        mix.append({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']})
    n_seed = 0
    if a.arm == 'seeded':
        for l in open(a.seed_proofs):
            x = json.loads(l)
            for _ in range(a.rl_weight):
                mix.append({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['proof'].count(';')}); n_seed += 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    mixf = a.out.replace('.pt', '_mix.jsonl')
    with open(mixf, 'w') as f:
        for x in mix:
            f.write(json.dumps(x) + '\n')
    print(f'{a.arm}: found file {last}; mix {len(mix)} records ({n_seed} seed-proof copies)', flush=True)
    cmd = ['python3', 'state_train.py', '--data', mixf, '--init', a.init, '--steps', str(a.steps), '--lr', '0.0003', '--min_lr', '3e-05',
           '--warmup', '50', '--cap', '0', '--out', a.out, '--seed', str(a.seed * 1000 + 17), '--log_every', '200', '--recs', '128']
    print(' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
