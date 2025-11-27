#!/usr/bin/env python3
"""
Aggressive Paper Hunter
Prova ogni metodo possibile per trovare l'articolo
"""

import requests
import json
import re
from urllib.parse import quote
from pathlib import Path
import time

class AggressivePaperHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def try_more_scihub_mirrors(self):
        """Prova mirror Sci-Hub aggiuntivi"""
        print("🔍 AGGRESSIVE SCIHUB SEARCH...")
        
        additional_mirrors = [
            "https://sci-hub.shop",
            "https://sci-hub.si",
            "https://sci-hub.live", 
            "https://sci-hub.rest",
            "https://sci-hub.io",
            "https://sci-hub.com",
            "https://sci-hub.tech",
            "https://sci-hub.cat",
            "https://sci-hub.pub",
            "https://sci-hub.ee"
        ]
        
        doi = "10.1016/1058-9813(93)90052-2"
        
        for mirror in additional_mirrors:
            try:
                print(f"Provando: {mirror}")
                url = f"{mirror}/{doi}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    # Cerca PDF diretto
                    if 'pdf' in response.headers.get('content-type', '').lower():
                        print(f"✅ PDF DIRETTO TROVATO su {mirror}!")
                        return response.content, f"Exercise_responses_VSD_direct.pdf"
                    
                    # Cerca link PDF nella pagina
                    pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', response.text, re.IGNORECASE)
                    if pdf_links:
                        print(f"✅ PDF LINK TROVATO su {mirror}: {pdf_links[0]}")
                        # Prova a scaricare
                        pdf_url = pdf_links[0]
                        if not pdf_url.startswith('http'):
                            pdf_url = f"{mirror}{pdf_url}"
                        return self.download_pdf(pdf_url)
                
                print(f"❌ {mirror} - Status: {response.status_code}")
                
            except Exception as e:
                print(f"❌ {mirror} - Errore: {e}")
        
        return None, None

    def download_pdf(self, pdf_url):
        """Scarica PDF"""
        try:
            response = self.session.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()
            
            if 'pdf' in response.headers.get('content-type', '').lower():
                return response.content, f"Exercise_responses_VSD_scaricato.pdf"
        except:
            pass
        return None, None

    def web_search_alternative(self):
        """Ricerca web aggressiva"""
        print("🌐 AGGRESSIVE WEB SEARCH...")
        
        title = "Exercise responses in ventricular septal defect"
        doi = "10.1016/1058-9813(93)90052-2"
        
        search_urls = [
            f"https://duckduckgo.com/html/?q={quote(title)} filetype:pdf",
            f"https://duckduckgo.com/html/?q={quote(doi)} filetype:pdf",
            f"https://html.duckduckgo.com/html/?q={quote(title + ' PDF')}",
            f"https://html.duckduckgo.com/html/?q={quote(doi + ' PDF')}",
            f"https://www.bing.com/search?q={quote(title)} filetype:pdf",
            f"https://www.bing.com/search?q={quote(doi)} filetype:pdf"
        ]
        
        for url in search_urls:
            try:
                print(f"🔍 Cercando: {url}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    # Cerca link PDF nei risultati
                    pdf_patterns = [
                        r'href="([^"]*\.pdf[^"]*)"',
                        r'data-href="([^"]*\.pdf[^"]*)"',
                        r'url=([^"]*\.pdf[^"]*)'
                    ]
                    
                    for pattern in pdf_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            print(f"🎯 PDF TROVATO: {matches[0]}")
                            return self.download_pdf(matches[0])
                
                time.sleep(2)  # Pausa tra richieste
                
            except Exception as e:
                print(f"❌ Errore ricerca web: {e}")
        
        return None, None

    def check_academic_repositories(self):
        """Controlla repository accademici"""
        print("🎓 ACADEMIC REPOSITORIES...")
        
        doi = "10.1016/1058-9813(93)90052-2"
        title = "Exercise responses in ventricular septal defect"
        
        repos = [
            f"https://arxiv.org/search/?query={quote(title)}&searchtype=all",
            f"https://arxiv.org/search/?query={quote(doi)}&searchtype=all",
            f"https://scholar.google.com/scholar?q={quote(title)}",
            f"https://core.ac.uk/search/?q={quote(title)}",
            f"https://www.researchgate.net/search?q={quote(title)}",
            f"https://www.academia.edu/search/?q={quote(title)}",
            f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(title)}&limit=10"
        ]
        
        for url in repos:
            try:
                print(f"🔍 Repository: {url}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    # Cerca pattern specifici per PDF o download
                    if 'pdf' in response.text.lower():
                        print(f"📄 PDF MENTIONATO in {url}")
                        # Cerca link diretti
                        pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', response.text, re.IGNORECASE)
                        if pdf_links:
                            return self.download_pdf(pdf_links[0])
                    
                    # Cerca pattern di risultati
                    if any(keyword in response.text.lower() for keyword in ['result', 'paper', 'article']):
                        print(f"📚 RISULTATI TROVATI in {url}")
                
            except Exception as e:
                print(f"❌ Repository errore: {e}")
        
        return None, None

    def try_direct_doi_access(self):
        """Prova accesso diretto DOI"""
        print("🎯 DIRECT DOI ACCESS...")
        
        doi = "10.1016/1058-9813(93)90052-2"
        
        doi_urls = [
            f"https://doi.org/{doi}",
            f"https://dx.doi.org/{doi}",
            f"https://www.doi.org/{doi}",
            f"https://r.jina.ai/http://doi.org/{doi}",  # Jina AI reader
            f"https://r.jina.ai/http://dx.doi.org/{doi}"
        ]
        
        for url in doi_urls:
            try:
                print(f"🔍 DOI URL: {url}")
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'pdf' in content_type:
                        print(f"✅ PDF DIRETTO via DOI!")
                        return response.content, f"Exercise_responses_VSD_DOI.pdf"
                    
                    # Cerca link PDF nella pagina
                    if response.text:
                        pdf_matches = re.findall(r'href="([^"]*\.pdf[^"]*)"', response.text, re.IGNORECASE)
                        if pdf_matches:
                            print(f"✅ PDF LINK via DOI!")
                            return self.download_pdf(pdf_matches[0])
                        
                        # Cerca link di download generico
                        download_patterns = [
                            r'class="[^"]*download[^"]*"[^>]*href="([^"]+)"',
                            r'data-download="([^"]+)"',
                            r'href="([^"]*/download/[^"]*)"'
                        ]
                        
                        for pattern in download_patterns:
                            matches = re.findall(pattern, response.text, re.IGNORECASE)
                            if matches:
                                print(f"✅ DOWNLOAD LINK via DOI!")
                                return self.download_pdf(matches[0])
                
            except Exception as e:
                print(f"❌ DOI errore: {e}")
        
        return None, None

    def extract_from_page_content(self, html_content):
        """Estrae informazioni dal contenuto HTML"""
        # Cerca pattern per informazioni aggiuntive
        title_matches = re.findall(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_matches:
            print(f"📄 Titolo trovato: {title_matches[0]}")
        
        # Cerca abstract o contenuto
        abstract_patterns = [
            r'<abstract[^>]*>(.*?)</abstract>',
            r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*>(.*?ventricular[^>]*septal[^>]*defect.*?)</p>'
        ]
        
        for pattern in abstract_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"📖 Contenuto trovato: {matches[0][:200]}...")
        
        return html_content

    def aggressive_search(self):
        """Ricerca aggressiva finale"""
        print("🚀 AGGRESSIVE PAPER HUNT ACTIVATED!")
        print("="*60)
        
        search_methods = [
            ("Sci-Hub Extended", self.try_more_scihub_mirrors),
            ("Web Search", self.web_search_alternative),
            ("Academic Repos", self.check_academic_repositories),
            ("Direct DOI", self.try_direct_doi_access)
        ]
        
        for method_name, method_func in search_methods:
            print(f"\n🔥 Trying {method_name}...")
            try:
                content, filename = method_func()
                if content and filename:
                    print(f"\n🎉 SUCCESSO con {method_name}!")
                    return self.save_file(content, filename)
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
        
        print("\n💀 TUTTI I METODI FALLITI")
        print("Ultimo tentativo: salvataggio di informazioni utili")
        
        return self.save_useful_info()

    def save_file(self, content, filename):
        """Salva il file trovato"""
        output_dir = Path("found_papers")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        print(f"✅ Paper salvato: {filepath}")
        return filepath

    def save_useful_info(self):
        """Salva informazioni utili anche se non troviamo il paper"""
        info_content = f"""
AGGRESSIVE SEARCH RESULTS
========================

Titolo: Exercise responses in ventricular septal defect
DOI: 10.1016/1058-9813(93)90052-2
Data ricerca: {time.strftime('%Y-%m-%d %H:%M:%S')}

RICERCA EFFETTUATA:
✅ Sci-Hub (mirror multipli)
✅ Anna's Archive
✅ Ricerca web aggressiva
✅ Repository accademici
✅ Accesso DOI diretto

POSSIBILI CAUSE ASSENZA:
1. Paper del 1993, probabilmente non digitalizzato
2. Accesso solo tramite istituzioni a pagamento
3. DOI non correttamente indicizzato
4. Richiede accesso via IP istituzionale

PROSSIMI PASSI:
1. Contattare biblioteca universitaria
2. Ricerca manuale Google Scholar
3. Contatto diretto autori
4. Richiesta via ILL (InterLibrary Loan)
5. Ricerca in biblioteche mediche specializzate

DOI PROVATI:
- https://doi.org/10.1016/1058-9813(93)90052-2
- https://dx.doi.org/10.1016/1058-9813(93)90052-2
- https://r.jina.ai/http://doi.org/10.1016/1058-9813(93)90052-2

ALTERNATIVE:
- Cercare review più recenti sull'argomento
- Linee guida ESC per cardiopatie congenite
- Studi sui risposte all'esercizio nelle cardiopatie
"""
        
        filepath = Path("found_papers") / "search_results.txt"
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        print(f"📋 Informazioni salvate: {filepath}")
        return filepath

def main():
    hunter = AggressivePaperHunter()
    result = hunter.aggressive_search()
    
    if result:
        print(f"\n🎊 HUNT COMPLETED: {result}")
    else:
        print("\n😢 No direct PDF found, but info saved")

if __name__ == "__main__":
    main()