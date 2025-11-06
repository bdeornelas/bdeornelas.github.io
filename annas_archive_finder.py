#!/usr/bin/env python3
"""
Anna's Archive Paper Finder
Cerca articoli scientifici su Anna's Archive
"""

import requests
import json
import re
from urllib.parse import quote
from pathlib import Path

class AnnasArchiveFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_by_title(self, title):
        """Cerca per titolo su Anna's Archive"""
        print(f"Cercando per titolo: {title}")
        
        # Anna's Archive search API
        search_url = "https://annas-archive.org/search"
        
        # Parametri di ricerca
        params = {
            'q': title,
            'searchfield': 'all',
            'sort': 'relevance',
            'view': 'list'
        }
        
        try:
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Cerca pattern di risultati nella pagina HTML
            # Anna's Archive usa strutture specifiche per mostrare i risultati
            
            results = []
            
            # Cerca div con risultati
            result_patterns = [
                r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
                r'<div[^>]*data-doi[^>]*>(.*?)</div>'
            ]
            
            for pattern in result_patterns:
                matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
                results.extend(matches)
            
            return results
            
        except Exception as e:
            print(f"Errore nella ricerca per titolo: {e}")
            return []

    def search_by_doi(self, doi):
        """Cerca per DOI su Anna's Archive"""
        print(f"Cercando per DOI: {doi}")
        
        # Anna's Archive ha anche ricerca diretta per DOI
        search_url = f"https://annas-archive.org/search/{quote(doi)}"
        
        try:
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Controlla se c'è una pagina specifica per il DOI
            if response.url != search_url:
                print(f"Rinviato a: {response.url}")
                # Segui il redirect
                final_response = self.session.get(response.url, timeout=30)
                return self.extract_results(final_response.text)
            
            return self.extract_results(response.text)
            
        except Exception as e:
            print(f"Errore nella ricerca per DOI: {e}")
            return []

    def extract_results(self, html_content):
        """Estrae i risultati dal contenuto HTML"""
        results = []
        
        # Pattern per identificare file scaricabili
        download_patterns = [
            r'href="(/md5/[a-f0-9]{32})"[^>]*>[^<]*\.pdf[^<]*</a>',
            r'href="(/download/[a-zA-Z0-9]+)"[^>]*>[^<]*\.pdf[^<]*</a>',
            r'data-download="(/[^"]+)"[^>]*>[^<]*\.pdf[^<]*</a>'
        ]
        
        for pattern in download_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            results.extend(matches)
        
        # Cerca anche link generici a file
        generic_pdf_patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'download[^>]*="([^"]*\.pdf[^"]*)"'
        ]
        
        for pattern in generic_pdf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            results.extend(matches)
        
        return results

    def download_file(self, download_url, title):
        """Scarica un file da Anna's Archive"""
        try:
            print(f"Scaricando: {download_url}")
            
            # Costruisci l'URL completo
            if download_url.startswith('/'):
                full_url = f"https://annas-archive.org{download_url}"
            else:
                full_url = download_url
            
            response = self.session.get(full_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Crea la directory di output
            output_dir = Path("annas_archive_papers")
            output_dir.mkdir(exist_ok=True)
            
            # Determina l'estensione del file
            content_type = response.headers.get('content-type', '')
            if 'pdf' in content_type:
                extension = '.pdf'
            else:
                extension = '.dat'  # default per Anna's Archive
            
            # Salva il file
            filename = f"{title.replace(' ', '_').replace('/', '_')}{extension}"
            filepath = output_dir / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"File salvato: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Errore nel download: {e}")
            return None

    def search_paper(self, title, doi=None):
        """Cerca un paper su Anna's Archive"""
        print(f"=== Ricerca su Anna's Archive ===")
        print(f"Titolo: {title}")
        if doi:
            print(f"DOI: {doi}")
        print()
        
        all_results = []
        
        # Prima cerca per DOI se disponibile
        if doi:
            doi_results = self.search_by_doi(doi)
            if doi_results:
                print(f"Trovati {len(doi_results)} risultati per DOI")
                all_results.extend(doi_results)
        
        # Poi cerca per titolo
        title_results = self.search_by_title(title)
        if title_results:
            print(f"Trovati {len(title_results)} risultati per titolo")
            all_results.extend(title_results)
        
        if not all_results:
            print("Nessun risultato trovato su Anna's Archive")
            return None
        
        print(f"\nTotale risultati trovati: {len(all_results)}")
        
        # Prova a scaricare il primo risultato valido
        for i, result in enumerate(all_results[:3]):  # Prova i primi 3 risultati
            print(f"\nTentativo {i+1}: {result}")
            filepath = self.download_file(result, title)
            if filepath:
                return filepath
        
        print("Nessun file è stato scaricato con successo")
        return None

def main():
    title = "Exercise responses in ventricular septal defect"
    doi = "10.1016/1058-9813(93)90052-2"
    
    finder = AnnasArchiveFinder()
    result = finder.search_paper(title, doi)
    
    if result:
        print(f"\n✅ SUCCESSO! Paper trovato e scaricato in: {result}")
    else:
        print("\n❌ Paper non trovato su Anna's Archive")
        print("\nSuggerimenti:")
        print("1. Verifica il titolo esatto dell'articolo")
        print("2. Prova varianti del titolo")
        print("3. Cerca manualmente su annas-archive.org")
        print("4. Anna's Archive potrebbe non avere tutti gli articoli")

if __name__ == "__main__":
    main()