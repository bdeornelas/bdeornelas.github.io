#!/usr/bin/env python3
"""
Extract Table of Contents from ESC Guidelines PDFs
Generates a unified Markdown file with all TOCs
"""

import os
import fitz  # PyMuPDF
from datetime import datetime
from pathlib import Path


def extract_toc_from_pdf(pdf_path):
    """
    Extract TOC from a PDF file using PyMuPDF
    Returns list of (level, title, page) tuples
    """
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()  # Returns [(level, title, page), ...]
        doc.close()

        if not toc:
            print(f"  ⚠️  No embedded TOC found in {os.path.basename(pdf_path)}")
            return None

        return toc
    except Exception as e:
        print(f"  ❌ Error extracting TOC from {os.path.basename(pdf_path)}: {e}")
        return None


def format_toc_as_markdown(toc, base_indent=0):
    """
    Convert TOC list to Markdown format with proper indentation
    """
    if not toc:
        return "  *Nessun indice disponibile*\n"

    md_lines = []
    for level, title, page in toc:
        # Clean title
        title = title.strip()
        if not title:
            continue

        # Calculate indentation (level 1 = no indent, level 2 = 2 spaces, etc.)
        indent = "  " * (level - 1 + base_indent)

        # Format as Markdown list item with page number
        md_lines.append(f"{indent}- {title} *(p. {page})*")

    return "\n".join(md_lines) + "\n"


def parse_guideline_info(filename):
    """
    Extract year and topic from filename
    Example: "2024_Atrial_Fibrillation.pdf" -> (2024, "Atrial Fibrillation")
    """
    name = filename.replace('.pdf', '')
    parts = name.split('_', 1)

    if len(parts) == 2:
        year = parts[0]
        topic = parts[1].replace('_', ' ')
        return year, topic

    return "Unknown", name


def generate_unified_toc_markdown(guidelines_dir, output_file):
    """
    Main function to generate unified TOC markdown file
    """
    guidelines_dir = Path(guidelines_dir)
    output_file = Path(output_file)

    # Get all PDF files
    pdf_files = sorted(guidelines_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {guidelines_dir}")
        return

    print(f"📚 Found {len(pdf_files)} ESC Guidelines PDFs")
    print(f"📝 Extracting TOCs...\n")

    # Group by year
    guidelines_by_year = {}

    for pdf_path in pdf_files:
        year, topic = parse_guideline_info(pdf_path.name)

        print(f"Processing: {pdf_path.name}")
        toc = extract_toc_from_pdf(pdf_path)

        if year not in guidelines_by_year:
            guidelines_by_year[year] = []

        guidelines_by_year[year].append({
            'filename': pdf_path.name,
            'topic': topic,
            'toc': toc
        })

    # Generate Markdown content
    print(f"\n📄 Generating Markdown file...")

    md_content = []

    # Header
    md_content.append("# Indice Linee Guida ESC (2020-2025)")
    md_content.append("")
    md_content.append(f"*Generato automaticamente il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}*")
    md_content.append("")
    md_content.append(f"Questo documento contiene i Table of Contents (TOC) estratti da **{len(pdf_files)} linee guida ESC**.")
    md_content.append("")
    md_content.append("---")
    md_content.append("")

    # Generate index
    md_content.append("## Indice Rapido")
    md_content.append("")

    for year in sorted(guidelines_by_year.keys(), reverse=True):
        md_content.append(f"### {year}")
        for guideline in sorted(guidelines_by_year[year], key=lambda x: x['topic']):
            # Create anchor link
            anchor = guideline['topic'].lower().replace(' ', '-').replace('/', '-')
            md_content.append(f"- [{guideline['topic']}](#{year.lower()}-{anchor})")
        md_content.append("")

    md_content.append("---")
    md_content.append("")

    # Generate full TOCs
    for year in sorted(guidelines_by_year.keys(), reverse=True):
        md_content.append(f"## {year}")
        md_content.append("")

        for guideline in sorted(guidelines_by_year[year], key=lambda x: x['topic']):
            # Create anchor
            anchor = guideline['topic'].lower().replace(' ', '-').replace('/', '-')

            md_content.append(f"### <a name=\"{year.lower()}-{anchor}\"></a>{guideline['topic']}")
            md_content.append("")
            md_content.append(f"**File:** `{guideline['filename']}`")
            md_content.append("")

            if guideline['toc']:
                md_content.append(format_toc_as_markdown(guideline['toc']))
            else:
                md_content.append("*Nessun indice disponibile*")

            md_content.append("")
            md_content.append("---")
            md_content.append("")

    # Footer
    md_content.append("## Note")
    md_content.append("")
    md_content.append("- I numeri di pagina si riferiscono alla numerazione interna del PDF")
    md_content.append("- Le linee guida ESC sono proprietà della European Society of Cardiology")
    md_content.append("- Questo documento è generato automaticamente a scopo di consultazione interna")
    md_content.append("")

    # Write to file
    output_file.write_text('\n'.join(md_content), encoding='utf-8')

    print(f"\n✅ File generato: {output_file}")
    print(f"📊 Statistiche:")
    print(f"   - Linee guida totali: {len(pdf_files)}")
    print(f"   - Anni coperti: {min(guidelines_by_year.keys())} - {max(guidelines_by_year.keys())}")
    print(f"   - Dimensione file: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    # Configuration
    GUIDELINES_DIR = "../references/esc-guidelines"
    OUTPUT_FILE = "../references/esc-guidelines/ESC_GUIDELINES_TOC.md"

    # Get absolute paths
    script_dir = Path(__file__).parent
    guidelines_dir = (script_dir / GUIDELINES_DIR).resolve()
    output_file = (script_dir / OUTPUT_FILE).resolve()

    print("=" * 60)
    print("ESC Guidelines TOC Extractor")
    print("=" * 60)
    print()

    generate_unified_toc_markdown(guidelines_dir, output_file)

    print()
    print("=" * 60)
    print("Completato!")
    print("=" * 60)
