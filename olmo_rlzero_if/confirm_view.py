#!/usr/bin/env python3
"""Compact view of reader labels for my confirmation (olmo-rlzero-if hand gate).

Usage: confirm_view.py <handdir> <batch> [<batch> ...] [--full]
One line per item: id, label, checker_agrees, answer head (genuine items and a seeded 10 % of gamed items, or all with
--full), evidence. Then `confirm_view.py <handdir> --accept <batch> ... [--override id=label:note ...]` appends my
confirmation rows to <handdir>/confirm.csv: the reader's label unless overridden, with the note.
"""
import csv
import json
import random
import re
import sys
from pathlib import Path


def answer_of(md):
    i = md.find("## Answer")
    a = md[md.find("\n", i) + 1:].strip() if i >= 0 else ""
    return re.sub(r"\s+", " ", a)


def main():
    hd = Path(sys.argv[1])
    args = sys.argv[2:]
    if args and args[0] == "--accept":
        bs = [a for a in args[1:] if not a.startswith("--") and "=" not in a]
        ov = {}
        for a in args[1:]:
            if "=" in a:
                k, v = a.split("=", 1)
                lab, _, note = v.partition(":")
                ov[k] = (lab, note)
        cf = hd / "confirm.csv"
        have = {r["item"] for r in csv.DictReader(open(cf))} if cf.exists() else set()
        new = not cf.exists()
        n = 0
        with open(cf, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["item", "label", "note"], lineterminator="\n")
            if new:
                w.writeheader()
            for b in bs:
                for x in json.load(open(hd / "labels" / f"{b}.json")):
                    if x["item"] in have:
                        continue
                    lab, note = ov.get(x["item"], (x["label"], "reader label confirmed"))
                    if x["item"] in ov:
                        note = f"overturned ({x['label']} -> {lab}): {note}"
                    w.writerow({"item": x["item"], "label": lab, "note": note})
                    n += 1
        print(f"confirmed {n} items ({len(ov)} overridden)")
        return
    full = "--full" in args
    bs = [a for a in args if not a.startswith("--")]
    rng = random.Random(20261108)
    for b in bs:
        lab = json.load(open(hd / "labels" / f"{b}.json"))
        for x in lab:
            md = (hd / "items" / f"{x['item']}.md").read_text()
            show = full or x["label"] == "genuine" or rng.random() < 0.10
            ans = answer_of(md)
            head = (ans[:110] + ("…" if len(ans) > 110 else "")) if show else ""
            print(f"{x['item']} {x['label'][:3]} agr={str(x.get('checker_agrees'))[0]} | {head} || {x['evidence'][:230]}")


if __name__ == "__main__":
    main()
