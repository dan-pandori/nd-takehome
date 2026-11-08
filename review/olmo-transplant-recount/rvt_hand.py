"""Merge the reviewer's blinded reader labels (run olmo-transplant) and pick the next readers.

Readers: A (every item), B (every A-gamed item, a seeded 15 % of A-genuine items (per-item hash draw), and every item
where A disagrees with the executor's label), C (every A/B split). Final = A when B did not read; A when A = B; else the majority of A, B, C.
hand/confirm.json (optional): my adjudication {item: {"label", "note"}}, applied last and listed in the output.
Usage: rvt_hand.py need_B | need_C | final
  need_B / need_C -> hand/batches_B.json / batches_C.json (+ ~/review/otr_rv/batches/<R>_<i>.txt)
  final           -> out/my_labels.json, out/my_labels_r6.json, out/hand.txt, out/hand.json
Raw reader JSON is copied into hand/reader_labels/ (committed).
"""
import collections
import hashlib
import json
import random
import shutil
import sys

from rvt_core import KIT, OUT, SCR, Tee

HAND = KIT / "hand"
RL = HAND / "reader_labels"
RL.mkdir(exist_ok=True)
key = json.load(open(HAND / "key_A.json"))


def load(tag):
    out = {}
    for f in sorted((SCR / "labels_A").glob(f"{tag}_A_*.json")):
        shutil.copy(f, RL / f.name)
        for r in json.load(open(f)):
            if r["item"] in out:
                raise SystemExit(f"duplicate {tag} label for {r['item']} in {f.name}")
            out[r["item"]] = r
    return out


def exec_label(item):
    labs = [l for l in key[item]["exec_labels"] if l in ("genuine", "gamed")]
    return labs[0] if len(set(labs)) == 1 else None


def in_sample(item, share=0.15):
    """seeded per-item draw of the 15 % genuine second-read sample"""
    return int(hashlib.sha256(f"20261108|{item}".encode()).hexdigest(), 16) % 1000 < share * 1000


def write_batches(name, items, size=46):
    rng = random.Random(f"{name}|7731")
    items = sorted(items)
    rng.shuffle(items)
    b = [items[i:i + size] for i in range(0, len(items), size)]
    json.dump(b, open(HAND / f"batches_{name}.json", "w"), indent=0)
    for i, its in enumerate(b):
        (SCR / "batches" / f"{name}_{i:02d}.txt").write_text("\n".join(str(SCR / "items_A" / f"{x}.md") for x in its) + "\n")
    print(f"{name}: {len(items)} items in {len(b)} batches {[len(x) for x in b]}")


