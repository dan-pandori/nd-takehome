"""Reviewer (olmo-weights): recompute a seeded sample of intervals from the raw released checkpoints, on a pod.

Independent of olmo_weights/engine.py: own safetensors header parser and byte reader (numpy), bf16 -> float32 by bit
shift, all arithmetic in float64, ulp from the bf16 bit increment, LoRA products formed explicitly (2 * B @ A in float64), own random
rank-16 baselines (own seeds). Whole checkpoints are downloaded (any shard layout works, since tensors are found by
name in each file's own header), sha256-checked with hashlib against the plan (= the executor's manifest), and deleted
after their last task.

Per triple task (a2 -> a -> b, stage start s), per tensor:
  iv  for (a2 -> a) and (a -> b): numel, d2, na2, nb2, n_eq, n_ulp(<= 1 ulp of the earlier value), n_nonfinite
  lag1: <b - a, a - a2>
  st  for a and b against s: o2 = ||x - s||^2, n_eq_s, n_ulp_s (ulp of s), dot_prev = <x - x_prev, x_prev - s>
Per lora task (s = 32B/dpo, b = 32B/rl/2300), per tensor: st row (all tensors); per LoRA-targeted matrix: o2, n2 and
<b - s, dW> for dW = 2 B A of main and ctrl, and 8 Gaussian rank-16 baselines scaled to ||dW_main||.
Usage: python rv_recompute.py plan.json OUTDIR [--dl /root/rvdl] [--cap-gb 450] [--inflight 8] [--lora-dir D]
"""
import argparse, hashlib, json, os, shutil, struct, threading, time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch

CHUNK = 1 << 26          # elements per row-chunk per checkpoint


def now():
    return time.strftime("%H:%M:%S", time.gmtime())


def header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    base = 8 + n
    out = {}
    for k, v in h.items():
        if k == "__metadata__":
            continue
        s, e = v["data_offsets"]
        out[k] = dict(path=path, dtype=v["dtype"], shape=v["shape"], off=base + s, nbytes=e - s)
    return out


def read_rows(t, r0, r1, dev):
    """rows r0:r1 of tensor t (bf16) -> float64 values on dev, plus the raw 16-bit patterns (int16 on dev).
    bf16 bits b -> float32 bits b << 16, done as sign-extended int32 * 65536 (no overflow) and a bit view."""
    shape = t["shape"]
    per_row = int(np.prod(shape[1:])) if len(shape) > 1 else 1
    cnt = (r1 - r0) * per_row
    raw = np.fromfile(t["path"], dtype=np.int16, count=cnt, offset=t["off"] + 2 * r0 * per_row)
    assert raw.size == cnt
    bits = torch.from_numpy(raw).to(dev)
    f32 = (bits.to(torch.int32) * 65536).view(torch.float32)
    return f32.double(), bits


def ulp_bits(bits):
    """1 ulp of each bf16 value, from its 16-bit pattern (int16 tensor): value(|b| + 1) - value(|b|) on the magnitude
    bits, exact in float64. Gives 2^(E - 7) for normal values and 2^-133 for zero and subnormals.
    (A frexp / torch.ldexp version was dropped: torch.ldexp in float64 on CUDA returns 2^k minus one float64 ulp on
    large tensors, which the self-test caught; the engine's float32 ldexp was checked exact on CUDA.)"""
    m = bits.to(torch.int32) & 0x7FFF
    lo = (m * 65536).view(torch.float32).double()
    hi = ((m + 1) * 65536).view(torch.float32).double()
    return hi - lo


