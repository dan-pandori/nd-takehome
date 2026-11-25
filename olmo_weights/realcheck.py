"""Real-data cross-check (stage 0 and the reviewer): recompute interval statistics for chosen tensors of two
downloaded checkpoints straight from the safetensors bytes with numpy (no torch, no safetensors package), and compare
with the engine's iv.csv. Usage: realcheck.py --a DIR_A --b DIR_B --label-a L --label-b L --stats DIR [--tensors t1,t2]
Prints one line per tensor and REALCHECK PASS / FAIL (sums to 1e-6 relative, counts exactly)."""
import argparse, csv, glob, json, os, struct
import numpy as np


def header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return json.loads(f.read(n)), 8 + n


def tensor_bits(dirpath, name):
    for p in sorted(glob.glob(os.path.join(dirpath, "*.safetensors"))):
        h, off = header(p)
        if name in h:
            d = h[name]
            assert d["dtype"] == "BF16"
            s, e = d["data_offsets"]
            with open(p, "rb") as f:
                f.seek(off + s)
                return np.frombuffer(f.read(e - s), dtype="<u2").astype(np.uint16)
    raise KeyError(name)


def f64(b):
    return (b.astype(np.uint32) << 16).view(np.float32).astype(np.float64)


def ulp(b):
    e = (b.astype(np.int64) >> 7) & 0xFF
    return np.ldexp(1.0, np.maximum(e, 1) - 134)


ap = argparse.ArgumentParser()
for k in ["--a", "--b", "--label-a", "--label-b", "--stats"]:
    ap.add_argument(k, required=True)
ap.add_argument("--tensors", default="model.embed_tokens.weight,model.layers.0.self_attn.q_proj.weight,model.norm.weight")
a = ap.parse_args()
rows = {}
import gzip, io
for p in glob.glob(os.path.join(a.stats, "shard_*", "iv.csv")) + glob.glob(os.path.join(a.stats, "shard_*", "iv.csv.gz")):
    for r in csv.DictReader(io.TextIOWrapper(gzip.open(p, "rb")) if p.endswith(".gz") else open(p)):
        if r["a"] == a.label_a and r["b"] == a.label_b:
            rows[r["tensor"]] = r
ok = True
for t in a.tensors.split(","):
    A, B = tensor_bits(a.a, t), tensor_bits(a.b, t)
    D = f64(B) - f64(A)
    # float64 sums of exact differences, accumulated in 1M-element blocks
    d2 = sum(float((D[i:i + (1 << 20)] ** 2).sum()) for i in range(0, D.size, 1 << 20))
    na2 = sum(float((f64(A[i:i + (1 << 20)]) ** 2).sum()) for i in range(0, A.size, 1 << 20))
    neq, nul = int((A == B).sum()), int((np.abs(D) <= ulp(A)).sum())
    r = rows.get(t)
    if r is None:
        print("MISSING", t)
        ok = False
        continue
    rel = max(abs(float(r["d2"]) - d2) / max(d2, 1e-300), abs(float(r["na2"]) - na2) / na2)
    cnt = int(r["n_eq"]) == neq and int(r["n_ulp"]) == nul
    ok &= rel < 1e-6 and cnt
    print(f"{t}: numel {A.size} rel.err(d2, na2) {rel:.2e}; n_eq {r['n_eq']} vs {neq}; n_ulp {r['n_ulp']} vs {nul}; "
          f"rel change {np.sqrt(d2 / na2):.4e}")
print("REALCHECK", "PASS" if ok else "FAIL")
