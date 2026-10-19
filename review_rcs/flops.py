#!/usr/bin/env python3
"""Reviewer's own RL / pretraining compute ratios (review of rl-compute-share; written before reading the
executor's table). Formulae are the pre-registration's (preregistration/rl-compute-share.md §Design):
  pretraining = 6·N·D;  RL = 2·N·(prompt+generated) per rollout token  + 6·N per trained token
                         + 2·N per token for each extra reference / old-policy forward pass  (+ critic 2·N_c + 6·N_c).
When policy and pretrained model are the same network, N cancels:
  ratio = (2·g + 6·E + 2·ref + 2·old + 8·critic) · S · (p + r) / (6·D)
with S = sequences trained (steps × prompts/step × group), g = generated / trained sequences (dynamic sampling),
E = passes over each trained sequence, p = prompt tokens, r = mean response tokens.
Two length conventions:  'prereg' = r from ¼·max to max unless the mean is stated in text;
                         'best'   = r read from the source's own length figure where there is one (else = prereg).
Low bound: low S, p, r, g and old = 0;  high bound: high S, p, r, g and old = 1 (if the framework recomputes it).
Also: an upper bound from reported GPU-hours at 100 % of dense bf16 peak (A100 312, H100/H800 989 TFLOP/s)."""
import json, math

PEAK = {'A100': 312e12, 'H100': 989e12, 'H800': 989e12, 'H200': 989e12, 'H20': 148e12}

def ratio(S, p, r, D, g=(1, 1), E=1, ref=0, old=(0, 1), critic=0):
    lo = (2*g[0] + 6*E + 2*ref + 2*old[0] + 8*critic) * S[0] * (p[0] + r[0]) / (6 * D)
    hi = (2*g[1] + 6*E + 2*ref + 2*old[1] + 8*critic) * S[1] * (p[1] + r[1]) / (6 * D)
    tok_lo = g[0] * S[0] * (p[0] + r[0]) / D           # generated-sequence tokens / pretraining tokens
    tok_hi = g[1] * S[1] * (p[1] + r[1]) / D
    return lo, hi, tok_lo, tok_hi

def gpuh_bound(gpu_h, gpu, N, D):
    return gpu_h * 3600 * PEAK[gpu] / (6 * N * D)

Q25 = 18e12           # Qwen2.5 pretraining tokens (Y-51)
ROWS = []
def row(name, base, D, steps, B, G, p, r_prereg, r_best=None, **kw):
    S = (steps[0] * B * G, steps[1] * B * G)
    d = dict(name=name, base=base, D=D, steps=steps, B=B, G=G, p=p, r_prereg=r_prereg, r_best=r_best or r_prereg, kw=kw)
    d['prereg'] = ratio(S, p, r_prereg, D, **kw)
    d['best'] = ratio(S, p, r_best or r_prereg, D, **kw)
    ROWS.append(d)

# ---- Yue et al. 2504.13837v5: every RL-trained checkpoint it evaluates ----
# SimpleRL-Zoo (Y-15..20): 1,024 prompts × 8, max 8,192, 4 mini-batches/step (old-policy pass), KL loss (ref pass)
row('SimpleRL-Zoo Qwen2.5-7B',  'Qwen2.5-7B',  Q25, (100, 100), 1024, 8, (100, 300), (2048, 8192), (500, 1200), ref=1, old=(1, 1))
row('SimpleRL-Zoo Qwen2.5-14B', 'Qwen2.5-14B', Q25, (100, 100), 1024, 8, (100, 300), (2048, 8192), (500, 1200), ref=1, old=(1, 1))
row('SimpleRL-Zoo Qwen2.5-32B', 'Qwen2.5-32B', Q25, (100, 160), 1024, 8, (100, 300), (2048, 8192), (500, 1000), ref=1, old=(1, 1))
row('SimpleRL-Zoo Llama-3.1-8B', 'Llama-3.1-8B', 15e12, (80, 100), 1024, 8, (100, 300), (2048, 8192), (500, 2000), ref=1, old=(1, 1))
# Oat-Zero-7B (Y-22..26): steps not reported -> indicative 200-500 steps; binding bound is GPU-hours
row('Oat-Zero-7B (steps assumed 200-500)', 'Qwen2.5-Math-7B', Q25 + 1e12, (200, 500), 128, 8, (100, 300), (750, 3000), (400, 1000), old=(1, 1))
# DAPO-32B (Y-27..34): 5,000-10,000 gradient updates / 16 per rollout step = 313-625 rollout steps; g = 1..3 (recipe 3x gen batch)
row('DAPO-32B', 'Qwen2.5-32B', Q25, (313, 625), 512, 16, (100, 300), (5120, 20480), (1500, 5000), g=(1, 3), old=(1, 1))
# CodeR1-Zero-Qwen2.5-7B-12k-832 (Y-35..39): 832 steps × 16 prompts × 16; max resp 4,096, max prompt 2,048; KL
row('CodeR1-Zero-7B', 'Qwen2.5-7B-Instruct-1M', Q25, (832, 832), 16, 16, (200, 2048), (1024, 4096), ref=1, old=(1, 1))
# DeepCoder-14B (Y-40..46): ~605-1,260 steps × 128 × 8; mean length 8K->17.5K (stated); no KL
row('DeepCoder-14B', 'DeepSeek-R1-Distill-Qwen-14B', Q25, (605, 1260), 128, 8, (200, 2048), (8000, 17500), old=(1, 1))
# EasyR1 Qwen2.5-VL-7B on Geometry3K (Y-47..51): 15 episodes × 4-5 steps × 512 × 5; KL; D = 18T + 4.1T
row('EasyR1 Qwen2.5-VL-7B (Yue)', 'Qwen2.5-VL-7B-Instruct', Q25 + 4.1e12, (60, 75), 512, 5, (300, 2048), (512, 2048), ref=1, old=(1, 1))
# Qwen2.5-Math-7B-Instruct (Y-63..64): 66K queries x 32 responses, one pass assumed (episodes not stated); max length not stated -> 1,024-4,096; KL
row('Qwen2.5-Math-7B-Instruct (1 epoch assumed)', 'Qwen2.5-Math-7B', Q25 + 1e12, (1, 1), 66000, 32, (100, 300), (1024, 4096), ref=1, old=(1, 1))
# Yue's own VeRL runs on Qwen2.5-7B (Y-6..12): 256 prompts × 8, max 8,192, no KL, 1 update per step
for st in (150, 300, 450):
    row(f'Yue GRPO step {st}', 'Qwen2.5-7B', Q25, (st, st), 256, 8, (100, 300), (2048, 8192))
