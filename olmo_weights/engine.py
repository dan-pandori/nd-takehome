"""olmo-weights statistics engine: stream one job's checkpoints shard file by shard file and write per-tensor statistics.

A job (manifest/jobs.json) lists members (checkpoint labels) in download order, chains (ordered members with a stage
start), pairs, Gram sets and an optional LoRA comparison. All members of a job share one shard layout, so shard k of
every member holds the same tensors. For each shard k the members' files are downloaded in member order (several in
flight, under a disk cap), each file's sha256 is checked against the manifest, every statistic whose members are all
present is computed, and a file is deleted as soon as nothing later needs it. Only CSV statistics leave the pod.

Arithmetic: bf16 values -> float32 (differences of two bf16 values are exact in float32); sums in float64; Gram
matrices with float64 products.

Outputs in <out>/<job>/shard_<k>/: iv.csv (intervals and pairs), lag.csv, st.csv (against the chain's start),
gram.csv, lora.csv; <out>/<job>/lora_norms.csv; <out>/<job>/files.csv (download / hash log); <out>/<job>/summary.json.
A shard with shard_<k>/DONE is skipped on restart.

Usage: engine.py --job ID [--jobs F] [--ckpts F] [--out D] [--work D] [--device cuda|cpu] [--inflight 6]
                 [--disk-cap-gb 150] [--keep 0] [--local-root D] [--lora-dir D] [--verify 1]
"""
import argparse, csv, hashlib, json, math, os, shutil, sys, threading, time, zlib
from concurrent.futures import ThreadPoolExecutor

import torch
from safetensors import safe_open

LAGS = (1, 2, 3)
N_RANDOM = 8


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


# ------------------------------------------------------------------------------------------------- statistics kernels
def ulp_bf16(a):
    """1 ulp of each bf16 value: 2^(e - 127 - 7) for biased exponent e >= 1; 2^-133 for zero / subnormals."""
    e = (a.view(torch.int16).to(torch.int32) >> 7) & 0xFF
    return torch.ldexp(torch.ones(e.shape, dtype=torch.float32, device=a.device), (e.clamp(min=1) - 134))


def f64sum(x):
    return torch.sum(x, dtype=torch.float64)


class Acc:
    """Per-tensor float64 / int64 accumulators kept on the device until the tensor is finished."""

    def __init__(self, dev):
        self.dev, self.v = dev, {}

    def add(self, key, x):
        if key in self.v:
            self.v[key] = self.v[key] + x
        else:
            self.v[key] = x.clone() if torch.is_tensor(x) else x

    def pop_all(self):
        out = {k: (v.item() if torch.is_tensor(v) and v.numel() == 1 else v) for k, v in self.v.items()}
        self.v = {}
        return out


# ------------------------------------------------------------------------------------------------------ job planning
def plan(job, J):
    """Turn a job into computations. Each computation: dict(kind, needs=[labels], ...). trigger = last needed member
    in download order."""
    order = {m: i for i, m in enumerate(J["members"])}
    comps = []
    for c in J["chains"]:
        mem, s = c["members"], c["start"]
        for i in range(1, len(mem)):
            a, b = mem[i - 1], mem[i]
            comps.append(dict(kind="iv", chain=c["name"], idx=i, a=a, b=b, needs=[a, b]))
            for L in LAGS:
                if i - L >= 1:
                    a2, b2 = mem[i - L - 1], mem[i - L]
                    comps.append(dict(kind="lag", chain=c["name"], idx=i, lag=L, a=a, b=b, a2=a2, b2=b2,
                                      needs=sorted({a, b, a2, b2}, key=order.get)))
            comps.append(dict(kind="st", chain=c["name"], idx=i, s=s, a=a, b=b, needs=sorted({s, a, b}, key=order.get)))
            if J.get("lora") and c["name"] == "rl":
                comps.append(dict(kind="lora", chain=c["name"], idx=i, s=s, b=b, needs=sorted({s, b}, key=order.get)))
    for p in J.get("pairs", []):
        a, b = p
        comps.append(dict(kind="iv", chain="pair", idx=0, a=a, b=b, needs=sorted({a, b}, key=order.get)))
    for gi, g in enumerate(J.get("gram", [])):
        comps.append(dict(kind="gram", set=gi, ref=g[0], others=g[1:], needs=sorted(set(g), key=order.get)))
    for c in comps:
        c["trigger"] = max(order[m] for m in c["needs"])
    last_use = {}
    for c in comps:
        for m in c["needs"]:
            last_use[m] = max(last_use.get(m, -1), c["trigger"])
    return comps, last_use


