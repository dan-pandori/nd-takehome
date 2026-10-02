"""Fetch an arXiv paper as plain text for grep-based claim checking (lit-review run).

    /tmp/lrvenv/bin/python lit_review/fetch.py 2506.02355          # latest version
    /tmp/lrvenv/bin/python lit_review/fetch.py 2506.02355v2 --abs  # abstract page only

Writes ~/lr_sources/<id>.txt (full text: arXiv HTML if it exists, else the PDF via pdfminer) or
~/lr_sources/<id>.abs.txt, and prints the resolved version, title, and which source was used.
Sources stay outside the repository (copyrighted text); REVIEW.md cites id + version + section,
so a reviewer can re-fetch and grep the same text.
"""
import html
import io
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

OUT = os.path.expanduser("~/lr_sources")
UA = {"User-Agent": "Mozilla/5.0 (lit-review; dantweinand research)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.geturl()


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
        elif tag == "img" or tag == "math":
            alt = dict(attrs).get("alttext") or dict(attrs).get("alt")
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

    def handle_startendtag(self, tag, attrs):
        if tag == "math":
            alt = dict(attrs).get("alttext")
            if alt:
                self.out.append(f" {alt} ")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def html_text(raw):
    # keep LaTeX alttext of <math> elements: replace the element with its alttext before parsing
    s = raw.decode("utf-8", "replace")
    s = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>',
               lambda m: " $" + html.unescape(m.group(1)) + "$ ", s, flags=re.S)
    p = Text()
    p.feed(s)
    t = "".join(p.out)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t


def main():
    aid = sys.argv[1].replace("arxiv:", "")
    os.makedirs(OUT, exist_ok=True)
    raw, _ = get(f"https://arxiv.org/abs/{aid}")
    page = raw.decode("utf-8", "replace")
    title = re.search(r'<meta name="citation_title" content="([^"]*)"', page)
    ver = re.findall(r"/abs/[0-9.]+(v\d+)", page)
    vers = sorted(set(ver), key=lambda v: int(v[1:]))
    latest = aid if re.search(r"v\d+$", aid) else aid + (vers[-1] if vers else "")
    date = re.search(r'<meta name="citation_date" content="([^"]*)"', page)
    head = (f"id {latest}  title {html.unescape(title.group(1)) if title else '?'}  "
            f"date {date.group(1) if date else '?'}")
    if "--abs" in sys.argv:
        path = f"{OUT}/{aid}.abs.txt"
        open(path, "w").write(head + "\n\n" + html_text(raw))
        print(head, "->", path, "(abs)")
        return
    path = f"{OUT}/{aid}.txt"
    src = None
    for _ in range(3):
        try:
            raw, url = get(f"https://arxiv.org/html/{latest}")
            t = html_text(raw)
            if len(t) > 5000 and "No HTML for" not in t:
                src = "html"
            break
        except Exception:
            pass
    if src is None:
        from pdfminer.high_level import extract_text
        raw, _ = get(f"https://arxiv.org/pdf/{latest}")
        pages = extract_text(io.BytesIO(raw)).split("\f")
        t = "\n".join(f"\n[[page {i + 1}]]\n" + p for i, p in enumerate(pages))
        src = "pdf"
    open(path, "w").write(head + f"\nsource: {src}\n\n" + t)
    print(head, "->", path, f"({src}, {len(t.split())} words)")


if __name__ == "__main__":
    main()
