"""Format-check items (Design 6), my own draw: on each prompt given, up to 4 base strict failures from different
extension chunks (fixed phase if fewer) and up to 2 main failures, random.Random(20261108) in sorted pid order;
binding constraint = the constraint the model fails most often on that prompt over all its draws within 256.
Answers longer than 12,000 characters are shown as the first 8,000 and the last 4,000 with the omission marked.
Items to ~/review/rzi_rv/fail/items/<batch>.md, key to hand/fail_key.json, batches to hand/fail_batches.json.
Usage: rv_fail_items.py pid [pid ...]"""
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

import rv_core as C
from rv_hand_items import con_block, fetch_texts

ITEMS = os.path.join(C.BIG, "fail", "items")


def per_of(job):
    out = {}
    for r in map(json.loads, open(os.path.join(C.OUT, "regrade", f"{job}.jsonl"))):
        out[(r["pid"], r["chunk"], r["i"])] = (r["per"], r["finish"], r["n_tok"])
    return out


def main():
    pids = sorted(sys.argv[1:])
    P = C.load_problems()
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    rnd = random.Random(20261108)
    sel = []
    pers = {}
    for p in pids:
        for model, k in (("base", 4), ("main", 2)):
            d = cells[model][p][:256]
            fails = [x for x in d if not x[3]]
            for j in {x[0] for x in d}:
                if j not in pers:
                    pers[j] = per_of(j)
            cnt = Counter()
            for x in d:
                for ci, ok in enumerate(pers[x[0]][(p, x[1], x[2])][0]):
                    cnt[ci] += not ok
            binding = max(cnt, key=lambda c: (cnt[c], -c)) if cnt else 0
            if model == "base":
                ext = defaultdict(list)
                for x in fails:
                    if not x[0].startswith("F_"):
                        ext[(x[0], x[1])].append(x)
                groups = sorted(ext)
                pick = [rnd.choice(ext[g]) for g in rnd.sample(groups, min(k, len(groups)))]
                if len(pick) < k:
                    fx = [x for x in fails if x[0].startswith("F_")]
                    pick += rnd.sample(fx, min(k - len(pick), len(fx)))
            else:
                pick = rnd.sample(fails, min(k, len(fails)))
            for x in pick:
                per, fin, nt = pers[x[0]][(p, x[1], x[2])]
                sel.append({"pid": p, "task": P[p]["task"], "model": model, "job": x[0], "chunk": x[1], "i": x[2],
                            "per": per, "finish": fin, "n_tok": nt, "binding": binding,
                            "binding_id": P[p]["instruction_id_list"][binding],
                            "fail_rate_binding": cnt[binding] / max(1, len(d))})
    texts = fetch_texts({(s["job"], s["chunk"], s["i"], s["pid"]) for s in sel})
    rnd.shuffle(sel)
    key, batches, cur, size = {}, [], [], 0
    for s in sel:
        s["text"] = texts[(s["job"], s["chunk"], s["i"], s["pid"])]
        h = hashlib.sha1(f"fail|{s['pid']}|{s['model']}|{s['job']}|{s['chunk']}|{s['i']}".encode()).hexdigest()
        s["id"] = f"f-{h[:6]}"
        key[s["id"]] = {k: v for k, v in s.items() if k != "text"}
        n = min(len(s["text"]), 12400) + len(P[s["pid"]]["prompt"]) + 600
        if cur and (len(cur) >= 12 or size + n > 110_000):
            batches.append(cur)
            cur, size = [], 0
        cur.append(s)
        size += n
    if cur:
        batches.append(cur)
    os.makedirs(ITEMS, exist_ok=True)
    index = []
    for bi, xs in enumerate(batches):
        name = f"fail_{bi:02d}"
        md = [f"# Format-check batch {name}: {len(xs)} items\n"]
        for s in xs:
            pr = P[s["pid"]]
            ans = C.remove_thinking_section(s["text"])
            shown = ans if len(ans) <= 12000 else (ans[:8000] + f"\n[... {len(ans) - 12000} characters omitted ...]\n"
                                                    + ans[-4000:])
            verdicts = "\n".join(f"- `{iid}`: checker says {'followed' if ok else 'NOT followed'}"
                                 for iid, ok in zip(pr["instruction_id_list"], s["per"]))
            note = ("closed its reasoning with `</think>`; graded answer = the text after it" if "</think>" in s["text"]
                    else "never closed its reasoning; graded answer = the whole response")
            cut = "it was cut at the 16,384-token cap" if s["finish"] == "length" else "it ended on its own"
            md.append(f"## Item {s['id']}\n\n### Prompt\n\n{pr['prompt']}\n\n### Constraints (id and parameters)\n\n"
                      f"{con_block(pr)}\n\n### Checker verdicts\n\n{verdicts}\n\n### Binding constraint\n\n"
                      f"`{s['binding_id']}`\n\n### Graded answer (the response {note}; {cut}; {len(ans)} characters)\n\n"
                      f"<<<ANSWER\n{shown}\nANSWER>>>\n")
            key[s["id"]]["batch"] = name
        open(os.path.join(ITEMS, f"{name}.md"), "w").write("\n---\n\n".join(md))
        index.append({"batch": name, "n": len(xs), "ids": [x["id"] for x in xs]})
    json.dump(key, open(os.path.join(C.HERE, "hand", "fail_key.json"), "w"), indent=0)
    json.dump(index, open(os.path.join(C.HERE, "hand", "fail_batches.json"), "w"), indent=0)
    print(len(sel), "items in", len(batches), "batches", [(b["batch"], b["n"]) for b in index])


if __name__ == "__main__":
    main()
