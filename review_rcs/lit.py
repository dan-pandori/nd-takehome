#!/usr/bin/env python3
"""Reviewer's own literature table (Q2/Q4): RL / pretraining FLOP ratio per run, from the reviewer's extraction ledgers
R1-R3 (+Y for Yue's checkpoints, flops.py). Same formula as flops.py (pre-registration's). Ranges carry every
stated ambiguity (steps, batch units, mean length). 'gpuh_bound' = ratio upper bound from reported RL GPU-hours at 100 %
of dense bf16 peak (A100/A800 312, H100/H800 989, GB200 2,500 TFLOP/s); 'gpuh_ratio' = RL GPU-h / pretraining GPU-h
where both are reported (same GPU class). Verdict is the paper's own (R ledgers), 'n' = none stated."""
import json, statistics as st
from flops import ratio, ROWS as YUE

PEAK = {'A100': 312e12, 'A800': 312e12, 'H100': 989e12, 'H800': 989e12, 'H200': 989e12, 'GB200': 2.5e15}
L = []
def run(name, paper, verdict, kmax, D, S, p, r, g=(1, 1), E=1, ref=0, old=(0, 1), critic=0, gpuh=None, gpu=None, N=None,
        note='', refs='', create_test=False, multi=None):
    """S = (lo, hi) sequences trained; multi = list of (S, p, r) segments summed (for staged runs)"""
    if multi:
        lo = sum(ratio(s, pp, rr, D, g=g, E=E, ref=ref, old=old, critic=critic)[0] for s, pp, rr in multi)
        hi = sum(ratio(s, pp, rr, D, g=g, E=E, ref=ref, old=old, critic=critic)[1] for s, pp, rr in multi)
    elif S is None:
        lo = hi = None
    else:
        lo, hi = ratio(S, p, r, D, g=g, E=E, ref=ref, old=old, critic=critic)[:2]
    b = gpuh * 3600 * PEAK[gpu] / (6 * N * D) if (gpuh and gpu and N and D) else None
    L.append(dict(name=name, paper=paper, verdict=verdict, kmax=kmax, lo=lo, hi=hi, gpuh_bound=b, note=note, refs=refs))

Q25, Q25M, L31, Q3, V3 = 18e12, 19e12, 15e12, 36e12, 14.8e12
# ---------- frontier-scale open runs (R1) ----------
# DeepSeek-R1-Zero: 10,400 grad steps x 512 responses (R1-17..23); max 32K -> 64K after 8.2k (R1-24); mean: Fig. 1(b) axis to 20K
run('DeepSeek-R1-Zero', '2501.12948 / Nature', 'n (framing only; pass@1, cons@16)', None, V3, None, None, None,
    multi=[((8200*512, 8200*512), (100, 500), (8192, 32768)), ((2200*512, 2200*512), (100, 500), (16384, 65536))],
    ref=1, old=(1, 1), gpuh=101e3, gpu='H800', N=37e9, refs='R1-17..32', note='GPU-h ratio vs V3 pre-training 101K/2,664K = 0.038')
run('DeepSeek-R1-Zero (mean length 5K-15K)', '2501.12948', 'n', None, V3, (10400*512, 10400*512), (100, 500), (5000, 15000), ref=1, old=(1, 1),
    refs='R1-25', note='length range is my reading of the Fig. 1(b) curve, not a stated value')
# MiniMax-M1: 512 H800 x 3 weeks (R1-103/104); D = 8.2-11.4T Text-01 + 7.5T CPT (R1-112..117, 78-83); batch/G n.r.
for D_ in (15.7e12, 18.9e12):
    run(f'MiniMax-M1 (D={D_/1e12:.1f}T)', '2506.13585', 'n', None, D_, None, None, None, gpuh=258e3, gpu='H800', N=45.9e9, refs='R1-78..117',
        note='config-based ratio not computable (batch, G, steps n.r.)')
# Qwen3-8B RL vs distillation: 17,920 GPU-h (type n.r.; H100-class assumed), D 36T (R1-178..182)
run('Qwen3-8B RL stage', '2505.09388', 'elicit (pass@64 unchanged)', 64, Q3, None, None, None, gpuh=17920, gpu='H100', N=8.2e9, refs='R1-178..182')
# ScaleRL 8B dense (base unnamed; Llama-3.1-8B-like D 15T assumed) 100k GB200-h, 7,400 steps; batch 768 completions or 2,048 prompts x 16
run('ScaleRL-8B (768 completions/step)', '2510.13786', 'n (asymptote = mean@16 pass rate)', None, L31, (7400*768, 7400*768), (100, 2048), (3584, 14336),
    old=(0, 1), gpuh=100e3, gpu='GB200', N=8e9, refs='R1-184..217', note='D assumed 15T (base not named)')
