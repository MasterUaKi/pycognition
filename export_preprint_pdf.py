# File: export_preprint_pdf.py
# Version: 1.0.0 | Release Date: 2026-11-17
# EN: Converts IMRaD Markdown manuscripts with LaTeX formulas into publication-grade A4 Zenodo PDF preprints.
# DE: Konvertiert IMRaD-Markdown-Manuskripte mit LaTeX-Formeln in druckfertige A4-Zenodo-PDF-Preprints.

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


ACADEMIC_PREPRINT_CSS = """
@page {
    size: A4 portrait;
    margin: 22mm 20mm 24mm 20mm;
}

* {
    box-sizing: border-box;
}

body {
    font-family: "Georgia", "Times New Roman", "Liberation Serif", serif;
    font-size: 10.5pt;
    line-height: 1.52;
    color: #1a1d20;
    margin: 0;
    padding: 0;
    background: #ffffff;
}

header.preprint-banner {
    border-top: 2.5pt solid #1b365d;
    border-bottom: 1pt solid #cfd8e3;
    padding: 8pt 0 10pt 0;
    margin-bottom: 14pt;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 8.5pt;
    color: #4a5568;
    display: flex;
    justify-content: space-between;
}

h1 {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 17.5pt;
    font-weight: 700;
    line-height: 1.25;
    color: #0f2537;
    margin: 0 0 10pt 0;
    page-break-after: avoid;
}

h2 {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12.5pt;
    font-weight: 700;
    color: #1b365d;
    border-bottom: 0.75pt solid #d8e1eb;
    padding-bottom: 3pt;
    margin: 18pt 0 8pt 0;
    page-break-after: avoid;
}

h3 {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10.8pt;
    font-weight: 700;
    color: #243b53;
    margin: 13pt 0 5pt 0;
    page-break-after: avoid;
}

h4 {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    font-weight: 700;
    color: #334e68;
    margin: 10pt 0 4pt 0;
    page-break-after: avoid;
}

p {
    margin: 0 0 8pt 0;
    text-align: justify;
    hyphens: auto;
}

ul, ol {
    margin: 4pt 0 10pt 0;
    padding-left: 18pt;
}

li {
    margin-bottom: 4pt;
    text-align: justify;
}

hr {
    border: none;
    border-top: 0.75pt solid #d8e1eb;
    margin: 12pt 0;
}

a {
    color: #1b4f9c;
    text-decoration: none;
}

code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9pt;
    background-color: #f3f6fa;
    padding: 1pt 3.5pt;
    border-radius: 2.5pt;
    color: #1f2933;
}

pre.ascii-diagram {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.2pt;
    line-height: 1.32;
    background-color: #f8fafc;
    border: 0.75pt solid #cbd5e1;
    border-left: 3pt solid #1b365d;
    border-radius: 3pt;
    padding: 9pt 11pt;
    margin: 12pt 0;
    white-space: pre;
    overflow-x: hidden;
    page-break-inside: avoid;
    break-inside: avoid;
}

pre.ascii-diagram code {
    background: transparent;
    padding: 0;
    font-size: inherit;
}

.math-display {
    margin: 10pt 0;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0 14pt 0;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 8.8pt;
    page-break-inside: avoid;
    break-inside: avoid;
}

thead th {
    background-color: #1b365d;
    color: #ffffff;
    font-weight: 600;
    padding: 6pt 7pt;
    border: 0.5pt solid #1b365d;
}

tbody td {
    padding: 5.5pt 7pt;
    border-bottom: 0.5pt solid #d8e1eb;
    border-left: 0.5pt solid #e6ecf2;
    border-right: 0.5pt solid #e6ecf2;
    vertical-align: top;
}

tbody tr:nth-child(even) {
    background-color: #f8fafc;
}

.references-section p,
.references-section li {
    font-size: 9.2pt;
    line-height: 1.42;
    text-align: left;
    margin-bottom: 5pt;
}
"""


