#!/usr/bin/env python3
"""
Sci-Hub Paper Finder
Trova e scarica articoli scientifici da Sci-Hub
"""

import requests
import re
from urllib.parse import quote
from pathlib import Path

class SciHubFinder:
    def __init__(self):
        # Lista di mirror Sci-Hub da provare
        self.mirrors = [
            "https://sci-hub.se",
            "https://sci-hub.ru",
            "https://sci-hub.st",
            "https://sci-hub.wf",
            "https://sci-hub.sh",
            "https://sci-hub.pl",
            "https://sci-hub.tw",
            "https://sci-hub.hk",
            "https://sci-hub.mn"
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_paper(self, title, doi=None):
        """Cerca un articolo usando il titolo o DOI"""
        print(f"Cercando: {title}")

        # Usa il DOI se fornito, altrimenti codifica il titolo
        if doi:
            # Estrai solo il DOI puro dall'URL
            if 'doi.org/' in doi:
                clean_doi = doi.split('doi.org/')[1]
            else:
                clean_doi = doi
            # Non URL-encodare il DOI, usalo direttamente
            encoded_query = clean_doi
            print(f"Usando DOI pulito: {clean_doi}")
        else:
            encoded_query = quote(title)

        # Prova ogni mirror disponibile
        for mirror in self.mirrors:
            print(f"Provando mirror: {mirror}")
            url = f"{mirror}/{encoded_query}"
            print(f"URL Sci-Hub: {url}")

            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                # Controlla se abbiamo trovato il PDF
                if 'pdf' in response.headers.get('content-type', '').lower():
                    print("PDF trovato direttamente!")
                    filename = f"{title.replace(' ', '_').replace('/', '_')}.pdf"
                    return response.content, filename

                # Cerca il link al PDF nella pagina HTML
                pdf_match = re.search(r'href="([^"]*\.pdf[^"]*)"', response.text, re.IGNORECASE)
                if pdf_match:
                    pdf_url = pdf_match.group(1)
                    if not pdf_url.startswith('http'):
                        pdf_url = f"{mirror}{pdf_url}"
                    print(f"Link PDF trovato: {pdf_url}")

                    # Scarica il PDF
                    pdf_response = self.session.get(pdf_url, timeout=30)
                    pdf_response.raise_for_status()
                    filename = f"{title.replace(' ', '_').replace('/', '_')}.pdf"
                    return pdf_response.content, filename

                # Se non trovato, continua con il prossimo mirror
                print(f"PDF non trovato su {mirror}, provo il prossimo...")
                continue

            except Exception as e:
                print(f"Errore su {mirror}: {e}")
                continue

        # Nessun mirror ha funzionato
        print("Nessun mirror ha restituito il paper.")
        return None, None

    def save_paper(self, content, filename):
        """Salva il contenuto del paper"""
        output_dir = Path("papers")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        with open(filepath, 'wb') as f:
            f.write(content)

        print(f"Paper salvato: {filepath}")
        return filepath

def main():
    title = "Exercise responses in ventricular septal defect"
    doi = "https://doi.org/10.1016/1058-9813(93)90052-2"

    finder = SciHubFinder()
    content, filename = finder.search_paper(title, doi)

    if content and filename:
        filepath = finder.save_paper(content, filename)
        print(f"\nSuccesso! Paper disponibile in: {filepath}")
    else:
        print("\nPaper non trovato. Potrebbe essere necessario:")
        print("1. Verificare l'ortografia del titolo")
        print("2. Cercare il DOI dell'articolo")
        print("3. Provare con un motore di ricerca accademico")

if __name__ == "__main__":
    main()