"""Reviewer contamination scan, run olmo-ifomega: word 8-gram containment of every IF evaluation prompt (IFBench 300,
IFEval 150) and every OMEGA problem (200) against
  rl : all 102,026 Dolci-Think-RL-32B prompts @ d581ecde (local copy),
  dpo: the `prompt` of all Dolci-Think-DPO-32B rows @ 0898aac9 (each file downloaded, scanned, deleted),
  sft: the user and system turns of all Dolci-Think-SFT-32B conversations @ 7668c638 (the same; IF prompts only).
Tokens: lower-cased [a-z0-9]+ runs (my own tokeniser). raw containment = |G(p) & G(d)| / |G(p)| over word 8-gram sets;
content containment = the same over p's 8-grams that occur in fewer than 20 RL prompts (df from the rl pass), the
pre-registration's definition. Per (corpus, prompt): the top 5 documents by raw and by content containment, with the
matched document's text (first 4,000 characters) for every document with raw or content >= 0.3.
Executor scanned SFT all turns and DPO prompt + both responses; this scan reads user / system turns and prompts only
(a request copied into a response is not counted here).
Usage: python rv_contam.py rl|dpo|sft  -> ~/review/oif_rv/contam/<corpus>.json (+ progress log)"""
import gzip
import heapq
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict

import pyarrow.compute as pc
import pyarrow.parquet as pq

import rv_core as C

W = re.compile(r"[a-z0-9]+")
N = 8
OUTD = os.path.join(C.BIG, "contam")
DATA = os.path.join(C.BIG, "data")
REVS = {"dpo": ("allenai/Dolci-Think-DPO-32B", "0898aac9657c0fa79b02c0e91627b370bed2a127", 9),
        "sft": ("allenai/Dolci-Think-SFT-32B", "7668c638cc84100951973b456069a1a462d6d915", 156)}


def grams(text):
    ws = W.findall(text.lower())
    if len(ws) < N:
        return set()
    return set(zip(*[ws[i:] for i in range(N)]))


def eval_prompts(ifonly=False):
    P = C.load_problems()
    out = {}
    for p, r in P.items():
        if ifonly and not r["task"].startswith("if"):
            continue
        out[p] = grams(r["prompt"])
    return out


class Scanner:
    def __init__(self, ev, content=None):
        self.ev = ev
        self.content = content or {}
        self.owner = defaultdict(list)
        for p, gs in ev.items():
            for g in gs:
                self.owner[g].append(p)
        self.allg = set(self.owner)
        self.top_raw = defaultdict(list)   # p -> heap of (raw, content, docid)
        self.top_con = defaultdict(list)
        self.texts = {}
        self.df = Counter()
        self.ndocs = 0

    def doc(self, docid, text, source=""):
        self.ndocs += 1
        dg = grams(text)
        if not dg:
            return
        hit = dg & self.allg
        if not hit:
            return
        for g in hit:
            self.df[g] += 1
        cnt = Counter()
        ccnt = Counter()
        for g in hit:
            for p in self.owner[g]:
                cnt[p] += 1
                if g in self.content.get(p, ()):
                    ccnt[p] += 1
        for p, k in cnt.items():
            raw = k / len(self.ev[p])
            cg = self.content.get(p)
            con = (ccnt[p] / len(cg)) if cg else 0.0
            item = (round(raw, 4), round(con, 4), docid, source)
            for heap, key in ((self.top_raw[p], raw), (self.top_con[p], con)):
                if len(heap) < 5:
                    heapq.heappush(heap, (key, item))
                elif key > heap[0][0]:
                    heapq.heapreplace(heap, (key, item))
            if (raw >= 0.3 or con >= 0.3) and docid not in self.texts:
                self.texts[docid] = text[:4000]

    def result(self):
        out = {}
        for p in self.ev:
            out[p] = {"n_grams": len(self.ev[p]), "n_content": len(self.content.get(p, ())),
                      "top_raw": [x[1] for x in sorted(self.top_raw[p], reverse=True)],
                      "top_content": [x[1] for x in sorted(self.top_con[p], reverse=True)]}
        return out


