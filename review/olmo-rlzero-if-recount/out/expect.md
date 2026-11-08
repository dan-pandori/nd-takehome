| quantity | expected | interval | recount | verdict |
|---|---|---|---|---|
| IFBench base strict pass@1 | 0.07 | 0.03–0.14 | 0.129 | inside |
| IFBench s0100 strict pass@1 | 0.1 | 0.04–0.22 | 0.477 | MISS |
| IFBench s0500 strict pass@1 | 0.25 | 0.1–0.4 | 0.410 | MISS |
| IFBench main strict pass@1 | 0.3 | 0.15–0.45 | 0.469 | MISS |
| IFEval base strict pass@1 | 0.2 | 0.12–0.3 | 0.200 | inside |
| IFEval s0100 strict pass@1 | 0.35 | 0.2–0.55 | 0.806 | MISS |
| IFEval s0500 strict pass@1 | 0.65 | 0.45–0.8 | 0.782 | inside |
| IFEval main strict pass@1 | 0.75 | 0.6–0.88 | 0.817 | inside |
| IFBench base pass@8 | 0.3 | — | 0.334 | (point only) |
| IFBench main pass@8 | 0.6 | 0.4–0.75 | 0.576 | inside |
| IFEval base pass@8 | 0.6 | — | 0.496 | (point only) |
| IFEval main pass@8 | 0.93 | — | 0.860 | (point only) |
| IFBench base mean tokens | 2300 | 1200–4000 | 2510 | inside |
| IFEval base mean tokens | 2100 | — | 2194 | (point only) |
| ifbench s0100 mean tokens | 1500 | 300–3000 | 36 | MISS |
| ifeval s0100 mean tokens | 1500 | 300–3000 | 98 | MISS |
| ifbench s0500 mean tokens | 300 | 60–1500 | 162 | inside |
| ifeval s0500 mean tokens | 300 | 60–1500 | 142 | inside |
| ifbench main mean tokens | 60 | 30–200 | 29 | MISS |
| ifeval main mean tokens | 60 | 30–200 | 49 | inside |
| ifbench base cut at the cap | 2 % | 0.005–0.05 | 0.0304 | inside |
| ifeval base cut at the cap | 2 % | 0.005–0.05 | 0.0271 | inside |
| IFBench candidates R (all 300) | 110 | 60–170 | 109 | inside |
| IFEval candidates R | 45 | 25–70 | 56 | inside |
| IFBench reverse V | 5 | 0–15 | 38 | MISS |
| IFEval reverse V | 3 | 0–10 | 14 | MISS |
| base resolves under strict, of all extended | 40 % | 0.2–0.7 | 0.373 | inside |
| IFBench gamed share of main's first reads | 80 % | 0.6–0.95 | 0.922 | inside |
| IFBench main hand-confirmed share of R | 25 % | 0.1–0.45 | 0.074 | MISS |
| IFBench main open-gaming share of R | 50 % | 0.3–0.75 | 0.204 | MISS |
| IFBench hand-reach prompts | 3 | 0–15 | 5 | inside |
| IFEval gamed share of main's first reads | 80 % | 0.6–0.95 | 0.936 | inside |
| IFEval main hand-confirmed share of R | 25 % | 0.1–0.45 | 0.071 | MISS |
| IFEval main open-gaming share of R | 50 % | 0.3–0.75 | 0.411 | inside |
| IFEval hand-reach prompts | 3 | 0–10 | 1 | inside |
| format check (u) share of base failures | 0.45 | 0.25–0.7 | 0.500 | inside |
| format check (a) share | 0.2 | — | 0.208 | (point only) |
| format check (c) share | 0.15 | — | 0.292 | (point only) |
| format check (d) share | 0.12 | — | 0.000 | (point only) |
| format check (b) share | 0.08 | — | 0.000 | (point only) |
