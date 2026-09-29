# long-pool-2 pilot (VPS, 2026-09-29 16:00–16:40 UTC, before any pod)
- `probe_bound17.jsonl`: `pod/lpool2/probe.py` on `lp_g2_249483` (≥ 17 file), bound 20 / 1,500 s: bound 14/15/16 done at 55/148/372 s, 17 not done at 1,517 s. 2-vCPU VPS, a second job running.
- `pypy_*.jsonl`: `minlen.py --bound 14 --time 200 --procs 1` on 3 `L_true` 13 generator theorems: CPython 59.3 s total, PyPy 3.11.15 71.1 s.
- Funnel of long-pool's 608,216 labelled generator theorems by generated length: `pod/lpool2/funnel.py` over `hf://…/long-pool/data/lp/g{1..4}_ml{10,12,14,16}.jsonl`; table in `funnel.txt`.
- Construction length vs SN-cap12 solves on the ≥ 17 file: state-cap12's `artifacts/sc12/rr/*_SN12_s*__ge17.jsonl` (bucket), table in the pre-registration.