def run_rl():
    ev = eval_prompts()
    sc = Scanner(ev)
    for i in range(4):
        t = pq.read_table(os.path.join(DATA, "dolci_rl", "data", f"train-0000{i}-of-00004.parquet"),
                          columns=["prompt", "custom_id", "original_dataset"]).to_pylist()
        for r in t:
            sc.doc(r["custom_id"], r["prompt"], r["original_dataset"])
    # second pass with content grams (df < 20 over RL prompts)
    content = {p: {g for g in gs if sc.df[g] < 20} for p, gs in ev.items()}
    sc2 = Scanner(ev, content)
    for i in range(4):
        t = pq.read_table(os.path.join(DATA, "dolci_rl", "data", f"train-0000{i}-of-00004.parquet"),
                          columns=["prompt", "custom_id", "original_dataset"]).to_pylist()
        for r in t:
            sc2.doc(r["custom_id"], r["prompt"], r["original_dataset"])
    json.dump({p: sorted(" ".join(g) for g in gs) for p, gs in content.items()},
              open(os.path.join(OUTD, "content_grams.json"), "w"))
    return sc2


def load_content():
    d = json.load(open(os.path.join(OUTD, "content_grams.json")))
    return {p: {tuple(s.split(" ")) for s in v} for p, v in d.items()}


def fetch(repo, rev, f, dst):
    url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{f}"
    for attempt in range(5):
        r = subprocess.run(["curl", "-sfL", "--retry", "3", "-o", dst, url])
        if r.returncode == 0:
            return True
        time.sleep(30 * (attempt + 1))
    return False


def run_remote(kind, log):
    repo, rev, nf = REVS[kind]
    ev = eval_prompts(ifonly=(kind == "sft"))
    content = load_content()
    sc = Scanner(ev, {p: content[p] for p in ev})
    tmp = os.path.join(C.BIG, f"tmp_{kind}.parquet")
    for i in range(nf):
        f = f"data/train-{i:05d}-of-{nf:05d}.parquet"
        t0 = time.time()
        if not fetch(repo, rev, f, tmp):
            log.write(f"FAILED {f}\n")
            log.flush()
            continue
        t1 = time.time()
        pf = pq.ParquetFile(tmp)
        nd = 0
        if kind == "dpo":
            for b in pf.iter_batches(columns=["prompt", "prompt_id", "dataset"], batch_size=4000):
                for r in b.to_pylist():
                    sc.doc(r["prompt_id"], r["prompt"] or "", r["dataset"])
                    nd += 1
        else:
            for b in pf.iter_batches(columns=["messages", "id", "source"], batch_size=1000):
                ids = b.column("id").to_pylist()
                srcs = b.column("source").to_pylist()
                msgs = b.column("messages")
                flat = pc.list_flatten(msgs)
                par = pc.list_parent_indices(msgs).to_numpy()
                roles = pc.struct_field(flat, "role").to_pylist()
                conts = pc.struct_field(flat, "content").to_pylist()
                per = defaultdict(list)
                for j, (ro, co) in enumerate(zip(roles, conts)):
                    if ro in ("user", "system") and co:
                        per[int(par[j])].append(co)
                for k in range(len(ids)):
                    nd += 1
                    if per.get(k):
                        sc.doc(ids[k], "\n".join(per[k]), srcs[k])
        os.remove(tmp)
        log.write(f"{f}: {nd} docs, fetch {t1 - t0:.0f}s scan {time.time() - t1:.0f}s\n")
        log.flush()
    return sc


def main():
    kind = sys.argv[1]
    os.makedirs(OUTD, exist_ok=True)
    log = open(os.path.join(OUTD, f"{kind}.log"), "a")
    t0 = time.time()
    sc = run_rl() if kind == "rl" else run_remote(kind, log)
    res = {"corpus": kind, "docs_scanned": sc.ndocs, "prompts": sc.result()}
    json.dump(res, open(os.path.join(OUTD, f"{kind}.json"), "w"))
    with gzip.open(os.path.join(OUTD, f"{kind}_texts.json.gz"), "wt") as g:
        json.dump(sc.texts, g)
    log.write(f"DONE {kind}: {sc.ndocs} docs in {time.time() - t0:.0f}s\n")
    log.close()
    print("done", kind, sc.ndocs)


if __name__ == "__main__":
    main()
