#!/usr/bin/env python3
"""Cost projection for run olmo-rlzero-if from Stage-0 measurements (tokens x measured $ per million tokens).

Usage: project.py [--usd_per_M 0.634] [--L base=2300,s0100=2000,s0500=1000,main=51,math=3000] [--R 150]
                  [--unres 0.6] [--Gfrac 0.25] [--spent 0.75]
Fixed phase: base 16 x 450, s0100 / s0500 / main 8 x 450, math 8 x 300.
Candidates R (strict); `unres` = share the base does not resolve under strict (each costs 240 base samples; a resolved
one ~48); `Gfrac` = share of R on which main is confirmed by hand (the base extension that decides the hand verdict).
main's confirmation on all of R: up to 248 fresh samples each (worst case). Prints parts and totals under the brief's
cuts (math, then s0500) and the cost of extending the strict-only rest.
"""
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usd_per_M", type=float, default=0.634)
    ap.add_argument("--L", default="base=2300,s0100=2000,s0500=1000,main=51,math=3000")
    ap.add_argument("--R", type=int, default=150)
    ap.add_argument("--unres", type=float, default=0.6)
    ap.add_argument("--Gfrac", type=float, default=0.25)
    ap.add_argument("--spent", type=float, default=0.75)
    a = ap.parse_args()
    L = {k: float(v) for k, v in (x.split("=") for x in a.L.split(","))}
    usd = lambda tok: tok / 1e6 * a.usd_per_M
    ext1 = lambda n: usd(n * ((a.unres) * 240 + (1 - a.unres) * 48) * L["base"])
    parts = {
        "fixed base 16 x 450": usd(16 * 450 * L["base"]),
        "fixed s0100 8 x 450": usd(8 * 450 * L["s0100"]),
        "fixed s0500 8 x 450": usd(8 * 450 * L["s0500"]),
        "fixed main 8 x 450": usd(8 * 450 * L["main"]),
        "fixed math 8 x 300": usd(8 * 300 * L["math"]),
        "main confirmation on all R (worst case 248)": usd(a.R * 248 * L["main"]),
        "base extension on hand-confirmed R (Gfrac)": ext1(a.R * a.Gfrac),
        "base extension on the strict-only rest": ext1(a.R * (1 - a.Gfrac)),
    }
    for k, v in parts.items():
        print(f"{k:48s} ${v:7.2f}")
    full = sum(parts.values()) + a.spent
    print(f"{'Stage 0':48s} ${a.spent:7.2f}\nTOTAL full design                                ${full:7.2f}")
    core = full - parts["fixed math 8 x 300"] - parts["base extension on the strict-only rest"]
    print(f"default (no math; strict-only rest not extended) ${core:7.2f}; per strict-only candidate extended "
          f"${ext1(1):.2f}")


if __name__ == "__main__":
    main()