class Downloader:
    def __init__(self, plan, dl, cap, inflight, log):
        self.plan, self.dl, self.cap, self.log = plan, dl, cap, log
        self.cond = threading.Condition()
        self.on_disk = 0
        self.reserved = 0
        self.present = {}
        self.records = []
        self.pool = ThreadPoolExecutor(max_workers=inflight)
        self.futs = {}

    def path(self, label, fn):
        return os.path.join(self.dl, label.replace("/", "_"), fn)

    def queue(self, labels):
        for lab in labels:
            c = self.plan["checkpoints"][lab]
            for fn, sha, sz in zip(c["files"], c["sha256"], c["sizes"]):
                if (lab, fn) not in self.futs:
                    self.futs[(lab, fn)] = self.pool.submit(self._get, lab, c, fn, sha, sz)

    def _get(self, lab, c, fn, sha, sz):
        from huggingface_hub import hf_hub_download
        with self.cond:
            while self.on_disk + self.reserved + sz > self.cap:
                self.cond.wait(5)
            self.reserved += sz
        dst = self.path(lab, fn)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        t0 = time.time()
        for attempt in range(5):
            try:
                p = hf_hub_download(c["repo"], fn, revision=c["commit"], local_dir=os.path.dirname(dst))
                break
            except Exception as e:
                self.log(f"retry {attempt} {lab} {fn}: {repr(e)[:160]}")
                time.sleep(20 * (attempt + 1))
        else:
            raise RuntimeError(f"download failed {lab} {fn}")
        t1 = time.time()
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 24), b""):
                h.update(b)
        got, size = h.hexdigest(), os.path.getsize(p)
        t2 = time.time()
        rec = dict(label=lab, file=fn, commit=c["commit"], sha256=got, bytes=size, sha_ok=got == sha,
                   size_ok=size == sz, dl_s=round(t1 - t0, 2), sha_s=round(t2 - t1, 2))
        with self.cond:
            self.reserved -= sz
            self.on_disk += size
            self.present[(lab, fn)] = p
            self.records.append(rec)
            self.cond.notify_all()
        if not (rec["sha_ok"] and rec["size_ok"]):
            raise RuntimeError(f"HASH MISMATCH {rec}")
        return p

    def wait(self, lab):
        c = self.plan["checkpoints"][lab]
        return [self.futs[(lab, fn)].result() for fn in c["files"]]

    def drop(self, lab):
        c = self.plan["checkpoints"][lab]
        d = os.path.join(self.dl, lab.replace("/", "_"))
        freed = 0
        for fn in c["files"]:
            p = self.present.pop((lab, fn), None)
            if p and os.path.exists(p):
                freed += os.path.getsize(p)
        shutil.rmtree(d, ignore_errors=True)
        with self.cond:
            self.on_disk -= freed
            self.cond.notify_all()


def index_ckpt(paths):
    idx = {}
    for p in paths:
        for k, v in header(p).items():
            assert k not in idx, f"tensor {k} in two files"
            idx[k] = v
    return idx


