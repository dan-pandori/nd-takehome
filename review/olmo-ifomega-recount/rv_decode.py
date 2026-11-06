"""Storage checks on every stored sample: text == tokenizer.decode(ids, skip_special_tokens=True) with the checkpoints'
shared tokenizer.json (allenai/Olmo-3-32B-Think-DPO @ main, blob 5fe1721279, identical at all four revisions);
len(ids) == n_tok; finish == 'length' iff n_tok == 32768 (and last id != EOS); finish == 'stop' -> last id == EOS 100257.
Output: out/decode_check.txt"""
import base64
import json
import os
from collections import Counter

import numpy as np
from tokenizers import Tokenizer

import rv_core as C

TOK = Tokenizer.from_file(os.path.join(C.BIG, "tok", "tokenizer.json"))
EOS = 100257


def main():
    tot = Counter()
    bad = []
    for job in C.jobs():
        for r in C.iter_rows(job):
            ids = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32).tolist()
            tot["rows"] += 1
            tot["tokens"] += len(ids)
            if len(ids) != r["n_tok"]:
                tot["len_mismatch"] += 1
            if r["finish"] == "length":
                tot["length"] += 1
                if len(ids) != C.CAP:
                    tot["length_not_cap"] += 1
            elif r["finish"] == "stop":
                tot["stop"] += 1
                if not ids or ids[-1] != EOS:
                    tot["stop_without_eos"] += 1
                if len(ids) >= C.CAP:
                    tot["stop_at_cap"] += 1
            else:
                tot["finish_other"] += 1
            if TOK.decode(ids, skip_special_tokens=True) != r["text"]:
                tot["text_mismatch"] += 1
                if len(bad) < 20:
                    bad.append((job, r["pid"], r["chunk"], r["i"]))
    lines = [json.dumps(dict(tot))] + [json.dumps(b) for b in bad]
    open(os.path.join(C.OUT, "decode_check.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
