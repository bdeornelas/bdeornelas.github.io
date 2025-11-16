#!/usr/bin/env python3
"""
SEO and Content Audit Script for Italian Medical Blog
Analyzes all 45 articles for metadata, SEO optimization, and content quality
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Article directory
ARTICLES_DIR = Path("/Users/benjamindeornelas/Documents/bdeornelas.github.io/_articles")

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown file"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"')
        return frontmatter
    return {}

def count_headers(content):
    """Count H1, H2, H3 headers"""
    # Remove frontmatter first
    content_no_fm = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    h1_count = len(re.findall(r'^# [^#]', content_no_fm, re.MULTILINE))
    h2_count = len(re.findall(r'^## [^#]', content_no_fm, re.MULTILINE))
    h3_count = len(re.findall(r'^### [^#]', content_no_fm, re.MULTILINE))

    return h1_count, h2_count, h3_count

def count_internal_links(content):
    """Count internal links to other articles"""
    return len(re.findall(r'\[.*?\]\(/articles/[^)]+\)', content))

def check_uptodate_compliance(content):
    """Check compliance with UpToDate style guide patterns"""
    issues = []

    # Check for question-based H2 headers (UpToDate pattern)
    h2_headers = re.findall(r'^## (.+)$', content, re.MULTILINE)
    question_headers = [h for h in h2_headers if h.strip().endswith('?') or 'COS\'È' in h or 'QUALI' in h or 'COME' in h or 'QUANDO' in h or 'PERCHÉ' in h or 'CHI' in h]

    if h2_headers:
        question_ratio = len(question_headers) / len(h2_headers)
    else:
        question_ratio = 0

    # Check for medical term definitions (pattern: term (explanation))
    medical_defs = len(re.findall(r'\*\*[A-Za-zÀ-ÿ\s]+\*\*\s*–|●\*\*[A-Za-zÀ-ÿ\s]+\*\*', content))

    # Check for abbreviations (pattern: "term," or "ABBR")
    abbr_pattern = len(re.findall(r'"[A-Z]{2,}"', content))

    # Check for numeric data
    numeric_data = len(re.findall(r'\d+\s*(su|persone|percento|%|mg|mmHg)', content))

    return {
        'question_header_ratio': question_ratio,
        'medical_definitions': medical_defs,
        'abbreviations': abbr_pattern,
        'numeric_data_points': numeric_data
    }

def analyze_article(filepath):
    """Analyze a single article"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter = extract_frontmatter(content)
    h1, h2, h3 = count_headers(content)
    internal_links = count_internal_links(content)
    uptodate_check = check_uptodate_compliance(content)

    # Count words (approximate)
    word_count = len(re.findall(r'\b\w+\b', content))

    analysis = {
        'filename': filepath.name,
        'has_title': 'title' in frontmatter,
        'has_description': 'description' in frontmatter,
        'has_date': 'date' in frontmatter,
        'has_og_title': 'og_title' in frontmatter,
        'has_og_description': 'og_description' in frontmatter,
        'title': frontmatter.get('title', 'MISSING'),
        'description': frontmatter.get('description', 'MISSING'),
        'date': frontmatter.get('date', 'MISSING'),
        'h1_count': h1,
        'h2_count': h2,
        'h3_count': h3,
        'internal_links': internal_links,
        'word_count': word_count,
        **uptodate_check
    }

    return analysis

