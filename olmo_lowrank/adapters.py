#!/usr/bin/env python3
"""olmo-lowrank Part 2 models (pod side): the SVD of RL's change D = W_s2300 - W_dpo on the 448 matrices, the T_k /
C16 / zero LoRA adapters (PEFT format, fp32), the F448 weights, and their checks.

  adapters.py svd    --dpo D --rl D --out O [--method exact|rsvd --p 256 --q 8]
        per layer O/factors/layer_XX.safetensors: <type>.U [m, 256], <type>.S [all or 256], <type>.V [n, 256] (fp32);
        O/factors/norms.csv (exact ||D||^2, sigma count, seconds per matrix); with --method exact also the full
        spectrum of every matrix (O/factors/spectra_N2300_exact.npz: name -> all singular values, float32 -> float64).
  adapters.py write  --out O [--base D]   O/adapters/{T1,T4,T16,T64,T256,C16,Z8}/ (adapter_config.json + adapter_model.safetensors)
  adapters.py verify --out O --dpo D --rl D   8 seeded matrices: B A vs U_k S_k V_k^T (fp32) and after a bf16 cast of
        B and A; the truncation identity ||D - D_k||^2 = ||D||^2 - sum_{i<=k} s_i^2; sha256 of every adapter file
        -> O/adapters/verify.json
  adapters.py f448   --dpo D --rl D --dst D   DPO with the 448 matrices replaced by the RL tensors (bitwise), checked
        tensor by tensor -> D/f448_check.json

B = U_k diag(S_k), A = V_k^T, lora_alpha = r (vLLM / PEFT scaling alpha / r = 1); C16 has B = -U_16 diag(S_16).
Z8 (r 8) has B = 0 and a seeded random A, so B A = 0 exactly (the zero-delta check of vLLM's LoRA path).
"""
import argparse
import csv
import json
import os
import random
import shutil
import sys
import time

import numpy as np
import torch
from safetensors import safe_open
from safetensors.torch import load_file, save_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linalg  # noqa: E402
from ckpt import GROUP, TYPES, Ckpt, matrices, sha256_file  # noqa: E402

RANKS = (1, 4, 16, 64, 256)
KMAX = 256


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


def peft_key(layer, t, which):
    return f"base_model.model.model.layers.{layer}.{GROUP[t]}.{t}.lora_{which}.weight"


