"""Local checkpoint access (pod side): tensor -> shard file from the files' own safetensors headers (not the index,
which olmo-weights found can describe another layout), the 448 / 224 attention and MLP matrices, sha256 checks."""
import glob
import hashlib
import os

from safetensors import safe_open

TYPES = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
GROUP = {"q_proj": "self_attn", "k_proj": "self_attn", "v_proj": "self_attn", "o_proj": "self_attn",
         "gate_proj": "mlp", "up_proj": "mlp", "down_proj": "mlp"}


def mat_name(layer, t):
    return f"model.layers.{layer}.{GROUP[t]}.{t}.weight"


def matrices(n_layers):
    """The attention and MLP matrices in layer-major order: (layer, type, tensor name)."""
    return [(i, t, mat_name(i, t)) for i in range(n_layers) for t in TYPES]


class Ckpt:
    """A checkpoint directory of *.safetensors files; get(name, dev) -> bf16 tensor on dev."""

    def __init__(self, d):
        self.dir = d
        self.where = {}
        for f in sorted(glob.glob(os.path.join(d, "*.safetensors"))):
            with safe_open(f, framework="pt") as h:
                for k in h.keys():
                    assert k not in self.where, f"{k} in two files of {d}"
                    self.where[k] = f
        self.handles = {}

    def n_layers(self):
        return 1 + max(int(k.split(".")[2]) for k in self.where if k.startswith("model.layers."))

    def get(self, name, dev="cpu"):
        f = self.where[name]
        if f not in self.handles:
            self.handles[f] = safe_open(f, framework="pt", device="cpu")
        return self.handles[f].get_tensor(name).to(dev)

    def close(self):
        self.handles = {}


def sha256_file(path, bufsize=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
