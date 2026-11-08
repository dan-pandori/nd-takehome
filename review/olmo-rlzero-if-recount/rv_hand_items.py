"""Blinded hand-check items from the raw texts (reviewer, olmo-rlzero-if). Selections are mine, from my cells
(out/cells.json, draw order) and my candidate sets (out/stats.json); excluded prompts are skipped.

  round 1 (non-adaptive):  main on every reach candidate R: the first two strict successes in the pre-registered
                           reading order (the first two fixed-phase ones, then fresh C1_main ones in draw order, then
                           the remaining fixed ones) = the "first-read" set of the gamed share;
                           base on every R: every strict success within its first 256 draws;
                           controls: 8 swapped-prompt items (a real success shown under another prompt with the same
                           constraint ids and kwargs, the checker re-run to pass: the request is not done -> gamed) and
                           8 duplicates (the same item twice under two ids).
  round N >= 2 (need file): further main successes in reading order where my rv_hand.py says a prompt needs them;
                           diagnostic models (base_btok, math, s0100, s0500) on the prompts named.
Items go to ~/review/rzi_rv/hand/items/<batch>.md (not committed; regenerable), the key to hand/key_r<N>.json, the
batch index to hand/batches_r<N>.json.
Usage: rv_hand_items.py 1 | rv_hand_items.py N hand/need_rN.json"""
import hashlib
import json
import os
import random
import sys
from collections import defaultdict

import rv_core as C
import rv_graders as G
from rv_cells import EXCL

HAND = os.path.join(C.HERE, "hand")
ITEMS = os.path.join(C.BIG, "hand", "items")
MAX_ITEMS, MAX_CHARS = 30, 110_000


def reading_order(cell):
    """main (challenger) successes within 256 in the pre-registered reading order: [(draw1, job, chunk, i, fresh)]"""
    d = cell[:256]
    fx = [(k + 1, x[0], x[1], x[2], False) for k, x in enumerate(d) if x[3] and x[0].startswith("F_")]
    fr = [(k + 1, x[0], x[1], x[2], True) for k, x in enumerate(d) if x[3] and not x[0].startswith("F_")]
    return fx[:2] + fr + fx[2:]


def base_succ(cell):
    return [(k + 1, x[0], x[1], x[2], not x[0].startswith("F_")) for k, x in enumerate(cell[:256]) if x[3]]


def fetch_texts(need):
    by_job = defaultdict(set)
    for job, ch, i, pid in need:
        by_job[job].add((ch, i, pid))
    out = {}
    for job, want in by_job.items():
        for r in C.iter_rows(job):
            k = (r["chunk"], r["i"], r["pid"])
            if k in want:
                out[(job,) + k] = r["text"]
    return out


def con_block(prob):
    out = []
    for iid, kw in zip(prob["instruction_id_list"], prob["kwargs"]):
        kw = {a: b for a, b in dict(kw or {}).items() if b is not None}
        out.append(f"- `{iid}` {json.dumps(kw, ensure_ascii=False)}")
    return "\n".join(out)


def select_round1(cells, st):
    sel = []
    for task in ("ifbench", "ifeval"):
        for p in st["cands"][task]["R"]:
            if p in EXCL:
                continue
            for rank, x in enumerate(reading_order(cells["main"][p])[:2]):
                sel.append({"task": task, "pid": p, "model": "main", "side": "R_main", "read_rank": rank + 1,
                            "draw": x[0], "job": x[1], "chunk": x[2], "i": x[3], "fresh": x[4]})
            for rank, x in enumerate(base_succ(cells["base"][p])):
                sel.append({"task": task, "pid": p, "model": "base", "side": "R_base", "read_rank": rank + 1,
                            "draw": x[0], "job": x[1], "chunk": x[2], "i": x[3], "fresh": x[4]})
    return sel


def select_need(cells, need):
    """need: [{"pid", "model", "ranks": [..]}] -> items (main: reading order; others: strict successes in draw order)"""
    sel = []
    P = C.load_problems()
    for n in need:
        p, m = n["pid"], n["model"]
        # challengers (main, s0100, s0500) in the reading order; diagnostics (base_btok, math) in draw order
        lst = reading_order(cells[m][p]) if m in ("main", "s0100", "s0500") else \
            [(k + 1, x[0], x[1], x[2], True) for k, x in enumerate(cells[m][p]) if x[3]]
        for rank in n["ranks"]:
            if rank <= len(lst):
                x = lst[rank - 1]
                sel.append({"task": P[p]["task"], "pid": p, "model": m, "side": n.get("side", f"R_{m}"),
                            "read_rank": rank, "draw": x[0], "job": x[1], "chunk": x[2], "i": x[3], "fresh": x[4]})
    return sel


