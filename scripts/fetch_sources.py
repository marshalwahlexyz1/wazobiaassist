"""Download the official pages listed in domains/*/sources.txt and save each one
as a DRAFT source document for a human to review.

    python -m scripts.fetch_sources                 # all domains
    python -m scripts.fetch_sources health civic    # some domains

sources.txt format, one source per line (several lines may share a file name):

    cassava-production | IITA | https://www.iita.org/.../Growing_cassava.pdf

Each file is saved as domains/<domain>/docs/_fetched-<file>.md. The assistant
ignores files starting with "_". To approve a draft, a teammate:
  1. opens the official page and checks the text against it,
  2. deletes menus, adverts and anything off-topic (keep the "Source:" first line),
  3. renames it to <file>.md (drop "_fetched-").
If a hand-written _draft-<file>.md exists too, compare the two and keep one.
Approved files are never overwritten.
"""

import io
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser

import httpx

from app.config import Settings

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "button"}
BLOCK_TAGS = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article", "table"}
HEADERS = {"User-Agent": "Mozilla/5.0 (WazobiaAssist source collector; NAIC 2026)"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")
        if tag == "li" and not self.skip_depth:
            self.parts.append("- ")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def tidy(text: str) -> str:
    """Collapses whitespace and drops very short fragments (menu items, labels)."""
    paragraphs = []
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s+", " ", para).strip()
        if len(para) >= 40 or para.startswith("- ") or re.match(r"^\d+[.)] ", para):
            paragraphs.append(para)
    return "\n\n".join(paragraphs)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return tidy("".join(parser.parts))


def pdf_to_text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return tidy("\n\n".join(page.extract_text() or "" for page in reader.pages))


def fetch(url: str, client: httpx.Client) -> str:
    r = client.get(url)
    r.raise_for_status()
    kind = r.headers.get("content-type", "")
    if "pdf" in kind or url.lower().endswith(".pdf"):
        return pdf_to_text(r.content)
    return html_to_text(r.text)


def read_sources(path) -> dict[str, list[tuple[str, str]]]:
    files = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, org, url = (part.strip() for part in line.split("|", 2))
        files[name].append((org, url))
    return files


def main() -> None:
    root = Settings().domains_dir
    wanted = set(sys.argv[1:])
    report = []
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60) as client:
        for sources in sorted(root.glob("*/sources.txt")):
            domain = sources.parent.name
            if wanted and domain not in wanted:
                continue
            docs = sources.parent / "docs"
            for name, items in read_sources(sources).items():
                if (docs / f"{name}.md").exists():
                    report.append(f"SKIP   {domain}/{name}.md (already approved)")
                    continue
                texts, used = [], []
                for org, url in items:
                    try:
                        text = fetch(url, client)
                    except Exception as exc:
                        report.append(f"FAIL   {domain}/{name}: {url} ({exc.__class__.__name__}: {exc})")
                        continue
                    if len(text) < 200:
                        report.append(f"EMPTY  {domain}/{name}: {url} (page has little text; open it by hand)")
                        continue
                    texts.append(f"(From {url})\n\n{text}")
                    used.append(f"{org} ({url})")
                if not texts:
                    continue
                out = docs / f"_fetched-{name}.md"
                out.write_text("Source: " + "; ".join(used) + "\n\n" + "\n\n".join(texts) + "\n", encoding="utf-8")
                words = sum(len(t.split()) for t in texts)
                report.append(f"DRAFT  {out.relative_to(root)} ({words} words)")
    print("\n".join(report) or "No sources.txt files found.")
    print("\nNext: review each _fetched-*.md against the official page, trim it, and rename it to approve.")


if __name__ == "__main__":
    main()
