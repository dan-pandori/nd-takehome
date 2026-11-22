"""Blinded hand-check items for my repeat of run olmo-ifcurve's hand gate.

usage: rvc_hand_items.py ROUND [BATCH]     (reads hand/need_<ROUND>.json; BATCH = items per reader, default 40)

Item text (my own format, same content as the pre-registered item): the prompt exactly as the model received it (the
original IFBench / IFEval prompt; no hints in this run), the constraints with the official strict checker's verdict
(my re-grade; every strict success has all followed), and the answer (text after the last '</think>'). No model,
checkpoint, arm, thinking or selection reason. Item ids are random (seeded by the round name); items are shuffled
across prompts, checkpoints and arms. Writes ~/review/oifc_rv/items/<id>.md, hand/key_<ROUND>.json (id -> draw key)
and hand/batches_<ROUND>.json; reader task text: rvc_hand_items.py task ROUND K.
"""
import gzip
import hashlib
import json
import random
import sys

from rvc_core import KIT, OUT, SCR, upstream_record

HAND = KIT / "hand"
ITEMS = SCR / "items"
ITEMS.mkdir(parents=True, exist_ok=True)
LABELS = SCR / "labels"
LABELS.mkdir(parents=True, exist_ok=True)
PROMPT = KIT / "hand" / "reader_prompt.md"


def per_of(k, _c={}):
    job = k[0]
    if job not in _c:
        _c[job] = {}
        with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                _c[job][(r["pid"], int(r["chunk"]), int(r["i"]))] = (r["strict"], r["per"])
    return _c[job][(k[1], k[2], k[3])]


def item_md(iid, prompt, rec, answer, per):
    lines = [f"# Item {iid}", "", "## Prompt (as the model received it)", "", prompt, "", "## Verifiable constraints", ""]
    for j, (cid, kw) in enumerate(zip(rec["instruction_id_list"], rec["kwargs"])):
        kw = {a: b for a, b in dict(kw).items() if b is not None}
        lines.append(f"- `{cid}` {json.dumps(kw, ensure_ascii=False)}: "
                     f"{'followed' if per[j] else 'NOT followed'} (official strict checker)")
    lines += ["", "## Answer", "", answer, ""]
    return "\n".join(lines)


def write_round(rnd, batch=40):
    keys = [tuple(k) for k in json.load(open(HAND / f"need_{rnd}.json"))]
    with gzip.open(OUT / "answers.json.gz", "rt") as f:
        ans = {tuple(json.loads(k)): v for k, v in json.load(f).items()}
    rng = random.Random(f"oifc-{rnd}")
    rng.shuffle(keys)
    key, used = {}, set()
    for k in keys:
        st, per = per_of(k)
        assert st, k
        while True:
            iid = "z" + hashlib.sha256(f"{rnd}|{rng.random()}".encode()).hexdigest()[:6]
            if iid not in used and not (ITEMS / f"{iid}.md").exists():
                break
        used.add(iid)
        task, rec = upstream_record(k[1])
        (ITEMS / f"{iid}.md").write_text(item_md(iid, rec["prompt"], rec, ans[k], per))
        key[iid] = list(k)
    ids = list(key)
    # batches of about `batch` items, balanced by characters
    nb = max(1, -(-len(ids) // batch))
    sizes = {i: len((ITEMS / f"{i}.md").read_text()) for i in ids}
    bs = [[] for _ in range(nb)]
    load = [0] * nb
    for i in sorted(ids, key=lambda x: -sizes[x]):
        j = min(range(nb), key=lambda b: (load[b], len(bs[b])))
        bs[j].append(i)
        load[j] += sizes[i]
    for b in bs:
        rng.shuffle(b)
    json.dump(key, open(HAND / f"key_{rnd}.json", "w"), indent=0)
    json.dump(bs, open(HAND / f"batches_{rnd}.json", "w"))
    print(rnd, len(ids), "items in", nb, "batches; chars per batch", load)


def task(rnd, k):
    b = json.load(open(HAND / f"batches_{rnd}.json"))[k]
    s = PROMPT.read_text().rstrip() + "\n\nItem files (read each one in full):\n"
    s += "\n".join(str(ITEMS / f"{i}.md") for i in b)
    out = LABELS / f"{rnd}_{k:02d}.json"
    s += f"\n\nOutput path: {out}\n\n"
    s += ("Write the JSON list to the output path (python3 is fine; write any scratch file only under /tmp, and keep "
          "scripts short and in the foreground). Then reply with ONE line only, e.g. \"DONE: 40 items, 31 genuine, "
          "9 gamed\" — do not repeat the JSON in your reply unless writing the file failed.")
    return s


def write_tasks(rnd):
    """One task file per batch: ~/review/oifc_rv/tasks/<ROUND>_<k>.txt (reader prompt + items + output path)."""
    T = SCR / "tasks"
    T.mkdir(exist_ok=True)
    n = len(json.load(open(HAND / f"batches_{rnd}.json")))
    for k in range(n):
        (T / f"{rnd}_{k:02d}.txt").write_text(task(rnd, k) + "\n")
    print(n, "task files in", T)


def rebatch(rnd, start, size):
    """Split batches[start:] of a round into batches of `size` items (readers must finish within 600 s): writes
    hand/batches_<ROUND>_s.json and task files <ROUND>_s<k>.txt whose labels go to labels/<ROUND>_s<k>.json (same key)."""
    bs = json.load(open(HAND / f"batches_{rnd}.json"))
    items = [i for b in bs[start:] for i in b]
    small = [items[j:j + size] for j in range(0, len(items), size)]
    json.dump({"from_batch": start, "batches": small}, open(HAND / f"batches_{rnd}_s.json", "w"))
    T = SCR / "tasks"
    for k, b in enumerate(small):
        s = PROMPT.read_text().rstrip() + "\n\nItem files (read each one in full):\n"
        s += "\n".join(str(ITEMS / f"{i}.md") for i in b)
        s += f"\n\nOutput path: {LABELS / f'{rnd}_s{k:02d}.json'}\n\n"
        s += ("Write the JSON list to the output path (python3 is fine; write any scratch file only under /tmp, and keep "
              "scripts short and in the foreground). Then reply with ONE line only, e.g. \"DONE: 40 items, 31 genuine, "
              "9 gamed\" — do not repeat the JSON in your reply unless writing the file failed.")
        (T / f"{rnd}_s{k:02d}.txt").write_text(s + "\n")
    print(len(items), "items re-batched into", len(small), "batches of <=", size)


if __name__ == "__main__":
    if sys.argv[1] == "task":
        print(task(sys.argv[2], int(sys.argv[3])))
    elif sys.argv[1] == "tasks":
        write_tasks(sys.argv[2])
    elif sys.argv[1] == "rebatch":
        rebatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else:
        write_round(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40)

