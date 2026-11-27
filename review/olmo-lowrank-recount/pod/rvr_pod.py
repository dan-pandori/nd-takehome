"""Reviewer (olmo-lowrank): seeded raw-weight recompute of Part 1 (spectra, floors, LoRA overlaps) and of the Part-2
adapter truncations, on a pod. My own code, independent of olmo_lowrank/{spectra,linalg,adapters,ckpt}.py:
  - my own safetensors byte reader (header JSON + np.fromfile at the tensor's offset), bf16 -> float32 by bit shift;
  - every change D = W_b - W_a in float64 (exact for any two bf16 values);
  - singular values from a float64 QR of the tall orientation followed by the SVD of the triangular factor
    (the executor used fp32 randomized SVD for the top 256 and float64 Gram eigenvalues for the full spectra);
  - my own bf16 round-to-nearest-even (integer bit arithmetic, checked against torch's cast in the self-test), my own
    floor bisection, my own seeds (crc32 of keys starting "rv|"), my own Gaussian and random rank-16 baselines.

usage: python rvr_pod.py selftest
       python rvr_pod.py fetch   plan.json --dl /root/rvdl --ext /root/rvext [--inflight 8]
       python rvr_pod.py compute plan.json --ext /root/rvext --out OUT --lora /root/rv/lora --adapters /root/rv/adapters
Outputs in OUT: rows.csv (family x matrix x change / floor), lora.csv, adapters.csv, gauss.csv, sv_<fam>_L<layer>.npz
(every singular value, float64), timing.csv, files.csv (fetch: bytes, seconds, sha256 check).
"""
import csv
import hashlib
import json
import math
import os
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import torch

KS = (1, 4, 16, 64, 256)
TYPES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
GROUP = {t: ("self_attn" if t[0] in "qkvo" else "mlp") for t in TYPES}
DEV = "cuda"

# changes per family (pre-registration "Part 1: spectra" table)
CH32 = [(f"N{t}", "dpo", f"s{t:04d}", "net") for t in (50, 100, 500, 750, 1100, 1600, 2300)] + \
       [("I_early", "s0050", "s0100", "interval"), ("I_mid", "s1100", "s1150", "interval"),
        ("I_late", "s2250", "s2300", "interval"), ("K", "s1100", "s2100", "chord"),
        ("SFT", "base", "sft", "total"), ("DPO", "sft", "dpo", "total")]
CH7 = [(f"N{t}", "dpo", f"r{t:04d}", "net") for t in (25, 100, 500, 1000, 1375)] + \
      [("I_early", "r0025", "r0050", "interval"), ("I_mid", "r0500", "r0525", "interval"),
       ("I_late", "r1350", "r1375", "interval"), ("K", "r0500", "r1375", "chord"),
       ("SFT", "base", "sft", "total"), ("DPO", "sft", "dpo", "total"), ("ZIF", "base", "zif", "total")]
FLOORB = {"32B": {"N50", "N500", "N1100", "N2300", "I_early", "I_late", "K", "SFT", "DPO"},
          "7B": {"N1375", "I_late", "SFT", "ZIF"}}
VEC = {"32B": {"N100", "N1100", "N2300"}, "7B": set()}  # changes whose top singular vectors are formed


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


def seed_of(*parts):
    return zlib.crc32(("rv|" + "|".join(map(str, parts))).encode())


# ------------------------------------------------------------------ safetensors bytes
def st_header(path):
    with open(path, "rb") as f:
        n = int.from_bytes(f.read(8), "little")
        h = json.loads(f.read(n))
    h.pop("__metadata__", None)
    return {k: dict(dtype=v["dtype"], shape=v["shape"], off=8 + n + v["data_offsets"][0],
                    nbytes=v["data_offsets"][1] - v["data_offsets"][0]) for k, v in h.items()}


