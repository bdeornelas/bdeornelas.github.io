#!/usr/bin/env python3
"""
UpToDate Authenticated Scraper
================================

Scraper che usa credenziali istituzionali per scaricare articoli completi.

Requisiti:
pip install selenium webdriver-manager
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class AuthenticatedUpToDateScraper:
    """Scraper con autenticazione per UpToDate"""

    def __init__(self, config_file='config.json', headless=False):
        self.config = self.load_config(config_file)
        self.base_url = "https://www.uptodate.com"
        self.output_dir = Path("uptodate/articles_authenticated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir / "metadata.json"
        self.driver = None
        self.headless = headless
        self.authenticated = False

    def load_config(self, config_file):
        """Carica configurazione"""
        with open(config_file, 'r') as f:
            return json.load(f)

    def setup_driver(self):
        """Configura Chrome WebDriver"""
        print("⚙️  Configurazione Chrome WebDriver...")

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"user-agent={self.config['user_agent']}")

        # Disabilita rilevamento automation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Rimuovi flag webdriver
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.config['user_agent']
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("✅ WebDriver configurato")

    def login(self):
        """Esegue login su UpToDate"""
        print("\n🔐 Autenticazione UpToDate...")

        try:
            # Vai alla pagina di login
            login_url = self.config.get('institution_login_url', 'https://www.uptodate.com/login')
            print(f"   → Apertura: {login_url}")
            self.driver.get(login_url)
            time.sleep(3)

            # Cerca campo username
            print("   → Inserimento credenziali...")
            try:
                # Prova diversi selettori comuni
                username_field = None
                username_selectors = [
                    "input[name='username']",
                    "input[name='email']",
                    "input[type='email']",
                    "input[id='username']",
                    "input[id='email']",
                    "#username",
                    "#email"
                ]

                for selector in username_selectors:
                    try:
                        username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if not username_field:
                    # Salva screenshot per debug
                    self.driver.save_screenshot("uptodate/login_page.png")
                    print("   ⚠️  Campo username non trovato. Screenshot salvato.")
                    return False

                username_field.clear()
                username_field.send_keys(self.config['username'])

                # Cerca campo password
                password_field = None
                password_selectors = [
                    "input[name='password']",
                    "input[type='password']",
                    "input[id='password']",
                    "#password"
                ]

                for selector in password_selectors:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if not password_field:
                    print("   ⚠️  Campo password non trovato.")
                    return False

                password_field.clear()
                password_field.send_keys(self.config['password'])

                # Cerca bottone submit
                submit_button = None
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button[class*='login']",
                    "button[class*='submit']",
                    "#login-button",
                    ".login-button"
                ]

                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue

                if not submit_button:
                    print("   ⚠️  Bottone submit non trovato.")
                    return False

                print("   → Invio form...")
                submit_button.click()
                time.sleep(5)

                # Verifica se login è riuscito
                current_url = self.driver.current_url
                if "login" not in current_url.lower() or "contents" in current_url:
                    print("✅ Login completato!")
                    self.authenticated = True
                    return True
                else:
                    print("   ⚠️  Login potrebbe essere fallito. URL corrente:", current_url)
                    self.driver.save_screenshot("uptodate/after_login.png")
                    return False

            except Exception as e:
                print(f"   ❌ Errore durante login: {e}")
                self.driver.save_screenshot("uptodate/login_error.png")
                return False

        except Exception as e:
            print(f"❌ Errore generale login: {e}")
            return False

    def extract_article_content(self, url):
        """Scarica e estrae contenuto di un singolo articolo"""
        try:
            self.driver.get(url)
            time.sleep(3)

            # Attendi che il contenuto carichi
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            except TimeoutException:
                # Prova con article tag
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "article"))
                    )
                except:
                    pass

            # Estrai tutto il contenuto testuale visibile
            try:
                # Prova main element
                main = self.driver.find_element(By.TAG_NAME, "main")
                content_html = main.get_attribute("outerHTML")
            except:
                try:
                    # Prova article element
                    article = self.driver.find_element(By.TAG_NAME, "article")
                    content_html = article.get_attribute("outerHTML")
                except:
                    # Fallback: body completo
                    content_html = self.driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")

            # Estrai anche il titolo
            try:
                title = self.driver.find_element(By.TAG_NAME, "h1").text
            except:
                title = self.driver.title

            return {
                "title": title,
                "html": content_html,
                "url": url,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"      ❌ Errore estrazione: {e}")
            return None

    def download_articles_from_list(self, articles_list):
        """Scarica articoli da lista JSON"""
        print(f"\n📥 Download di {len(articles_list)} articoli...")

        successful = 0
        failed = []

        for i, article_info in enumerate(articles_list, 1):
            title = article_info.get('title', 'Unknown')
            url = article_info.get('url_it') or article_info.get('url_en')

            print(f"\n[{i}/{len(articles_list)}] {title}")
            print(f"   URL: {url}")

            content = self.extract_article_content(url)

            if content:
                # Salva file HTML
                filename = self.sanitize_filename(title) + ".html"
                filepath = self.output_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>{content['title']}</title>
    <meta name="source" content="UpToDate Patient Education">
    <meta name="url" content="{content['url']}">
    <meta name="download_date" content="{content['timestamp']}">
</head>
<body>
{content['html']}
</body>
</html>""")

                print(f"   ✅ Salvato: {filename}")
                successful += 1
            else:
                print(f"   ❌ Fallito")
                failed.append(title)

            # Pausa tra richieste
            time.sleep(self.config['delay_between_requests'])

        print(f"\n{'='*60}")
        print(f"✅ Completati: {successful}/{len(articles_list)}")
        if failed:
            print(f"❌ Falliti ({len(failed)}): {', '.join(failed[:5])}")
        print(f"📁 Directory: {self.output_dir.absolute()}")

    def sanitize_filename(self, title):
        """Crea nome file valido"""
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '_', filename)
        return filename[:100]

    def run(self):
        """Esegue processo completo"""
        print("\n" + "="*60)
        print("UPTODATE AUTHENTICATED SCRAPER")
        print("="*60)

        try:
            # Setup
            self.setup_driver()

            # Login
            if not self.login():
                print("\n❌ Login fallito. Verifica credenziali in config.json")
                return

            # Carica lista articoli
            articles_json = Path("uptodate/articoli_uptodate.json")
            if not articles_json.exists():
                print(f"\n❌ File {articles_json} non trovato!")
                return

            with open(articles_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                articles = data.get('articles', [])

            print(f"\n📋 Caricati {len(articles)} articoli da {articles_json.name}")

            # Download
            self.download_articles_from_list(articles)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interruzione utente")
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✅ Browser chiuso")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--visible", action="store_true", help="Mostra browser")
    args = parser.parse_args()

    scraper = AuthenticatedUpToDateScraper(headless=not args.visible)
    scraper.run()


if __name__ == "__main__":
    main()
