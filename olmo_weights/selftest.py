"""Self-test of engine.py on synthetic bf16 checkpoints against an independent numpy implementation.

Positive control: every statistic of a synthetic job (two chains, a pair, a Gram set, LoRA dots) matches numpy
computed from the raw bf16 bits (sums to 1e-6 relative, counts exactly). The synthetic values include unchanged
weights, exact 1-ulp steps, half-ulp steps at powers of two, zeros, subnormals and sign changes.
Negative controls: (1) the engine run on a copy with one tensor altered must disagree with numpy on the original
files (so the comparison can fail); (2) a wrong sha256 in the manifest must stop the engine.
Usage: python olmo_weights/selftest.py [--device cpu|cuda] [--dir /tmp/ow_selftest]   (prints SELFTEST PASS / FAIL)
"""
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, zlib
import numpy as np

SHAPES = {0: {"model.embed_tokens.weight": (50, 16), "model.norm.weight": (16,)},
          1: {"model.layers.0.self_attn.q_proj.weight": (16, 16), "model.layers.0.self_attn.q_norm.weight": (16,)},
          2: {"model.layers.0.mlp.down_proj.weight": (16, 40), "lm_head.weight": (50, 16)}}
FILES = [f"model-0000{k + 1}-of-00003.safetensors" for k in range(3)]
LABELS = [f"T/c{i}" for i in range(6)]


def bf16_bits(x):
    """float64 array -> bf16 bits (round to nearest even), uint16."""
    u = np.asarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)
    r = ((u >> 16) & 1) + 0x7FFF
    return ((u + r) >> 16).astype(np.uint16)


def bits_to_f64(b):
    return (b.astype(np.uint32) << 16).view(np.float32).astype(np.float64)


def ulp_np(b):
    e = (b.astype(np.int64) >> 7) & 0xFF
    return np.ldexp(1.0, np.maximum(e, 1) - 134)


def write_st(path, tensors):
    """Minimal safetensors writer (bf16 only), independent of the safetensors package."""
    hdr, off, blobs = {}, 0, []
    for name, b in tensors.items():
        raw = b.astype("<u2").tobytes()
        hdr[name] = {"dtype": "BF16", "shape": list(b.shape), "data_offsets": [off, off + len(raw)]}
        off += len(raw)
        blobs.append(raw)
    h = json.dumps(hdr).encode()
    h += b" " * ((8 - len(h) % 8) % 8)
    with open(path, "wb") as f:
        f.write(len(h).to_bytes(8, "little") + h + b"".join(blobs))


def make_ckpts(rng):
    C = []
    base = {}
    for k, d in SHAPES.items():
        for n, sh in d.items():
            x = rng.normal(0, 0.02, sh)
            if n.endswith("norm.weight"):
                x = 1.0 + rng.normal(0, 0.05, sh)
            x.flat[0] = 0.0
            x.flat[1] = 2.0 ** -130          # subnormal in bf16
            x.flat[2] = 0.015625               # power of two
            x.flat[3] = -0.0078125
            base[n] = bf16_bits(x)
    C.append(base)
    for i in range(1, 6):
        prev, cur = C[-1], {}
        for n, b in prev.items():
            b = b.copy()
            m = rng.random(b.shape)
            step = np.where(m < 0.4, 0, np.where(m < 0.6, 1, np.where(m < 0.7, -1, 0)))
            nb = (b.astype(np.int32) + step).astype(np.uint16)          # exact +-1 ulp (same sign) or unchanged
            big = m >= 0.7
            vals = bits_to_f64(b) + rng.normal(0, 0.003, b.shape)
            nb = np.where(big, bf16_bits(vals), nb)
            if i == 3:
                nb.flat[2] = bf16_bits(0.015625 - 2.0 ** -14)   # half-ulp step just below a power of two
                nb.flat[1] = bf16_bits(-(2.0 ** -130))           # sign change of a subnormal
            cur[n] = nb.astype(np.uint16)
        C.append(cur)
    return C