def triple(task, idx, dev):
    a2, a, b, s = (idx[task[k]] for k in ("a2", "a", "b", "s"))
    names = sorted(a)
    for m in (a2, b, s):
        assert sorted(m) == names, "tensor sets differ"
    rows_out = []
    for t in names:
        shp = a[t]["shape"]
        for m in (a2, b, s):
            assert m[t]["shape"] == shp and m[t]["dtype"] == "BF16", (t, m[t]["shape"], m[t]["dtype"])
        assert a[t]["dtype"] == "BF16"
        rows = shp[0] if shp else 1
        per_row = int(np.prod(shp[1:])) if len(shp) > 1 else 1
        step = max(1, CHUNK // per_row)
        z = torch.zeros((), dtype=torch.float64, device=dev)
        acc = {k: z.clone() for k in ("d2_1", "na2_1", "nb2_1", "d2_2", "nb2_2", "lag1", "o2_a", "o2_b",
                                      "dp_a", "dp_b")}
        cnt = {k: 0 for k in ("eq_1", "ulp_1", "nf_1", "eq_2", "ulp_2", "nf_2", "eqs_a", "ulps_a", "eqs_b", "ulps_b")}
        for r0 in range(0, rows, step):
            r1 = min(rows, r0 + step)
            X2, B2 = read_rows(a2[t], r0, r1, dev)
            XA, BA = read_rows(a[t], r0, r1, dev)
            XB, BB = read_rows(b[t], r0, r1, dev)
            XS, BS = read_rows(s[t], r0, r1, dev)
            D1, D2 = XA - X2, XB - XA            # interval idx-1 (a2 -> a) and idx (a -> b)
            acc["d2_1"] += (D1 * D1).sum(); acc["na2_1"] += (X2 * X2).sum(); acc["nb2_1"] += (XA * XA).sum()
            acc["d2_2"] += (D2 * D2).sum(); acc["nb2_2"] += (XB * XB).sum()
            acc["lag1"] += (D2 * D1).sum()
            OA, OB = XA - XS, XB - XS
            acc["o2_a"] += (OA * OA).sum(); acc["o2_b"] += (OB * OB).sum()
            acc["dp_a"] += (D1 * (X2 - XS)).sum(); acc["dp_b"] += (D2 * OA).sum()
            cnt["eq_1"] += int((B2 == BA).sum()); cnt["ulp_1"] += int((D1.abs() <= ulp_bits(B2)).sum())
            cnt["nf_1"] += int((~torch.isfinite(XA)).sum())
            cnt["eq_2"] += int((BA == BB).sum()); cnt["ulp_2"] += int((D2.abs() <= ulp_bits(BA)).sum())
            cnt["nf_2"] += int((~torch.isfinite(XB)).sum())
            us = ulp_bits(BS)
            cnt["eqs_a"] += int((BA == BS).sum()); cnt["ulps_a"] += int((OA.abs() <= us).sum())
            cnt["eqs_b"] += int((BB == BS).sum()); cnt["ulps_b"] += int((OB.abs() <= us).sum())
            del X2, XA, XB, XS, B2, BA, BB, BS, D1, D2, OA, OB, us
        r = {k: float(v) for k, v in acc.items()}
        r.update(cnt)
        r["tensor"], r["numel"], r["shape"] = t, rows * per_row, shp
        rows_out.append(r)
    return rows_out


def pair(task, idx, dev):
    a, b = idx[task["a"]], idx[task["b"]]
    names = sorted(a)
    assert sorted(b) == names, "tensor sets differ"
    out = []
    for t in names:
        shp = a[t]["shape"]
        assert b[t]["shape"] == shp and a[t]["dtype"] == b[t]["dtype"] == "BF16"
        rows = shp[0] if shp else 1
        per_row = int(np.prod(shp[1:])) if len(shp) > 1 else 1
        step = max(1, CHUNK // per_row)
        d2 = na2 = nb2 = 0.0
        eq = ulp = nf = 0
        for r0 in range(0, rows, step):
            r1 = min(rows, r0 + step)
            XA, BA = read_rows(a[t], r0, r1, dev)
            XB, BB = read_rows(b[t], r0, r1, dev)
            D = XB - XA
            d2 += float((D * D).sum()); na2 += float((XA * XA).sum()); nb2 += float((XB * XB).sum())
            eq += int((BA == BB).sum()); ulp += int((D.abs() <= ulp_bits(BA)).sum()); nf += int((~torch.isfinite(XB)).sum())
            del XA, XB, BA, BB, D
        out.append(dict(tensor=t, numel=rows * per_row, shape=shp, d2=d2, na2=na2, nb2=nb2, n_eq=eq, n_ulp=ulp,
                        n_nonfinite=nf))
    return out


def lora_task(task, idx, dev, lora_dir):
    s, b = idx[task["s"]], idx[task["b"]]
    names = sorted(s)
    assert sorted(b) == names
    ad = {}
    for nm in ("main", "ctrl"):
        cfg = json.load(open(os.path.join(lora_dir, nm, "adapter_config.json")))
        assert not cfg.get("use_rslora") and not cfg.get("use_dora")
        scale = cfg["lora_alpha"] / cfg["r"]
        ad[nm] = (header(os.path.join(lora_dir, nm, "adapter_model.safetensors")), scale)

    def lora_factor(nm, key):
        h = ad[nm][0][key]
        assert h["dtype"] == "F32"
        arr = np.fromfile(h["path"], dtype=np.float32, count=h["nbytes"] // 4, offset=h["off"])
        return torch.from_numpy(arr.reshape(h["shape"])).to(dev).double()

    st_rows, lo_rows = [], []
    for ti, t in enumerate(names):
        shp = s[t]["shape"]
        assert b[t]["shape"] == shp and s[t]["dtype"] == b[t]["dtype"] == "BF16"
        rows = shp[0] if shp else 1
        per_row = int(np.prod(shp[1:])) if len(shp) > 1 else 1
        key = "base_model.model." + t.replace(".weight", ".lora_A.weight")
        targeted = key in ad["main"][0]
        if targeted:
            dW = {}
            for nm in ("main", "ctrl"):
                A = lora_factor(nm, key)
                B = lora_factor(nm, key.replace("lora_A", "lora_B"))
                assert A.shape[0] == 16 and B.shape[1] == 16 and B.shape[0] == shp[0] and A.shape[1] == per_row
                dW[nm] = ad[nm][1] * (B @ A)
            nmain = float(torch.sqrt((dW["main"] * dW["main"]).sum()))
            for q in range(8):
                g = torch.Generator(device=dev).manual_seed(20261125 * 1000 + ti * 10 + q)
                B = torch.randn((shp[0], 16), generator=g, device=dev, dtype=torch.float64)
                A = torch.randn((16, per_row), generator=g, device=dev, dtype=torch.float64)
                R = B @ A
                dW[f"q{q}"] = R * (nmain / float(torch.sqrt((R * R).sum())))
                del R
        step = max(1, CHUNK // per_row)
        o2 = torch.zeros((), dtype=torch.float64, device=dev)
        dots = {k: torch.zeros((), dtype=torch.float64, device=dev) for k in (dW if targeted else {})}
        eq = ulp = 0
        for r0 in range(0, rows, step):
            r1 = min(rows, r0 + step)
            XS, BS = read_rows(s[t], r0, r1, dev)
            XB, BB = read_rows(b[t], r0, r1, dev)
            O = XB - XS
            o2 += (O * O).sum()
            eq += int((BS == BB).sum()); ulp += int((O.abs() <= ulp_bits(BS)).sum())
            if targeted:
                O2d = O.reshape(r1 - r0, per_row)
                for k in dots:
                    dots[k] += (O2d * dW[k][r0:r1]).sum()
            del XS, XB, BS, BB, O
        st_rows.append(dict(tensor=t, numel=rows * per_row, o2=float(o2), n_eq_s=eq, n_ulp_s=ulp))
        if targeted:
            r = dict(tensor=t, o2=float(o2))
            for k in dW:
                r[f"n2_{k}"] = float((dW[k] * dW[k]).sum())
                r[f"dot_{k}"] = float(dots[k])
            r["dot_main_ctrl"] = float((dW["main"] * dW["ctrl"]).sum())
            lo_rows.append(r)
            del dW
    return st_rows, lo_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("out")
    ap.add_argument("--dl", default="/root/rvdl")
    ap.add_argument("--cap-gb", type=float, default=450)
    ap.add_argument("--inflight", type=int, default=8)
    ap.add_argument("--lora-dir", default="/workspace/nd-takehome/rvlora")
    a = ap.parse_args()
    torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(a.out, exist_ok=True)
    plan = json.load(open(a.plan))
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logf = open(os.path.join(a.out, "rv_recompute.log"), "a")

    def log(*x):
        line = " ".join(str(y) for y in (now(),) + x)
        print(line, flush=True)
        logf.write(line + "\n"); logf.flush()

    tasks = plan["tasks"]
    keys = lambda t: [t[k] for k in ("a2", "a", "b", "s") if k in t]
    last = {}
    for i, t in enumerate(tasks):
        for m in keys(t):
            last[m] = i
    D = Downloader(plan, a.dl, a.cap_gb * 1e9, a.inflight, log)
    order = []
    for t in tasks:
        for m in keys(t):
            if m not in order:
                order.append(m)
    D.queue(order)
    T0 = time.time()
    log(f"start: {len(tasks)} tasks, {len(order)} checkpoints, device {dev}")
    timing = []
    for i, t in enumerate(tasks):
        tw = time.time()
        idx = {m: index_ckpt(D.wait(m)) for m in keys(t)}
        tc = time.time()
        log(f"task {i} {t['kind']} {t.get('job')} {t.get('chain')} idx {t.get('idx')}: files ready after "
            f"{tc - tw:.0f} s wait")
        if t["kind"] == "triple":
            res = dict(task=t, rows=triple(t, idx, dev))
        elif t["kind"] == "pair":
            res = dict(task=t, rows=pair(t, idx, dev))
        else:
            st_rows, lo_rows = lora_task(t, idx, dev, a.lora_dir)
            res = dict(task=t, st_rows=st_rows, lora_rows=lo_rows)
        if dev.type == "cuda":
            torch.cuda.synchronize()
        te = time.time()
        json.dump(res, open(os.path.join(a.out, f"task_{i}.json"), "w"))
        timing.append(dict(task=i, wait_s=round(tc - tw, 1), compute_s=round(te - tc, 1)))
        log(f"task {i} done: compute {te - tc:.0f} s")
        for m in keys(t):
            if last[m] == i:
                D.drop(m)
    D.pool.shutdown(wait=True)
    summ = dict(wall_s=round(time.time() - T0, 1), timing=timing, files=D.records,
                downloaded_bytes=sum(r["bytes"] for r in D.records),
                all_sha_ok=all(r["sha_ok"] and r["size_ok"] for r in D.records),
                gpu=torch.cuda.get_device_name(0) if dev.type == "cuda" else "", torch=torch.__version__,
                finished=time.strftime("%FT%TZ", time.gmtime()))
    json.dump(summ, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
    log("ALL DONE", json.dumps({k: v for k, v in summ.items() if k != "files"}))
    open(os.path.join(a.out, "DONE"), "w").write(summ["finished"] + "\n")


if __name__ == "__main__":
    main()