row('Yue PPO step 150 (critic)', 'Qwen2.5-7B', Q25, (150, 150), 256, 8, (100, 300), (2048, 8192), critic=1)
for a in ('RLOO', 'Reinforce++'):
    row(f'Yue {a} step 150', 'Qwen2.5-7B', Q25, (150, 150), 256, 8, (100, 300), (2048, 8192))
row('Yue ReMax step 150 (+1 greedy rollout)', 'Qwen2.5-7B', Q25, (150, 150), 256, 8, (100, 300), (2048, 8192), g=(1.125, 1.125))
row('Yue DAPO step 150 (3-6x sampling)', 'Qwen2.5-7B', Q25, (150, 150), 256, 8, (100, 300), (2048, 8192), g=(3, 6))
row('Yue GRPO n=32, 220 steps', 'Qwen2.5-7B', Q25, (220, 220), 256, 32, (100, 300), (2048, 8192))

GPUH = [  # (name, gpu_h, gpu, N, D) -- upper bounds at 100 % peak
    ('SimpleRL-Zoo Qwen2.5-7B', 240, 'H100', 7.6e9, Q25),
    ('SimpleRL-Zoo Qwen2.5-14B', 240, 'H100', 14.7e9, Q25),
    ('SimpleRL-Zoo Qwen2.5-32B', 2304, 'H100', 32.5e9, Q25),
    ('Oat-Zero-7B', 216, 'A100', 7.6e9, Q25 + 1e12),
    ('DeepCoder-14B', 13440, 'H100', 14.8e9, Q25),
]

if __name__ == '__main__':
    out = []
    print(f"{'run':42s} {'prereg lo':>9s} {'prereg hi':>9s} {'best lo':>9s} {'best hi':>9s}  tok-ratio(best)")
    for d in ROWS:
        a, b = d['prereg'], d['best']
        print(f"{d['name']:42s} {a[0]:9.2e} {a[1]:9.2e} {b[0]:9.2e} {b[1]:9.2e}  {b[2]:.1e}-{b[3]:.1e}")
        out.append(dict(name=d['name'], base=d['base'], prereg_lo=a[0], prereg_hi=a[1], best_lo=b[0], best_hi=b[1],
                        tok_lo=b[2], tok_hi=b[3]))
    print('\nGPU-hour upper bounds (100 % of dense bf16 peak):')
    for n, h, g, N, D in GPUH:
        print(f'  {n:30s} {h:>7} {g}-h  ratio <= {gpuh_bound(h, g, N, D):.1e}')
    import statistics as st
    his = sorted(d['prereg'][1] for d in ROWS)
    print('\nmedian prereg-high over', len(his), 'Yue checkpoints:', f'{st.median(his):.2e}')
    print('median best-high:', f"{st.median(sorted(d['best'][1] for d in ROWS)):.2e}")
    print('median prereg-low:', f"{st.median(sorted(d['prereg'][0] for d in ROWS)):.2e}")
    json.dump(out, open('out/yue_rows.json', 'w'), indent=1)
