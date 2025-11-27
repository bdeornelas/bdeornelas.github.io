#!/usr/bin/env python3
"""
Script per aggiungere 'collection: articles' a tutti i file .md in _articles/
che non lo hanno già.
"""

import os
import re

def add_collection_to_articles():
    articles_dir = "_articles"
    files_added = []
    files_skipped = []
    
    # Ottieni tutti i file .md nella cartella _articles
    for filename in os.listdir(articles_dir):
        if filename.endswith('.md') and filename != '_template.md':
            filepath = os.path.join(articles_dir, filename)
            
            # Leggi il contenuto del file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Controlla se il file ha già 'collection: articles'
            if 'collection:' in content and 'collection: articles' in content:
                files_skipped.append(filename)
                continue
            
            # Aggiungi 'collection: articles' dopo la prima riga del front matter
            if content.startswith('---'):
                # Trova la fine del front matter
                lines = content.split('\n')
                front_matter_end = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        front_matter_end = i
                        break
                
                if front_matter_end > 0:
                    # Inserisci 'collection: articles' dopo la prima riga del front matter
                    lines.insert(1, 'collection: articles')
                    new_content = '\n'.join(lines)
                    
                    # Salva il file modificato
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    files_added.append(filename)
                else:
                    print(f"⚠️  Non posso processare {filename}: front matter non trovato")
            else:
                print(f"⚠️  Non posso processare {filename}: non ha front matter")
    
    # Stampa i risultati
    print(f"\n✅ Script completato!")
    print(f"📄 Articoli modificati: {len(files_added)}")
    print(f"⏭️  Articoli saltati (già con collection: {len(files_skipped)}")
    
    if files_added:
        print(f"\n📝 Articoli modificati:")
        for filename in files_added:
            print(f"  - {filename}")
    
    if files_skipped:
        print(f"\n⏭️  Articoli già configurati:")
        for filename in files_skipped:
            print(f"  - {filename}")

if __name__ == "__main__":
    add_collection_to_articles()