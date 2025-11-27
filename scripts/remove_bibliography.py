#!/usr/bin/env python3
"""
Remove bibliography/references sections from ESC guideline markdown files.
The references are numbered citations that confuse the LLM.
"""
import os
import re
from pathlib import Path

GUIDELINES_DIR = Path(__file__).parent.parent / "claude-project-files"

def find_references_start(content: str) -> int:
    """Find where the actual references section starts (not TOC mentions)."""
    lines = content.split('\n')

    # Look for patterns like "## References", "22. References", "References" as a header
    # But skip TOC lines (which contain links like [References](#references))
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip TOC entries (contain brackets and links)
        if '[' in stripped or '](#' in stripped:
            continue

        # Skip lines that are part of page references like "References . . . . . . . . 3312"
        if '. . .' in stripped:
            continue

        # Match actual reference section headers
        # Patterns: "## References", "22. References", "References", "12 References"
        if re.match(r'^#+\s*References\s*$', stripped, re.IGNORECASE):
            return i
        if re.match(r'^\d+\.?\s+References\s*$', stripped, re.IGNORECASE):
            return i
        if stripped.lower() == 'references':
            return i

    return -1

def find_first_numbered_reference(content: str, start_line: int) -> int:
    """Find the first numbered reference like '1. Author...' after the header."""
    lines = content.split('\n')

    for i in range(start_line, min(start_line + 50, len(lines))):
        stripped = lines[i].strip()
        # Match numbered references like "1. Knuuti J, Wijns W..."
        if re.match(r'^1\.\s+[A-Z]', stripped):
            return i

    return -1

def remove_bibliography(filepath: Path) -> tuple[bool, int, int]:
    """Remove bibliography from a file. Returns (modified, lines_before, lines_after)."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    original_count = len(lines)

    ref_header_line = find_references_start(content)

    if ref_header_line == -1:
        # Try finding the first numbered reference directly
        for i, line in enumerate(lines):
            if re.match(r'^1\.\s+[A-Z][a-z]+\s+[A-Z]', line.strip()):
                # Found a numbered reference, look for the section header above
                for j in range(max(0, i - 20), i):
                    if 'references' in lines[j].lower() and '[' not in lines[j]:
                        ref_header_line = j
                        break
                if ref_header_line == -1:
                    ref_header_line = i  # Start from the first reference
                break

    if ref_header_line == -1:
        return False, original_count, original_count

    # Keep content up to but not including the references section
    # But also remove the References entry from the TOC
    new_lines = []
    for i, line in enumerate(lines[:ref_header_line]):
        # Skip TOC entries pointing to references
        if re.search(r'\[.*References.*\]\(#', line, re.IGNORECASE):
            continue
        if re.search(r'References\s*\.\s*\.\s*\.', line):
            continue
        new_lines.append(line)

    # Remove trailing empty lines
    while new_lines and not new_lines[-1].strip():
        new_lines.pop()

    new_content = '\n'.join(new_lines) + '\n'
    filepath.write_text(new_content, encoding='utf-8')

    return True, original_count, len(new_lines)

def main():
    print("Removing bibliography from ESC guideline files...\n")

    md_files = sorted(GUIDELINES_DIR.glob("*.md"))

    # Skip TOC file
    md_files = [f for f in md_files if 'TOC' not in f.name]

    total_lines_removed = 0

    for filepath in md_files:
        modified, before, after = remove_bibliography(filepath)
        removed = before - after

        if modified:
            total_lines_removed += removed
            print(f"✓ {filepath.name}: {before} → {after} lines (-{removed})")
        else:
            print(f"- {filepath.name}: no references found")

    print(f"\nTotal lines removed: {total_lines_removed}")

if __name__ == "__main__":
    main()
