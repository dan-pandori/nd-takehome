#!/usr/bin/env python3
"""Stream the math / reasoning / instruction subsets of Olmo 3 7B's midtraining mix and n-gram-scan them against
the evaluation problems (contam.py scan). Each shard is downloaded, scanned and deleted; one summary row per shard
goes to <out>. Resumable: shards already in <out> are skipped.

Usage: midscan.py <problems.jsonl> <out.jsonl> [workers]
"""
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contam  # noqa: E402

REPO = "allenai/dolma3_dolmino_mix-100B-1025"
SUBSETS = ["cranemath", "dolmino-math", "math-meta-reasoning", "megamatt", "tinymath-mind", "tinymath-pot",
           "omr-rewrite-fullthoughts", "openthoughts2-reasoning-traces", "qwq-reasoning-traces",
           "gemini-reasoning-traces", "llama_nemotron-reasoning-traces", "general_reasoning_mix", "program_verifiable",
           "tulu-3-sft"]
TMP = "/workspace/midscan"


def work(args):
    path, problems, out = args
    import time
    from huggingface_hub import hf_hub_download
    for attempt in range(12):
        try:
            local = hf_hub_download(REPO, path, repo_type="dataset", local_dir=TMP)
            break
        except Exception as e:  # 429 (account-wide API quota: 1,000 requests / 5 min) or a transient network error
            time.sleep(90 if "429" in str(e) else 20)
    else:
        return f"FAILED {path}"
    part = f"{out}.{os.getpid()}"
    contam.mode_scan(problems, part, [local])
    os.remove(local)
    return path


def main():
    problems, out = sys.argv[1:3]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    from huggingface_hub import HfApi
    files = [f for f in HfApi().list_repo_files(REPO, repo_type="dataset")
             if f.startswith("data/") and f.split("/")[1] in SUBSETS and f.endswith((".zst", ".jsonl", ".gz"))]
    done = set()
    for p in Path(out).parent.glob(Path(out).name + ".*"):
        for ln in open(p):
            try:
                done.add(json.loads(ln)["file"].split(TMP + "/")[-1])
            except (json.JSONDecodeError, KeyError):
                pass
    todo = [f for f in files if f not in done]
    print(f"{len(files)} shards in {len(SUBSETS)} subsets; {len(done)} done; {len(todo)} to scan", flush=True)
    with Pool(workers) as pool:
        for k, f in enumerate(pool.imap_unordered(work, [(f, problems, out) for f in todo]), 1):
            if f.startswith("FAILED"):
                print(f, flush=True)
            if k % 100 == 0 or k == len(todo):
                print(f"{k}/{len(todo)} scanned (last {f})", flush=True)
    print("MIDSCAN_DONE", flush=True)


if __name__ == "__main__":
    main()
