#!/usr/bin/env python3
"""
Auto-link script: detect plain text mentions of existing articles and convert to [[wiki links]].

This script scans .md files for mentions of other articles (by title or slug) 
and wraps them in [[wiki links]].
"""
import os, re, yaml, time
from pathlib import Path
from collections import defaultdict

CONTENT_DIR = "/home/ubuntu/wiki/content"

def load_articles():
    """Load all articles and create a lookup table."""
    articles = {}
    content_path = Path(CONTENT_DIR)
    
    for md_file in sorted(content_path.glob("*.md")):
        if md_file.name in ["index.md", "templates.md"]:
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if fm and isinstance(fm, dict):
                        title = fm.get('title', '')
                        slug = md_file.stem
                        tags = fm.get('tags', [])
                        articles[slug] = {
                            'title': title,
                            'slug': slug,
                            'tags': tags,
                            'file': str(md_file)
                        }
        except Exception as e:
            pass
    
    return articles

def create_lookup(articles):
    """Create lookup tables for matching."""
    # By slug
    by_slug = {}
    # By title (lowercase, normalized)
    by_title = {}
    
    for slug, data in articles.items():
        by_slug[slug] = data
        
        # Normalize title for matching
        title = data['title'].strip()
        if title:
            by_title[title.lower()] = data
        
        # Also add without common prefixes
        for prefix in ['Prof. ', 'Dr. ', 'Ir. ', 'H. ', 'Hj. ']:
            if title.startswith(prefix):
                by_title[len(prefix):].lower().strip()
    
    return by_slug, by_title

def find_mentions(content, current_slug, by_slug, by_title):
    """Find mentions of other articles in content."""
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Remove existing wiki links
    content_no_links = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
    
    # Remove code blocks
    content_no_code = re.sub(r'```[\s\S]*?```', '', content_no_links)
    
    # Sort titles by length (longest first) to avoid partial matches
    sorted_titles = sorted(by_title.keys(), key=len, reverse=True)
    
    mentions = []
    for title_lower in sorted_titles:
        data = by_title[title_lower]
        if data['slug'] == current_slug:
            continue
        
        # Case-insensitive search for the title
        pattern = re.compile(re.escape(title_lower), re.IGNORECASE)
        
        for match in pattern.finditer(content_no_code):
            start, end = match.start(), match.end()
            
            # Check if it's already inside a [[link]]
            surrounding = content_no_links[max(0, start-2):min(len(content_no_links), end+2)]
            if '[[' in surrounding and ']]' in surrounding:
                continue
            
            # Check if it's a whole word/phrase
            before = content_no_code[max(0, start-1):start]
            after = content_no_code[end:min(len(content_no_code), end+1)]
            
            # Don't link if part of a larger word (unless it's a name)
            if before and before.isalnum():
                continue
            if after and after.isalnum():
                continue
            
            mentions.append({
                'start': start,
                'end': end,
                'matched_text': content_no_code[start:end],
                'slug': data['slug'],
                'title': data['title']
            })
    
    # Remove overlapping matches (keep longer ones)
    mentions.sort(key=lambda x: x['start'])
    filtered = []
    for m in mentions:
        # Check overlap with existing
        overlap = False
        for f in filtered:
            if not (m['end'] <= f['start'] or m['start'] >= f['end']):
                overlap = True
                break
        if not overlap:
            filtered.append(m)
    
    return filtered

def convert_mentions(content, mentions):
    """Convert matched mentions to [[wiki links]]."""
    if not mentions:
        return content
    
    # Sort by position (reverse) to replace from end to start
    mentions.sort(key=lambda x: x['start'], reverse=True)
    
    result = content
    for m in mentions:
        before = result[:m['start']]
        matched = result[m['start']:m['end']]
        after = result[m['end']:]
        
        result = before + f"[[{m['slug']}]]" + after
    
    return result

def process_file(filepath, articles, by_slug, by_title):
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    slug = Path(filepath).stem
    mentions = find_mentions(content, slug, by_slug, by_title)
    
    if not mentions:
        return False, 0
    
    new_content = convert_mentions(content, mentions)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, len(mentions)
    
    return False, 0

def main():
    articles = load_articles()
    by_slug, by_title = create_lookup(articles)
    
    print(f"Loaded {len(articles)} articles")
    print(f"Found {len(by_title)} title variations for matching")
    
    content_path = Path(CONTENT_DIR)
    md_files = sorted(content_path.glob("*.md"))
    
    total_processed = 0
    total_links = 0
    
    for md_file in md_files:
        if md_file.name in ["index.md"] or md_file.is_dir():
            continue
        
        try:
            processed, links = process_file(str(md_file), articles, by_slug, by_title)
            if processed:
                total_processed += 1
                total_links += links
                print(f"  ✓ {md_file.name}: {links} links added")
            else:
                print(f"  - {md_file.name}: no changes")
        except Exception as e:
            print(f"  ✗ {md_file.name}: {e}")
        
        time.sleep(0.1)
    
    print(f"\nDone! {total_processed} files updated, {total_links} links added")

if __name__ == "__main__":
    main()
