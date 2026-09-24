#!/usr/bin/env python3
"""
Inject relations from frontmatter into body as markdown.
Run before quartz build.

For each article with relation fields in frontmatter,
append a "## Relasi" section to the body.
"""
import os, re, yaml
from pathlib import Path

CONTENT_DIR = "/home/ubuntu/wiki/content"

RELATION_FIELDS = [
    ("member_of", "Anggota dari"),
    ("leader_of", "Pemimpin dari"),
    ("owner_of", "Pemilik dari"),
    ("related", "Terkait dengan"),
    ("influenced_by", "Dipengaruhi oleh"),
    ("same_group_as", "Satu kelompok dengan"),
    ("oppose", "Berlawanan dengan"),
]


def extract_body_and_frontmatter(content):
    """Extract frontmatter text and body separately."""
    if not content.startswith('---'):
        return None, content, content
    
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return None, content, content
    
    fm_text = content[3:end_idx]
    body = content[end_idx + 3:]
    return fm_text, body, content


def generate_relations_section(fm):
    """Generate markdown section for relations from frontmatter dict."""
    sections = []
    
    for field_key, field_label in RELATION_FIELDS:
        value = fm.get(field_key)
        if not value:
            continue
        
        items = value if isinstance(value, list) else [value]
        if not items:
            continue
        
        # Build markdown list
        item_strs = []
        for item in items:
            title = item.replace('-', ' ').replace('_', ' ').title()
            item_strs.append(f"- [{title}](/{item})")
        
        sections.append(f"**{field_label}**\n" + "\n".join(item_strs))
    
    if not sections:
        return None
    
    return "## Relasi\n\n" + "\n\n".join(sections)


def remove_existing_relations_section(body):
    """Remove existing ## Relasi section if present."""
    lines = body.split('\n')
    new_lines = []
    skip = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('## Relasi'):
            skip = True
            # Remove trailing newlines before
            while new_lines and new_lines[-1].strip() == '':
                new_lines.pop()
            continue
        
        if skip and (line.strip().startswith('## ') and not line.strip().startswith('## Relasi')):
            skip = False
        
        if not skip:
            new_lines.append(line)
    
    return '\n'.join(new_lines)


def process_file(filepath):
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm_text, body, full_content = extract_body_and_frontmatter(content)
    
    if fm_text is None:
        return False
    
    try:
        fm = yaml.safe_load(fm_text)
    except:
        return False
    
    if not isinstance(fm, dict):
        return False
    
    # Check if any relation fields exist
    has_relations = any(fm.get(field) for field, _ in RELATION_FIELDS)
    
    if not has_relations:
        return False
    
    # Remove existing relations section
    body = remove_existing_relations_section(body)
    
    # Generate new relations section
    rel_section = generate_relations_section(fm)
    
    if rel_section is None:
        return False
    
    # Append to body
    body = body.rstrip() + '\n\n' + rel_section + '\n'
    
    # Reconstruct file
    end_idx = content.find('---', 3)
    new_content = content[:end_idx + 3] + body
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False


def main():
    content_path = Path(CONTENT_DIR)
    md_files = sorted(content_path.glob("*.md"))
    
    total = 0
    for md_file in md_files:
        if md_file.name in ["index.md"]:
            continue
        try:
            if process_file(str(md_file)):
                total += 1
                print(f"  ✓ {md_file.name}")
        except Exception as e:
            print(f"  ✗ {md_file.name}: {e}")
    
    print(f"\nDone! {total} files updated with relations section")


if __name__ == "__main__":
    main()
