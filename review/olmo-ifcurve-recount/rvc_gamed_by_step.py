"""Gamed share by checkpoint: my arm-C half-sample and arm-B first min(strict, 4) per cell. Writes out/gamed_by_step.txt."""
import rvc_hand as H
from rvc_core import Tee

T = Tee("gamed_by_step.txt")
L = H.labels()
lab = H.lab_fn(L)
T("gamed share by checkpoint (mine): arm C sub-sample (20 / ckpt, all labelled) | arm-B first min(strict,4) per cell")
for c in H.CKA:
    a = [lab(k) for k in H.ARMC[c]]
    s = f"   {c:6s} armC {a.count('gamed'):2d}/{len(a):2d} = {a.count('gamed') / len(a):.2f}"
    if c in H.CK:
        b = [x for x in (lab(k) for p in H.REACH for k in H.B[c][p][:4]) if x]
        s += f" | armB first-4 {b.count('gamed'):3d}/{len(b):3d}" + (f" = {b.count('gamed') / len(b):.2f}" if b else "")
    T(s)