run('ScaleRL-8B (2,048 prompts x 16/step)', '2510.13786', 'n', None, L31, (7400*2048*16, 7400*2048*16), (100, 2048), (3584, 14336),
    old=(0, 1), gpuh=100e3, gpu='GB200', N=8e9, refs='R1-202,203', note='batch unit ambiguous in source')
run('ScaleRL-Scout (17B active, 40T)', '2510.13786', 'n', None, 40e12, (7100*768, 7100*768), (100, 2048), (3584, 14336), old=(0, 1),
    gpuh=50e3, gpu='GB200', N=17e9, refs='R1-185..200', note='GPU-h ratio 50k GB200-h / 5.0M H100-h = 0.010 raw')
# Olmo 3 RL-Zero 7B: 2,000 steps x 32 x 8, 16K, no KL; D = 5.93T + 0.1T + 0.05T (R1-228..259)
run('Olmo-3-7B RL-Zero', '2512.13961', 'create (pass@32)', 32, 6.08e12, (2000*256, 3000*256), (100, 2048), (4096, 16384), old=(0, 1), refs='R1-228..259',
    note='midtraining has distilled reasoning traces (contaminated)')
# Olmo 3 / 3.1 Think 32B RL: 750 / 2,300 steps x 128 x 8, 32K, no KL (R1-264..282); D = 5.5T + 0.2T; GPU-h 26.9K / 139.8K H100-h vs ~977K pre-training
run('Olmo-3 Think 32B RL (750 steps)', '2512.13961', 'n', None, 5.7e12, (750*1024, 750*1024), (100, 2048), (8192, 32768), old=(0, 1),
    gpuh=26.9e3, gpu='H100', N=32e9, refs='R1-264..282', note='GPU-h ratio 26.9K/977K = 0.028 (both interp from days x GPUs)')
run('Olmo-3.1 Think 32B RL (2,300 steps)', '2512.13961', 'n', None, 5.7e12, (2300*1024, 2300*1024), (100, 2048), (8192, 32768), old=(0, 1),
    gpuh=139.8e3, gpu='H100', N=32e9, refs='R1-269,276,280', note='GPU-h ratio 139.8K/977K = 0.143')
# MiMo-V2.6-Pro: ~30 steps (figure) x 2.7-3.7B training tokens per step; D 30T (R1-339..356)
run('MiMo-V2.6-Pro', '2610.11959', 'n', None, 30e12, (30, 30), (0, 0), (2.7e9, 3.7e9), old=(0, 1), refs='R1-339..356',
    note='S x (p+r) given directly as tokens/step; steps read from figure')
# ---------- open recipes (R2) ----------
run('ORZ-32B', '2503.24290', 'n', None, Q25, (1200*8192, 1300*8192), (100, 2048), (2000, 8000), critic=1, refs='R2-41..68')
run('Skywork-OR1-32B', '2505.22312', 'n', None, Q25, None, None, None, refs='R2-79..106',
    multi=[((760*4096, 760*4096), (100, 2048), (4096, 16384)), ((240*5120, 370*5120), (100, 2048), (6144, 24576))])
run('Polaris-4B', 'blog', 'n', None, Q3, (500*1024, 1000*1024), (100, 1024), (10000, 52224), gpuh=7680, gpu='H800', N=4.0e9, refs='R2-120..149',
    note='steps inferred (10 d / ~0.33 h); base Qwen3-4B is post-trained')
run('JustRL-DeepSeek-1.5B', '2512.16649', 'n', None, Q25M, (4380*2048, 4380*2048), (100, 1000), (4000, 5500), old=(1, 1),
    gpuh=11500, gpu='A800', N=1.78e9, refs='R2-182..202')
run('1-shot RLVR (Qwen2.5-Math-1.5B)', '2504.20571', 'elicit (k<=8)', 8, Q25M, (2000*1024, 2000*1024), (100, 1024), (768, 3072), ref=1, old=(1, 1), refs='R2-215..235')
run('Spurious rewards (Qwen2.5-Math-7B)', '2506.10947', 'elicit (model-dependent; pass@1)', 8, Q25M, (300*1024, 300*1024), (100, 500), (750, 3500),
    old=(1, 1), gpuh=192, gpu='A100', N=7.6e9, refs='R2-245..263')
run('INTELLECT-2 (QwQ-32B)', '2505.07291', 'n', None, Q25, (350*4096, 350*4096), (100, 1000), (2000, 32768), g=(1, 2), ref=1, old=(1, 1),
    refs='R2-266..294', note='base QwQ-32B already RL-trained')
