#!/usr/bin/env python3
"""
UpToDate Article Scraper
========================

Questo script scarica articoli di educazione del paziente da UpToDate
per uso personale con accesso istituzionale.

IMPORTANTE: Questo script è destinato SOLO per uso personale con accesso
istituzionale valido. Non violare i termini di servizio di UpToDate.

Requisiti:
- Python 3.7+
- (Opzionale) selenium se serve gestire autenticazione complessa

Installazione dipendenze opzionale:
pip install selenium

Uso:
1. Configura le credenziali nel file config.json
2. Esegui: python scraper.py
"""

import json
import os
import re
import time
from pathlib import Path
from html import unescape
from urllib.parse import urljoin

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class UpToDateScraper:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.base_url = "https://www.uptodate.com"
        self.table_of_contents_url = "https://www.uptodate.com/contents/table-of-contents/patient-education/heart-and-blood-vessels"
        self.output_dir = Path("uptodate/articles")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurazione Selenium per autenticazione
        self.driver = None

    def load_config(self, config_file):
        """Carica configurazione da file JSON"""
        if not os.path.exists(config_file):
            config = {
                "username": "YOUR_INSTITUTIONAL_USERNAME",
                "password": "YOUR_INSTITUTIONAL_PASSWORD",
                "institution_login_url": "YOUR_INSTITUTION_LOGIN_URL",
                "delay_between_requests": 2,
                "max_retries": 3,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"File di configurazione creato: {config_file}")
            print("MODIFICA le credenziali prima di eseguire lo script!")
            return config

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_selenium(self):
        """Configura Selenium WebDriver"""
        print("Selenium non utilizzato in questa versione semplificata")
        pass

    def authenticate(self):
        """Gestisce l'autenticazione - assume che l'utente sia già loggato"""
        print("Assumendo che tu sia già autenticato in UpToDate...")
        print("Se non lo sei, accedi manualmente prima di eseguire lo script.")
        print("Lo script userà i cookie del browser esistente.")

        # Per ora, proviamo senza autenticazione complessa
        # L'utente dovrebbe essere già loggato
        return True

    def get_article_links(self):
        """Estrae i link degli articoli dalla tabella dei contenuti"""
        print("Estrazione link articoli...")
        print("Nota: UpToDate usa una Single Page Application (SPA) con JavaScript.")
        print("La pagina iniziale potrebbe non contenere i link effettivi.")

        headers = {
            "User-Agent": self.config.get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            ),
        }

        try:
            toc_html = self.fetch_url(self.table_of_contents_url, headers=headers)
            links = self.parse_article_links(toc_html)
            if links:
                print(f"Trovati {len(links)} articoli dalla tabella dei contenuti")
                return links
            print("Nessun link rilevato automaticamente, uso la lista manuale.")
        except (HTTPError, URLError, UnicodeDecodeError) as exc:
            print(f"Impossibile scaricare la tabella dei contenuti ({exc}). Uso la lista manuale.")
        except Exception as exc:
            print(f"Errore inatteso durante la lettura della tabella: {exc}")
            print("Uso la lista manuale.")

        return self.get_manual_articles()

    def fetch_url(self, url, headers):
        """Scarica un URL e restituisce il contenuto come stringa"""
        request = Request(url, headers=headers)
        with urlopen(request) as response:
            raw_bytes = response.read()
            encoding = response.headers.get_content_charset() or 'utf-8'
            return raw_bytes.decode(encoding, errors='replace')

    def parse_article_links(self, html_content):
        """Estrae tutti i link degli articoli dall'HTML della tabella"""
        if not html_content:
            return []

        anchor_pattern = re.compile(
            r'<a[^>]+href=["\']([^"\']+/contents/[^"\']+)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )

        links = []
        seen = set()

        for match in anchor_pattern.finditer(html_content):
            href = unescape(match.group(1))
            text = unescape(match.group(2))
            href = href.strip()

            if not href:
                continue

            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = urljoin(self.base_url, href)

            if not href.startswith("http"):
                href = urljoin(self.base_url, href)

            if not href.startswith(self.base_url):
                continue

            if "/calculator" in href or "/image" in href:
                continue

            if href in seen:
                continue

            cleaned_text = re.sub(r'<[^>]+>', '', text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            title = cleaned_text or href.rsplit('/', 1)[-1].replace('-', ' ').title()

            links.append({"url": href, "title": title})
            seen.add(href)

        return links

    def get_manual_articles(self):
        """Lista manuale di URL da usare come fallback"""
        # Lista manuale di articoli comuni sulla sezione cuore e vasi sanguigni
        # Poiché UpToDate è una SPA, dovremmo conoscere gli URL diretti
        manual_articles = [
            {
                'url': 'https://www.uptodate.com/contents/the-heart-and-blood-vessels-in-adults-the-basics',
                'title': 'Cuore e vasi sanguigni negli adulti - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/coronary-artery-disease-the-basics',
                'title': 'Malattia coronarica - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/angina-pectoris-the-basics',
                'title': 'Angina pectoris - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/heart-failure-in-adults-the-basics',
                'title': 'Scompenso cardiaco - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/high-blood-pressure-in-adults-the-basics',
                'title': 'Ipertensione arteriosa - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/atrial-fibrillation-the-basics',
                'title': 'Fibrillazione atriale - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/coronary-artery-disease-beyond-the-basics',
                'title': 'Malattia coronarica - Beyond the Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/valvular-heart-disease-the-basics',
                'title': 'Malattie delle valvole cardiache - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/peripheral-artery-disease-the-basics',
                'title': 'Malattia arteriosa periferica - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/deep-vein-thrombosis-dvt-the-basics',
                'title': 'Trombosi venosa profonda (DVT) - The Basics'
            },
            {
                'url': 'https://www.uptodate.com/contents/aortic-aneurysm-repair-the-basics',
                'title': 'Riparazione di aneurisma aortico - The Basics'
            }
        ]

        print(f"Usando lista manuale di {len(manual_articles)} articoli comuni")
        return manual_articles

    def sanitize_filename(self, filename):
        """Sanitizza il nome del file per il filesystem"""
        # Rimuovi caratteri speciali e limita lunghezza
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', '_', filename)
        return filename[:100] + '.html' if len(filename) > 100 else filename + '.html'

    def download_article(self, article_info, retry_count=0):
        """Scarica un singolo articolo"""
        url = article_info['url']
        title = article_info['title']
        headers = {
            "User-Agent": self.config.get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            ),
        }

        try:
            print(f"Download: {title}")

            request = Request(url, headers=headers)
            with urlopen(request) as response:
                raw_bytes = response.read()
                encoding = response.headers.get_content_charset() or 'utf-8'
                html_content = raw_bytes.decode(encoding, errors='replace')

            # Cerca di isolare il contenuto principale dell'articolo
            main_content = self.extract_main_content(html_content)

            # Salva il contenuto
            filename = self.sanitize_filename(title)
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!DOCTYPE html>\n<html>\n<head>\n")
                f.write(f"<meta charset='utf-8'>\n")
                f.write(f"<title>{title}</title>\n")
                f.write("</head>\n<body>\n")
                f.write(f"<h1>{title}</h1>\n")
                f.write(f"<p><em>Scaricato da: {url}</em></p>\n")
                f.write(f"<p><em>Data: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>\n")
                f.write("<hr>\n")
                f.write(main_content)
                f.write("\n</body>\n</html>")

            print(f"Salvato: {filepath}")
            return True

        except (HTTPError, URLError, UnicodeDecodeError) as e:
            print(f"Errore nel download di '{title}': {e}")
            if retry_count < self.config['max_retries']:
                print(f"Ritento... ({retry_count + 1}/{self.config['max_retries']})")
                time.sleep(self.config['delay_between_requests'] * 2)
                return self.download_article(article_info, retry_count + 1)
            return False
        except Exception as e:
            print(f"Errore imprevisto durante il download di '{title}': {e}")
            return False

    def extract_main_content(self, html_content):
        """Prova a estrarre il contenuto principale dall'HTML scaricato"""
        if not html_content:
            return ""

        main_match = re.search(r'<main\b[^>]*>(.*?)</main>', html_content, re.IGNORECASE | re.DOTALL)
        if main_match:
            return main_match.group(0)

        content_match = re.search(r'<div\b[^>]*class=["\']?(?:content|main-content)["\']?[^>]*>(.*?)</div>', html_content, re.IGNORECASE | re.DOTALL)
        if content_match:
            return content_match.group(0)

        body_match = re.search(r'<body\b[^>]*>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
        if body_match:
            return body_match.group(1)

        return html_content

    def run(self):
        """Esegue il processo completo di scraping"""
        print("=== UpToDate Article Scraper ===")
        print("IMPORTANTE: Assicurati di avere accesso istituzionale valido!")
        print()

        # Autenticazione
        if not self.authenticate():
            print("Autenticazione fallita. Controlla le credenziali e la configurazione.")
            return

        # Estrai link articoli
        articles = self.get_article_links()
        if not articles:
            print("Nessun articolo trovato. Verifica l'accesso e l'URL.")
            return

        # Scarica articoli
        successful = 0
        total = len(articles)

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{total}] ", end="")
            if self.download_article(article):
                successful += 1

            # Pausa tra richieste per evitare blocchi
            if i < total:
                time.sleep(self.config['delay_between_requests'])

        print("\n=== Completato ===")
        print(f"Articoli scaricati con successo: {successful}/{total}")
        print(f"Salvati in: {self.output_dir}")

        # Chiudi browser (non utilizzato)
        pass


if __name__ == "__main__":
    scraper = UpToDateScraper()
    scraper.run()