def cmd_svd(a):
    linalg.precision()
    dev = "cuda"
    P, R = Ckpt(a.dpo), Ckpt(a.rl)
    L = P.n_layers()
    fd = os.path.join(a.out, "factors")
    os.makedirs(fd, exist_ok=True)
    rows, spectra = [], {}
    t_all = time.time()
    for layer in range(L):
        fn = os.path.join(fd, f"layer_{layer:02d}.safetensors")
        if os.path.exists(fn) and not a.force:
            continue
        out = {}
        for t in TYPES:
            name = f"model.layers.{layer}.{GROUP[t]}.{t}.weight"
            D = R.get(name, dev).float() - P.get(name, dev).float()
            n2 = linalg.norm2(D)
            torch.cuda.synchronize()
            t0 = time.time()
            if a.method == "exact":
                U, S, Vh = torch.linalg.svd(D, full_matrices=False)
                V = Vh[:KMAX].T
                U = U[:, :KMAX]
                spectra[name] = S.double().cpu().numpy()
            else:
                U, S, V = linalg.rsvd(D, k=KMAX, p=a.p, q=a.q, seed=linalg.seed_of("N2300", name))
            torch.cuda.synchronize()
            dt = time.time() - t0
            out[f"{t}.U"] = U.contiguous().cpu()
            out[f"{t}.S"] = S.contiguous().cpu()
            out[f"{t}.V"] = V.contiguous().cpu()
            s2 = float(S.double().pow(2).sum())
            rows.append({"name": name, "layer": layer, "type": t, "m": D.shape[0], "n": D.shape[1], "norm2": repr(n2),
                         "n_sigma": len(S), "sum_s2": repr(s2), "seconds": round(dt, 3), "method": a.method,
                         "p": a.p, "q": a.q})
            del D, U, S, V
        save_file(out, fn + ".tmp", metadata={"format": "pt", "method": a.method})
        os.replace(fn + ".tmp", fn)
        log(f"layer {layer} done ({time.time() - t_all:.0f} s)")
        if spectra:
            np.savez_compressed(os.path.join(fd, f"spectra_layer_{layer:02d}.npz"), **{k.replace(".", "__"): v for k, v in spectra.items()})
            spectra = {}
        with open(os.path.join(fd, "norms.csv"), "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            if f.tell() == 0:
                w.writeheader()
            w.writerows(rows)
        rows = []
    log(f"svd done in {time.time() - t_all:.0f} s")


def factors(out, layer):
    return load_file(os.path.join(out, "factors", f"layer_{layer:02d}.safetensors"))


def adapter_config(r, base):
    return {"alpha_pattern": {}, "auto_mapping": None, "base_model_name_or_path": base, "bias": "none",
            "fan_in_fan_out": False, "inference_mode": True, "init_lora_weights": True, "layers_pattern": None,
            "layers_to_transform": None, "lora_alpha": r, "lora_dropout": 0.0, "modules_to_save": None,
            "peft_type": "LORA", "r": r, "rank_pattern": {}, "revision": None, "target_modules": list(TYPES),
            "task_type": "CAUSAL_LM", "use_dora": False, "use_rslora": False}


def cmd_write(a):
    ad = os.path.join(a.out, "adapters")
    names = [f"T{k}" for k in RANKS] + ["C16", "Z8"]
    tens = {n: {} for n in names}
    L = len([f for f in os.listdir(os.path.join(a.out, "factors")) if f.startswith("layer_") and f.endswith(".safetensors")])
    for layer in range(L):
        F = factors(a.out, layer)
        for t in TYPES:
            U, S, V = F[f"{t}.U"], F[f"{t}.S"], F[f"{t}.V"]
            for k in RANKS:
                tens[f"T{k}"][peft_key(layer, t, "B")] = (U[:, :k] * S[:k]).contiguous()
                tens[f"T{k}"][peft_key(layer, t, "A")] = V[:, :k].T.contiguous()
            tens["C16"][peft_key(layer, t, "B")] = (-(U[:, :16] * S[:16])).contiguous()
            tens["C16"][peft_key(layer, t, "A")] = V[:, :16].T.contiguous()
            g = torch.Generator().manual_seed(linalg.seed_of("Z8", layer, t))
            tens["Z8"][peft_key(layer, t, "B")] = torch.zeros(U.shape[0], 8)
            tens["Z8"][peft_key(layer, t, "A")] = (0.01 * torch.randn(8, V.shape[0], generator=g)).contiguous()
    for n in names:
        d = os.path.join(ad, n)
        os.makedirs(d, exist_ok=True)
        r = 8 if n == "Z8" else (16 if n == "C16" else int(n[1:]))
        json.dump(adapter_config(r, a.base), open(os.path.join(d, "adapter_config.json"), "w"), indent=2)
        save_file(tens[n], os.path.join(d, "adapter_model.safetensors"), metadata={"format": "pt"})
        log(f"wrote {n}: {len(tens[n])} tensors")
        tens[n] = None


def cmd_verify(a):
    linalg.precision()
    dev = "cuda"
    P, R = Ckpt(a.dpo), Ckpt(a.rl)
    L = P.n_layers()
    rnd = random.Random(4949)
    pick = rnd.sample(matrices(L), 8)
    ad = os.path.join(a.out, "adapters")
    rep = {"matrices": [p[2] for p in pick], "checks": [], "files": {}}
    H = {}
    for n in sorted(os.listdir(ad)):
        f = os.path.join(ad, n, "adapter_model.safetensors")
        if os.path.exists(f):
            rep["files"][n] = {"sha256": sha256_file(f), "bytes": os.path.getsize(f),
                               "config_sha256": sha256_file(os.path.join(ad, n, "adapter_config.json"))}
            H[n] = safe_open(f, framework="pt")
    for layer, t, name in pick:
        F = factors(a.out, layer)
        U, S, V = F[f"{t}.U"].to(dev), F[f"{t}.S"].to(dev), F[f"{t}.V"].to(dev)
        D = R.get(name, dev).float() - P.get(name, dev).float()
        n2 = linalg.norm2(D)
        for n, h in H.items():
            B = h.get_tensor(peft_key(layer, t, "B")).to(dev)
            A = h.get_tensor(peft_key(layer, t, "A")).to(dev)
            BA = B @ A
            if n == "Z8":
                rep["checks"].append({"adapter": n, "name": name, "max_abs_BA": float(BA.abs().max())})
                continue
            k = 16 if n == "C16" else int(n[1:])
            sign = -1.0 if n == "C16" else 1.0
            ref = sign * ((U[:, :k] * S[:k]) @ V[:, :k].T)
            e = (BA - ref).double().norm() / ref.double().norm()
            Bb, Ab = B.to(torch.bfloat16).float(), A.to(torch.bfloat16).float()
            eb = (Bb @ Ab - ref).double().norm() / ref.double().norm()
            resid = linalg.norm2(D - sign * BA)
            ident = n2 - float(S[:k].double().pow(2).sum())
            rep["checks"].append({"adapter": n, "name": name, "rel_err_fp32": float(e), "rel_err_bf16_factors": float(eb),
                                  "resid_n2": resid, "identity_n2": ident,
                                  "identity_rel_gap": abs(resid - ident) / n2 if sign > 0 else None,
                                  "kept_share": float(S[:k].double().pow(2).sum()) / n2})
        del D
    ok = all((c.get("rel_err_fp32", 0) <= 1e-6) for c in rep["checks"] if "rel_err_fp32" in c) and \
        all(c.get("max_abs_BA", 0) == 0 for c in rep["checks"] if "max_abs_BA" in c)
    rep["pass"] = ok
    json.dump(rep, open(os.path.join(ad, "verify.json"), "w"), indent=1)
    log(f"verify {'PASS' if ok else 'FAIL'}; max fp32 rel err "
        f"{max(c['rel_err_fp32'] for c in rep['checks'] if 'rel_err_fp32' in c):.2e}; max bf16-factor rel err "
        f"{max(c['rel_err_bf16_factors'] for c in rep['checks'] if 'rel_err_bf16_factors' in c):.2e}")


def cmd_f448(a):
    """DPO with the 448 matrices from the RL checkpoint: written per RL shard file, every tensor checked bitwise."""
    P, R = Ckpt(a.dpo), Ckpt(a.rl)
    mats = {m[2] for m in matrices(P.n_layers())}
    assert set(P.where) == set(R.where), "tensor sets differ"
    os.makedirs(a.dst, exist_ok=True)
    rep = {"from_rl": 0, "from_dpo": 0, "dpo_rl_differ_outside": [], "files": {}}
    for f in sorted({R.where[k] for k in R.where}):
        base = os.path.basename(f)
        T = load_file(f)
        out = {}
        for k, v in T.items():
            if k in mats:
                out[k] = v
                rep["from_rl"] += 1
            else:
                d = P.get(k)
                if not torch.equal(d, v):
                    rep["dpo_rl_differ_outside"].append(k)
                out[k] = d
                rep["from_dpo"] += 1
        meta = safe_open(f, framework="pt").metadata() or {"format": "pt"}
        save_file(out, os.path.join(a.dst, base), metadata=meta)
        chk = load_file(os.path.join(a.dst, base))
        for k, v in chk.items():
            src = T[k] if k in mats else P.get(k)
            assert torch.equal(v, src) and v.dtype == src.dtype, f"mismatch {k}"
        rep["files"][base] = sha256_file(os.path.join(a.dst, base))
        log(f"f448 {base}: {len(out)} tensors")
        del T, out, chk
    for fn in os.listdir(a.dpo):
        if not fn.endswith(".safetensors") and os.path.isfile(os.path.join(a.dpo, fn)) and not fn.startswith("."):
            shutil.copy(os.path.join(a.dpo, fn), os.path.join(a.dst, fn))
    rep["pass"] = rep["from_rl"] == len(mats)
    json.dump(rep, open(os.path.join(a.dst, "f448_check.json"), "w"), indent=1)
    log(f"f448 {'PASS' if rep['pass'] else 'FAIL'}: {rep['from_rl']} RL tensors, {rep['from_dpo']} DPO tensors, "
        f"{len(rep['dpo_rl_differ_outside'])} non-448 tensors differ between DPO and RL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["svd", "write", "verify", "f448"])
    ap.add_argument("--dpo")
    ap.add_argument("--rl")
    ap.add_argument("--out")
    ap.add_argument("--dst")
    ap.add_argument("--base", default="/workspace/models/dpo")
    ap.add_argument("--method", default="exact", choices=["exact", "rsvd"])
    ap.add_argument("--p", type=int, default=256)
    ap.add_argument("--q", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    {"svd": cmd_svd, "write": cmd_write, "verify": cmd_verify, "f448": cmd_f448}[a.cmd](a)


if __name__ == "__main__":
    main()
