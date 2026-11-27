"""Blinded hand-gate items of my review: one item per group (pid, whitespace-collapsed answer sha) of the scope
(out/scope.json). Item file = the prompt as the model received it (upstream text; identical to the run's problems
file), the verifiable constraints with kwargs and MY strict checker's per-instruction verdict, and the answer (text
after the last '</think>', stripped). No job, arm, step, draw index or thinking. Item ids are seeded random hex.

usage: rvr_items.py r1                 -> ~/review/olr_rv/items/<id>.md, hand/key_r1.json (id -> group, draws),
                                          hand/batches/r1_<k>.txt (seeded shuffle, 40 per batch)
       rvr_items.py batches <round> <file-of-groups> [--size N]   -> a further read round over existing items
       rvr_items.py prompt <batch>     -> the reader prompt for one batch (stdout)
"""
import gzip
import json
import random
import sys
from collections import defaultdict

from rvr_core import KIT, OUT, SCR, upstream_record

H = KIT / "hand"
ITEMS = SCR / "items"
LABELS = SCR / "labels"
READER = (Path := __import__("pathlib").Path)(Path.home() / "review" / "olmo-lowrank" / "olmo_lowrank" / "handcheck_prompt_if.md")


def groups():
    S = json.load(open(OUT / "scope.json"))["scope"]
    with gzip.open(OUT / "answers_scope.json.gz", "rt") as f:
        A = {tuple(json.loads(k)): v for k, v in json.load(f).items()}
    G = defaultdict(list)
    for d in S:
        G[f"{d['pid']}|{d['ans_sha']}"].append((d["job"], d["pid"], d["chunk"], d["i"]))
    return G, A


def item_text(item, pid, ans, per):
    task, rec = upstream_record(pid)
    cons = "\n".join(f"- `{i}` {json.dumps({a: b for a, b in k.items() if b is not None})}: "
                     f"{'followed' if ok else 'NOT followed'} (official strict checker)"
                     for i, k, ok in zip(rec["instruction_id_list"], rec["kwargs"], per))
    return (f"# Item {item}\n\n## Prompt (as the model received it)\n\n{rec['prompt']}\n\n"
            f"## Verifiable constraints\n\n{cons}\n\n## Answer\n\n{ans}\n")


def write_batches(rnd, items, size):
    random.Random(f"olmo-lowrank review batches {rnd}").shuffle(items)
    (H / "batches").mkdir(parents=True, exist_ok=True)
    n = 0
    for k in range(0, len(items), size):
        n += 1
        (H / "batches" / f"{rnd}_{n}.txt").write_text("\n".join(items[k:k + size]) + "\n")
    print(f"{rnd}: {len(items)} items in {n} batches")


def cmd_r1():
    G, A = groups()
    per = {}
    for job in sorted({k[0] for v in G.values() for k in v}):
        for ln in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            per[(job, r["pid"], int(r["chunk"]), int(r["i"]))] = r["per"]
    ITEMS.mkdir(parents=True, exist_ok=True)
    rng = random.Random("olmo-lowrank review item ids 2026-11-27")
    used, key = set(), {}
    for g in sorted(G):
        while True:
            it = "v%06x" % rng.randrange(16 ** 6)
            if it not in used:
                used.add(it)
                break
        d0 = sorted(G[g])[0]
        assert all(per[d] == per[d0] for d in G[g]) and all(A[d].split() == A[d0].split() for d in G[g])
        (ITEMS / f"{it}.md").write_text(item_text(it, d0[1], A[d0], per[d0]))
        key[it] = {"group": g, "draws": [list(d) for d in sorted(G[g])]}
    json.dump(key, open(H / "key_items.json", "w"), indent=1)
    write_batches("r1", sorted(key), 40)


def cmd_batches(rnd, path, size):
    key = json.load(open(H / "key_items.json"))
    by_g = {v["group"]: k for k, v in key.items()}
    items = [by_g[g.strip()] for g in open(path) if g.strip()]
    write_batches(rnd, items, size)


def cmd_prompt(batch):
    txt = READER.read_text().replace("(olmo-lowrank hand check;", "(olmo-lowrank hand check, second team;")
    ids = [l.strip() for l in open(H / "batches" / f"{batch}.txt") if l.strip()]
    LABELS.mkdir(parents=True, exist_ok=True)
    print(txt)
    print("Item files (read each one in full):")
    for i in ids:
        print(f"{ITEMS}/{i}.md")
    print(f"\nOutput path: {LABELS}/{batch}.json\n")
    print(f'Write the JSON list to the output path (python is fine). Then reply with ONE line only, e.g. "DONE {batch}: '
          f'{len(ids)} items, 31 genuine, 9 gamed" — do not repeat the JSON in your reply unless writing the file failed.')


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "r1":
        cmd_r1()
    elif c == "batches":
        cmd_batches(sys.argv[2], sys.argv[3], int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 40)
    elif c == "prompt":
        cmd_prompt(sys.argv[2])
