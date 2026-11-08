"""Weight-space spot check over HTTP range reads (the VPS cannot hold shards): a subset of shard-2 tensors and the
embedding / unembedding rows of the added tokens, for base main, base stage3-step11000 and RL-Zero-IF step_100,
step_200, step_1800, step_1900, main. Not the executor's full-shard numbers (theirs: 136 tensors of shard 2); this
checks their ordering and ratios on 4 large matrices, and whether the base's rows for ids 100268 / 100269 (<think> /
</think> in RL's tokenizer) look trained.
Output: out/weights.txt, out/weights.json"""
import json
import os
import struct
import time
import urllib.request

import numpy as np

import rv_core as C

CK = {"base": ("allenai/Olmo-3-1025-7B", "main"), "b11000": ("allenai/Olmo-3-1025-7B", "stage3-step11000"),
      "s0100": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_100"), "s0200": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_200"),
      "s1800": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_1800"), "s1900": ("allenai/Olmo-3-7B-RL-Zero-IF", "step_1900"),
      "main": ("allenai/Olmo-3-7B-RL-Zero-IF", "main")}
TENSORS = ["model.layers.16.mlp.down_proj.weight", "model.layers.16.self_attn.q_proj.weight",
           "model.layers.20.mlp.up_proj.weight", "model.layers.20.self_attn.o_proj.weight"]
ROWS = list(range(100256, 100278))
REG = list(range(1000, 1016))


def commit(repo, rev):
    refs = json.load(open(os.path.join(C.BIG, "hf", f"refs_{repo.replace('/', '_')}.json")))
    return next(b["targetCommit"] for b in refs["branches"] if b["name"] == rev)


def rng(url, a, b):
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={a}-{b - 1}"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            assert len(data) == b - a, (len(data), b - a)
            return data
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(5 * (k + 1))
    raise err


HDR = {}


def header(url):
    if url not in HDR:
        n = struct.unpack("<Q", rng(url, 0, 8))[0]
        HDR[url] = (8 + n, json.loads(rng(url, 8, 8 + n)))
    return HDR[url]


def bf16(buf):
    u = np.frombuffer(buf, dtype=np.uint16).astype(np.uint32) << 16
    return u.view(np.float32)


def shard_of(name, label):
    repo, rev = CK[label]
    if not hasattr(shard_of, "idx"):
        shard_of.idx = {}
    if label not in shard_of.idx:
        url = f"https://huggingface.co/{repo}/resolve/{commit(repo, rev)}/model.safetensors.index.json"
        with urllib.request.urlopen(url, timeout=60) as r:
            shard_of.idx[label] = json.load(r)["weight_map"]
    return f"https://huggingface.co/{repo}/resolve/{commit(repo, rev)}/{shard_of.idx[label][name]}"


def tensor(label, name, rows=None):
    url = shard_of(name, label)
    off, h = header(url)
    meta = h[name]
    assert meta["dtype"] == "BF16", meta["dtype"]
    s, e = meta["data_offsets"]
    shape = meta["shape"]
    if rows is None:
        return bf16(rng(url, off + s, off + e)).reshape(shape)
    w = shape[1] * 2
    a, b = rows[0], rows[-1] + 1
    return bf16(rng(url, off + s + a * w, off + s + b * w)).reshape(b - a, shape[1])


def main():
    t0 = time.time()
    pairs = [("main", "s1900"), ("main", "s1800"), ("s1900", "s1800"), ("s0100", "base"), ("s0200", "s0100"),
             ("s0100", "b11000"), ("base", "b11000"), ("main", "base")]
    num = {f"{a}|{b}": 0.0 for a, b in pairs}
    den = dict(num)
    for n in TENSORS:  # one tensor at a time, its first 1,024 rows, all checkpoints (memory)
        T = {lab: tensor(lab, n, list(range(0, 1024))) for lab in CK}
        for a, b in pairs:
            num[f"{a}|{b}"] += float(np.sum((T[a] - T[b]) ** 2))
            den[f"{a}|{b}"] += float(np.sum(T[b] ** 2))
        del T
        print(n, f"{time.time() - t0:.0f}s", flush=True)
    W = {lab: {} for lab in CK}
    res = {"pairs": {}, "rows": {}}
    lines = [f"rel. L2 = ||a - b|| / ||b|| over rows 0-1023 of {len(TENSORS)} shard-2 matrices ({', '.join(TENSORS)})"]
    for a, b in pairs:
        res["pairs"][f"{a}|{b}"] = (num[f"{a}|{b}"] / den[f"{a}|{b}"]) ** 0.5
        lines.append(f"  {a:6s} vs {b:6s}: {res['pairs'][f'{a}|{b}']:.4e}")
    r = res["pairs"]
    lines.append(f"  ratio (s0100 vs b11000) / (s0100 vs base) = {r['s0100|b11000'] / r['s0100|base']:.2f}")
    lines.append(f"  main closer to step_1900 than step_1800: {r['main|s1900'] < r['main|s1800']}")
    # added-token rows
    for lab in ("base", "s0100", "main"):
        E = tensor(lab, "model.embed_tokens.weight", ROWS)
        Er = tensor(lab, "model.embed_tokens.weight", REG)
        Lh = tensor(lab, "lm_head.weight", ROWS)
        Lr = tensor(lab, "lm_head.weight", REG)
        res["rows"][lab] = {"embed": {i: float(np.linalg.norm(x)) for i, x in zip(ROWS, E)},
                            "lm_head": {i: float(np.linalg.norm(x)) for i, x in zip(ROWS, Lh)},
                            "embed_regular_mean": float(np.linalg.norm(Er, axis=1).mean()),
                            "lm_head_regular_mean": float(np.linalg.norm(Lr, axis=1).mean())}
        W[lab]["_E"], W[lab]["_L"] = E, Lh
    names = json.load(open(os.path.join(C.BIG, "hf", "allenai_Olmo-3-7B-RL-Zero-IF@main", "tokenizer.json")))
    nm = {x["id"]: x["content"] for x in names["added_tokens"]}
    lines.append("row norms (embed / lm_head); regular ids 1000-1015 mean: " + ", ".join(
        f"{lab} {res['rows'][lab]['embed_regular_mean']:.3f} / {res['rows'][lab]['lm_head_regular_mean']:.3f}"
        for lab in ("base", "s0100", "main")))
    for k, i in enumerate(ROWS):
        d1 = float(np.linalg.norm(W["s0100"]["_E"][k] - W["base"]["_E"][k]))
        d2 = float(np.linalg.norm(W["main"]["_E"][k] - W["base"]["_E"][k]))
        same = bool(np.array_equal(W["base"]["_E"][k], W["base"]["_E"][0]))
        lines.append(f"  {i} {nm.get(i, '?'):18s} embed base {res['rows']['base']['embed'][i]:.4f} s0100 "
                     f"{res['rows']['s0100']['embed'][i]:.4f} main {res['rows']['main']['embed'][i]:.4f} | lm_head base "
                     f"{res['rows']['base']['lm_head'][i]:.4f} main {res['rows']['main']['lm_head'][i]:.4f} | "
                     f"|d embed| s0100 {d1:.4f} main {d2:.4f} | base row == row 100256: {same}")
    json.dump(res, open(os.path.join(C.OUT, "weights.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "weights.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
