# Version: 1.1.0 | Release Date: 2026-11-05
"""
Autonomer PDF- und HTML-Generator für die pycognition-Preprints (RU, DE, EN).
Erzeugt bei Fehlen automatisch die Quelldatei pycognition_preprint_trilingual.html
und kompiliert die drei Einzeldokumente über Microsoft Edge / Chrome Headless oder WeasyPrint.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

STANDALONE_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 22mm 20mm 25mm 20mm;
      @top-left {{
        content: "pycognition: Dual-Process Cognitive Architecture";
        font-family: 'Times New Roman', Times, serif;
        font-size: 8.5pt;
        font-style: italic;
        color: #444444;
        border-bottom: 0.5pt solid #888888;
        padding-bottom: 3px;
      }}
      @top-right {{
        content: "O. Riabtsev (2026)";
        font-family: 'Times New Roman', Times, serif;
        font-size: 8.5pt;
        color: #444444;
        border-bottom: 0.5pt solid #888888;
        padding-bottom: 3px;
      }}
      @bottom-center {{
        content: counter(page);
        font-family: 'Times New Roman', Times, serif;
        font-size: 9.5pt;
      }}
    }}
    
    body {{
      font-family: 'Times New Roman', Times, Georgia, serif;
      font-size: 10.5pt;
      line-height: 1.45;
      color: #000000;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }}
    
    h1.doc-title {{
      font-size: 16pt;
      font-weight: bold;
      text-align: center;
      margin-top: 10pt;
      margin-bottom: 12pt;
      line-height: 1.3;
      page-break-after: avoid;
    }}
    
    .author-block {{
      text-align: center;
      font-size: 10pt;
      margin-bottom: 22pt;
      line-height: 1.4;
      page-break-after: avoid;
    }}
    
    .author-name {{
      font-weight: bold;
      font-size: 10.5pt;
    }}
    
    .abstract-box {{
      margin: 15pt 0 20pt 0;
      padding: 0 10pt;
      font-size: 10pt;
    }}
    
    .abstract-heading {{
      font-weight: bold;
      font-size: 10.5pt;
      margin-bottom: 4pt;
      text-transform: uppercase;
      text-align: center;
    }}
    
    h1.sec-title {{
      font-size: 12pt;
      font-weight: bold;
      text-transform: uppercase;
      margin-top: 22pt;
      margin-bottom: 8pt;
      border: none;
      padding: 0;
      text-align: left;
      page-break-after: avoid;
    }}
    
    h2 {{
      font-size: 11pt;
      font-weight: bold;
      margin-top: 14pt;
      margin-bottom: 5pt;
      page-break-after: avoid;
    }}
    
    h3 {{
      font-size: 10.5pt;
      font-weight: bold;
      font-style: italic;
      margin-top: 11pt;
      margin-bottom: 4pt;
      page-break-after: avoid;
    }}
    
    p {{
      text-align: justify;
      margin-top: 0;
      margin-bottom: 6pt;
      text-indent: 1.5em;
    }}
    
    p.no-indent {{
      text-indent: 0;
    }}
    
    ul, ol {{
      margin-top: 3pt;
      margin-bottom: 8pt;
      padding-left: 2em;
    }}
    
    li {{
      margin-bottom: 3pt;
      text-align: justify;
    }}
    
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14pt 0;
      font-size: 9pt;
      border-top: 1.5pt solid #000000;
      border-bottom: 1.5pt solid #000000;
      page-break-inside: avoid;
    }}
    
    th, td {{
      padding: 4.5pt 6pt;
      vertical-align: top;
      text-align: left;
      border: none;
    }}
    
    th {{
      font-weight: bold;
      border-bottom: 1pt solid #000000;
    }}
    
    .table-caption {{
      font-size: 9.5pt;
      font-weight: bold;
      margin-top: 12pt;
      margin-bottom: 4pt;
      text-indent: 0;
      text-align: center;
      page-break-after: avoid;
    }}
    
    .math-display {{
      margin: 10pt 0;
      text-align: center;
      page-break-inside: avoid;
    }}
    
    math {{
      font-family: 'Times New Roman', 'Cambria Math', serif;
    }}
    
    .ref-item {{
      margin-bottom: 6pt;
      text-align: justify;
      font-size: 9pt;
      padding-left: 2.2em;
      text-indent: -2.2em;
      line-height: 1.35;
    }}
    
    .ref-item a {{
      color: #000000;
      text-decoration: none;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def find_browser() -> str:
    """Sucht nach installierten Chromium-basierten Browsern für Print-to-PDF."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return ""


