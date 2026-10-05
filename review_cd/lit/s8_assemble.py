"""Assemble LIT_AUDIT.md from LIT_AUDIT.src.md and the generated tables in s7_tables.md; report the summary's word
count (limit 200) and the L2 section's word count (limit 150)."""
import re

from common import OUT

src = open(f"{OUT}/LIT_AUDIT.src.md", encoding="utf-8").read()
t4, t5 = open(f"{OUT}/s7_tables.md", encoding="utf-8").read().strip().split("\n\n")
doc = src.replace("<!-- TABLE4 -->", t4).replace("<!-- TABLE5 -->", t5)
open(f"{OUT}/LIT_AUDIT.md", "w", encoding="utf-8").write(doc)


def words(section):
    body = re.search(rf"## {re.escape(section)}.*?\n(.*?)(?=\n## )", doc, re.S).group(1)
    return len(re.findall(r"\S+", body))


print("summary words:", words("Summary"), "| L2 words:", words("6. L2 (summary, ≤ 150 words)"))
print("tables inserted:", t4.count("\n| S"), "claim rows;", t5.count("\n| R"), "sentence rows")