def st_read(path, info):
    """-> float32 numpy array of the tensor (BF16 by bit shift, F32 as stored, F16 widened)."""
    shape, dt = info["shape"], info["dtype"]
    cnt = int(np.prod(shape))
    if dt == "BF16":
        raw = np.fromfile(path, dtype="<u2", count=cnt, offset=info["off"])
        assert raw.size == cnt and info["nbytes"] == 2 * cnt
        return (raw.astype(np.uint32) << 16).view(np.float32).reshape(shape)
    if dt == "F32":
        raw = np.fromfile(path, dtype="<f4", count=cnt, offset=info["off"])
        assert raw.size == cnt and info["nbytes"] == 4 * cnt
        return raw.reshape(shape)
    if dt == "F16":
        raw = np.fromfile(path, dtype="<f2", count=cnt, offset=info["off"])
        assert raw.size == cnt
        return raw.astype(np.float32).reshape(shape)
    raise ValueError(dt)


def bf16_bits_to_t(u16, dev=DEV):
    """uint16 numpy (bf16 bits) -> float32 torch tensor on dev (bit shift)."""
    t = torch.from_numpy(u16.astype(np.int32)).to(dev)
    return (t << 16).view(torch.float32)


# ------------------------------------------------------------------ numerics
def bf16_rne(x):
    """float32 tensor -> float32 tensor holding the nearest bf16 values (ties to even), by integer arithmetic on the
    float32 bit pattern: add 0x7FFF + (bit 16), clear the low 16 bits (finite inputs; a mantissa carry moves into the
    exponent, which is the correct rounding)."""
    b = x.contiguous().view(torch.int32).to(torch.int64) & 0xFFFFFFFF
    lsb = (b >> 16) & 1
    r = ((b + 0x7FFF + lsb) >> 16) << 16
    r = torch.where(r >= 2 ** 31, r - 2 ** 32, r).to(torch.int32)
    return r.view(torch.float32)


def tall(D):
    """(A, transposed): A = D or D^T with rows >= cols."""
    return (D.T, True) if D.shape[0] < D.shape[1] else (D, False)


SVMODE = {"values": "gpu", "vectors": "gpu"}


def svals(D):
    """All singular values of D (float64, descending): QR of the tall orientation, then the SVD of R."""
    A, _ = tall(D)
    R = torch.linalg.qr(A, mode="r")[1] if A.shape[0] > A.shape[1] else A
    if SVMODE["values"] == "cpu":
        s = np.linalg.svd(R.cpu().numpy(), compute_uv=False)
        return torch.from_numpy(s).to(DEV)
    return torch.linalg.svdvals(R)


def svd_top(D, k):
    """(U [m,k], S [all], V [n,k]) of D, float64, from the QR of the tall orientation and the SVD of R."""
    A, tr = tall(D)
    if A.shape[0] > A.shape[1]:
        Q, R = torch.linalg.qr(A, mode="reduced")
    else:
        Q, R = None, A
    if SVMODE["vectors"] == "cpu":
        u, s, vh = np.linalg.svd(R.cpu().numpy(), full_matrices=False)
        Ur, S, Vr = torch.from_numpy(u[:, :k]).to(DEV), torch.from_numpy(s).to(DEV), torch.from_numpy(vh[:k].T.copy()).to(DEV)
    else:
        u, S, vh = torch.linalg.svd(R, full_matrices=False)
        Ur, Vr = u[:, :k], vh[:k].T
    L = Q @ Ur if Q is not None else Ur   # left vectors of A
    # A = L S Vr^T ; D = A (not transposed) or A^T
    return (Vr, S, L) if tr else (L, S, Vr)


def n2(M):
    return float((M.double() ** 2).sum())


def shares(s, nn):
    c = torch.cumsum(s.double() ** 2, 0)
    return {k: float(c[min(k, len(s)) - 1]) / nn for k in KS}


