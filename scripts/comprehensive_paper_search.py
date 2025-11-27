#!/usr/bin/env python3
"""
Comprehensive Paper Search Tool
Cerca articoli scientifici su multiple piattaforme
"""

import requests
import json
import re
from urllib.parse import quote
from pathlib import Path
import time

class ComprehensivePaperSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_google_scholar(self, title, doi):
        """Cerca su Google Scholar (simulato)"""
        print("🔍 Ricerca su Google Scholar...")
        print("NOTA: Google Scholar richiede autenticazione per l'accesso completo")
        
        # Costruisci URL di ricerca Google Scholar
        search_query = f'scholar.google.com/scholar?q="{title}" OR "{doi}"'
        print(f"URL di ricerca: https://{search_query}")
        
        print("\n📋 STRATEGIE MANUALI GOOGLE SCHOLAR:")
        print("1. Vai su scholar.google.com")
        print(f"2. Cerca: '{title}'")
        print(f"3. Oppure cerca: '{doi}'")
        print("4. Controlla se ci sono risultati disponibili")
        print("5. Cerca il pulsante [PDF] o [All versions]")
        
        return []

    def search_pubmed(self, title, doi):
        """Cerca su PubMed"""
        print("🔍 Ricerca su PubMed...")
        
        # PubMed API
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        # Cerca sia per titolo che per DOI
        queries = [
            f'"{title}"[Title]',
            f'"{title}"[All Fields]',
            f'"{doi}"[All Fields]'
        ]
        
        results = []
        
        for query in queries:
            try:
                params = {
                    'db': 'pubmed',
                    'term': query,
                    'retmax': 10,
                    'retmode': 'json'
                }
                
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    ids = data['esearchresult']['idlist']
                    if ids:
                        print(f"   Trovato ID PubMed per query '{query}': {len(ids)} risultati")
                        results.extend(ids)
                        
                        # Recupera i dettagli
                        self.get_pubmed_details(ids[:3])  # Mostra primi 3
                
                time.sleep(0.5)  # Rispetta i limiti dell'API
                
            except Exception as e:
                print(f"   Errore in ricerca PubMed: {e}")
        
        return results

    def get_pubmed_details(self, pubmed_ids):
        """Recupera dettagli da PubMed"""
        if not pubmed_ids:
            return
            
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        
        try:
            params = {
                'db': 'pubmed',
                'id': ','.join(pubmed_ids),
                'retmode': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'result' in data:
                for uid in pubmed_ids:
                    if uid in data['result']:
                        doc = data['result'][uid]
                        print(f"\n📄 RISULTATO PUBMED:")
                        print(f"   ID: {uid}")
                        print(f"   Titolo: {doc.get('title', 'N/A')}")
                        print(f"   Autori: {doc.get('authors', [{}])[0].get('name', 'N/A')}")
                        print(f"   Rivista: {doc.get('fulljournalname', 'N/A')}")
                        print(f"   PMID: https://pubmed.ncbi.nlm.nih.gov/{uid}")
                        print()
        
        except Exception as e:
            print(f"Errore nel recupero dettagli: {e}")

    def search_researchgate(self, title):
        """Cerca su ResearchGate (info manuale)"""
        print("🔍 Ricerca su ResearchGate...")
        print("ResearchGate non ha API pubblica, ma puoi:")
        print(f"1. Andare su researchgate.net")
        print(f"2. Cercare: '{title}'")
        print(f"3. Controllare se l'autore ha caricato il paper")
        print("4. Inviare messaggio diretto all'autore")
        
        return []

    def search_alternative_terms(self, title):
        """Prova varianti del titolo"""
        print("🔍 Prova con termini alternativi...")
        
        terms = [
            title,
            title.replace('in ', ''),
            title.replace('responses', 'response'),
            'ventricular septal defect exercise',
            'VSD exercise response',
            'exercise ventricular defect'
        ]
        
        results = {}
        
        for term in terms:
            print(f"\n🔎 Cerco: '{term}'")
            results[term] = self.basic_search(term)
            
        return results

    def basic_search(self, search_term):
        """Ricerca di base web"""
        try:
            # Prova una ricerca generica
            search_url = "https://duckduckgo.com/html"
            params = {'q': f'"{search_term}" filetype:pdf'}
            
            response = self.session.get(search_url, params=params, timeout=15)
            # Nota: duckduckgo potrebbe richiedere JavaScript
            
            if response.status_code == 200:
                # Cerca pattern di PDF
                pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', response.text, re.IGNORECASE)
                if pdf_links:
                    print(f"   Trovati {len(pdf_links)} link PDF")
                    return pdf_links[:3]  # Primi 3 risultati
            
        except Exception as e:
            print(f"   Errore ricerca base: {e}")
        
        return []

    def provide_alternative_access_methods(self, title, doi):
        """Fornisce metodi alternativi per accedere al paper"""
        print("\n" + "="*60)
        print("📚 METODI ALTERNATIVI DI ACCESSO")
        print("="*60)
        
        print("\n1. 📖 ACCESSO ISTITUZIONALE:")
        print("   - Verifica con la biblioteca universitaria")
        print("   - Contatta il reparto cardiochirurgia")
        print("   - Usa il login istituzionale")
        
        print("\n2. 📧 CONTATTO DIRETTO:")
        print("   - Cerca l'autore su ResearchGate")
        print("   - Invia email accademica")
        print("   - Chiedi tramite colleghi")
        
        print("\n3. 📄 SERVIZI DOCUMENTALI:")
        print("   - WorldCat per biblioteche locali")
        print("   - Document delivery universitario")
        print("   - ILL (InterLibrary Loan)")
        
        print("\n4. 🔍 RICERCHE ALTERNATIVE:")
        print("   - Cerca review più recenti")
        print("   - Controlla linee guida ESC/AHA")
        print("   - Cerca meta-analisi sull'argomento")
        
        print("\n5. 📊 BASI DATI SPECIALIZZATE:")
        print("   - EMBASE (se hai accesso)")
        print("   - Web of Science")
        print("   - Cochrane Library")
        
        print(f"\n6. 🆔 DOI DI RIFERIMENTO:")
        print(f"   DOI: {doi}")
        print(f"   Puoi provare questo DOI direttamente:")

        # Prova URL alternativi per DOI
        doi_variants = [
            f"https://doi.org/{doi}",
            f"https://dx.doi.org/{doi}",
            f"https://r.jina.ai/http://doi.org/{doi}"  # Jina AI reader
        ]
        
        for url in doi_variants:
            print(f"   - {url}")
        
        print("\n7. 🗂️ REPOSITORY ISTITUZIONALI:")
        print("   - Controlla il sito dell'autore")
        print("   - Cerca su arXiv se pubblicato lì")
        print("   - Repository dell'università dell'autore")

    def comprehensive_search(self, title, doi):
        """Esegue ricerca completa"""
        print("🔍 COMPREHENSIVE PAPER SEARCH")
        print("="*60)
        print(f"Titolo: {title}")
        print(f"DOI: {doi}")
        print("="*60)
        
        all_results = {}
        
        # Ricerca su diverse piattaforme
        all_results['pubmed'] = self.search_pubmed(title, doi)
        all_results['google_scholar'] = self.search_google_scholar(title, doi)
        all_results['researchgate'] = self.search_researchgate(title)
        
        # Ricerca con termini alternativi
        all_results['alternative_terms'] = self.search_alternative_terms(title)
        
        # Fornisci metodi alternativi
        self.provide_alternative_access_methods(title, doi)
        
        # Riepilogo risultati
        print("\n" + "="*60)
        print("📊 RIEPILOGO RISULTATI")
        print("="*60)
        
        total_found = sum(len(v) if isinstance(v, list) else 0 for v in all_results.values())
        
        if total_found > 0:
            print("✅ Alcuni risultati trovati! Controlla sopra per i dettagli.")
        else:
            print("❌ Nessun risultato diretto trovato.")
        
        print(f"\n🔗 LINK UTILI PER TENTATIVI MANUALI:")
        print(f"Google Scholar: https://scholar.google.com/scholar?q={quote(title)}")
        print(f"PubMed Search: https://pubmed.ncbi.nlm.nih.gov/?term={quote(title)}")
        print(f"ResearchGate: https://www.researchgate.net/search?q={quote(title)}")
        print(f"DOI Direct: https://doi.org/{doi}")

def main():
    title = "Exercise responses in ventricular septal defect"
    doi = "10.1016/1058-9813(93)90052-2"
    
    searcher = ComprehensivePaperSearch()
    searcher.comprehensive_search(title, doi)

if __name__ == "__main__":
    main()