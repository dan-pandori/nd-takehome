"""Torch-free encoder for the Olmo 3 tokenizer, ASCII text only (run olmo-answeronly). The tokenizer is byte-level BPE
with the cl100k pre-tokenizer regex; for ASCII input, \\p{L} = [A-Za-z] and \\p{N} = [0-9], so Python's `re` suffices.
Used once, to fix the token ids of the inserted wordings (pre-registration); the pod's HF tokenizer re-checks them."""
import json
import re
import sys

sys.path.insert(0, "olmo_transplant")
from tok import TOKJ, _byte_decoder  # noqa: E402

L, N = "A-Za-z", "0-9"
PAT = re.compile(rf"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n{L}{N}]?[{L}]+|[{N}]{{1,3}}| ?[^\s{L}{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+")


class Enc:
    def __init__(self, path=TOKJ):
        tj = json.load(open(path))
        self.vocab = tj["model"]["vocab"]
        ms = tj["model"]["merges"]
        self.rank = {tuple(m.split(" ")) if isinstance(m, str) else tuple(m): i for i, m in enumerate(ms)}
        self.be = {b: c for c, b in _byte_decoder().items()}

    def _bpe(self, word):
        parts = list(word)
        while len(parts) > 1:
            best = min(range(len(parts) - 1), key=lambda i: self.rank.get((parts[i], parts[i + 1]), 1 << 30))
            if (parts[best], parts[best + 1]) not in self.rank:
                break
            parts[best:best + 2] = [parts[best] + parts[best + 1]]
        return [self.vocab[p] for p in parts]

    def encode(self, text):
        assert text.isascii(), "ASCII only"
        out = []
        for m in PAT.finditer(text):
            out += self._bpe("".join(self.be[b] for b in m.group().encode()))
        return out
