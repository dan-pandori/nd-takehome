#!/usr/bin/env python3
"""Cost projection of the pre-registered design from measured Stage-0 numbers (Part B3).

tokens = fixed (60 problems: dpo 16, each of three RL checkpoints 8; RL length = r x dpo length)
       + extension (R + V candidates x samples per candidate x failing-sample length)
       + challenger confirmation (5 % of the extension); hours = tokens / throughput + overhead; $ = hours x rate.
Usage: project.py <L_dpo> <tok_per_s> <usd_per_h> [--spent 8] [--R 3] [--V 1] [--ext_samples 150] [--ext_len 28000]
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("L", type=float)
ap.add_argument("tps", type=float)
ap.add_argument("rate", type=float)
ap.add_argument("--spent", type=float, default=8.0)
ap.add_argument("--R", type=int, default=3)
ap.add_argument("--V", type=int, default=1)
ap.add_argument("--ext_samples", type=float, default=150)
ap.add_argument("--ext_len", type=float, default=28000)
ap.add_argument("--overhead_h", type=float, default=0.6)
ap.add_argument("--rl_ckpts", type=int, default=3)
a = ap.parse_args()
for r in (0.8, 1.0, 1.3, 1.6):
    fixed = 60 * 16 * a.L + 60 * 8 * a.rl_ckpts * r * a.L
    ext = (a.R + a.V) * a.ext_samples * a.ext_len * 1.05
    h = (fixed + ext) / a.tps / 3600 + a.overhead_h
    print(f"RL/dpo length {r:.1f}: fixed {fixed / 1e6:.1f} M tok, extension {ext / 1e6:.1f} M tok, {h:.1f} pod-h, "
          f"${h * a.rate:.0f} + spent ${a.spent:.0f} = ${h * a.rate + a.spent:.0f}")
