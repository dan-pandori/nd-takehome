"""Provenance of the Part-2 draws (my own code): (1) prompt token ids rebuilt from MY rendering of the olmo_thinker
template (system "You are a helpful AI assistant.", user = the upstream prompt, assistant + "<think>") and the DPO
tokenizer.json (tokenizers library), against every meta's prompt_sha256_by_pid / prompt_tokens_by_pid and every row's
prompt_tokens; (2) decoding settings of every arm and stored endpoint job; (3) a hand look at the template boundary;
(4) stored endpoint files vs my earlier bucket copies (sha256). -> out/provenance.json, out/provenance.txt"""
import gzip
import hashlib
import json
from pathlib import Path

from tokenizers import Tokenizer

from rvr_core import ALL_JOBS, ART, OUT, RAW, TOKJ, Pieces, Tee, iter_job, sha_int32, unb64, upstream_record

SYSTEM = "You are a helpful AI assistant."
METAS = {**{p.stem: p for p in (ART / "meta").glob("*.json") if p.stem != "f448_check"},
         "B_s2300": Path.home() / "review/oifc_rv/bucket_copy/artifacts/olmo_ifcurve/meta/B_s2300.json"}
for p in (Path.home() / "review/oifc_rv/src/meta").glob("F_*_ifb*.json"):
    METAS[p.stem] = p
MINE = {"B_s2300": Path.home() / "review/oifc_rv/bucket_copy/artifacts/olmo_ifcurve/samples/B_s2300.jsonl.gz",
        "F_s2300_ifb": Path.home() / "review/otr_rv/src/F_s2300_ifb.jsonl.gz",
        "F_dpo_ifb": Path.home() / "review/otr_rv/src/F_dpo_ifb.jsonl.gz"}


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    T = Tee("provenance.txt")
    tk = Tokenizer.from_file(str(TOKJ))
    P = Pieces()

    def ids_of(prompt):
        s = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>"
        return tk.encode(s, add_special_tokens=False).ids
    res = {"metas": {}, "rows": {}}
    cache = {}
    for name, path in sorted(METAS.items()):
        m = json.load(open(path))
        ok = bad = 0
        badl = []
        for p, s in (m.get("prompt_sha256_by_pid") or {}).items():
            if p not in cache:
                cache[p] = ids_of(upstream_record(p)[1]["prompt"])
            if s == sha_int32(cache[p]) and (m.get("prompt_tokens_by_pid") or {}).get(p, len(cache[p])) == len(cache[p]):
                ok += 1
            else:
                bad += 1
                badl.append(p)
        res["metas"][name] = {"prompt_sha_match": ok, "prompt_sha_differ": bad, "differ": badl[:5],
                              **{k: m.get(k) for k in ("model_dir", "name", "rev", "seed", "temperature", "top_p", "max_tokens",
                                                       "vllm", "template_sha256", "tp", "chunk", "gpus", "lora_rank", "samples")}}
        T(f"[1] {name:14s} prompt ids: {ok} match my rebuild, {bad} differ | " + ", ".join(
            f"{k}={m.get(k)}" for k in ("rev", "seed", "temperature", "top_p", "max_tokens", "vllm", "tp", "lora_rank", "samples")))
    for job in ALL_JOBS:
        n = good = 0
        for r in iter_job(job):
            n += 1
            if r["pid"] not in cache:
                cache[r["pid"]] = ids_of(upstream_record(r["pid"])[1]["prompt"])
            good += r.get("prompt_tokens") == len(cache[r["pid"]])
        res["rows"][job] = {"rows": n, "prompt_tokens_match": good}
        T(f"[1] rows {job:12s}: {good}/{n} rows carry my prompt length")
    # (3) boundary by hand: the end of my rendered prompt and the start of the response, 3 rows per arm
    T("[3] template boundary (my rendered prompt tail | decoded response head):")
    for job in ("dpo", "T16", "F448", "C16"):
        k = 0
        for r in iter_job(job, with_ids=True):
            ids = unb64(r["ids"])
            tail = tk.decode(cache[r["pid"]][-6:], skip_special_tokens=False)
            T(f"    {job} {r['pid']}: ...{tail!r} | {P.text(ids[:12])!r}")
            k += 1
            if k == 2:
                break
    # (4) stored endpoint files: the run's copies vs my earlier bucket copies
    res["stored_sha"] = {}
    for j, p in MINE.items():
        a, b = sha_file(RAW / {"B_s2300": "artifacts/olmo_ifcurve/samples/B_s2300.jsonl.gz",
                                "F_s2300_ifb": "artifacts/olmo_ifomega/samples/F_s2300_ifb.jsonl.gz",
                                "F_dpo_ifb": "artifacts/olmo_ifomega/samples/F_dpo_ifb.jsonl.gz"}[j]), sha_file(p)
        res["stored_sha"][j] = {"run_copy": a, "my_copy": b, "equal": a == b}
        T(f"[4] {j}: run copy == my earlier bucket copy: {a == b}")
    json.dump(res, open(OUT / "provenance.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