def protect_math_and_code(md_text: str) -> Tuple[str, Dict[str, str]]:
    """
    EN: Replaces fenced code blocks, inline code, and LaTeX math spans with opaque tokens
        so Markdown inline formatting never corrupts underscores or operators.
    DE: Ersetzt Codeblöcke und LaTeX-Formeln durch Platzhalter vor dem Markdown-Parsing.
    """
    cleaned = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL).strip()
    placeholders: Dict[str, str] = {}
    counter = 0

    def _store(html_fragment: str) -> str:
        nonlocal counter
        token = f"@@PYCOG_TOKEN_{counter}@@"
        placeholders[token] = html_fragment
        counter += 1
        return token

    # 1. Fenced code / ASCII architecture diagrams
    def _repl_fence(match: re.Match[str]) -> str:
        body = (
            match.group(2)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return _store(f'<pre class="ascii-diagram"><code>{body}</code></pre>')

    cleaned = re.sub(r"```([a-zA-Z0-9_-]*)\n(.*?)```", _repl_fence, cleaned, flags=re.DOTALL)

    # 2. Inline code spans
    def _repl_code(match: re.Match[str]) -> str:
        body = (
            match.group(1)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return _store(f"<code>{body}</code>")

    cleaned = re.sub(r"`([^`\n]+)`", _repl_code, cleaned)

    # 3. Display math $$...$$
    def _repl_display_math(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        return _store(f'<div class="math-display">$${expr}$$</div>')

    cleaned = re.sub(r"\$\$(.*?)\$\$", _repl_display_math, cleaned, flags=re.DOTALL)

    # 4. Inline math $...$
    def _repl_inline_math(match: re.Match[str]) -> str:
        expr = match.group(1)
        return _store(f'<span class="math-inline">${expr}$</span>')

    cleaned = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", _repl_inline_math, cleaned)

    return cleaned, placeholders


def render_inline_markdown(text: str) -> str:
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"  $", "<br />", text)
    return text


def convert_markdown_to_html(md_text: str) -> str:
    protected_md, placeholders = protect_math_and_code(md_text)
    lines = protected_md.splitlines()
    blocks: List[str] = []
    i = 0
    n = len(lines)
    in_references = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("@@PYCOG_TOKEN_") and stripped.endswith("@@"):
            blocks.append(stripped)
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            blocks.append("<hr />")
            i += 1
            continue

        h_match = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if h_match:
            level = len(h_match.group(1))
            raw_heading = h_match.group(2).strip()
            if level == 2 and raw_heading.lower() == "references":
                if not in_references:
                    blocks.append('<div class="references-section">')
                    in_references = True
            elif level == 2 and in_references:
                blocks.append("</div>")
                in_references = False

            blocks.append(f"<h{level}>{render_inline_markdown(raw_heading)}</h{level}>")
            i += 1
            continue

        # Markdown pipe table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            align_tokens = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            aligns: List[str] = []
            for tok in align_tokens:
                if tok.startswith(":") and tok.endswith(":"):
                    aligns.append("center")
                elif tok.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("left")

            tbl = ["<table>", "<thead><tr>"]
            for idx, cell in enumerate(headers):
                al = aligns[idx] if idx < len(aligns) else "left"
                tbl.append(f'<th style="text-align:{al};">{render_inline_markdown(cell)}</th>')
            tbl.append("</tr></thead><tbody>")

            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                tbl.append("<tr>")
                for idx, cell in enumerate(cells):
                    al = aligns[idx] if idx < len(aligns) else "left"
                    tbl.append(f'<td style="text-align:{al};">{render_inline_markdown(cell)}</td>')
                tbl.append("</tr>")
                i += 1
            tbl.append("</tbody></table>")
            blocks.append("\n".join(tbl))
            continue

        # Unordered list
        if re.match(r"^[\*\-]\s+", stripped):
            items: List[str] = []
            while i < n and re.match(r"^[\*\-]\s+", lines[i].strip()):
                item_body = re.sub(r"^[\*\-]\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline_markdown(item_body)}</li>")
                i += 1
            blocks.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                item_body = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline_markdown(item_body)}</li>")
                i += 1
            blocks.append("<ol>\n" + "\n".join(items) + "\n</ol>")
            continue

        # Standard paragraph
        para: List[str] = []
        while i < n:
            cur_s = lines[i].strip()
            if (
                not cur_s
                or cur_s in ("---", "***", "___")
                or re.match(r"^#{1,4}\s+", cur_s)
                or cur_s.startswith("|")
                or re.match(r"^[\*\-]\s+", cur_s)
                or re.match(r"^\d+\.\s+", cur_s)
                or (cur_s.startswith("@@PYCOG_TOKEN_") and cur_s.endswith("@@"))
            ):
                break
            para.append(render_inline_markdown(lines[i].rstrip()))
            i += 1
        blocks.append("<p>" + "\n".join(para) + "</p>")

    if in_references:
        blocks.append("</div>")

    body_html = "\n\n".join(blocks)
    for token, fragment in placeholders.items():
        body_html = body_html.replace(token, fragment)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>PyCognition v1.3.0 — Preprint</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<style>
{ACADEMIC_PREPRINT_CSS}
</style>
</head>
<body>
<header class="preprint-banner">
  <span><strong>PyCognition Research Series — Part III</strong> | Preprint (CC-BY-4.0)</span>
  <span>Universität Vechta (RFNT) • ORCID: 0009-0003-7848-6418</span>
</header>
<main>
{body_html}
</main>
<script>
document.addEventListener("DOMContentLoaded", function() {{
    if (typeof renderMathInElement === "function") {{
        renderMathInElement(document.body, {{
            delimiters: [
                {{left: "$$", right: "$$", display: true}},
                {{left: "$", right: "$", display: false}}
            ],
            throwOnError: false
        }});
    }}
}});
</script>
</body>
</html>
"""


def find_headless_browser() -> str:
    """
    EN: Locates Microsoft Edge or Google Chrome / Chromium executable for headless PDF printing.
    DE: Sucht Microsoft Edge oder Google Chrome / Chromium für den Headless-PDF-Druck.
    """
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path_str in candidates:
        if os.path.isfile(path_str):
            return path_str

    for cmd in ("msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser"):
        resolved = shutil.which(cmd)
        if resolved:
            return resolved

    raise FileNotFoundError(
        "Could not locate Microsoft Edge or Chrome executable for PDF export."
    )


def build_pdf_preprint(
    input_md: Path,
    output_pdf: Path,
    keep_html: bool = False,
) -> None:
    if not input_md.exists():
        raise FileNotFoundError(f"Input Markdown manuscript not found: {input_md}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temp_html = output_pdf.with_suffix(".preprint.html")

    md_source = input_md.read_text(encoding="utf-8")
    html_document = convert_markdown_to_html(md_source)
    temp_html.write_text(html_document, encoding="utf-8")

    browser_bin = find_headless_browser()
    file_uri = temp_html.resolve().as_uri()

    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={output_pdf.resolve()}",
        file_uri,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not output_pdf.exists():
        raise RuntimeError(
            f"Headless PDF generation failed (exit={result.returncode}): {result.stderr}"
        )

    if not keep_html and temp_html.exists():
        temp_html.unlink()

    size_kb = output_pdf.stat().st_size / 1024.0
    print(f"Successfully generated Zenodo PDF preprint: {output_pdf.resolve()} ({size_kb:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert IMRaD Markdown manuscript to formatted Zenodo PDF preprint."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("docs/paper_part3_imrad.md"),
        help="Path to input Markdown manuscript (default: docs/paper_part3_imrad.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/paper_part3_imrad.pdf"),
        help="Path to output PDF preprint (default: docs/paper_part3_imrad.pdf)",
    )
    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Keep intermediate HTML file alongside the generated PDF.",
    )
    args = parser.parse_args()
    build_pdf_preprint(args.input, args.output, keep_html=args.keep_html)


if __name__ == "__main__":
    main()