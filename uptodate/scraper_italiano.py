#!/usr/bin/env python3
"""
UpToDate Italian Patient Education Scraper
==========================================

Script avanzato per scaricare TUTTI gli articoli patient education
in italiano dalla sezione cardiovascolare di UpToDate.

IMPORTANTE: Solo per uso personale con accesso istituzionale valido.

Requisiti:
- Python 3.7+
- selenium
- webdriver_manager (per gestione automatica driver)

Installazione:
pip install selenium webdriver-manager

Uso:
python scraper_italiano.py
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin, urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("ATTENZIONE: Selenium non installato!")
    print("Installa con: pip install selenium webdriver-manager")


class UpToDateItalianScraper:
    """Scraper avanzato per articoli UpToDate in italiano"""

    def __init__(self, headless: bool = True):
        self.base_url = "https://www.uptodate.com"
        # URL italiano della sezione cardiovascolare
        self.toc_url = "https://www.uptodate.com/contents/it/table-of-contents/patient-education/heart-and-blood-vessels"

        self.output_dir = Path("uptodate/articles_it")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.output_dir / "metadata.json"

        self.driver = None
        self.headless = headless
        self.articles_metadata = []

    def setup_driver(self):
        """Configura Selenium WebDriver con Chrome"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium non disponibile. Installa con: pip install selenium webdriver-manager")

        print("Configurazione Chrome WebDriver...")

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent realistico
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ WebDriver configurato")

    def close_driver(self):
        """Chiude il browser"""
        if self.driver:
            self.driver.quit()
            print("✓ Browser chiuso")

    def extract_articles_list(self) -> List[Dict[str, str]]:
        """Estrae lista completa di articoli dalla TOC italiana"""
        print(f"\nCaricamento pagina: {self.toc_url}")
        self.driver.get(self.toc_url)

        # Attendi che la pagina carichi il contenuto JavaScript
        print("Attesa caricamento contenuto...")
        time.sleep(5)  # Attesa iniziale

        try:
            # Attendi esplicitamente elementi link
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
            )
        except Exception as e:
            print(f"Timeout attesa link: {e}")

        # Scroll per caricare contenuto lazy-loaded
        print("Scroll pagina per caricare tutti gli articoli...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(10):  # Max 10 scroll
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Estrai tutti i link
        print("Estrazione link articoli...")
        links = self.driver.find_elements(By.TAG_NAME, "a")

        articles = []
        seen_urls = set()

        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()

                if not href or not text:
                    continue

                # Filtra solo link a contenuti patient education
                if "/contents/" not in href:
                    continue

                # Escl di calculator, image, graphics
                if any(x in href for x in ["/calculator", "/image", "/graphic", "/table-of-contents"]):
                    continue

                # Normalizza URL
                if href.startswith("/"):
                    href = urljoin(self.base_url, href)

                # Evita duplicati
                if href in seen_urls:
                    continue

                seen_urls.add(href)

                # Determina categoria
                category = "Unknown"
                if "the-basics" in href.lower():
                    category = "The Basics"
                elif "beyond-the-basics" in href.lower():
                    category = "Beyond the Basics"

                articles.append({
                    "title": text,
                    "url": href,
                    "category": category,
                    "filename": self.sanitize_filename(text)
                })

            except Exception as e:
                continue

        print(f"\n✓ Trovati {len(articles)} articoli unici")

        # Salva metadata
        self.articles_metadata = articles
        self.save_metadata()

        return articles

    def sanitize_filename(self, title: str) -> str:
        """Crea nome file valido da titolo"""
        # Rimuovi caratteri speciali
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        # Sostituisci spazi con underscore
        filename = re.sub(r'\s+', '_', filename)
        # Limita lunghezza
        if len(filename) > 100:
            filename = filename[:100]
        return filename + ".html"

    def download_article(self, article: Dict[str, str]) -> bool:
        """Scarica singolo articolo"""
        url = article["url"]
        title = article["title"]
        filename = article["filename"]

        print(f"\n  → {title}")

        try:
            self.driver.get(url)
            time.sleep(3)  # Attesa caricamento

            # Attendi che il contenuto principale carichi
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except:
                pass  # Continua anche se timeout

            # Estrai contenuto HTML completo
            page_source = self.driver.page_source

            # Prova a estrarre solo contenuto principale
            try:
                main_element = self.driver.find_element(By.TAG_NAME, "main")
                main_content = main_element.get_attribute("outerHTML")
            except:
                try:
                    article_element = self.driver.find_element(By.TAG_NAME, "article")
                    main_content = article_element.get_attribute("outerHTML")
                except:
                    main_content = page_source

            # Salva file
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="source" content="UpToDate Patient Education">
    <meta name="category" content="{article['category']}">
    <meta name="url" content="{url}">
    <meta name="download_date" content="{time.strftime('%Y-%m-%d %H:%M:%S')}">
</head>
<body>
    <h1>{title}</h1>
    <p><em>Fonte: <a href="{url}">{url}</a></em></p>
    <p><em>Categoria: {article['category']}</em></p>
    <p><em>Scaricato: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    <hr>
    {main_content}
</body>
</html>""")

            print(f"    ✓ Salvato: {filepath.name}")
            return True

        except Exception as e:
            print(f"    ✗ Errore: {e}")
            return False

    def download_all_articles(self):
        """Scarica tutti gli articoli estratti"""
        if not self.articles_metadata:
            print("Nessun articolo da scaricare!")
            return

        total = len(self.articles_metadata)
        successful = 0

        print(f"\n{'='*60}")
        print(f"DOWNLOAD {total} ARTICOLI")
        print(f"{'='*60}")

        for i, article in enumerate(self.articles_metadata, 1):
            print(f"\n[{i}/{total}] {article['category']}")

            if self.download_article(article):
                successful += 1

            # Pausa tra richieste
            time.sleep(2)

        print(f"\n{'='*60}")
        print(f"COMPLETATO")
        print(f"{'='*60}")
        print(f"Scaricati con successo: {successful}/{total}")
        print(f"Directory: {self.output_dir.absolute()}")

    def save_metadata(self):
        """Salva metadata articoli in JSON"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "source": "UpToDate Patient Education (Italian)",
                "section": "Heart and Blood Vessels",
                "url": self.toc_url,
                "extraction_date": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_articles": len(self.articles_metadata),
                "articles": self.articles_metadata
            }, f, indent=2, ensure_ascii=False)

        print(f"✓ Metadata salvato: {self.metadata_file}")

    def load_metadata(self) -> List[Dict[str, str]]:
        """Carica metadata da file esistente"""
        if not self.metadata_file.exists():
            return []

        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("articles", [])

    def run(self, skip_extraction: bool = False):
        """Esegue processo completo di scraping"""
        print("\n" + "="*60)
        print("UPTODATE ITALIAN PATIENT EDUCATION SCRAPER")
        print("="*60)
        print(f"Target: {self.toc_url}")
        print(f"Output: {self.output_dir.absolute()}")
        print("="*60 + "\n")

        try:
            # Setup Selenium
            self.setup_driver()

            # Estrai lista articoli (o carica da file esistente)
            if skip_extraction and self.metadata_file.exists():
                print("Caricamento metadata esistente...")
                self.articles_metadata = self.load_metadata()
                print(f"✓ Caricati {len(self.articles_metadata)} articoli da metadata")
            else:
                self.articles_metadata = self.extract_articles_list()

            if not self.articles_metadata:
                print("\n✗ Nessun articolo trovato!")
                return

            # Download articoli
            self.download_all_articles()

        except KeyboardInterrupt:
            print("\n\n⚠ Interruzione utente")
        except Exception as e:
            print(f"\n✗ Errore: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close_driver()


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scraper per articoli UpToDate in italiano"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Mostra browser (non headless)"
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Salta estrazione lista e usa metadata esistente"
    )

    args = parser.parse_args()

    scraper = UpToDateItalianScraper(headless=not args.visible)
    scraper.run(skip_extraction=args.skip_extraction)


if __name__ == "__main__":
    main()
