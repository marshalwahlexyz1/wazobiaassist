"""Builds the submission PDFs in docs/:

    WazobiaAssist_Technical_Documentation.pdf       the whole README
    WazobiaAssist_Architecture_Setup_Usage.pdf      architecture, setup and usage sections of the README
    WazobiaAssist_N-ATLaS_Integration_Evidence.pdf  docs/N-ATLaS_integration_evidence.md

    python docs/build_pdf.py        (needs: pip install markdown, and Microsoft Edge or Chrome)
"""

import base64
import datetime
import re
import shutil
import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google-chrome", "chromium", "msedge",
]

# README sections that make up the architecture, setup and usage document.
ARCHITECTURE_SETUP_USAGE = [
    "Try it", "What it does", "How it works", "Technology stack", "Domains are plug-in folders",
    "Run it", "Users' commands", "NAFDAC product check", "Routing test", "Privacy and safety",
    "Known limitations", "Project layout",
]

PIPELINE = [
    ("Voice note or text", "Web page · Telegram"),
    ("Speech to text", "NCAIR ASR (ha, ig, yo, en)"),
    ("Translate in", "N-ATLaS → English"),
    ("Route", "Keywords + N-ATLaS"),
    ("Retrieve", "Agency documents · NAFDAC registers"),
    ("Answer", "N-ATLaS, grounded, names source"),
    ("Translate out", "N-ATLaS → user's language, codes checked"),
    ("Reply and log", "Text (+ voice) · 👍/👎 · anonymous log"),
]


def pipeline_html() -> str:
    steps = "".join(
        f'<div class="step"><span class="n">{i}</span><b>{t}</b><small>{d}</small></div>'
        for i, (t, d) in enumerate(PIPELINE, 1)
    )
    return f'<div class="pipeline">{steps}</div><p class="legend">Gold steps are N-ATLaS calls.</p>'


def readme_text() -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    # The cover replaces the README's logo, title and tagline.
    text = re.sub(r"\A(<p[^\n]*logo[^\n]*\n+)?# WazobiaAssist\s*\n+\*\*Government answers in one place, in your language\.\*\*\s*\n", "", text)
    # The cover already names the challenge.
    return re.sub(r"\nNational AI Innovation Challenge \(NAIC\) 2026, Problem Statement 02[^\n]*\n", "\n", text, count=1)


def sections(text: str, titles: list[str]) -> str:
    """The README's "## " sections with these titles, in README order."""
    parts = re.split(r"(?m)^(?=## )", text)
    keep = [s for s in parts if s.startswith("## ") and s[3:].splitlines()[0].strip() in titles]
    missing = set(titles) - {s[3:].splitlines()[0].strip() for s in keep}
    if missing:
        raise SystemExit(f"README has no section named: {', '.join(sorted(missing))}")
    return "".join(keep)


def body_html(text: str) -> str:
    # GitHub renders a list right after a line of text; Python-Markdown needs a blank line first.
    text = re.sub(r"(?m)^([^\n\-|#>`\s][^\n]*)\n(- )", r"\1\n\n\2", text)
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    # Replace the ASCII pipeline sketch, or the marker in the evidence document, with a drawn one.
    html = re.sub(r"<pre><code>voice note ─►.*?</code></pre>", pipeline_html(), html, flags=re.S)
    return html.replace("<!-- pipeline -->", pipeline_html())