def build(d, C, rng, alter=None):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    rows = []
    for li, lab in enumerate(LABELS):
        ld = os.path.join(d, "local", lab.replace("/", "_"))
        os.makedirs(ld)
        shas, sizes = [], []
        for k, fn in enumerate(FILES):
            t = {n: C[li][n] for n in SHAPES[k]}
            if alter and alter[0] == li and alter[1] in t:
                t = dict(t)
                b = t[alter[1]].copy()
                b.flat[5] ^= 1
                t[alter[1]] = b
            p = os.path.join(ld, fn)
            write_st(p, t)
            shas.append(hashlib.sha256(open(p, "rb").read()).hexdigest())
            sizes.append(str(os.path.getsize(p)))
        rows.append(dict(label=lab, family="T", stage="t", repo="none", branch="b", commit="c", step=li, n_files=3,
                         bytes=sum(map(int, sizes)), files=";".join(FILES), sizes=";".join(sizes), sha256=";".join(shas),
                         note=""))
    with open(os.path.join(d, "ckpts.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L = LABELS
    job = {"chains": [{"name": "rl", "members": L[:5], "start": L[0]}, {"name": "side", "members": [L[0], L[5]],
                                                                        "start": L[0]}],
           "pairs": [[L[1], L[3]]], "gram": [[L[2], L[3], L[4], L[5]]], "lora": True}
    job["members"] = L
    json.dump({"T": job}, open(os.path.join(d, "jobs.json"), "w"))
    # LoRA adapters (rank 4, alpha 8) on q_proj and down_proj
    for name in ("main", "ctrl"):
        ad = os.path.join(d, "lora", name)
        os.makedirs(ad)
        json.dump({"r": 4, "lora_alpha": 8}, open(os.path.join(ad, "adapter_config.json"), "w"))
        from safetensors.numpy import save_file
        t = {}
        for n, sh in [("model.layers.0.self_attn.q_proj.weight", (16, 16)), ("model.layers.0.mlp.down_proj.weight", (16, 40))]:
            base = "base_model.model." + n.replace(".weight", "")
            t[base + ".lora_A.weight"] = rng.normal(0, 0.1, (4, sh[1])).astype(np.float32)
            t[base + ".lora_B.weight"] = rng.normal(0, 0.1, (sh[0], 4)).astype(np.float32)
        save_file(t, os.path.join(ad, "adapter_model.safetensors"))
    return job


def run_engine(d, device, out, extra=()):
    cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine.py"), "--job", "T",
           "--jobs", os.path.join(d, "jobs.json"), "--ckpts", os.path.join(d, "ckpts.csv"), "--out", out,
           "--work", os.path.join(d, "work"), "--device", device, "--local-root", os.path.join(d, "local"),
           "--lora-dir", os.path.join(d, "lora"), "--chunk-melems", "0.0001", "--disk-cap-gb", "1"] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True)


def read(out, kind):
    rows = []
    for k in range(3):
        p = os.path.join(out, "T", f"shard_{k}", f"{kind}.csv")
        rows += list(csv.DictReader(open(p)))
    return rows


