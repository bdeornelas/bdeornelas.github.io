import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
import re

# Define websites with cardiology sections
sites = [
    {'name': 'Humanitas', 'base': 'https://www.humanitas.it', 'cardio_url': 'https://www.humanitas.it/malattie'}
]

# Keywords to filter relevant articles
keywords = ['cuore', 'cardiaco', 'cardiologia', 'infarto', 'ipertensione', 'aritmia', 'insufficienza', 'valvola', 'cardiomiopatia', 'angina', 'fibrillazione', 'flutter', 'stenosi', 'aneurisma', 'colesterolo', 'scompenso', 'pericardite', 'miocardite', 'endocardite', 'extrasistoli', 'tachicardia', 'bradicardia', 'embolia', 'polmonare', 'tvp', 'tpsv']

# Headers to mimic browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

results = []
scraped_urls = set()

def is_relevant(text, keywords):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

def scrape_page(url, site, page_num=1):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find article links
            links = soup.find_all('a', href=True)
            article_urls = []
            for link in links:
                href = link.get('href')
                if href and ('/pazienti/' in href or '/articoli/' in href or '/notizie/' in href or '/categorie/cuore/' in href or '/categoria/cuore/' in href or 'cardio' in href.lower() or 'cuore' in href.lower() or '/servizi/' in href or '/malattie/' in href):
                    if not href.startswith('http'):
                        href = site['base'] + href
                    if href not in scraped_urls:
                        article_urls.append(href)
                        scraped_urls.add(href)
            return article_urls
        else:
            print(f"Failed to access {url}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error with {url}: {e}")
        return []

for site in sites:
    page = 1
    max_pages = 2  # Limit to 2 pages per site to avoid overloading
    articles_found = 0
    max_articles = 10  # Increased limit per site
    cardio_urls = [site['cardio_url']]

    for cardio_url in cardio_urls:
        page = 1
        while page <= max_pages and articles_found < max_articles:
            if page == 1:
                current_url = cardio_url
            else:
                # Attempt pagination: add /page/2, /page/3, etc. or ?page=2, etc.
                current_url = cardio_url + f'?page={page}'
            article_urls = scrape_page(current_url, site, page)
            for url in article_urls:
                if articles_found >= max_articles:
                    break
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
                        articles_found += 1
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                time.sleep(2)  # Delay to be ethical
            page += 1
            time.sleep(1)

# Print results
print(f"Total articles found: {len(results)}")
for result in results:
    print(f"Title: {result['title']}")
    print(f"Source: {result['source']}")
    print(f"Word Count: {result['word_count']}")
    print("-" * 50)