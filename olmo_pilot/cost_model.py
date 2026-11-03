#!/usr/bin/env python3
"""Cost of sampling designs from measured throughput and response lengths.

cost = sum over cells (model, problem) of samples x mean tokens per sample / (tokens per second x 3600) x $ per hour.
Inputs are the Stage-0 measurements (olmo_pilot/stage0_summary.json); designs are dicts of per-model sample counts.
Prints one line per design: samples, generated tokens, GPU-hours, dollars.

Usage: cost_model.py [stage0_summary.json]
"""
import json
import sys


def design_cost(d, mu, tps, rate, n_prob=90):
    """d: {model_class: samples_per_problem} plus 'extension_samples'; mu: tokens/sample per model class."""
    toks = sum(n * n_prob * mu[m] for m, n in d.items() if m in mu)
    toks += d.get("extension_samples", 0) * mu.get("extension", mu["base"])
    h = toks / tps / 3600
    return toks, h, h * rate


def main():
    s = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "olmo_pilot/stage0_summary.json"))
    mu = {"base": s["base_mean_tok"], "final": s["final_mean_tok"],
          "inter": (s["base_mean_tok"] + s["final_mean_tok"]) / 2, "extension": s["base_fail_mean_tok"]}
    tps, rate = s["tok_per_s_job"], s["usd_per_h"]
    designs = {
        "brief (512/512, 6x64, ext 2048 on ~10)": {"base": 512, "final": 512, "inter": 6 * 64, "extension_samples": 10 * 1536},
        "B1 (64/64, 4x16, ext 512 on ~12)": {"base": 64, "final": 64, "inter": 4 * 16, "extension_samples": 12 * 448},
        "B2 (32/32, 3x8, ext 256 on ~12)": {"base": 32, "final": 32, "inter": 3 * 8, "extension_samples": 12 * 224},
        "B3 (32/32, 4x8, ext 512 on ~12)": {"base": 32, "final": 32, "inter": 4 * 8, "extension_samples": 12 * 480},
    }
    for name, d in designs.items():
        t, h, usd = design_cost(d, mu, tps, rate)
        print(f"{name:42s} tokens {t/1e6:7.1f} M  GPU-h {h:6.1f}  ${usd:7.1f}")


if __name__ == "__main__":
    main()
