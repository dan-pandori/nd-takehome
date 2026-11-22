"""Generated tokens per draw by checkpoint (arm A cells and arm-B base cells, every source incl. reused stored draws):
the run compares checkpoints at equal draws, so this is the per-checkpoint compute ratio to flag (> 1.25x step 0 /
the earliest checkpoint). Writes out/compute_ckpt.txt."""
import numpy as np

from rvc_cells import CK, CKA, build
from rvc_core import Tee

T = Tee("compute_ckpt.txt")
rows, armA, reach, A, B, XC, J = build()
base = None
T("ckpt | arm A: draws, tokens, tokens/draw, x dpo | arm B base: draws, tokens, tokens/draw, x s0050")
b0 = None
for c in CKA:
    ka = [tuple(k) for p in armA for k in A[c][p]]
    ta = sum(rows[k]["n_ids"] for k in ka)
    base = base or ta / len(ka)
    s = f"   {c:6s} | {len(ka):5d} {ta:11,d} {ta / len(ka):7.0f} {ta / len(ka) / base:5.2f}"
    if c in B:
        kb = [tuple(k) for p in reach for k in B[c][p]]
        tb = sum(rows[k]["n_ids"] for k in kb)
        b0 = b0 or tb / len(kb)
        s += f" | {len(kb):5d} {tb:11,d} {tb / len(kb):7.0f} {tb / len(kb) / b0:5.2f}"
    T(s)
