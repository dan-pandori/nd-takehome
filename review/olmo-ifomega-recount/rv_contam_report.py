"""Contamination report from my scans (~/review/oif_rv/contam/{rl,dpo,sft}.json) against the executor's exclusion
list (olmo_ifomega/exclusions.csv) and its per-prompt maxima (olmo_ifomega/contamination.csv).
Exclusion rule (pre-registration, IF): content >= 0.5 against any document, raw >= 0.8, or a variant confirmed by
reading among matches with raw or content >= 0.3. Prints, per corpus: prompts over the automatic thresholds, prompts in
the 0.3 band, and the agreement with the executor's list. Output: out/contam_report.txt, out/contam_mine.csv"""
import csv
import json
import os
from collections import defaultdict

import rv_core as C


def main():
    P = C.load_problems()
    ex = {r["pid"]: r for r in csv.DictReader(open(os.path.join(C.WS, "olmo_ifomega", "exclusions.csv")))}
    theirs = defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(C.WS, "olmo_ifomega", "contamination.csv"))):
        theirs[r["pid"]][r["kind"]] = r
    mine = {}
    for k in ("rl", "dpo", "sft"):
        fn = os.path.join(C.BIG, "contam", f"{k}.json")
        if os.path.exists(fn):
            mine[k] = json.load(open(fn))
    lines = []
    rows = []
    auto, band = defaultdict(set), defaultdict(set)
    for k, res in mine.items():
        lines.append(f"== {k}: {res['docs_scanned']} documents scanned")
        for p, v in res["prompts"].items():
            raw = v["top_raw"][0][0] if v["top_raw"] else 0.0
            con = v["top_content"][0][1] if v["top_content"] else 0.0
            braw = v["top_raw"][0][2] if v["top_raw"] else ""
            bcon = v["top_content"][0][2] if v["top_content"] else ""
            t = theirs.get(p, {}).get(k, {})
            rows.append({"pid": p, "task": P[p]["task"], "corpus": k, "max_raw": raw, "max_content": con,
                         "best_raw_doc": braw, "best_content_doc": bcon,
                         "exec_max_raw": t.get("max_raw", ""), "exec_max_content": t.get("max_content", ""),
                         "exec_best_raw_doc": t.get("best_raw_doc", ""), "excluded": int(p in ex)})
            if not P[p]["task"].startswith("if"):
                continue
            if con >= 0.5 or raw >= 0.8:
                auto[k].add(p)
            elif con >= 0.3 or raw >= 0.3:
                band[k].add(p)
    with open(os.path.join(C.OUT, "contam_mine.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    allauto = set().union(*auto.values()) if auto else set()
    allband = set().union(*band.values()) - allauto if band else set()
    exset = set(ex)
    lines.append(f"executor excluded {len(exset)} ({sorted({P[p]['task'] for p in exset})})")
    for k in mine:
        lines.append(f"{k}: over automatic thresholds {len(auto[k])}; 0.3 band {len(band[k])}")
    lines.append(f"my automatic set (any corpus scanned) {len(allauto)}; in executor's list {len(allauto & exset)};"
                 f" not in it: {sorted(allauto - exset)}")
    lines.append(f"executor's exclusions not over my automatic thresholds: {len(exset - allauto)} -> "
                 f"in my 0.3 band {len((exset - allauto) & allband)}, below 0.3 in my scans {sorted(exset - allauto - allband)}")
    lines.append(f"my 0.3-band prompts not excluded by the executor: {sorted(allband - exset)}")
    # agreement of maxima where both scanned (rl)
    import statistics
    for k in mine:
        d = [abs(float(r["max_raw"]) - float(r["exec_max_raw"])) for r in rows if r["corpus"] == k and r["exec_max_raw"] != ""]
        if d:
            lines.append(f"{k}: |my raw max - executor raw max| median {statistics.median(d):.3f}, max {max(d):.3f}, n {len(d)}")
    open(os.path.join(C.OUT, "contam_report.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
