#!/usr/bin/env python3
"""Contamination exclusions (pre-registration Part A, Contamination): olmo_ifomega/contamination.csv -> exclusions.csv.

Rule (IF): content containment >= 0.5 against any RL / DPO / SFT document, or raw containment >= 0.8, or a variant
(the same request with other or no constraints) confirmed by reading among matches with raw or content >= 0.3
(READ below: my reading of every IF prompt in the 0.3-0.5 band, 2026-11-04 20:40 UTC, from the kept windows).
OMEGA: relabelled copies were removed before the draw (build_problems.canon); none remain, so no exclusion.
"""
import csv
from collections import defaultdict

READ = {  # pid -> (variant?, note)
    "ifbench_43": (False, "SFT WildChat doc is another request by the same user (replace bracketed words), not this one"),
    "ifbench_50": (True, "SFT WildChat conversation with this request verbatim (blockchain identity literature review)"),
    "ifbench_73": (True, "SFT WildChat conversation with this request verbatim (SFM body mechanics)"),
    "ifbench_127": (True, "SFT WildChat conversation with this request verbatim (five interpretations)"),
    "ifbench_132": (True, "DPO (filtered_wc_sample_500k) row with this request verbatim (memorization)"),
    "ifbench_140": (True, "SFT WildChat conversation with this request verbatim (hedgehog with glasses)"),
    "ifbench_144": (True, "SFT WildChat conversation containing this proof request (n - p <= m)"),
    "ifbench_159": (True, "DPO (filtered_wc_sample_500k) row with this request verbatim (alternate Lord's Prayer)"),
    "ifbench_190": (True, "DPO (IF_sft_data_verified_permissive) row with the same passage to assess"),
    "ifbench_229": (True, "SFT WildChat conversation with this request verbatim (One Day More / ceasefire)"),
    "ifbench_232": (True, "SFT WildChat conversation with this request verbatim (sewer dweller natal aspect)"),
    "ifbench_244": (True, "SFT WildChat conversation with this request verbatim (no industrial revolution timeline)"),
    "ifbench_248": (False, "SFT doc shares only the quoted song lyric, inside a different request"),
    "ifbench_254": (True, "SFT WildChat conversation with this request verbatim (Sirius watch bands)"),
    "ifbench_263": (True, "SFT WildChat conversation with this request verbatim (gender balance in stories)"),
    "ifbench_289": (True, "SFT WildChat conversation with this request verbatim (hadiths / living tradition)"),
    "ifbench_291": (False, "match is constraint boilerplate (title case) in an unrelated precise-IF prompt"),
    "ifeval_279": (False, "match is IFEval-style constraint boilerplate in an unrelated RL IF prompt"),
    "ifeval_1012": (False, "match is IFEval-style constraint boilerplate (repeat the request; title in << >>)"),
    "ifbench_60": (False, "match is constraint boilerplate (repeat the request ...) in an unrelated RL IF prompt"),
    "ifbench_61": (False, "match is constraint boilerplate (repeat the request ...) in an unrelated RL IF prompt"),
    "ifeval_1139": (False, "match is IFEval-style constraint boilerplate (repeat the request word for word)"),
    "ifeval_1480": (False, "match is IFEval-style constraint boilerplate (repeat the sentence above) in a DPO row"),
    "ifeval_2097": (False, "match is IFEval-style constraint boilerplate (title in << >>) in a DPO row"),
    "ifeval_2305": (False, "match is IFEval-style constraint boilerplate (repeat the request) in a DPO row"),
    "ifeval_2870": (False, "match is IFEval-style constraint boilerplate (words with all capital letters)"),
    "ifeval_3752": (False, "match is IFEval-style constraint boilerplate (exact phrases yes / no / maybe)"),
}

rows = list(csv.DictReader(open("olmo_ifomega/contamination.csv")))
by = defaultdict(list)
for r in rows:
    by[r["pid"]].append(r)
out = []
for pid, rs in by.items():
    if not rs[0]["task"].startswith("if"):
        continue
    hits = [r for r in rs if float(r["max_content"]) >= 0.5 or float(r["max_raw"]) >= 0.8]
    if hits:
        h = max(hits, key=lambda r: float(r["max_content"]))
        out.append({"pid": pid, "task": rs[0]["task"], "reason": f"{h['kind']} content {h['max_content']} raw "
                    f"{h['max_raw']} ({h['best_source']}; doc {h['best_content_doc']})",
                    "corpora": " ".join(sorted(r["kind"] for r in hits))})
    elif pid in READ and READ[pid][0]:
        h = max(rs, key=lambda r: float(r["max_content"]))
        out.append({"pid": pid, "task": rs[0]["task"], "reason": f"variant by reading: {READ[pid][1]} "
                    f"({h['kind']} content {h['max_content']})", "corpora": h["kind"]})
band = {pid for pid, rs in by.items() if rs[0]["task"].startswith("if") and pid not in {o["pid"] for o in out}
        and max(max(float(r["max_content"]), float(r["max_raw"])) for r in rs) >= 0.3}
assert band <= set(READ), sorted(band - set(READ))
out.sort(key=lambda r: (r["task"], int(r["pid"].split("_")[1])))
with open("olmo_ifomega/exclusions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["pid", "task", "reason", "corpora"])
    w.writeheader()
    w.writerows(out)
print(f"{len(out)} exclusions:", {t: sum(o['task'] == t for o in out) for t in ('ifbench', 'ifeval')},
      "| by corpus:", {k: sum(k in o['corpora'] for o in out) for k in ('rl', 'dpo', 'sft')})
