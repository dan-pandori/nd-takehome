"""Task 5: seeded random sample (random.Random(20261005)) of 12 sentences in REVIEW.md that cite a paper; for each,
list ledger rows whose claim text shares a quoted fragment or a number with the sentence (aid for manual tracing).
Scope: the 'Bottom line' and sections 1-6 (lines from '## Bottom line' up to the pre-registration table); the
header counts, the pre-registration table and the file list are about the run, not papers, and are excluded.
Writes s5_candidates.txt and s5_sample.txt."""
import json
import random
import re

from common import LIT, OUT

ledger = json.load(open(f"{OUT}/s2_claims.json"))
lines = open(f"{LIT}/REVIEW.md", encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## Bottom line"))
stop = next(i for i, l in enumerate(lines) if l.startswith("## Pre-registered expectations"))

# group lines into blocks (a bullet / numbered item plus its continuation lines)
blocks = []
cur = None
for i in range(start + 1, stop):
    l = lines[i]
    s = l.strip()
    if not s or s.startswith("#"):
        cur = None
        continue
    if re.match(r"^(\s*)([-*]|\d+\.)\s+", l) or cur is None:
        cur = [i + 1, s]
        blocks.append(cur)
    else:
        cur[1] += " " + s
ABBR = ["et al.", "Sec.", "Eq.", "App.", "Fig.", "Thm.", "e.g.", "i.e.", "vs.", "Prop.", "Def.", "No.", "cf."]


def split_sentences(text):
    t = text
    for k, a in enumerate(ABBR):
        t = t.replace(a, a.replace(".", f"<D{k}>"))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(*])", t)
    out = []
    for p in parts:
        for k, a in enumerate(ABBR):
            p = p.replace(a.replace(".", f"<D{k}>"), a)
        out.append(p.strip())
    return out


CITE = re.compile(r"(et al\.|[A-Z][a-zäöüé\-]+ & [A-Z][a-zäöüé\-]+|[A-Z][a-zäöüé\-]+ (19|20)\d\d\b|\(\d{4}\)|"
                  r"\b\d{4}\.\d{4,5}\b|SEP \"|Anthropic's RSP|Hernández-Orallo|Firestone|Burden|Harding|Korbak|"
                  r"METR|URIAL|PassUntil|Skill-Mix|ADeLe|tinyBenchmarks|Wright & Linacre)")
cands = []
for ln, text in blocks:
    for s in split_sentences(re.sub(r"^([-*]|\d+\.)\s+", "", text)):
        if CITE.search(s) and len(s) > 25:
            cands.append((ln, s))
with open(f"{OUT}/s5_candidates.txt", "w", encoding="utf-8") as fh:
    for k, (ln, s) in enumerate(cands, 1):
        fh.write(f"{k}\tL{ln}\t{s}\n")
rng = random.Random(20261005)
pick = sorted(rng.sample(range(len(cands)), 12))


def nums(s):
    return set(re.findall(r"\d+(?:[.,]\d+)?", s))


out = [f"candidate sentences citing a paper: {len(cands)}; sampled 12 (indices {[p + 1 for p in pick]})"]
for p in pick:
    ln, s = cands[p]
    out.append("=" * 90)
    out.append(f"R{p + 1} (REVIEW.md block starting line {ln}): {s}")
    qs = [q for q in re.findall(r"[\"“]([^\"”]{8,})[\"”]", s)]
    hits = []
    for r in ledger:
        c = r["claim"].lower()
        score = 0
        for q in qs:
            frag = q.lower().split("…")[0][:40]
            if frag and frag in c:
                score += 3
        common = (nums(s) & nums(r["claim"])) - {"1", "2", "3", "4", "5", "0", "10", "100"}
        score += len(common)
        if score >= 2 or (qs and score >= 3):
            hits.append((score, r["reader"], r["n"], r["pid"][:28], r["status"], r["loc"][:40], r["claim"][:160]))
    for h in sorted(hits, reverse=True)[:6]:
        out.append(f"   ledger candidate: score={h[0]} {h[1]} #{h[2]} {h[3]} [{h[4]}] loc={h[5]} | {h[6]}")
open(f"{OUT}/s5_sample.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