def check(out, C, d):
    """Compare engine CSVs with numpy on the original (unaltered) bits. Returns the number of mismatches."""
    bad = []
    V = [{n: bits_to_f64(b) for n, b in c.items()} for c in C]
    idx = {lab: i for i, lab in enumerate(LABELS)}

    def close(x, y, tol=1e-6):
        return abs(float(x) - y) <= tol * max(abs(y), 1e-30) + 1e-300

    for r in read(out, "iv"):
        a, b, t = idx[r["a"]], idx[r["b"]], r["tensor"]
        A, B = V[a][t], V[b][t]
        D = B - A
        exp = dict(d2=(D * D).sum(), na2=(A * A).sum(), nb2=(B * B).sum())
        for kk, v in exp.items():
            if not close(r[kk], v):
                bad.append(("iv", kk, r["a"], r["b"], t, r[kk], v))
        neq = int((C[a][t] == C[b][t]).sum())
        nul = int((np.abs(D) <= ulp_np(C[a][t])).sum())
        if int(r["n_eq"]) != neq or int(r["n_ulp"]) != nul or int(r["numel"]) != A.size:
            bad.append(("iv-count", r["a"], r["b"], t, r["n_eq"], neq, r["n_ulp"], nul))
    job = json.load(open(os.path.join(d, "jobs.json")))["T"]
    chains = {c["name"]: c for c in job["chains"]}
    for r in read(out, "lag"):
        mem = chains[r["chain"]]["members"]
        i, L, t = int(r["idx"]), int(r["lag"]), r["tensor"]
        d1 = V[idx[mem[i]]][t] - V[idx[mem[i - 1]]][t]
        d2 = V[idx[mem[i - L]]][t] - V[idx[mem[i - L - 1]]][t]
        if not close(r["dot"], (d1 * d2).sum(), 1e-5):
            bad.append(("lag", r["chain"], i, L, t))
    for r in read(out, "st"):
        mem = chains[r["chain"]]["members"]
        i, t = int(r["idx"]), r["tensor"]
        s, a, b = (idx[x] for x in (chains[r["chain"]]["start"], mem[i - 1], mem[i]))
        O = V[b][t] - V[s][t]
        if not close(r["o2"], (O * O).sum()) or not close(r["dot_prev"], ((V[b][t] - V[a][t]) * (V[a][t] - V[s][t])).sum(), 1e-5):
            bad.append(("st", r["chain"], i, t))
        if int(r["n_eq_s"]) != int((C[b][t] == C[s][t]).sum()) or int(r["n_ulp_s"]) != int((np.abs(O) <= ulp_np(C[s][t])).sum()):
            bad.append(("st-count", r["chain"], i, t))
    for r in read(out, "gram"):
        t = r["tensor"]
        ref = idx[r["ref"]]
        Y = np.stack([(V[idx[m]][t] - V[ref][t]).ravel() for m in r["members"].split("|")])
        G = Y @ Y.T
        exp = [G[i, j] for i in range(len(G)) for j in range(i, len(G))]
        got = [float(x) for x in r["gram_upper"].split()]
        if len(got) != len(exp) or any(not close(g, e, 1e-9) for g, e in zip(got, exp)):
            bad.append(("gram", t))
    # LoRA: main / ctrl dots against numpy B @ A; random baselines against the engine's own factors (norm match)
    from safetensors.numpy import load_file
    ad = {n: load_file(os.path.join(d, "lora", n, "adapter_model.safetensors")) for n in ("main", "ctrl")}
    lr = read(out, "lora")
    if len(lr) != 4 * 2:
        bad.append(("lora-rows", len(lr)))
    for r in lr:
        t = r["tensor"]
        base = "base_model.model." + t.replace(".weight", "")
        O = V[idx[r["b"]]][t] - V[0][t]
        for n in ("main", "ctrl"):
            W = 2.0 * ad[n][base + ".lora_B.weight"].astype(np.float64) @ ad[n][base + ".lora_A.weight"].astype(np.float64)
            if not close(r[f"dot_{n}"], (O * W).sum(), 1e-5):
                bad.append(("lora", n, r["b"], t, r[f"dot_{n}"], (O * W).sum()))
    for r in csv.DictReader(open(os.path.join(out, "T", "lora_norms.csv"))):
        for q in range(8):
            if not close(r[f"n2_r{q}"], float(r["n2_main"]), 1e-6):
                bad.append(("lora-norm", r["tensor"], q))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dir", default="/tmp/ow_selftest")
    ap.add_argument("--cache-gb", default="-1", help="engine --gpu-cache-gb; a tiny value (4e-6) forces evictions")
    a = ap.parse_args()
    X = ["--gpu-cache-gb", a.cache_gb]
    rng = np.random.default_rng(20261125)
    C = make_ckpts(rng)
    ok = True
    # positive control
    build(a.dir, C, np.random.default_rng(1))
    p = run_engine(a.dir, a.device, os.path.join(a.dir, "out"), X)
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-3000:])
        print("SELFTEST FAIL (engine error)")
        sys.exit(1)
    pos_out = p.stdout + p.stderr
    bad = check(os.path.join(a.dir, "out"), C, a.dir)
    n_iv = len(read(os.path.join(a.dir, "out"), "iv"))
    print(f"positive control: {n_iv} interval rows, {len(bad)} mismatches", bad[:3])
    ok &= not bad and n_iv == (4 + 1 + 1) * 6
    # edge-case coverage: the synthetic data must contain each kind of change
    t = "model.layers.0.self_attn.q_proj.weight"
    D = bits_to_f64(C[3][t]) - bits_to_f64(C[2][t])
    u = ulp_np(C[2][t])
    cov = dict(eq=int((D == 0).sum()), one_ulp=int(((np.abs(D) > 0) & (np.abs(D) <= u)).sum()), more=int((np.abs(D) > u).sum()))
    print("coverage c2->c3 q_proj:", cov)
    ok &= all(v > 0 for v in cov.values())
    # negative control 1: alter one element of c3's q_proj by one bit; engine output must disagree with the original
    build(a.dir + "_neg", C, np.random.default_rng(1), alter=(3, "model.layers.0.self_attn.q_proj.weight"))
    p = run_engine(a.dir + "_neg", a.device, os.path.join(a.dir + "_neg", "out"), X)
    bad_neg = check(os.path.join(a.dir + "_neg", "out"), C, a.dir + "_neg") if p.returncode == 0 else ["engine error"]
    print(f"negative control 1 (altered tensor): {len(bad_neg)} mismatches (must be > 0)")
    ok &= len(bad_neg) > 0
    # negative control 2: wrong sha256 in the manifest must stop the engine
    d2 = a.dir + "_sha"
    build(d2, C, np.random.default_rng(1))
    rows = list(csv.DictReader(open(os.path.join(d2, "ckpts.csv"))))
    s = rows[2]["sha256"].split(";")
    s[1] = "0" * 64
    rows[2]["sha256"] = ";".join(s)
    with open(os.path.join(d2, "ckpts.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    p = run_engine(d2, a.device, os.path.join(d2, "out"))
    caught = p.returncode != 0 and "HASH MISMATCH" in (p.stdout + p.stderr)
    print(f"negative control 2 (wrong sha256): engine stopped = {caught}")
    ok &= caught
    cache_line = [l.split("gpu cache", 1)[1][:60] for l in pos_out.splitlines() if "gpu cache" in l][-1:]
    print("SELFTEST", "PASS" if ok else "FAIL", f"device={a.device} cache={a.cache_gb}", cache_line)


if __name__ == "__main__":
    main()