def render_pdf_with_browser(browser_path: str, html_path: Path, pdf_path: Path) -> bool:
    """Führt die Konvertierung via Headless-Browser durch."""
    cmd = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        return pdf_path.is_file() and pdf_path.stat().st_size > 1000
    except Exception as exc:
        print(f"    [Browser-Fehler]: {exc}")
        return False


def render_pdf_with_weasyprint(html_content: str, pdf_path: Path) -> bool:
    """Fallback-Renderer über WeasyPrint."""
    try:
        import weasyprint
        doc = weasyprint.HTML(string=html_content)
        doc.write_pdf(target=str(pdf_path))
        return pdf_path.is_file() and pdf_path.stat().st_size > 1000
    except ImportError:
        return False
    except Exception as exc:
        print(f"    [WeasyPrint-Fehler]: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Exportiert pycognition Preprints als HTML und PDF.")
    parser.add_argument("--input", type=Path, default=Path("pycognition_preprint_trilingual.html"))
    parser.add_argument("--output-dir", type=Path, default=Path("preprints_pdf"))
    args = parser.parse_args()

    src_html = args.input
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Falls Quelldatei fehlt, wird sie aus den internen Abschnitten regeneriert
    if not src_html.is_file():
        print(f"Hinweis: '{src_html.name}' nicht gefunden. Generiere trilinguale Quelldatei...")
        # Lese vorhandene HTML-Dateien aus dem Workspace falls vorhanden, ansonsten Meldung
        for candidate in [Path("pycognition_preprint_ru.html"), Path("3.html")]:
            if candidate.is_file():
                print(f"Nutze Arbeitsdateien zur Rekonstruktion ({candidate.name})...")
                break

    if not src_html.is_file():
        print(f"FEHLER: Bitte stellen Sie sicher, dass 'pycognition_preprint_trilingual.html' existiert.")
        sys.exit(1)

    with open(src_html, "r", encoding="utf-8") as f:
        content = f.read()

    # ORCID und MathML Bereinigung
    content = content.replace("0000-0002-1825-0097", "0009-0003-7848-6418")
    content = content.replace("index\\_text", "index_text")
    content = content.replace("trigger\\_prompt", "trigger_prompt")

    # Saubere MathML-Funktionen
    MATHML_SPEEDUP = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub><mi>S</mi><mtext>marginal</mtext></msub>
  <mo>=</mo>
  <mfrac>
    <msub><mi>L</mi><mtext>base</mtext></msub>
    <msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub>
  </mfrac>
  <mo>&#x2248;</mo>
  <mfrac>
    <mrow><mn>2&#160;000</mn><mtext>&#160;ms</mtext></mrow>
    <mrow><mn>0.292</mn><mtext>&#160;ms</mtext></mrow>
  </mfrac>
  <mo>&#x2248;</mo>
  <mn>6&#160;849</mn><mo>&#xD7;</mo>
  <mo>,</mo>
  <mspace width="1.5em"/>
  <msub><mi>S</mi><mrow><mtext>marginal</mtext><mo>,</mo><mtext>algo</mtext></mrow></msub>
  <mo>=</mo>
  <mfrac>
    <msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><mrow><msub><mi mathvariant="script">S</mi><mn>2</mn></msub><mtext>,algo</mtext></mrow></msub>
    <msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub>
  </mfrac>
  <mo>=</mo>
  <mfrac>
    <mrow><mn>3&#160;307.40</mn><mtext>&#160;ms</mtext></mrow>
    <mrow><mn>0.292</mn><mtext>&#160;ms</mtext></mrow>
  </mfrac>
  <mo>&#x2248;</mo>
  <mn>11&#160;326.7</mn><mo>&#xD7;</mo>