def generate_report(analyses):
    """Generate comprehensive SEO audit report"""

    print("=" * 80)
    print("SEO & CONTENT AUDIT REPORT")
    print("Italian Medical Blog - Dr. Benjamin De Ornelas")
    print("=" * 80)
    print()

    # Summary statistics
    total_articles = len(analyses)
    complete_metadata = sum(1 for a in analyses if all([
        a['has_title'], a['has_description'], a['has_date'],
        a['has_og_title'], a['has_og_description']
    ]))

    print(f"TOTAL ARTICLES: {total_articles}")
    print(f"Complete Metadata: {complete_metadata}/{total_articles} ({complete_metadata/total_articles*100:.1f}%)")
    print()

    # Metadata issues
    print("=" * 80)
    print("1. METADATA ANALYSIS")
    print("=" * 80)

    missing_title = [a for a in analyses if not a['has_title']]
    missing_desc = [a for a in analyses if not a['has_description']]
    missing_date = [a for a in analyses if not a['has_date']]
    missing_og_title = [a for a in analyses if not a['has_og_title']]
    missing_og_desc = [a for a in analyses if not a['has_og_description']]

    print(f"Missing title: {len(missing_title)}")
    print(f"Missing description: {len(missing_desc)}")
    print(f"Missing date: {len(missing_date)}")
    print(f"Missing og_title: {len(missing_og_title)}")
    print(f"Missing og_description: {len(missing_og_desc)}")
    print()

    if missing_title:
        print("Articles missing 'title':")
        for a in missing_title[:10]:
            print(f"  - {a['filename']}")
        if len(missing_title) > 10:
            print(f"  ... and {len(missing_title) - 10} more")
        print()

    # Header structure
    print("=" * 80)
    print("2. HEADER STRUCTURE (SEO)")
    print("=" * 80)

    multiple_h1 = [a for a in analyses if a['h1_count'] > 1]
    no_h1 = [a for a in analyses if a['h1_count'] == 0]
    few_h2 = [a for a in analyses if a['h2_count'] < 3]

    print(f"Articles with multiple H1 tags: {len(multiple_h1)} (should be 1 per page)")
    print(f"Articles with no H1: {len(no_h1)}")
    print(f"Articles with <3 H2 sections: {len(few_h2)}")
    print()

    avg_h2 = sum(a['h2_count'] for a in analyses) / len(analyses)
    avg_h3 = sum(a['h3_count'] for a in analyses) / len(analyses)
    print(f"Average H2 per article: {avg_h2:.1f}")
    print(f"Average H3 per article: {avg_h3:.1f}")
    print()

    # Internal linking
    print("=" * 80)
    print("3. INTERNAL LINKING")
    print("=" * 80)

    no_links = [a for a in analyses if a['internal_links'] == 0]
    good_links = [a for a in analyses if a['internal_links'] >= 3]

    print(f"Articles with NO internal links: {len(no_links)}/{total_articles}")
    print(f"Articles with 3+ internal links: {len(good_links)}/{total_articles}")
    avg_links = sum(a['internal_links'] for a in analyses) / len(analyses)
    print(f"Average internal links: {avg_links:.1f}")
    print()

    if no_links:
        print("Articles with NO internal links (top 15):")
        for a in sorted(no_links, key=lambda x: x['filename'])[:15]:
            print(f"  - {a['filename']}")
        print()

    # UpToDate style compliance
    print("=" * 80)
    print("4. UPTODATE STYLE GUIDE COMPLIANCE")
    print("=" * 80)

    avg_question_ratio = sum(a['question_header_ratio'] for a in analyses) / len(analyses)
    avg_numeric = sum(a['numeric_data_points'] for a in analyses) / len(analyses)

    print(f"Average H2 headers as questions: {avg_question_ratio*100:.1f}%")
    print(f"Average numeric data points per article: {avg_numeric:.1f}")
    print()

    low_questions = [a for a in analyses if a['question_header_ratio'] < 0.3]
    print(f"Articles with <30% question headers: {len(low_questions)}")

    low_data = [a for a in analyses if a['numeric_data_points'] < 10]
    print(f"Articles with <10 numeric data points: {len(low_data)}")
    print()

    # Content quality
    print("=" * 80)
    print("5. CONTENT LENGTH & QUALITY")
    print("=" * 80)

    avg_words = sum(a['word_count'] for a in analyses) / len(analyses)
    short_articles = [a for a in analyses if a['word_count'] < 1500]
    long_articles = [a for a in analyses if a['word_count'] > 3000]

    print(f"Average word count: {avg_words:.0f}")
    print(f"Articles <1500 words: {len(short_articles)}")
    print(f"Articles >3000 words: {len(long_articles)}")
    print()

    # SEO Score
    print("=" * 80)
    print("6. OVERALL SEO SCORE")
    print("=" * 80)

    def calculate_seo_score(article):
        score = 0
        # Metadata (40 points)
        if article['has_title']: score += 10
        if article['has_description']: score += 10
        if article['has_date']: score += 5
        if article['has_og_title']: score += 5
        if article['has_og_description']: score += 10

        # Structure (30 points)
        if article['h1_count'] == 1: score += 10
        if article['h2_count'] >= 5: score += 10
        elif article['h2_count'] >= 3: score += 5
        if article['h3_count'] >= 3: score += 10

        # Content (30 points)
        if article['internal_links'] >= 3: score += 10
        elif article['internal_links'] >= 1: score += 5
        if article['question_header_ratio'] >= 0.5: score += 10
        if article['numeric_data_points'] >= 20: score += 10
        elif article['numeric_data_points'] >= 10: score += 5

        return score

    for article in analyses:
        article['seo_score'] = calculate_seo_score(article)

    avg_seo = sum(a['seo_score'] for a in analyses) / len(analyses)
    print(f"Average SEO Score: {avg_seo:.1f}/100")
    print()

    excellent = [a for a in analyses if a['seo_score'] >= 80]
    good = [a for a in analyses if 60 <= a['seo_score'] < 80]
    needs_work = [a for a in analyses if a['seo_score'] < 60]

    print(f"Excellent (80-100): {len(excellent)}")
    print(f"Good (60-79): {len(good)}")
    print(f"Needs improvement (<60): {len(needs_work)}")
    print()

    if needs_work:
        print("Articles needing improvement (score <60):")
        for a in sorted(needs_work, key=lambda x: x['seo_score'])[:20]:
            print(f"  - {a['filename']}: {a['seo_score']}/100")
        print()

    # Top recommendations
    print("=" * 80)
    print("7. TOP RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("PRIORITY 1 - Metadata Optimization:")
    if missing_desc:
        print(f"  - Add meta descriptions to {len(missing_desc)} articles")
    if missing_og_desc:
        print(f"  - Add Open Graph descriptions to {len(missing_og_desc)} articles")
    print()

    print("PRIORITY 2 - Internal Linking:")
    print(f"  - Add internal links to {len(no_links)} articles with zero links")
    print("  - Target: minimum 3-5 contextual links per article")
    print()

    print("PRIORITY 3 - Content Structure:")
    if few_h2:
        print(f"  - Improve structure of {len(few_h2)} articles with <3 H2 sections")
    if multiple_h1:
        print(f"  - Fix {len(multiple_h1)} articles with multiple H1 tags")
    print()

    print("PRIORITY 4 - UpToDate Style Compliance:")
    print(f"  - Convert more H2 headers to questions (currently {avg_question_ratio*100:.1f}%)")
    print(f"  - Add more specific numeric data (avg {avg_numeric:.1f} per article)")
    print()

    # Detailed table
    print("=" * 80)
    print("8. DETAILED ARTICLE BREAKDOWN")
    print("=" * 80)
    print()
    print(f"{'Filename':<35} {'SEO':<5} {'H1':<4} {'H2':<4} {'Links':<6} {'Words':<6}")
    print("-" * 80)

    for article in sorted(analyses, key=lambda x: x['seo_score'], reverse=True)[:45]:
        print(f"{article['filename']:<35} {article['seo_score']:<5} {article['h1_count']:<4} {article['h2_count']:<4} {article['internal_links']:<6} {article['word_count']:<6}")

    return analyses

def main():
    """Main execution"""
    articles = list(ARTICLES_DIR.glob("*.md"))

    if not articles:
        print(f"No articles found in {ARTICLES_DIR}")
        return

    analyses = []
    for article_path in sorted(articles):
        try:
            analysis = analyze_article(article_path)
            analyses.append(analysis)
        except Exception as e:
            print(f"Error analyzing {article_path.name}: {e}")

    generate_report(analyses)

if __name__ == "__main__":
    main()