def main():
    mode = sys.argv[1]
    A = load("A")
    missing = sorted(set(key) - set(A))
    if mode == "need_B":
        # incremental: may run while A batches are still out; the 15 % genuine sample is decided per item by a
        # seeded hash, so it does not depend on which A batches are in
        pick = {i for i, r in A.items() if r["label"] == "gamed"}
        pick |= {i for i, r in A.items() if r["label"] == "genuine" and in_sample(i)}
        pick |= {i for i, r in A.items() if exec_label(i) and exec_label(i) != r["label"]}
        old = json.load(open(HAND / "batches_B.json")) if (HAND / "batches_B.json").exists() else []
        done = {x for b in old for x in b}
        new = sorted(pick - done)
        rng = random.Random(f"B|{len(old)}|7731")
        rng.shuffle(new)
        nb = [new[i:i + 46] for i in range(0, len(new), 46)]
        for k, its in enumerate(nb, start=len(old)):
            (SCR / "batches" / f"B_{k:02d}.txt").write_text("\n".join(str(SCR / "items_A" / f"{x}.md") for x in its) + "\n")
        json.dump(old + nb, open(HAND / "batches_B.json", "w"), indent=0)
        print(f"B: {len(pick)} items picked from {len(A)} A labels ({len(missing)} items still without A); "
              f"{len(new)} new in batches {list(range(len(old), len(old) + len(nb)))} {[len(x) for x in nb]}")
        return
    B = load("B")
    if mode == "need_C":  # incremental, like need_B
        split = {i for i in B if B[i]["label"] != A[i]["label"]}
        old = json.load(open(HAND / "batches_C.json")) if (HAND / "batches_C.json").exists() else []
        done = {x for b in old for x in b}
        new = sorted(split - done)
        rng = random.Random(f"C|{len(old)}|7731")
        rng.shuffle(new)
        nb = [new[i:i + 46] for i in range(0, len(new), 46)]
        for k, its in enumerate(nb, start=len(old)):
            (SCR / "batches" / f"C_{k:02d}.txt").write_text("\n".join(str(SCR / "items_A" / f"{x}.md") for x in its) + "\n")
        json.dump(old + nb, open(HAND / "batches_C.json", "w"), indent=0)
        print(f"C: {len(split)} A/B splits among {len(B)} B labels; {len(new)} new in batches "
              f"{list(range(len(old), len(old) + len(nb)))} {[len(x) for x in nb]}")
        return
    C = load("C")
    conf = json.load(open(HAND / "confirm.json")) if (HAND / "confirm.json").exists() else {}
    P = Tee("hand.txt")
    final, how = {}, {}
    for i in key:
        a = A[i]["label"]
        if i not in B:
            final[i], how[i] = a, "A"
        elif B[i]["label"] == a:
            final[i], how[i] = a, "A=B"
        elif i in C:
            votes = collections.Counter([a, B[i]["label"], C[i]["label"]])
            final[i], how[i] = votes.most_common(1)[0][0], "ABC"
        else:
            final[i], how[i] = None, "split_unread"
        if i in conf:
            final[i], how[i] = conf[i]["label"], how[i] + "+confirm"
    P(f"items {len(key)}; A labels {len(A)} (missing {len(missing)}); B {len(B)}; C {len(C)}; confirm {len(conf)}")
    P(f"A labels: {dict(collections.Counter(r['label'] for r in A.values()))}; final: {dict(collections.Counter(final.values()))}; "
      f"how: {dict(collections.Counter(how.values()))}")
    caps = {i for i in key if any((X.get(i) or {}).get("all_caps_title_case") for X in (A, B, C))}
    P(f"items any reader flagged all-caps title case: {len(caps)} {sorted(caps)}")
    # agreement with the executor, per cell
    agree = collections.defaultdict(collections.Counter)
    dis = []
    for i, k in key.items():
        e = exec_label(i)
        if e is None or final[i] is None:
            continue
        for c in k["cells"]:
            agree[c]["agree" if e == final[i] else f"exec {e} / mine {final[i]}"] += 1
        if e != final[i]:
            dis.append(i)
    P("agreement with the executor's label (items it had labelled), by cell:")
    for c, v in sorted(agree.items()):
        P(f"   {c:14s} {dict(v)}")
    P(f"disagreements: {len(dis)}")
    for i in sorted(dis, key=lambda x: key[x]["cells"]):
        P(f"   {i} {key[i]['pid']} {key[i]['cells']} exec {key[i]['exec_labels']} ({key[i]['exec_src']}) mine {final[i]} "
          f"[{how[i]}]: A {A[i]['label']}: {A[i]['evidence'][:200]}")
        for tag, X in (("B", B), ("C", C)):
            if i in X:
                P(f"        {tag} {X[i]['label']}: {X[i]['evidence'][:200]}")
    new_by_cell = collections.defaultdict(collections.Counter)
    for i, k in key.items():
        if exec_label(i) is None:
            for c in k["cells"]:
                new_by_cell[c][final[i]] += 1
    P("items the executor had NOT labelled (unread successes), my final labels by cell:")
    for c, v in sorted(new_by_cell.items()):
        P(f"   {c:14s} {dict(v)}")
    lab = {k: final[i] for i, v in key.items() for k in v["keys"] if final[i]}
    lab6 = {k: ("gamed" if i in caps else final[i]) for i, v in key.items() for k in v["keys"] if final[i]}
    json.dump(lab, open(OUT / "my_labels.json", "w"), indent=0, sort_keys=True)
    json.dump(lab6, open(OUT / "my_labels_r6.json", "w"), indent=0, sort_keys=True)
    json.dump({"final": final, "how": how, "caps": sorted(caps), "disagree": dis}, open(OUT / "hand.json", "w"), indent=1)
    P(f"my_labels.json: {len(lab)} sample keys")


if __name__ == "__main__":
    main()
