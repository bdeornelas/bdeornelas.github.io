import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
import re

# Define websites with cardiology sections
sites = [
    {'name': 'Gruppo San Donato', 'base': 'https://www.grupposandonato.it', 'cardio_url': 'https://www.grupposandonato.it/pazienti/cuore-e-vasi/'},
    {'name': 'Humanitas', 'base': 'https://www.humanitas.it', 'cardio_url': 'https://www.humanitas.it/categorie/cuore/'}
]

# Keywords to filter relevant articles
keywords = ['insufficienza mitralica', 'stenosi mitralica', 'insufficienza aortica', 'stenosi aortica', 'cardiomiopatia', 'insufficienza cardiaca', 'cuore', 'cardiaco', 'valvola']

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

results = []
scraped_urls = set()

def is_relevant(text, keywords):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

for site in sites:
    try:
        response = requests.get(site['cardio_url'], headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find article links
            links = soup.find_all('a', href=True)
            article_urls = []
            for link in links:
                href = link.get('href')
                if href and ('/pazienti/' in href or '/articoli/' in href or '/notizie/' in href or '/categorie/cuore/' in href):
                    if not href.startswith('http'):
                        href = site['base'] + href
                    if href not in scraped_urls:
                        article_urls.append(href)
                        scraped_urls.add(href)
            # Limit to 10 articles per site
            for url in article_urls[:10]:
                try:
                    article = Article(url, language='it')
                    article.download()
                    article.parse()
                    title = article.title
                    text = article.text
                    if title and text and len(text.split()) > 100 and is_relevant(title + ' ' + text, keywords):
                        word_count = len(text.split())
                        results.append({
                            'title': title,
                            'source': site['name'],
                            'word_count': word_count
                        })
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                time.sleep(2)  # Delay to be ethical
        else:
            print(f"Failed to access {site['cardio_url']}: {response.status_code}")
    except Exception as e:
        print(f"Error with {site['cardio_url']}: {e}")
    time.sleep(1)

# Print results
for result in results:
    print(f"Title: {result['title']}")
    print(f"Source: {result['source']}")
    print(f"Word Count: {result['word_count']}")
    print("-" * 50)