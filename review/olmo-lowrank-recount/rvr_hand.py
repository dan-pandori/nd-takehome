"""My hand-gate label state (policy: hand/POLICY.md). Reads every reader file ~/review/olr_rv/labels/<round>_<k>.json
through the item key (hand/key_items.json); group label per the policy; my mechanical screen (out/screen.json) first;
accepted adjudications from hand/confirm.json.
usage: rvr_hand.py status           -> agreement, splits, per-job counts (stdout, out/hand_status.json)
       rvr_hand.py need3 <round>    -> groups with a 1-1 split and no third read -> hand/<round>_groups.txt
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rvr_core import KIT, OUT, SCR

H = KIT / "hand"


def load():
    key = json.load(open(H / "key_items.json"))
    reads = defaultdict(list)
    for f in sorted((SCR / "labels").glob("*.json")):
        rnd = f.stem.split("_")[0]
        for x in json.load(open(f)):
            reads[x["item"]].append((rnd, f.stem, x["label"].strip().lower(), x.get("checker_agrees"), x.get("evidence", "")))
    for it in reads:
        reads[it].sort(key=lambda r: r[0])
    scr = json.load(open(OUT / "screen.json"))
    conf = json.load(open(H / "confirm.json")) if (H / "confirm.json").exists() else {}
    return key, reads, scr, conf


def group_label(it, key, reads, scr, conf):
    g = key[it]["group"]
    if g in scr:
        return "gamed", "screen"
    if it in conf and conf[it].get("accepted"):
        return conf[it]["label"], "confirmed"
    ls = [r[2] for r in reads.get(it, [])]
    if not ls:
        return None, "unread"
    if len(ls) == 1:
        return ls[0], "one read"
    if len(ls) == 2:
        return (ls[0], "two agree") if ls[0] == ls[1] else (None, "split")
    c = Counter(ls[:3])
    return c.most_common(1)[0][0], "majority of 3"


def main():
    key, reads, scr, conf = load()
    cmd = sys.argv[1]
    if cmd == "status":
        pairs = [(r[0][2], r[1][2]) for it, r in reads.items() if len(r) >= 2]
        agree = sum(a == b for a, b in pairs)
        print(f"double-read items {len(pairs)}, agree {agree} ({agree / max(1, len(pairs)):.3f}); "
              f"first-gamed confirmed by second {sum(a == b == 'gamed' for a, b in pairs)}/{sum(a == 'gamed' for a, b in pairs)}; "
              f"first-genuine confirmed {sum(a == b == 'genuine' for a, b in pairs)}/{sum(a == 'genuine' for a, b in pairs)}")
        hows = Counter(group_label(it, key, reads, scr, conf)[1] for it in key)
        print("label sources (groups):", dict(hows))
        per = defaultdict(Counter)
        for it, v in key.items():
            lab, how = group_label(it, key, reads, scr, conf)
            for d in v["draws"]:
                per[d[0]][lab or "unresolved"] += 1
        for j in ["T1", "T4", "T16", "T64", "T256", "F448", "C16", "B_s2300"]:
            c = per[j]
            print(f"  {j:8s} draws {sum(c.values()):4d} genuine {c['genuine']:4d} gamed {c['gamed']:4d} unresolved {c['unresolved']:3d}")
        json.dump({"pairs": len(pairs), "agree": agree, "sources": dict(hows), "per_job": {j: dict(c) for j, c in per.items()}},
                  open(OUT / "hand_status.json", "w"), indent=1)
    elif cmd == "need3":
        need = [key[it]["group"] for it, r in sorted(reads.items()) if len(r) == 2 and r[0][2] != r[1][2]
                and key[it]["group"] not in scr]
        (H / f"{sys.argv[2]}_groups.txt").write_text("\n".join(need) + "\n")
        print(len(need), "groups need a third read")


if __name__ == "__main__":
    main()