# ------------------------------------------------------------------------------------------------------- downloader
class Store:
    """Files of the current job: download (or link from a local root), verify, track, delete."""

    def __init__(self, a, ck, job_dir):
        self.a, self.ck = a, ck
        self.lock = threading.Lock()
        self.present = {}        # (label, k) -> path
        self.events = {}         # (label, k) -> threading.Event
        self.bytes_on_disk = 0
        self.flog = open(os.path.join(job_dir, "files.csv"), "a", newline="")
        self.fw = csv.writer(self.flog)
        self.dl_bytes = 0
        self.dl_secs = 0.0

    def path(self, label, k):
        return os.path.join(self.a.work, self.a.job, label.replace("/", "_"), self.ck[label]["files"][k])

    def event(self, key):
        with self.lock:
            return self.events.setdefault(key, threading.Event())

    def fetch(self, label, k):
        c = self.ck[label]
        fn, want, size = c["files"][k], c["sha256"][k], c["sizes"][k]
        dst = self.path(label, k)
        t0 = time.time()
        pre = self.a.prestaged_map.get(label)
        if pre:   # restage.py output: the same tensors re-sharded into the reference layout (bytes checked there)
            src = os.path.join(pre, fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                os.symlink(src, dst)
            rs = {r["file"]: r for r in json.load(open(os.path.join(pre, "restage.json")))["restaged"]}[fn]
            want, size = rs["sha256"], rs["bytes"]
            how = "prestaged"
        elif self.a.local_root:
            src = os.path.join(self.a.local_root, label.replace("/", "_"), fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                os.symlink(src, dst)
            how = "local"
        else:
            from huggingface_hub import hf_hub_download
            for attempt in range(4):
                try:
                    p = hf_hub_download(c["repo"], fn, revision=c["commit"], local_dir=os.path.dirname(dst))
                    assert os.path.abspath(p) == os.path.abspath(dst), (p, dst)
                    break
                except Exception as e:
                    log(f"download retry {attempt} {label} {fn}: {repr(e)[:200]}")
                    time.sleep(20 * (attempt + 1))
            else:
                raise RuntimeError(f"download failed {label} {fn}")
            how = "hub"
        t1 = time.time()
        got = os.path.getsize(dst)
        sha = ""
        if self.a.verify:
            h = hashlib.sha256()
            with open(dst, "rb") as f:
                while True:
                    b = f.read(1 << 24)
                    if not b:
                        break
                    h.update(b)
            sha = h.hexdigest()
            if sha != want or got != size:
                os.remove(dst)
                raise RuntimeError(f"HASH MISMATCH {label} {fn}: {sha} != {want} or {got} != {size}")
        t2 = time.time()
        with self.lock:
            self.present[(label, k)] = dst
            self.bytes_on_disk += got
            if how == "hub":
                self.dl_bytes += got
                self.dl_secs += t1 - t0
            self.fw.writerow([label, c["repo"], c["commit"], fn, got, sha, "ok" if self.a.verify else "unverified",
                              round(t1 - t0, 2), round(t2 - t1, 2), how])
            self.flog.flush()
        self.event((label, k)).set()
        return got / max(t1 - t0, 1e-9)

    def drop(self, label, k):
        with self.lock:
            p = self.present.pop((label, k), None)
            if p is None:
                return
            sz = os.path.getsize(p) if os.path.exists(p) else 0
            self.bytes_on_disk -= sz
        pre = self.a.prestaged_map.get(label)
        if pre:
            src = os.path.realpath(p)
            os.remove(p)
            if not self.a.keep and os.path.exists(src):
                os.remove(src)
        elif not self.a.keep and not self.a.local_root:
            os.remove(p)
            cache = os.path.join(os.path.dirname(p), ".cache", "huggingface", "download",
                                 os.path.basename(p) + ".metadata")
            if os.path.exists(cache):
                os.remove(cache)
        elif self.a.local_root and os.path.islink(p):
            os.remove(p)


# ---------------------------------------------------------------------------------------------------------- LoRA
class Lora:
    """lora_main / lora_ctrl factors and N_RANDOM random rank-16 baselines (Gaussian factors, seeded by tensor name)."""

    def __init__(self, lora_dir, dev):
        self.dev = dev
        self.ad = {}
        self.cache = {}
        for name in ("main", "ctrl"):
            cfg = json.load(open(os.path.join(lora_dir, name, "adapter_config.json")))
            scale = cfg["lora_alpha"] / cfg["r"]
            f = safe_open(os.path.join(lora_dir, name, "adapter_model.safetensors"), framework="pt")
            self.ad[name] = (f, scale, cfg["r"])
        f0 = self.ad["main"][0]
        self.keys = {}
        for k in f0.keys():
            if k.endswith("lora_A.weight"):
                t = k.replace("base_model.model.", "").replace(".lora_A.weight", ".weight")
                self.keys[t] = (k, k.replace("lora_A", "lora_B"))

    def factors(self, tensor):
        """-> list of (name, B [out, r], A [r, in], scale) incl. random baselines; None if not targeted.
        Cached for the tensors of the current shard (clear() at each new shard)."""
        if tensor not in self.keys:
            return None
        if tensor in self.cache:
            return self.cache[tensor]
        ka, kb = self.keys[tensor]
        out = []
        for name, (f, scale, r) in self.ad.items():
            out.append((name, f.get_tensor(kb).float().to(self.dev), f.get_tensor(ka).float().to(self.dev), scale))
        Bm, Am, sm = out[0][1], out[0][2], out[0][3]
        n_main = math.sqrt(max(float(frob2(Bm, Am)) * sm * sm, 0.0))
        for q in range(N_RANDOM):
            g = torch.Generator().manual_seed(zlib.crc32(f"{tensor}|{q}".encode()))
            B = torch.randn(Bm.shape, generator=g).to(self.dev)
            A = torch.randn(Am.shape, generator=g).to(self.dev)
            s = n_main / math.sqrt(float(frob2(B, A)))
            out.append((f"r{q}", B, A, s))
        self.cache[tensor] = out
        return out

    def clear(self):
        self.cache = {}


def frob2(B, A):
    """||B @ A||_F^2 without forming B @ A: sum((B^T B) * (A A^T))."""
    return f64sum((B.double().T @ B.double()) * (A.double() @ A.double().T))


def inner(B1, A1, B2, A2):
    """<B1 A1, B2 A2>_F = sum((B1^T B2) * (A1 A2^T))."""
    return f64sum((B1.double().T @ B2.double()) * (A1.double() @ A2.double().T))


# ------------------------------------------------------------------------------------------------------ GPU cache
class GpuCache:
    """Whole shard files held as bf16 tensors on the device, so a file is read from disk about once. All future uses
    are known (uses[m] = sorted triggers), so eviction is Belady's: drop the cached file whose next use is farthest."""

    def __init__(self, budget, uses, dev):
        self.budget, self.uses, self.dev = budget, uses, dev
        self.data, self.size, self.total = {}, {}, 0
        self.loaded_bytes, self.load_s = 0, 0.0

    def next_use(self, m, j):
        for u in self.uses.get(m, []):
            if u >= j:
                return u
        return None

    def get(self, m):
        return self.data.get(m)

    def offer(self, m, path, j, nbytes):
        if m in self.data or self.budget <= 0:
            return m in self.data
        nu = self.next_use(m, j)
        if nu is None or nbytes > self.budget:
            return False
        while self.total + nbytes > self.budget:
            far = max(self.data, key=lambda x: self.next_use(x, j) if self.next_use(x, j) is not None else 1 << 60)
            fu = self.next_use(far, j)
            if fu is not None and fu <= nu:
                return False
            self.evict(far)
        t0 = time.time()
        with safe_open(path, framework="pt", device=str(self.dev)) as f:
            self.data[m] = {t: f.get_tensor(t) for t in f.keys()}
        self.size[m] = nbytes
        self.total += nbytes
        self.loaded_bytes += nbytes
        self.load_s += time.time() - t0
        return True

    def evict(self, m):
        if m in self.data:
            del self.data[m]
            self.total -= self.size.pop(m)

    def evict_unused(self, j):
        for m in list(self.data):
            if self.next_use(m, j) is None:
                self.evict(m)

    def clear(self):
        for m in list(self.data):
            self.evict(m)


# --------------------------------------------------------------------------------------------------- shard compute
CSV_COLS = {
    "iv": ["chain", "idx", "a", "b", "tensor", "numel", "d2", "na2", "nb2", "n_eq", "n_ulp", "n_nonfinite"],
    "lag": ["chain", "idx", "lag", "tensor", "dot"],
    "st": ["chain", "idx", "s", "b", "tensor", "o2", "n_eq_s", "n_ulp_s", "dot_prev"],
    "gram": ["set", "ref", "members", "tensor", "gram_upper"],
    "lora": ["chain", "idx", "b", "tensor", "o2"] + ["dot_main", "dot_ctrl"] + [f"dot_r{q}" for q in range(N_RANDOM)],
}


def run_trigger(comps, files, dev, chunk_elems, writers, lora, lora_norms, lora_seen, cache):
    """Compute every computation in comps (all needing members whose shard-k files are in `files`). Members held in
    the GPU cache are used from there; the others are read from disk slice by slice."""
    need = sorted({m for c in comps for m in c["needs"]})
    handles = {m: safe_open(files[m], framework="pt") for m in need if cache.get(m) is None}

    def keys_of(m):
        return list(cache.get(m).keys()) if cache.get(m) is not None else list(handles[m].keys())
    names = keys_of(need[0])
    for m in need:
        assert set(keys_of(m)) == set(names), f"tensor sets differ: {m}"
    for t in names:
        sl = {m: (cache.get(m)[t] if cache.get(m) is not None else handles[m].get_slice(t)) for m in need}

        def shp(x):
            return list(x.shape) if torch.is_tensor(x) else list(x.get_shape())

        def dt(x):
            return "BF16" if torch.is_tensor(x) and x.dtype == torch.bfloat16 else (x.get_dtype() if not torch.is_tensor(x) else str(x.dtype))
        shape = shp(sl[need[0]])
        for m in need:
            assert shp(sl[m]) == shape and dt(sl[m]) == "BF16", (m, t, shp(sl[m]), dt(sl[m]))
        rows = shape[0]
        per_row = int(math.prod(shape[1:])) if len(shape) > 1 else 1
        # about 4 * chunk_elems elements across all loaded members (fewer rows when many members are loaded)
        step = max(1, min(rows, (chunk_elems * 4 // max(4, len(need))) // per_row))
        acc = Acc(dev)
        lf = lora.factors(t) if (lora is not None and any(c["kind"] == "lora" for c in comps)) else None
        if lf is not None and t not in lora_seen:
            lora_seen.add(t)
            row = {"tensor": t}
            for (n1, B1, A1, s1) in lf:
                row[f"n2_{n1}"] = float(frob2(B1, A1)) * s1 * s1
            row["dot_main_ctrl"] = float(inner(lf[0][1], lf[0][2], lf[1][1], lf[1][2])) * lf[0][3] * lf[1][3]
            lora_norms.append(row)
        for r0 in range(0, rows, step):
            r1 = min(rows, r0 + step)
            X = {m: (sl[m][r0:r1] if torch.is_tensor(sl[m]) else sl[m][r0:r1].to(dev)) for m in need}
            F = {m: X[m].float() for m in need}
            for ci, c in enumerate(comps):
                k = c["kind"]
                if k == "iv":
                    A, B = X[c["a"]], X[c["b"]]
                    D = F[c["b"]] - F[c["a"]]
                    acc.add((ci, "d2"), f64sum(D * D))
                    acc.add((ci, "na2"), f64sum(F[c["a"]] * F[c["a"]]))
                    acc.add((ci, "nb2"), f64sum(F[c["b"]] * F[c["b"]]))
                    acc.add((ci, "n_eq"), (A.view(torch.int16) == B.view(torch.int16)).sum())
                    acc.add((ci, "n_ulp"), (D.abs() <= ulp_bf16(A)).sum())
                    acc.add((ci, "n_nonfinite"), (~torch.isfinite(F[c["b"]])).sum())
                elif k == "lag":
                    acc.add((ci, "dot"), f64sum((F[c["b"]] - F[c["a"]]) * (F[c["b2"]] - F[c["a2"]])))
                elif k == "st":
                    O = F[c["b"]] - F[c["s"]]
                    acc.add((ci, "o2"), f64sum(O * O))
                    acc.add((ci, "n_eq_s"), (X[c["b"]].view(torch.int16) == X[c["s"]].view(torch.int16)).sum())
                    acc.add((ci, "n_ulp_s"), (O.abs() <= ulp_bf16(X[c["s"]])).sum())
                    acc.add((ci, "dot_prev"), f64sum((F[c["b"]] - F[c["a"]]) * (F[c["a"]] - F[c["s"]])))
                elif k == "gram":
                    R = F[c["ref"]]
                    Y = torch.stack([(F[m] - R).reshape(-1) for m in c["others"]]).double()
                    acc.add((ci, "G"), Y @ Y.T)
                elif k == "lora" and lf is not None:
                    O = (F[c["b"]] - F[c["s"]]).reshape(r1 - r0, -1)
                    acc.add((ci, "o2"), f64sum(O * O))
                    for (n1, B1, A1, s1) in lf:
                        # <O, s B A> over these rows = s * sum((B[rows]^T O) * A)
                        acc.add((ci, n1), f64sum((B1[r0:r1].T @ O) * A1) * s1)
            del X, F
        vals = acc.pop_all()
        for ci, c in enumerate(comps):
            k = c["kind"]
            if k == "iv":
                writers["iv"].writerow([c["chain"], c["idx"], c["a"], c["b"], t, rows * per_row]
                                       + [repr(float(vals[(ci, x)])) for x in ("d2", "na2", "nb2")]
                                       + [int(vals[(ci, x)]) for x in ("n_eq", "n_ulp", "n_nonfinite")])
            elif k == "lag":
                writers["lag"].writerow([c["chain"], c["idx"], c["lag"], t, repr(float(vals[(ci, "dot")]))])
            elif k == "st":
                writers["st"].writerow([c["chain"], c["idx"], c["s"], c["b"], t, repr(float(vals[(ci, "o2")])),
                                        int(vals[(ci, "n_eq_s")]), int(vals[(ci, "n_ulp_s")]),
                                        repr(float(vals[(ci, "dot_prev")]))])
            elif k == "gram":
                G = vals[(ci, "G")].cpu().numpy()
                iu = [repr(float(G[i, j])) for i in range(G.shape[0]) for j in range(i, G.shape[0])]
                writers["gram"].writerow([c["set"], c["ref"], "|".join(c["others"]), t, " ".join(iu)])
            elif k == "lora" and lf is not None:
                writers["lora"].writerow([c["chain"], c["idx"], c["b"], t, repr(float(vals[(ci, "o2")]))]
                                         + [repr(float(vals[(ci, n)])) for n in ["main", "ctrl"] +
                                            [f"r{q}" for q in range(N_RANDOM)]])


# ----------------------------------------------------------------------------------------------------------- main
def cpu_quota():
    """CPUs this container may use (cgroup v2 cpu.max quota / period), capped by os.cpu_count()."""
    n = os.cpu_count() or 1
    try:
        q, per = open("/sys/fs/cgroup/cpu.max").read().split()
        if q != "max":
            n = min(n, max(1, int(int(q) / int(per))))
    except Exception:
        pass
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--jobs", default="olmo_weights/manifest/jobs.json")
    ap.add_argument("--ckpts", default="olmo_weights/manifest/checkpoints.csv")
    ap.add_argument("--out", default="artifacts/olmo_weights/stats")
    ap.add_argument("--work", default="/workspace/dl")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--inflight", type=int, default=6)
    ap.add_argument("--disk-cap-gb", type=float, default=150)
    ap.add_argument("--chunk-melems", type=float, default=32)
    ap.add_argument("--keep", type=int, default=0)
    ap.add_argument("--local-root", default="")
    ap.add_argument("--lora-dir", default="/workspace/lora")
    ap.add_argument("--verify", type=int, default=1)
    ap.add_argument("--shards", default="", help="comma list of shard indices to run (default all)")
    ap.add_argument("--gpu-cache-gb", type=float, default=-1, help="default: 0.7 x device memory (0 on CPU)")
    ap.add_argument("--prestaged", action="append", default=[],
                    help="LABEL=DIR: take LABEL's shard files from DIR (restage.py output, checked against restage.json)")
    a = ap.parse_args()
    a.prestaged_map = dict(x.split("=", 1) for x in a.prestaged)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_num_threads(cpu_quota())
    J = json.load(open(a.jobs))[a.job]
    ck = {}
    for r in csv.DictReader(open(a.ckpts)):
        r["files"] = r["files"].split(";")
        r["sha256"] = r["sha256"].split(";")
        r["sizes"] = [int(x) for x in r["sizes"].split(";")]
        ck[r["label"]] = r
    members = J["members"]
    nfiles = {len(ck[m]["files"]) for m in members}
    assert len(nfiles) == 1, f"members differ in shard count: {nfiles}"
    nfiles = nfiles.pop()
    for m in members:
        assert ck[m]["files"] == ck[members[0]]["files"], f"shard names differ: {m}"
    comps, last_use = plan(a.job, J)
    order = {m: i for i, m in enumerate(members)}
    job_dir = os.path.join(a.out, a.job)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    dev = torch.device(a.device)
    lora = Lora(a.lora_dir, dev) if J.get("lora") else None
    store = Store(a, ck, job_dir)
    shards = [int(x) for x in a.shards.split(",")] if a.shards else list(range(nfiles))
    # live-set check: the disk cap must hold the largest set of files alive at once, plus the in-flight downloads
    max_live = 0
    for k in shards:
        for j in range(len(members)):
            live = [m for m in members if order[m] <= j <= last_use.get(m, -1)]
            max_live = max(max_live, sum(ck[m]["sizes"][k] for m in live))
    biggest = max(ck[m]["sizes"][k] for m in members for k in shards)
    cap = a.disk_cap_gb * 1e9
    assert max_live + biggest <= cap, f"disk cap {a.disk_cap_gb} GB < live set {max_live / 1e9:.1f} GB + one file"
    log(f"job {a.job}: {len(members)} members, {nfiles} shards, {len(comps)} computations per shard, device {dev}, "
        f"max live set {max_live / 1e9:.1f} GB, cap {a.disk_cap_gb} GB, inflight {a.inflight}")
    t_start = time.time()
    t_compute = 0.0
    lora_norms, lora_seen = [], set()
    uses = {}
    for c in comps:
        for m in c["needs"]:
            uses.setdefault(m, set()).add(c["trigger"])
    uses = {m: sorted(v) for m, v in uses.items()}
    if a.gpu_cache_gb < 0:
        a.gpu_cache_gb = 0.7 * torch.cuda.get_device_properties(0).total_memory / 1e9 if dev.type == "cuda" else 0
    cache = GpuCache(a.gpu_cache_gb * 1e9, uses, dev)
    log(f"gpu cache {a.gpu_cache_gb:.1f} GB")
    todo = [k for k in shards if not os.path.exists(os.path.join(job_dir, f"shard_{k}", "DONE"))]
    queue = [(k, m) for k in todo for m in members]
    pool = ThreadPoolExecutor(max_workers=a.inflight)
    pending = {}
    qi = [0]
    reserved = [0]
    rlock = threading.Lock()

    def pump():
        """Start downloads in queue order while the disk cap and the in-flight limit allow."""
        while qi[0] < len(queue):
            k, m = queue[qi[0]]
            sz = ck[m]["sizes"][k]
            with rlock:
                inflight = sum(1 for f in pending.values() if not f.done())
                if inflight >= a.inflight or store.bytes_on_disk + reserved[0] + sz > cap:
                    return
                reserved[0] += sz

            def job(k=k, m=m, sz=sz):
                try:
                    return store.fetch(m, k)
                finally:
                    with rlock:
                        reserved[0] -= sz
            pending[(k, m)] = pool.submit(job)
            qi[0] += 1

    if not a.local_root and not a.keep:   # leftovers of an interrupted run of this job are not counted on disk
        shutil.rmtree(os.path.join(a.work, a.job), ignore_errors=True)
    for k in todo:
        if lora is not None:
            lora.clear()
        cache.clear()
        sdir = os.path.join(job_dir, f"shard_{k}")
        os.makedirs(sdir, exist_ok=True)
        fh = {x: open(os.path.join(sdir, f"{x}.csv"), "w", newline="") for x in CSV_COLS}
        writers = {x: csv.writer(f) for x, f in fh.items()}
        for x, w in writers.items():
            w.writerow(CSV_COLS[x])
        for j, m in enumerate(members):
            while True:
                pump()
                f = pending.get((k, m))
                if f is not None and f.done():
                    f.result()   # re-raises a download / hash failure
                    break
                time.sleep(0.2)
            cache.offer(m, store.present[(m, k)], j, ck[m]["sizes"][k])
            ready = [c for c in comps if c["trigger"] == j]
            if ready:
                files = {x: store.present[(x, k)] for c in ready for x in c["needs"]}
                t0 = time.time()
                for x in sorted(files, key=lambda x: cache.next_use(x, j)):
                    cache.offer(x, files[x], j, ck[x]["sizes"][k])
                run_trigger(ready, files, dev, int(a.chunk_melems * 1e6), writers, lora, lora_norms, lora_seen, cache)
                if dev.type == "cuda":
                    torch.cuda.synchronize()
                t_compute += time.time() - t0
            cache.evict_unused(j + 1)
            for x in members:
                if last_use.get(x, -1) == j or (x == m and x not in last_use):
                    store.drop(x, k)
            if (members.index(m) + 1) % 10 == 0 or j == len(members) - 1:
                el = time.time() - t_start
                log(f"shard {k} member {j + 1}/{len(members)} {m}: downloaded {store.dl_bytes / 1e9:.1f} GB "
                    f"({store.dl_bytes / 1e9 / max(el, 1):.2f} GB/s wall), compute {t_compute:.0f} s, "
                    f"disk {store.bytes_on_disk / 1e9:.1f} GB, gpu cache {cache.total / 1e9:.1f} GB "
                    f"(loaded {cache.loaded_bytes / 1e9:.0f} GB in {cache.load_s:.0f} s)")
        for f in fh.values():
            f.close()
        open(os.path.join(sdir, "DONE"), "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
        pump()
    pool.shutdown(wait=True)
    if lora is not None and lora_norms:
        cols = sorted({k for r in lora_norms for k in r}, key=lambda x: (x != "tensor", x))
        mode = "a" if os.path.exists(os.path.join(job_dir, "lora_norms.csv")) else "w"
        with open(os.path.join(job_dir, "lora_norms.csv"), mode, newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            if mode == "w":
                w.writeheader()
            for r in lora_norms:
                w.writerow(r)
    wall = time.time() - t_start
    summ = dict(job=a.job, members=len(members), shards_run=todo, wall_s=round(wall, 1), compute_s=round(t_compute, 1),
                downloaded_bytes=store.dl_bytes, download_thread_s=round(store.dl_secs, 1),
                gpu_cache_gb=round(a.gpu_cache_gb, 1), cache_loaded_bytes=cache.loaded_bytes,
                cache_load_s=round(cache.load_s, 1),
                gb_per_s_wall=round(store.dl_bytes / 1e9 / max(wall, 1), 3), device=str(dev),
                gpu=torch.cuda.get_device_name(0) if dev.type == "cuda" else "",
                torch=torch.__version__, finished=time.strftime("%FT%TZ", time.gmtime()))
    prev = os.path.join(job_dir, "summary.json")
    runs = json.load(open(prev))["runs"] if os.path.exists(prev) else []
    json.dump({"runs": runs + [summ]}, open(prev, "w"), indent=1)
    log("DONE", json.dumps(summ))


if __name__ == "__main__":
    main()
