#!/usr/bin/env python3
import re
from pathlib import Path

# Mapping slug -> ISO date (YYYY-MM-DD)
MAPPING = {
    "attivita-fisica-cuore": "2025-09-02",
    "holter-pressorio-mapa": "2025-09-03",
    "bradicardie-blocchi-av": "2025-09-04",
    "insufficienza-aortica": "2025-09-06",
    "arteriopatia-periferica": "2025-09-07",
    "dieta-mediterranea-colesterolo": "2025-09-09",
    "risonanza-cardiaca": "2025-09-10",
    "flutter-atriale": "2025-09-11",
    "stenosi-aortica": "2025-09-13",
    "ictus-tia": "2025-09-14",
    "angina-pectoris": "2025-09-16",
    "pericardite": "2025-09-17",
    "tpsv": "2025-09-18",
    "fumo-e-cuore": "2025-09-20",
    "aneurisma-aortico": "2025-09-21",
    "cardiomiopatia-ipertrofica": "2025-09-23",
    "tac-coronarica": "2025-09-24",
    "insufficienza-tricuspidale": "2025-09-25",
    "sincope": "2025-09-27",
    "anticoagulanti-doac-warfarin": "2025-09-28",
    "cardiomiopatia-dilatativa": "2025-10-02",
    "embolia-polmonare-tvp": "2025-10-03",
    "stenosi-mitralica": "2025-10-04",
    "tachicardia-ventricolare": "2025-10-06",
    "tilt-test": "2025-10-07",
    "malattia-coronarica": "2025-10-09",
    "insufficienza-mitralica": "2025-10-10",
    "vita-con-pacemaker-icd": "2025-10-11",
    "apnee-del-sonno-cuore": "2025-10-13",
    "miocardite": "2025-10-14",
    "soffio-al-cuore": "2025-10-16",
    "ipertensione-gestione": "2025-10-17",
    "scompenso-cardiaco": "2025-10-18",
    "ipertensione-polmonare": "2025-10-20",
    "endocardite-infettiva": "2025-10-21",
    "statine-target-ldl": "2025-10-29",
    "test-ergometrico": "2025-10-30",
    "holter-ecg": "2025-10-31",
    "ecocardiogramma-importanza": "2025-11-01",
    "extrasistoli": "2025-11-02",
    "prevenzione-cardiovascolare": "2025-11-03",
    "colesterolo-alto": "2025-11-04",
    "ipertensione-arteriosa": "2025-11-05",
    "infarto-miocardico": "2025-11-06",
    "fibrillazione-atriale": "2025-11-07",
}

MONTHS_IT = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}

def human_it(date_iso: str) -> str:
    y, m, d = date_iso.split("-")
    y = int(y); m = int(m); d = int(d)
    return f"{d} {MONTHS_IT[m]} {y}"

def update_front_matter(lines, date_iso: str):
    # find yaml front matter block
    if not lines or lines[0].strip() != '---':
        return lines, False
    # locate closing '---'
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return lines, False
    changed = False
    # search for existing date:
    for i in range(1, end):
        if re.match(r"^date:\s*", lines[i]):
            if lines[i].strip() != f'date: "{date_iso}"':
                lines[i] = f'date: "{date_iso}"\n'
                changed = True
            return lines, changed
    # not found: insert before closing
    insert_at = end
    lines.insert(insert_at, f'date: "{date_iso}"\n')
    changed = True
    return lines, changed

def update_visible_date(lines, date_iso: str):
    target = human_it(date_iso)
    # find the first calendar icon and replace the next meaningful line with target, preserving indent
    for i, line in enumerate(lines):
        if '<i data-lucide="calendar"' in line:
            # search next 1..4 lines for a date text line
            for j in range(i+1, min(i+6, len(lines))):
                txt = lines[j]
                # skip closing tags only lines
                if txt.strip() == '' or txt.strip() == '</div>':
                    continue
                # Replace whole line with preserved indentation + target
                indent = re.match(r"^\s*", txt).group(0)
                lines[j] = f"{indent}{target}\n"
                return lines, True
            break
    return lines, False

def process_file(path: Path, date_iso: str):
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines(keepends=True)
    lines, fm_changed = update_front_matter(lines, date_iso)
    lines, vd_changed = update_visible_date(lines, date_iso)
    if fm_changed or vd_changed:
        path.write_text(''.join(lines), encoding='utf-8')
    return fm_changed, vd_changed

def main():
    base = Path('_articles')
    updated = []
    skipped = []
    for slug, date_iso in MAPPING.items():
        path = base / f"{slug}.md"
        if not path.exists():
            skipped.append((slug, 'missing'))
            continue
        fm, vd = process_file(path, date_iso)
        updated.append((slug, fm, vd))
    # Summary
    print("Updated articles:")
    for slug, fm, vd in updated:
        print(f"- {slug}: front_matter={'Y' if fm else 'N'}, visible_date={'Y' if vd else 'N'}")
    if skipped:
        print("Skipped (not found):")
        for slug, reason in skipped:
            print(f"- {slug}: {reason}")

if __name__ == '__main__':
    main()

