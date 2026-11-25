"""Reviewer self-test for rv_recompute.py: synthetic bf16 safetensors files (own writer) with known equal / 1-ulp /
2-ulp / zero / subnormal / sign changes; rv_recompute.triple() must match a pure-numpy reference that gets the ulp by
incrementing the bf16 bit pattern (a different method from frexp), and the planted counts exactly.
Negative control: altering one element of one checkpoint must change the counts. Prints SELFTEST PASS / FAIL."""
import json, os, struct, sys, tempfile

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_recompute as R


def bf16_bits_from_f32(x):
    """round-to-nearest-even float32 -> bf16 bit patterns (uint16)."""
    u = np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)
    r = ((u >> 16) & 1) + 0x7FFF
    return ((u + r) >> 16).astype(np.uint16)


def val(bits):
    return (bits.astype(np.uint32) << 16).view(np.float32).astype(np.float64)


def ulp_ref(bits):
    """|value(b with magnitude bits + 1) - value(b)| for the magnitude of each bf16 pattern."""
    mag = bits & 0x7FFF
    return val((mag + 1).astype(np.uint16)) - val(mag.astype(np.uint16))


def write(path, tensors):
    hdr, off, blobs = {}, 0, []
    for k in sorted(tensors):
        b = tensors[k][0].astype(np.uint16).tobytes()
        hdr[k] = dict(dtype="BF16", shape=list(tensors[k][1]), data_offsets=[off, off + len(b)])
        off += len(b)
        blobs.append(b)
    h = json.dumps(hdr).encode()
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(h)) + h + b"".join(blobs))


def make(seed):
    rng = np.random.default_rng(seed)
    shapes = {"w.a": (300, 70), "w.b": (1000,), "w.c": (5, 3, 4)}
    base = {k: bf16_bits_from_f32(rng.normal(0, 0.02, int(np.prod(s))).astype(np.float32)) for k, s in shapes.items()}
    base["w.b"][:10] = 0                              # zeros
    base["w.b"][10:20] = np.arange(1, 11)             # positive subnormals
    base["w.b"][20:30] = 0x8000 | np.arange(1, 11)    # negative subnormals
    ck = [dict((k, v.copy()) for k, v in base.items())]
    for step in range(3):
        nxt = {}
        for k, v in ck[-1].items():
            w = v.copy()
            n = w.size
            sel = rng.choice(n, size=n // 2, replace=False)
            kind = rng.integers(0, 4, size=sel.size)   # 0 equal, 1 +1 ulp, 2 -1 ulp-ish (bit -1), 3 big change
            mag = w[sel] & 0x7FFF
            sign = w[sel] & 0x8000
            m1 = np.where(kind == 1, mag + 1, np.where(kind == 2, np.maximum(mag, 1) - 1, mag))
            m1 = np.where(kind == 3, mag + 2 + rng.integers(0, 50, size=sel.size), m1)
            w[sel] = (sign | (m1 & 0x7FFF)).astype(np.uint16)
            nxt[k] = w
        ck.append(nxt)
    return shapes, ck


def ref_triple(shapes, x2, xa, xb, xs):
    out = {}
    for k in sorted(shapes):
        v2, va, vb, vs = val(x2[k]), val(xa[k]), val(xb[k]), val(xs[k])
        d1, d2 = va - v2, vb - va
        out[k] = dict(d2_1=(d1 * d1).sum(), d2_2=(d2 * d2).sum(), na2_1=(v2 * v2).sum(), nb2_2=(vb * vb).sum(),
                      lag1=(d1 * d2).sum(), o2_b=((vb - vs) ** 2).sum(), dp_b=(d2 * (va - vs)).sum(),
                      eq_2=int((xa[k] == xb[k]).sum()), ulp_2=int((np.abs(d2) <= ulp_ref(xa[k])).sum()),
                      eq_1=int((x2[k] == xa[k]).sum()), ulp_1=int((np.abs(d1) <= ulp_ref(x2[k])).sum()),
                      ulps_b=int((np.abs(vb - vs) <= ulp_ref(xs[k])).sum()), eqs_b=int((xb[k] == xs[k]).sum()))
    return out


def run(dirn, shapes, ck, dev):
    labs = ["s", "a2", "a", "b"]
    idx = {}
    for lab, c in zip(labs, ck):
        p = os.path.join(dirn, f"{lab}.safetensors")
        write(p, {k: (c[k], shapes[k]) for k in shapes})
        idx[lab] = R.index_ckpt([p])
    rows = R.triple(dict(a2="a2", a="a", b="b", s="s"), idx, dev)
    return {r["tensor"]: r for r in rows}


def main():
    dev = torch.device(sys.argv[1] if len(sys.argv) > 1 else ("cuda" if torch.cuda.is_available() else "cpu"))
    ok = True
    with tempfile.TemporaryDirectory() as d:
        shapes, ck = make(1)
        # ck[0] = s, ck[1] = a2, ck[2] = a, ck[3] = b
        got = run(d, shapes, ck, dev)
        ref = ref_triple(shapes, ck[1], ck[2], ck[3], ck[0])
        for k in shapes:
            for f, v in ref[k].items():
                g = got[k][f]
                good = (g == v) if isinstance(v, int) else abs(g - v) <= 1e-12 * max(1.0, abs(v))
                if not good:
                    ok = False
                    print("MISMATCH", k, f, g, v)
        # planted structure: about 1/2 untouched + 1/8 equal-kind -> n_eq near 5/8; ulp-kind adds about 2/8
        tot = sum(int(np.prod(s)) for s in shapes.values())
        eq = sum(got[k]["eq_2"] for k in shapes) / tot
        ul = sum(got[k]["ulp_2"] for k in shapes) / tot
        print(f"planted: eq fraction {eq:.3f} (expect ~0.625), ulp fraction {ul:.3f} (expect ~0.875)")
        ok &= 0.58 < eq < 0.67 and 0.83 < ul < 0.92
        # negative control: alter one element of b
        ck2 = [dict((k, v.copy()) for k, v in c.items()) for c in ck]
        ck2[3]["w.a"][7] = (ck2[3]["w.a"][7] & 0x7FFF) + 0x0300
        got2 = run(d, shapes, ck2, dev)
        changed = (got2["w.a"]["d2_2"] != got["w.a"]["d2_2"])
        print("negative control changes d2:", changed)
        ok &= changed
    print("SELFTEST PASS" if ok else "SELFTEST FAIL", dev)


if __name__ == "__main__":
    main()
