#!/usr/bin/env python3
"""
Convert ESC Guidelines PDFs to Markdown
Extracts full text content with section headers and page references
"""

import os
import re
import fitz  # PyMuPDF
from datetime import datetime
from pathlib import Path


def clean_text(text):
    """
    Clean extracted text: fix common PDF extraction issues
    """
    # Fix hyphenation at line breaks
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # Remove multiple newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix broken words (lowercase followed by newline then lowercase)
    text = re.sub(r'([a-z])\n([a-z])', r'\1 \2', text)

    # Remove page headers/footers (common patterns)
    text = re.sub(r'\n\d+\s+ESC Guidelines.*?\n', '\n', text)
    text = re.sub(r'\nEuropean Heart Journal.*?\n', '\n', text)
    text = re.sub(r'\nDownloaded from.*?\n', '\n', text)

    return text.strip()


def detect_section_header(text):
    """
    Detect if text line is a section header (e.g., "5.4.6 Cardiovascular computed tomography")
    Returns (level, title) if header, None otherwise
    """
    # Pattern for numbered sections: 1., 1.1, 1.1.1, etc.
    patterns = [
        (r'^(\d+)\.\s+([A-Z][^.]+)$', 1),           # "5. Section Title"
        (r'^(\d+\.\d+)\s+([A-Z][^.]+)$', 2),        # "5.4 Section Title"
        (r'^(\d+\.\d+\.\d+)\s+([A-Z][^.]+)$', 3),   # "5.4.6 Section Title"
        (r'^(\d+\.\d+\.\d+\.\d+)\s+([A-Z][^.]+)$', 4),  # "5.4.6.1 Section Title"
    ]

    text = text.strip()
    for pattern, level in patterns:
        match = re.match(pattern, text)
        if match:
            return (level, f"{match.group(1)} {match.group(2)}")

    return None


def extract_recommendation_boxes(text):
    """
    Identify and format recommendation boxes (Class I/IIa/IIb/III)
    """
    # Pattern for recommendations
    rec_patterns = [
        r'(Class I[Ia-b]*.*?Level [A-C].*?)(?=\n\n|Class I|\Z)',
        r'(Recommendation[s]?.*?Class.*?Level.*?)(?=\n\n|\Z)',
    ]

    for pattern in rec_patterns:
        text = re.sub(pattern, r'\n> **RECOMMENDATION**: \1\n', text, flags=re.DOTALL | re.IGNORECASE)

    return text


def convert_pdf_to_markdown(pdf_path, output_dir):
    """
    Convert a single PDF to Markdown
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # Create output filename
    md_filename = pdf_path.stem + ".md"
    output_path = output_dir / md_filename

    try:
        doc = fitz.open(pdf_path)

        # Get metadata
        year, topic = parse_guideline_info(pdf_path.name)
        toc = doc.get_toc()

        md_content = []

        # Header
        md_content.append(f"# ESC Guidelines: {topic} ({year})")
        md_content.append("")
        md_content.append(f"**Source**: `{pdf_path.name}`")
        md_content.append(f"**Converted**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        md_content.append(f"**Pages**: {len(doc)}")
        md_content.append("")
        md_content.append("---")
        md_content.append("")

        # Table of Contents
        if toc:
            md_content.append("## Table of Contents")
            md_content.append("")
            for level, title, page in toc:
                indent = "  " * (level - 1)
                anchor = title.lower().replace(' ', '-').replace('.', '')[:50]
                md_content.append(f"{indent}- [{title}](#{anchor}) *(p. {page})*")
            md_content.append("")
            md_content.append("---")
            md_content.append("")

        # Extract text from each page
        md_content.append("## Full Text")
        md_content.append("")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            if not text.strip():
                continue

            # Clean text
            text = clean_text(text)

            # Add page marker
            md_content.append(f"\n<!-- PAGE {page_num + 1} -->\n")
            md_content.append(f"### Page {page_num + 1}")
            md_content.append("")

            # Process text blocks
            blocks = text.split('\n\n')
            for block in blocks:
                block = block.strip()
                if not block:
                    continue

                # Check for section headers
                header = detect_section_header(block.split('\n')[0] if '\n' in block else block)
                if header:
                    level, title = header
                    md_content.append(f"{'#' * (level + 2)} {title}")
                    md_content.append("")
                    # Add remaining text if any
                    remaining = '\n'.join(block.split('\n')[1:]).strip()
                    if remaining:
                        md_content.append(remaining)
                        md_content.append("")
                else:
                    # Regular paragraph
                    md_content.append(block)
                    md_content.append("")

        doc.close()

        # Write to file
        output_path.write_text('\n'.join(md_content), encoding='utf-8')

        return {
            'success': True,
            'input': pdf_path.name,
            'output': md_filename,
            'pages': len(doc) if 'doc' not in locals() else page_num + 1,
            'size_kb': output_path.stat().st_size / 1024
        }

    except Exception as e:
        return {
            'success': False,
            'input': pdf_path.name,
            'error': str(e)
        }


def parse_guideline_info(filename):
    """
    Extract year and topic from filename
    """
    name = filename.replace('.pdf', '')
    parts = name.split('_', 1)

    if len(parts) == 2:
        year = parts[0]
        topic = parts[1].replace('_', ' ')
        return year, topic

    return "Unknown", name


def batch_convert_pdfs(input_dir, output_dir):
    """
    Convert all PDFs in directory to Markdown
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all PDFs
    pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files to convert")
    print("=" * 60)

    results = {'success': [], 'failed': []}

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Converting: {pdf_path.name}")

        result = convert_pdf_to_markdown(pdf_path, output_dir)

        if result['success']:
            print(f"  -> {result['output']} ({result['size_kb']:.1f} KB)")
            results['success'].append(result)
        else:
            print(f"  ERROR: {result['error']}")
            results['failed'].append(result)

    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Success: {len(results['success'])}/{len(pdf_files)}")
    print(f"Failed:  {len(results['failed'])}/{len(pdf_files)}")

    if results['success']:
        total_size = sum(r['size_kb'] for r in results['success'])
        print(f"\nTotal output size: {total_size:.1f} KB ({total_size/1024:.2f} MB)")

    if results['failed']:
        print("\nFailed conversions:")
        for r in results['failed']:
            print(f"  - {r['input']}: {r['error']}")

    return results


if __name__ == "__main__":
    # Configuration
    GUIDELINES_DIR = "../references/esc-guidelines"
    OUTPUT_DIR = "../references/esc-guidelines-md"

    # Get absolute paths
    script_dir = Path(__file__).parent
    input_dir = (script_dir / GUIDELINES_DIR).resolve()
    output_dir = (script_dir / OUTPUT_DIR).resolve()

    print("=" * 60)
    print("ESC Guidelines PDF to Markdown Converter")
    print("=" * 60)
    print(f"\nInput:  {input_dir}")
    print(f"Output: {output_dir}")

    batch_convert_pdfs(input_dir, output_dir)