run('Phi-4-reasoning-plus RL', '2504.21318', 'n', None, 10.25e12, (90*512, 90*512), (100, 1000), (7750, 31000), ref=1, old=(0, 1), refs='R2-306..326')
run('LN-Ultra reasoning RL', '2505.00949', 'create (vs teacher, pass@1)', 1, 15.6e12, None, None, None, gpuh=140e3, gpu='H100', N=253e9, refs='R2-333..355',
    note='N = 253B derivative of Llama-3.1-405B; D = 405B parent tokens')
run('AceReason-Nemotron-14B (indicative)', '2505.16400', 'both (pass@k to 64 / 1,024 LCB)', 1024, Q25, (1000*1024, 3500*2048), (100, 1000), (4000, 8000),
    refs='R2-153..179', note='steps/G for 14B n.r.; 7B curves used')
# ---------- create-vs-elicit threads (R3) ----------
run('ProRL-v1 (1.5B)', '2505.24864', 'create (task-dependent; math diminishes)', 128, Q25M, (2000*4096, 2500*4096), (100, 500), (3000, 7000), g=(1, 2), ref=1, old=(1, 1),
    gpuh=16e3, gpu='H100', N=1.78e9, refs='R3-1..36', note='mean length read from Fig. 2 axis (3-7K)')
run('ProRL-v2 (cumulative 3,000 steps)', 'NVIDIA blog', 'create (Invisible Leash: net shrinkage 48 gained / 175 lost)', 8192, Q25M, None, None, None,
    g=(1, 2), ref=1, old=(1, 1), refs='R3-40..63',
    multi=[((2000*4096, 2500*4096), (100, 500), (3000, 7000)), ((1000*8192, 1000*8192), (100, 500), (2000, 8192))])
run('BroRL (ProRLv2 + 191-419 steps x 128 x 512)', '2510.01180', 'n (pass@1 only)', 1, Q25M, None, None, None, g=(1.6, 2.4), ref=1, old=(1, 1),
    refs='R3-76..104', multi=[((2000*4096, 2500*4096), (100, 500), (3000, 7000)), ((1000*8192, 1000*8192), (100, 500), (2000, 8192)),
                              ((191*65536, 419*65536), (100, 500), (4096, 16384))])
run('Negative-sample RL (Qwen2.5-Math-7B)', '2506.01347', 'n (refines prior; k<=256)', 256, Q25M, (120*8192, 120*8192), (100, 500), (1024, 4096), ref=1, old=(1, 1), refs='R3-132..160')
run('f(g(x)) composition (Llama-3.1-8B-Instruct)', '2509.25123', 'create (k~1,024 vs RFT base)', 1024, L31, (600*256, 600*256), (100, 500), (2048, 8192), refs='R3-162..187')
run('Interplay (100M from scratch, 10B tokens)', '2512.07783', 'both (create at edge of competence)', 128, 10e9, (50*6144, 954*6144), (50, 200), (256, 1024), refs='R3-189..217',
    note='own FLOP-equivalents: 1.05B-20B tokens vs 10B pre-training -> 0.1-2')
run('Two-stage debate (Qwen2.5-Math-7B)', '2510.04028', 'both', 256, Q25M, (42*8192, 42*8192), (100, 500), (1024, 4096), refs='R3-219..243')
run('Diversity collapse (Qwen2.5-Math-7B)', '2606.15455', 'both', 256, Q25M, (140*8192, 140*8192), (100, 500), (768, 3072), refs='R3-287..296')

if __name__ == '__main__':
    yue = [dict(name='Yue: ' + d['name'], paper='2504.13837 (evaluated)', verdict='elicit', kmax=1024, lo=d['prereg'][0], hi=d['prereg'][1],
                gpuh_bound=None, note='', refs='Y') for d in YUE]
    allrows = yue + L
    json.dump(allrows, open('out/lit_rows.json', 'w'), indent=1)
    f = lambda x: f'{x:.1e}' if x is not None else '   n.c. '
    for r in L:
        print(f"{r['name'][:46]:46s} {f(r['lo'])} – {f(r['hi'])}  gpuh<= {f(r['gpuh_bound'])}  | {r['verdict'][:40]}")
    vals = [r for r in allrows if r['hi'] is not None]
    print('\nrows with a config ratio:', len(vals), ' min lo', f(min(r['lo'] for r in vals)), ' max hi', f(max(r['hi'] for r in vals)))
    print('max low bound among non-Interplay open runs:', max((r['lo'], r['name']) for r in L if r['lo'] is not None and 'Interplay' not in r['name']))
