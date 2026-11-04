"""Phase 2 (reviewer): join the executor's hand-check table (olmo32/handcheck.csv) to my items on
(job, pid, chunk, i); compare labels item by item with my readers' labels and my strict / exec_rule classes."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
key = json.load(open(os.path.join(HERE, "hand", "key.json")))
conf = json.load(open(os.path.join(HERE, "hand", "confirm.json")))
lab = {}
import glob
for f in glob.glob(os.path.join(HERE, "hand", "reader_labels", "*.json")):
    for r in json.load(open(f)):
        lab[r["item"]] = r["label"]
mine = {(k["job"], k["pid"], int(k["chunk"]), int(k["i"])): (i, k) for i, k in key.items()}
ex = list(csv.DictReader(open(os.path.join(ROOT, "olmo32", "handcheck.csv"))))
rows = []; only_ex = []
for r in ex:
    k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
    if k in mine:
        i, kk = mine[k]
        rows.append((kk["model"], kk["pid"], kk["draw"], "D" if (kk["rl"] and kk["final"]) else "rl", r["item"], i,
                     r["reader_label"], r["final_label"], r.get("strict_label") or "", lab[i], conf[i]["class"],
                     conf[i]["strict"], conf[i]["exec_rule"]))
    else:
        only_ex.append((r["model"], r["pid"], r["job"], r["chunk"], r["i"], r["role"], r["final_label"]))
ex_keys = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])) for r in ex}
only_mine = [(k[1]["model"], k[1]["pid"], k[1]["draw"], k[0]) for kk, k in mine.items() if kk not in ex_keys]
print("executor columns:", list(ex[0].keys()))
print(f"executor items {len(ex)}, mine {len(key)}, common {len(rows)}")
print("model pid draw kind | exec_item my_item | exec_reader exec_final | my_reader my_class my_strict my_exec_rule")
for r in sorted(rows):
    flag = "" if r[7] == r[12] else "  <-- executor final vs my exec_rule differ"
    print(" ".join(str(x) for x in r) + flag)
print("only in executor's set:", only_ex)
print("only in mine:", sorted(only_mine))

# executor's strict reading, derived from its notes: uniform-sound items whose note says the strict reading is flawed
print()
strict_ex = {}
for r in ex:
    s = r["final_label"]
    if s == "sound" and ("strict" in r["my_note"] or "minor gap" in r["my_note"]):
        s = "flawed"
    strict_ex[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))] = (r["item"], s)
agree = dis = 0
for k, (it, s) in sorted(strict_ex.items()):
    if k in mine:
        i, kk = mine[k]
        m = conf[i]["strict"]
        agree += m == s; dis += m != s
        if m != s:
            print("strict differs:", kk["model"], kk["pid"], kk["draw"], it, i, "exec", s, "mine", m)
print(f"strict reading, common items: agree {agree}, differ {dis}")
import collections
c = collections.Counter((r["model"], r["pid"], strict_ex[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))][1]) for r in ex)
print("executor strict counts:", sorted(c.items()))
