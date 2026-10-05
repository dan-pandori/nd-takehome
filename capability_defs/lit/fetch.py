"""Fetch a paper as plain text for grep-based claim checking (run capability-defs).

Adapted from lit-review's lit_review/fetch.py (fork branch dan_lit-review), plus a --url mode for
sources that are not on arXiv, and a lock so that parallel readers download one at a time.

    python3 capability_defs/lit/fetch.py 2506.02355           # arXiv, latest version (HTML, else PDF)
    python3 capability_defs/lit/fetch.py 2506.02355v2 --abs   # abstract page only
    python3 capability_defs/lit/fetch.py --url https://.../paper.pdf --name harding2024-capability

Writes ~/cd_sources/<id or name>.txt and prints the resolved version, title and source type.
Full texts stay outside the repository (copyright); notes cite id + version + section/page so a
reviewer can re-fetch and grep the same text. PDF text carries [[page N]] markers.
"""
import fcntl
import html
import io
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from html.parser import HTMLParser

OUT = os.path.expanduser("~/cd_sources")
UA = {"User-Agent": "Mozilla/5.0 (capability-defs literature review; research use)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read(), r.geturl(), r.headers.get("Content-Type", "")


class Text(HTMLParser):
    SKIP = {"script", "style", "math", "annotation", "nav", "header", "footer"}
    BLOCK = {"p", "div", "section", "h1", "h2", "h3", "h4", "h5", "li", "tr", "br", "table",
             "figcaption", "caption", "td", "th"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.out.append(f" {alt} ")
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def html_text(raw):
    s = raw.decode("utf-8", "replace")
    s = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>',
               lambda m: " $" + html.unescape(m.group(1)) + "$ ", s, flags=re.S)
    p = Text()
    p.feed(s)
    t = "".join(p.out)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t


def pdf_text(raw):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(raw)
        f.flush()
        try:
            t = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True,
                               timeout=300).stdout.decode("utf-8", "replace")
        except Exception:
            from pdfminer.high_level import extract_text
            t = extract_text(io.BytesIO(raw))
    pages = t.split("\f")
    return "\n".join(f"\n[[page {i + 1}]]\n" + p for i, p in enumerate(pages))


def locked(fn):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, ".lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # one download at a time across all readers
        try:
            return fn()
        finally:
            time.sleep(1)
            fcntl.flock(lk, fcntl.LOCK_UN)


def fetch_url(url, name):
    path = f"{OUT}/{name}.txt"
    raw, final, ctype = get(url)
    if raw[:5] == b"%PDF-" or "pdf" in ctype.lower():
        t, src = pdf_text(raw), "pdf"
    else:
        t, src = html_text(raw), "html"
    open(path, "w").write(f"url {final}\nsource: {src}\n\n" + t)
    print(f"{name} <- {final} -> {path} ({src}, {len(t.split())} words)")


def fetch_arxiv(aid, abs_only):
    raw, _, _ = get(f"https://arxiv.org/abs/{aid}")
    page = raw.decode("utf-8", "replace")
    title = re.search(r'<meta name="citation_title" content="([^"]*)"', page)
    vers = sorted(set(re.findall(r"/abs/[0-9.]+(v\d+)", page)), key=lambda v: int(v[1:]))
    latest = aid if re.search(r"v\d+$", aid) else aid + (vers[-1] if vers else "")
    date = re.search(r'<meta name="citation_date" content="([^"]*)"', page)
    head = (f"id {latest}  title {html.unescape(title.group(1)) if title else '?'}  "
            f"date {date.group(1) if date else '?'}")
    if abs_only:
        path = f"{OUT}/{aid}.abs.txt"
        open(path, "w").write(head + "\n\n" + html_text(raw))
        print(head, "->", path, "(abs)")
        return
    path = f"{OUT}/{aid}.txt"
    src, t = None, ""
    for _ in range(2):
        try:
            raw, _, _ = get(f"https://arxiv.org/html/{latest}")
            t = html_text(raw)
            if len(t) > 5000 and "No HTML for" not in t:
                src = "html"
            break
        except Exception:
            time.sleep(3)
    if src is None:
        raw, _, _ = get(f"https://arxiv.org/pdf/{latest}")
        t, src = pdf_text(raw), "pdf"
    open(path, "w").write(head + f"\nsource: {src}\n\n" + t)
    print(head, "->", path, f"({src}, {len(t.split())} words)")


def main():
    a = sys.argv[1:]
    if "--url" in a:
        url, name = a[a.index("--url") + 1], a[a.index("--name") + 1]
        locked(lambda: fetch_url(url, name))
    else:
        aid = a[0].replace("arxiv:", "").replace("arXiv:", "")
        locked(lambda: fetch_arxiv(aid, "--abs" in a))


if __name__ == "__main__":
    main()
