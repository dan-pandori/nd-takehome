"""Reviewer hand gate of run olmo-iffu: reader labels + my confirmations -> per-prompt statuses and outcomes.

Inputs: hand/key_r*.json (item -> arm, job, pid, rank, chunk, i), hand/reader_labels/<batch>[_b].json (the readers'
JSON verbatim; `_b` = a second, independent reader of the same items), hand/confirm.json (my final label for an item,
with a note; it overrides the readers).
An item's label: mine if confirmed, else the readers' when they agree, else "unsure" (I must adjudicate).
Reading rule per (arm, prompt), strict successes in draw order (the pre-registered gate; for s2300 the reading the
run ended up using, deviation 1): read until 2 genuine or none left. Test 3: every strict success. Test 1: every
response credited under omega or rl.
Rule 6 (title case in ALL CAPS): genuine under the primary reading; under the strict reading not a success.
Writes out/hand.json, out/hand.txt and, when reads are still needed, hand/need_r<next>.json.
"""
import collections
import glob
import json
import os
import sys

import rvi_core as C
from rvi_hand_items import successes

H = C.KIT / "hand"


def load_labels():
    keys = {}
    for f in sorted(glob.glob(str(H / "key_r*.json"))):
        keys.update(json.load(open(f)))
    reads = collections.defaultdict(list)
    for f in sorted(glob.glob(str(H / "reader_labels" / "*.json"))):
        reader = os.path.basename(f)[:-5]
        for x in json.load(open(f)):
            reads[x["item"]].append(dict(x, reader=reader))
    conf = {k: v for k, v in json.load(open(H / "confirm.json")).items() if not k.startswith("_")} if (H / "confirm.json").exists() else {}
    return keys, reads, conf


def item_label(iid, reads, conf):
    if iid in conf:
        return conf[iid]["label"], conf[iid].get("all_caps_title_case", False)
    labs = {x["label"] for x in reads.get(iid, [])}
    caps = any(x.get("all_caps_title_case") for x in reads.get(iid, []))
    if not labs:
        return None, caps
    if len(labs) == 1:
        return labs.pop(), caps
    return "unsure", caps


def main():
    keys, reads, conf = load_labels()
    succ = successes()
    by_rank = {}
    for iid, k in keys.items():
        by_rank[(k["arm"], k["pid"], k["rank"])] = iid
    status, need, lines = {}, [], []
    for (arm, pid), rs in sorted(succ.items()):
        if arm == "T1_dpo":
            continue
        labs = []
        for rank in range(len(rs)):
            iid = by_rank.get((arm, pid, rank))
            lab, caps = item_label(iid, reads, conf) if iid else (None, False)
            labs.append({"rank": rank, "item": iid, "label": lab, "caps": caps, "chunk": rs[rank]["chunk"],
                         "i": rs[rank]["i"], "job": rs[rank]["job"]})
        # walk in draw order until 2 genuine (primary reading) or none left
        g = gs = 0
        pending = False
        read = []
        for x in labs:
            if g >= 2 and (arm != "T3_dpo"):
                break
            if x["label"] in (None, "unsure"):
                pending = True
                break
            read.append(x)
            if x["label"] == "genuine":
                g += 1
                if not x["caps"]:
                    gs += 1
        # strict reading (rule 6): keep reading past ALL-CAPS genuine items if needed
        gs2, pend2 = 0, False
        for x in labs:
            if gs2 >= 2:
                break
            if x["label"] in (None, "unsure"):
                pend2 = True
                break
            if x["label"] == "genuine" and not x["caps"]:
                gs2 += 1
        if pending or (pend2 and g >= 2 and gs2 < 2):
            nxt = [x["rank"] for x in labs if x["label"] is None][:3]
            need += [[arm, pid, r] for r in nxt]
        status[f"{arm}|{pid}"] = {"strict": len(rs), "genuine": g, "genuine_strict_reading": gs2,
                                  "read": len(read), "pending": pending or (pend2 and g >= 2 and gs2 < 2),
                                  "items": labs}
    # T1
    t1 = {}
    for (arm, pid), rs in sorted(succ.items()):
        if arm != "T1_dpo":
            continue
        its = []
        for rank, r in enumerate(rs):
            iid = by_rank.get((arm, pid, rank))
            lab, _ = item_label(iid, reads, conf) if iid else (None, False)
            its.append({"rank": rank, "item": iid, "label": lab, "omega": r["omega"], "rl": r["rl"],
                        "chunk": r["chunk"], "i": r["i"]})
        t1[pid] = {"any_credited": len(its), "doubly_credited": sum(x["omega"] and x["rl"] for x in its),
                   "sound_any": sum(x["label"] == "sound" for x in its),
                   "sound_doubly": sum(x["label"] == "sound" and x["omega"] and x["rl"] for x in its),
                   "unsure": sum(x["label"] in (None, "unsure") for x in its), "items": its}
    out = {"if": status, "t1": t1}
    C.dump(out, "hand.json")
    nxt = 1 + max(int(os.path.basename(f)[5:-5]) for f in glob.glob(str(H / "key_r*.json")))
    if need:
        json.dump(need, open(H / f"need_r{nxt}.json", "w"))
    for k, v in status.items():
        lines.append(f"{k}: strict {v['strict']}, read {v['read']}, genuine {v['genuine']} (strict reading "
                     f"{v['genuine_strict_reading']}){' PENDING' if v['pending'] else ''}  "
                     + " ".join(f"{x['rank']}:{(x['label'] or '-')[:3]}{'*' if x['caps'] else ''}" for x in v["items"][:12]))
    for k, v in t1.items():
        lines.append(f"T1|{k[-3:]}: any {v['any_credited']} doubly {v['doubly_credited']} sound(any) {v['sound_any']} "
                     f"sound(doubly) {v['sound_doubly']} unsure {v['unsure']}  "
                     + " ".join(f"c{x['chunk']}.{x['i']}:{x['label']}{'(rl only)' if not x['omega'] else ''}" for x in v["items"]))
    lines.append(f"unlabelled-or-unsure items blocking: {len(need)} next reads -> need_r{nxt}.json" if need else "no reads needed")
    (C.OUT / "hand.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-12:]) if "-q" in sys.argv else "\n".join(lines))


if __name__ == "__main__":
    main()
