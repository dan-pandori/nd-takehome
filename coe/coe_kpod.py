#!/usr/bin/env python3
"""create-or-elicit: on a ladder pod after the ladder and reads -- the seed's K_train(16) (pre-registration Addendum 1:
sample + fine-tune phase GPU-seconds of rounds 1-16 / (322 x the base's own seconds per attempt on the 322, alone, batch
1,024)), the certificate's attempts per strict held-out member (pooled n >= 59.9 K over the 106), and the standard-A list:
theorems of the 322 that r16 solves (x0) and the base failed in its 512 read attempts (x0 + x1).

  python3 coe/coe_kpod.py --arm ko --seed 0 [--registry artifacts/create-or-elicit/registry] -> prints "K N_SIGMA N_STDA",
  writes artifacts/coe/large/stdA_names_<arm>_s<seed>.txt and artifacts/coe/budget/k_<arm>_s<seed>.json
"""
import argparse, glob, gzip, json, math, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--registry', default='artifacts/create-or-elicit/registry')
    ap.add_argument('--rounds', type=int, default=16)
    a = ap.parse_args()
    N = f'{a.arm}_s{a.seed}'
    name = f'la_{N}'
    sec = {'sample': 0.0, 'finetune': 0.0, 'eval': 0.0}
    for f in glob.glob(os.path.join(a.registry, '*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            lab = r.get('labels') or {}
            if r.get('metric') != 'gpu_seconds' or lab.get('phase') not in sec or lab.get('round') is None:
                continue
            if int(lab['round']) > a.rounds:
                continue
            arm_ok = str(r.get('arm')) == name or (r.get('script') == 'state_train.py' and r.get('arm') == a.arm and int(r.get('seed', -1)) == a.seed)
            if arm_ok:
                sec[lab['phase']] += r['value']
    t = json.load(open(f'artifacts/coe/timing/A40_pend_{N}_b1024.json'))
    c = t['wall_s'] / (t['n'] * t['k'])
    K = (sec['sample'] + sec['finetune']) / (322 * c)
    n_sig = int(math.ceil(59.9 * K / 106))
    # standard A: r16 solves on x0, base fails on x0 and x1 (512 attempts)
    def solved(tag):
        fn = f'artifacts/coe/eval/{tag}.jsonl.gz'
        out = {}
        for l in gzip.open(fn, 'rt'):
            r = json.loads(l); out[r['name']] = bool(r['solved'])
        return out
    first322 = [json.loads(l)['name'] for l in open('data/coe/r322.jsonl')]
    r16 = solved(f'r16_{N}_x0'); p0 = solved(f'pend_{N}_x0'); p1 = solved(f'pend_{N}_x1')
    names = [n for n in first322 if r16.get(n) and not p0.get(n) and not p1.get(n)]
    os.makedirs('artifacts/coe/large', exist_ok=True); os.makedirs('artifacts/coe/budget', exist_ok=True)
    open(f'artifacts/coe/large/stdA_names_{N}.txt', 'w').write('\n'.join(names) + '\n')
    json.dump({'arm': a.arm, 'seed': a.seed, 'phase_seconds': sec, 'c_base_s': c, 'K_train16': K, 'n_sigma_per_member': n_sig,
               'stdA_theorems': len(names), 'timing_file': f'artifacts/coe/timing/A40_pend_{N}_b1024.json'},
              open(f'artifacts/coe/budget/k_{N}.json', 'w'), indent=1)
    print(int(round(K)), n_sig, int(math.ceil(K)))


if __name__ == '__main__':
    main()