def page(title: str, sub: str, body: str) -> str:
    logo = base64.b64encode((DOCS / "logo.svg").read_bytes()).decode()
    today = datetime.date.today().strftime("%d %B %Y").lstrip("0")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>WazobiaAssist {title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap">
<style>
  @page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
  :root {{ --green: #008751; --gold: #f2b705; --ink: #14201a; --muted: #5a6b62; --line: #d9e3dc; --soft: #eef6f1; }}
  html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  body {{ font: 10.5pt/1.5 "Source Sans 3", "Segoe UI", Arial, sans-serif; color: var(--ink); margin: 0; }}
  .cover {{ border-bottom: 3px solid var(--green); padding-bottom: 14px; margin-bottom: 18px; }}
  .cover img {{ height: 64px; display: block; }}
  .cover h1 {{ font: 700 22pt/1.15 Poppins, "Segoe UI", sans-serif; margin: 16px 0 4px; }}
  .cover .sub {{ color: var(--muted); font-size: 11.5pt; margin: 0 0 12px; }}
  .meta {{ display: grid; grid-template-columns: max-content 1fr; gap: 3px 14px; font-size: 10pt; }}
  .meta b {{ color: var(--muted); font-weight: 600; }}
  .meta a {{ color: var(--green); text-decoration: none; }}
  h2 {{ font: 600 14pt/1.25 Poppins, "Segoe UI", sans-serif; color: var(--green); margin: 22px 0 6px; padding-top: 6px; border-top: 1px solid var(--line); break-after: avoid; }}
  h3 {{ font: 700 11.5pt/1.3 "Source Sans 3", sans-serif; margin: 14px 0 4px; break-after: avoid; }}
  p, li {{ orphans: 2; widows: 2; }}
  a {{ color: var(--green); }}
  table {{ border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9.5pt; break-inside: auto; }}
  th, td {{ border: 1px solid var(--line); padding: 5px 7px; text-align: left; vertical-align: top; }}
  th {{ background: var(--soft); }}
  tr {{ break-inside: avoid; }}
  code {{ font: 8.8pt "JetBrains Mono", Consolas, monospace; background: var(--soft); padding: 0 3px; border-radius: 3px; }}
  pre {{ background: #f5f7f6; border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; white-space: pre-wrap; word-break: break-word; break-inside: avoid; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ margin: 8px 0; padding: 6px 12px; border-left: 3px solid var(--gold); background: #fffaf0; }}
  blockquote p {{ margin: 2px 0; }}
  .pipeline {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0 14px; break-inside: avoid; }}
  .step {{ border: 1px solid var(--line); border-top: 3px solid var(--green); border-radius: 6px; padding: 6px 8px; display: grid; gap: 2px; font-size: 9.5pt; }}
  .step:nth-child(3), .step:nth-child(4), .step:nth-child(6), .step:nth-child(7) {{ border-top-color: var(--gold); }}
  .step .n {{ font: 600 8pt "JetBrains Mono", monospace; color: var(--muted); }}
  .step small {{ color: var(--muted); font-size: 8.5pt; line-height: 1.3; }}
  .legend {{ font-size: 8.5pt; color: var(--muted); margin-top: -8px; }}
</style></head><body>
<header class="cover">
  <img src="data:image/svg+xml;base64,{logo}" alt="WazobiaAssist">
  <h1>{title}</h1>
  <p class="sub">{sub}</p>
  <div class="meta">
    <b>Challenge</b><span>National AI Innovation Challenge (NAIC) 2026 · Problem Statement 02: Voice-First Access · Track B (Innovation &amp; Enterprise)</span>
    <b>Try it</b><span><a href="https://wazobiaassist.github.io">wazobiaassist.github.io</a> · Telegram <a href="https://t.me/WazobiaAssist_bot">@WazobiaAssist_bot</a></span>
    <b>Code</b><span><a href="https://github.com/marshalwahlexyz1/wazobiaassist">github.com/marshalwahlexyz1/wazobiaassist</a></span>
    <b>Date</b><span>{today}</span>
  </div>
</header>
{body}
</body></html>"""


def print_pdf(browser: str, html: str, out: Path) -> None:
    html_path = DOCS / "_print.html"
    html_path.write_text(html, encoding="utf-8")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={out}", html_path.as_uri()],
                   check=True, capture_output=True)
    html_path.unlink()
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


def main() -> None:
    browser = next((b for b in BROWSERS if Path(b).exists() or shutil.which(b)), None)
    if not browser:
        raise SystemExit("Install Microsoft Edge or Google Chrome to print the PDF.")
    tagline = "Government answers in one place, in your language. A voice-first assistant built on N-ATLaS."
    readme = readme_text()
    evidence = (DOCS / "N-ATLaS_integration_evidence.md").read_text(encoding="utf-8")
    evidence = re.sub(r"\A# [^\n]*\n", "", evidence)  # the cover carries the title
    docs = [
        ("Technical Documentation", tagline, readme, "WazobiaAssist_Technical_Documentation.pdf"),
        ("Architecture, Setup and Usage", tagline, sections(readme, ARCHITECTURE_SETUP_USAGE),
         "WazobiaAssist_Architecture_Setup_Usage.pdf"),
        ("N-ATLaS Integration Evidence", "How WazobiaAssist uses N-ATLaS, with proof from the live system and real users.",
         evidence, "WazobiaAssist_N-ATLaS_Integration_Evidence.pdf"),
    ]
    for title, sub, text, name in docs:
        print_pdf(browser, page(title, sub, body_html(text)), DOCS / name)


if __name__ == "__main__":
    main()