def floor(W32, target, key):
    """R(s) = bf16_rne(W + s Z) - W (float32, exact), Z ~ N(0, 1) seeded by key; s by bisection on log s with
    ||R(s)||^2 = target (relative tolerance 1e-6 or 80 halvings). -> (R float64, s, achieved norm^2)."""
    g = torch.Generator(device=DEV)
    g.manual_seed(seed_of("floor", key))
    Z = torch.randn(W32.shape, generator=g, device=DEV, dtype=torch.float32)

    def R(s):
        return bf16_rne(W32 + s * Z) - W32

    lo, hi = 1e-12, 1e-12
    while n2(R(hi)) < target:
        hi *= 4.0
    lo = hi / 4.0
    while n2(R(lo)) > target and lo > 1e-30:
        lo /= 4.0
    s = math.sqrt(lo * hi)
    for _ in range(80):
        s = math.sqrt(lo * hi)
        v = n2(R(s))
        if abs(v / target - 1) < 1e-6:
            break
        lo, hi = (s, hi) if v < target else (lo, s)
    Rs = R(s).double()
    del Z
    return Rs, s, n2(Rs)


def orth(X):
    return torch.linalg.qr(X.double(), mode="reduced")[0]


def overlap(U, Q):
    return float(((U.T @ Q) ** 2).sum()) / U.shape[1]


# ------------------------------------------------------------------ self-test
def selftest():
    ok = True
    torch.backends.cuda.matmul.allow_tf32 = False
    g = torch.Generator(device=DEV)
    g.manual_seed(1)
    x = torch.randn(4_000_000, device=DEV, generator=g) * 3.0
    # exact ties: bf16 values plus half an ulp
    base = bf16_rne(torch.randn(1_000_000, device=DEV, generator=g))
    bits = base.view(torch.int32)
    tie = (bits + 0x8000).view(torch.float32)
    for name, v in (("random", x), ("ties", tie), ("tiny", x * 1e-30), ("big", x * 1e30)):
        a, b = bf16_rne(v), v.to(torch.bfloat16).float()
        e = int((a != b).sum())
        print(f"bf16_rne vs torch cast ({name}): {e} mismatches")
        ok &= e == 0
    # negative control: truncation instead of rounding must disagree
    trunc = ((x.view(torch.int32).to(torch.int64) >> 16) << 16).to(torch.int32).view(torch.float32)
    nc = int((trunc != x.to(torch.bfloat16).float()).sum())
    print(f"negative control (truncation) mismatches: {nc} (expect ~half of 4e6)")
    ok &= nc > 1_000_000
    # SVD routes against numpy LAPACK, tall / wide / square
    for m, n in ((900, 300), (300, 900), (400, 400)):
        M = torch.randn(m, n, device=DEV, generator=g, dtype=torch.float64)
        ref = np.linalg.svd(M.cpu().numpy(), compute_uv=False)
        for mode in ("gpu", "cpu"):
            SVMODE["values"] = mode
            e = float(np.max(np.abs(svals(M).cpu().numpy() - ref) / ref[0]))
            print(f"svals {m}x{n} {mode}: max err / s1 {e:.1e}")
            ok &= e < 1e-12
        for mode in ("gpu", "cpu"):
            SVMODE["vectors"] = mode
            U, S, V = svd_top(M, 20)
            rec = (U * S[:20]) @ V.T
            u, s, vh = np.linalg.svd(M.cpu().numpy(), full_matrices=False)
            ref20 = (u[:, :20] * s[:20]) @ vh[:20]
            e = float(np.linalg.norm(rec.cpu().numpy() - ref20) / np.linalg.norm(ref20))
            print(f"svd_top {m}x{n} {mode}: rank-20 product rel err {e:.1e}")
            ok &= e < 1e-10
    # floor: calibrated norm, W + R is bf16, monotone construction
    W = bf16_rne(0.02 * torch.randn(512, 768, device=DEV, generator=g))
    tgt = 1e-6 * n2(W)
    R, s, a = floor(W, tgt, "selftest")
    rebf = bool(torch.equal(bf16_rne((W.double() + R).float()), (W.double() + R).float()))
    print(f"floor: achieved/target {a / tgt:.7f}, W+R on the bf16 grid {rebf}, unchanged share {float((R == 0).double().mean()):.3f}")
    ok &= abs(a / tgt - 1) < 1e-5 and rebf
    # planted overlap
    U0 = orth(torch.randn(2000, 16, device=DEV, generator=g, dtype=torch.float64))
    print(f"overlap planted {overlap(U0, U0):.4f} (1), random {overlap(U0, orth(torch.randn(2000, 16, device=DEV, generator=g, dtype=torch.float64))):.4f} (~{16 / 2000:.4f})")
    # timing at the real sizes: choose cpu or gpu per route
    R5 = torch.randn(5120, 5120, device=DEV, generator=g, dtype=torch.float64)
    tm = {}
    for mode in ("gpu", "cpu"):
        SVMODE["values"] = mode
        torch.cuda.synchronize(); t0 = time.time(); svals(R5); torch.cuda.synchronize(); tm[("values", mode)] = time.time() - t0
        SVMODE["vectors"] = mode
        torch.cuda.synchronize(); t0 = time.time(); svd_top(R5, 256); torch.cuda.synchronize(); tm[("vectors", mode)] = time.time() - t0
    for route in ("values", "vectors"):
        SVMODE[route] = min(("gpu", "cpu"), key=lambda md: tm[(route, md)])
    print("timing 5120^2 float64:", {f"{a}/{b}": round(v, 2) for (a, b), v in tm.items()}, "-> chosen", SVMODE)
    json.dump(SVMODE, open("svmode.json", "w"))
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok


