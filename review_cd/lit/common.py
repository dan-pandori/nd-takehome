"""Shared helpers for the literature audit (review of run capability-defs). Read-only on inputs."""
import os
import re
import unicodedata

LIT = os.path.expanduser("~/review/capability-defs/capability_defs/lit")
SRC = os.path.expanduser("~/cd_sources")
PRIOR_DIRS = [os.path.expanduser("~/nd-rl/docs/literature/2026-09-29-lit-review"),
              os.path.expanduser("~/nd-rl/docs/literature/2026-10-02-lit-review-2")]
OUT = os.path.expanduser("~/review/capability-defs/review_cd/lit")

ARXIV_RE = re.compile(r"(?<![\d.])(\d{2})(\d{2})\.(\d{4,5})(v\d+)?(?!\d)")
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s|,;`'\"<>\]]+")
URL_RE = re.compile(r"https?://[^\s|`'\"<>\)]+")


def arxiv_ids(text):
    """arXiv new-style ids (without version) in text; month 01-12, year 07-26."""
    out = []
    for m in ARXIV_RE.finditer(text):
        yy, mm = int(m.group(1)), int(m.group(2))
        if 7 <= yy <= 26 and 1 <= mm <= 12:
            out.append(f"{m.group(1)}{m.group(2)}.{m.group(3)}")
    return out


def dois(text):
    out = []
    for m in DOI_RE.finditer(text):
        d = m.group(0).rstrip(").,;:").lower()
        out.append(d)
    return out


def urls(text):
    return [u.rstrip(").,;:").lower().replace("http://", "https://").replace("www.", "").rstrip("/")
            for u in URL_RE.findall(text)]


def norm_title(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace("&", " and ")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def table_rows(path):
    """Rows of all markdown tables in a file: list of (line_no, [cells]). Skips header/separator rows."""
    rows = []
    lines = open(path, encoding="utf-8").read().split("\n")
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        # split on unescaped pipes
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", s)[1:-1]]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append((i, cells))
    return rows


def clean_title_cell(cell):
    """Strip note references and trailing '(Author)' from a screened-table title cell."""
    t = re.split(r"\s+[—–]\s+", cell)[0]          # drop " — note `x.md`" etc.
    t = re.sub(r"\s*\[@[^\]]*\]", "", t)
    # drop trailing parenthetical(s) holding the author / remarks
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r"\s*\([^()]*\)\s*$", "", t)
    return t.strip()
