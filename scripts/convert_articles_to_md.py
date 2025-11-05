#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"

FALLBACK_MARKERS = [
    "<!-- Fallback: se GitHub Pages non applica il layout Jekyll, carica gli asset minimi qui -->",
    "https://cdn.tailwindcss.com",
    "https://unpkg.com/aos@2.3.1/dist/aos.css",
    "https://unpkg.com/aos@2.3.1/dist/aos.js",
    "/assets/css/style.min.css",
    "https://unpkg.com/lucide@latest",
]

def strip_fallback_snippet(text: str) -> str:
    lines = text.splitlines()
    keep = []
    skip_ids = set()

    # remove explicit fallback asset lines
    for i, line in enumerate(lines):
        if any(marker in line for marker in FALLBACK_MARKERS):
            skip_ids.add(i)

    # remove the container wrapper open line if present
    for i, line in enumerate(lines):
        if '<div class="container mx-auto px-4 sm:px-6 lg:px-8">' in line:
            skip_ids.add(i)
            # also try to remove a trailing standalone closing </div> added as pair (search from bottom)
            for j in range(len(lines) - 1, -1, -1):
                if lines[j].strip() == "</div>":
                    skip_ids.add(j)
                    break
            break

    # remove fallback init script block if present
    in_fallback_script = False
    for i, line in enumerate(lines):
        if "<!-- Fallback init script" in line:
            in_fallback_script = True
            skip_ids.add(i)
            continue
        if in_fallback_script:
            skip_ids.add(i)
            if "</script>" in line:
                in_fallback_script = False

    for i, line in enumerate(lines):
        if i not in skip_ids:
            keep.append(line)

    return "\n".join(keep) + ("\n" if keep and keep[-1] != "" else "")

def convert_one(index_html: Path) -> bool:
    txt = index_html.read_text(encoding="utf-8")
    if not txt.lstrip().startswith("---"):
        # require front matter; if not present, skip
        return False
    cleaned = strip_fallback_snippet(txt)
    index_md = index_html.with_suffix(".md")
    index_md.write_text(cleaned, encoding="utf-8")
    index_html.unlink()
    return True

def main() -> int:
    if not ARTICLES.exists():
        print("Cartella 'articles' non trovata", file=sys.stderr)
        return 1
    converted = []
    skipped = []
    for child in sorted(ARTICLES.iterdir()):
        if not child.is_dir():
            continue
        idx = child / "index.html"
        if not idx.exists():
            continue
        try:
            ok = convert_one(idx)
            if ok:
                converted.append(str(child))
            else:
                skipped.append(str(child))
        except Exception as e:
            print(f"Errore su {idx}: {e}")
            skipped.append(str(child))

    print(f"Convertiti: {len(converted)}")
    for p in converted:
        print(f"  - {p}")
    if skipped:
        print(f"Saltati: {len(skipped)}")
        for p in skipped:
            print(f"  - {p}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

