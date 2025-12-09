#!/usr/bin/env python3
"""
Script per estrarre tutte le raccomandazioni ESC dai file delle linee guida
e generare un CSV con:
- Testo della raccomandazione
- Classe (I, IIa, IIb, III)
- Livello (A, B, C)
- Nome della tabella
- Linea guida (nome del file)
- Pagina
"""

import os
import re
import csv
from pathlib import Path

# Directory con i file delle linee guida
GUIDELINES_DIR = Path("/Users/benjamindeornelas/Documents/bdeornelas.github.io/claude-project-files")
OUTPUT_CSV = Path("/Users/benjamindeornelas/Documents/bdeornelas.github.io/esc_recommendations.csv")

def extract_guideline_info(filename):
    """Estrae anno e nome della linea guida dal nome del file"""
    # Es: 2023_CVD_Diabetes.md -> (2023, CVD Diabetes)
    match = re.match(r'(\d{4})_(.+)\.md', filename)
    if match:
        year = match.group(1)
        name = match.group(2).replace('_', ' ')
        return year, name
    return None, filename

def parse_recommendations(content, guideline_name, year):
    """Estrae le raccomandazioni dal contenuto del file markdown"""
    recommendations = []

    # Trova tutte le occorrenze delle tabelle di raccomandazione
    # e il contenuto che segue fino alla prossima sezione
    lines = content.split('\n')

    current_table_num = None
    current_table_name = None
    current_page = None
    in_recommendation_table = False
    recommendation_text = []
    table_counter = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Cerca il numero di pagina
        page_match = re.search(r'<!-- PAGE (\d+) -->', line)
        if page_match:
            current_page = page_match.group(1)

        # Cerca l'inizio di una tabella di raccomandazione
        # Formato 2022+: "Recommendation Table X — Recommendations for ..."
        table_match = re.match(r'Recommendation Table (\d+) — (.+)', line)
        if table_match:
            current_table_num = table_match.group(1)
            current_table_name = table_match.group(2).strip()
            in_recommendation_table = True
            recommendation_text = []
            i += 1
            continue

        # Formato 2020-2021: "Recommendations for ..." seguito da "Recommendations" e "Classa"
        if line.startswith('Recommendations for ') and not in_recommendation_table:
            # Verifica che le prossime righe contengano "Recommendations" e "Classa"
            if i + 2 < len(lines):
                next_lines = [lines[j].strip() for j in range(i+1, min(i+4, len(lines)))]
                if 'Recommendations' in next_lines or 'Classa' in next_lines:
                    table_counter += 1
                    current_table_num = str(table_counter)
                    current_table_name = line.replace('Recommendations for ', '').strip()
                    in_recommendation_table = True
                    recommendation_text = []
                    i += 1
                    continue

        if in_recommendation_table:
            # Skip header lines like "Recommendations", "Classa", "Levelb"
            if line in ['Recommendations', 'Classa', 'Levelb', '']:
                i += 1
                continue

            # Check if we hit the end marker
            if line.startswith('© ESC'):
                in_recommendation_table = False
                i += 1
                continue

            # Check if this is a footnote or abbreviation line
            if line.startswith('a') and 'Class of recommendation' in line:
                in_recommendation_table = False
                i += 1
                continue

            # Check for new table or section
            if re.match(r'Recommendation Table \d+', line) or re.match(r'Table \d+', line):
                in_recommendation_table = False
                continue

            # Check if line is just a Class indicator (I, IIa, IIb, III)
            if line in ['I', 'IIa', 'IIb', 'III']:
                # The next line should be the level
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line in ['A', 'B', 'C']:
                        # We have a complete recommendation
                        if recommendation_text:
                            rec_text = ' '.join(recommendation_text).strip()
                            # Clean up the recommendation text
                            rec_text = re.sub(r'\s+', ' ', rec_text)
                            rec_text = re.sub(r'\d+[,\d]*$', '', rec_text).strip()  # Remove trailing reference numbers

                            # Remove page markers and continued markers
                            rec_text = re.sub(r'Continued.*$', '', rec_text, flags=re.IGNORECASE).strip()
                            rec_text = re.sub(r'<!-- PAGE \d+ -->.*$', '', rec_text).strip()
                            rec_text = re.sub(r'### Page \d+.*$', '', rec_text).strip()
                            rec_text = re.sub(r'ESC \d+.*$', '', rec_text).strip()

                            # Remove footnote references like superscript numbers
                            rec_text = re.sub(r'[,\d]+$', '', rec_text).strip()

                            if rec_text and len(rec_text) > 10:  # Only add meaningful recommendations
                                recommendations.append({
                                    'recommendation': rec_text,
                                    'class': line,
                                    'level': next_line,
                                    'table_number': current_table_num,
                                    'table_name': current_table_name,
                                    'guideline': guideline_name,
                                    'year': year,
                                    'page': current_page
                                })
                            recommendation_text = []
                        i += 2
                        continue
                i += 1
                continue

            # Check if line is just a Level indicator
            if line in ['A', 'B', 'C']:
                i += 1
                continue

            # This is recommendation text
            recommendation_text.append(line)

        i += 1

    return recommendations

def process_all_guidelines():
    """Processa tutti i file delle linee guida"""
    all_recommendations = []

    # Lista dei file delle linee guida
    guideline_files = sorted(GUIDELINES_DIR.glob("*.md"))

    for filepath in guideline_files:
        if filepath.name == "ESC_GUIDELINES_TOC.md":
            continue

        print(f"Processing: {filepath.name}")

        year, guideline_name = extract_guideline_info(filepath.name)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        recs = parse_recommendations(content, guideline_name, year)
        all_recommendations.extend(recs)
        print(f"  Found {len(recs)} recommendations")

    return all_recommendations

def write_csv(recommendations, output_path):
    """Scrive le raccomandazioni in un file CSV"""
    fieldnames = [
        'recommendation',
        'class',
        'level',
        'table_number',
        'table_name',
        'guideline',
        'year',
        'page'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recommendations)

    print(f"\nWritten {len(recommendations)} recommendations to {output_path}")

def main():
    print("ESC Guidelines Recommendation Extractor")
    print("=" * 50)

    recommendations = process_all_guidelines()

    if recommendations:
        write_csv(recommendations, OUTPUT_CSV)

        # Print summary
        print("\nSummary:")
        print(f"Total recommendations: {len(recommendations)}")

        # Count by class
        class_counts = {}
        for rec in recommendations:
            cls = rec['class']
            class_counts[cls] = class_counts.get(cls, 0) + 1
        print("\nBy Class:")
        for cls in ['I', 'IIa', 'IIb', 'III']:
            if cls in class_counts:
                print(f"  Class {cls}: {class_counts[cls]}")

        # Count by level
        level_counts = {}
        for rec in recommendations:
            lvl = rec['level']
            level_counts[lvl] = level_counts.get(lvl, 0) + 1
        print("\nBy Level:")
        for lvl in ['A', 'B', 'C']:
            if lvl in level_counts:
                print(f"  Level {lvl}: {level_counts[lvl]}")

        # Count by guideline
        guideline_counts = {}
        for rec in recommendations:
            guide = f"{rec['year']} {rec['guideline']}"
            guideline_counts[guide] = guideline_counts.get(guide, 0) + 1
        print("\nBy Guideline:")
        for guide in sorted(guideline_counts.keys()):
            print(f"  {guide}: {guideline_counts[guide]}")
    else:
        print("No recommendations found!")

if __name__ == "__main__":
    main()
