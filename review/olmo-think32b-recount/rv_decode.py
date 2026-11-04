"""Decode check (reviewer): stored text == tokenizer.decode(ids, skip_special_tokens=True) for every sample;
'</think>' is not a special token (so the RL reward saw it); the prompt the olmo_thinker template builds."""
import base64, glob, gzip, json, os, sys
import numpy as np
from tokenizers import Tokenizer
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
tok = Tokenizer.from_file(os.path.join(HERE, "out", "tokcfg", "tokenizer.json"))
cfg = json.load(open(os.path.join(HERE, "out", "tokcfg", "dpo_tokenizer_config.json")))
special = {int(k): v["content"] for k, v in cfg["added_tokens_decoder"].items() if v.get("special")}
nonspecial_added = {int(k): v["content"] for k, v in cfg["added_tokens_decoder"].items() if not v.get("special")}
th = [t for t in ("<think>", "</think>") ]
print("think tokens:", {t: tok.token_to_id(t) for t in th}, "special?", [tok.token_to_id(t) in special for t in th])
print("eos 100257 =", tok.id_to_token(100257), "special:", 100257 in special)
n = bad = 0; ex = []
for f in sorted(glob.glob(os.path.join(ROOT, "artifacts", "olmo32", "samples", "*.jsonl.gz"))):
    with gzip.open(f, "rt") as g:
        for ln in g:
            r = json.loads(ln)
            ids = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32).tolist()
            t = tok.decode(ids, skip_special_tokens=True)
            n += 1
            if t != r["text"]:
                bad += 1
                if len(ex) < 5:
                    ex.append((r["job"], r["pid"], r["chunk"], r["i"], len(t), len(r["text"])))
print(f"decoded {n}: text mismatches {bad}", ex)
