#!/usr/bin/env python3
"""
Update ESC_GUIDELINES_TOC.md with line numbers from .md files
This allows Claude to jump directly to sections using Read(offset=X)
"""

import os
import re
from pathlib import Path


def find_page_markers(md_file: Path) -> dict:
    """
    Scan a markdown file and return a mapping of page numbers to line numbers.
    Looks for <!-- PAGE X --> markers.

    Returns: {page_number: line_number}
    """
    page_to_line = {}

    with open(md_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            match = re.search(r'<!-- PAGE (\d+) -->', line)
            if match:
                page_num = int(match.group(1))
                page_to_line[page_num] = line_num

    return page_to_line


def find_section_lines(md_file: Path) -> dict:
    """
    Scan a markdown file and return a mapping of section numbers to line numbers.
    Looks for patterns like "7.4.1. Diagnosis" or "### 7.4 Section"

    Returns: {section_number: line_number}
    """
    section_to_line = {}

    # Patterns for section headers
    section_patterns = [
        r'^#+\s*(\d+(?:\.\d+)*)\s',           # "### 7.4.1 Title"
        r'^(\d+(?:\.\d+)*)\.\s+[A-Z]',         # "7.4.1. Title"
        r'^(\d+(?:\.\d+)*)\s+[A-Z]',           # "7.4.1 Title"
    ]

    with open(md_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            for pattern in section_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    section_num = match.group(1)
                    if section_num not in section_to_line:
                        section_to_line[section_num] = line_num
                    break

    return section_to_line


def build_line_index(md_dir: Path) -> dict:
    """
    Build a complete index of all .md files with page and section line numbers.

    Returns: {
        'filename.md': {
            'pages': {1: 100, 2: 150, ...},
            'sections': {'7.4': 7414, '7.4.1': 7420, ...}
        }
    }
    """
    index = {}

    md_files = sorted(md_dir.glob("*.md"))

    for md_file in md_files:
        print(f"Indexing: {md_file.name}")
        index[md_file.name] = {
            'pages': find_page_markers(md_file),
            'sections': find_section_lines(md_file)
        }
        print(f"  -> {len(index[md_file.name]['pages'])} pages, {len(index[md_file.name]['sections'])} sections")

    return index


def update_toc_file(toc_path: Path, md_dir: Path, index: dict):
    """
    Update ESC_GUIDELINES_TOC.md to include line numbers.

    Transforms:
      "- 7.4. Section Title *(p. 67)*"
    Into:
      "- 7.4. Section Title *(p. 67, L7414)*"
    """

    with open(toc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track current file context
    current_file = None
    lines = content.split('\n')
    updated_lines = []

    # Pattern to detect file declarations
    file_pattern = re.compile(r'\*\*File:\*\*\s*`([^`]+\.pdf)`')

    # Pattern to detect TOC entries with page numbers
    # Matches: "- 7.4.1. Section Title *(p. 67)*"
    toc_entry_pattern = re.compile(r'^(\s*-\s+.*?)\s*\*\(p\.\s*(\d+)\)\*\s*$')

    # Pattern to extract section number from entry
    section_pattern = re.compile(r'-\s+(?:\[)?(\d+(?:\.\d+)*)\.')

    for line in lines:
        # Check if this line declares a new file
        file_match = file_pattern.search(line)
        if file_match:
            pdf_name = file_match.group(1)
            # Convert PDF name to MD name
            current_file = pdf_name.replace('.pdf', '.md')
            updated_lines.append(line)
            continue

        # Check if this is a TOC entry with page number
        toc_match = toc_entry_pattern.match(line)
        if toc_match and current_file and current_file in index:
            entry_text = toc_match.group(1)
            page_num = int(toc_match.group(2))

            # Try to find the line number
            line_num = None

            # First try: exact page marker
            file_index = index[current_file]
            if page_num in file_index['pages']:
                line_num = file_index['pages'][page_num]

            # Second try: look for section number
            if line_num is None:
                section_match = section_pattern.search(entry_text)
                if section_match:
                    section_num = section_match.group(1)
                    if section_num in file_index['sections']:
                        line_num = file_index['sections'][section_num]

            # Update the line with line number
            if line_num:
                updated_line = f"{entry_text} *(p. {page_num}, L{line_num})*"
            else:
                updated_line = line  # Keep original if no line found

            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    # Write updated content
    updated_content = '\n'.join(updated_lines)

    with open(toc_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    return len([l for l in updated_lines if ', L' in l])


def main():
    # Configuration
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    md_dir = repo_root / "references" / "esc-guidelines-md"
    toc_path = repo_root / "ESC_GUIDELINES_TOC.md"

    print("=" * 60)
    print("ESC Guidelines TOC Line Number Updater")
    print("=" * 60)
    print(f"\nMarkdown dir: {md_dir}")
    print(f"TOC file: {toc_path}")

    if not md_dir.exists():
        print(f"\nERROR: Markdown directory not found: {md_dir}")
        return

    if not toc_path.exists():
        print(f"\nERROR: TOC file not found: {toc_path}")
        return

    # Build index
    print("\n" + "-" * 60)
    print("Building line number index...")
    print("-" * 60)
    index = build_line_index(md_dir)

    # Update TOC
    print("\n" + "-" * 60)
    print("Updating TOC with line numbers...")
    print("-" * 60)
    entries_updated = update_toc_file(toc_path, md_dir, index)

    print(f"\nDone! Updated {entries_updated} TOC entries with line numbers.")
    print("\nFormat: *(p. 67, L7414)* means page 67 in PDF, line 7414 in .md file")


if __name__ == "__main__":
    main()