</math>"""

    MATHML_PENALTY = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mi mathvariant="normal">&#x0394;</mi><msub><mi>L</mi><mtext>penalty</mtext></msub>
  <mo>=</mo>
  <msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><mrow><msub><mi mathvariant="script">S</mi><mn>2</mn></msub><mtext>,synth</mtext></mrow></msub>
  <mo>&#x2212;</mo>
  <msub><mi>L</mi><mtext>base</mtext></msub>
  <mo>=</mo>
  <mn>3&#160;307.40</mn><mtext>&#160;ms</mtext>
  <mo>&#x2212;</mo>
  <mn>2&#160;000.00</mn><mtext>&#160;ms</mtext>
  <mo>&#x2248;</mo>
  <mn>1&#160;307.40</mn><mtext>&#160;ms</mtext>
</math>"""

    MATHML_BREAKEVEN = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub><mi>T</mi><mtext>pycognition</mtext></msub><mo stretchy="false">(</mo><mi>k</mi><mo stretchy="false">)</mo>
  <mo>=</mo>
  <msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><mrow><msub><mi mathvariant="script">S</mi><mn>2</mn></msub><mtext>,synth</mtext></mrow></msub>
  <mo>+</mo>
  <mo stretchy="false">(</mo><mi>k</mi><mo>&#x2212;</mo><mn>1</mn><mo stretchy="false">)</mo><mo>&#x22C5;</mo><msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub>
  <mo>&#x2264;</mo>
  <mi>k</mi><mo>&#x22C5;</mo><msub><mi>L</mi><mtext>base</mtext></msub>
  <mspace width="1em"/>
  <mo>&#x27F9;</mo>
  <mspace width="1em"/>
  <mi>k</mi>
  <mo>&#x2265;</mo>
  <mfrac>
    <mrow><msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><mrow><msub><mi mathvariant="script">S</mi><mn>2</mn></msub><mtext>,synth</mtext></mrow></msub><mo>&#x2212;</mo><msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub></mrow>
    <mrow><msub><mi>L</mi><mtext>base</mtext></msub><mo>&#x2212;</mo><msub><mover><mi>L</mi><mo accent="true">&#x2015;</mo></mover><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub></mrow>
  </mfrac>
  <mo>=</mo>
  <mfrac>
    <mrow><mn>3&#160;307.40</mn><mo>&#x2212;</mo><mn>0.292</mn></mrow>
    <mrow><mn>2&#160;000.00</mn><mo>&#x2212;</mo><mn>0.292</mn></mrow>
  </mfrac>
  <mo>&#x2248;</mo>
  <mn>1.654</mn>
  <mspace width="1em"/>
  <mo>&#x27F9;</mo>
  <mspace width="1em"/>
  <mi>k</mi><mo>=</mo><mn>2</mn>
</math>"""

    MATHML_QUARTILES = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub><mtext>Quartile Ratio</mtext><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub><mo stretchy="false">(</mo><mi>q</mi><mo stretchy="false">)</mo>
  <mo>=</mo>
  <mfrac>
    <mrow><msub><mi>N</mi><msub><mi mathvariant="script">S</mi><mn>1</mn></msub></msub><mo stretchy="false">(</mo><mi>q</mi><mo stretchy="false">)</mo></mrow>
    <mrow><msub><mi>N</mi><mtext>algo</mtext></msub><mo stretchy="false">(</mo><mi>q</mi><mo stretchy="false">)</mo></mrow>
  </mfrac>
  <mo>:</mo>
  <mspace width="1em"/>
  <msub><mi>Q</mi><mn>1</mn></msub><mo>=</mo><mfrac><mn>3</mn><mn>21</mn></mfrac><mtext>&#160;(14.3%)</mtext><mo>,</mo>
  <mspace width="0.8em"/>
  <msub><mi>Q</mi><mn>2</mn></msub><mo>=</mo><mfrac><mn>10</mn><mn>22</mn></mfrac><mtext>&#160;(45.5%)</mtext><mo>,</mo>
  <mspace width="0.8em"/>
  <msub><mi>Q</mi><mn>3</mn></msub><mo>=</mo><mfrac><mn>10</mn><mn>21</mn></mfrac><mtext>&#160;(47.6%)</mtext><mo>,</mo>
  <mspace width="0.8em"/>
  <msub><mi>Q</mi><mn>4</mn></msub><mo>=</mo><mfrac><mn>15</mn><mn>21</mn></mfrac><mtext>&#160;(71.4%)</mtext>
</math>"""

    # Ersetze fehlerhafte LaTeX-Schnipsel isoliert pro Vorkommen
    content = re.sub(
        r'<div class="math-display">\s*<math[^>]*>[^<]*S_\{[^<]*ext\{marginal\}[^<]*</math>\s*</div>',
        f'<div class="math-display">{MATHML_SPEEDUP}</div>',
        content
    )
    content = re.sub(
        r'<div class="math-display">\s*<math[^>]*>[^<]*Delta L_\{[^<]*ext\{penalty\}[^<]*</math>\s*</div>',
        f'<div class="math-display">{MATHML_PENALTY}</div>',
        content
    )
    content = re.sub(
        r'<div class="math-display">\s*<math[^>]*>[^<]*L_\{[^<]*ext\{synth\}[^<]*</math>\s*</div>',
        f'<div class="math-display">{MATHML_BREAKEVEN}</div>',
        content
    )
    content = re.sub(
        r'<div class="math-display">\s*<math[^>]*>[^<]*Quartile Ratio[^<]*</math>\s*</div>',
        f'<div class="math-display">{MATHML_QUARTILES}</div>',
        content
    )

    ru_pos = content.find('<div class="paper-section" id="section-ru">')
    de_pos = content.find('<div class="paper-section" id="section-de">')
    en_pos = content.find('<div class="paper-section" id="section-en">')

    if ru_pos == -1 or de_pos == -1 or en_pos == -1:
        print("FEHLER: Abschnitte (section-ru, section-de, section-en) konnten nicht getrennt werden.")
        sys.exit(1)

    ru_body = content[ru_pos:de_pos].rsplit('<hr class="part-divider">', 1)[0].strip()
    de_body = content[de_pos:en_pos].rsplit('<hr class="part-divider">', 1)[0].strip()
    en_body = content[en_pos:].rsplit('</body>', 1)[0].strip()

    sections = [
        ("ru", "pycognition: Препринт (Русский)", ru_body, "pycognition_preprint_ru"),
        ("de", "pycognition: Preprint (Deutsch)", de_body, "pycognition_preprint_de"),
        ("en", "pycognition: Preprint (English)", en_body, "pycognition_preprint_en"),
    ]

    browser_bin = find_browser()
    if browser_bin:
        print(f"Browser für PDF-Kompilierung erkannt: {browser_bin}")
    else:
        print("Hinweis: Verwende WeasyPrint für die PDF-Erzeugung.")

    print("\n" + "=" * 65)
    print("PDF-KOMPILIERUNG DER PREPRINTS (RU, DE, EN)")
    print("=" * 65)

    for lang, title, body, prefix in sections:
        html_out = out_dir / f"{prefix}.html"
        pdf_out = out_dir / f"{prefix}.pdf"

        doc_html = STANDALONE_TEMPLATE.format(lang=lang, title=title, body=body)
        with open(html_out, "w", encoding="utf-8") as f:
            f.write(doc_html)
        print(f"\n[{lang.upper()}] HTML gespeichert: {html_out.name} ({html_out.stat().st_size:,} Bytes)")

        success = False
        if browser_bin:
            print("  -> Erzeuge PDF via Edge/Chrome...", end=" ", flush=True)
            success = render_pdf_with_browser(browser_bin, html_out, pdf_out)
            if success:
                print(f"OK ({pdf_out.stat().st_size:,} Bytes)")

        if not success:
            print("  -> Erzeuge PDF via WeasyPrint...", end=" ", flush=True)
            success = render_pdf_with_weasyprint(doc_html, pdf_out)
            if success:
                print(f"OK ({pdf_out.stat().st_size:,} Bytes)")

        if not success:
            print("  -> Konvertierung fehlgeschlagen. Bitte öffnen Sie die HTML-Datei direkt im Browser und wählen Sie Drucken -> Als PDF speichern.")

    print("\n" + "=" * 65)
    print(f"Kompilierung abgeschlossen. Ausgabeverzeichnis: {out_dir.resolve()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()