# ------------------------------------------------------------------ fetch
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 24)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def cmd_fetch(plan, dl, ext, inflight):
    from huggingface_hub import hf_hub_download
    P = json.load(open(plan))
    jobs = []
    for key, m in P["members"].items():
        for fn, sha in m["files"]:
            jobs.append((key, m, fn, sha))
    os.makedirs(ext, exist_ok=True)
    flog = open(os.path.join(ext, "files.csv"), "a", newline="")
    fw = csv.writer(flog)
    lock = threading.Lock()

    def one(job):
        key, m, fn, sha = job
        fam, name = key.split(":")
        outd = os.path.join(ext, fam, name)
        os.makedirs(outd, exist_ok=True)
        need = {k: v for k, v in m["tensors"].items() if v["file"] == fn}
        if all(os.path.exists(os.path.join(outd, k + ".npy")) for k in need):
            return key, fn, "skip"
        t0 = time.time()
        local = os.path.join(dl, fam, name)
        for att in range(4):
            try:
                p = hf_hub_download(m["repo"], fn, revision=m["commit"], local_dir=local)
                break
            except Exception as e:  # retried, then raised
                log("retry", key, fn, repr(e)[:200])
                if att == 3:
                    raise
                time.sleep(30)
        t_dl = time.time() - t0
        got = sha256_file(p)
        ok = got == sha
        if ok:
            hdr = st_header(p)
            for k, v in need.items():
                h = hdr[k]
                assert h["dtype"] == v["dtype"] == "BF16" and h["shape"] == v["shape"] and h["off"] == v["off"], (key, k)
                raw = np.fromfile(p, dtype="<u2", count=int(np.prod(h["shape"])), offset=h["off"]).reshape(h["shape"])
                np.save(os.path.join(outd, k + ".npy.tmp.npy"), raw)
                os.replace(os.path.join(outd, k + ".npy.tmp.npy"), os.path.join(outd, k + ".npy"))
        os.remove(p)
        with lock:
            fw.writerow([key, m["label"], m["commit"], fn, sha, got, ok, round(t_dl, 1), round(time.time() - t0, 1),
                         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
            flog.flush()
        if not ok:
            raise RuntimeError(f"sha256 mismatch {key} {fn}")
        return key, fn, round(time.time() - t0, 1)

    t0 = time.time()
    with ThreadPoolExecutor(inflight) as ex:
        futs = [ex.submit(one, j) for j in jobs]
        for f in as_completed(futs):
            log("fetched", *f.result())
    log(f"fetch done: {len(jobs)} files in {time.time() - t0:.0f} s")
    open(os.path.join(ext, "FETCH_DONE"), "w").close()


# ------------------------------------------------------------------ compute
class Adapter:
    def __init__(self, d):
        self.cfg = json.load(open(os.path.join(d, "adapter_config.json")))
        self.path = os.path.join(d, "adapter_model.safetensors")
        self.hdr = st_header(self.path)
        self.scale = self.cfg["lora_alpha"] / self.cfg["r"]

    def BA(self, layer, t):
        k = f"base_model.model.model.layers.{layer}.{GROUP[t]}.{t}.lora_"
        B = torch.from_numpy(st_read(self.path, self.hdr[k + "B.weight"]).copy()).to(DEV).double()
        A = torch.from_numpy(st_read(self.path, self.hdr[k + "A.weight"]).copy()).to(DEV).double()
        return B, A


def cmd_compute(plan, ext, out, lora_dir, ad_dir):
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    if os.path.exists("svmode.json"):
        SVMODE.update(json.load(open("svmode.json")))
    log("svd routes", SVMODE)
    P = json.load(open(plan))
    os.makedirs(out, exist_ok=True)
    F = {}
    for name, fn in (("rows", ["fam", "name", "layer", "type", "change", "kind", "m", "n", "norm2", "s1", "s256",
                               "n_sigma"] + [f"share_{k}" for k in KS] +
                      ["stable_rank", "floorA_s1", "signal_full", "signal_256", "floorB_s", "floorB_n2", "floorB_s1",
                       "spike", "seconds"]),
                     ("lora", ["fam", "name", "layer", "type", "change", "adapter", "overlap_left", "overlap_right",
                               "lora_norm2", "inner_full"] + [f"inner_k{k}" for k in KS]),
                     ("adapters", ["name", "layer", "type", "adapter", "r", "lora_alpha", "B_shape", "A_shape",
                                   "rel_err_fp64", "rel_err_bf16_factors", "resid_n2", "identity_n2", "kept_share",
                                   "max_abs_BA"]),
                     ("gauss", ["fam", "m", "n", "seed", "norm2", "s1"] + [f"share_{k}" for k in KS] + ["stable_rank"]),
                     ("timing", ["fam", "name", "what", "seconds"])):
        f = open(os.path.join(out, f"{name}.csv"), "a", newline="")
        w = csv.DictWriter(f, fieldnames=fn)
        if f.tell() == 0:
            w.writeheader()
        F[name] = (f, w)

    def put(name, row):
        F[name][1].writerow(row)
        F[name][0].flush()

    lora = {n: Adapter(os.path.join(lora_dir, n)) for n in ("main", "ctrl")}
    ads = {n: Adapter(os.path.join(ad_dir, n)) for n in ("T1", "T4", "T16", "T64", "T256", "C16", "Z8")
           if os.path.exists(os.path.join(ad_dir, n, "adapter_model.safetensors"))}
    log("adapters", {n: (a.cfg["r"], a.cfg["lora_alpha"]) for n, a in ads.items()}, "lora", {n: (a.cfg["r"], a.cfg["lora_alpha"]) for n, a in lora.items()})
    gauss_done = set()
    for fam, CH in (("32B", CH32), ("7B", CH7)):
        members = sorted({x for c in CH for x in (c[1], c[2])})
        for layer in P["layers"][fam]:
            done_mark = os.path.join(out, f"done_{fam}_L{layer}")
            if os.path.exists(done_mark):
                continue
            sv_store = {}
            for t in TYPES:
                name = f"model.layers.{layer}.{GROUP[t]}.{t}.weight"
                W = {mb: bf16_bits_to_t(np.load(os.path.join(ext, fam, mb, name + ".npy"))) for mb in members}
                nn_of, S_of = {}, {}
                for cid, a, b, kind in CH:
                    t0 = time.time()
                    D = W[b].double() - W[a].double()
                    nn = n2(D)
                    nn_of[cid] = nn
                    if cid in VEC[fam] or (fam == "32B" and cid == "N2300"):
                        U, S, V = svd_top(D, 256)
                    else:
                        U = V = None
                        S = svals(D)
                    S_of[cid] = S
                    sh = shares(S, nn)
                    row = {"fam": fam, "name": name, "layer": layer, "type": t, "change": cid, "kind": kind,
                           "m": D.shape[0], "n": D.shape[1], "norm2": repr(nn), "s1": repr(float(S[0])),
                           "s256": repr(float(S[min(255, len(S) - 1)])), "n_sigma": len(S),
                           "stable_rank": repr(nn / float(S[0]) ** 2)}
                    row.update({f"share_{k}": repr(sh[k]) for k in KS})
                    if cid in FLOORB[fam]:
                        tb = time.time()
                        RB, sB, aB = floor(W[a], nn, ("B", fam, cid, name))
                        SB = svals(RB)
                        del RB
                        row.update({"floorB_s": repr(sB), "floorB_n2": repr(aB), "floorB_s1": repr(float(SB[0])),
                                    "spike": int((S > SB[0]).sum())})
                        put("timing", {"fam": fam, "name": name, "what": f"floorB {cid}", "seconds": round(time.time() - tb, 2)})
                    sv_store[f"{cid}|{name}"] = S.cpu().numpy()
                    if U is not None and fam == "32B":
                        U16, V16 = U[:, :16], V[:, :16]
                        for an, ad in lora.items():
                            B, A = ad.BA(layer, t)
                            sc = ad.scale
                            QB, QA = orth(B), orth(A.T)
                            inner_full = sc * float((B * (D @ A.T)).sum())
                            # <U_k S_k V_k^T, sc B A> = sc * sum_i S_i (U^T B)_i . (A V)_i
                            tk = ((U.T @ B) * (A @ V).T).sum(1) * S[:U.shape[1]] * sc
                            ck = torch.cumsum(tk, 0)
                            ln2 = sc * sc * float(((B.T @ B) * (A @ A.T)).sum())
                            put("lora", {"fam": fam, "name": name, "layer": layer, "type": t, "change": cid,
                                         "adapter": an, "overlap_left": repr(overlap(U16, QB)),
                                         "overlap_right": repr(overlap(V16, QA)), "lora_norm2": repr(ln2),
                                         "inner_full": repr(inner_full),
                                         **{f"inner_k{k}": repr(float(ck[k - 1])) for k in KS}})
                        for qn in range(4):
                            g = torch.Generator(device=DEV)
                            g.manual_seed(seed_of("rand16", name, qn))
                            Br = torch.randn(D.shape[0], 16, generator=g, device=DEV, dtype=torch.float64)
                            Ar = torch.randn(16, D.shape[1], generator=g, device=DEV, dtype=torch.float64)
                            put("lora", {"fam": fam, "name": name, "layer": layer, "type": t, "change": cid,
                                         "adapter": f"rv_r{qn}", "overlap_left": repr(overlap(U16, orth(Br))),
                                         "overlap_right": repr(overlap(V16, orth(Ar.T)))})
                        if cid == "N2300":
                            for an, ad in ads.items():
                                B, A = ad.BA(layer, t)
                                BA = B @ A
                                r = {"name": name, "layer": layer, "type": t, "adapter": an, "r": ad.cfg["r"],
                                     "lora_alpha": ad.cfg["lora_alpha"], "B_shape": "x".join(map(str, B.shape)),
                                     "A_shape": "x".join(map(str, A.shape)), "max_abs_BA": repr(float(BA.abs().max()))}
                                if an != "Z8":
                                    k = 16 if an == "C16" else int(an[1:])
                                    sign = -1.0 if an == "C16" else 1.0
                                    ref = sign * ((U[:, :k] * S[:k]) @ V[:, :k].T)
                                    r["rel_err_fp64"] = repr(float(torch.linalg.norm(ad.scale * BA - ref) / torch.linalg.norm(ref)))
                                    Bb = bf16_rne(B.float()).double()
                                    Ab = bf16_rne(A.float()).double()
                                    r["rel_err_bf16_factors"] = repr(float(torch.linalg.norm(ad.scale * Bb @ Ab - ref) / torch.linalg.norm(ref)))
                                    r["resid_n2"] = repr(n2(D - sign * ad.scale * BA))
                                    r["identity_n2"] = repr(nn - float((S[:k] ** 2).sum()))
                                    r["kept_share"] = repr(float((S[:k] ** 2).sum()) / nn)
                                put("adapters", r)
                                del B, A, BA
                    del D, U, V
                    row["seconds"] = round(time.time() - t0, 2)
                    put("rows", row)
                # floor A: bf16 rounding of a Gaussian update on the RL start at the mean single-interval norm^2
                t0 = time.time()
                target = sum(nn_of[i] for i in ("I_early", "I_mid", "I_late")) / 3
                RA, sA, aA = floor(W["dpo"], target, ("A", fam, name))
                SA = svals(RA)
                del RA
                shA = shares(SA, aA)
                rowA = {"fam": fam, "name": name, "layer": layer, "type": t, "change": "floorA", "kind": "floor",
                        "m": W["dpo"].shape[0], "n": W["dpo"].shape[1], "norm2": repr(aA), "s1": repr(float(SA[0])),
                        "s256": repr(float(SA[min(255, len(SA) - 1)])), "n_sigma": len(SA),
                        "stable_rank": repr(aA / float(SA[0]) ** 2), "floorB_s": repr(sA), "floorB_n2": repr(target),
                        "seconds": round(time.time() - t0, 2)}
                rowA.update({f"share_{k}": repr(shA[k]) for k in KS})
                put("rows", rowA)
                sv_store[f"floorA|{name}"] = SA.cpu().numpy()
                # signal rank of every change against MY floor A
                for cid, S in S_of.items():
                    put("rows", {"fam": fam, "name": name, "layer": layer, "type": t, "change": cid, "kind": "signal",
                                 "floorA_s1": repr(float(SA[0])), "signal_full": int((S > SA[0]).sum()),
                                 "signal_256": int((S[:256] > SA[0]).sum())})
                # Gaussian baseline per shape (3 seeds)
                shp = tuple(sorted(W["dpo"].shape, reverse=True))
                if (fam, shp) not in gauss_done:
                    gauss_done.add((fam, shp))
                    for sd in range(3):
                        g = torch.Generator(device=DEV)
                        g.manual_seed(seed_of("gauss", shp, sd))
                        G = torch.randn(shp, generator=g, device=DEV, dtype=torch.float64)
                        gn = n2(G)
                        SG = svals(G)
                        shg = shares(SG, gn)
                        put("gauss", {"fam": fam, "m": shp[0], "n": shp[1], "seed": sd, "norm2": repr(gn),
                                      "s1": repr(float(SG[0])), **{f"share_{k}": repr(shg[k]) for k in KS},
                                      "stable_rank": repr(gn / float(SG[0]) ** 2)})
                        del G
                del W
                torch.cuda.empty_cache()
                log(f"{fam} {name} done")
            np.savez_compressed(os.path.join(out, f"sv_{fam}_L{layer}.npz"),
                                **{k.replace(".", "~"): v for k, v in sv_store.items()})
            open(done_mark, "w").close()
            log(f"{fam} layer {layer} done")
    open(os.path.join(out, "COMPUTE_DONE"), "w").close()


def main():
    a = sys.argv[1:]
    if a[0] == "selftest":
        sys.exit(0 if selftest() else 1)

    def opt(k, d=None):
        return a[a.index(k) + 1] if k in a else d
    if a[0] == "fetch":
        cmd_fetch(a[1], opt("--dl"), opt("--ext"), int(opt("--inflight", 8)))
    elif a[0] == "compute":
        cmd_compute(a[1], opt("--ext"), opt("--out"), opt("--lora"), opt("--adapters"))


if __name__ == "__main__":
    main()
