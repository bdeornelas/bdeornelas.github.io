import os
import re
from bs4 import BeautifulSoup

def count_words_and_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        title = None
        # Check for YAML front matter
        if content.startswith('---'):
            end_front = content.find('---', 3)
            if end_front != -1:
                front_matter = content[3:end_front]
                # Extract title manually using regex
                title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
        if not title:
            soup = BeautifulSoup(content, 'html.parser')
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
            else:
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else 'No Title'
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        words = text.split()
        word_count = len(words)
        return title, word_count
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

articles_dir = 'articles/'
subdirs = [d for d in os.listdir(articles_dir) if os.path.isdir(os.path.join(articles_dir, d)) and d != '_template']
results = []
for subdir in subdirs:
    index_path = os.path.join(articles_dir, subdir, 'index.html')
    if os.path.exists(index_path):
        result = count_words_and_title(index_path)
        if result:
            results.append(result)

# Sort all results by word count in ascending order
results.sort(key=lambda x: x[1])

# Print all articles with word counts sorted
print("All articles word counts (sorted by word count ascending):")
for title, count in results:
    print(f"{title}: {count} words")

# Calculate average word count
if results:
    total_words = sum(count for title, count in results)
    average_words = total_words / len(results)
    print(f"\nAverage word count: {average_words:.2f}")
else:
    print("\nNo articles found.")