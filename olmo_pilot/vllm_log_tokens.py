#!/usr/bin/env python3
"""Integrate vLLM's periodic 'Avg generation throughput' log lines to total generated tokens and time-weighted
throughput (used for jobs stopped before their requests finished). Usage: vllm_log_tokens.py <log>"""
import re
import sys
from datetime import datetime

pat = re.compile(r"INFO (\d\d-\d\d \d\d:\d\d:\d\d).*generation throughput: ([0-9.]+) tokens/s, Running: (\d+) reqs, Waiting: (\d+)")
pts = []
for ln in open(sys.argv[1], errors="ignore"):
    m = pat.search(ln)
    if m:
        pts.append((datetime.strptime("2026-" + m.group(1), "%Y-%m-%d %H:%M:%S"), float(m.group(2)), int(m.group(3))))
tot = 0.0
for (t0, _, _), (t1, r1, _) in zip(pts, pts[1:]):
    tot += r1 * (t1 - t0).total_seconds()
span = (pts[-1][0] - pts[0][0]).total_seconds() if len(pts) > 1 else 0
print(f"intervals {len(pts) - 1}, span {span:.0f} s, generated ~{tot:.0f} tokens, mean {tot / max(span, 1):.0f} tok/s, "
      f"mean resident {sum(p[2] for p in pts) / max(len(pts), 1):.1f}")
