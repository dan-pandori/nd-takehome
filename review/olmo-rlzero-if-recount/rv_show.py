"""Show hand items for my own confirmation: prompt, constraints, graded answer (head / tail or full), reader label.
Usage: rv_show.py [--full] [--chars N] ID [ID ...] | rv_show.py --pid PID [--model M]"""
import glob
import json
import os
import sys

import rv_core as C
from rv_hand_items import fetch_texts

HAND = os.path.join(C.HERE, "hand")


def main():
    a = sys.argv[1:]
    full = "--full" in a
    chars = 1500
    if "--chars" in a:
        chars = int(a[a.index("--chars") + 1])
    keys = {}
    for f in sorted(glob.glob(os.path.join(HAND, "key_r*.json"))):
        keys.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(HAND, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["item"]] = x
    if "--pid" in a:
        pid = a[a.index("--pid") + 1]
        model = a[a.index("--model") + 1] if "--model" in a else None
        ids = sorted((i for i, k in keys.items() if k["pid"] == pid and k["kind"] == "real"
                      and (model is None or k["model"] == model)),
                     key=lambda i: (keys[i]["model"], keys[i]["read_rank"]))
    else:
        ids = [x for x in a if x.startswith("q")]
    P = C.load_problems()
    texts = fetch_texts({(keys[i]["job"], keys[i]["chunk"], keys[i]["i"], keys[i].get("swapped_from", keys[i]["pid"]))
                         for i in ids})
    for i in ids:
        k = keys[i]
        src = k.get("swapped_from", k["pid"])
        t = texts[(k["job"], k["chunk"], k["i"], src)]
        ans = C.remove_thinking_section(t)
        pr = P[k["pid"]]
        print("=" * 100)
        print(f"{i} | {k['pid']} {k['model']} {k['side']} rank {k['read_rank']} draw {k['draw']} fresh {k['fresh']} "
              f"{k['job']}/{k['chunk']}/{k['i']} kind {k['kind']} | reader: {lab.get(i, {}).get('label')} "
              f"rule {lab.get(i, {}).get('rule')}")
        print("READER:", lab.get(i, {}).get("evidence"))
        print("PROMPT:", pr["prompt"][:1200])
        print("CONSTRAINTS:", pr["instruction_id_list"],
              [{x: y for x, y in dict(kw).items() if y is not None} for kw in pr["kwargs"]])
        if full or len(ans) <= 2 * chars:
            print(f"ANSWER ({len(ans)} chars):\n{ans}")
        else:
            print(f"ANSWER ({len(ans)} chars) HEAD:\n{ans[:chars]}\n[...]\nTAIL:\n{ans[-chars // 2:]}")


if __name__ == "__main__":
    main()
