#!/usr/bin/env python3
"""
Auto-link script: detect plain text mentions of existing articles and convert to [[wiki links]].
Only edits body text after frontmatter (--- second delimiter), never touches YAML.
"""
import os, re, yaml, time
from pathlib import Path

CONTENT_DIR = "/home/ubuntu/wiki/content"

def load_articles():
    articles = {}
    content_path = Path(CONTENT_DIR)
    for md_file in sorted(content_path.glob("*.md")):
        if md_file.name in ["index.md", "templates.md"]:
            continue
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    fm_text = content[3:end_idx]
                    fm = yaml.safe_load(fm_text)
                    if fm and isinstance(fm, dict):
                        title = fm.get('title', '')
                        slug = md_file.stem
                        articles[slug] = {'title': title, 'slug': slug, 'file': str(md_file)}
        except:
            pass
    return articles

def create_lookup(articles):
    by_title = {}
    for slug, data in articles.items():
        title = data['title'].strip()
        if title:
            by_title[title.lower()] = data
    return by_title

def extract_body(content):
    """Extract body text after second --- delimiter."""
    if not content.startswith('---'):
        return content
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return content
    return content[end_idx + 3:]

def find_mentions(body, current_slug, by_title):
    """Find mentions of other articles in body only, excluding code blocks."""
    # Remove existing wiki links for search purposes
    body_no_links = re.sub(r'\[\[([^\]]+)\]\]', r'\1', body)
    
    # Remove code blocks to avoid matching inside code
    body_no_code = re.sub(r'```[\s\S]*?```', '', body_no_links)
    
    sorted_titles = sorted(by_title.keys(), key=len, reverse=True)
    mentions = []
    
    for title_lower in sorted_titles:
        data = by_title[title_lower]
        if data['slug'] == current_slug:
            continue
        
        pattern = re.compile(re.escape(title_lower), re.IGNORECASE)
        
        for match in pattern.finditer(body_no_code):
            start, end = match.start(), match.end()
            
            # Check if already inside a [[link]]
            surrounding = body_no_links[max(0, start-2):min(len(body_no_links), end+2)]
            if '[[' in surrounding and ']]' in surrounding:
                continue
            
            # Check word boundaries
            before = body_no_code[max(0, start-1):start]
            after = body_no_code[end:min(len(body_no_code), end+1)]
            if (before and before.isalnum()) or (after and after.isalnum()):
                continue
            
            mentions.append({
                'start': start,
                'end': end,
                'slug': data['slug'],
            })
    
    # Remove overlapping matches (keep longer ones)
    mentions.sort(key=lambda x: x['start'])
    filtered = []
    for m in mentions:
        overlap = any(not (m['end'] <= f['start'] or m['start'] >= f['end']) for f in filtered)
        if not overlap:
            filtered.append(m)
    
    return filtered

def convert_mentions(body, mentions):
    """Convert matched mentions to [[wiki links]] in body text."""
    if not mentions:
        return body
    
    mentions.sort(key=lambda x: x['start'], reverse=True)
    result = body
    for m in mentions:
        result = result[:m['start']] + f"[[{m['slug']}]]" + result[m['end']:]
    return result

def process_file(filepath, articles, by_title):
    """Process single file. Only body is modified."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    slug = Path(filepath).stem
    body = extract_body(content)
    mentions = find_mentions(body, slug, by_title)
    
    if not mentions:
        return False, 0
    
    new_body = convert_mentions(body, mentions)
    
    if new_body != body:
        end_idx = content.find('---', 3)
        new_content = content[:end_idx + 3] + new_body
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, len(mentions)
    
    return False, 0

def main():
    articles = load_articles()
    by_title = create_lookup(articles)
    print(f"Loaded {len(articles)} articles, {len(by_title)} title variations")
    
    content_path = Path(CONTENT_DIR)
    md_files = sorted(content_path.glob("*.md"))
    
    total_processed = 0
    total_links = 0
    
    for md_file in md_files:
        if md_file.name in ["index.md"] or md_file.is_dir():
            continue
        try:
            processed, links = process_file(str(md_file), articles, by_title)
            if processed:
                total_processed += 1
                total_links += links
                print(f"  ✓ {md_file.name}: {links} links")
        except Exception as e:
            print(f"  ✗ {md_file.name}: {e}")
        time.sleep(0.05)
    
    print(f"\nDone! {total_processed} files updated, {total_links} links added")

if __name__ == "__main__":
    main()
