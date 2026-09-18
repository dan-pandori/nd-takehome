#!/usr/bin/env python3
"""round3-run4b diagnostic: what does a base model WRITE on the required@8 depth-3 targets? (not a success count)

  python3 r3_4b_depthdiag.py --ckpt CKPT --out artifacts/r3_4b/diag_<tag>.json [--n 60 --k 64 --temperature 0.8 --seed 0]

Samples k proofs for each of the first n targets of data/r3_1/depth3_req.jsonl and records, per sample: the deepest box the text
opens (max number of '|' before a formula), lines written, whether it ends with QED, and nd_verify's verdict / reason. The question
it answers: does a zero-rate model never open a third box, or open it and fail to close the proof?
"""
import argparse, json, collections, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def written_depth(proof):
    d = 0; n = 0
    for line in proof.split(';'):
        toks = line.split()
        if not toks or toks[0] == 'QED':
            continue
        n += 1
        b = 0
        for t in toks[1:]:
            if t == '|':
                b += 1
            else:
                break
        d = max(d, b)
    return d, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--targets', default='data/r3_1/depth3_req.jsonl')
    ap.add_argument('--n', type=int, default=60); ap.add_argument('--k', type=int, default=64)
    ap.add_argument('--temperature', type=float, default=0.8); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--batch', type=int, default=768)
    a = ap.parse_args()
    import torch
    from model import load_ckpt
    from sample import generate
    from nd_verify import verify_text
    model, tok, _ = load_ckpt(a.ckpt, 'cuda')
    T = [json.loads(l) for l in open(a.targets)][:a.n]
    outs = generate(model, tok, [t['prompt'] for t in T for _ in range(a.k)], greedy=False, temperature=a.temperature, batch=a.batch, seed=a.seed)
    depth = collections.Counter(); lines = collections.Counter(); reasons = collections.Counter(); qed = 0; ok = 0; ok_d3 = 0
    d3_reasons = collections.Counter(); d3_lines = collections.Counter(); examples = []; targets_with_d3_attempt = set()
    for i, p in enumerate(outs):
        t = T[i // a.k]
        d, n = written_depth(p)
        v = verify_text(t['prompt'] + ' ' + p)
        depth[d] += 1; lines[n] += 1; qed += p.strip().endswith('QED'); ok += bool(v[0])
        r = re.sub(r'N?\d+', '#', str(v[1]))[:80] if not v[0] else 'OK'
        reasons[r] += 1
        if d >= 3:
            targets_with_d3_attempt.add(t['name']); d3_reasons[r] += 1; d3_lines[n] += 1; ok_d3 += bool(v[0])
            if len(examples) < 8:
                examples.append({'thm': t['thm'], 'proof': p, 'verdict': str(v[1]) if not v[0] else 'OK'})
    S = {'ckpt': a.ckpt, 'n_targets': len(T), 'k': a.k, 'temperature': a.temperature, 'samples': len(outs), 'verified': ok, 'ends_with_QED': qed,
         'written_max_depth_hist': dict(sorted(depth.items())), 'frac_depth_ge3': sum(v for d, v in depth.items() if d >= 3) / len(outs),
         'targets_with_a_depth3_attempt': len(targets_with_d3_attempt), 'verified_depth_ge3': ok_d3,
         'lines_written_hist': dict(sorted(lines.items())), 'top_reasons': reasons.most_common(8),
         'depth_ge3_reasons': d3_reasons.most_common(8), 'depth_ge3_lines_hist': dict(sorted(d3_lines.items())), 'depth_ge3_examples': examples}
    json.dump(S, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in S.items() if k != 'depth_ge3_examples'}, indent=1))


if __name__ == '__main__':
    main()