def write_items(rnd_no, sel, P, controls):
    rnd = random.Random(20261108 + rnd_no)
    texts = fetch_texts({(s["job"], s["chunk"], s["i"], s["pid"]) for s in sel})
    items = []
    for s in sel:
        items.append(dict(s, text=texts[(s["job"], s["chunk"], s["i"], s["pid"])], kind="real"))
    if controls:
        real = list(items)
        for x in rnd.sample(real, 8):
            items.append(dict(x, kind="duplicate"))
        sig = defaultdict(list)
        for p, r in P.items():
            if p not in EXCL:
                sig[json.dumps([r["instruction_id_list"], r["kwargs"]], sort_keys=True)].append(p)
        made = 0
        for x in rnd.sample(real, len(real)):
            s = json.dumps([P[x["pid"]]["instruction_id_list"], P[x["pid"]]["kwargs"]], sort_keys=True)
            others = [q for q in sig[s] if q != x["pid"]]
            if not others:
                continue
            q = rnd.choice(others)
            ans = C.remove_thinking_section(x["text"])
            if ans and G.if_check(P[q]["task"], P[q], ans)[0]:
                items.append(dict(x, kind="swapped", pid=q, task=P[q]["task"], swapped_from=x["pid"]))
                made += 1
            if made >= 8:
                break
    rnd.shuffle(items)
    key = {}
    for x in items:
        h = hashlib.sha1(f"{rnd_no}|{x['kind']}|{x['pid']}|{x['model']}|{x['job']}|{x['chunk']}|{x['i']}".encode())
        x["id"] = f"q{rnd_no}-{h.hexdigest()[:6]}"
        key[x["id"]] = {k: v for k, v in x.items() if k != "text"}
    # pack into batches by count and characters
    batches, cur, size = [], [], 0
    for x in items:
        n = len(x["text"]) + len(P[x["pid"]]["prompt"]) + 400
        if cur and (len(cur) >= MAX_ITEMS or size + n > MAX_CHARS):
            batches.append(cur)
            cur, size = [], 0
        cur.append(x)
        size += n
    if cur:
        batches.append(cur)
    os.makedirs(ITEMS, exist_ok=True)
    index = []
    for bi, xs in enumerate(batches):
        name = f"q{rnd_no}_{bi:02d}"
        md = [f"# Batch {name}: {len(xs)} items\n"]
        for x in xs:
            pr = P[x["pid"]]
            ans = C.remove_thinking_section(x["text"])
            note = ("the response closed its reasoning with `</think>`; the graded answer is the text after it"
                    if "</think>" in x["text"] else
                    "the response never closed its reasoning; the graded answer is the whole response")
            md.append(f"## Item {x['id']}\n\n### Prompt\n\n{pr['prompt']}\n\n### Constraints (checker id and parameters; "
                      f"the official checker judged every one followed)\n\n{con_block(pr)}\n\n### Graded answer "
                      f"({note}; {len(ans)} characters)\n\n<<<ANSWER\n{ans}\nANSWER>>>\n")
            key[x["id"]]["batch"] = name
        open(os.path.join(ITEMS, f"{name}.md"), "w").write("\n---\n\n".join(md))
        index.append({"batch": name, "n": len(xs), "chars": sum(len(x["text"]) for x in xs),
                      "ids": [x["id"] for x in xs]})
    os.makedirs(HAND, exist_ok=True)
    json.dump(key, open(os.path.join(HAND, f"key_r{rnd_no}.json"), "w"), indent=0)
    json.dump(index, open(os.path.join(HAND, f"batches_r{rnd_no}.json"), "w"), indent=0)
    print(f"round {rnd_no}: {len(items)} items ({sum(x['kind'] == 'real' for x in items)} real) in {len(batches)} batches:",
          [(b["batch"], b["n"], b["chars"]) for b in index])


def main():
    P = C.load_problems()
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    rnd_no = int(sys.argv[1])
    if rnd_no == 1:
        st = json.load(open(os.path.join(C.OUT, "stats.json")))
        write_items(1, select_round1(cells, st), P, controls=True)
    else:
        need = json.load(open(sys.argv[2]))
        write_items(rnd_no, select_need(cells, need), P, controls=False)


if __name__ == "__main__":
    main()
