#!/usr/bin/env python3
"""
Script per convertire PDF ESC in Markdown e generare TOC.
Uso: python pdf_to_md.py input.pdf output.md
"""

import subprocess
import sys
import re
from pathlib import Path


def pdf_to_text(pdf_path: str) -> str:
    """Converte PDF in testo usando pdftotext."""
    result = subprocess.run(
        ['pdftotext', '-layout', pdf_path, '-'],
        capture_output=True,
        text=True
    )
    return result.stdout


def clean_text(text: str) -> str:
    """Pulisce il testo estratto dal PDF."""
    # Rimuovi header/footer ripetuti
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Salta righe con solo numeri di pagina
        if re.match(r'^\s*\d+\s*$', line):
            continue
        # Salta righe vuote multiple
        if not line.strip() and cleaned_lines and not cleaned_lines[-1].strip():
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def detect_sections(text: str) -> list:
    """Rileva le sezioni del documento per costruire il TOC."""
    sections = []
    lines = text.split('\n')
    line_num = 0

    for line in lines:
        line_num += 1
        # Pattern per sezioni numerate (es. "1. Introduction", "2.1. Methods")
        match = re.match(r'^(\d+(?:\.\d+)*\.?)\s+([A-Z][^.!?]*)', line.strip())
        if match:
            num = match.group(1).rstrip('.')
            title = match.group(2).strip()
            depth = num.count('.') + 1
            sections.append({
                'number': num,
                'title': title,
                'depth': depth,
                'line': line_num
            })

    return sections


def generate_toc(sections: list, filename: str) -> str:
    """Genera il TOC in formato compatibile con ESC_GUIDELINES_TOC.md."""
    toc_lines = []

    for section in sections:
        indent = '  ' * (section['depth'] - 1)
        toc_lines.append(
            f"{indent}- {section['number']}. {section['title']} *(L{section['line']})*"
        )

    return '\n'.join(toc_lines)


def text_to_markdown(text: str) -> str:
    """Converte il testo in formato Markdown."""
    lines = text.split('\n')
    md_lines = []

    for line in lines:
        stripped = line.strip()

        # Converti sezioni in headers markdown
        match = re.match(r'^(\d+(?:\.\d+)*\.?)\s+([A-Z].*)$', stripped)
        if match:
            num = match.group(1)
            title = match.group(2)
            depth = num.count('.') + 1
            header_level = min(depth + 1, 6)  # Max h6
            md_lines.append(f"\n{'#' * header_level} {num} {title}\n")
        else:
            md_lines.append(line)

    return '\n'.join(md_lines)


def convert_pdf(pdf_path: str, output_path: str) -> dict:
    """Converte un PDF in Markdown e restituisce info per TOC."""
    print(f"Converting {pdf_path}...")

    # Estrai testo
    raw_text = pdf_to_text(pdf_path)
    cleaned_text = clean_text(raw_text)

    # Rileva sezioni
    sections = detect_sections(cleaned_text)

    # Converti in markdown
    markdown = text_to_markdown(cleaned_text)

    # Scrivi output
    Path(output_path).write_text(markdown, encoding='utf-8')
    print(f"Written to {output_path}")

    # Genera TOC
    toc = generate_toc(sections, Path(output_path).stem)

    return {
        'sections': len(sections),
        'toc': toc,
        'lines': len(markdown.split('\n'))
    }


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_md.py input.pdf output.md")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    result = convert_pdf(pdf_path, output_path)

    print(f"\nConversion complete:")
    print(f"  Sections found: {result['sections']}")
    print(f"  Total lines: {result['lines']}")
    print(f"\nTOC entry for ESC_GUIDELINES_TOC.md:")
    print("-" * 50)
    print(result['toc'][:2000])  # Prima parte del TOC
