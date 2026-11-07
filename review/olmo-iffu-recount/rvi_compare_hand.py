"""Phase 2: the executor's hand table (olmo_iffu/handcheck.csv) joined to my items on (job, pid, chunk, i).

Coverage both ways, label agreement (executor final_label vs my final label), every disagreement with both
evidences, and per (arm, prompt) outcome comparison (executor's walk recomputed from its own final labels with the
same rule as mine).  -> out/hand_compare.{txt,json}
"""
import collections
import csv
import glob
import json
import os

import rvi_core as C
from rvi_hand_items import successes

H = C.KIT / "hand"
ARM = {"T2_dpo": "T2_dpo", "T2_s2300": "T2_s2300", "T2c_dpo": "T2c_dpo", "T2c_s2300": "T2c_s2300",
       "T4_s0750": "T4", "T4b_s0750": "T4", "T1_dpo": "T1_dpo", "T3_dpo": "T3_dpo"}


def main():
    ex = list(csv.DictReader(open(C.KIT.parent.parent / "olmo_iffu" / "handcheck.csv")))
    keys = {}
    for f in glob.glob(str(H / "key_r*.json")):
        keys.update(json.load(open(f)))
    mine = json.load(open(C.OUT / "hand.json"))
    my_lab = {}
    for k, v in mine["if"].items():
        for x in v["items"]:
            if x["label"]:
                my_lab[(x["job"], k.split("|")[1], x["chunk"], x["i"])] = (x["label"], x["item"], x["caps"])
    for pid, v in mine["t1"].items():
        for x in v["items"]:
            my_lab[("T1_dpo", pid, x["chunk"], x["i"])] = (x["label"], x["item"], False)
    reads = collections.defaultdict(list)
    for f in sorted(glob.glob(str(H / "reader_labels" / "*.json"))):
        for x in json.load(open(f)):
            reads[x["item"]].append(x)
    exl = {}
    for r in ex:
        exl[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))] = r
    both = sorted(set(exl) & set(my_lab))
    only_ex = sorted(set(exl) - set(my_lab))
    only_me = sorted(set(my_lab) - set(exl))
    agree = [k for k in both if exl[k]["final_label"] == my_lab[k][0]]
    dis = [k for k in both if exl[k]["final_label"] != my_lab[k][0]]
    lines = [f"executor items {len(exl)}, mine {len(my_lab)}, both {len(both)}, agree {len(agree)}, disagree {len(dis)}; "
             f"executor-only {len(only_ex)}, mine-only {len(only_me)}",
             "executor final labels: " + str(dict(collections.Counter(r["final_label"] for r in ex)))]
    out = {"disagree": [], "only_ex": [], "only_me": []}
    for k in dis:
        e = exl[k]
        lab, iid, caps = my_lab[k]
        ev = " || ".join(f"{x['label']}: {x['evidence'][:220]}" for x in reads.get(iid, []))
        out["disagree"].append({"key": k, "executor": e["final_label"], "executor_reader": e["all_reader_labels"],
                                "overturned": e["overturned"], "mine": lab, "my_item": iid,
                                "executor_note": (e["my_note"] or "")[:300],
                                "executor_evidence": (e["reader_evidence"] or "")[:300], "my_readers": ev})
        lines.append(f"\nDISAGREE {k}: executor {e['final_label']} (readers {e['all_reader_labels']}, overturned "
                     f"{e['overturned']}) vs mine {lab} ({iid})\n  ex note: {(e['my_note'] or '')[:260]}\n  ex reader: "
                     f"{(e['reader_evidence'] or '')[:260]}\n  my readers: {ev[:600]}")
    for k in only_ex:
        out["only_ex"].append({"key": k, "label": exl[k]["final_label"], "role": exl[k]["role"]})
    for k in only_me:
        out["only_me"].append({"key": k, "label": my_lab[k][0]})
    lines.append("\nexecutor-only items (key, label, role): " + "; ".join(
        f"{k[0]} {k[1]} c{k[2]}.{k[3]} {exl[k]['final_label']} {exl[k]['role']}" for k in only_ex))
    lines.append("\nmine-only items: " + "; ".join(f"{k[0]} {k[1]} c{k[2]}.{k[3]} {my_lab[k][0]}" for k in only_me))
    # executor's walk per (arm, prompt) from its own labels, same rule
    succ = successes()
    walk = {}
    for (arm, pid), rs in succ.items():
        if arm in ("T1_dpo",):
            continue
        g = 0
        state = "done"
        for r in rs:
            if g >= 2:
                break
            e = exl.get((r["job"], pid, r["chunk"], r["i"]))
            if e is None:
                state = f"unread from rank {rs.index(r)}"
                break
            if e["final_label"] == "genuine":
                g += 1
        walk[f"{arm}|{pid}"] = {"genuine": g, "state": state}
    diff = []
    for k, v in walk.items():
        m = mine["if"].get(k)
        if m and (min(m["genuine"], 2) != v["genuine"] or v["state"] != "done"):
            diff.append((k, v, m["genuine"]))
    lines.append("\n(arm, prompt) where the executor's walk differs from mine or stops early:")
    lines += [f"  {k}: executor {v}, mine {g}" for k, v, g in diff]
    out["walk_diff"] = diff
    C.dump(out, "hand_compare.json")
    (C.OUT / "hand_compare.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
