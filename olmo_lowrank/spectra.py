#!/usr/bin/env python3
"""olmo-lowrank Part 1 engine (pod side): spectra of training changes on the attention and MLP matrices.

  spectra.py --job R32|S32|R7 [--plan olmo_lowrank/plan/spectra_jobs.json] [--work /models/spec]
             [--out artifacts/olmo_lowrank/spectra] [--p 256 --q 8] [--full gram|svd] [--lora-dir D] [--inflight 8]
             [--disk-cap-gb 200]
  spectra.py --selftest

Per job (plan from plan_spectra.py): members are downloaded from the Hub at their pinned commits (hf_xet, several
files in flight, each file's sha256 checked against the manifest), step by step ("shard": shard file k of every
member; "all": every file), and deleted when no later step needs them. For every matrix of a step:
  - each change D = float32(W_b) - float32(W_a): exact ||D||^2, randomized top-256 (p, q), and for layers = 0 mod
    `subset_mod` all singular values (float64, --full);
  - floor A (jobs with RL intervals): bf16 rounding of a Gaussian update on the RL start, calibrated to the mean
    ||D||^2 of the three single intervals (linalg.floor_matrix); top-256 and (subset) full spectrum;
  - floor B per change: the same construction on the change's start weights at the change's own ||D||^2; top-16;
  - LoRA (R32, net changes): overlaps of RL's top-16 left / right singular subspaces with lora_main's / lora_ctrl's
    col(B) / row(A) and 4 seeded random rank-16 subspaces; <dW_lora, D_k> for k in KS and <dW_lora, D>.
Gaussian baselines per shape (3 seeds): top-256 and full spectra.

Outputs in <out>/<job>/: rows.csv (change x matrix), lora.csv, gauss.csv, files.csv, sigma_<step>.npz (top-256 sigma per
change|matrix and floorA|matrix), full_<step>.npz (subset), summary.json, DONE. A step with step_<k>.done is skipped on
restart.
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linalg  # noqa: E402
from ckpt import GROUP, TYPES, sha256_file  # noqa: E402

KS = linalg.KS
ROW_FIELDS = ["change", "kind", "name", "layer", "type", "m", "n", "norm2", "s1", "s256", "n_sigma"] + \
             [f"share_{k}" for k in KS] + ["stable_rank", "floorB_s", "floorB_n2", "floorB_s1", "floorB_share_16",
                                           "full", "seconds"]


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


def matname(layer, t):
    return f"model.layers.{layer}.{GROUP[t]}.{t}.weight"


class Store:
    """Downloads (hf_hub_download at the pinned commit into <work>/<member>/), sha256 checks, deletion."""

    def __init__(self, job, work, out_dir, inflight):
        from huggingface_hub import hf_hub_download
        self.dl = hf_hub_download
        self.work = work
        self.mem = {m["name"]: m for m in job["members"]}
        self.ex = ThreadPoolExecutor(inflight)
        self.fut = {}
        self.lock = threading.Lock()
        self.flog = open(os.path.join(out_dir, "files.csv"), "a", newline="")
        self.fw = csv.writer(self.flog)
        if self.flog.tell() == 0:
            self.fw.writerow(["member", "label", "file", "bytes", "seconds", "sha256_ok", "utc"])

    def path(self, member, f):
        return os.path.join(self.work, member, f)

    def _get(self, member, f):
        m = self.mem[member]
        p = self.path(member, f)
        want = m["sha256"][m["files"].index(f)]
        if os.path.exists(p + ".ok"):
            return p
        t0 = time.time()
        for attempt in range(4):
            try:
                self.dl(m["repo"], f, revision=m["commit"], local_dir=os.path.join(self.work, member))
                break
            except Exception as e:  # retried; the last failure propagates
                log("download retry", member, f, repr(e)[:200])
                if attempt == 3:
                    raise
                time.sleep(20)
        dt = time.time() - t0
        ok = sha256_file(p) == want
        with self.lock:
            self.fw.writerow([member, m["label"], f, os.path.getsize(p), round(dt, 1), ok,
                              time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
            self.flog.flush()
        if not ok:
            raise RuntimeError(f"sha256 mismatch {member} {f}")
        open(p + ".ok", "w").close()
        return p

    def want(self, member, f):
        k = (member, f)
        if k not in self.fut:
            self.fut[k] = self.ex.submit(self._get, member, f)
        return self.fut[k]

    def drop(self, member, f):
        p = self.path(member, f)
        for q in (p, p + ".ok"):
            if os.path.exists(q):
                os.remove(q)
        self.fut.pop((member, f), None)


def headers(path):
    from safetensors import safe_open
    with safe_open(path, framework="pt") as h:
        return list(h.keys())


def plan_steps(job):
    """-> list of steps: (step id, {member: [files]}). 'shard': file k of every member (identical layouts asserted on
    the pod from the real headers when the step runs); 'all': every file of every member."""
    if job["steps"] == "all":
        return [("all", {m["name"]: list(m["files"]) for m in job["members"]})]
    n = len(job["members"][0]["files"])
    assert all(len(m["files"]) == n for m in job["members"])
    return [(f"{k:02d}", {m["name"]: [m["files"][k]] for m in job["members"]}) for k in range(n)]


class Lora:
    def __init__(self, d, dev):
        from safetensors import safe_open
        self.f, self.scale = {}, {}
        for name in ("main", "ctrl"):
            cfg = json.load(open(os.path.join(d, name, "adapter_config.json")))
            self.scale[name] = cfg["lora_alpha"] / cfg["r"]
            self.f[name] = safe_open(os.path.join(d, name, "adapter_model.safetensors"), framework="pt")
        self.dev = dev

    def get(self, layer, t):
        k = f"base_model.model.model.layers.{layer}.{GROUP[t]}.{t}.lora_"
        return {n: (self.f[n].get_tensor(k + "B.weight").float().to(self.dev),
                    self.f[n].get_tensor(k + "A.weight").float().to(self.dev), self.scale[n]) for n in self.f}


def spectrum_row(cid, kind, name, layer, t, D, n2, S, full, dt):
    sh = linalg.shares(S, n2)
    s1 = float(S[0])
    r = {"change": cid, "kind": kind, "name": name, "layer": layer, "type": t, "m": D.shape[0], "n": D.shape[1],
         "norm2": repr(n2), "s1": repr(s1), "s256": repr(float(S[-1])), "n_sigma": len(S),
         "stable_rank": repr(n2 / (s1 * s1)) if s1 > 0 else "", "full": int(full is not None), "seconds": round(dt, 3)}
    for k in KS:
        r[f"share_{k}"] = repr(sh[k]) if sh[k] is not None else ""
    return r


def run_job(a):
    linalg.precision()
    dev = "cuda"
    J = json.load(open(a.plan))[a.job]
    out = os.path.join(a.out, a.job)
    os.makedirs(out, exist_ok=True)
    work = os.path.join(a.work, a.job)
    os.makedirs(work, exist_ok=True)
    store = Store(J, work, out, a.inflight)
    steps = plan_steps(J)
    lora = Lora(a.lora_dir, dev) if J.get("lora") else None
    t_job = time.time()
    summ = {"job": a.job, "p": a.p, "q": a.q, "full": a.full, "gpu": torch.cuda.get_device_name(0), "steps": {}}
    chg = J["changes"]
    by_id = {c["id"]: c for c in chg}
    fA = J.get("floorA")
    rows_f = open(os.path.join(out, "rows.csv"), "a", newline="")
    rw = csv.DictWriter(rows_f, fieldnames=ROW_FIELDS)
    if rows_f.tell() == 0:
        rw.writeheader()
    lora_f = open(os.path.join(out, "lora.csv"), "a", newline="")
    lw = csv.writer(lora_f)
    if lora_f.tell() == 0:
        lw.writerow(["change", "name", "layer", "type", "adapter", "overlap_left", "overlap_right", "lora_norm2",
                     "inner_full"] + [f"inner_k{k}" for k in KS])

    # Gaussian baselines per shape (once per job)
    gpath = os.path.join(out, "gauss.csv")
    shapes_done = set()
    if not os.path.exists(gpath):
        with open(gpath, "w", newline="") as gf:
            gw = csv.writer(gf)
            gw.writerow(["m", "n", "seed", "norm2", "s1"] + [f"share_{k}" for k in KS] + ["full_s1"] +
                        [f"full_share_{k}" for k in KS] + ["stable_rank"])
    # prefetch the first two steps
    for sid, need in steps[:2]:
        for mbr, fs in need.items():
            for f in fs:
                store.want(mbr, f)
    for si, (sid, need) in enumerate(steps):
        done_mark = os.path.join(out, f"step_{sid}.done")
        for nxt in steps[si + 1: si + 2]:
            for mbr, fs in nxt[1].items():
                for f in fs:
                    store.want(mbr, f)
        if os.path.exists(done_mark):
            log(f"step {sid} already done")
            continue
        t_dl = time.time()
        paths = {mbr: [store.want(mbr, f).result() for f in fs] for mbr, fs in need.items()}
        t_wait = time.time() - t_dl
        # tensors per member from the real headers; the matrices whose every member has them in this step
        from safetensors import safe_open
        hs = {mbr: {} for mbr in paths}
        for mbr, ps in paths.items():
            for p in ps:
                for k in headers(p):
                    hs[mbr][k] = p
        names = None
        for mbr in hs:
            s = {k for k in hs[mbr] if k.endswith("_proj.weight")}
            names = s if names is None else names & s
        if J["steps"] == "shard":
            first = sorted(hs)[0]
            for mbr in hs:  # identical layouts within a shard step
                assert {k for k in hs[mbr]} == {k for k in hs[first]}, f"layout differs: {mbr} step {sid}"
        mats = sorted(((int(n.split(".")[2]), n.split(".")[-2], n) for n in names), key=lambda x: (x[0], TYPES.index(x[1])))
        handles = {}

        def get(mbr, name):
            p = hs[mbr][name]
            if p not in handles:
                handles[p] = safe_open(p, framework="pt", device="cpu")
            return handles[p].get_tensor(name).to(dev)
        sig, full = {}, {}
        t_comp = time.time()
        for layer, t, name in mats:
            sub = (layer % (a.subset_mod or J["subset_mod"]) == 0)
            W = {}
            for c in chg:
                for mbr in (c["a"], c["b"]):
                    if mbr not in W:
                        W[mbr] = get(mbr, name)
            n2s = {}
            for c in chg:
                t0 = time.time()
                D = W[c["b"]].float() - W[c["a"]].float()
                n2 = linalg.norm2(D)
                n2s[c["id"]] = n2
                U, S, V = linalg.rsvd(D, k=256, p=a.p, q=a.q, seed=linalg.seed_of(a.job, c["id"], name))
                fs = linalg.full_svals(D, a.full).float().cpu().numpy() if sub else None
                # floor B: matched-norm rounded noise on the change's start weights
                RB, sB, nB = linalg.floor_matrix(W[c["a"]], n2, ("B", a.job, c["id"], name))
                _, SB, _ = linalg.rsvd(RB, k=16, p=a.p, q=a.q, seed=linalg.seed_of("B", a.job, c["id"], name))
                del RB
                r = spectrum_row(c["id"], c["kind"], name, layer, t, D, n2, S, fs, time.time() - t0)
                r.update({"floorB_s": repr(sB), "floorB_n2": repr(nB), "floorB_s1": repr(float(SB[0])),
                          "floorB_share_16": repr(float(SB.double().pow(2).sum()) / nB) if nB > 0 else ""})
                rw.writerow(r)
                sig[f"{c['id']}|{name}"] = S.cpu().numpy()
                if fs is not None:
                    full[f"{c['id']}|{name}"] = fs
                if lora is not None and c["kind"] == "net":
                    F = lora.get(layer, t)
                    U16, V16 = U[:, :16], V[:, :16]
                    for an, (B, A, sc) in F.items():
                        QB, QA = linalg.orth(B), linalg.orth(A.T)
                        inner_full = sc * float(((B.T @ D).double() * A.double()).sum())
                        ck = linalg.lowrank_inner(U, S, V, B, A, sc)
                        lw.writerow([c["id"], name, layer, t, an, repr(linalg.overlap(U16, QB)),
                                     repr(linalg.overlap(V16, QA)), repr(sc * sc * linalg.frob2_lowrank(B, A)),
                                     repr(inner_full)] + [repr(float(ck[k - 1])) for k in KS])
                    for qn in range(4):
                        g = linalg.gen(dev, linalg.seed_of("rand16", name, qn))
                        B = torch.randn(D.shape[0], 16, device=dev, generator=g)
                        A = torch.randn(16, D.shape[1], device=dev, generator=g)
                        lw.writerow([c["id"], name, layer, t, f"r{qn}", repr(linalg.overlap(U16, linalg.orth(B))),
                                     repr(linalg.overlap(V16, linalg.orth(A.T))), "", "", "", "", "", "", ""])
                del D, U, S, V
            if fA:
                t0 = time.time()
                target = sum(n2s[i] for i in fA["intervals"]) / len(fA["intervals"])
                RA, sA, nA = linalg.floor_matrix(W[fA["on"]], target, ("A", a.job, name))
                _, SA, _ = linalg.rsvd(RA, k=256, p=a.p, q=a.q, seed=linalg.seed_of("A", a.job, name))
                fs = linalg.full_svals(RA, a.full).float().cpu().numpy() if sub else None
                r = spectrum_row("floorA", "floor", name, layer, t, RA, nA, SA, fs, time.time() - t0)
                r.update({"floorB_s": repr(sA), "floorB_n2": repr(target)})  # floor A: its s and its target norm^2
                rw.writerow(r)
                sig[f"floorA|{name}"] = SA.cpu().numpy()
                if fs is not None:
                    full[f"floorA|{name}"] = fs
                del RA
            shp = tuple(sorted(W[chg[0]["a"]].shape, reverse=True))
            if shp not in shapes_done:
                shapes_done.add(shp)
                with open(gpath) as gf:
                    have = {(int(x["m"]), int(x["n"])) for x in csv.DictReader(gf)}
                if shp not in have:
                    with open(gpath, "a", newline="") as gf:
                        gw = csv.writer(gf)
                        for sd in range(3):
                            G = linalg.gaussian(shp, ("gauss", shp, sd), dev)
                            gn2 = linalg.norm2(G)
                            _, SG, _ = linalg.rsvd(G, k=256, p=a.p, q=a.q, seed=linalg.seed_of("G", shp, sd))
                            fg = linalg.full_svals(G, a.full)
                            shg, shf = linalg.shares(SG, gn2), linalg.shares(fg, gn2)
                            gw.writerow([shp[0], shp[1], sd, repr(gn2), repr(float(SG[0]))] + [repr(shg[k]) for k in KS] +
                                        [repr(float(fg[0]))] + [repr(shf[k]) for k in KS] +
                                        [repr(gn2 / float(fg[0]) ** 2)])
                            full[f"gauss{sd}|{shp[0]}x{shp[1]}"] = fg.float().cpu().numpy()
                            del G
            del W
            rows_f.flush()
            lora_f.flush()
        handles.clear()
        np.savez_compressed(os.path.join(out, f"sigma_{sid}.npz"), **{k.replace(".", "~"): v for k, v in sig.items()})
        if full:
            np.savez_compressed(os.path.join(out, f"full_{sid}.npz"), **{k.replace(".", "~"): v for k, v in full.items()})
        dt_comp = time.time() - t_comp
        summ["steps"][sid] = {"matrices": len(mats), "wait_download_s": round(t_wait, 1), "compute_s": round(dt_comp, 1)}
        log(f"step {sid}: {len(mats)} matrices, waited {t_wait:.0f} s for downloads, computed {dt_comp:.0f} s")
        # delete files no later step needs
        later = {(mbr, f) for _, nd in steps[si + 1:] for mbr, fs in nd.items() for f in fs}
        for mbr, fs in need.items():
            for f in fs:
                if (mbr, f) not in later:
                    store.drop(mbr, f)
        open(done_mark, "w").close()
        json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    summ["wall_s"] = round(time.time() - t_job, 1)
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    open(os.path.join(out, "DONE"), "w").close()
    shutil.rmtree(work, ignore_errors=True)
    log(f"job {a.job} done in {summ['wall_s']:.0f} s")


def selftest():
    """Planted low-rank + noise matrices against numpy-free exact references on the GPU; negative controls."""
    linalg.precision()
    dev = "cuda"
    ok = True
    g = linalg.gen(dev, 7)
    m, n, r = 3000, 1200, 8
    U0, _ = torch.linalg.qr(torch.randn(m, r, device=dev, generator=g))
    V0, _ = torch.linalg.qr(torch.randn(n, r, device=dev, generator=g))
    s0 = torch.linspace(50, 20, r, device=dev)
    N = 0.05 * torch.randn(m, n, device=dev, generator=g)
    M = U0 @ torch.diag(s0) @ V0.T + N
    n2 = linalg.norm2(M)
    Sf = linalg.full_svals(M, "svd")
    Sg = linalg.full_svals(M, "gram")
    U, S, V = linalg.rsvd(M, k=256, p=256, q=8, seed=1)
    e_top = float(((S[:r].double() - Sf[:r]).abs() / Sf[:r]).max())
    e_g = float(((Sg[:256] - Sf[:256]).abs() / Sf[:256]).max())
    sh, shf = linalg.shares(S, n2), linalg.shares(Sf, n2)
    e_sh = max(abs(sh[k] / shf[k] - 1) for k in KS)
    ov = linalg.overlap(U[:, :r], U0)
    ov_rand = linalg.overlap(U[:, :r], linalg.orth(torch.randn(m, r, device=dev, generator=g)))
    print(f"rsvd top-{r} rel err {e_top:.2e}; gram vs svd {e_g:.2e}; share rel err {e_sh:.2e}; overlap planted {ov:.4f}"
          f" (expect ~1), random {ov_rand:.4f} (expect ~{r / m:.4f})")
    ok &= e_top < 1e-4 and e_g < 1e-3 and e_sh < 0.02 and ov > 0.99 and ov_rand < 10 * r / m
    # lowrank_inner against the dense product; negative control: a sign flip must change it
    B, A = torch.randn(m, 4, device=dev, generator=g), torch.randn(4, n, device=dev, generator=g)
    ck = linalg.lowrank_inner(U, S, V, B, A, 2.0)
    dense = float(((U[:, :16] * S[:16]) @ V[:, :16].T * (2.0 * B @ A)).double().sum())
    e_in = abs(float(ck[15]) - dense) / abs(dense)
    neg = abs(float(linalg.lowrank_inner(U, S, V, -B, A, 2.0)[15]) - dense) / abs(dense)
    print(f"lowrank_inner rel err {e_in:.2e}; sign-flip control {neg:.2f} (expect 2)")
    ok &= e_in < 1e-4 and abs(neg - 2) < 1e-3
    fb2 = linalg.frob2_lowrank(B, A)
    e_fb = abs(fb2 - linalg.norm2(B @ A)) / fb2
    ok &= e_fb < 1e-5
    # floor: calibrated norm, entries are multiples of the bf16 step of W (rounded values are bf16)
    W = (0.02 * torch.randn(512, 768, device=dev, generator=g)).to(torch.bfloat16)
    R, s, nr = linalg.floor_matrix(W, 1e-6 * linalg.norm2(W.float()), "t")
    e_n = abs(nr / (1e-6 * linalg.norm2(W.float())) - 1)
    rebf = torch.equal((W.float() + R).to(torch.bfloat16).float(), W.float() + R)
    frac0 = float((R == 0).float().mean())
    print(f"floor norm rel err {e_n:.1e}; W+R is bf16 {rebf}; unchanged share {frac0:.3f}; s {s:.3e}")
    ok &= e_n < 1e-3 and rebf
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    ap.add_argument("--plan", default="olmo_lowrank/plan/spectra_jobs.json")
    ap.add_argument("--work", default="/models/spec")
    ap.add_argument("--out", default="artifacts/olmo_lowrank/spectra")
    ap.add_argument("--p", type=int, default=256)
    ap.add_argument("--q", type=int, default=8)
    ap.add_argument("--full", default="gram", choices=["gram", "svd"])
    ap.add_argument("--lora-dir", default="/workspace/lora")
    ap.add_argument("--inflight", type=int, default=8)
    ap.add_argument("--subset-mod", type=int, default=None,
                    help="full spectra for layers = 0 mod this (default: the plan's subset_mod; 1 = every matrix)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    run_job(a)


if __name__ == "__main__":
    main()
